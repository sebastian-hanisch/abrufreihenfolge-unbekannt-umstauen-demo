"""Gemeinsame Fixtures: die Buchten, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand():
    """Die Bucht von Hand: (2, 7, 4), (6, 1, 9), (8, 5, 3), Höchsthöhe 5, Gruppen aus je 3 Nummern ((1 2 3), (4 5 6), (7 8 9)). Blocker an den wahren Nummern: 7 und 4 über der 2, die 9 über der 1:
    LB1 = 3; die 9 hat keinen sicheren Stapel (Minima 2 und 3): LB2 = 4. Erwartete Blocker bei Gruppen: 7 und 4 sind sicher Blocker (unter ihnen die 2 einer früheren Gruppe), die 9 ebenfalls
    (unter ihr die 6 und die 1), alle anderen Container haben nur Container derselben oder späterer Gruppen unter sich ohne Gleichgruppe (m = 0): 3,0. Ohne Vorschau (k = 0) sehen die Stapel
    1 und 3 gleich aus (früheste mögliche Nummer 2,5), die Regel wählt Stapel 1 und braucht 7 Hübe; ab k = 1 wählt sie Stapel 3 und trifft das Optimum 5."""
    return ((2, 7, 4), (6, 1, 9), (8, 5, 3)), 5


@pytest.fixture
def counter():
    """Das Gegenbeispiel aus Stück 1: (3, 6), (2, 4), (1, 5), Höchsthöhe 4: Optimum 4, die Regel braucht bei voller Information 5."""
    return ((3, 6), (2, 4), (1, 5)), 4
