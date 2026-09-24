"""
TimeMeshin Indic OTM Tokenizer for Raspberry Pi Pico (RP2040 MicroPython)
=========================================================================
Target: Dual ARM Cortex-M0+ @ 133 MHz, 264 KB SRAM, <50 mW Power Envelope.
Supports: 22 Indian Official Languages + English/Hinglish on MicroPython.
Authored by Chandramouli for Project Brahmand.
"""

# Indic Numeral Translation Table (Devanagari, Bengali, Gujarati, Tamil, Telugu, Kannada, Malayalam, Odia, Gurmukhi)
INDIC_DIGIT_MAP = {
    # Devanagari
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
    # Bengali / Assamese
    '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9',
    # Gurmukhi
    '੦': '0', '੧': '1', '੨': '2', '੩': '3', '੪': '4', '੫': '5', '੬': '6', '੭': '7', '੮': '8', '੯': '9',
    # Gujarati
    '૦': '0', '૧': '1', '૨': '2', '૩': '3', '૪': '4', '૫': '5', '૬': '6', '૭': '7', '૮': '8', '૯': '9',
    # Odia
    '୦': '0', '୧': '1', '୨': '2', '୩': '3', '୪': '4', '୫': '5', '୬': '6', '୭': '7', '୮': '8', '୯': '9',
    # Tamil
    '௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4', '௫': '5', '௬': '6', '௭': '7', '௮': '8', '௯': '9',
    # Telugu
    '౦': '0', '౧': '1', '౨': '2', '౩': '3', '౪': '4', '౫': '5', '౬': '6', '౭': '7', '౮': '8', '౯': '9',
    # Kannada
    '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4', '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9',
    # Malayalam
    '൦': '0', '൧': '1', '൨': '2', '൩': '3', '൪': '4', '൫': '5', '൬': '6', '൭': '7', '൮': '8', '൯': '9',
}

PAN_INDIC_SYNSETS = {
    "egg": "egg", "ande": "egg", "anda": "egg", "अंडे": "egg", "अंडा": "egg", "डिम": "egg", "ডিম": "egg",
    "മുട്ട": "egg", "గుడ్డు": "egg", "ಮೊಟ್ಟೆ": "egg", "முட்டை": "egg", "ઇંડું": "egg", "ਇੰਡਾ": "egg", "ଅଣ୍ଡା": "egg",
    "protein": "protein", "प्रोटीन": "protein", "প্রোটিন": "protein", "புரதம்": "protein", "ప్రోటీన్": "protein",
    "heart": "heart", "dil": "heart", "दिल": "heart", "हृदय": "heart", "இதயம்": "heart", "గుండె": "heart",
    "water": "water", "pani": "water", "पानी": "water", "जल": "water", "தண்ணீர்": "water", "నీరు": "water",
    "aircraft": "aircraft", "hawai": "aircraft", "jahaj": "aircraft", "b737": "aircraft", "विमान": "aircraft"
}

class PicoIndicOTMTokenizer:
    def __init__(self):
        pass

    def normalize_numerals(self, text):
        res = []
        for ch in text:
            if ch in INDIC_DIGIT_MAP:
                res.append(INDIC_DIGIT_MAP[ch])
            else:
                res.append(ch)
        return "".join(res)

    def parse_slots(self, text):
        norm = self.normalize_numerals(text)
        words = norm.split()
        qty = 1.0
        has_qty = False

        for w in words:
            clean_num = ''.join(c for c in w if c.isdigit() or c == '.')
            if clean_num:
                try:
                    qty = float(clean_num)
                    has_qty = True
                    break
                except Exception:
                    pass

        # Detect entity
        norm_lower = norm.lower()
        matched_entity = "general"
        for k, v in PAN_INDIC_SYNSETS.items():
            if k in norm_lower:
                matched_entity = v
                break

        # Polarity
        polarity = "NEGATIVE" if any(neg in norm_lower for neg in ["नहीं", "नाही", "இல்லை", "కాదు", "ಇಲ್ಲ", "ഇല്ല", "না", "not", "nahi", "illa"]) else "POSITIVE"

        return {
            "query": text,
            "normalized": norm,
            "quantity": qty,
            "has_quantity": has_qty,
            "entity": matched_entity,
            "polarity": polarity
        }
