"""
16-Pin Bare 8x8 LED Matrix Driver for Raspberry Pi Pico (RP2040)
================================================================
Controls bare 8x8 LED matrix modules (1088AS / 1088BS / 788AS / 1588BS)
using hardware Timer interrupt (ISR) multiplexing for 100% flicker-free display.

Default Wiring (Rows: GP6-GP13, Cols: GP14-GP21):
- Matrix Pin 9  (Row 1) -> GP6  (Pico Pin 9)
- Matrix Pin 14 (Row 2) -> GP7  (Pico Pin 10)
- Matrix Pin 8  (Row 3) -> GP8  (Pico Pin 11)
- Matrix Pin 12 (Row 4) -> GP9  (Pico Pin 12)
- Matrix Pin 1  (Row 5) -> GP10 (Pico Pin 14)
- Matrix Pin 7  (Row 6) -> GP11 (Pico Pin 15)
- Matrix Pin 2  (Row 7) -> GP12 (Pico Pin 16)
- Matrix Pin 5  (Row 8) -> GP13 (Pico Pin 17)

- Matrix Pin 13 (Col 1) -> GP14 (Pico Pin 19)
- Matrix Pin 3  (Col 2) -> GP15 (Pico Pin 20)
- Matrix Pin 4  (Col 3) -> GP16 (Pico Pin 21)
- Matrix Pin 10 (Col 4) -> GP17 (Pico Pin 22)
- Matrix Pin 6  (Col 5) -> GP18 (Pico Pin 24)
- Matrix Pin 11 (Col 6) -> GP19 (Pico Pin 25)
- Matrix Pin 15 (Col 7) -> GP20 (Pico Pin 26)
- Matrix Pin 16 (Col 8) -> GP21 (Pico Pin 27)
"""

import time
from machine import Pin, Timer

BITMAPS = {
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
    "SMILE": bytes([
        0b00111100,
        0b01000010,
        0b10100101,
        0b10000001,
        0b10100101,
        0b10011001,
        0b01000010,
        0b00111100
    ]),
    "SKULL": bytes([
        0b81, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x81
    ])
}

class Matrix16Pin:
    def __init__(self, row_gpios=[6, 7, 8, 9, 10, 11, 12, 13], 
                       col_gpios=[14, 15, 16, 17, 18, 19, 20, 21], 
                       anode_rows=True):
        self.anode_rows = anode_rows
        self.rows = [Pin(p, Pin.OUT) for p in row_gpios]
        self.cols = [Pin(p, Pin.OUT) for p in col_gpios]
        self.buffer = bytearray(8)
        self.curr_row = 0
        self.clear()
        
        # Hardware timer multiplexing at 800Hz (100Hz per full frame = zero flicker)
        self._timer = Timer()
        self._timer.init(freq=800, mode=Timer.PERIODIC, callback=self._isr_refresh)

    def _isr_refresh(self, t):
        # 1. Turn off current row
        if self.anode_rows:
            self.rows[self.curr_row].value(0)
        else:
            self.rows[self.curr_row].value(1)

        # 2. Advance to next row
        self.curr_row = (self.curr_row + 1) & 7
        row_val = self.buffer[self.curr_row]

        # 3. Set columns for this row
        for c_idx in range(8):
            bit_on = (row_val >> (7 - c_idx)) & 1
            if self.anode_rows:
                self.cols[c_idx].value(0 if bit_on else 1) # Active LOW
            else:
                self.cols[c_idx].value(1 if bit_on else 0) # Active HIGH

        # 4. Turn on new row
        if self.anode_rows:
            self.rows[self.curr_row].value(1) # Active HIGH
        else:
            self.rows[self.curr_row].value(0) # Active LOW

    def clear(self):
        for i in range(8):
            self.buffer[i] = 0
        for r in self.rows:
            r.value(0 if self.anode_rows else 1)
        for c in self.cols:
            c.value(1 if self.anode_rows else 0)

    def show_bitmap(self, bitmap_8bytes):
        for i in range(8):
            self.buffer[i] = bitmap_8bytes[i]

    def set_pixel(self, x, y, val=1):
        if 0 <= x < 8 and 0 <= y < 8:
            if val:
                self.buffer[y] |= (1 << (7 - x))
            else:
                self.buffer[y] &= ~(1 << (7 - x))

    def deinit(self):
        try:
            self._timer.deinit()
        except Exception:
            pass
        self.clear()
