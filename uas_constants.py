"""Konstanten: Regler-Stufen, feste Annahmen, Farben und Presets."""

STACK_OPTIONS = (3, 4, 5, 6, 8)                           # Zahl der Stapel (Stufen des Reglers)
DEFAULT_STACKS = 4
LAYERS_MIN, LAYERS_MAX, DEFAULT_LAYERS = 2, 5, 4          # Anfangsfüllung je Stapel (Lagen)
EXTRA_MIN, EXTRA_MAX, DEFAULT_EXTRA = 1, 4, 2             # Platz: Höchsthöhe = Lagen + Zuschlag (Standard 2 wie in Stück 1 bis 11)
GROUP_OPTIONS = (1, 2, 3, 4, 6, 8, 12)                    # Gruppengröße g (1 = volle Information)
DEFAULT_GROUP = 6
LOOKAHEAD_OPTIONS = (0, 1, 2, 3, 4, 6, 8, 12, 24)         # Vorschau k: so viele Abrufe nach dem aktuellen sind vorab bekannt
DEFAULT_LOOKAHEAD = 2
BAY_OPTIONS = (20, 50, 100, 200)                          # Zahl der Buchten einer Stichprobe (Stufen des Reglers)
DEFAULT_BAYS = 100
DEFAULT_SEED = 0                                          # erste Bucht-Nummer der Stichprobe: Seeds seed bis seed + Buchten − 1
SEED_MAX = 999999

CURVE_KS = (0, 1, 2, 3, 4, 6, 8)                          # Vorschau-Stufen der Kurve (dazu „alle“ = volle Information)
EXACT_MAX_CONTAINERS = 16                                 # das Optimum bei voller Information wird live nur bis zu dieser Containerzahl gerechnet
EXACT_CAP = 100_000                                       # Knotenlimit der Suche je Bucht

# Zellen der vorberechneten Tabellen. Dieselben Buchten wie in Stück 1 bis 11 (Seeds ab 0, Platz 2).
CURVE_CELLS = ((4, 3), (4, 4), (5, 4), (8, 3))            # A: Hubzahl gegen Vorschau (Stapel, Lagen)
CURVE_GROUPS = (2, 3, 4, 6)
CURVE_BAYS = 200
TIE_CELLS = ((4, 3, 4), (4, 4, 4), (4, 4, 6), (5, 4, 6))  # C: Gleichstand (Stapel, Lagen, Gruppengröße), Vorschau 0 und 2
TIE_KS = (0, 2)
EXACT_CELLS = ((4, 3), (4, 4))                            # B: Optimum bei voller Information
EXACT_BAYS = 100

# Schwellen der Verdikte
SHARE_ALMOST = 0.9                                        # „fast die ganze Lücke“: Anteil der Lücke zur vollen Information, den die Vorschau schließt, ab hier
SHARE_HALF = 0.5                                          # „etwa die Hälfte“: darunter „wenig“
NEGLIGIBLE_GAP = 0.1                                      # Lücke zur vollen Information (Hübe, Mittel) unter dieser Schwelle: „Reihenfolge fast egal“
TIE_GAIN = 0.05                                           # „Vorsicht bei Gleichstand lohnt“: relative Ersparnis ab hier
EXPECT_TOL = 0.02                                         # „Erwartungswert trifft“: relative Abweichung der erwarteten von der wahren Blockerzahl höchstens so groß

COLOR_CELL = "#7a8fa6"
COLOR_BLOCK = "#b5545a"        # blockierend (liegt über einem früher abzurufenden)
COLOR_TARGET = "#2F6B65"       # nächster Abruf
COLOR_LINES = {1: "#1c4742", 2: "#7a8fa6", 3: "#2F6B65", 4: "#d9822b", 6: "#4c78a8", 8: "#b5545a", 12: "#8b6bb0"}     # je Gruppengröße
COLOR_FULL, COLOR_LB, COLOR_OPT = "#1c4742", "#7a8fa6", "#2F6B65"

# Sonderbuchten und Presets (Eigenschaften in tests/test_presets.py)
HAND_BAY = ((2, 7, 4), (6, 1, 9), (8, 5, 3))              # 3 Stapel, Höchsthöhe 5, Gruppen aus je 3 Nummern: (1 2 3) (4 5 6) (7 8 9)
HAND_HEIGHT = 5
HAND_GROUP = 3
PRESETS = {
    "Zwei Abrufe voraus (4 Stapel, 4 Lagen, g = 6)": {"stacks": 4, "layers": 4, "extra": DEFAULT_EXTRA, "group": 6, "lookahead": 2, "bays": 100, "seed": 0},
    "Nur Gruppen (4 Stapel, 4 Lagen, g = 6)": {"stacks": 4, "layers": 4, "extra": DEFAULT_EXTRA, "group": 6, "lookahead": 0, "bays": 100, "seed": 0},
    "Volle Information (g = 1)": {"stacks": 4, "layers": 4, "extra": DEFAULT_EXTRA, "group": 1, "lookahead": 0, "bays": 100, "seed": 0},
    "Viele Stapel: egal (8 Stapel, 3 Lagen, g = 6)": {"stacks": 8, "layers": 3, "extra": DEFAULT_EXTRA, "group": 6, "lookahead": 0, "bays": 100, "seed": 0},
    "Kleine Gruppen (4 Stapel, 4 Lagen, g = 2)": {"stacks": 4, "layers": 4, "extra": DEFAULT_EXTRA, "group": 2, "lookahead": 0, "bays": 100, "seed": 0},
}
PRESET_HELP = {
    "Zwei Abrufe voraus (4 Stapel, 4 Lagen, g = 6)": "Dieselben Buchten, aber die nächsten zwei Abrufe sind vorab bekannt: fast zwei Drittel der Lücke sind zu.",
    "Nur Gruppen (4 Stapel, 4 Lagen, g = 6)": "16 Container, Gruppen aus 6 Nummern, keine Vorschau: die Regel braucht rund 14 % mehr Hübe als bei voller Information.",
    "Volle Information (g = 1)": "Jede Nummer ist eine Gruppe: die Regel kennt alles, die Lücke ist null (Vergleichsmaß der anderen Presets).",
    "Viele Stapel: egal (8 Stapel, 3 Lagen, g = 6)": "24 Container: bei vielen Stapeln findet die große Mehrheit der Blocker einen sicheren Stapel, das Nichtwissen kostet nur rund 4 %.",
    "Kleine Gruppen (4 Stapel, 4 Lagen, g = 2)": "Gruppen aus 2 Nummern: das Nichtwissen kostet nur rund 2 % mehr Hübe.",
}
