"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import uas_constants as C
import uas_evaluation as ev


def _stats(h0=13.0, full=11.0, hubs=None, ks=(0, 1, 2, 4, 16), lb1=7.5, eb=7.5, lb2=9.0):
    hubs = hubs or [h0, 12.0, 11.4, 11.1, full]
    return {"full": full, "ks": list(ks), "hubs": list(hubs), "lb1": lb1, "eb": eb, "lb2": lb2}


def test_info_verdict_three_states_and_numbers():
    kind, text = ev.verdict_info(_stats(), 4, "4 × 4, g = 6")
    assert kind == "success" and text == ("4 × 4, g = 6: Nur mit den Gruppen kostet die Regel 13 Hübe, bei voller Information 11 (18 % mehr); mit Vorschau auf 4 Abrufe 11,10 Hübe: "
                                          "95 % der Lücke sind geschlossen. Damit ist fast die ganze Lücke zu.")
    kind, text = ev.verdict_info(_stats(), 1, "x")
    assert kind == "info" and "mit Vorschau auf 1 Abrufe 12 Hübe: 50 % der Lücke sind geschlossen." in text and text.endswith("Damit ist etwa die Hälfte der Lücke oder mehr zu.")
    kind, text = ev.verdict_info(_stats(), 0, "x")
    assert kind == "warning" and "0 % der Lücke sind geschlossen" in text and text.endswith("Damit ist erst weniger als die Hälfte der Lücke zu.")


def test_info_verdict_thresholds_are_inclusive():
    # Lücke 2 Hübe: Anteil 0,9 bei 11,2 (genau SHARE_ALMOST), 0,5 bei 12,0 (genau SHARE_HALF)
    assert ev.verdict_info(_stats(hubs=[13.0, 12.0, 11.2, 11.1, 11.0]), 2, "x")[0] == "success" and C.SHARE_ALMOST == 0.9
    assert ev.verdict_info(_stats(hubs=[13.0, 12.0, 11.21, 11.1, 11.0]), 2, "x")[0] == "info"
    assert ev.verdict_info(_stats(hubs=[13.0, 12.0, 11.2, 11.1, 11.0]), 1, "x")[0] == "info" and C.SHARE_HALF == 0.5
    assert ev.verdict_info(_stats(hubs=[13.0, 12.01, 11.2, 11.1, 11.0]), 1, "x")[0] == "warning"


def test_info_verdict_without_a_gap():
    s = _stats(h0=11.05, full=11.0, hubs=[11.05, 11.04, 11.03, 11.02, 11.0])
    assert ev.verdict_info(s, 2, "8 × 3, g = 2") == ("info", "8 × 3, g = 2: Die Reihenfolge ist hier fast egal: Nur mit den Gruppen kostet die Regel 11,05 Hübe, bei voller Information 11.")
    edge = _stats(h0=11.1, full=11.0, hubs=[11.1, 11.05, 11.02, 11.01, 11.0])                                                         # Lücke genau 0,1 (NEGLIGIBLE_GAP) zählt noch
    assert ev.verdict_info(edge, 0, "x")[0] == "warning" and ev.verdict_info(edge, 2, "x")[0] == "info" and "80 % der Lücke" in ev.verdict_info(edge, 2, "x")[1]
    assert C.NEGLIGIBLE_GAP == 0.1


def test_curve_verdict_states_and_numbers():
    kind, text = ev.verdict_curve(_stats(), 6, "4 × 4, g = 6")
    assert kind == "success" and text == "4 × 4, g = 6: Ab einer Vorschau auf 4 Abrufe sind 90 % der Lücke geschlossen (Gruppengröße 6). Eine Vorschau bis zur Gruppengröße genügt."
    assert ev.verdict_curve(_stats(), 4, "x")[0] == "success"                                                                        # k90 = g zählt noch
    kind, text = ev.verdict_curve(_stats(), 3, "x")
    assert kind == "warning" and text.endswith("Das ist mehr als die Gruppengröße.")
    kind, text = ev.verdict_curve(_stats(hubs=[13.0, 13.0, 13.0, 13.0, 11.0], ks=(0, 1, 2, 4, 16)), 6, "8 × 3, g = 6")
    assert kind == "warning" and "Ab einer Vorschau auf 16 Abrufe" in text                                                            # erst die volle Information schließt die Lücke
    kind, text = ev.verdict_curve(_stats(h0=11.05, hubs=[11.05, 11.04, 11.03, 11.02, 11.0]), 6, "x")
    assert kind == "info" and text == "x: Die Lücke zur vollen Information ist kleiner als 0,10 Hübe; die Vorschau bringt hier nichts mehr."


def test_tie_verdict_three_states_and_numbers():
    kind, text = ev.verdict_tie(12.27, 14.06, "4 × 4, g = 4, k = 0")
    assert kind == "success" and text == ("4 × 4, g = 4, k = 0: Wenn Gleichstand als unsicher gilt, kostet die Regel 12,27 Hübe, wenn er als sicher gilt 14,06 (13 % weniger). "
                                          "Vorsicht bei Gleichstand lohnt.")
    assert ev.verdict_tie(95.0, 100.0, "x")[0] == "success" and C.TIE_GAIN == 0.05 and ev.verdict_tie(95.1, 100.0, "x")[0] == "info"        # genau 5 % zählt
    kind, text = ev.verdict_tie(10.2, 10.0, "x")
    assert kind == "info" and text.endswith("Der Unterschied ist klein.") and "(2,0 % mehr)" in text
    kind, text = ev.verdict_tie(10.5, 10.0, "x")
    assert kind == "warning" and text.endswith("Hier ist Vertrauen bei Gleichstand besser.") and ev.verdict_tie(10.49, 10.0, "x")[0] == "info"


def test_expect_verdict_two_states_and_numbers():
    kind, text = ev.verdict_expect(_stats(lb1=7.67, eb=7.62), 6, "4 × 4, g = 6")
    assert kind == "success" and text == ("4 × 4, g = 6: Erwartete Blocker bei Gruppengröße 6: 7,62, gezählt an den wahren Nummern: 7,67 (Abweichung 0,7 %). Die erwartete Zahl trifft die Zählung.")
    assert ev.verdict_expect(_stats(lb1=10.0, eb=10.2), 6, "x")[0] == "success" and C.EXPECT_TOL == 0.02 and ev.verdict_expect(_stats(lb1=10.0, eb=10.21), 6, "x")[0] == "info"
    kind, text = ev.verdict_expect(_stats(lb1=10.0, eb=9.0), 3, "x")
    assert kind == "info" and text.endswith("Die Stichprobe weicht vom Erwartungswert ab.") and "(Abweichung 10 %)" in text
    assert ev.verdict_expect(_stats(lb1=0.0, eb=0.4), 3, "x") == ("info", "x: Keine Blocker an den wahren Nummern; die erwartete Zahl ist 0,40.")


def test_hand_decision_by_hand():
    d0, d1, d2 = ev.hand_decision(0), ev.hand_decision(1), ev.hand_decision(2)
    assert d0["blocker"] == 9 and d0["key"] == 8 and d0["dest"] == 0 and d0["hubs"] == 7 and d0["optimum"] == 5
    assert [c["min_key"] for c in d0["candidates"]] == [2.5, 2.5] and [c["content"] for c in d0["candidates"]] == [(2, 7, 4), (8, 5, 3)]
    assert d1["dest"] == 2 and d1["hubs"] == 5 and [c["min_key"] for c in d1["candidates"]] == [2.0, 3.0] and d2["dest"] == 2 and d2["hubs"] == 5
