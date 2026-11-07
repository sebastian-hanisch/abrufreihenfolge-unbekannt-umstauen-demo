"""Gruppen, Schlüssel, Regel und Untergrenzen gegen Handrechnung (DEMO-PLAYBOOK §1b und §12)."""

import pytest

import uas_algorithm as A
from uas_scenario import make_bay


def test_group_of_by_hand():
    assert [A.group_of(n, 3) for n in range(1, 10)] == [1, 1, 1, 2, 2, 2, 3, 3, 3] and A.group_of(1, 1) == 1 and A.group_of(7, 1) == 7 and A.group_of(10, 4) == 3 and A.group_of(12, 12) == 1


def test_key_of_by_hand():
    # N = 9, g = 3, beim Abruf 1 ohne Vorschau: die 9 ist unbekannt in der Gruppe 7..9 (Schlüssel 8), die 2 in 1..3 ohne die 1 (2,5), die 5 in 4..6 (5)
    assert A.key_of(9, 1, 0, 3, 9) == 8 and A.key_of(2, 1, 0, 3, 9) == 2.5 and A.key_of(5, 1, 0, 3, 9) == 5 and A.key_of(1, 1, 0, 3, 9) == 1
    assert A.key_of(2, 1, 1, 3, 9) == 2 and A.key_of(3, 1, 1, 3, 9) == 3 and A.key_of(3, 1, 0, 3, 9) == 2.5                 # enthüllt: die Nummer selbst
    assert A.key_of(6, 4, 0, 3, 9) == 5.5 and A.key_of(6, 4, 0, 3, 9, "min") == 5 and A.key_of(6, 4, 0, 3, 9, "max") == 6     # die 4 ist der aktuelle Abruf: noch möglich 5 und 6
    assert A.key_of(8, 1, 0, 3, 8) == 7.5                                                                                     # letzte Gruppe kürzer (7, 8)
    assert A.key_of(7, 1, 5, 3, 9) == 8 and A.key_of(9, 1, 5, 3, 9) == 8                                                       # Vorschau reicht bis 6: die 7 und die 9 (Gruppe 3) bleiben unbekannt, Schlüssel 8
    assert A.key_of(4, 1, 5, 3, 9) == 4                                                                                       # 4 <= 1 + 5: enthüllt


def test_key_with_full_lookahead_is_the_number_and_with_group_one_too():
    for c in range(1, 13):
        assert A.key_of(c, 1, 12, 4, 12) == c and A.key_of(c, 1, 0, 1, 12) == c and A.key_of(c, 5, 0, 1, 12) == c


def test_simulate_by_hand(hand, counter):
    bay, h = hand
    assert [A.simulate(bay, h, 3, k) for k in (0, 1, 2, 3, 8)] == [7, 5, 5, 5, 5] and A.simulate(bay, h, 1, 0) == 5 and A.search(bay, h).optimum == 5
    bay, h = counter
    assert A.simulate(bay, h, 1, 0) == 5 and A.search(bay, h).optimum == 4                                                   # die Regel verfehlt das Optimum (Stück 1)
    assert A.simulate(((1, 2), (), ()), 2, 2, 0) == 1 and A.simulate(((2, 1),), 2, 1, 0) == 0                                # ein Blocker auf einen leeren Stapel; sortiert


def test_choose_destination_by_hand(hand):
    bay, h = hand
    st = [list(s) for s in bay]
    c = st[1].pop()                                                                                                           # die 9 über der 1
    cands, dest = A.choose_destination(st, 1, c, 1, 0, 3, 9, h)
    assert cands == [{"stack": 0, "min_key": 2.5, "safe": False}, {"stack": 2, "min_key": 2.5, "safe": False}] and dest == 0   # Gleichstand: der kleinste Index
    cands, dest = A.choose_destination(st, 1, c, 1, 2, 3, 9, h)
    assert cands == [{"stack": 0, "min_key": 2.0, "safe": False}, {"stack": 2, "min_key": 3.0, "safe": False}] and dest == 2   # die 3 liegt später als die 2: größte früheste Nummer
    assert A.choose_destination(st, 1, c, 1, 0, 3, 9, h, tie_safe=True)[1] == 0                                              # ohne sicheren Stapel ändert tie_safe nichts, der Gleichstand ist hier kein „sicher“
    full = [list(s) for s in ((1, 2), (3,))]
    assert A.choose_destination(full, 0, 2, 1, 0, 1, 3, 2) == ([{"stack": 1, "min_key": 3.0, "safe": True}], 1)              # Blocker 2: Stapel (3) hat spätere früheste Nummer: sicher
    assert A.choose_destination([[1, 2], [3, 4]], 0, 2, 1, 0, 1, 4, 2)[1] is None                                            # beide Stapel voll: kein Ziel


def test_tie_safe_changes_the_choice_when_a_stack_has_the_same_key():
    st = [[1, 6], [5, 4], [9], [2]]                                                                                           # N = 9, g = 3, Abruf 1, k = 0: der Blocker 6 hat den Schlüssel 5
    c = st[0].pop()
    cands, dest = A.choose_destination(st, 0, c, 1, 0, 3, 9, 6)
    assert [(x["stack"], x["min_key"], x["safe"]) for x in cands] == [(1, 5.0, False), (2, 8.0, True), (3, 2.5, False)] and dest == 2      # Gleichstand zählt als unsicher: nur die 9 (Schlüssel 8) ist sicher
    cands, dest = A.choose_destination(st, 0, c, 1, 0, 3, 9, 6, tie_safe=True)
    assert [x["safe"] for x in cands] == [True, True, False] and dest == 1                                                    # mit tie_safe sind beide sicher: die engste Passung (kleinste früheste Nummer) gewinnt


def test_expected_blockers_by_hand(hand):
    bay, _ = hand
    assert A.expected_blockers(bay, 3) == 3.0 and A.lb1(bay) == 3 and A.lb2(bay) == 4                                          # Hand-Bucht: alle Wahrscheinlichkeiten 0 oder 1
    assert A.expected_blockers(((1, 2),), 2) == 0.5                                                                           # die 2 über der 1 derselben Gruppe: m = 1, Blocker mit Wahrscheinlichkeit 1/2
    assert A.expected_blockers(((1, 2, 3),), 3) == pytest.approx(0.5 + 2 / 3)                                                 # die 3 hat zwei Gruppenmitglieder unter sich: 2/3
    assert A.expected_blockers(((1, 2),), 1) == 1.0 and A.expected_blockers(((2, 1),), 1) == 0.0                              # g = 1: die Zählung selbst
    assert A.expected_blockers(((3, 1), (2,)), 3) == pytest.approx(0.5)                                                       # eine Gruppe (1 2 3): die 1 über der 3 ist Blocker mit Wahrscheinlichkeit 1/2


def test_bounds_by_hand(hand, counter):
    assert A.lb1(hand[0]) == 3 and A.lb2(hand[0]) == 4 and A.lb1(counter[0]) == 3 and A.lb2(counter[0]) == 4
    assert A.lb2(()) == 0 and A.lb2(((),)) == 0 and A.stack_blockers((7, 5, 2)) == 0 and A.stack_blockers((2, 5, 7)) == 2


def test_scenario_is_deterministic_and_full():
    bay = make_bay(4, 4, 0)
    assert sorted(c for s in bay for c in s) == list(range(1, 17)) and all(len(s) == 4 for s in bay) and make_bay(4, 4, 0) == bay and make_bay(4, 4, 1) != bay


def test_simulate_raises_without_room():
    with pytest.raises(ValueError):
        A.simulate(((1, 5), (2, 3)), 2, 1, 0)                                                                                  # beide Stapel voll: die 5 findet keinen Platz
