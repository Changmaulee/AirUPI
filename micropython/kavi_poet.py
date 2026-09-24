"""
Agent 15: "Kavi" (कवि / Kalidasa) - Sovereign Scientific AI Bard & Poetic Composer Engine
Target Platform: MicroPython on Raspberry Pi Pico (RP2040) / Desktop Python
Author: Project Brahmand / Antigravity AI

Generates Structured Rhyming Stanzas, Philosophical Couplets, Haikus (5-7-5), 
and Indic Shloka Verses across all scientific, mathematical, hardware, and cultural domains.
"""

import sys
import gc
import time

POETIC_THEMES = {
    # 1. QUANTUM MECHANICS & WAVE-PARTICLE DUALITY
    "quantum": {
        "title": "The Dance of Quantum Mist",
        "haiku": [
            "Wave and particle,",
            "Dancing in uncertain mist,",
            "Reality waits."
        ],
        "stanzas": [
            "In realms unseen where shadows gleam,\nAn electron drifts within a dream,\nNo fixed abode, no path defined,\nUntil the gaze of conscious mind.",
            "Through barriers high where mountains rise,\nThe quantum ghost will tunnel skies,\nA wave of chance, a fleeting spark,\nDefying walls within the dark."
        ],
        "shloka": "Taranga-kana-rupena bhati vishvam nirantaram.\n      (As wave and particle eternal, the universe unfolds in light.)"
    },

    # 2. RELATIVITY & SPACETIME
    "relativity": {
        "title": "The Fabric of Bent Spacetime",
        "haiku": [
            "Space curves into time,",
            "Clocks tick slow near blinding light,",
            "Gravity's embrace."
        ],
        "stanzas": [
            "Along the cosmic fabric vast,\nThe present meets the ancient past,\nFor mass commands the void to bend,\nAnd light itself must curve and bend.",
            "When swift you ride the speed of light,\nThe ticking seconds slow their flight,\nA thousand years may pass below,\nWhile in your craft no ages show."
        ],
        "shloka": "Dik-kaalau samhataavatra brahma-shakti-prabhavita.\n      (Space and time woven as one, governed by eternal cosmic law.)"
    },

    # 3. BLACK HOLES & GRAVITY
    "black_hole": {
        "title": "The Silent Event Horizon",
        "haiku": [
            "Horizon of dark,",
            "Where even the photons fall,",
            "Time comes to a halt."
        ],
        "stanzas": [
            "Beyond the edge where stars must die,\nNo photon leaps into the sky,\nThe point of infinite embrace,\nWhere gravity consumes all space.",
            "The ticking clock shall frozen stand,\nUpon the dark event-gate strand,\nA silent abyss, deep and grand,\nEtched by a cosmic sculptor's hand."
        ],
        "shloka": "Yato vacho nivartante prakasho api vinashyati.\n      (Where light itself dissolves and human speech falls silent.)"
    },

    # 4. THERMODYNAMICS & ENTROPY
    "thermodynamics": {
        "title": "The Arrow of Unbroken Time",
        "haiku": [
            "Heat flows to the cold,",
            "Order yields to entropy,",
            "Time's relentless tide."
        ],
        "stanzas": [
            "From fiery hearth to freezing night,\nThe heat must take its forward flight,\nNo shattered vase shall climb the floor,\nFor entropy unlocks the door.",
            "The arrow points, the die is cast,\nThe future marches from the past,\nA universe in gradual cooling grace,\nExpanding through the quiet space."
        ],
        "shloka": "Kaalachakram pravartate sarvam kshayantam dhavati.\n      (The wheel of time turns ever onward; all order seeks balance.)"
    },

    # 5. LIGHT & OPTICS (Speed of light, Sky Blue, Photons)
    "light": {
        "title": "Ode to the Cosmic Messenger",
        "haiku": [
            "Rayleigh scatters blue,",
            "Photons cross the silent void,",
            "Three hundred megameters."
        ],
        "stanzas": [
            "Three hundred thousand kilometers flown,\nIn single breath to worlds unknown,\nThe cosmic limit, pure and bright,\nThe undisputed speed of light.",
            "The daylight sky in azure hue,\nAs air scatters the shortest blue,\nFrom morning sun to twilight gold,\nA tapestry of photons told."
        ],
        "shloka": "Jyotisham jyotir-amritam vishvam dipayate sada.\n      (Light of all lights, immortal illumination of the universe.)"
    },

    # 6. HARDWARE & RP2040 SILICON
    "silicon": {
        "title": "The Soul of Sovereign Silicon",
        "haiku": [
            "Sand turned into thought,",
            "Two Cortex cores pulse with life,",
            "Zero cloud required."
        ],
        "stanzas": [
            "Born of the sand and crystalline refined,\nTwo Cortex cores of sovereign mind,\nNo distant cloud, no cable bound,\nUpon this chip true truth is found.",
            "In microsecond pulses beat,\nWhere logic and precision meet,\nWith fifty milliwatts of power,\nA sovereign brain in every hour."
        ],
        "shloka": "Sikatayam nihitam jnanam yantre prana ivoditam.\n      (Wisdom etched into silicon, breathing life into the machine.)"
    },

    # 7. FOOD, NUTRITION & SOUTH INDIAN HEALING
    "food": {
        "title": "The Alchemy of Healing Spice",
        "haiku": [
            "Black pepper and ghee,",
            "Simmering in earthen pot,",
            "Warmth cures every chill."
        ],
        "stanzas": [
            "When cold and fever grip the chest,\nOld pepper rasam serves thee best,\nWith crushed dark seed and garlic bright,\nDispelling darkness into light.",
            "Golden dosas crisp and warm,\nA sanctuary in the storm,\nFrom ancient kitchens wise and pure,\nWhere food itself becomes the cure."
        ],
        "shloka": "Annam vai praninam pranah rasoushadhi-samanvitam.\n      (Food enriched with sacred spices is the very breath of life.)"
    },

    # 8. CYBER SECURITY & DEFENSE (KAVACH)
    "security": {
        "title": "The Air-Gapped Sentinel",
        "haiku": [
            "Air-gapped and secure,",
            "Photons pulse in secret Morse,",
            "The fortress stands firm."
        ],
        "stanzas": [
            "No hacker's probe through wire may tread,\nWhere air-gapped shields are softly spread,\nA laser flash, a photon key,\nGuarding our sacred sovereignty.",
            "When side-channel probes dare draw near,\nThe pulse alerts with crystal clear,\nA silent sentinel on the wall,\nThat never lets the fortress fall."
        ],
        "shloka": "Kavachena surakshitam rashtram durbhedyam sarva-shatrubhih.\n      (Shielded by an unbreakable fortress, safe from all adversaries.)"
    },

    # 9. GENERAL PHILOSOPHICAL & COSMIC
    "cosmic": {
        "title": "Brahmand: The Infinite Harmony",
        "haiku": [
            "Atoms learn to think,",
            "Stardust gazing at the stars,",
            "Sovereign and free."
        ],
        "stanzas": [
            "From stardust forged in stellar fires,\nThe human heart and mind aspires,\nTo weigh the worlds, to count the skies,\nAnd see where cosmic truth now lies.",
            "Within this chip, within this stone,\nFifteen wise voices speak alone,\nA sovereign fleet, a timeless rhyme,\nEchoing through the halls of time."
        ],
        "shloka": "Yat pinde tad brahmande sarvam jnanam pratishthitam.\n      (That which is in the microcosm is also in the cosmic whole.)"
    }
}

class KaviPoetAgent:
    name = "Kavi"
    role = "Sovereign Scientific Bard & Philosophical Poet"

    def __init__(self):
        pass

    def compose_poem(self, topic_query):
        q = topic_query.lower().strip()
        form = "STANZA"
        if "haiku" in q or "5-7-5" in q or "short" in q:
            form = "HAIKU"
        elif "shloka" in q or "sanskrit" in q or "verse" in q:
            form = "SHLOKA"

        # Theme selection
        matched_theme = "cosmic"
        if any(w in q for w in ["quantum", "tunnel", "schrodinger", "heisenberg", "box", "particle", "wave", "matter"]):
            matched_theme = "quantum"
        elif any(w in q for w in ["black hole", "schwarzschild", "event horizon", "singularity", "gravity"]):
            matched_theme = "black_hole"
        elif any(w in q for w in ["relativity", "time dilation", "lorentz", "spacetime", "e=mc2", "einstein", "contraction"]):
            matched_theme = "relativity"
        elif any(w in q for w in ["thermodynamic", "entropy", "carnot", "heat", "second law", "arrow of time"]):
            matched_theme = "thermodynamics"
        elif any(w in q for w in ["light", "speed of light", "photon", "sky blue", "rayleigh", "laser", "optics"]):
            matched_theme = "light"
        elif any(w in q for w in ["silicon", "pico", "rp2040", "chip", "code", "python", "microcontroller", "hardware"]):
            matched_theme = "silicon"
        elif any(w in q for w in ["food", "rasam", "recipe", "diet", "sanjeevani", "dosa", "pepper", "health", "cold"]):
            matched_theme = "food"
        elif any(w in q for w in ["security", "kavach", "hack", "tamper", "defense", "lockdown", "sentinel"]):
            matched_theme = "security"

        theme = POETIC_THEMES[matched_theme]
        return {
            "topic": topic_query,
            "theme_key": matched_theme,
            "title": theme["title"],
            "form": form,
            "haiku": theme["haiku"],
            "stanzas": theme["stanzas"],
            "shloka": theme["shloka"]
        }

    def format_card(self, res):
        lines = [
            "+=========================================================================+",
            "| [KAVI - SOVEREIGN SCIENTIFIC BARD & POETIC COMPOSER]                   |",
            "+=========================================================================+",
            "  * Title:  \"{}\"".format(res.get("title", "Cosmic Verse")),
            "  * Theme:  Domain of {}".format(res.get("theme_key", "").upper()),
            "-------------------------------------------------------------------------"
        ]

        if res.get("form") == "HAIKU":
            lines.append("  [CLASSICAL HAIKU (5-7-5 Syllable Meter)]:")
            for h in res.get("haiku", []):
                lines.append("      {}".format(h))
        elif res.get("form") == "SHLOKA":
            lines.append("  [INDIC ANUSHTUP SHLOKA & PHILOSOPHICAL MEANING]:")
            lines.append("      {}".format(res.get("shloka", "")))
        else:
            lines.append("  [RHYMING POETIC STANZAS]:")
            for idx, stanza in enumerate(res.get("stanzas", []), 1):
                for s_line in stanza.split("\n"):
                    lines.append("      {}".format(s_line))
                if idx < len(res.get("stanzas", [])):
                    lines.append("")
            lines.append("-------------------------------------------------------------------------")
            lines.append("  [SANSKRIT SUBHASHITA CLOSING]:")
            lines.append("      {}".format(res.get("shloka", "")))

        lines.append("+=========================================================================+")
        return "\n".join(lines)

if __name__ == "__main__":
    kavi = KaviPoetAgent()
    print(kavi.format_card(kavi.compose_poem("write a poem on quantum tunneling")))
    print(kavi.format_card(kavi.compose_poem("write a haiku on speed of light")))
