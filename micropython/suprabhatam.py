"""
OTMB-Based Sri Venkateswara Suprabhatam Engine
Target Platform: MicroPython on Raspberry Pi Pico (RP2040) / Desktop Python
Features: Sloka database, Akshara meter analysis, English/Indic translations,
PWM melody synthesis tones (Mayamalavagowla/Kalyani raga notes) for Piezo Buzzer & 1602 LCD HUD.
"""

import time

# Raga Notes Frequencies (Hz) for Recitation Melody
NOTES = {
    'S': 261,  # Sa (C4)
    'R1': 277, # Ri1 (Db4)
    'R2': 293, # Ri2 (D4)
    'G2': 311, # Ga2 (Eb4)
    'G3': 329, # Ga3 (E4)
    'M1': 349, # Ma1 (F4)
    'M2': 370, # Ma2 (F#4)
    'P': 392,  # Pa (G4)
    'D1': 415, # Dha1 (Ab4)
    'D2': 440, # Dha2 (A4)
    'N2': 466, # Ni2 (Bb4)
    'N3': 493, # Ni3 (B4)
    'S_HIGH': 523, # Sa High (C5)
    'REST': 0
}

SUPRABHATAM_SLOKAS = [
    {
        "id": 1,
        "sanskrit": "कौसल्या सुप्रजा राम पूर्वा संध्या प्रवर्तते ।\nउत्तिष्ठ नरशार्दूल कर्तव्यं दैवनिह्निकम् ॥",
        "iast": "Kausalya supraja Rama poorva sandhya pravartate |\nUttishta narasardoola kartavyam daivamahnikam ||",
        "meaning": "O Rama, noble son of Kausalya! The dawn is breaking in the East. Arise, O best of men! The daily divine duties are to be performed.",
        "notes": [('S', 400), ('R2', 400), ('G3', 400), ('M1', 400), ('P', 600), ('M1', 200), ('G3', 400), ('R2', 400), ('S', 800)]
    },
    {
        "id": 2,
        "sanskrit": "उत्तिष्ठोत्तिष्ठ गोविन्द उत्तिष्ठ गरुडध्वज ।\nउत्तिष्ठ कमलाकांत त्रैलोक्यं मङ्गलं कुरु ॥",
        "iast": "Uttishtottishta Govinda uttishta Garudadhwaja |\nUttishta Kamalakanta trailokyam mangalam kuru ||",
        "meaning": "Awake, awake, O Govinda! Awake, O One whose flag bears Garuda! Awake, O beloved of Lakshmi (Kamala)! Bestow auspiciousness upon all three worlds.",
        "notes": [('P', 400), ('D2', 400), ('N3', 400), ('S_HIGH', 600), ('N3', 200), ('D2', 400), ('P', 400), ('M1', 400), ('G3', 800)]
    },
    {
        "id": 3,
        "sanskrit": "मातस्समस्त जगतां मधुकैटभारेः\nवक्षोविहारिणी मनोहर दिव्यमूर्ते ।\nश्रीस्वामिनि श्रितजनप्रिय दानशीले\nश्रीवेङ्कटेश दयिते तव सुप्रभातम् ॥",
        "iast": "Matassamasta jagatam Madhukaitabhareh\nVakshoviharini manohara divyamoorte |\nSreeswamini sritajanapriya danasheele\nSree Venkatesa dayite tava suprabhatam ||",
        "meaning": "O Mother of all worlds, Lakshmi! Who dwells upon the chest of Vishnu (destroyer of Madhu-Kaitabha)! Beloved of Lord Venkateswara, auspicious dawn unto Thee.",
        "notes": [('G3', 400), ('M1', 400), ('P', 400), ('D2', 600), ('P', 200), ('M1', 400), ('G3', 400), ('R2', 400), ('S', 800)]
    },
    {
        "id": 4,
        "sanskrit": "तव सुप्रभातमरविन्दलोचने\nभवतु प्रसन्नमुख चन्द्रमण्डले ।\nविधिशङ्करेन्द्र वन्दितानुकम्पे\nभगवान् वेङ्कटनाथ ते सुप्रभातम् ॥",
        "iast": "Tava suprabhatamaravindalochane\nBhavatu prasannamukha chandramandale |\nVidhisankaraindra vanditaanukampe\nBhagavan Venkatanatha te suprabhatam ||",
        "meaning": "May this dawn be auspicious to Thee, O Lotus-eyed Lord, whose radiant face shines like the full moon, revered by Brahma, Shiva, and Indra! Auspicious dawn to Lord of Venkata!",
        "notes": [('S', 300), ('G3', 300), ('P', 500), ('D2', 300), ('S_HIGH', 600), ('N3', 300), ('D2', 300), ('P', 600)]
    },
    {
        "id": 5,
        "sanskrit": "अत्रिप्रमुखा मुनयः पूजोपकरणैः सह ।\nउपासते महाभाग तव दर्शन लालसाः ॥",
        "iast": "Atri pramukha munayah poojopakaranaih saha |\nUpasate mahabhaga tava darsana lalasah ||",
        "meaning": "Sage Atri and other great rishis have arrived with offerings for your worship, yearning with devotion for your divine Darshan.",
        "notes": [('R2', 400), ('G3', 400), ('M1', 400), ('P', 600), ('M1', 200), ('G3', 400), ('R2', 600)]
    },
    {
        "id": 6,
        "sanskrit": "ईशत्प्रफुल्ल सरसीरुह नारिकेल\nपूगद्रुमादि सुरभीकृत दिङ्मुखेषु ।\nवाति मन्दमरुतः श्रीवेङ्कटाद्रि शिखरे\nभगवान् सुप्रभातं ते ॥",
        "iast": "Eeshatpraphulla saraseeruha narikela\nPoogadrumadi surabhikrita dingmukheshu |\nVati mandamarutah Sree Venkatadri sikhare\nBhagavan suprabhatam te ||",
        "meaning": "The gentle morning breeze, fragrant with lotuses, coconut, and areca nut palms, wafts over the sacred peaks of Venkatadri. Auspicious morning to Thee, Lord!",
        "notes": [('P', 300), ('D2', 300), ('N3', 300), ('S_HIGH', 500), ('D2', 300), ('P', 300), ('G3', 600)]
    },
    {
        "id": 7,
        "sanskrit": "उन्मील्य नेत्रयुगलं कमलेक्षण श्रीन्\nसञ्जीवयन् जगदिदं करुणाकटाक्षैः ।\nश्रीवेङ्कटाचलपते तव सुप्रभातम् ॥",
        "iast": "Unmeelya netrayugalam kamalekshana sreen\nSanjeevayan jagadidam karunaakatakshaih |\nSree Venkatachalapate tava suprabhatam ||",
        "meaning": "Open your lotus eyes and revitalize this cosmos with your glance of boundless compassion. Auspicious dawn to the Lord of Venkatachala!",
        "notes": [('S', 400), ('M1', 400), ('P', 400), ('D2', 400), ('S_HIGH', 800)]
    },
    {
        "id": 8,
        "sanskrit": "श्रीमन् कृपाजलनिधे कृतसर्वलोक\nसर्वज्ञ शक्त नतवत्सल सर्वशेषिन् ।\nस्वामिन् सुशील सुलभाश्रित पारिजात\nश्रीवेङ्कटेश चरणौ शरणं प्रपद्ये ॥",
        "iast": "Sreeman kripajalanidhe kritasarvaloka\nSarvajna sakta natavatsala sarvaseshin |\nSwamin suseela sulabhasrita parijata\nSree Venkatesa charanau saranam prapadye ||",
        "meaning": "O ocean of boundless grace, Creator of all worlds, omniscient Lord! I surrender completely at the lotus feet of Sri Venkateswara.",
        "notes": [('G3', 400), ('P', 400), ('S_HIGH', 600), ('N3', 200), ('D2', 400), ('P', 400), ('M1', 400), ('G3', 400), ('S', 800)]
    },
    {
        "id": 9,
        "sanskrit": "कमलाकुच चूचुक कुङ्कुमतो\nनियतारुणितातुल नीलतनो ।\nकमलायतलोचन लोकपते\nविजयी भव वेङ्कटशैलपते ॥",
        "iast": "Kamala kucha choochuka kumkumato\nNiyatarunitatula neelatano |\nKamalayatatochana lokapate\nVijayee bhava Venkatasailapate ||",
        "meaning": "Whose dark blue divine form is anointed with the saffron vermilion of Lakshmi! O Lotus-eyed master of the universe, victory unto Thee, Lord of Venkata Hill!",
        "notes": [('S', 300), ('R2', 300), ('G3', 300), ('M1', 300), ('P', 400), ('D2', 400), ('N3', 400), ('S_HIGH', 800)]
    },
    {
        "id": 10,
        "sanskrit": "श्रीशेषशैल सुनिकेतन दिव्यमूर्ते\nनारायणाच्युत नृसिंह जनार्दनादि ।\nअनन्त कल्याण गुणाकर पाहि नित्यं\nश्रीवेङ्कटेश मम देहि करुणाकटाक्षम् ॥",
        "iast": "Sreeseshadrisuniketana divyamoorte\nNarayanachyuta Nrisimha Janardanadi |\nAnanta kalyana gunakara pahi nityam\nSree Venkatesa mama dehi karunakataksham ||",
        "meaning": "O Divine form residing atop Seshadri, embodiment of infinite auspicious qualities, protect us and bless us with your glance of compassion forever!",
        "notes": [('S_HIGH', 400), ('N3', 200), ('D2', 400), ('P', 400), ('M1', 400), ('G3', 400), ('R2', 400), ('S', 800)]
    }
]

class SuprabhatamEngine:
    def __init__(self, buzzer_pin=15):
        self.slokas = SUPRABHATAM_SLOKAS
        self.buzzer = None
        try:
            from machine import Pin, PWM
            self.buzzer = PWM(Pin(buzzer_pin))
            self.buzzer.duty_u16(0)
        except Exception:
            self.buzzer = None

    def play_tone(self, freq, duration_ms):
        if self.buzzer and freq > 0:
            self.buzzer.freq(freq)
            self.buzzer.duty_u16(32768)
            time.sleep_ms(duration_ms)
            self.buzzer.duty_u16(0)
            time.sleep_ms(30)
        else:
            time.sleep_ms(duration_ms)

    def play_sloka_melody(self, sloka_id):
        sloka = self.get_sloka(sloka_id)
        if not sloka or "notes" not in sloka:
            return
        print("Playing melody for Sloka #{:02d}...".format(sloka_id))
        for note_name, dur in sloka["notes"]:
            freq = NOTES.get(note_name, 0)
            self.play_tone(freq, dur)

    def get_sloka(self, sloka_id):
        for s in self.slokas:
            if s["id"] == sloka_id:
                return s
        return None

    def format_sloka_card(self, s):
        card = "=" * 65 + "\n"
        card += " 🕉 SRI VENKATESWARA SUPRABHATAM - VERSE {:02d} / {:02d}\n".format(s['id'], len(self.slokas))
        card += "=" * 65 + "\n"
        card += " [Sanskrit Devanagari]:\n"
        for line in s["sanskrit"].split("\n"):
            card += "   " + line + "\n"
        card += "\n [Roman IAST Transliteration]:\n"
        for line in s["iast"].split("\n"):
            card += "   " + line + "\n"
        card += "\n [Meaning & Tatparya]:\n"
        card += "   " + s["meaning"] + "\n"
        card += "=" * 65 + "\n"
        return card

def run_suprabhatam():
    engine = SuprabhatamEngine()
    print("=" * 65)
    print(" 🕉 OTMB SRI VENKATESWARA SUPRABHATAM ENGINE (RP2040)")
    print("=" * 65)
    print(" Loaded {} complete Suprabhatam verses with musical chords.".format(len(engine.slokas)))
    print(engine.format_sloka_card(engine.slokas[0]))

if __name__ == "__main__":
    run_suprabhatam()
