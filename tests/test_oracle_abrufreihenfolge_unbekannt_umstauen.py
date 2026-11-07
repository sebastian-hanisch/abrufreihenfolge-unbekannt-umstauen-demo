"""Orakel-Test abrufreihenfolge-unbekannt-umstauen-demo (ORACLE-PLAYBOOK, DEMO-PLAYBOOK §12): erwartete Blocker und Regel gegen ANDERE Rechenwege.

Eigene, unabhängige Umsetzungen im Test: (a) die erwartete Blockerzahl durch **Mitteln über alle** Zuordnungen der Nummern innerhalb der Gruppen (vollständige Aufzählung), (b) die Regel mit
Vorschau über explizite Mengen möglicher Nummern (statistics.mean statt Bereichsformel) und eigener Zielwahl über sortierte Kandidaten, (c) die Regel mit voller Information gegen die Regel aus
Stück 1 (child_targets), (d) das Optimum aus der Suche. Vorher an den Handzahlen geprüft: Hand-Bucht k = 0: 7 Hübe, k = 1: 5 Hübe, erwartete Blocker 3,0."""

import itertools
import statistics

import pytest

import uas_algorithm as A
import uas_evaluation as ev
from uas_scenario import make_bay

INF = 10 ** 9


def all_assignments(bay, g):
    """Alle Bayen, die dieselben Gruppen pro Position haben und deren Nummern innerhalb jeder Gruppe beliebig vertauscht sind (vollständige Aufzählung)."""
    n = sum(len(s) for s in bay)
    groups = {}
    for gi in range(1, (n - 1) // g + 2):
        groups[gi] = [m for m in range((gi - 1) * g + 1, min(gi * g, n) + 1)]
    pos_by_group = {gi: [] for gi in groups}
    for si, s in enumerate(bay):
        for pi, c in enumerate(s):
            pos_by_group[(c - 1) // g + 1].append((si, pi))
    keys = list(groups)
    for perms in itertools.product(*[itertools.permutations(groups[gi]) for gi in keys]):
        new = [list(s) for s in bay]
        for gi, perm in zip(keys, perms):
            for (si, pi), val in zip(pos_by_group[gi], perm):
                new[si][pi] = val
        yield tuple(tuple(s) for s in new)


def true_blockers(bay):
    n = 0
    for s in bay:
        for i, c in enumerate(s):
            if any(x < c for x in s[:i]):
                n += 1
    return n


def ref_simulate(bay, height, g, k, tie_safe=False):
    """Regel mit Vorschau über explizite Mengen möglicher Nummern."""
    st = [list(s) for s in bay]
    total = sum(len(s) for s in st)
    hubs = 0
    for n in range(1, total + 1):
        def key(c):
            if c <= n + k:
                return c
            group = [m for m in range((c - 1) // g * g + 1, min((c - 1) // g * g + g, total) + 1) if m > n + k]
            return statistics.mean(group)
        src = next(i for i, s in enumerate(st) if n in s)
        while st[src][-1] != n:
            c = st[src].pop()
            kc = key(c)
            opts = []
            for j, t in enumerate(st):
                if j == src or len(t) >= height:
                    continue
                m = min([key(x) for x in t], default=INF)
                safe = (m >= kc) if tie_safe else (m > kc)
                opts.append(((0, m, j) if safe else (1, -m, j), j))
            st[sorted(opts)[0][1]].append(c)
            hubs += 1
        st[src].pop()
    return hubs


def ref_greedy(bay, height):
    """Regel aus Stück 1 über child_targets (Kern der Stücke davor)."""
    st, _ = A.autopop(bay)
    cost = 0
    while any(st):
        _, i = A.target_stack(st)
        lst = [list(s) for s in st]
        c = lst[i].pop()
        base = tuple(tuple(s) for s in lst)
        lst[A.child_targets(base, i, height, c)[0]].append(c)
        st = A.autopop(tuple(tuple(s) for s in lst))[0]
        cost += 1
    return cost


@pytest.mark.parametrize("stacks,layers,g", [(3, 2, 2), (2, 3, 3), (3, 2, 3), (2, 3, 2), (3, 2, 6), (2, 2, 2), (3, 2, 1)])
def test_expected_blockers_equals_the_mean_over_all_assignments_within_the_groups(stacks, layers, g):
    for sd in range(12):
        bay = make_bay(stacks, layers, sd)
        every = list(all_assignments(bay, g))
        assert bay in every
        assert A.expected_blockers(bay, g) == pytest.approx(statistics.mean(true_blockers(b) for b in every)), (stacks, layers, g, sd)


def test_the_enumeration_has_the_right_size():
    bay = make_bay(3, 2, 0)
    assert len(list(all_assignments(bay, 2))) == 8 and len(list(all_assignments(bay, 3))) == 36 and len(list(all_assignments(bay, 1))) == 1 and len(list(all_assignments(bay, 6))) == 720


@pytest.mark.parametrize("g,k,tie", [(2, 0, False), (3, 1, False), (4, 2, False), (6, 0, True), (4, 3, True), (3, 0, False), (6, 4, False)])
def test_the_rule_equals_an_independent_implementation(g, k, tie):
    for stacks, layers in ((4, 3), (3, 4), (5, 2)):
        for sd in range(25):
            bay = make_bay(stacks, layers, sd)
            assert A.simulate(bay, layers + 2, g, k, tie_safe=tie) == ref_simulate(bay, layers + 2, g, k, tie), (stacks, layers, sd)


def test_full_information_is_the_rule_of_stueck_1():
    for stacks, layers in ((3, 3), (4, 3), (4, 4), (6, 3)):
        for sd in range(30):
            bay = make_bay(stacks, layers, sd)
            h = layers + 2
            r = ref_greedy(bay, h)
            assert A.simulate(bay, h, 1, 0) == r                                                       # g = 1: jede Nummer ist eine Gruppe
            for g in (2, 3, 6):
                assert A.simulate(bay, h, g, stacks * layers) == r                                    # Vorschau auf alle Container: ebenfalls volle Information


def test_the_key_variants_give_the_same_hubs():
    """Phase-0-Befund im Test: Mittelwert, kleinste und größte mögliche Nummer als Schlüssel liefern an jeder Bucht dieselbe Hubzahl (nur die Reihenfolge der Schlüssel zählt)."""
    for stacks, layers, g, k in ((4, 3, 4, 0), (4, 4, 6, 2), (5, 3, 3, 1), (3, 4, 2, 0)):
        for sd in range(30):
            bay = make_bay(stacks, layers, sd)
            h = layers + 2
            base = A.simulate(bay, h, g, k, "mean")
            assert A.simulate(bay, h, g, k, "min") == base == A.simulate(bay, h, g, k, "max"), (stacks, layers, g, k, sd)


def test_the_order_of_the_bounds_the_optimum_and_the_rule():
    for sd in range(40):
        for stacks, layers in ((3, 3), (4, 3)):
            bay = make_bay(stacks, layers, sd)
            h = layers + 2
            st = A.autopop(bay)[0]
            opt = A.search(bay, h).optimum
            assert A.lb1(st) <= A.lb2(st) <= opt <= A.simulate(bay, h, 1, 0)
            assert opt <= A.simulate(bay, h, 6, 0)                                                      # jede Regel liegt über dem Optimum, auch die mit Gruppenwissen


def test_bay_rows_use_the_same_numbers_as_the_pieces():
    rows = ev.bay_rows(4, 3, 2, 4, [0, 2, 12], range(10))
    for r in rows:
        bay = make_bay(4, 3, r["seed"])
        assert r["hubs"] == [ref_simulate(bay, 5, 4, k) for k in (0, 2, 12)] and r["full"] == ref_greedy(bay, 5)
        assert r["lb1"] == true_blockers(bay) and r["eb"] == pytest.approx(A.expected_blockers(bay, 4))
