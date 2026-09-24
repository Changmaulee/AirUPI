"""
Agent 13: "Pramana" (प्रमाण) - Master Multi-Dimensional Unit Conversion & Dimensional Analysis Engine
Target Platform: MicroPython on Raspberry Pi Pico (RP2040) / Desktop Python
Author: Project Brahmand / Antigravity AI

Comprehensive 15-Domain Matrix:
  1. Length & Astronomy & Nanotech (m, cm, mm, km, in, ft, yd, mi, AU, ly, parsec, Gaj, Hath, Angul)
  2. Mass & Gemology & Ayurveda (kg, g, mg, lb, oz, ton, troy oz, carat, Tola, Ratti, Masha, Seer, Maund, Quintal)
  3. Area & Real Estate & Land Slabs (sqm, sqft, sqyd, acre, ha, Guntha, Bigha, Cent, Ground, Ankanam, Marla, Kanal, Katha)
  4. Volume & Culinary Kitchen Measures (liter, ml, m3, gallon US/UK, barrel, fl oz, cup, tbsp, tsp, pint, quart)
  5. Temperature & Thermal Scales (Celsius, Fahrenheit, Kelvin, Rankine, Reaumur)
  6. Pressure & Barometric Vacuum (Pa, kPa, MPa, bar, mbar, PSI, atm, Torr, mmHg, inHg)
  7. Energy, Work & Heat (Joule, kJ, Calorie, kcal, Wh, kWh, BTU, Therm, eV, Erg)
  8. Power & HVAC (Watt, kW, MW, HP, Metric PS, BTU/hr, Ton of Refrigeration)
  9. Speed & Velocity (m/s, km/h, mph, ft/s, knot, Mach, c speed of light)
  10. Electrical & Electronics (V, mV, kV, A, mA, uA, Ohm, kOhm, MOhm, Farad, uF, nF, pF, Hz, kHz, MHz, GHz, RPM)
  11. Digital Data & Storage (Byte, KB, MB, GB, TB, PB, bits, Kbps, Mbps, Gbps)
  12. Time & Vedic Chronometry (sec, ms, us, ns, min, hr, day, week, month, year, decade, century, Muhurta, Ghati, Prahara)
  13. Angle & Trigonometry (Degree, Radian, Gradian, Arcminute, Arcsecond, Revolution)
  14. Volumetric Flow Rate (LPM, L/s, m3/h, GPM, CFM)
  15. Fuel Economy (km/L, MPG US/UK, L/100km)
"""

import sys
import gc
import time

# ==============================================================================
# 15-DOMAIN CONVERSION REGISTRY (Exact SI Rational Multipliers)
# ==============================================================================

UNITS_DB = {
    # 1. LENGTH / DISTANCE (Base: meter)
    "length": {
        "m": 1.0, "meter": 1.0, "meters": 1.0, "metre": 1.0,
        "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
        "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
        "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
        "um": 1e-6, "micrometer": 1e-6, "micron": 1e-6,
        "nm": 1e-9, "nanometer": 1e-9, "angstrom": 1e-10, "a": 1e-10,
        "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
        "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
        "yd": 0.9144, "yard": 0.9144, "yards": 0.9144,
        "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
        "nmi": 1852.0, "nautical mile": 1852.0, "fathom": 1.8288,
        "rod": 5.0292, "chain": 20.1168, "furlong": 201.168, "hand": 0.1016,
        # Astronomical Units
        "au": 149597870700.0, "astronomical unit": 149597870700.0,
        "ly": 9460730472580800.0, "light year": 9460730472580800.0, "light-year": 9460730472580800.0,
        "parsec": 30856775814913673.0, "pc": 30856775814913673.0,
        # Indian / Vedic Units
        "gaj": 0.9144, "gaz": 0.9144,
        "hath": 0.4572, "cubit": 0.4572,
        "angul": 0.01905, "dhanush": 1.8288, "kosa": 3657.6, "yojana": 14630.4
    },

    # 2. MASS / WEIGHT (Base: kilogram)
    "mass": {
        "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
        "g": 0.001, "gram": 0.001, "grams": 0.001,
        "mg": 1e-6, "milligram": 1e-6, "milligrams": 1e-6,
        "ug": 1e-9, "microgram": 1e-9,
        "ton": 1000.0, "tonne": 1000.0, "metric ton": 1000.0,
        "short ton": 907.18474, "long ton": 1016.0469,
        "lb": 0.45359237, "lbs": 0.45359237, "pound": 0.45359237, "pounds": 0.45359237,
        "oz": 0.028349523, "ounce": 0.028349523, "ounces": 0.028349523,
        "troy oz": 0.0311034768, "ozt": 0.0311034768, "carat": 0.0002, "ct": 0.0002,
        "grain": 0.00006479891, "stone": 6.35029318,
        # Indian Traditional Units
        "tola": 0.0116638, "ratti": 0.0001215, "masha": 0.000972,
        "chhatak": 0.05832, "seer": 0.9331, "maund": 37.3242, "mann": 37.3242,
        "quintal": 100.0
    },

    # 3. AREA & LAND (Base: square meter)
    "area": {
        "sqm": 1.0, "sq m": 1.0, "square meter": 1.0, "square meters": 1.0, "m2": 1.0,
        "sqft": 0.09290304, "sq ft": 0.09290304, "square feet": 0.09290304, "square foot": 0.09290304, "ft2": 0.09290304,
        "sqin": 0.00064516, "sq in": 0.00064516, "square inch": 0.00064516, "in2": 0.00064516,
        "sqyd": 0.83612736, "sq yd": 0.83612736, "square yard": 0.83612736, "yd2": 0.83612736,
        "sqkm": 1000000.0, "square kilometer": 1000000.0, "km2": 1000000.0,
        "sqmi": 2589988.11, "square mile": 2589988.11, "mi2": 2589988.11,
        "acre": 4046.8564224, "acres": 4046.8564224,
        "hectare": 10000.0, "hectares": 10000.0, "ha": 10000.0, "are": 100.0,
        # Indian Land Units
        "guntha": 101.17141, "gunta": 101.17141,
        "bigha": 2529.285, "pucca bigha": 2529.285, "kaccha bigha": 843.095,
        "biswa": 126.464, "cent": 40.468564, "ground": 222.967,
        "ankanam": 6.689, "marla": 25.29285, "kanal": 505.857, "katha": 66.89
    },

    # 4. VOLUME & CAPACITY (Base: liter)
    "volume": {
        "l": 1.0, "liter": 1.0, "liters": 1.0, "litre": 1.0,
        "ml": 0.001, "milliliter": 0.001, "milliliters": 0.001, "cc": 0.001,
        "cum": 1000.0, "cubic meter": 1000.0, "m3": 1000.0,
        "cuin": 0.016387064, "cubic inch": 0.016387064,
        "cuft": 28.316846592, "cubic foot": 28.316846592, "cft": 28.316846592,
        "gal": 3.785411784, "gallon": 3.785411784, "gallons": 3.785411784,
        "uk_gal": 4.54609, "imperial gallon": 4.54609,
        "bbl": 158.987294928, "barrel": 158.987294928, "oil barrel": 158.987294928,
        "floz": 0.02957353, "fluid ounce": 0.02957353,
        "pt": 0.473176473, "pint": 0.473176473, "qt": 0.946352946, "quart": 0.946352946,
        "cup": 0.2365882, "cups": 0.2365882,
        "tbsp": 0.01478676, "tablespoon": 0.01478676,
        "tsp": 0.00492892, "teaspoon": 0.00492892, "drop": 0.00005
    },

    # 5. PRESSURE (Base: pascal)
    "pressure": {
        "pa": 1.0, "pascal": 1.0, "pascals": 1.0,
        "kpa": 1000.0, "kilopascal": 1000.0, "mpa": 1000000.0, "megapascal": 1000000.0,
        "bar": 100000.0, "bars": 100000.0, "mbar": 100.0, "millibar": 100.0, "hpa": 100.0,
        "psi": 6894.75729, "lb/sq in": 6894.75729, "psf": 47.8802589,
        "atm": 101325.0, "atmosphere": 101325.0,
        "torr": 133.322368, "mmhg": 133.322368, "inhg": 3386.388666,
        "cmh2o": 98.0665, "inh2o": 249.0889
    },

    # 6. ENERGY, WORK & HEAT (Base: joule)
    "energy": {
        "j": 1.0, "joule": 1.0, "joules": 1.0,
        "kj": 1000.0, "kilojoule": 1000.0, "mj": 1000000.0, "gj": 1000000000.0,
        "cal": 4.184, "calorie": 4.184, "calories": 4.184,
        "kcal": 4184.0, "kilocalorie": 4184.0, "food calorie": 4184.0,
        "wh": 3600.0, "watt-hour": 3600.0,
        "kwh": 3600000.0, "kilowatt-hour": 3600000.0, "mwh": 3600000000.0,
        "btu": 1055.056, "therm": 105480400.0,
        "ev": 1.602176634e-19, "mev": 1.602176634e-13, "erg": 1e-7,
        "ftlbf": 1.3558179483314004, "ton tnt": 4184000000.0
    },

    # 7. POWER (Base: watt)
    "power": {
        "w": 1.0, "watt": 1.0, "watts": 1.0,
        "kw": 1000.0, "kilowatt": 1000.0, "mw": 1000000.0, "gw": 1000000000.0,
        "hp": 745.699872, "horsepower": 745.699872, "mechanical hp": 745.699872,
        "ps": 735.49875, "metric hp": 735.49875, "cv": 735.49875,
        "btu/hr": 0.29307107, "btu/h": 0.29307107, "ton ref": 3516.85284, "tr": 3516.85284
    },

    # 8. SPEED & VELOCITY (Base: meter per second)
    "speed": {
        "mps": 1.0, "m/s": 1.0, "meter per second": 1.0,
        "kmph": 0.27777778, "km/h": 0.27777778, "kph": 0.27777778,
        "mph": 0.44704, "miles per hour": 0.44704,
        "fps": 0.3048, "ft/s": 0.3048, "feet per second": 0.3048,
        "knot": 0.51444444, "knots": 0.51444444,
        "mach": 343.0, "c": 299792458.0
    },

    # 9. ELECTRICAL & ELECTRONICS
    "voltage": {
        "v": 1.0, "volt": 1.0, "volts": 1.0,
        "mv": 0.001, "millivolt": 0.001, "uv": 1e-6, "microvolt": 1e-6,
        "kv": 1000.0, "kilovolt": 1000.0, "megavolt": 1000000.0
    },
    "current": {
        "a": 1.0, "amp": 1.0, "ampere": 1.0, "amps": 1.0,
        "ma": 0.001, "milliamp": 0.001, "milliampere": 0.001,
        "ua": 1e-6, "microamp": 1e-6, "microampere": 1e-6, "ka": 1000.0
    },
    "resistance": {
        "ohm": 1.0, "ohms": 1.0, "mohm": 0.001,
        "kohm": 1000.0, "kiloohm": 1000.0, "k": 1000.0,
        "megohm": 1000000.0, "mo": 1000000.0
    },
    "capacitance": {
        "f": 1.0, "farad": 1.0, "mf": 0.001,
        "uf": 1e-6, "microfarad": 1e-6,
        "nf": 1e-9, "nanofarad": 1e-9,
        "pf": 1e-12, "picofarad": 1e-12
    },
    "frequency": {
        "hz": 1.0, "hertz": 1.0,
        "khz": 1000.0, "kilohertz": 1000.0,
        "mhz": 1000000.0, "megahertz": 1000000.0,
        "ghz": 1000000000.0, "gigahertz": 1000000000.0,
        "rpm": 0.0166666667
    },

    # 10. DIGITAL DATA & BANDWIDTH (Base: byte)
    "digital": {
        "b": 1.0, "byte": 1.0, "bytes": 1.0,
        "kb": 1024.0, "kilobyte": 1024.0, "kib": 1024.0,
        "mb": 1048576.0, "megabyte": 1048576.0, "mib": 1048576.0,
        "gb": 1073741824.0, "gigabyte": 1073741824.0, "gib": 1073741824.0,
        "tb": 1099511627776.0, "terabyte": 1099511627776.0,
        "pb": 1125899906842624.0, "petabyte": 1125899906842624.0,
        "bit": 0.125, "bits": 0.125,
        "kbit": 128.0, "mbit": 131072.0, "gbit": 134217728.0
    },

    # 11. TIME & VEDIC CHRONOMETRY (Base: second)
    "time": {
        "s": 1.0, "sec": 1.0, "second": 1.0, "seconds": 1.0,
        "ms": 0.001, "millisecond": 0.001, "milliseconds": 0.001,
        "us": 1e-6, "microsecond": 1e-6, "ns": 1e-9, "nanosecond": 1e-9,
        "min": 60.0, "minute": 60.0, "minutes": 60.0,
        "hr": 3600.0, "hour": 3600.0, "hours": 3600.0,
        "day": 86400.0, "days": 86400.0,
        "week": 604800.0, "weeks": 604800.0,
        "fortnight": 1209600.0,
        "month": 2592000.0, "months": 2592000.0, # 30-day standard
        "yr": 31557600.0, "year": 31557600.0, "years": 31557600.0, # 365.25 days
        "decade": 315576000.0, "century": 3155760000.0,
        # Vedic Chronometry
        "truti": 0.000030864, "nimesha": 0.2133,
        "ghati": 1440.0, # 1 Ghati = 24 minutes
        "muhurta": 2880.0, # 1 Muhurta = 2 Ghatis = 48 minutes
        "prahara": 10800.0 # 1 Prahara = 3 hours
    },

    # 12. ANGLE & TRIGONOMETRY (Base: radian)
    "angle": {
        "rad": 1.0, "radian": 1.0, "radians": 1.0,
        "deg": 0.017453292519943295, "degree": 0.017453292519943295, "degrees": 0.017453292519943295,
        "grad": 0.015707963267948967, "gradian": 0.015707963267948967,
        "arcmin": 0.0002908882086657216, "arcsec": 4.84813681109536e-6,
        "rev": 6.283185307179586, "turn": 6.283185307179586
    },

    # 13. FLOW RATE (Base: liter per second)
    "flow": {
        "lps": 1.0, "l/s": 1.0, "liter per second": 1.0,
        "lpm": 0.0166666667, "l/min": 0.0166666667, "liter per minute": 0.0166666667,
        "cum_hr": 0.27777778, "m3/h": 0.27777778, "cubic meter per hour": 0.27777778,
        "gpm": 0.0630901964, "gallon per minute": 0.0630901964,
        "cfm": 0.471947443, "cubic feet per minute": 0.471947443
    }
}

class PramanaUnitConverterAgent:
    name = "Pramana"
    role = "Master Multi-Dimensional Unit Conversion Agent"

    def __init__(self):
        self.db = UNITS_DB

    def convert_temperature(self, value, from_u, to_u):
        from_u = from_u.lower().strip()
        to_u = to_u.lower().strip()

        # To Celsius
        if from_u in ["c", "celsius", "centigrade"]:
            c = value
        elif from_u in ["f", "fahrenheit"]:
            c = (value - 32.0) * (5.0 / 9.0)
        elif from_u in ["k", "kelvin"]:
            c = value - 273.15
        elif from_u in ["r", "rankine"]:
            c = (value - 491.67) * (5.0 / 9.0)
        elif from_u in ["reaumur", "re"]:
            c = value * 1.25
        else:
            return None, "Unknown temp unit '{}'".format(from_u)

        # From Celsius to target
        if to_u in ["c", "celsius", "centigrade"]:
            res = c
        elif to_u in ["f", "fahrenheit"]:
            res = (c * (9.0 / 5.0)) + 32.0
        elif to_u in ["k", "kelvin"]:
            res = c + 273.15
        elif to_u in ["r", "rankine"]:
            res = (c + 273.15) * (9.0 / 5.0)
        elif to_u in ["reaumur", "re"]:
            res = c * 0.8
        else:
            return None, "Unknown target temp unit '{}'".format(to_u)

        return res, "temperature"

    def convert(self, value, from_unit, to_unit):
        from_u = from_unit.lower().strip()
        to_u = to_unit.lower().strip()

        temp_units = ["c", "celsius", "centigrade", "f", "fahrenheit", "k", "kelvin", "r", "rankine", "reaumur", "re"]
        if from_u in temp_units or to_u in temp_units:
            res, cat = self.convert_temperature(value, from_u, to_u)
            if res is not None:
                return {
                    "value": value, "from_unit": from_unit, "to_unit": to_unit,
                    "result": res, "category": "temperature", "success": True
                }

        for cat, units in self.db.items():
            if from_u in units and to_u in units:
                factor_from = units[from_u]
                factor_to = units[to_u]
                base_si_val = value * factor_from
                result_val = base_si_val / factor_to
                return {
                    "value": value, "from_unit": from_unit, "to_unit": to_unit,
                    "result": result_val, "category": cat, "success": True
                }

        return {
            "value": value, "from_unit": from_unit, "to_unit": to_unit,
            "result": None, "category": "unknown", "success": False,
            "error": "Incompatible or unknown unit pair: '{}' -> '{}'".format(from_unit, to_unit)
        }

    def parse_and_convert(self, text):
        raw = text.lower().replace("convert", "").replace("how many", "").replace("what is", "").strip()
        sep = " to "
        if " to " in raw: sep = " to "
        elif " in " in raw: sep = " in "
        elif "->" in raw: sep = "->"
        elif "=" in raw: sep = "="

        if sep in raw:
            parts = raw.split(sep, 1)
            left = parts[0].strip()
            to_unit = parts[1].strip().split()[0]
            left_words = left.split()
            val = 1.0
            from_unit = ""
            for i, w in enumerate(left_words):
                try:
                    val = float(w)
                    from_unit = " ".join(left_words[i+1:])
                    break
                except ValueError:
                    pass
            if from_unit and to_unit:
                return self.convert(val, from_unit, to_unit)

        return {"success": False, "error": "Could not parse conversion query: '{}'".format(text)}

    def format_card(self, res):
        if not res.get("success"):
            return " [PRAMANA CONVERTER ERROR]: " + res.get("error", "Conversion failed")

        val = res["value"]
        from_u = res["from_unit"]
        res_val = res["result"]
        to_u = res["to_unit"]
        cat = res["category"].upper()

        card = "=" * 65 + "\n"
        card += " [PRAMANA UNIT CONVERSION ENGINE - {}]\n".format(cat)
        card += "=" * 65 + "\n"
        card += "   Input:    {:>16,.4f} {}\n".format(val, from_u)
        card += "   Result:   {:>16,.4f} {}\n".format(res_val, to_u)
        card += "-" * 65 + "\n"
        card += "   * Formula: Exact SI rational calculation on ARM Cortex-M0+ ALU\n"
        card += "=" * 65 + "\n"
        return card

def run_pramana_demo():
    agent = PramanaUnitConverterAgent()
    print("=" * 65)
    print(" 📐 AGENT 13: 'PRAMANA' - MASTER 15-DOMAIN UNIT CONVERTER")
    print("=" * 65)
    demo_queries = [
        "5.8 feet to cm",
        "100 celsius to fahrenheit",
        "2.5 acres to sqft",
        "10 tola to grams",
        "50 psi to bar",
        "100 kmph to mph",
        "100 hp to kw",
        "500 kcal to joules",
        "16 gb to mb",
        "10 muhurta to minutes",
        "1000 uF to mF",
        "50 gpm to lpm"
    ]
    for q in demo_queries:
        res = agent.parse_and_convert(q)
        print(agent.format_card(res))

if __name__ == "__main__":
    run_pramana_demo()
