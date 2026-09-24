"""
Project Brahmand: Retro Snake Game with Levels (RP2040)
========================================================
Hardware Targets:
- 16-Pin Direct 8x8 LED Matrix (GP6-GP13 Rows, GP14-GP21 Cols) OR MAX7219 SPI Matrix (GP10, GP11, GP13)
- 1602A Character LCD (GP0-GP5): Live Scoreboard & Level HUD
- Onboard LED (GP25): Food eat & Level up flash
- Controls:
  - Hardware Buttons: UP=GP16 (or GP26 if using GP16 for matrix), DOWN=GP27, etc.
  - USB Serial Keyboard: 'w' (Up), 's' (Down), 'a' (Left), 'd' (Right), 'q' (Quit)
  - Auto-Demo AI Mode: Automatically plays smoothly if no manual input is given!

Features:
- 5 Progressive Difficulty Levels with unique obstacle maps and speeds
- Dynamic food spawning (blinking LED)
- High score tracking across rounds
"""

import time
import random
from machine import Pin

# 1. Onboard LED
try:
    led = Pin(25, Pin.OUT)
except Exception:
    led = None

def blink_led(times=1, delay=0.03):
    if led:
        for _ in range(times):
            led.value(1)
            time.sleep(delay)
            led.value(0)
            time.sleep(delay)

# 2. Displays Auto-Detection
# A. LCD Scoreboard
lcd = None
try:
    from hd44780_lcd import HD44780_GPIO
    lcd = HD44780_GPIO(rs_pin=0, e_pin=1, d4_pin=2, d5_pin=3, d6_pin=4, d7_pin=5)
except Exception:
    try:
        from lcd1602 import GpioLcd1602
        lcd = GpioLcd1602(rs_pin=0, e_pin=1, d4_pin=2, d5_pin=3, d6_pin=4, d7_pin=5)
    except Exception:
        pass

# B. 8x8 Display Matrix (Prioritize 16-Pin bare matrix, fallback to MAX7219)
matrix = None
BITMAPS = {}

try:
    from matrix_16pin import Matrix16Pin, BITMAPS as BM16
    matrix = Matrix16Pin(row_gpios=[6, 7, 8, 9, 10, 11, 12, 13], 
                         col_gpios=[14, 15, 16, 17, 18, 19, 20, 21], 
                         anode_rows=True)
    BITMAPS = BM16
    print("[+] 16-Pin Direct 8x8 LED Matrix Initialized with Hardware ISR Multiplexing!")
except Exception as e:
    try:
        from max7219_8x8 import Max7219_8x8, BITMAPS as BM7219
        matrix = Max7219_8x8(sck_pin=10, mosi_pin=11, cs_pin=13, brightness=6)
        BITMAPS = BM7219
        print("[+] MAX7219 8x8 LED Matrix Initialized!")
    except Exception:
        print("[!] Running in Console Grid Mode (No physical matrix detected).")

# 3. Hardware Pushbuttons (GP22, GP26, GP27, GP28 with Internal Pull-Up to not conflict with matrix)
btn_up = Pin(22, Pin.IN, Pin.PULL_UP) if hasattr(Pin, "PULL_UP") else None
btn_down = Pin(26, Pin.IN, Pin.PULL_UP) if hasattr(Pin, "PULL_UP") else None
btn_left = Pin(27, Pin.IN, Pin.PULL_UP) if hasattr(Pin, "PULL_UP") else None
btn_right = Pin(28, Pin.IN, Pin.PULL_UP) if hasattr(Pin, "PULL_UP") else None

# 4. Level Definitions (Obstacles, Target Score, Speed in Seconds)
LEVELS = [
    {
        "level": 1,
        "name": "OPEN MEADOW",
        "speed": 0.28,
        "target_score": 4,
        "obstacles": []
    },
    {
        "level": 2,
        "name": "CANYON PILLARS",
        "speed": 0.24,
        "target_score": 5,
        "obstacles": [(3, 3), (4, 4)]
    },
    {
        "level": 3,
        "name": "STONE LABYRINTH",
        "speed": 0.20,
        "target_score": 6,
        "obstacles": [(2, 2), (2, 5), (5, 2), (5, 5)]
    },
    {
        "level": 4,
        "name": "FORTRESS GATES",
        "speed": 0.16,
        "target_score": 7,
        "obstacles": [(1, 1), (1, 6), (6, 1), (6, 6), (3, 4), (4, 3)]
    },
    {
        "level": 5,
        "name": "SOVEREIGN BOSS",
        "speed": 0.12,
        "target_score": 8,
        "obstacles": [(3, 1), (3, 6), (4, 1), (4, 6), (1, 3), (6, 3), (1, 4), (6, 4)]
    }
]

class SnakeGame:
    def __init__(self):
        self.high_score = 0
        self.reset_game()

    def reset_game(self):
        self.level_idx = 0
        self.score = 0
        self.total_eaten = 0
        self.is_game_over = False
        self.is_victory = False
        self.init_level()

    def init_level(self):
        cfg = LEVELS[self.level_idx]
        self.obstacles = set(cfg["obstacles"])
        self.speed = cfg["speed"]
        self.level_eaten = 0
        self.target_eaten = cfg["target_score"]
        
        # Initial snake in center (length 3, moving RIGHT)
        self.snake = [(3, 2), (3, 1), (3, 0)]
        self.dir = (0, 1) # (dy, dx) -> RIGHT
        self.spawn_food()
        
        if lcd:
            try:
                lcd.print_line(0, f"LVL:{cfg['level']} {cfg['name'][:10]}")
                lcd.print_line(1, f"SCORE:{self.score:<3} GOAL:{self.target_eaten}")
            except Exception:
                pass
        print(f"\n--- LEVEL {cfg['level']}: {cfg['name']} (Speed: {int(self.speed*1000)}ms, Goal: {self.target_eaten}) ---")

    def spawn_food(self):
        occupied = set(self.snake) | self.obstacles
        free_cells = [(r, c) for r in range(8) for c in range(8) if (r, c) not in occupied]
        if free_cells:
            self.food = random.choice(free_cells)
        else:
            self.food = (0, 0)

    def read_input(self):
        # 1. Hardware buttons (active LOW on GP22, GP26, GP27, GP28)
        try:
            if btn_up and btn_up.value() == 0 and self.dir != (1, 0):
                return (-1, 0)
            if btn_down and btn_down.value() == 0 and self.dir != (-1, 0):
                return (1, 0)
            if btn_left and btn_left.value() == 0 and self.dir != (0, 1):
                return (0, -1)
            if btn_right and btn_right.value() == 0 and self.dir != (0, -1):
                return (0, 1)
        except Exception:
            pass
        return None

    def auto_ai_step(self):
        """
        Smart Greedy AI: Safely paths towards food avoiding walls, body, and obstacles.
        """
        head_r, head_c = self.snake[0]
        food_r, food_c = self.food
        
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # Filter 180-degree reverse
        possible_moves = [m for m in possible_moves if (m[0] != -self.dir[0] or m[1] != -self.dir[1])]
        
        best_move = self.dir
        min_dist = 999
        occupied = set(self.snake[:-1]) | self.obstacles

        # Sort moves by Manhattan distance to food
        for move in possible_moves:
            nr = head_r + move[0]
            nc = head_c + move[1]
            
            # Wall collisions
            if not (0 <= nr < 8 and 0 <= nc < 8):
                continue
            # Body/Obstacle collisions
            if (nr, nc) in occupied:
                continue
                
            dist = abs(nr - food_r) + abs(nc - food_c)
            if dist < min_dist:
                min_dist = dist
                best_move = move
                
        return best_move

    def update(self, new_dir):
        if new_dir:
            self.dir = new_dir
            
        head_r, head_c = self.snake[0]
        dy, dx = self.dir
        nr = head_r + dy
        nc = head_c + dx

        # Check Wall Collision
        if not (0 <= nr < 8 and 0 <= nc < 8):
            self.is_game_over = True
            return

        # Check Obstacle or Self-Collision
        new_head = (nr, nc)
        if new_head in self.obstacles or new_head in self.snake[:-1]:
            self.is_game_over = True
            return

        # Move Snake
        self.snake.insert(0, new_head)
        
        # Check Food
        if new_head == self.food:
            self.score += (self.level_idx + 1) * 10
            self.total_eaten += 1
            self.level_eaten += 1
            if self.score > self.high_score:
                self.high_score = self.score
                
            blink_led(1, 0.02)
            
            # Check Level Up
            if self.level_eaten >= self.target_eaten:
                self.level_up()
            else:
                self.spawn_food()
                if lcd:
                    try:
                        lvl_num = LEVELS[self.level_idx]["level"]
                        lcd.print_line(0, f"LVL:{lvl_num} SCORE:{self.score:<4}")
                        lcd.print_line(1, f"LEFT:{self.target_eaten - self.level_eaten} BEST:{self.high_score}")
                    except Exception:
                        pass
        else:
            self.snake.pop() # Remove tail

    def level_up(self):
        blink_led(3, 0.05)
        self.level_idx += 1
        
        if self.level_idx >= len(LEVELS):
            self.is_victory = True
            if lcd:
                try:
                    lcd.print_line(0, "GAME WON! VICTORY")
                    lcd.print_line(1, f"FINAL SCORE:{self.score}")
                except Exception:
                    pass
            print(f"\n🎉 VICTORY! ALL {len(LEVELS)} LEVELS CONQUERED! SCORE: {self.score}")
            return
            
        if lcd:
            try:
                lcd.print_line(0, ">>> LEVEL UP! <<<")
                lcd.print_line(1, f"NOW ON LEVEL {LEVELS[self.level_idx]['level']}")
            except Exception:
                pass
            
        if matrix and "CHECK_MARK" in BITMAPS:
            for _ in range(2):
                matrix.clear()
                time.sleep(0.1)
                matrix.show_bitmap(BITMAPS["CHECK_MARK"])
                time.sleep(0.2)
                
        time.sleep(1.0)
        self.init_level()

    def render_matrix(self, blink_state):
        if not matrix:
            return
            
        frame = bytearray(8)
        
        # 1. Render Obstacles
        for (r, c) in self.obstacles:
            frame[r] |= (1 << (7 - c))
            
        # 2. Render Snake Body
        for (r, c) in self.snake:
            frame[r] |= (1 << (7 - c))
            
        # 3. Render Food (Blinking)
        fr, fc = self.food
        if blink_state:
            frame[fr] |= (1 << (7 - fc))
            
        matrix.show_bitmap(frame)

def run_snake():
    game = SnakeGame()
    print("=================================================================")
    print(" [RETRO SNAKE WITH 5 LEVELS] RUNNING ON RASPBERRY PI PICO")
    print(" Hardware: 16-Pin Direct Matrix (GP6-GP21) + 1602A LCD (GP0-GP5)")
    print(" Control: Auto-AI Autopilot Mode Active | Press Buttons if wired")
    print("=================================================================")

    blink_counter = 0
    while True:
        # Check input (Hardware button or Autonomous AI)
        user_input = game.read_input()
        if user_input is None:
            chosen_dir = game.auto_ai_step()
        else:
            chosen_dir = user_input

        game.update(chosen_dir)
        blink_counter = (blink_counter + 1) % 2
        game.render_matrix(blink_state=(blink_counter == 0))

        if game.is_game_over:
            blink_led(4, 0.08)
            if lcd:
                try:
                    lcd.print_line(0, "GAME OVER! :(")
                    lcd.print_line(1, f"SCORE:{game.score} BEST:{game.high_score}")
                except Exception:
                    pass
            if matrix:
                matrix.show_bitmap(bytes([0x81, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x81]))
            print(f"\n💀 GAME OVER! Final Score: {game.score} | Highest Score: {game.high_score}")
            time.sleep(2.5)
            game.reset_game()
            
        if game.is_victory:
            if matrix:
                matrix.show_bitmap(BITMAPS.get("SMILE", BITMAPS.get("CHECK_MARK", bytes(8))))
            time.sleep(3.5)
            game.reset_game()

        time.sleep(game.speed)

if __name__ == "__main__":
    run_snake()
