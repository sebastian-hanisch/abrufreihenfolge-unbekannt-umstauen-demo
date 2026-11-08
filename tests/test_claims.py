"""Aussagen der Demo und des READMEs gegen die vorberechneten Bänder und gegen eine frische Nachrechnung kleiner Zellen (DEMO-PLAYBOOK §5, §12).

Alle Größen sind deterministisch (feste Seeds, Zählungen, keine Zeiten) und müssen bei der Nachrechnung gleich sein."""

import pytest

import uas_constants as C
import uas_evaluation as ev


def _b():
    return ev.load_bands()


def test_the_stored_cells_cover_exactly_the_cells_of_the_constants():
    b = _b()
    assert set(b["kurve"]) == {ev.curve_key(s, l, g) for s, l in C.CURVE_CELLS for g in C.CURVE_GROUPS} and all(c["n"] == C.CURVE_BAYS for c in b["kurve"].values())
    assert set(b["gleichstand"]) == {ev.tie_key(s, l, g, k) for s, l, g in C.TIE_CELLS for k in C.TIE_KS} and all(c["n"] == C.CURVE_BAYS for c in b["gleichstand"].values())
    assert set(b["exakt"]) == {f"{s},{l}" for s, l in C.EXACT_CELLS} and all(c["opt"]["n"] == C.EXACT_BAYS for c in b["exakt"].values())


def test_the_hubs_fall_with_the_lookahead_and_end_at_full_information():
    for c in _b()["kurve"].values():
        assert all(x >= y - 1e-9 for x, y in zip(c["hubs"], c["hubs"][1:])), c["ks"]                      # nicht steigend im Mittel
        assert c["hubs"][-1] == pytest.approx(c["full"]) and c["hubs"][0] >= c["full"] - 1e-9


def test_the_cost_of_not_knowing_grows_with_the_group_size_and_shrinks_with_more_stacks_at_equal_layers():
    kurve = _b()["kurve"]
    for s, l in C.CURVE_CELLS:
        h0 = [kurve[ev.curve_key(s, l, g)]["hubs"][0] for g in C.CURVE_GROUPS]
        assert h0 == sorted(h0), (s, l, h0)
    rel = lambda s, l: kurve[ev.curve_key(s, l, 6)]["hubs"][0] / kurve[ev.curve_key(s, l, 6)]["full"] - 1
    assert rel(4, 4) > rel(5, 4) and rel(4, 3) > rel(8, 3) and round(rel(4, 4), 2) == 0.16 and round(rel(8, 3), 2) == 0.04      # gleiche Lagenzahl: 4 × 4 gegen 5 × 4, 4 × 3 gegen 8 × 3
    assert round(rel(4, 3), 3) == 0.146 and round(rel(5, 4), 3) == 0.134


def test_the_numbers_the_readme_quotes_for_the_curve():
    k = _b()["kurve"]
    c = k[ev.curve_key(4, 4, 6)]
    assert c["ks"] == [0, 1, 2, 3, 4, 6, 8, 16] and c["hubs"] == pytest.approx([13.11, 12.38, 11.89, 11.52, 11.39, 11.32, 11.305, 11.305], abs=0.006) and c["full"] == pytest.approx(11.305)
    assert k[ev.curve_key(4, 3, 6)]["hubs"] == pytest.approx([6.96, 6.62, 6.3, 6.16, 6.11, 6.08, 6.08, 6.08], abs=0.006)
    assert k[ev.curve_key(5, 4, 6)]["hubs"] == pytest.approx([14.965, 14.625, 14.09, 13.83, 13.565, 13.315, 13.24, 13.2], abs=0.006)
    assert k[ev.curve_key(8, 3, 6)]["hubs"] == pytest.approx([10.98, 10.98, 10.98, 10.97, 10.95, 10.8, 10.735, 10.55], abs=0.006)
    assert [k[ev.curve_key(4, 4, g)]["hubs"][0] - k[ev.curve_key(4, 4, g)]["full"] for g in (2, 4, 6)] == pytest.approx([0.305, 0.965, 1.805], abs=0.006)
    assert ev.share_closed(c, 2) == pytest.approx(0.675, abs=0.002) and ev.k_share(c, 0.9) == 4 and ev.k_share(k[ev.curve_key(4, 3, 6)], 0.9) == 3


def test_information_beyond_the_group_size_is_worth_almost_nothing_in_the_small_cells():
    kurve = _b()["kurve"]
    for s, l in ((4, 3), (4, 4)):
        for g in C.CURVE_GROUPS:
            c = kurve[ev.curve_key(s, l, g)]
            assert ev.hub_at(c, max(g, 4)) - c["full"] < 0.09, (s, l, g)                              # ab k = g (mindestens 4) ist die Lücke bis auf 0,09 Hübe zu
    assert kurve[ev.curve_key(4, 3, 6)]["hubs"][5] == pytest.approx(kurve[ev.curve_key(4, 3, 6)]["full"], abs=0.006)         # 4 × 3, g = 6: ab k = 6 gleich


def test_the_tie_numbers_the_readme_quotes():
    t = _b()["gleichstand"]
    flat = [v for k in ("4,3,4,0", "4,4,4,0", "4,4,6,0", "5,4,6,0") for v in (t[k]["strict"], t[k]["safe"])]
    assert flat == pytest.approx([6.505, 8.21, 12.27, 14.06, 13.105, 14.96, 14.965, 18.36], abs=0.006)
    assert all(t[k]["strict"] < t[k]["safe"] for k in t) and [t["4,4,4,2"]["strict"], t["4,4,4,2"]["safe"]] == pytest.approx([11.66, 11.96], abs=0.006)
    assert all(t[f"{s},{l},{g},2"]["safe"] - t[f"{s},{l},{g},2"]["strict"] < t[f"{s},{l},{g},0"]["safe"] - t[f"{s},{l},{g},0"]["strict"] for s, l, g in C.TIE_CELLS)   # mit Vorschau schrumpft der Unterschied


def test_the_expected_blockers_match_the_count_within_six_hundredths():
    kurve = _b()["kurve"]
    for key, c in kurve.items():
        assert abs(c["eb"] - c["lb1"]) <= 0.06, key
    assert (kurve["4,3,4"]["eb"], kurve["4,3,4"]["lb1"]) == pytest.approx((4.58, 4.635), abs=0.006) and kurve["4,4,6"]["eb"] == pytest.approx(7.62, abs=0.006) and kurve["8,3,4"]["eb"] == pytest.approx(9.22, abs=0.006)


def test_the_exact_numbers_the_readme_quotes():
    e = _b()["exakt"]
    assert {k: (c["opt"]["opt"], c["opt"]["full"], c["opt"]["lb2"]) for k, c in e.items()} == {"4,3": pytest.approx((5.81, 5.92, 5.35), abs=0.006), "4,4": pytest.approx((10.44, 11.24, 8.88), abs=0.006)}


@pytest.mark.parametrize("stacks,layers,group", [(4, 3, 4), (4, 3, 6), (4, 4, 2)])
def test_a_fresh_recomputation_of_a_curve_cell_reproduces_the_stored_band(stacks, layers, group):
    ks = ev.effective_ks(stacks * layers)
    fresh = ev.curve_stats(ev.bay_rows(stacks, layers, C.DEFAULT_EXTRA, group, ks, range(C.CURVE_BAYS)), ks)
    assert fresh == _b()["kurve"][ev.curve_key(stacks, layers, group)]


def test_a_fresh_recomputation_of_a_tie_cell_and_the_exact_cell_reproduces_the_stored_bands():
    assert ev.tie_stats(4, 3, 4, 0) == _b()["gleichstand"]["4,3,4,0"]
    ks = ev.effective_ks(12)
    fresh = ev.curve_stats(ev.bay_rows(4, 3, C.DEFAULT_EXTRA, 6, ks, range(C.EXACT_BAYS), True, 400_000), ks)
    assert fresh == _b()["exakt"]["4,3"]
