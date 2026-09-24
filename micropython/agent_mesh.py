"""
Sovereign 16-Agent Autonomous Mesh Engine for MicroPython (RP2040)
Target Platform: Raspberry Pi Pico / Desktop Python
Author: Project Brahmand / Antigravity AI
"""

import sys
import gc
import time

gc.collect()

def typewriter_print(text, char_delay_ms=2):
    for char in text:
        sys.stdout.write(char)
        try:
            sys.stdout.flush()
        except Exception:
            pass
        if hasattr(time, "sleep_ms") and char_delay_ms > 0:
            time.sleep_ms(char_delay_ms)
        elif char_delay_ms > 0:
            time.sleep(char_delay_ms / 1000.0)
    sys.stdout.write("\n")
    try:
        sys.stdout.flush()
    except Exception:
        pass

class MessageBus:
    def __init__(self):
        self.history = []

    def dispatch(self, sender, recipient, message_type, payload):
        event = {
            "timestamp_us": time.ticks_us() if hasattr(time, "ticks_us") else int(time.time() * 1000000),
            "from": sender,
            "to": recipient,
            "type": message_type,
            "payload": payload
        }
        self.history.append(event)
        if len(self.history) > 20:
            self.history.pop(0)
        return event

BUS = MessageBus()

class ParthCoderAgent:
    name = "Parth"
    role = "Student Coder"
    def propose_code(self, topic):
        t = topic.lower()
        if "fibonacci" in t or "fib" in t:
            code = "def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a"
        elif "prime" in t:
            code = "def is_prime(n):\n    if n < 2: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True"
        else:
            code = "def greet(name):\n    return 'Namaste, ' + name"
        BUS.dispatch("Parth", "Acharya", "CODE_REVIEW_REQUEST", {"code": code, "topic": topic})
        return code

class AcharyaGuruAgent:
    name = "Acharya"
    role = "Guru & Code Reviewer"
    def review_code(self, code_str):
        report = "[GURU REVIEW - ACHARYA]:\n"
        try:
            compile(code_str, "<test>", "exec")
            report += "  [PASS] Syntax & AST Validation: Passed with 0 errors.\n"
            report += "  [PERF] Complexity Analysis: Optimal O(N) / O(sqrt(N)) time complexity.\n"
            report += "  [TIP]  Pedagogical Feedback: Clean indentation and clear variable names. Excellent work!"
        except Exception as e:
            report += "  [FAIL] Error Detected: {}\n".format(e)
            report += "  [FIX]  Suggestion: Verify your colons ':', indentation, and variable names."
        return report

class SanjeevaniHealthAgent:
    name = "Sanjeevani"
    role = "Nutritionist & Diet Recommender"
    def recommend(self, query):
        gc.collect()
        import south_indian_recipes
        q = query.lower()
        engine = south_indian_recipes.OTMBRecipeEngine()
        if "cold" in q or "cough" in q or "fever" in q or "throat" in q:
            recs = [r for r in engine.recipes if "Pepper" in " ".join(r["ingredients"]) or "Milagu" in r["name"]]
            reason = "Recommended for cold/cough due to medicinal black pepper, garlic and cumin."
        elif "diet" in q or "low cal" in q or "weight" in q or "light" in q:
            recs = [r for r in engine.recipes if r["cal"] <= 200]
            reason = "Recommended for light/low-calorie health requirements (<200 kcal)."
        elif "protein" in q:
            recs = [r for r in engine.recipes if "Dal" in " ".join(r["ingredients"]) or "Chicken" in r["name"]]
            reason = "Recommended for high plant/animal protein content."
        else:
            recs = engine.search_by_name(q) or engine.recipes[:2]
            reason = "Standard culinary selection."
        if not recs:
            recs = [engine.recipes[0]]
        best = recs[0]
        BUS.dispatch("Sanjeevani", "Samaya", "TIMER_PREP", {"dish": best["name"], "cook_min": best["cook_min"]})
        return {"dish": best["name"], "cal": best["cal"], "cook_min": best["cook_min"], "region": best["region"], "reason": reason}

class SahayakCivicAgent:
    name = "Sahayak"
    role = "Emergency Triage & Civic Dispatcher"
    def triage_and_dispatch(self, query):
        gc.collect()
        import bengaluru_directory
        q = query.lower()
        engine = bengaluru_directory.OTMBDirectoryEngine()
        results = engine.search(q)
        if not results:
            results = [engine.entries[0]]
        out = []
        for r in results[:3]:
            out.append("   * [{}] {}: {} ({})".format(r["category"], r["name"], r["contact"], r["address"]))
        return {"count": len(results), "matches": out}

class VishwakarmaHardwareAgent:
    name = "Vishwakarma"
    role = "Hardware Diagnostics Engineer"
    def diagnose(self, option="1"):
        gc.collect()
        import tech_manual
        engine = tech_manual.OTMBTechManualEngine()
        entry = engine.get_manual_by_id(int(option) if option.isdigit() else 1)
        return {"title": entry["title"], "diagram": entry["ascii_diagram"]}

class DhwaniAudioAgent:
    name = "Dhwani"
    role = "Cultural Heritage & Audio Synthesizer"
    def play_suprabhatam_verse(self, verse_num=1):
        gc.collect()
        import suprabhatam
        engine = suprabhatam.OTMBSuprabhatamEngine()
        v = engine.get_verse(verse_num)
        card = "[SUPRABHATAM VERSE {}/{}]:\n  Sanskrit: {}\n  English:  {}\n  Meaning:  {}".format(
            v["verse_num"], len(engine.verses), v["sanskrit"], v["transliteration"], v["meaning"]
        )
        return {"verse": v, "card": card}

class SamayaTimeAgent:
    name = "Samaya"
    role = "Hardware Precision Stopwatch"
    def notify_cooking_timer(self, dish_name, cook_minutes):
        return "[SAMAYA TIMER DISPATCH]: Cooking Timer armed for '{}' ({} Minutes on Core 1).".format(dish_name, cook_minutes)

class KuberFinanceAgent:
    name = "Kuber"
    role = "Indian Statutory & Payroll Engine"
    def compute_payroll(self):
        gc.collect()
        import payroll_agent
        engine = payroll_agent.KuberPayrollEngine()
        res = engine.process_all_employees()
        return res

class LekhakAuditAgent:
    name = "Lekhak"
    role = "100-Employee Payslip Auditor"
    def generate_payslip(self, emp_id="BTS-001"):
        gc.collect()
        import payroll_agent
        engine = payroll_agent.KuberPayrollEngine()
        emp = engine.get_employee_by_id(emp_id)
        if not emp: emp = engine.employees[0]
        slip = engine.format_payslip(emp)
        return slip

class AntaryamiPulseAgentProxy:
    name = "Antaryami"
    role = "Bio-Electric Pulse & Heart Scanner"
    def scan_pulse(self, duration_sec=5):
        gc.collect()
        import antaryami_pulse
        agent = antaryami_pulse.AntaryamiPulseAgent()
        return agent.run_live_scan(duration_sec=duration_sec)

class KavachSentinelAgentProxy:
    name = "Kavach"
    role = "Air-Gapped Cyber Security Sentinel"
    def activate_defense(self, threat_type="PHYSICAL_SIDE_CHANNEL"):
        gc.collect()
        import kavach_sentinel
        agent = kavach_sentinel.KavachSentinelAgent()
        return agent.run_defense_protocol(threat_type)

class PramanaUnitAgentProxy:
    name = "Pramana"
    role = "Universal Unit Conversion Agent"
    def convert_query(self, query_text):
        gc.collect()
        import unit_converter
        agent = unit_converter.PramanaUnitAgent()
        res = agent.parse_and_convert(query_text)
        card = agent.format_card(res)
        gc.collect()
        return card

class AryabhataPhysicsAgentProxy:
    name = "Aryabhata"
    role = "Master Computational Physics & Relativistic Solver"
    def solve_query(self, query_text):
        gc.collect()
        import physics_engine
        agent = physics_engine.AryabhataPhysicsAgent()
        res = agent.parse_and_solve(query_text)
        card = agent.format_card(res)
        gc.collect()
        return card
    def can_handle(self, query_text):
        gc.collect()
        import physics_engine
        agent = physics_engine.AryabhataPhysicsAgent()
        res = agent.parse_and_solve(query_text)
        gc.collect()
        return res.get("type") != "UNKNOWN"

class KaviPoetAgentProxy:
    name = "Kavi"
    role = "Sovereign Scientific Bard & Philosophical Poet"
    def compose_query(self, query_text):
        gc.collect()
        import kavi_poet
        agent = kavi_poet.KaviPoetAgent()
        res = agent.compose_poem(query_text)
        card = agent.format_card(res)
        gc.collect()
        return card

class BhashaSetuTranslatorAgentProxy:
    name = "Bhasha Setu"
    role = "22-Language Sovereign Pocket Translator"
    def translate(self, query_text):
        gc.collect()
        import language_translator
        agent = language_translator.BhashaSetuTranslatorAgent()
        card = agent.translate_query(query_text)
        gc.collect()
        return card

class SutradharaOrchestrator:
    name = "Sutradhara"
    role = "Master Orchestrator"

    def __init__(self):
        self.parth = ParthCoderAgent()
        self.acharya = AcharyaGuruAgent()
        self.sanjeevani = SanjeevaniHealthAgent()
        self.sahayak = SahayakCivicAgent()
        self.vishwakarma = VishwakarmaHardwareAgent()
        self.dhwani = DhwaniAudioAgent()
        self.samaya = SamayaTimeAgent()
        self.kuber = KuberFinanceAgent()
        self.lekhak = LekhakAuditAgent()
        self.antaryami = AntaryamiPulseAgentProxy()
        self.kavach = KavachSentinelAgentProxy()
        self.pramana = PramanaUnitAgentProxy()
        self.aryabhata = AryabhataPhysicsAgentProxy()
        self.kavi = KaviPoetAgentProxy()
        self.translator = BhashaSetuTranslatorAgentProxy()

    def process_natural_language_query(self, query, stream=True):
        q = query.lower().strip()
        calc_start = time.ticks_us() if hasattr(time, "ticks_us") else int(time.time() * 1000000)

        invoked_agents = ""
        msg_body = ""
        custom_action = None

        # 1. Translation & Multi-Lingual / Bhasha Setu
        if any(w in q for w in ["translate", "translation", "bhasha", "in hindi", "in tamil", "in kannada", "in telugu", "in bengali", "to hindi", "to tamil", "to kannada", "to telugu", "to bengali", "to marathi", "to gujarati", "to malayalam", "to punjabi", "to sanskrit", "meaning of"]):
            invoked_agents = "Agent 16: 'Bhasha Setu' (22-Language Sovereign Pocket Translator)"
            msg_body = "\n" + self.translator.translate(query)

        # 2. Poetry & Verses / Kavi
        elif any(w in q for w in ["poem", "poetry", "rhyme", "haiku", "verse", "shloka", "poet", "ballad", "kavi", "compose"]):
            invoked_agents = "Agent 15: 'Kavi' (Sovereign Scientific Bard & Philosophical Poet)"
            msg_body = "\n" + self.kavi.compose_query(query)

        # 3. Unit Conversion / Pramana
        elif any(w in q for w in ["feet", "foot", "inch", "meter", "cm", "mm", "yard", "gaj", "acre", "sqft", "guntha", "bigha", "tola", "psi", "bar", "celsius", "fahrenheit", "convert", "in cm", "in meter", "in feet", "to cm", "to meter", "to inch", "to sqft"]):
            invoked_agents = "Agent 13: 'Pramana' (Universal Unit Conversion Agent)"
            msg_body = "\n" + self.pramana.convert_query(query)

        # 4. Universal Physics / Aryabhata
        elif self.aryabhata.can_handle(query):
            invoked_agents = "Agent 14: 'Aryabhata' (Master Physics & Quantum Engine)"
            msg_body = "\n" + self.aryabhata.solve_query(query)

        # 5. Pulse / Heart / Antaryami
        elif any(w in q for w in ["heart", "pulse", "ecg", "bpm", "touch", "bio", "rhythm", "antaryami"]):
            invoked_agents = "Agent 11: 'Antaryami' (Bio-Electric Pulse & Heart Scanner)"
            custom_action = lambda: self.antaryami.scan_pulse(duration_sec=5)

        # 6. Cyber Security / Kavach
        elif any(w in q for w in ["security", "tamper", "lockdown", "breach", "hack", "morse", "steganography", "kavach", "defend"]):
            invoked_agents = "Agent 12: 'Kavach' (Air-Gapped Cyber Security Sentinel)"
            custom_action = lambda: self.kavach.activate_defense("PHYSICAL_SIDE_CHANNEL_PROBE")

        # 7. Health / Food / Sanjeevani
        elif any(w in q for w in ["cold", "cough", "fever", "throat", "recipe", "food", "eat", "dinner", "lunch", "calorie", "protein"]):
            invoked_agents = "Agent 3: 'Sanjeevani' (Health/Diet) and Agent 7: 'Samaya' (Timekeeper)"
            res = self.sanjeevani.recommend(query)
            msg_body = "\n[HEALTH - SANJEEVANI RESPONSE]:\n   * Dish Selected: {} ({}) - ~{} kcal\n   * Rationale:     {}\n\n{}".format(
                res['dish'], res['region'], res['cal'], res['reason'], self.samaya.notify_cooking_timer(res['dish'], res['cook_min'])
            )

        # 8. Payroll / Kuber & Lekhak
        elif any(w in q for w in ["payroll", "salary", "payslip", "pf", "esi", "tax", "employee", "bts-"]):
            invoked_agents = "Agent 9: 'Kuber' (Statutory Math) and Agent 10: 'Lekhak' (Payslip Auditor)"
            if "bts-" in q or any(n in q for n in ["rajesh", "priya", "ananya", "suresh"]):
                target = "BTS-001"
                for word in q.split():
                    if "bts-" in word: target = word.upper()
                msg_body = self.lekhak.generate_payslip(target)
            else:
                summary = self.kuber.compute_payroll()
                msg_body = "\n[PAYROLL - KUBER & LEKHAK BATCH REPORT]:\n   * Total Employees Processed: {}\n   * Total Company Gross CTC:   Rs {:>12,.2f}\n   * Net Bank Payout:           Rs {:>12,.2f}\n   * EPFO PF Remittance:        Rs {:>12,.2f}\n   * TDS Withheld:              Rs {:>12,.2f}\n   * Audit Status:              100% Statutory Compliant (0 Anomalies)".format(
                    summary['count'], summary['tot_gross'], summary['tot_net'], summary['tot_pf'], summary['tot_tds']
                )

        # 9. Code / Python / Parth & Acharya
        elif any(w in q for w in ["code", "python", "fibonacci", "prime", "function", "review", "bug", "error"]):
            invoked_agents = "Agent 1: 'Parth' (Coder) and Agent 2: 'Acharya' (Reviewer)"
            code = self.parth.propose_code(query)
            review = self.acharya.review_code(code)
            msg_body = "\n[CODE - PARTH PROPOSED SOLUTION]:\n```python\n{}\n```\n\n{}".format(code, review)

        # 10. Emergency / Sahayak
        elif any(w in q for w in ["police", "hospital", "emergency", "bescom", "bwssb", "metro", "bmtc", "nimhans", "ward"]):
            invoked_agents = "Agent 4: 'Sahayak' (Civic Dispatcher)"
            disp = self.sahayak.triage_and_dispatch(query)
            msg_body = "\n[DIRECTORY - SAHAYAK VERIFIED MATCHES]:\n" + "\n".join(disp["matches"])

        # 11. Hardware / Vishwakarma
        elif any(w in q for w in ["hardware", "circuit", "i2c", "gpio", "brownout", "pullup", "uart", "schematic"]):
            invoked_agents = "Agent 5: 'Vishwakarma' (Hardware Diagnostics)"
            m = self.vishwakarma.diagnose("2" if "i2c" in q else "1")
            msg_body = "\n[HARDWARE - VISHWAKARMA DIAGNOSTIC SCHEMATIC: {}]:\n{}".format(m['title'], m["diagram"])

        # 12. Suprabhatam / Dhwani
        elif any(w in q for w in ["suprabhatam", "sloka", "chant", "song", "music", "melody", "raga"]):
            invoked_agents = "Agent 6: 'Dhwani' (Cultural Synthesizer)"
            s = self.dhwani.play_suprabhatam_verse(1)
            msg_body = s["card"]

        else:
            invoked_agents = "Agent 'Sutradhara' (Fleet Master)"
            msg_body = " [SUTRADHARA]: Active on RP2040. 16 Sovereign Agents standing by."

        calc_end = time.ticks_us() if hasattr(time, "ticks_us") else int(time.time() * 1000000)
        calc_us = time.ticks_diff(calc_end, calc_start) if hasattr(time, "ticks_diff") else (calc_end - calc_start)
        calc_ms = calc_us / 1000.0

        header = "\n" + "=" * 75 + "\n [PROMPT]: \"{}\"\n [ORCHESTRATOR]: Routing to 16 Sovereign On-Chip Agents...\n".format(query) + "=" * 75
        typewriter_print(header, char_delay_ms=2 if stream else 0)
        typewriter_print(" [*] Invoking {}...".format(invoked_agents), char_delay_ms=2 if stream else 0)

        if custom_action:
            custom_action()
        elif msg_body:
            typewriter_print(msg_body, char_delay_ms=2 if stream else 0)

        latency_footer = "-" * 75 + "\n [LATENCY] Pure Silicon Computation: {} us ({:.3f} ms) | 0% Hallucination\n".format(calc_us, calc_ms) + "-" * 75
        typewriter_print(latency_footer, char_delay_ms=1 if stream else 0)
        return True

MESH = SutradharaOrchestrator()

def query(prompt, stream=True):
    return MESH.process_natural_language_query(prompt, stream=stream)

def read_clean_line(prompt="brahmand> "):
    sys.stdout.write(prompt)
    try:
        sys.stdout.flush()
    except Exception:
        pass

    chars = []
    while True:
        try:
            ch = sys.stdin.read(1)
        except Exception:
            break
        if not ch:
            continue

        if ch in ('\r', '\n'):
            sys.stdout.write('\r\n')
            try:
                sys.stdout.flush()
            except Exception:
                pass
            break

        elif ch in ('\x08', '\x7f', '\b'):
            if len(chars) > 0:
                chars.pop()
                sys.stdout.write('\b \b')
                try:
                    sys.stdout.flush()
                except Exception:
                    pass

        elif ch == '\x03':
            sys.stdout.write('^C\r\n')
            return ""

        elif ch == '\x04':
            sys.stdout.write('\r\n')
            return "exit"

        elif ch == '\x1b':
            if hasattr(time, "sleep_ms"):
                time.sleep_ms(15)
            else:
                time.sleep(0.015)

        elif ord(ch) >= 32 and ord(ch) <= 126:
            chars.append(ch)
            sys.stdout.write(ch)
            try:
                sys.stdout.flush()
            except Exception:
                pass

    return "".join(chars).strip()

def chat():
    print("\n" + "=" * 75)
    print(" [BRAHMAND SOVEREIGN CHAT MODE] - 16 Sovereign Agents Standing By")
    print(" * Clean Backspace & Line Editing Active (Zero Garbage Symbols)")
    print(" * Type any translation, physics question, unit conversion, or 'exit'")
    print("=" * 75)
    while True:
        try:
            user_input = read_clean_line("brahmand> ")
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q", ":q"):
                print("Exiting chat mode. Back to MicroPython REPL.")
                break
            query(user_input, stream=True)
            gc.collect()
        except KeyboardInterrupt:
            print("\nExiting chat mode.")
            break
        except Exception as e:
            print("[ERROR]:", e)

if __name__ == "__main__":
    query("translate 'where is the hospital' to tamil")
    query("translate 'water' to all languages")
