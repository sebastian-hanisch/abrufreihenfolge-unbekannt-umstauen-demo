"""Abbildungen an synthetischen Daten: Werte, Farben, gesperrte Achsen (DEMO-PLAYBOOK §12)."""

import plotly.graph_objects as go
import pytest

import uas_constants as C
import uas_visualization as V


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def test_blocker_cells_by_hand():
    assert V.blocker_cells(((2, 7, 4), (6, 1, 9), (8, 5, 3))) == {(0, 1), (0, 2), (1, 2)} and V.blocker_cells(((7, 5, 2), (), (6,))) == set()


def test_bay_chart_colours_the_target_and_the_blockers():
    fig = V.build_bay(((2, 7, 4), (6, 1, 9), (8, 5, 3)), 5, target=1)
    assert _locked(fig) and len(fig.data) == 5 and list(fig.layout.yaxis.range) == [0, 5.35]
    assert list(fig.data[0].marker.color) == [C.COLOR_CELL, C.COLOR_CELL, C.COLOR_CELL] and list(fig.data[1].marker.color) == [C.COLOR_BLOCK, C.COLOR_TARGET, C.COLOR_CELL]
    assert list(fig.data[2].marker.color) == [C.COLOR_BLOCK, C.COLOR_BLOCK, C.COLOR_CELL] and list(fig.data[3].y) == [0, 0, 0] and [s.y0 for s in fig.layout.shapes] == [5]


def test_curve_chart_has_one_line_per_group_and_the_references_and_a_category_axis():
    ks = [0, 1, 2, 4, 16]
    series = [("g = 2", ks, [6.0, 5.8, 5.6, 5.5, 5.4], C.COLOR_LINES[2]), ("g = 6", ks, [7.0, 6.5, 6.0, 5.6, 5.4], C.COLOR_LINES[6])]
    fig = V.build_curve(series, 5.4, 4.0)
    assert _locked(fig) and fig.layout.xaxis.type == "category" and not fig.layout.shapes
    assert [t.name for t in fig.data] == ["g = 2", "g = 6", "volle Information", "Untergrenze LB2"] and list(fig.data[0].x) == ["0", "1", "2", "4", "alle"]
    assert list(fig.data[1].y) == [7.0, 6.5, 6.0, 5.6, 5.4] and list(fig.data[2].y) == [5.4] * 5 and list(fig.data[3].y) == [4.0] * 5 and fig.data[1].line.color == C.COLOR_LINES[6]
    assert [t.name for t in V.build_curve(series, 5.4).data] == ["g = 2", "g = 6", "volle Information"]                          # ohne LB2


def test_saved_chart_skips_the_first_step_and_shows_the_saved_hubs():
    rows = [{"k": 0, "hubs": 13.0, "saved": None, "share": 0.0}, {"k": 1, "hubs": 12.0, "saved": 1.0, "share": 0.5}, {"k": 2, "hubs": 11.5, "saved": 0.5, "share": 0.75}]
    fig = V.build_saved(rows)
    assert _locked(fig) and list(fig.data[0].x) == ["auf 1", "auf 2"] and list(fig.data[0].y) == [1.0, 0.5] and fig.layout.yaxis.rangemode == "tozero"


def test_tie_chart_is_ordered_and_has_two_bars_per_cell():
    cells = {"4,4,6,2": {"strict": 11.89, "safe": 12.02}, "4,3,4,0": {"strict": 6.5, "safe": 8.21}, "4,4,6,0": {"strict": 13.11, "safe": 14.96}}
    fig = V.build_tie(cells)
    assert _locked(fig) and list(fig.data[0].x) == ["4 × 3, g = 4, k = 0", "4 × 4, g = 6, k = 0", "4 × 4, g = 6, k = 2"]
    assert list(fig.data[0].y) == pytest.approx([6.5, 13.11, 11.89]) and list(fig.data[1].y) == pytest.approx([8.21, 14.96, 12.02]) and [t.name for t in fig.data] == ["Gleichstand = unsicher", "Gleichstand = sicher"]


def test_all_figures_are_plotly_figures():
    assert all(isinstance(f, go.Figure) for f in (V.build_bay(((1,),), 2), V.build_curve([("g", [0, 1], [1.0, 0.5], "#000000")], 0.5), V.build_saved([{"k": 1, "saved": 1.0}])))
