"""Kern: Relocation (restricted) bei nur gruppenweise bekannter Abrufreihenfolge. Untergrenzen und exakte Suche aus Stück 5 bis 9 (verschlankt), dazu die Regel mit Vorschau.

Eine Bucht besteht aus Stapeln (Tupel von unten nach oben) mit den Abrufnummern 1 bis N (die wahre Reihenfolge). Gruppe j = die Nummern (j-1)g+1 bis jg (letzte Gruppe kürzer). Bekannt
ist, zu welcher Gruppe ein Container gehört; die Reihenfolge innerhalb der Gruppe ist zufällig. Beim Abruf n kennt die Regel die genauen Nummern von n bis n + k (Vorschau k).

  group_of      Gruppe einer Nummer.
  key_of        Schlüssel eines Containers: enthüllt (Nummer <= n + k) seine Nummer, sonst der Mittelwert (oder kleinste/größte) der noch möglichen Nummern seiner Gruppe.
  simulate      die Regel „engste Passung“ (Stück 1) auf den Schlüsseln; Hubzahl bei vollständigem Abruf. Gleichstand der Schlüssel zählt als unsicher (tie_safe=False).
  expected_blockers   erwartete Blockerzahl, wenn nur die Gruppen bekannt sind und die Reihenfolge innerhalb der Gruppen gleichverteilt zufällig ist.
  lb1, lb2      Untergrenzen an den wahren Nummern (Stück 2 und 9).
  search        exakte Suche (IDA* mit Zustandsmerken, Stück 5, 6 und 9): Optimum bei voller Information.
"""

from dataclasses import dataclass

INF = 10 ** 9
MODES = ("mean", "min", "max")


def autopop(stacks):
    """Ruft ab, was oben liegt und gerade dran ist. Gibt (neue Stapel, abgerufene Nummern in Reihenfolge) zurück."""
    st = [list(s) for s in stacks]
    popped = []
    while True:
        present = [c for s in st for c in s]
        if not present:
            return tuple(tuple(s) for s in st), popped
        t = min(present)
        for s in st:
            if s and s[-1] == t:
                s.pop()
                popped.append(t)
                break
        else:
            return tuple(tuple(s) for s in st), popped


def stack_blockers(stack):
    """Container in einem Stapel (unten nach oben), die über einem früher abzurufenden liegen."""
    total, lowest = 0, INF
    for c in stack:
        if c > lowest:
            total += 1
        else:
            lowest = c
    return total


def lb1(stacks):
    """Zahl der blockierenden Container an den wahren Nummern (Untergrenze der Hubzahl, Stück 2)."""
    return sum(stack_blockers(s) for s in stacks)


def target_stack(stacks):
    """(nächste Abrufnummer, Index ihres Stapels). Die Bucht darf nicht leer sein."""
    t = min(c for s in stacks for c in s)
    for i, s in enumerate(stacks):
        if t in s:
            return t, i


def canon(stacks):
    """Kanonische Form: die Stapel sortiert."""
    return tuple(sorted(stacks))


def stack_min(stack):
    """Früheste Abrufnummer im Stapel; leer = unendlich."""
    return min(stack) if stack else INF


def lb2(stacks):
    """lb1 plus die Zahl der Container über dem Ziel, die größer sind als die früheste Nummer jedes anderen Stapels (Stück 9)."""
    if not any(stacks):
        return 0
    t, i = target_stack(stacks)
    s = stacks[i]
    above = s[s.index(t) + 1:]
    others = [stack_min(x) for k, x in enumerate(stacks) if k != i]
    top = max(others) if others else -1
    return lb1(stacks) + sum(1 for c in above if c > top)


def _fit_key(stacks, j, c):
    m = stack_min(stacks[j])
    return (0, m) if m > c else (1, -m)


def child_targets(stacks, src, height, c):
    """Zielstapel für den Blocker c in der Reihenfolge der engsten Passung (Stück 1); nur Stapel mit Platz."""
    dests = [j for j in range(len(stacks)) if j != src and len(stacks[j]) < height]
    dests.sort(key=lambda j: (_fit_key(stacks, j, c), j))
    return dests


@dataclass(frozen=True)
class SearchResult:
    optimum: int | None     # None, wenn das Knotenlimit erreicht wurde
    nodes: int
    capped: bool


class _CapReached(Exception):
    pass


class _Found(Exception):
    pass


def search(stacks, height, cap=1_000_000) -> SearchResult:
    """IDA* mit lb2 und Zustandsmerken (kanonisch), engste Passung zuerst: Optimum bei voller Information."""
    start = tuple(tuple(s) for s in stacks)
    budget = lb2(autopop(start)[0])
    total = 0
    while True:
        b = budget
        nodes = [0]
        table = {}
        found = []

        def rec(state, g):
            nodes[0] += 1
            if total + nodes[0] > cap:
                raise _CapReached
            st, _ = autopop(state)
            if not any(st):
                found.append(g)
                raise _Found
            if g + lb2(st) > b:
                return
            key = canon(st)
            if table.get(key, INF) <= g:
                return
            table[key] = g
            _, i = target_stack(st)
            lst = [list(s) for s in st]
            c = lst[i].pop()
            base = tuple(tuple(s) for s in lst)
            for j in child_targets(base, i, height, c):
                nxt = [list(s) for s in lst]
                nxt[j].append(c)
                rec(tuple(tuple(s) for s in nxt), g + 1)

        try:
            rec(start, 0)
        except _Found:
            pass
        except _CapReached:
            return SearchResult(None, cap, True)
        total += nodes[0]
        if found:
            return SearchResult(found[0], total, False)
        budget += 1


# ---------------------------------------------------------------- unbekannte Reihenfolge

def group_of(n: int, g: int) -> int:
    """Gruppe der Nummer n bei Gruppengröße g (Gruppe 1 = Nummern 1 bis g)."""
    return (n - 1) // g + 1


def key_of(c: int, n: int, k: int, g: int, total: int, mode: str = "mean") -> float:
    """Schlüssel eines Containers mit wahrer Nummer c beim aktuellen Abruf n und Vorschau k (Gesamtzahl der Container total).
    Enthüllt (c <= n + k): die Nummer selbst. Sonst bilden die noch möglichen Nummern der Gruppe (größer als n + k) einen Bereich lo..hi; der Schlüssel ist dessen Mittelwert
    (mode "mean", Erwartungswert), der Anfang ("min") oder das Ende ("max")."""
    if c <= n + k:
        return float(c)
    j = group_of(c, g)
    lo, hi = max((j - 1) * g + 1, n + k + 1), min(j * g, total)
    if mode == "min":
        return float(lo)
    if mode == "max":
        return float(hi)
    return (lo + hi) / 2.0


def choose_destination(st, src, c, n, k, g, total, height, mode="mean", tie_safe=False):
    """Zielstapel für den Blocker c (schon vom Stapel src genommen): Liste der Kandidaten mit (Stapel, früheste Schlüssel-Nummer, sicher?) und der gewählte Stapel.
    Sicher ist ein Stapel, dessen früheste Schlüssel-Nummer später liegt als der Schlüssel von c (bei Gleichstand: unsicher, mit tie_safe sicher); unter den sicheren gewinnt die
    kleinste früheste Nummer (engste Passung), ohne sicheren die größte; bei Gleichstand der kleinste Index. Gibt (Kandidaten, gewählter Index) zurück oder (Kandidaten, None)."""
    kc = key_of(c, n, k, g, total, mode)
    cands, best = [], None
    for j, t in enumerate(st):
        if j == src or len(t) >= height:
            continue
        m = min((key_of(x, n, k, g, total, mode) for x in t), default=float(INF))
        safe = (m >= kc) if tie_safe else (m > kc)
        cands.append({"stack": j, "min_key": m, "safe": safe})
        cand = (0, m, j) if safe else (1, -m, j)
        if best is None or cand < best[0]:
            best = (cand, j)
    return cands, (None if best is None else best[1])


def simulate(bay, height, g: int, k: int, mode: str = "mean", tie_safe: bool = False) -> int:
    """Hubzahl der Regel „engste Passung“ auf den Schlüsseln bei Gruppengröße g und Vorschau k, an der wahren Abrufreihenfolge 1..N (restricted, Stück 1).
    Ein Blocker kommt auf den Stapel, den `choose_destination` wählt. Wirft ValueError, wenn ein Blocker nirgends Platz findet."""
    st = [list(s) for s in bay]
    total = sum(len(s) for s in st)
    hubs = 0
    for n in range(1, total + 1):
        src = next(i for i, s in enumerate(st) if n in s)
        while st[src][-1] != n:
            c = st[src].pop()
            _, dest = choose_destination(st, src, c, n, k, g, total, height, mode, tie_safe)
            if dest is None:
                raise ValueError("kein Stapel mit Platz")
            st[dest].append(c)
            hubs += 1
        st[src].pop()
    return hubs


def expected_blockers(bay, g: int) -> float:
    """Erwartete Blockerzahl bei nur gruppenweise bekannter Reihenfolge (innerhalb der Gruppen gleichverteilt zufällig): Ein Container ist Blocker mit Wahrscheinlichkeit 1, wenn unter ihm
    ein Container einer früheren Gruppe liegt, sonst mit Wahrscheinlichkeit m / (m + 1), wobei m die Zahl der Container derselben Gruppe unter ihm ist."""
    tot = 0.0
    for s in bay:
        for i, c in enumerate(s):
            gc = group_of(c, g)
            below = s[:i]
            if any(group_of(x, g) < gc for x in below):
                tot += 1.0
            else:
                m = sum(1 for x in below if group_of(x, g) == gc)
                tot += m / (m + 1)
    return tot
