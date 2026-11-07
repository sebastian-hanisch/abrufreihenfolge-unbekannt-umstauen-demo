"""Kennzahlen, Verdikt-Logik, vorberechnete Tabellen. Reine Funktionen: die App ruft st.<Art>(Text), die Tests prüfen jede Zahl und jede Schwelle."""

import json
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from statistics import mean

import uas_algorithm as A
import uas_constants as C
from uas_scenario import make_bay, max_height

BANDS_FILE = Path(__file__).resolve().parent / "uas_bands.json"


@dataclass(frozen=True)
class Settings:
    stacks: int = C.DEFAULT_STACKS
    layers: int = C.DEFAULT_LAYERS
    extra: int = C.DEFAULT_EXTRA
    group: int = C.DEFAULT_GROUP
    lookahead: int = C.DEFAULT_LOOKAHEAD
    bays: int = C.DEFAULT_BAYS
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    stats: dict             # curve_stats der Stichprobe
    exact: bool             # wurde das Optimum gerechnet?
    first_bay: tuple
    height: int
    containers: int


def effective_ks(total: int, extra_k: int = 0) -> list:
    """Vorschau-Stufen einer Kurve für `total` Container: CURVE_KS, die gewählte Stufe und „alle“ (= total); Werte über total werden auf total begrenzt."""
    ks = {min(k, total) for k in C.CURVE_KS} | {min(extra_k, total), total}
    return sorted(ks)


def bay_rows(stacks: int, layers: int, extra: int, group: int, ks, seeds, exact: bool = False, cap: int = C.EXACT_CAP) -> list[dict]:
    """Je Bucht: LB1 und LB2 an den wahren Nummern, erwartete Blockerzahl bei Gruppengröße `group`, Hubzahl der Regel bei voller Information und für jede Vorschau k in `ks`, das Optimum
    (nur wenn verlangt; None am Knotenlimit)."""
    height = max_height(layers, extra)
    rows = []
    for sd in seeds:
        bay = make_bay(stacks, layers, sd)
        st = A.autopop(bay)[0]
        row = {"seed": sd, "lb1": A.lb1(st), "lb2": A.lb2(st), "eb": A.expected_blockers(bay, group), "full": A.simulate(bay, height, 1, 0),
               "hubs": [A.simulate(bay, height, group, k) for k in ks], "opt": None}
        if exact:
            row["opt"] = A.search(bay, height, cap).optimum
        rows.append(row)
    return rows


def curve_stats(rows: list[dict], ks) -> dict:
    """Mittel über die Buchten: LB1, LB2, erwartete Blocker, volle Information, Hubzahl je Vorschau k (Listen `ks` und `hubs` gleich lang), Optimum (falls gerechnet)."""
    out = {"n": len(rows), "lb1": mean(r["lb1"] for r in rows), "lb2": mean(r["lb2"] for r in rows), "eb": mean(r["eb"] for r in rows), "full": mean(r["full"] for r in rows),
           "ks": list(ks), "hubs": [mean(r["hubs"][i] for r in rows) for i in range(len(ks))]}
    solved = [r for r in rows if r["opt"] is not None]
    if solved:
        out["opt"] = {"n": len(solved), "opt": mean(r["opt"] for r in solved), "full": mean(r["full"] for r in solved), "lb2": mean(r["lb2"] for r in solved)}
    return out


def analyse(settings: Settings) -> Analysis:
    total = settings.stacks * settings.layers
    ks = effective_ks(total, settings.lookahead)
    exact = total <= C.EXACT_MAX_CONTAINERS
    rows = bay_rows(settings.stacks, settings.layers, settings.extra, settings.group, ks, range(settings.seed, settings.seed + settings.bays), exact)
    return Analysis(curve_stats(rows, ks), exact, make_bay(settings.stacks, settings.layers, settings.seed), max_height(settings.layers, settings.extra), total)


def hub_at(stats: dict, k: int) -> float:
    """Mittlere Hubzahl bei Vorschau k (k wird auf die Zahl der Container begrenzt); KeyError, wenn die Stufe nicht gerechnet wurde."""
    total_k = stats["ks"][-1]
    return stats["hubs"][stats["ks"].index(min(k, total_k))]


# ---------------------------------------------------------------- Formate

def num(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ")


def _half_up(x: float, digits: int) -> str:
    """Kaufmännisch gerundet (…5 rundet auf) mit `digits` Nachkommastellen (vermeidet die Binärdarstellung: 1,635 als 1,63)."""
    d = Decimal(repr(round(float(x), 9))).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return f"{d:.{digits}f}"


def dec(x: float, digits: int = 2) -> str:
    """Dezimalzahl mit Komma und Leerzeichen als Tausendertrenner; ganzzahlige Werte ohne Nachkommastellen."""
    x = round(float(x), 6)
    if x.is_integer():
        return num(int(x))
    whole, frac = _half_up(x, digits).split(".")
    return f"{num(int(whole))},{frac}"


def percent_text(x: float) -> str:
    """Anteil als Prozent: unter 10 % mit einer Nachkommastelle, sonst ganzzahlig (Komma)."""
    p = x * 100
    return (_half_up(p, 1) if p < 10 else _half_up(p, 0)).replace(".", ",") + " %"


def _le(x: float, limit: float) -> bool:
    """x <= limit mit Toleranz für Gleitkommarauschen."""
    return round(x, 9) <= limit


def _ge(x: float, limit: float) -> bool:
    """x >= limit mit Toleranz für Gleitkommarauschen."""
    return round(x, 9) >= limit


# ---------------------------------------------------------------- Kennzahlen der Information

def gap(stats: dict) -> float:
    """Lücke zur vollen Information: Hubzahl nur mit Gruppen (k = 0) minus Hubzahl bei voller Information (Mittel)."""
    return hub_at(stats, 0) - stats["full"]


def share_closed(stats: dict, k: int):
    """Anteil der Lücke (k = 0 gegen volle Information), den die Vorschau k schließt; None, wenn die Lücke unter NEGLIGIBLE_GAP liegt."""
    g = gap(stats)
    if round(g, 9) < C.NEGLIGIBLE_GAP:
        return None
    return (hub_at(stats, 0) - hub_at(stats, k)) / g


def k_share(stats: dict, share: float):
    """Kleinste gerechnete Vorschau, die mindestens den Anteil `share` der Lücke schließt; None, wenn keine."""
    for k in stats["ks"]:
        s = share_closed(stats, k)
        if s is not None and _ge(s, share):
            return k
    return None


def marginal_rows(stats: dict) -> list[dict]:
    """Je gerechneter Vorschau-Stufe: Hubzahl, in dieser Stufe gesparte Hübe gegenüber der vorigen, geschlossener Anteil der Lücke (None, wenn keine Lücke)."""
    rows = []
    prev = None
    for k, h in zip(stats["ks"], stats["hubs"]):
        rows.append({"k": k, "hubs": h, "saved": None if prev is None else prev - h, "share": share_closed(stats, k)})
        prev = h
    return rows


# ---------------------------------------------------------------- Verdikte

def verdict_info(stats: dict, k: int, name: str) -> tuple[str, str]:
    """Verdikt der Kernfrage: wie viel der Lücke zur vollen Information schließt die Vorschau k?"""
    h0, hk, full = hub_at(stats, 0), hub_at(stats, k), stats["full"]
    s = share_closed(stats, k)
    if s is None:
        return "info", f"{name}: Die Reihenfolge ist hier fast egal: Nur mit den Gruppen kostet die Regel {dec(h0)} Hübe, bei voller Information {dec(full)}."
    text = (f"{name}: Nur mit den Gruppen kostet die Regel {dec(h0)} Hübe, bei voller Information {dec(full)} ({percent_text(h0 / full - 1)} mehr); mit Vorschau auf {k} Abrufe {dec(hk)} Hübe: "
            f"{percent_text(s)} der Lücke sind geschlossen.")
    if _ge(s, C.SHARE_ALMOST):
        return "success", text + " Damit ist fast die ganze Lücke zu."
    if _ge(s, C.SHARE_HALF):
        return "info", text + " Damit ist etwa die Hälfte der Lücke oder mehr zu."
    return "warning", text + " Damit ist erst weniger als die Hälfte der Lücke zu."


def verdict_curve(stats: dict, group: int, name: str) -> tuple[str, str]:
    """Verdikt „ab welcher Vorschau ist die Lücke zu?“: kleinste Vorschau mit 90 % der Lücke gegen die Gruppengröße."""
    if share_closed(stats, 0) is None:
        return "info", f"{name}: Die Lücke zur vollen Information ist kleiner als {dec(C.NEGLIGIBLE_GAP)} Hübe; die Vorschau bringt hier nichts mehr."
    k90 = k_share(stats, C.SHARE_ALMOST)
    if k90 is None:
        return "warning", f"{name}: Auch mit der größten gerechneten Vorschau sind weniger als {percent_text(C.SHARE_ALMOST)} der Lücke zu."
    text = f"{name}: Ab einer Vorschau auf {k90} Abrufe sind {percent_text(C.SHARE_ALMOST)} der Lücke geschlossen (Gruppengröße {group})."
    if k90 <= group:
        return "success", text + " Eine Vorschau bis zur Gruppengröße genügt."
    return "warning", text + " Das ist mehr als die Gruppengröße."


def verdict_tie(strict: float, safe: float, name: str) -> tuple[str, str]:
    """Verdikt „Gleichstand“: Hubzahl bei Gleichstand = unsicher (strict) gegen Gleichstand = sicher (safe)."""
    gain = (safe - strict) / safe if safe else 0.0
    text = f"{name}: Wenn Gleichstand als unsicher gilt, kostet die Regel {dec(strict)} Hübe, wenn er als sicher gilt {dec(safe)} ({percent_text(abs(gain))} {'weniger' if gain >= 0 else 'mehr'})."
    if _ge(gain, C.TIE_GAIN):
        return "success", text + " Vorsicht bei Gleichstand lohnt."
    if _le(gain, -C.TIE_GAIN):
        return "warning", text + " Hier ist Vertrauen bei Gleichstand besser."
    return "info", text + " Der Unterschied ist klein."


def verdict_expect(stats: dict, group: int, name: str) -> tuple[str, str]:
    """Verdikt „Untergrenze unter Unsicherheit“: erwartete Blockerzahl (nur Gruppen bekannt) gegen die wahre Zählung."""
    lb1, eb = stats["lb1"], stats["eb"]
    if not lb1:
        return "info", f"{name}: Keine Blocker an den wahren Nummern; die erwartete Zahl ist {dec(eb)}."
    rel = abs(eb - lb1) / lb1
    text = f"{name}: Erwartete Blocker bei Gruppengröße {group}: {dec(eb)}, gezählt an den wahren Nummern: {dec(lb1)} (Abweichung {percent_text(rel)})."
    if _le(rel, C.EXPECT_TOL):
        return "success", text + " Die erwartete Zahl trifft die Zählung."
    return "info", text + " Die Stichprobe weicht vom Erwartungswert ab."


# ---------------------------------------------------------------- Bucht von Hand

def hand_decision(k: int) -> dict:
    """Die erste Entscheidung der Hand-Bucht bei Vorschau k: Blocker, sein Schlüssel, die Kandidaten (Stapel, Inhalt, früheste Schlüssel-Nummer, sicher?), der gewählte Stapel, dazu die
    Hubzahl der ganzen Bucht und das Optimum bei voller Information."""
    bay, height, g = C.HAND_BAY, C.HAND_HEIGHT, C.HAND_GROUP
    st = [list(s) for s in bay]
    total = sum(len(s) for s in st)
    src = next(i for i, s in enumerate(st) if 1 in s)
    c = st[src].pop()
    cands, dest = A.choose_destination(st, src, c, 1, k, g, total, height)
    return {"blocker": c, "key": A.key_of(c, 1, k, g, total), "source": src, "candidates": [{**x, "content": tuple(st[x["stack"]])} for x in cands], "dest": dest,
            "hubs": A.simulate(bay, height, g, k), "optimum": A.search(bay, height).optimum}


# ---------------------------------------------------------------- vorberechnete Tabellen

def curve_key(stacks: int, layers: int, group: int) -> str:
    return f"{stacks},{layers},{group}"


def tie_key(stacks: int, layers: int, group: int, k: int) -> str:
    return f"{stacks},{layers},{group},{k}"


def tie_stats(stacks: int, layers: int, group: int, k: int, seeds=range(C.CURVE_BAYS)) -> dict:
    """Mittlere Hubzahl bei Gleichstand = unsicher und = sicher."""
    height = max_height(layers, C.DEFAULT_EXTRA)
    bays = [make_bay(stacks, layers, sd) for sd in seeds]
    return {"n": len(bays), "strict": mean(A.simulate(b, height, group, k) for b in bays), "safe": mean(A.simulate(b, height, group, k, tie_safe=True) for b in bays)}


def load_bands() -> dict:
    """Vorberechnete Kennzahlen, erzeugt von generate_precomputed.py: {"kurve": {"s,l,g": curve_stats}, "gleichstand": {"s,l,g,k": tie_stats}, "exakt": {"s,l": curve_stats mit "opt"}}."""
    return json.loads(BANDS_FILE.read_text(encoding="utf-8"))
