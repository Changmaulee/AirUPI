"""
Project Brahmand: 10 Old-School Retro MIDI Ringtones & Jukebox (RP2040)
======================================================================
Hardware:
- Piezo Buzzer / Speaker: PWM on GP15 (Pin 20) or any PWM GPIO
- 1602A LCD Display (GP0-GP5): Displays Ringtone Title & Track Info
- 8x8 LED Matrix (GP10, GP11, GP13): Displays Animated Audio Equalizer Bars / Notes

10 Classic Ringtones Included:
1. Nokia Original Tune (Grande Valse)
2. Samsung Over the Horizon
3. Motorola Hello Moto Jingle
4. Sony Ericsson Retro Polyphonic
5. Apple Marimba Classic
6. Super Mario Bros Overworld Theme
7. Tetris Theme (Korobeiniki)
8. Pac-Man Arcade Theme
9. Mission Impossible Theme
10. Pink Panther Theme

Authored by Chandramouli for Project Brahmand & TimeMeshin.
License: Apache-2.0
"""

import time
from machine import Pin, PWM

# ==============================================================================
# NOTE FREQUENCIES TABLE (Hz)
# ==============================================================================
REST = 0
NOTE_B0  = 31
NOTE_C1  = 33;  NOTE_CS1 = 35;  NOTE_D1  = 37;  NOTE_DS1 = 39;  NOTE_E1  = 41
NOTE_F1  = 44;  NOTE_FS1 = 46;  NOTE_G1  = 49;  NOTE_GS1 = 52;  NOTE_A1  = 55;  NOTE_AS1 = 58;  NOTE_B1  = 62
NOTE_C2  = 65;  NOTE_CS2 = 69;  NOTE_D2  = 73;  NOTE_DS2 = 78;  NOTE_E2  = 82
NOTE_F2  = 87;  NOTE_FS2 = 93;  NOTE_G2  = 98;  NOTE_GS2 = 104; NOTE_A2  = 110; NOTE_AS2 = 117; NOTE_B2  = 123
NOTE_C3  = 131; NOTE_CS3 = 139; NOTE_D3  = 147; NOTE_DS3 = 156; NOTE_E3  = 165
NOTE_F3  = 175; NOTE_FS3 = 185; NOTE_G3  = 196; NOTE_GS3 = 208; NOTE_A3  = 220; NOTE_AS3 = 233; NOTE_B3  = 247
NOTE_C4  = 262; NOTE_CS4 = 277; NOTE_D4  = 294; NOTE_DS4 = 311; NOTE_E4  = 330
NOTE_F4  = 349; NOTE_FS4 = 370; NOTE_G4  = 392; NOTE_GS4 = 415; NOTE_A4  = 440; NOTE_AS4 = 466; NOTE_B4  = 494
NOTE_C5  = 523; NOTE_CS5 = 554; NOTE_D5  = 587; NOTE_DS5 = 622; NOTE_E5  = 659
NOTE_F5  = 698; NOTE_FS5 = 740; NOTE_G5  = 784; NOTE_GS5 = 831; NOTE_A5  = 880; NOTE_AS5 = 932; NOTE_B5  = 988
NOTE_C6  = 1047;NOTE_CS6 = 1109;NOTE_D6  = 1175;NOTE_DS6 = 1245;NOTE_E6  = 1319
NOTE_F6  = 1397;NOTE_FS6 = 1480;NOTE_G6  = 1568;NOTE_GS6 = 1661;NOTE_A6  = 1760;NOTE_AS6 = 1865;NOTE_B6  = 1976
NOTE_C7  = 2093;NOTE_CS7 = 2217;NOTE_D7  = 2349;NOTE_DS7 = 2489;NOTE_E7  = 2637

# ==============================================================================
# 10 ICONIC RETRO RINGTONE TRACK DEFINITIONS: [(freq, duration_ms), ...]
# ==============================================================================

RINGTONES = {
    # 1. Nokia Original Tune (Grande Valse by Francisco Tárrega)
    "nokia_tune": {
        "title": "NOKIA ORIGINAL",
        "artist": "Grande Valse (1994)",
        "notes": [
            (NOTE_E5, 125), (NOTE_D5, 125), (NOTE_FS4, 250), (NOTE_GS4, 250),
            (NOTE_CS5, 125), (NOTE_B4, 125), (NOTE_D4, 250), (NOTE_E4, 250),
            (NOTE_B4, 125), (NOTE_A4, 125), (NOTE_CS4, 250), (NOTE_E4, 250),
            (NOTE_A4, 500)
        ]
    },
    
    # 2. Samsung Over the Horizon (Classic Signature Galaxy Tone)
    "samsung_horizon": {
        "title": "SAMSUNG GALAXY",
        "artist": "Over the Horizon",
        "notes": [
            (NOTE_C5, 150), (NOTE_D5, 150), (NOTE_G4, 200), (NOTE_E5, 150),
            (NOTE_D5, 300), (NOTE_G5, 400), (NOTE_E5, 200), (NOTE_D5, 150),
            (NOTE_C5, 150), (NOTE_D5, 200), (NOTE_G5, 300), (NOTE_C6, 600)
        ]
    },

    # 3. Motorola "Hello Moto" Jingle
    "motorola_moto": {
        "title": "MOTOROLA JINGLE",
        "artist": "Hello Moto (2004)",
        "notes": [
            (NOTE_E5, 150), (NOTE_G5, 150), (NOTE_E5, 150), (NOTE_C5, 150),
            (NOTE_D5, 300), (REST, 50),     (NOTE_G4, 150), (NOTE_B4, 150),
            (NOTE_D5, 150), (NOTE_G5, 450)
        ]
    },

    # 4. Sony Ericsson Retro Polyphonic
    "sony_ericsson": {
        "title": "SONY ERICSSON",
        "artist": "Classic Polyphonic",
        "notes": [
            (NOTE_A4, 120), (NOTE_C5, 120), (NOTE_E5, 120), (NOTE_A5, 240),
            (NOTE_G5, 120), (NOTE_E5, 120), (NOTE_C5, 240), (NOTE_D5, 120),
            (NOTE_E5, 120), (NOTE_F5, 120), (NOTE_E5, 120), (NOTE_D5, 360)
        ]
    },

    # 5. Apple Marimba Classic (iPhone Original)
    "apple_marimba": {
        "title": "APPLE MARIMBA",
        "artist": "iPhone Classic (2007)",
        "notes": [
            (NOTE_C5, 100), (NOTE_E5, 100), (NOTE_G5, 100), (NOTE_C6, 100),
            (NOTE_E6, 100), (NOTE_C6, 100), (NOTE_G5, 100), (NOTE_E5, 100),
            (NOTE_D5, 100), (NOTE_FS5, 100), (NOTE_A5, 100), (NOTE_D6, 100),
            (NOTE_FS6, 100), (NOTE_D6, 100), (NOTE_A5, 100), (NOTE_FS5, 100)
        ]
    },

    # 6. Super Mario Bros Overworld Theme
    "super_mario": {
        "title": "SUPER MARIO BROS",
        "artist": "Koji Kondo (1985)",
        "notes": [
            (NOTE_E5, 130), (NOTE_E5, 130), (REST, 130), (NOTE_E5, 130),
            (REST, 130), (NOTE_C5, 130), (NOTE_E5, 130), (REST, 130),
            (NOTE_G5, 260), (REST, 260), (NOTE_G4, 260)
        ]
    },

    # 7. Tetris Theme A (Korobeiniki)
    "tetris": {
        "title": "TETRIS THEME A",
        "artist": "Korobeiniki (1989)",
        "notes": [
            (NOTE_E5, 250), (NOTE_B4, 125), (NOTE_C5, 125), (NOTE_D5, 250),
            (NOTE_C5, 125), (NOTE_B4, 125), (NOTE_A4, 250), (NOTE_A4, 125),
            (NOTE_C5, 125), (NOTE_E5, 250), (NOTE_D5, 125), (NOTE_C5, 125),
            (NOTE_B4, 375), (NOTE_C5, 125), (NOTE_D5, 250), (NOTE_E5, 250),
            (NOTE_C5, 250), (NOTE_A4, 250), (NOTE_A4, 500)
        ]
    },

    # 8. Pac-Man Arcade Theme
    "pacman": {
        "title": "PAC-MAN THEME",
        "artist": "Namco Arcade (1980)",
        "notes": [
            (NOTE_B4, 120), (NOTE_B5, 120), (NOTE_FS5, 120), (NOTE_DS5, 120),
            (NOTE_B5, 120), (NOTE_FS5, 120), (NOTE_DS5, 240), (NOTE_C5, 120),
            (NOTE_C6, 120), (NOTE_G5, 120), (NOTE_E5, 120), (NOTE_C6, 120),
            (NOTE_G5, 120), (NOTE_E5, 240)
        ]
    },

    # 9. Mission Impossible Theme
    "mission_impossible": {
        "title": "MISSION IMPOSSIBLE",
        "artist": "Lalo Schifrin (1966)",
        "notes": [
            (NOTE_G4, 200), (REST, 50), (NOTE_G4, 200), (REST, 50),
            (NOTE_AS4, 150), (NOTE_C5, 150), (NOTE_G4, 200), (REST, 50),
            (NOTE_G4, 200), (REST, 50), (NOTE_F4, 150), (NOTE_FS4, 150),
            (NOTE_G4, 200), (REST, 50), (NOTE_G4, 200)
        ]
    },

    # 10. The Pink Panther Theme
    "pink_panther": {
        "title": "THE PINK PANTHER",
        "artist": "Henry Mancini (1963)",
        "notes": [
            (NOTE_DS4, 150), (NOTE_E4, 300), (REST, 150), (NOTE_FS4, 150),
            (NOTE_G4, 300), (REST, 150), (NOTE_DS4, 150), (NOTE_E4, 200),
            (NOTE_FS4, 150), (NOTE_G4, 200), (NOTE_C5, 150), (NOTE_B4, 200),
            (NOTE_E4, 150), (NOTE_G4, 200), (NOTE_B4, 150), (NOTE_AS4, 500)
        ]
    }
}

# ==============================================================================
# RETRO RINGTONE PLAYER & EQUALIZER HUD
# ==============================================================================

class MidiRingtonePlayer:
    def __init__(self, buzzer_pin=15):
        self.buzzer = PWM(Pin(buzzer_pin))
        self.buzzer.duty_u16(0) # Start silent
        
        # Displays
        self.lcd = None
        try:
            from lcd1602 import GpioLcd1602
            self.lcd = GpioLcd1602(rs_pin=0, e_pin=1, d4_pin=2, d5_pin=3, d6_pin=4, d7_pin=5)
        except Exception:
            pass

        self.matrix = None
        try:
            from max7219_8x8 import Max7219_8x8
            self.matrix = Max7219_8x8(sck_pin=10, mosi_pin=11, cs_pin=13, brightness=7)
        except Exception:
            pass

    def play_tone(self, freq, duration_ms):
        if freq > 0:
            self.buzzer.freq(freq)
            self.buzzer.duty_u16(32768) # 50% duty cycle
        else:
            self.buzzer.duty_u16(0)

        # Draw audio visualizer EQ bars on 8x8 matrix
        if self.matrix and freq > 0:
            # Map frequency to dynamic bar heights
            bar_height = min(8, max(1, int((freq / 1200.0) * 8)))
            frame = bytearray(8)
            for r in range(8 - bar_height, 8):
                frame[r] = 0b10111101
            self.matrix.show_bitmap(frame)

        time.sleep_ms(duration_ms)
        self.buzzer.duty_u16(0)
        time.sleep_ms(25) # Small staccato pause between notes

    def play_ringtone(self, tone_key):
        if tone_key not in RINGTONES:
            print(f"Ringtone '{tone_key}' not found!")
            return

        tune = RINGTONES[tone_key]
        title = tune["title"]
        artist = tune["artist"]

        print(f"\n🎵 Now Playing: {title} ({artist})")
        if self.lcd:
            self.lcd.display_ai_card(f"RINGTONE: {title[:7]}", f"{artist[:16]}")

        for freq, dur in tune["notes"]:
            self.play_tone(freq, dur)

        if self.matrix:
            self.matrix.clear()
        if self.lcd:
            self.lcd.display_ai_card("JUKEBOX READY", "SELECT TRACK 1-10")

    def play_all_jukebox(self):
        print("=================================================================")
        print(" [PROJECT BRAHMAND] 10 OLD-SCHOOL RETRO MIDI RINGTONES JUKEBOX")
        print(" Hardware: PWM Buzzer on GP15 + 1602A LCD + 8x8 LED Equalizer")
        print("=================================================================")

        track_keys = list(RINGTONES.keys())
        for idx, key in enumerate(track_keys, 1):
            info = RINGTONES[key]
            print(f"Track {idx:2d}/10: {info['title']:<20} | {info['artist']}")
            self.play_ringtone(key)
            time.sleep(1.0) # Pause between tracks

        print("\n[+] Jukebox playback complete!")

if __name__ == "__main__":
    player = MidiRingtonePlayer(buzzer_pin=15)
    player.play_all_jukebox()
