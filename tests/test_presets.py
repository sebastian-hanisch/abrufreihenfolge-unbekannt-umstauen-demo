"""Presets: jede Einstellung hat die Eigenschaft, für die sie steht (DEMO-PLAYBOOK §12), und die Hilfetexte nennen nur gemessene Zahlen."""

import pytest

import uas_constants as C
import uas_evaluation as ev
import uas_presets as P


def _analyse(name):
    p = C.PRESETS[name]
    return ev.analyse(ev.Settings(p["stacks"], p["layers"], p["extra"], p["group"], p["lookahead"], p["bays"], p["seed"]))


def test_every_preset_is_inside_the_slider_bounds_and_on_a_step_and_has_help():
    for name, p in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            lo, hi = P.bounds(state_key)
            assert lo <= p[key] <= hi and P.snap(state_key, p[key]) == p[key], (name, key)
    assert set(C.PRESET_HELP) == set(C.PRESETS) and all(C.PRESET_HELP.values())


def test_only_groups_costs_a_seventh_more():
    a = _analyse("Nur Gruppen (4 Stapel, 4 Lagen, g = 6)")
    s = a.stats
    assert a.exact and s["n"] == 100 and ev.hub_at(s, 0) == pytest.approx(12.77) and s["full"] == pytest.approx(11.24) and round(ev.hub_at(s, 0) / s["full"] - 1, 2) == 0.14
    assert ev.verdict_info(s, 0, "x")[0] == "warning"


def test_two_lookahead_steps_close_more_than_half_of_the_gap():
    s = _analyse("Zwei Abrufe voraus (4 Stapel, 4 Lagen, g = 6)").stats
    assert ev.hub_at(s, 2) == pytest.approx(11.78) and round(ev.share_closed(s, 2), 2) == 0.65 and ev.verdict_info(s, 2, "x")[0] == "info"


def test_full_information_has_no_gap():
    s = _analyse("Volle Information (g = 1)").stats
    assert ev.gap(s) == pytest.approx(0.0) and ev.share_closed(s, 0) is None and s["eb"] == pytest.approx(s["lb1"])


def test_many_stacks_make_the_order_nearly_irrelevant():
    a = _analyse("Viele Stapel: egal (8 Stapel, 3 Lagen, g = 6)")
    s = a.stats
    assert not a.exact and a.containers == 24 and round(ev.hub_at(s, 0) / s["full"] - 1, 3) == 0.039 and ev.gap(s) == pytest.approx(0.43, abs=0.02)


def test_small_groups_cost_little():
    s = _analyse("Kleine Gruppen (4 Stapel, 4 Lagen, g = 2)").stats
    assert round(ev.hub_at(s, 0) / s["full"] - 1, 2) == 0.02


def test_the_default_settings_are_the_first_preset_with_a_lookahead_of_two():
    assert {s: P.SETTING_SPECS[s].default for s in P.SETTING_SPECS} == {"stacks_slider": 4, "layers_slider": 4, "extra_slider": 2, "group_slider": 6, "lookahead_slider": 2, "bays_slider": 100,
                                                                      "seed_input": 0}
    assert next(iter(C.PRESETS)) == "Zwei Abrufe voraus (4 Stapel, 4 Lagen, g = 6)" and C.PRESETS[next(iter(C.PRESETS))] == {"stacks": 4, "layers": 4, "extra": 2, "group": 6, "lookahead": 2, "bays": 100, "seed": 0}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_apply_preset_writes_every_setting(name, monkeypatch):
    state = {}
    monkeypatch.setattr(P.st, "session_state", state)
    P.apply_preset(name)
    assert {k: state[sk] for k, sk in P.PRESET_KEYS.items()} == {k: C.PRESETS[name][k] for k in P.PRESET_KEYS}
    assert P.aktives_preset() == name
