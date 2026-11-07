"""Erzeugt uas_bands.json: Kennzahlen der festen Buchten (Seeds ab 0, Platz 2) für drei Auswertungen.

    python generate_precomputed.py

"kurve":       je Zelle (CURVE_CELLS) und Gruppengröße (CURVE_GROUPS) Hubzahl der Regel gegen die Vorschau k (CURVE_KS und „alle“), dazu volle Information, LB1, LB2 und die erwartete
               Blockerzahl (CURVE_BAYS Buchten).
"gleichstand": je Zelle aus TIE_CELLS und Vorschau aus TIE_KS die Hubzahl bei Gleichstand = unsicher gegen = sicher.
"exakt":       je Zelle aus EXACT_CELLS (EXACT_BAYS Buchten) das Optimum bei voller Information gegen die Regel und LB2 (Gruppengröße 6, Kurve wie oben).

Rechenzeit unter fünf Minuten (die Zellen laufen in getrennten Prozessen). Dieselben Funktionen wie die Tests (`uas_evaluation.bay_rows`, `curve_stats`, `tie_stats`); die Datei speichert nur
Kennzahlen, keine Zeilen."""

import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import uas_constants as C
import uas_evaluation as ev

sys.stdout.reconfigure(encoding="utf-8")


def job(kind, stacks, layers, group, k):
    total = stacks * layers
    if kind == "kurve":
        ks = ev.effective_ks(total)
        return kind, ev.curve_key(stacks, layers, group), ev.curve_stats(ev.bay_rows(stacks, layers, C.DEFAULT_EXTRA, group, ks, range(C.CURVE_BAYS)), ks)
    if kind == "gleichstand":
        return kind, ev.tie_key(stacks, layers, group, k), ev.tie_stats(stacks, layers, group, k)
    ks = ev.effective_ks(total)
    return "exakt", f"{stacks},{layers}", ev.curve_stats(ev.bay_rows(stacks, layers, C.DEFAULT_EXTRA, 6, ks, range(C.EXACT_BAYS), True, 400_000), ks)


def main():
    tasks = [("kurve", s, l, g, 0) for s, l in reversed(C.CURVE_CELLS) for g in C.CURVE_GROUPS]
    tasks += [("gleichstand", s, l, g, k) for s, l, g in C.TIE_CELLS for k in C.TIE_KS]
    tasks += [("exakt", s, l, 6, 0) for s, l in C.EXACT_CELLS]
    out = {"kurve": {}, "gleichstand": {}, "exakt": {}}
    with ProcessPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) - 2)) as pool:
        futures = {pool.submit(job, *t): t for t in tasks}
        for fut in as_completed(futures):
            kind, key, stats = fut.result()
            out[kind][key] = stats
            print(kind, key, "fertig", flush=True)
    with open("uas_bands.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("geschrieben: uas_bands.json", flush=True)


if __name__ == "__main__":
    main()
