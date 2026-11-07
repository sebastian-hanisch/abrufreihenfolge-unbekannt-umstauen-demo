"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

import pytest

import uas_algorithm as A
import uas_constants as C
import uas_evaluation as ev
import uas_presets as P


def test_effective_ks_clip_and_include_the_chosen_step_and_all():
    assert ev.effective_ks(16) == [0, 1, 2, 3, 4, 6, 8, 16] and ev.effective_ks(16, 12) == [0, 1, 2, 3, 4, 6, 8, 12, 16]
    assert ev.effective_ks(6) == [0, 1, 2, 3, 4, 6] and ev.effective_ks(6, 24) == [0, 1, 2, 3, 4, 6] and ev.effective_ks(24, 24) == [0, 1, 2, 3, 4, 6, 8, 24]
    assert ev.effective_ks(8, 5) == [0, 1, 2, 3, 4, 5, 6, 8]


def test_hub_at_clips_the_lookahead_to_the_number_of_containers():
    stats = {"ks": [0, 1, 2, 6], "hubs": [5.0, 4.5, 4.0, 3.0]}
    assert ev.hub_at(stats, 2) == 4.0 and ev.hub_at(stats, 24) == 3.0 and ev.hub_at(stats, 6) == 3.0
    with pytest.raises(ValueError):
        ev.hub_at(stats, 5)                                                                       # nicht gerechnet


def test_analysis_with_all_ks_and_the_exact_limit():
    a = ev.analyse(ev.Settings(4, 4, 2, 6, 24, 20, 0))                                           # k = 24 über N = 16: auf 16 begrenzt
    assert a.containers == 16 and a.exact and a.stats["ks"] == [0, 1, 2, 3, 4, 6, 8, 16] and "opt" in a.stats and a.stats["opt"]["n"] == 20
    b = ev.analyse(ev.Settings(5, 4, 2, 6, 2, 20, 0))                                            # 20 Container: kein Optimum
    assert not b.exact and "opt" not in b.stats and b.containers == 20 and b.stats["ks"][-1] == 20


def test_group_one_has_no_gap_and_the_verdict_says_so():
    a = ev.analyse(ev.Settings(4, 3, 2, 1, 0, 20, 0))
    assert a.stats["hubs"] == [a.stats["full"]] * len(a.stats["ks"]) and a.stats["eb"] == pytest.approx(a.stats["lb1"])      # g = 1: erwartete Blocker = gezählte
    assert ev.share_closed(a.stats, 0) is None and ev.verdict_info(a.stats, 2, "x")[0] == "info" and "fast egal" in ev.verdict_info(a.stats, 2, "x")[1]
    assert ev.verdict_curve(a.stats, 1, "x")[0] == "info"


def test_group_larger_than_the_bay_is_one_group_and_the_rule_still_runs():
    a = ev.analyse(ev.Settings(3, 2, 2, 12, 0, 20, 0))                                           # g = 12 über N = 6: alles eine Gruppe
    assert a.stats["hubs"][0] >= a.stats["full"] and all(h >= a.stats["full"] - 1e-9 for h in a.stats["hubs"][:-1])
    assert a.stats["hubs"][-1] == a.stats["full"]                                                # alle enthüllt: volle Information


def test_share_closed_by_hand_and_the_marginal_rows():
    stats = {"full": 10.0, "ks": [0, 1, 2, 4], "hubs": [12.0, 11.0, 10.5, 10.0], "lb1": 8.0, "lb2": 9.0, "eb": 8.0}
    assert ev.gap(stats) == 2.0 and ev.share_closed(stats, 0) == 0.0 and ev.share_closed(stats, 1) == 0.5 and ev.share_closed(stats, 4) == 1.0
    assert ev.k_share(stats, 0.5) == 1 and ev.k_share(stats, 0.9) == 4 and ev.k_share(stats, 1.0) == 4
    rows = ev.marginal_rows(stats)
    assert rows[0] == {"k": 0, "hubs": 12.0, "saved": None, "share": 0.0} and rows[1] == {"k": 1, "hubs": 11.0, "saved": 1.0, "share": 0.5} and rows[3]["saved"] == 0.5
    small = {"full": 10.0, "ks": [0, 4], "hubs": [10.05, 10.0]}
    assert ev.share_closed(small, 4) is None and ev.k_share(small, 0.5) is None and ev.marginal_rows(small)[1]["share"] is None
    edge = {"full": 10.0, "ks": [0, 4], "hubs": [10.1, 10.0]}                                    # Lücke genau NEGLIGIBLE_GAP zählt noch
    assert ev.share_closed(edge, 4) == pytest.approx(1.0)


def test_snap_moves_values_to_the_nearest_step_or_the_bounds():
    assert P.snap("stacks_slider", 7) == 6 and P.snap("stacks_slider", 100) == 8 and P.snap("stacks_slider", 1) == 3 and P.snap("group_slider", 5) == 4 and P.snap("group_slider", 10) == 8
    assert P.snap("lookahead_slider", 5) == 4 and P.snap("lookahead_slider", 100) == 24 and P.snap("lookahead_slider", -2) == 0 and P.snap("bays_slider", 80) == 100
    assert P.snap("layers_slider", 9) == 5 and P.snap("layers_slider", 0) == 2 and P.snap("seed_input", -3) == 0
    assert P.snap("group_slider", 5) == 4 and P.snap("group_slider", 7) == 6                       # genau in der Mitte: die kleinere Stufe


def test_number_formats():
    assert ev.num(5) == "5" and ev.num(60234) == "60 234"
    assert ev.dec(5.0) == "5" and ev.dec(6.505) == "6,51" and ev.dec(1.635) == "1,64" and ev.dec(0.665) == "0,67" and ev.dec(4.999999999) == "5" and ev.dec(1234.5) == "1 234,50"
    assert ev.percent_text(0.0259) == "2,6 %" and ev.percent_text(0.0625) == "6,3 %" and ev.percent_text(0.473) == "47 %" and ev.percent_text(0.05) == "5,0 %" and ev.percent_text(0.725) == "73 %"
    assert ev.curve_key(4, 4, 6) == "4,4,6" and ev.tie_key(4, 4, 6, 0) == "4,4,6,0"
