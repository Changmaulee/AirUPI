"""
OTMB-Based Embedded ASCII Technical Troubleshooting Manuals
Target Platform: MicroPython on Raspberry Pi Pico (RP2040) / Desktop Python
Features: ASCII schematics, decision trees, hardware diagnostics, and step-by-step
fault-tree analysis for Electronics, RP2040, I2C/SPI, Power/Battery, and MicroPython.
"""

import sys

MANUALS = {
    "1": {
        "title": "RP2040 GPIO & 3.3V vs 5V Level Shifting",
        "diagram": """
  +----------------------------------------------------------------+
  |  RP2040 3.3V GPIO <---> 5V ARDUINO / SENSOR LEVEL SHIFTER      |
  +----------------------------------------------------------------+
             +3.3V VCC (Pico)              +5V VBUS / Ext
                   |                              |
                [10k Pullup]                   [10k Pullup]
                   |                              |
  Pico GPIO ------+------- D (Drain)             |
  (3.3V Logic)               |                    |
                         +---| BSS138 N-MOSFET    |
                         |   |                    |
             +3.3V -----+--- S (Source) ---------+------ 5V Sensor
                         |                               (5V Logic)
                        Gate
        ⚠️ CAUTION: RP2040 GPIO pins are NOT 5V tolerant!
        Connecting 5V directly to GP0-GP29 will destroy the IO pad.
""",
        "symptoms": ["MCU resets when sensor attached", "Garbage serial data", "Blown GPIO pad"],
        "checks": [
            "1. Measure voltage on GPIO with multimeter: Must NOT exceed 3.3V.",
            "2. For unidirectional 5V->3.3V: Use voltage divider (1k resistor in series, 2k to GND -> 3.33V).",
            "3. For bidirectional I2C: Use BSS138 bi-directional level shifter with pullup resistors to both rails."
        ]
    },

    "2": {
        "title": "I2C Bus Hanging & Missing Acknowledge (NACK)",
        "diagram": """
  +----------------------------------------------------------------+
  |  I2C BUS PULL-UP RESISTOR TOPOLOGY                             |
  +----------------------------------------------------------------+
        +3.3V ----------------+---------------+
                              |               |
                           [4.7k]          [4.7k]  <-- REQUIRED!
                              |               |
  Pico GP4 (SDA) -------------+---------------+--- Sensor SDA (Pin 3)
                                              |
  Pico GP5 (SCL) -----------------------------+--- Sensor SCL (Pin 4)
  
  Pico GND --------------------------------------- Sensor GND
""",
        "symptoms": ["OSError: [Errno 110] ETIMEDOUT", "OSError: [Errno 19] ENODEV", "i2c.scan() returns empty []"],
        "checks": [
            "1. Missing Pullups: RP2040 internal pullups are ~50k-80k (too weak). Add external 4.7kΩ resistors to 3.3V.",
            "2. Address Mismatch: Run `i2c.scan()` to detect hexadecimal addresses (e.g. 0x27, 0x3C, 0x68).",
            "3. Bus Lockup Recovery: If SDA is held LOW by a stuck slave, toggle SCL 9 times manually to clock out stuck bit."
        ]
    },

    "3": {
        "title": "Power Rail Brownout & Decoupling Capacitor Fix",
        "diagram": """
  +----------------------------------------------------------------+
  |  SWITCHING NOISE SUPPRESSION & BROWNOUT PREVENTION             |
  +----------------------------------------------------------------+
  Power In (VBUS 5V / Batt 3.7V)
       +--------+---------+--------------------+-----> MCU VREG
       |        |         |                    |
     [===]    [===]     [===]                [===]
    100uF     10uF      0.1uF (Ceramic 104)  0.01uF
  (Bulk El) (Tantalum) (High-Freq Noise)    (RF Decouple)
       |        |         |                    |
  GND -+--------+---------+--------------------+-----> System GND
""",
        "symptoms": ["Pico reboots when relay/motor turns on", "Random MemoryAllocationError or HardFault crash"],
        "checks": [
            "1. Place a 0.1μF ceramic capacitor directly across VCC and GND pins within 5mm of the MCU.",
            "2. Add 100μF to 470μF electrolytic capacitor across power rails near motors/relays to absorb inrush current.",
            "3. Always use a 1N4007 flyback diode reverse-biased across inductive relay coils to clamp back-EMF spikes."
        ]
    },

    "4": {
        "title": "MicroPython RAM Heap Exhaustion & Fragmentation",
        "diagram": """
  +----------------------------------------------------------------+
  |  HEAP FRAGMENTATION DIAGNOSTIC MEMORY MAP                      |
  +----------------------------------------------------------------+
  SRAM (264KB):
  [ MicroPython VM Core (~32KB) ]
  [ FREE BLOCK 1 (4KB) ][ ALLOC (1KB) ][ FREE BLOCK 2 (8KB) ][ ALLOC ]
  --> Fragmentation prevents large contiguous buffer allocation!
  
  SOLUTION: Pre-allocate buffers & invoke gc.collect() periodically.
""",
        "symptoms": ["MemoryAllocationError: Out of memory", "Garbage collection taking >50ms in time-critical loops"],
        "checks": [
            "1. Run `import gc; gc.collect()` before heavy operations.",
            "2. Pre-allocate bytearrays: `buf = bytearray(1024)` globally instead of creating new strings in loops.",
            "3. Use `const()` from micropython module: `from micropython import const; PIN_A = const(15)` to avoid runtime dict lookup.",
            "4. For ISR handlers: Always wrap with `@micropython.native` or schedule deferred work using `micropython.schedule()`."
        ]
    },

    "5": {
        "title": "UART Serial Framing Error & Baud Rate Drift",
        "diagram": """
  +----------------------------------------------------------------+
  |  UART TX/RX CROSSOVER CONNECTION                               |
  +----------------------------------------------------------------+
   RASPBERRY PI PICO                   EXTERNAL MODULE (GPS/GSM/ESP)
  +--------------------+              +--------------------+
  | GP0 (UART0 TX) ----+------------->| RXD (Data In)      |
  | GP1 (UART0 RX) <---+--------------| TXD (Data Out)     |
  | GND ---------------+--------------| GND (Common Ref)   |
  +--------------------+              +--------------------+
  ⚠️ Rule 1: TX always goes to RX. RX always goes to TX.
  ⚠️ Rule 2: Common GND is mandatory. Without shared ground, logic levels float.
""",
        "symptoms": ["Garbage characters (e.g. ) received", "UART.read() returns None", "Framing / Overrun error"],
        "checks": [
            "1. Verify both devices share the exact same baud rate (e.g. 9600, 115200).",
            "2. Check for logic level inversion (RS232 ±12V requires MAX3232 transceiver; do NOT connect to 3.3V UART directly).",
            "3. Ensure TX/RX lines are crossed over (Pico TX -> Device RX, Pico RX -> Device TX)."
        ]
    }
}

class TechManualEngine:
    def __init__(self):
        self.manuals = MANUALS

    def list_topics(self):
        print("\n" + "=" * 65)
        print(" 📖 OTMB ASCII TECHNICAL TROUBLESHOOTING MANUALS")
        print("=" * 65)
        for key, m in sorted(self.manuals.items()):
            print(" [{}] {}".format(key, m["title"]))
        print("=" * 65)

    def print_manual(self, key):
        if key not in self.manuals:
            print("Topic [{}] not found.".format(key))
            return
        m = self.manuals[key]
        print("\n" + "=" * 70)
        print(" 🔧 MANUAL #{}: {}".format(key, m["title"].upper()))
        print("=" * 70)
        print(m["diagram"])
        print(" ⚠️ Common Symptoms & Error Signatures:")
        for s in m["symptoms"]:
            print("   • " + s)
        print("\n 🔍 Diagnostic Checks & Step-by-Step Fixes:")
        for c in m["checks"]:
            print("   " + c)
        print("=" * 70 + "\n")

def run_tech_manual():
    engine = TechManualEngine()
    engine.list_topics()
    print("\n--- Displaying Sample Manual #2 (I2C Bus Diagnostics) ---")
    engine.print_manual("2")

if __name__ == "__main__":
    run_tech_manual()
