"""Inhalt der App an festen Fällen (DEMO-PLAYBOOK §12): was im Ergebnis, in den Tabellen und in den Verdikten steht."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(preset=None):
    at = AppTest.from_file(APP, default_timeout=300)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    if preset:
        at.sidebar.button(key=f"preset_{preset}").click().run()
        assert not at.exception, [str(e) for e in at.exception]
    return at


def _text(at):
    return "\n".join(e.value for kind in (at.markdown, at.caption, at.info, at.success, at.warning) for e in kind)


def _metrics(at):
    return {m.label: (m.value, m.delta) for m in at.metric}


def test_default_page_has_the_sections_and_the_default_result():
    at = _run()
    subs = [s.value for s in at.subheader]
    assert [s for s in subs if s.startswith("🔬")] == ["🔬 Experiment: Eine Bucht von Hand", "🔬 Experiment: Der Wert der Vorschau", "🔬 Experiment: Gleichstand",
                                                       "🔬 Experiment: Die Untergrenze unter Unsicherheit", "🔬 Experiment: Das Optimum bei voller Information"]
    assert "🚧 Wo die Annahmen enden" in subs
    m = _metrics(at)
    assert m["Nur Gruppen (k = 0)"] == ("12,77", "g = 6") and m["Mit Vorschau k = 2"] == ("11,78", "7,8 % weniger") and m["Volle Information"] == ("11,24", "Untergrenze LB2 8,88")
    assert m["Erwartete Blocker"] == ("7,53", "gezählt 7,44") and m["Optimum (volle Info)"] == ("10,44", "100 Buchten gerechnet")
    assert any(i.value.startswith("4 × 4, g = 6: Nur mit den Gruppen kostet die Regel 12,77 Hübe") for i in at.info)


def test_default_page_tables_quote_the_stored_numbers():
    text = _text(_run())
    assert "| 4 × 4, g = 6 | 11,31 | 13,11 | 12,38 | 11,89 | 11,52 | 11,39 | 11,32 | 11,31 | 11,31 |" in text and "| 8 × 3, g = 6 | 10,55 | 10,98 | 10,98 | 10,98 | 10,97 | 10,95 | 10,80 | 10,74 | 10,55 |" in text
    assert "| 4 × 4, g = 4, k = 0 | 12,27 | 14,06 | 13 % weniger |" in text and "| 5 × 4, g = 6, k = 0 | 14,97 | 18,36 | 18 % weniger |" in text
    assert "| 4 × 3, g = 4 | 4,58 | 4,64 | 5,48 |" in text and "| 4 × 4 (100) | 10,44 | 11,24 | 8,88 | 7,7 % |" in text and "| 4 × 3 (100) | 5,81 | 5,92 | 5,35 | 1,9 % |" in text
    assert "4 × 4, g = 6: Ab einer Vorschau auf 4 Abrufe sind 90 % der Lücke geschlossen (Gruppengröße 6). Eine Vorschau bis zur Gruppengröße genügt." in text


def test_hand_section_shows_the_two_decisions():
    text = _text(_run())
    assert "| 0 | 8 | 2,50 | 2,50 | Stapel 1 | 7 |" in text and "| 1 | 8 | 2 | 3 | Stapel 3 | 5 |" in text and "| 2 | 8 | 2 | 3 | Stapel 3 | 5 |" in text
    assert "Gleichstand, die Regel nimmt Stapel 1 und braucht 7 Hübe" in text and "das **Optimum** bei voller Information (5)" in text


def test_marginal_table_for_the_live_sample():
    text = _text(_run())
    assert "| 0 | 12,77 | – | 0,0 % |" in text and "| 1 | 12,21 | 0,56 | 37 % |" in text and "| 2 | 11,78 | 0,43 | 65 % |" in text and "| alle | 11,24 | 0 | 100 % |" in text


def test_full_information_preset_says_the_order_is_irrelevant():
    at = _run("Volle Information (g = 1)")
    assert _metrics(at)["Nur Gruppen (k = 0)"][0] == "11,24" and _metrics(at)["Volle Information"][0] == "11,24"
    assert any("Die Reihenfolge ist hier fast egal" in i.value for i in at.info)


def test_many_stacks_preset_has_no_exact_optimum():
    at = _run("Viele Stapel: egal (8 Stapel, 3 Lagen, g = 6)")
    assert _metrics(at)["Optimum (volle Info)"] == ("nicht gerechnet", "über 16 Container") and _metrics(at)["Nur Gruppen (k = 0)"][0] == "10,93"


@pytest.mark.parametrize("stacks,group", [(3, 6), (6, 12)])
def test_settings_without_stored_bands_do_not_crash(stacks, group):
    at = _run()
    at.sidebar.select_slider(key="stacks_slider").set_value(stacks).run()
    at.sidebar.select_slider(key="group_slider").set_value(group).run()
    assert not at.exception
    text = _text(at)
    assert "ist nicht vorberechnet; gezeigt wird 4 × 4" in text and "wurde der Gleichstand nicht vorberechnet" in text.replace("Für Ihre Einstellung wurde der Gleichstand", "wurde der Gleichstand")
