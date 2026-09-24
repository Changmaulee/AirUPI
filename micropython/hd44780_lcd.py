"""
Hitachi HD44780 / KS0066U 16x2 Character LCD Driver (RP2040 MicroPython)
========================================================================
Supports:
1. Direct 4-Bit GPIO Mode (Standard 6-wire connection: RS, E, D4, D5, D6, D7)
2. I2C PCF8574 Backpack Mode (2-wire connection: SDA, SCL at 0x27 or 0x3F)
3. Custom CGRAM 5x8 Character Generator (Heart, Battery, Rupee ₹, Brain, etc.)
4. Smooth text alignment, auto-scrolling marquee, cursor and backlight controls.

Authored by Chandramouli for Project Brahmand & TimeMeshin.
License: Apache-2.0
"""

import time
from machine import Pin, I2C

# HD44780 Standard Command Instruction Set
LCD_CLEARDISPLAY   = 0x01
LCD_RETURNHOME     = 0x02
LCD_ENTRYMODESET   = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT    = 0x10
LCD_FUNCTIONSET    = 0x20
LCD_SETCGRAMADDR   = 0x40
LCD_SETDDRAMADDR   = 0x80

# Flags for Display Entry Mode
LCD_ENTRYRIGHT          = 0x00
LCD_ENTRYLEFT           = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Flags for Display On/Off & Cursor Control
LCD_DISPLAYON  = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON   = 0x02
LCD_CURSOROFF  = 0x00
LCD_BLINKON    = 0x01
LCD_BLINKOFF   = 0x00

# Flags for Display/Cursor Move
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE  = 0x00
LCD_MOVERIGHT   = 0x04
LCD_MOVELEFT    = 0x00

# Flags for Function Set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE    = 0x08
LCD_1LINE    = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS  = 0x00

class HD44780_Base:
    """Base HD44780 controller logic handling high-level LCD commands & CGRAM."""
    def __init__(self, cols=16, rows=2):
        self.cols = cols
        self.rows = rows
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        self.displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF

    def clear(self):
        self.send_command(LCD_CLEARDISPLAY)
        time.sleep_ms(3)

    def home(self):
        self.send_command(LCD_RETURNHOME)
        time.sleep_ms(3)

    def set_cursor(self, col, row):
        if row >= self.rows:
            row = self.rows - 1
        self.send_command(LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def display_on(self):
        self.displaycontrol |= LCD_DISPLAYON
        self.send_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def display_off(self):
        self.displaycontrol &= ~LCD_DISPLAYON
        self.send_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor_on(self):
        self.displaycontrol |= LCD_CURSORON
        self.send_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor_off(self):
        self.displaycontrol &= ~LCD_CURSORON
        self.send_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def blink_on(self):
        self.displaycontrol |= LCD_BLINKON
        self.send_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def blink_off(self):
        self.displaycontrol &= ~LCD_BLINKON
        self.send_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def write_char(self, char):
        if isinstance(char, str):
            self.send_data(ord(char))
        else:
            self.send_data(int(char))

    def write_str(self, text):
        for ch in text:
            self.send_data(ord(ch))

    def print_line(self, row, text, align="left"):
        self.set_cursor(0, row)
        txt = str(text)
        if align == "center":
            padded = txt.center(self.cols)[:self.cols]
        elif align == "right":
            padded = txt.rjust(self.cols)[:self.cols]
        else:
            padded = (txt + " " * self.cols)[:self.cols]
        self.write_str(padded)

    def create_custom_char(self, location, charmap):
        """
        Stores an 8-byte 5x8 pixel custom character into CGRAM locations 0..7.
        """
        location &= 0x07
        self.send_command(LCD_SETCGRAMADDR | (location << 3))
        for byte_val in charmap:
            self.send_data(byte_val)

    def scroll_left(self):
        self.send_command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    def scroll_right(self):
        self.send_command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    def marquee(self, row, text, delay_ms=250):
        """Scrolls text wider than 16 characters across the specified row."""
        if len(text) <= self.cols:
            self.print_line(row, text)
            return
        padded = text + "    " + text[:self.cols]
        for i in range(len(text) + 4):
            self.set_cursor(0, row)
            self.write_str(padded[i:i + self.cols])
            time.sleep_ms(delay_ms)


class HD44780_GPIO(HD44780_Base):
    """
    Direct 4-Bit GPIO Interface for HD44780 on Raspberry Pi Pico.
    Default Wiring:
      - RS : GP0 (Pin 1)
      - E  : GP1 (Pin 2)
      - D4 : GP2 (Pin 4)
      - D5 : GP3 (Pin 5)
      - D6 : GP4 (Pin 6)
      - D7 : GP5 (Pin 7)
      - RW : GND (Pin 38)
    """
    def __init__(self, rs_pin=0, e_pin=1, d4_pin=2, d5_pin=3, d6_pin=4, d7_pin=5, cols=16, rows=2):
        super().__init__(cols, rows)
        self.rs = Pin(rs_pin, Pin.OUT)
        self.e  = Pin(e_pin,  Pin.OUT)
        self.d4 = Pin(d4_pin, Pin.OUT)
        self.d5 = Pin(d5_pin, Pin.OUT)
        self.d6 = Pin(d6_pin, Pin.OUT)
        self.d7 = Pin(d7_pin, Pin.OUT)

        self.rs.value(0)
        self.e.value(0)
        time.sleep_ms(50)
        self._init_4bit()

    def _pulse_enable(self):
        self.e.value(0)
        time.sleep_us(1)
        self.e.value(1)
        time.sleep_us(1)
        self.e.value(0)
        time.sleep_us(100)

    def _write_nibble(self, nibble):
        self.d4.value((nibble >> 0) & 1)
        self.d5.value((nibble >> 1) & 1)
        self.d6.value((nibble >> 2) & 1)
        self.d7.value((nibble >> 3) & 1)
        self._pulse_enable()

    def _send(self, val, is_data=False):
        self.rs.value(1 if is_data else 0)
        self._write_nibble((val >> 4) & 0x0F)
        self._write_nibble(val & 0x0F)
        time.sleep_us(50)

    def send_command(self, cmd):
        self._send(cmd, is_data=False)

    def send_data(self, data):
        self._send(data, is_data=True)

    def _init_4bit(self):
        # 4-bit initialization sequence per HD44780 datasheet
        for _ in range(3):
            self._write_nibble(0x03)
            time.sleep_ms(5)
        self._write_nibble(0x02) # Set to 4-bit interface
        time.sleep_ms(2)

        self.send_command(LCD_FUNCTIONSET | LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS)
        self.send_command(LCD_DISPLAYCONTROL | self.displaycontrol)
        self.send_command(LCD_ENTRYMODESET | LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT)
        self.clear()


class HD44780_I2C(HD44780_Base):
    """
    I2C PCF8574 Backpack Interface for HD44780 on Raspberry Pi Pico.
    Default Wiring:
      - SDA : GP4 (I2C0) or GP8 (I2C0) / Pin 6
      - SCL : GP5 (I2C0) or GP9 (I2C0) / Pin 7
      - VCC : 5V (VBUS / Pin 40)
      - GND : GND (Pin 38)
    """
    MASK_RS = 0x01
    MASK_RW = 0x02
    MASK_E  = 0x04
    MASK_BL = 0x08 # Backlight

    def __init__(self, i2c_bus, addr=0x27, cols=16, rows=2):
        super().__init__(cols, rows)
        self.i2c = i2c_bus
        self.addr = addr
        self.backlight = self.MASK_BL
        time.sleep_ms(50)
        self._init_4bit()

    def _write_i2c(self, data):
        self.i2c.writeto(self.addr, bytearray([data | self.backlight]))

    def _pulse_enable(self, data):
        self._write_i2c(data | self.MASK_E)
        time.sleep_us(1)
        self._write_i2c(data & ~self.MASK_E)
        time.sleep_us(50)

    def _write_nibble(self, nibble, is_data=False):
        val = (nibble << 4) | (self.MASK_RS if is_data else 0)
        self._write_i2c(val)
        self._pulse_enable(val)

    def _send(self, val, is_data=False):
        self._write_nibble((val >> 4) & 0x0F, is_data)
        self._write_nibble(val & 0x0F, is_data)

    def send_command(self, cmd):
        self._send(cmd, is_data=False)

    def send_data(self, data):
        self._send(data, is_data=True)

    def backlight_on(self):
        self.backlight = self.MASK_BL
        self._write_i2c(0)

    def backlight_off(self):
        self.backlight = 0x00
        self._write_i2c(0)

    def _init_4bit(self):
        for _ in range(3):
            self._write_nibble(0x03)
            time.sleep_ms(5)
        self._write_nibble(0x02)
        time.sleep_ms(2)

        self.send_command(LCD_FUNCTIONSET | LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS)
        self.send_command(LCD_DISPLAYCONTROL | self.displaycontrol)
        self.send_command(LCD_ENTRYMODESET | LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT)
        self.clear()


# ==============================================================================
# BUILT-IN CGRAM CUSTOM CHARACTERS (5x8 PIXEL BITMAPS)
# ==============================================================================

CUSTOM_CHARACTERS = {
    # Location 0: Beating Heart
    "HEART": [
        0b00000,
        0b01010,
        0b11111,
        0b11111,
        0b01110,
        0b00100,
        0b00000,
        0b00000
    ],
    # Location 1: Full Battery
    "BATTERY": [
        0b01110,
        0b11111,
        0b10001,
        0b11111,
        0b11111,
        0b11111,
        0b11111,
        0b00000
    ],
    # Location 2: Indian Rupee Symbol (₹)
    "RUPEE": [
        0b11111,
        0b00100,
        0b11110,
        0b00100,
        0b01010,
        0b10001,
        0b00000,
        0b00000
    ],
    # Location 3: AI Brain Chip (🔲)
    "BRAIN": [
        0b01110,
        0b10001,
        0b11111,
        0b10101,
        0b11111,
        0b10001,
        0b01110,
        0b00000
    ],
    # Location 4: Checkmark (✓)
    "CHECK": [
        0b00000,
        0b00001,
        0b00011,
        0b10110,
        0b11100,
        0b01000,
        0b00000,
        0b00000
    ],
    # Location 5: Lightning Bolt (⚡)
    "LIGHTNING": [
        0b00010,
        0b00100,
        0b01000,
        0b11111,
        0b00100,
        0b01000,
        0b10000,
        0b00000
    ]
}

def load_default_custom_characters(lcd_inst):
    """Loads default custom glyphs into CGRAM slots 0..5."""
    icons = ["HEART", "BATTERY", "RUPEE", "BRAIN", "CHECK", "LIGHTNING"]
    for idx, name in enumerate(icons):
        lcd_inst.create_custom_char(idx, CUSTOM_CHARACTERS[name])
