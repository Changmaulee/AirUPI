"""
Project Brahmand: 8x8 LED Matrix Display Driver for Raspberry Pi Pico (RP2040)
=============================================================================
Supports:
1. MAX7219 SPI 8x8 Dot Matrix Modules (DIN, CS, CLK - 3 GPIOs + Power).
2. Animations: Beating Heart (ECG), AI Brain, 0-9 Digits, Status Ticks, and Scrolling Text.
3. Micro-power (<10 mA) execution on RP2040 ARM Cortex-M0+.

Pinout on Pico:
- DIN (MOSI) : GP11 (Pin 15)
- CS         : GP13 (Pin 17)
- CLK (SCK)  : GP10 (Pin 14)
- VCC        : 5V (VBUS / Pin 40) or 3V3 (Pin 36)
- GND        : GND (Pin 38)
"""

import time
from machine import Pin, SPI

class Max7219_8x8:
    REG_NOOP   = 0x00
    REG_DIGIT0 = 0x01
    REG_DECODE = 0x09
    REG_INTENS = 0x0A
    REG_SCAN   = 0x0B
    REG_SHUTDN = 0x0C
    REG_TEST   = 0x0F

    def __init__(self, sck_pin=10, mosi_pin=11, cs_pin=13, brightness=7):
        self.cs = Pin(cs_pin, Pin.OUT)
        self.cs.value(1)
        self.sck = Pin(sck_pin, Pin.OUT)
        self.mosi = Pin(mosi_pin, Pin.OUT)
        self.buffer = bytearray(8)
        self.init_display(brightness)

    def _write_byte(self, byte_val):
        # High speed bitbang SPI
        for i in range(8):
            bit = (byte_val >> (7 - i)) & 1
            self.mosi.value(bit)
            self.sck.value(1)
            self.sck.value(0)

    def _write_reg(self, reg, data):
        self.cs.value(0)
        self._write_byte(reg)
        self._write_byte(data)
        self.cs.value(1)

    def init_display(self, brightness):
        self._write_reg(self.REG_SHUTDN, 0x01) # Exit shutdown
        self._write_reg(self.REG_TEST,   0x00) # Disable test mode
        self._write_reg(self.REG_DECODE, 0x00) # Raw matrix mode
        self._write_reg(self.REG_SCAN,   0x07) # Scan all 8 rows
        self.set_brightness(brightness)
        self.clear()

    def set_brightness(self, level):
        clamped = max(0, min(15, level))
        self._write_reg(self.REG_INTENS, clamped)

    def clear(self):
        for i in range(8):
            self.buffer[i] = 0x00
            self._write_reg(self.REG_DIGIT0 + i, 0x00)

    def show_bitmap(self, bitmap_8bytes):
        for row in range(8):
            self.buffer[row] = bitmap_8bytes[row]
            self._write_reg(self.REG_DIGIT0 + row, bitmap_8bytes[row])

    def set_pixel(self, x, y, val=1):
        if 0 <= x < 8 and 0 <= y < 8:
            if val:
                self.buffer[y] |= (1 << (7 - x))
            else:
                self.buffer[y] &= ~(1 << (7 - x))
            self._write_reg(self.REG_DIGIT0 + y, self.buffer[y])

# Built-in 8x8 Graphic Bitmaps
BITMAPS = {
    # Beating Heart (ECG Holter Mode)
    "HEART_BIG": bytes([
        0b01100110,
        0b11111111,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00111100,
        0b00011000,
        0b00000000
    ]),
    "HEART_SMALL": bytes([
        0b00000000,
        0b00100100,
        0b01111110,
        0b01111110,
        0b00111100,
        0b00011000,
        0b00000000,
        0b00000000
    ]),
    # AI Brain (Project Brahmand Thinker)
    "BRAIN": bytes([
        0b00111100,
        0b01100110,
        0b11011011,
        0b10011001,
        0b11000011,
        0b11011011,
        0b01100110,
        0b00111100
    ]),
    # 0.0% Hallucination / Verified ALU Math Tick
    "CHECK_MARK": bytes([
        0b00000000,
        0b00000001,
        0b00000011,
        0b00000110,
        0b10001100,
        0b11011000,
        0b01110000,
        0b00100000
    ]),
    # Lightning Compute Pulse
    "LIGHTNING": bytes([
        0b00011000,
        0b00110000,
        0b01100000,
        0b11111100,
        0b00011000,
        0b00110000,
        0b01100000,
        0b01000000
    ])
}
