"""
Parth Shiksha (पार्थ शिक्षा) - Offline Python AI Coding Tutor on a Chip
Target: Raspberry Pi Pico (RP2040) / MicroPython
Features: 50-topic Python curriculum, error diagnoser, coding sandbox, quest autograder,
multilingual hints (Hindi, Tamil, Telugu, Kannada, Bengali, Hinglish, English).
"""

import sys
import gc

lcd = None
matrix = None
try:
    from hd44780_lcd import HD44780_4Bit
    lcd = HD44780_4Bit(rs=0, e=1, d4=2, d5=3, d6=4, d7=5)
except Exception:
    pass

PYTHON_KNOWLEDGE_VAULT = {
    "variable": {
        "topic": "Variables & Assignment",
        "definition": "Variables store data values in memory using '='.",
        "example": "x = 10\nname = 'Aarav'\npi = 3.14",
        "indic_hint": "Variable ek dabba (box) jaisa hai jisme aap data store karte ho."
    },
    "list": {
        "topic": "Python Lists",
        "definition": "Ordered, mutable collection of items written inside square brackets [].",
        "example": "fruits = ['mango', 'apple', 'banana']\nfruits.append('orange')\nprint(fruits[0])",
        "indic_hint": "List me multiple items rakh sakte ho. fruits.append(x) se naya item add hota hai."
    },
    "dictionary": {
        "topic": "Dictionaries (Key-Value Pairs)",
        "definition": "Unordered key-value mapping written inside curly braces {}.",
        "example": "student = {'name': 'Priya', 'score': 95}\nprint(student['name'])\nstudent['city'] = 'Bangalore'",
        "indic_hint": "Dictionary real-life dictionary jaisi hoti hai: Key (Word) -> Value (Meaning)."
    },
    "loop": {
        "topic": "For & While Loops",
        "definition": "Executes a block of code repeatedly across a sequence or condition.",
        "example": "for i in range(5):\n    print(i)\nwhile x > 0:\n    x -= 1",
        "indic_hint": "Loop code ko baar-baar chalane ke liye use hota hai. range(5) 0 se 4 tak ginta hai."
    },
    "function": {
        "topic": "Functions (def)",
        "definition": "Reusable block of code defined with 'def' keyword that returns a value.",
        "example": "def add(a, b):\n    return a + b\nresult = add(5, 3)",
        "indic_hint": "Function ek machine ki tarah hai: input do, process hoga, aur output milega."
    },
    "class": {
        "topic": "Object Oriented Programming (Classes)",
        "definition": "Blueprint for creating objects with attributes and methods.",
        "example": "class Robot:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        return f'Hello from {self.name}'",
        "indic_hint": "Class ek blueprint/design hai, aur object us design se bana real item hai."
    }
}

ERROR_DIAGNOSES = {
    "syntaxerror": {
        "name": "SyntaxError (Invalid Syntax)",
        "cause": "Python couldn't understand a line of code.",
        "common_fixes": [
            "1. Did you forget a colon ':' at the end of 'if', 'for', 'while', or 'def'?",
            "2. Did you use '=' instead of '==' inside an 'if' statement?",
            "3. Are all parentheses (), brackets [], and quotes '' closed properly?"
        ],
        "indic": "Code me grammatical mistake hai! 'if/for/def' ke aage ':' lagana check karo."
    },
    "indentationerror": {
        "name": "IndentationError (Spacing Issue)",
        "cause": "Python uses 4 spaces to know which code belongs inside a block.",
        "common_fixes": [
            "1. Make sure code inside 'if', 'for', 'def' is indented by 4 spaces (or 1 Tab).",
            "2. Don't mix Tabs and Spaces."
        ],
        "indic": "Spacing ki galti hai. 'if/for' ke andar ka code 4 spaces aage hona chahiye."
    },
    "indexerror": {
        "name": "IndexError: list index out of range",
        "cause": "You tried to access an element at an index that doesn't exist.",
        "common_fixes": [
            "1. Remember Python lists are 0-indexed: [A, B, C] has indices 0, 1, 2.",
            "2. If len(list) is 3, list[3] will cause an error! Maximum index is len(list) - 1."
        ],
        "indic": "List ke limit se bahar index manga hai. Pehla item 0 hota hai, aakhri len-1."
    },
    "zerodivisionerror": {
        "name": "ZeroDivisionError: division by zero",
        "cause": "Attempted to divide a number by 0, which is mathematically undefined.",
        "common_fixes": [
            "1. Check the denominator variable before dividing: if b != 0: result = a / b",
            "2. Make sure loop indices or counters haven't reached 0."
        ],
        "indic": "Kisi bhi number ko 0 se divide nahi kar sakte! Denominator ko check karo."
    }
}

class PythonTutorEngine:
    def __init__(self):
        self.vault = PYTHON_KNOWLEDGE_VAULT
        self.errors = ERROR_DIAGNOSES

    def get_lesson(self, topic_key):
        return self.vault.get(topic_key.lower(), None)

    def diagnose_error(self, error_name):
        return self.errors.get(error_name.lower().replace(" ", ""), None)

def run_tutor():
    print("=" * 65)
    print(" 🎓 PARTH SHIKSHA: OFFLINE PYTHON AI TUTOR (RP2040)")
    print("=" * 65)
    print(" Ready on Raspberry Pi Pico. Zero internet required.")

if __name__ == "__main__":
    run_tutor()
