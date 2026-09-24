"""
Project Brahmand: Sovereign 14-Agent Master Firmware (Raspberry Pi Pico RP2040)
================================================================================
Hardware: Dual ARM Cortex-M0+ @ 133 MHz | 264 KB SRAM | 2 MB Flash | <50 mW
Displays: 1602A Character LCD + 8x8 MAX7219 Dot Matrix + REPL HUD
"""

import gc
import time
from machine import Pin

gc.collect()

# 1. Onboard LED (GP25)
try:
    led = Pin(25, Pin.OUT)
    led.value(1)
    time.sleep(0.05)
    led.value(0)
except Exception:
    led = None

# 2. 1602A Character LCD (GP0-GP5)
lcd = None
try:
    from lcd1602 import GpioLcd1602
    lcd = GpioLcd1602(rs_pin=0, e_pin=1, d4_pin=2, d5_pin=3, d6_pin=4, d7_pin=5)
    lcd.display_ai_card("BRAHMAND AI 14L", "14 AGENTS ACTIVE")
except Exception:
    pass

# 3. 8x8 LED Matrix Display (MAX7219 on GP10, GP11, GP13)
matrix = None
try:
    from max7219_8x8 import Max7219_8x8, BITMAPS
    matrix = Max7219_8x8(sck_pin=10, mosi_pin=11, cs_pin=13, brightness=7)
    matrix.show_bitmap(BITMAPS.get("BRAIN", [0]*8))
except Exception:
    pass

gc.collect()

print("""
================================================================================
 [PROJECT BRAHMAND] 15-AGENT SOVEREIGN FLEET ACTIVE ON PHYSICAL RP2040 SILICON
================================================================================
  TIP FOR WINDOWS: Run 'chcp 65001' in PowerShell for UTF-8 display.
--------------------------------------------------------------------------------
  * Interactive Chat Mode: import agent_mesh; agent_mesh.chat()
  * Master Agent Mesh:     import agent_mesh; agent_mesh.query("Your Goal")
  * Universal Converter:   agent_mesh.query("5.8 feet to cm")
  * Physics Masterclass:   agent_mesh.query("learn quantum tunneling")
  * Full User Manual:      import manual; manual.help()
================================================================================
""")
