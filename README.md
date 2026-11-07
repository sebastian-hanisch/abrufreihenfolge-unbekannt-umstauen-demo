# Unbekannte Abrufreihenfolge: was ist eine Vorschau wert? – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-abrufreihenfolge-unbekannt-umstauen-demo.streamlit.app/)**

Dreizehntes Stück der Konzepte-Reihe **„Umstauen: Untergrenze und Suche“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Bisher war die **Abrufreihenfolge bekannt**. Hier ist sie nur **gruppenweise** bekannt: Die Nummern werden in **Gruppen** aus je *g* aufeinanderfolgenden Abrufen zusammengefasst, innerhalb einer Gruppe ist die Reihenfolge zufällig. Eine **Vorschau** auf die nächsten *k* Abrufe enthüllt deren genaue Nummern. Wie viele Hübe kostet das **Nichtwissen**, wie schnell **sinkt der Wert** jeder weiteren Information, und wann ist es **egal**? Die Demo rechnet das live über eine Stichprobe von Buchten und misst vorberechnet die Kurve **Hübe gegen Vorschau**. Zur Vorhersage von Algorithmen ohne Stapel siehe auch die Demos zu **Vorhersagen** und **Online-Algorithmen** (nur als Verweis, nicht nachgebaut).

## Warum dieses Problem

In der Praxis kennt man die Abholreihenfolge selten genau: Man weiß, dass ein Container „diese Woche“ oder „im nächsten Zug“ abgeholt wird, nicht in welcher Minute. Die Frage, was **frühe Information** wert ist, lässt sich hier genau messen. Ergebnis: Das Nichtwissen kostet Hübe, aber **wenige und nur kurz**. Bei 4 × 4 Containern und Gruppen aus 6 Nummern braucht die Regel mit reiner Gruppenkenntnis im Mittel 13,11 statt 11,31 Hübe (+16 %); mit der Vorschau auf **zwei** Abrufe 11,89 (68 % der Lücke sind zu), ab **vier** sind es 90 %. Der Grenznutzen sinkt schnell. Bei **vielen Stapeln** ist das Nichtwissen fast egal (8 × 3, Gruppen aus 6: +4 %), wie in Stück 10: Fast jeder Blocker findet einen sicheren Stapel. Und bei **Gleichstand** der Schlüssel ist **Vorsicht** viel besser als Vertrauen (12,27 gegen 14,06 Hübe).

## Modell

**Eigene Konstruktion.** Eine Schranke für die erwartete Umlagerungszahl und eine erwartungswertbasierte Heuristik für unbekannte Abrufreihenfolgen innerhalb von Gruppen untersucht die Literatur (APJOR 2025; aus dem Gedächtnis zugeordnet, **nicht gelesen**); nachgebaut ist sie nicht.

- **Gruppen:** Gruppe *j* = die Nummern (*j* − 1)·*g* + 1 bis *j*·*g* (die letzte kürzer). Bekannt ist die Gruppe jedes Containers; die Zuordnung der Nummern innerhalb der Gruppe ist gleichverteilt zufällig (die zufälligen Buchten enthalten sie ohnehin: Die Regel sieht die wahren Nummern nie, nur die Schlüssel).
- **Vorschau *k*:** Beim Abruf *n* sind die genauen Nummern von *n* bis *n* + *k* bekannt (*k* = 0: nur der aktuelle Abruf). *k* ≥ *N* − 1 und *g* = 1 sind die volle Information.
- **Schlüssel:** Ein nicht enthüllter Container der Gruppe *j* trägt eine der noch freien Nummern der Gruppe (alle größer als *n* + *k*); sein Schlüssel ist deren **Mittelwert** (Erwartungswert, wird beim Fortschreiten aktualisiert). Enthüllte Container haben ihre Nummer als Schlüssel.
- **Regel:** engste Passung (Stück 1) auf den Schlüsseln; ein Stapel ist „sicher“, wenn seine früheste Schlüssel-Nummer **größer** als der Schlüssel des Blockers ist (**Gleichstand zählt als unsicher**); unter den sicheren gewinnt die kleinste, ohne sichere die größte früheste Nummer.
- **Wert der Information:** Anteil der Lücke (Hübe nur mit Gruppen minus Hübe bei voller Information), den die Vorschau schließt.
- **Erwartete Blockerzahl:** Ein Container ist Blocker mit Wahrscheinlichkeit 1, wenn unter ihm ein Container einer früheren Gruppe liegt, sonst mit *m*/(*m* + 1) (*m* = Zahl der Container derselben Gruppe unter ihm).

## Methodik

- **Live:** Die Regel für alle Vorschau-Stufen (0, 1, 2, 3, 4, 6, 8, die gewählte und „alle“) über eine Stichprobe von 20 bis 200 Buchten (Stapel 3 bis 8, Lagen 2 bis 5, Platz 1 bis 4, Gruppengröße 1 bis 12), dazu volle Information, Untergrenzen, erwartete Blocker; das Optimum bis 16 Container (Knotenlimit 100 000 je Bucht).
- **Vorberechnet** (`uas_bands.json`, erzeugt von `generate_precomputed.py`, rund eine Minute in mehreren Prozessen): Kurve in vier Zellen (4 × 3, 4 × 4, 5 × 4, 8 × 3) mit Gruppen 2, 3, 4, 6 (200 Buchten), Gleichstand in vier Zeilen mal zwei Vorschau-Stufen, das Optimum in 4 × 3 und 4 × 4 (100 Buchten). Dieselben festen Buchten wie in Stück 1 bis 11 (Seeds ab 0, Platz 2).
- Alle Kennzahlen sind **Zählungen** (Hübe, Blocker) an festen Seeds; es gibt keine Zeitmessung.
- **Abschnitte der App:** Ergebnis (live, Kurve); eine Bucht von Hand; der Wert der Vorschau (Tabelle, Diagramm, Grenznutzen); Gleichstand; Untergrenze unter Unsicherheit; das Optimum bei voller Information; Grenzen; mathematische Formulierung.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an festen Buchten, nachgerechnet in `tests/test_claims.py`, `tests/test_presets.py` und `tests/test_oracle_abrufreihenfolge_unbekannt_umstauen.py`. Anzeigezahlen sind kaufmännisch gerundet.

**A: Hübe gegen Vorschau *k*** (Mittel der Regel über 200 Buchten; „alle“ = Vorschau auf alle Container)

| Zelle, Gruppengröße | volle Information | *k* = 0 | 1 | 2 | 3 | 4 | 6 | 8 | alle |
|---|---|---|---|---|---|---|---|---|---|
| 4 × 3, *g* = 2 | 6,08 | 6,22 | 6,22 | 6,12 | 6,10 | 6,08 | 6,08 | 6,08 | 6,08 |
| 4 × 3, *g* = 3 | 6,08 | 6,30 | 6,28 | 6,19 | 6,11 | 6,09 | 6,08 | 6,08 | 6,08 |
| 4 × 3, *g* = 4 | 6,08 | 6,51 | 6,39 | 6,23 | 6,15 | 6,10 | 6,08 | 6,08 | 6,08 |
| 4 × 3, *g* = 6 | 6,08 | 6,97 | 6,62 | 6,31 | 6,16 | 6,11 | 6,08 | 6,08 | 6,08 |
| 4 × 4, *g* = 2 | 11,31 | 11,61 | 11,49 | 11,42 | 11,32 | 11,31 | 11,31 | 11,31 | 11,31 |
| 4 × 4, *g* = 3 | 11,31 | 12,04 | 11,84 | 11,64 | 11,42 | 11,35 | 11,32 | 11,31 | 11,31 |
| 4 × 4, *g* = 4 | 11,31 | 12,27 | 11,94 | 11,66 | 11,48 | 11,39 | 11,32 | 11,31 | 11,31 |
| 4 × 4, *g* = 6 | 11,31 | 13,11 | 12,38 | 11,89 | 11,52 | 11,39 | 11,32 | 11,31 | 11,31 |
| 5 × 4, *g* = 2 | 13,20 | 13,41 | 13,41 | 13,35 | 13,29 | 13,24 | 13,21 | 13,20 | 13,20 |
| 5 × 4, *g* = 3 | 13,20 | 13,75 | 13,71 | 13,60 | 13,49 | 13,36 | 13,26 | 13,22 | 13,20 |
| 5 × 4, *g* = 4 | 13,20 | 14,14 | 14,09 | 13,83 | 13,63 | 13,42 | 13,29 | 13,23 | 13,20 |
| 5 × 4, *g* = 6 | 13,20 | 14,97 | 14,63 | 14,09 | 13,83 | 13,57 | 13,32 | 13,24 | 13,20 |
| 8 × 3, *g* = 2 | 10,55 | 10,60 | 10,60 | 10,60 | 10,60 | 10,60 | 10,59 | 10,58 | 10,55 |
| 8 × 3, *g* = 3 | 10,55 | 10,61 | 10,61 | 10,61 | 10,61 | 10,61 | 10,61 | 10,59 | 10,55 |
| 8 × 3, *g* = 4 | 10,55 | 10,78 | 10,78 | 10,78 | 10,78 | 10,77 | 10,72 | 10,66 | 10,55 |
| 8 × 3, *g* = 6 | 10,55 | 10,98 | 10,98 | 10,98 | 10,97 | 10,95 | 10,80 | 10,74 | 10,55 |

Die Hubzahl fällt mit *k* nicht (im Mittel) und erreicht bei *k* = „alle“ die volle Information. Die **Lücke** (*k* = 0 minus volle Information) wächst mit der Gruppengröße: 4 × 4: 0,31 (*g* = 2), 0,73 (3), 0,97 (4), 1,80 (6) Hübe, das sind 2,7 %, 6,5 %, 8,5 % und 16 %. Bei **vielen Stapeln** schrumpft sie: 8 × 3, *g* = 6: 0,43 Hübe (4,1 %), bei *g* = 2 und 3 unter 0,1 (die Reihenfolge ist dort praktisch egal). **Wie schnell sie zugeht:** In 4 × 3 und 4 × 4 sind 90 % der Lücke ab *k* = 3 bis 4 geschlossen, und ab *k* = max(*g*, 4) ist sie bis auf 0,08 Hübe zu (4 × 3, *g* = 6: ab *k* = 6 gleich der vollen Information). Bei **5 × 4** braucht es länger (90 % ab *k* = 6 bis 8; bei *k* = *g* = 6 fehlen noch 0,12 Hübe), bei **8 × 3** (*g* = 6) trägt die Vorschau erst bei sehr großem *k* (50 % der Lücke ab *k* = 8). Mit *k* = 2 sind in 4 × 4 zwischen 54 % (*g* = 3) und 68 % (*g* = 6) der Lücke geschlossen, in 5 × 4 zwischen 27 % und 50 %.

**B: Gleichstand** (Hübe der Regel, Mittel über 200 Buchten; „unsicher“ = bei gleichen Schlüsseln gilt der Stapel nicht als sicher)

| Zelle, Gruppengröße, Vorschau | Gleichstand = unsicher | Gleichstand = sicher | Unterschied |
|---|---|---|---|
| 4 × 3, *g* = 4, *k* = 0 | 6,51 | 8,21 | 21 % weniger |
| 4 × 3, *g* = 4, *k* = 2 | 6,23 | 6,49 | 4,1 % weniger |
| 4 × 4, *g* = 4, *k* = 0 | 12,27 | 14,06 | 13 % weniger |
| 4 × 4, *g* = 4, *k* = 2 | 11,66 | 11,96 | 2,5 % weniger |
| 4 × 4, *g* = 6, *k* = 0 | 13,11 | 14,96 | 12 % weniger |
| 4 × 4, *g* = 6, *k* = 2 | 11,89 | 12,02 | 1,1 % weniger |
| 5 × 4, *g* = 6, *k* = 0 | 14,97 | 18,36 | 18 % weniger |
| 5 × 4, *g* = 6, *k* = 2 | 14,09 | 14,77 | 4,6 % weniger |

Bei Gleichstand ist **Vorsicht** in allen acht Zeilen besser; der Unterschied ist ohne Vorschau groß (12 bis 21 %) und schrumpft mit der Vorschau. Der **Schlüssel** für nicht enthüllte Container (Mittelwert, kleinste oder größte mögliche Nummer der Gruppe) liefert dagegen an jeder gemessenen Bucht **dieselbe** Hubzahl (Test an 120 Buchten in vier Zellen): Nur die Reihenfolge der Schlüssel zählt, und enthüllte Nummern sind kleiner als alle nicht enthüllten.

**C: Untergrenze unter Unsicherheit** (Mittel über 200 Buchten)

| Zelle, Gruppengröße | erwartete Blocker | gezählt an den wahren Nummern | LB2 |
|---|---|---|---|
| 4 × 3, *g* = 2 | 4,61 | 4,64 | 5,48 |
| 4 × 3, *g* = 4 | 4,58 | 4,64 | 5,48 |
| 4 × 3, *g* = 6 | 4,60 | 4,64 | 5,48 |
| 4 × 4, *g* = 2 | 7,66 | 7,67 | 9,01 |
| 4 × 4, *g* = 4 | 7,62 | 7,67 | 9,01 |
| 4 × 4, *g* = 6 | 7,62 | 7,67 | 9,01 |
| 5 × 4, *g* = 2 | 9,50 | 9,49 | 10,68 |
| 5 × 4, *g* = 4 | 9,51 | 9,49 | 10,68 |
| 5 × 4, *g* = 6 | 9,45 | 9,49 | 10,68 |
| 8 × 3, *g* = 2 | 9,25 | 9,26 | 9,95 |
| 8 × 3, *g* = 4 | 9,22 | 9,26 | 9,95 |
| 8 × 3, *g* = 6 | 9,28 | 9,26 | 9,95 |

(Alle 16 Zeilen mit den Gruppengrößen 2, 3, 4 und 6 stehen in der App.) Die erwartete Blockerzahl trifft die Zählung an den wahren Nummern im Mittel auf **höchstens 0,06 Blocker** genau; die Formel ist im Test gegen die **vollständige Aufzählung** aller Zuordnungen innerhalb der Gruppen nachgerechnet (7 Fälle, je 12 Buchten).

**D: Das Optimum bei voller Information** (100 Buchten, Mittel)

| Zelle (Buchten) | Optimum | Regel (volle Information) | Untergrenze LB2 | Regel über Optimum |
|---|---|---|---|---|
| 4 × 3 (100) | 5,81 | 5,92 | 5,35 | 1,9 % |
| 4 × 4 (100) | 10,44 | 11,24 | 8,88 | 7,7 % |

| Frage | Befund |
|---|---|
| **Was kostet das Nichtwissen?** | Wenig: 0,4 % (8 × 3, *g* = 2) bis 16 % (4 × 4, *g* = 6) mehr Hübe als bei voller Information; es wächst mit der Gruppengröße und schrumpft mit der Stapelzahl. |
| **Wie schnell sinkt der Wert der Vorschau?** | Schnell: In 4 × 4 mit *g* = 6 holt der erste enthüllte Abruf 0,73 Hübe (40 % der Lücke), der zweite 0,49, der dritte 0,37, der vierte 0,13; ab *k* = 6 bleibt nichts. In größeren Zellen trägt die Vorschau länger. |
| **Reicht eine Vorschau bis zur Gruppengröße?** | In 4 × 3 und 4 × 4 ja (ab *k* = max(*g*, 4) höchstens 0,08 Hübe Lücke); in 5 × 4 mit *g* = 2 sind 90 % erst ab *k* = 6 geschlossen, bei 8 × 3 erst bei sehr großem *k*. Die Aussage gilt also für kleine Buchten, nicht allgemein. |
| **Wie geht die Regel bei Gleichstand um?** | Vorsichtig: gleich = unsicher spart 12 bis 21 % Hübe ohne Vorschau, 1 bis 5 % mit zwei Abrufen Vorschau. |
| **Trifft die Zählung unter Unsicherheit?** | Ja: die erwartete Blockerzahl liegt höchstens 0,06 neben der Zählung an den wahren Nummern. |
| **Und die Regel selbst?** | Auch bei voller Information liegt sie 1,9 % (4 × 3) und 7,7 % (4 × 4) über dem Optimum (Stück 1): Nichtwissen und Regelfehler addieren sich. |

**Die Bucht von Hand:** (2, 7, 4), (6, 1, 9), (8, 5, 3), Höchsthöhe 5, Gruppen aus 3 Nummern. Die 9 liegt über der 1. Ohne Vorschau sehen Stapel 1 und Stapel 3 gleich aus (früheste mögliche Nummer 2,5, Gleichstand): Die Regel nimmt Stapel 1 und braucht **7** Hübe. Mit **einem** enthüllten Abruf wählt sie Stapel 3 und braucht **5**, das Optimum bei voller Information. Untergrenzen: LB1 3, LB2 4, erwartete Blocker 3.

**Presets** (Eigenschaften in `tests/test_presets.py`, je 100 Buchten): „Zwei Abrufe voraus“ (4 × 4, *g* = 6, *k* = 2: 11,78 Hübe gegen 12,77 nur mit Gruppen und 11,24 bei voller Information), „Nur Gruppen“ (+14 %), „Volle Information“ (*g* = 1, Lücke 0), „Viele Stapel: egal“ (8 × 3, *g* = 6: +4 %), „Kleine Gruppen“ (*g* = 2: +2 %).

**Korrektur gegenüber dem Plan:** Zahlen mit anderer Rundung: In der Vormessung stand 6,50, 14,96 und 11,30, die App rundet kaufmännisch (6,51; 14,97; 11,31). Der Plan sprach von „höchstens 0,05 Blocker“ Abweichung der erwarteten Blockerzahl, gemessen sind 0,06 (4 × 3, *g* = 4: 4,58 gegen 4,64). Die Aussage „Information über die Gruppengröße hinaus ist wertlos“ gilt nur in den kleinen Zellen (siehe oben); bei 5 × 4 und 8 × 3 trägt die Vorschau länger. Der Plan nannte für *k* = 2 in 4 × 4 mit *g* = 6 „68 %“ (gemessen 67,5 %, mit den 100 Buchten der Presets 65 %).

## Ehrliche Grenzen

- **Eine Art von Unsicherheit:** nur die Reihenfolge innerhalb von Gruppen (gleichverteilt). Fehlerhafte Abrufmeldungen, Verspätungen und überlappende Gruppen sind nicht gemessen (Verweis auf die Demos zu Vorhersagen und Online-Algorithmen).
- **Die Regel ist die engste Passung** auf Erwartungsschlüsseln, keine erwartungswertoptimale Strategie; deren Hubzahl ist nicht gerechnet. Verglichen wird mit der Regel bei voller Information und mit dem Optimum bei voller Information (4 × 3, 4 × 4).
- **Schranke der Literatur nicht nachgebaut,** nur die erwartete Blockerzahl.
- **Volle Buchten, restricted, Platz 2** in den Tabellen; kleine Zellen (4 × 3, 4 × 4, 5 × 4, 8 × 3), Gruppen 2, 3, 4, 6; Optimum nur bis 16 Container.
- **Mittel über 200 Buchten:** Unterschiede unter etwa 0,05 Hüben liegen im Rauschen der Stichprobe.

## Verifikation

- **Kern:** Gruppen, Schlüssel (enthüllt, Mittelwert, kleinste und größte mögliche Nummer, kürzere letzte Gruppe), Zielwahl der Regel von Hand (Hand-Bucht: Gleichstand und Entscheidung mit Vorschau), Gleichstand-Variante an einer kleinen Bucht, erwartete Blocker von Hand, Untergrenzen, kein Platz.
- **Orakel:** erwartete Blocker gegen die **vollständige Aufzählung** aller Zuordnungen innerhalb der Gruppen (7 Fälle, je 12 Buchten, bis 720 Zuordnungen je Bucht); die Regel mit Vorschau gegen eine **zweite Umsetzung** (explizite Mengen möglicher Nummern, eigene Zielwahl) in 525 Läufen (7 Einstellungen, 3 Zellen, je 25 Buchten); volle Information gleich der **Regel aus Stück 1** (`child_targets`) in 120 Buchten, bei *g* = 1 und bei Vorschau auf alle Container; die drei Schlüsselvarianten an 120 Buchten gleich; Untergrenzen ≤ Optimum ≤ Regel.
- **Zahlen im README:** jede Zahl der Befunde in `tests/test_claims.py` (gespeicherte Bänder: nicht steigend in *k*, Lücke wächst mit *g* und schrumpft mit den Stapeln); drei Kurvenzellen, eine Gleichstandzeile und das Optimum werden frisch nachgerechnet (Zählungen).
- **Verdikte:** reine Funktionen, jede Schwelle einschließlich Gleichheitsfall (90 %, 50 %, Lücke 0,1, 5 % Ersparnis, 2 % Abweichung) und jede genannte Zahl an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), Inhalt (Kennzahlen, Tabellenzeilen, Hand-Bucht, Grenznutzen), Layout, Footer, Laufzeit-Importe, Abbildungen (Farben, gesperrte Achsen, Kategorieachse).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App (Aufbau nach DEMO-PLAYBOOK §2) |
| `generate_precomputed.py` | erzeugt `uas_bands.json` (Kurve, Gleichstand, Optimum) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt): streamlit, plotly |
| `uas_algorithm.py` | Gruppen, Schlüssel, die Regel mit Vorschau, erwartete Blocker, Untergrenzen und exakte Suche |
| `uas_bands.json` | vorberechnete Kennzahlen der festen Buchten je Zelle |
| `uas_constants.py` | Regler-Stufen, Limits, Zellen, Schwellen, Farben, Presets |
| `uas_evaluation.py` | Stichprobe, Kennzahlen, Verdikte (reine Funktionen) |
| `uas_layout.py` | Fester Kopf (Stylesheet) |
| `uas_presets.py` | Permalink (auf Stufen gerückt), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `uas_scenario.py` | Buchten (volle Buchten) |
| `uas_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handrechnung, Orakel, Randfälle, Behauptungen, Verdikte, Presets, Abbildungen, AppTest, Layout, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Eine erwartungswertoptimale Strategie** und die Schranke der Literatur.
- **Fehlerhafte Vorhersagen** (Verweis auf `vorhersagen-demo`).
- **Teilgefüllte Buchten** und größere Zellen.
- **PDF-Export:** nicht vorgesehen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

104 Tests, rund eine Minute.

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
