"""
Project Brahmand: Multi-Patch Pitch Bending Synthesizer (RP2040)
================================================================
Instruments Supported:
1. 🎹 PIANO PATCH: Pure harmonic chromatic tones with fine-pitch modulation (+/-2 semitones).
2. 🎸 GUITAR PATCH: Overdriven whammy bar dive-bomb (+/-12 semitones / full octave pitch bend).
3. 🎛️ SYNTH LEAD: Continuous microtonal portamento glide, sub-harmonics (+/-24 semitones dual octave sweep).

Hardware Setup on Raspberry Pi Pico:
- Potentiometer (Pitch Bend Wheel):
  * Outer Pin 1 -> 3V3 (Pin 36)
  * Outer Pin 2 -> GND (Pin 38)
  * Wiper (Center) -> GP26 / ADC0 (Pin 31)
- Audio Output (Buzzer / Speaker): PWM on GP15 (Pin 20)
- Note Buttons (Optional): GP16 (C4), GP17 (E4), GP18 (G4), GP19 (A4)
- Patch Switch Button: GP14 (Pin 19) or 'p' in serial terminal
- Live Displays: 1602A LCD + 8x8 LED Matrix Oscilloscope Waveform

Authored by Chandramouli for Project Brahmand & TimeMeshin.
License: Apache-2.0
"""

import time
import math
from machine import Pin, PWM, ADC

# 1. Hardware Pin Initialization
pot = ADC(Pin(26))       # GP26 (ADC0) for Pitch Bend Potentiometer
buzzer = PWM(Pin(15))    # GP15 for Audio PWM Output
buzzer.duty_u16(0)       # Start silent

btn_note1 = Pin(16, Pin.IN, Pin.PULL_UP) # C4
btn_note2 = Pin(17, Pin.IN, Pin.PULL_UP) # E4
btn_note3 = Pin(18, Pin.IN, Pin.PULL_UP) # G4
btn_note4 = Pin(19, Pin.IN, Pin.PULL_UP) # A4
btn_patch = Pin(14, Pin.IN, Pin.PULL_UP) # Switch Patch

# 2. Displays Auto-Detection
lcd = None
try:
    from lcd1602 import GpioLcd1602
    lcd = GpioLcd1602(rs_pin=0, e_pin=1, d4_pin=2, d5_pin=3, d6_pin=4, d7_pin=5)
except Exception:
    pass

matrix = None
try:
    from max7219_8x8 import Max7219_8x8
    matrix = Max7219_8x8(sck_pin=10, mosi_pin=11, cs_pin=13, brightness=7)
except Exception:
    pass

# 3. Base Musical Notes (Hz)
NOTES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25,
    "E5": 659.25,
    "G5": 783.99
}

# 4. Instrument Patch Profiles
PATCHES = [
    {
        "id": "piano",
        "name": "ACOUSTIC PIANO",
        "icon": "🎹",
        "max_bend_semitones": 2.0,   # Standard +/- 2 semitone pitch wheel
        "duty": 32768,               # 50% square/pulse wave
        "description": "Standard +/-2s"
    },
    {
        "id": "guitar",
        "name": "ELECTRIC GUITAR",
        "icon": "🎸",
        "max_bend_semitones": 12.0,  # Full octave whammy dive bomb
        "duty": 24000,               # Asymmetric pulse for rich guitar overdrive
        "description": "Whammy +/-12s"
    },
    {
        "id": "synth",
        "name": "ANALOG MOOG SYNTH",
        "icon": "🎛️",
        "max_bend_semitones": 24.0,  # 2 full octaves hyper-sweep glide
        "duty": 45000,               # Resonant synth lead pulse
        "description": "Sweep +/-24s"
    }
]

class PitchBendSynthesizer:
    def __init__(self):
        self.patch_idx = 0
        self.current_note = "A4"
        self.base_freq = NOTES["A4"]
        self.last_display_time = 0
        self.last_pot_val = 32768
        self.update_patch_display()

    def get_patch(self):
        return PATCHES[self.patch_idx]

    def next_patch(self):
        self.patch_idx = (self.patch_idx + 1) % len(PATCHES)
        self.update_patch_display()
        time.sleep(0.3)

    def update_patch_display(self):
        p = self.get_patch()
        print(f"\n--- INSTRUMENT PATCH: {p['name']} ({p['description']}) ---")
        if lcd:
            lcd.display_ai_card(f"PATCH: {p['name'][:9]}", f"{p['description'][:16]}")

    def read_pitch_bend_semitones(self):
        """
        Reads potentiometer on GP26 (ADC0).
        Calculates pitch bend offset in semitones: Delta_s = ((ADC - 32768) / 32768) * Max_Semitones
        """
        # Average 4 ADC samples to filter noise
        raw_adc = sum(pot.read_u16() for _ in range(4)) // 4
        
        # Deadzone filter around center (+/- 800)
        center = 32768
        diff = raw_adc - center
        if abs(diff) < 800:
            norm_offset = 0.0
        else:
            norm_offset = (diff / 32768.0)
            norm_offset = max(-1.0, min(1.0, norm_offset))

        p = self.get_patch()
        semitones_offset = norm_offset * p["max_bend_semitones"]
        return semitones_offset, raw_adc

    def calculate_bent_frequency(self, base_hz, semitones_offset):
        """
        Equal Temperament Pitch Formula: f_bent = f_base * 2^(semitones / 12)
        """
        bent_freq = base_hz * math.pow(2.0, semitones_offset / 12.0)
        return max(20.0, min(8000.0, bent_freq))

    def render_oscilloscope_matrix(self, bent_freq, semitones_offset):
        """
        Renders real-time dynamic pitch waveform on 8x8 LED matrix.
        Wave expands, contracts, and shifts with the potentiometer dial!
        """
        if not matrix:
            return
            
        frame = bytearray(8)
        # Period scaling based on bent frequency
        freq_factor = max(0.5, min(3.5, bent_freq / 440.0))
        
        for col in range(8):
            # Calculate sine wave amplitude height
            val = math.sin((col * freq_factor * 0.8) + (time.ticks_ms() / 150.0))
            row = int(3.5 + val * 3.0)
            row = max(0, min(7, row))
            frame[row] |= (1 << (7 - col))
            
        matrix.show_bitmap(frame)

    def run_engine(self):
        print("=================================================================")
        print(" [PROJECT BRAHMAND] MULTI-PATCH PITCH BENDING SYNTHESIZER")
        print(" Controls:")
        print(" - Dial Potentiometer on GP26 to bend pitch in real time!")
        print(" - Press Buttons GP16-GP19 (or type in Serial) to play notes")
        print(" - Press Button GP14 (or type 'p') to switch Piano/Guitar/Synth")
        print("=================================================================")

        while True:
            # 1. Check Patch Switch button (GP14)
            if btn_patch.value() == 0:
                self.next_patch()

            # 2. Check Note buttons
            is_active = False
            if btn_note1.value() == 0:
                self.current_note = "C4"
                self.base_freq = NOTES["C4"]
                is_active = True
            elif btn_note2.value() == 0:
                self.current_note = "E4"
                self.base_freq = NOTES["E4"]
                is_active = True
            elif btn_note3.value() == 0:
                self.current_note = "G4"
                self.base_freq = NOTES["G4"]
                is_active = True
            elif btn_note4.value() == 0:
                self.current_note = "A4"
                self.base_freq = NOTES["A4"]
                is_active = True
            else:
                # Default continuous carrier tone for demonstration
                is_active = True

            # 3. Read Potentiometer Pitch Bend
            semitones_offset, raw_adc = self.read_pitch_bend_semitones()
            bent_freq = self.calculate_bent_frequency(self.base_freq, semitones_offset)
            patch = self.get_patch()

            # 4. Output Tone via PWM
            if is_active and bent_freq > 20:
                buzzer.freq(int(round(bent_freq)))
                buzzer.duty_u16(patch["duty"])
            else:
                buzzer.duty_u16(0)

            # 5. Render Waveform on 8x8 Matrix
            self.render_oscilloscope_matrix(bent_freq, semitones_offset)

            # 6. Update 1602A LCD (Throttle to 10 FPS for crisp display)
            now = time.ticks_ms()
            if now - self.last_display_time > 100:
                self.last_display_time = now
                sign = "+" if semitones_offset >= 0 else ""
                bend_str = f"{sign}{semitones_offset:.1f}s"
                
                if lcd:
                    line1 = f"{patch['name'][:8]} {self.current_note:<3} {int(bent_freq)}Hz"[:16]
                    line2 = f"BEND: {bend_str:<6} ADC:{raw_adc:<5}"[:16]
                    lcd.display_ai_card(line1, line2)

            time.sleep(0.01)

def run_synth():
    synth = PitchBendSynthesizer()
    synth.run_engine()

if __name__ == "__main__":
    run_synth()
