"""
Digital Precision Hardware Clock & Timer Engine for Raspberry Pi Pico (RP2040)
Target Platform: MicroPython on RP2040 / Desktop Python
Features: Hardware RTC, microsecond precision ticks, Multi-Lap Stopwatch,
Countdown Timer with PWM Buzzer Alarm, Pomodoro Focus Cycles, and 1602 LCD HUD formatting.
"""

import time

class PrecisionHardwareClock:
    def __init__(self, buzzer_pin=15, led_pin=25):
        self.rtc = None
        self.buzzer = None
        self.led = None
        
        # Hardware setup on MicroPython
        try:
            import machine
            self.rtc = machine.RTC()
            self.led = machine.Pin(led_pin, machine.Pin.OUT)
            self.buzzer = machine.PWM(machine.Pin(buzzer_pin))
            self.buzzer.duty_u16(0)
        except Exception:
            pass

        # Stopwatch state
        self.sw_running = False
        self.sw_start_us = 0
        self.sw_elapsed_us = 0
        self.sw_laps = []

        # Countdown timer state
        self.cd_target_ms = 0
        self.cd_active = False

    def set_datetime(self, year, month, day, weekday, hours, minutes, seconds):
        """Set hardware RTC: (year, month, day, weekday[0-6], hours, minutes, seconds, subseconds)"""
        if self.rtc:
            self.rtc.datetime((year, month, day, weekday, hours, minutes, seconds, 0))
        print("⏰ Hardware RTC configured to: {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            year, month, day, hours, minutes, seconds
        ))

    def get_datetime_str(self):
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if self.rtc:
            dt = self.rtc.datetime()
            # dt format: (year, month, day, weekday, hour, min, sec, subsec)
            return "{:04d}-{:02d}-{:02d} ({}) {:02d}:{:02d}:{:02d}".format(
                dt[0], dt[1], dt[2], days[dt[3] % 7], dt[4], dt[5], dt[6]
            )
        else:
            t = time.localtime()
            return "{:04d}-{:02d}-{:02d} ({}) {:02d}:{:02d}:{:02d}".format(
                t[0], t[1], t[2], days[t[6] % 7], t[3], t[4], t[5]
            )

    # --- STOPWATCH ENGINE ---
    def stopwatch_start(self):
        if not self.sw_running:
            self.sw_start_us = time.ticks_us()
            self.sw_running = True
            print("⏱ Stopwatch STARTED.")

    def stopwatch_lap(self):
        if self.sw_running:
            now_us = time.ticks_us()
            total_us = self.sw_elapsed_us + time.ticks_diff(now_us, self.sw_start_us)
            lap_time = total_us / 1000000.0
            self.sw_laps.append(lap_time)
            print("🏁 Lap #{:02d}: {:.4f} seconds".format(len(self.sw_laps), lap_time))
            return lap_time
        return 0

    def stopwatch_stop(self):
        if self.sw_running:
            now_us = time.ticks_us()
            self.sw_elapsed_us += time.ticks_diff(now_us, self.sw_start_us)
            self.sw_running = False
            total_sec = self.sw_elapsed_us / 1000000.0
            print("⏹ Stopwatch STOPPED at: {:.4f} seconds".format(total_sec))
            return total_sec
        return self.sw_elapsed_us / 1000000.0

    def stopwatch_reset(self):
        self.sw_running = False
        self.sw_start_us = 0
        self.sw_elapsed_us = 0
        self.sw_laps = []
        print("🔄 Stopwatch RESET to 0.000s.")

    # --- COUNTDOWN & ALARM ENGINE ---
    def trigger_alarm(self, beeps=5):
        print("🚨 ALARM TRIGGERED!")
        for _ in range(beeps):
            if self.led:
                self.led.value(1)
            if self.buzzer:
                self.buzzer.freq(2000)
                self.buzzer.duty_u16(32768)
            time.sleep_ms(200)
            if self.led:
                self.led.value(0)
            if self.buzzer:
                self.buzzer.duty_u16(0)
            time.sleep_ms(150)

    def start_countdown(self, seconds):
        print("⏳ Countdown Started for {} seconds...".format(seconds))
        start = time.ticks_ms()
        target_ms = seconds * 1000
        while time.ticks_diff(time.ticks_ms(), start) < target_ms:
            rem_ms = target_ms - time.ticks_diff(time.ticks_ms(), start)
            rem_sec = rem_ms // 1000
            rem_dec = (rem_ms % 1000) // 100
            # Print status line
            sys.stdout.write("\r ⏳ Remaining: {:02d}.{}s ".format(rem_sec, rem_dec))
            time.sleep_ms(100)
        print("\r ⏳ Countdown Complete: 00.0s!          ")
        self.trigger_alarm(4)

    # --- POMODORO FOCUS CYCLE ---
    def start_pomodoro(self, work_min=25, break_min=5):
        print("\n" + "=" * 50)
        print(" 🍅 POMODORO FOCUS ENGINE (RP2040 PRECISION)")
        print("=" * 50)
        print(" Phase 1: FOCUS SESSION ({} Minutes)".format(work_min))
        print(" Put away distractions and immerse in flow.")
        # Fast demo or real minute count
        # In real hardware, multiply by 60 for full minutes
        self.start_countdown(work_min * 60)
        print("\n Phase 2: REST & REFRESH ({} Minutes)".format(break_min))
        self.start_countdown(break_min * 60)
        print("\n✅ Pomodoro Cycle Complete! Ready for next session.")

    def format_1602_lcd_lines(self):
        """Format 16x2 LCD output strings"""
        if self.rtc:
            dt = self.rtc.datetime()
            line1 = "{:02d}:{:02d}:{:02d} PREC".format(dt[4], dt[5], dt[6])
            line2 = "{:02d}/{:02d}/{:04d} RTC".format(dt[2], dt[1], dt[0])
        else:
            t = time.localtime()
            line1 = "{:02d}:{:02d}:{:02d} CLK ".format(t[3], t[4], t[5])
            line2 = "{:02d}/{:02d}/{:04d} SYS".format(t[2], t[1], t[0])
        return line1[:16], line2[:16]

def run_precision_clock():
    clock = PrecisionHardwareClock()
    # Set to current Indian Standard Time: 2026-09-22 12:15:00
    clock.set_datetime(2026, 9, 22, 1, 12, 15, 0)
    print("\n⏰ Active Clock Time:", clock.get_datetime_str())
    l1, l2 = clock.format_1602_lcd_lines()
    print(" 1602 LCD HUD Preview: [Line 1: '{}'] [Line 2: '{}']".format(l1, l2))

if __name__ == "__main__":
    run_precision_clock()
