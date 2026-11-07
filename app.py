"""Unbekannte Abrufreihenfolge: was ist eine Vorschau wert? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 13 der Reihe „Umstauen: Untergrenze und Suche“. Bisher war die Abrufreihenfolge bekannt. Hier ist sie nur gruppenweise bekannt (innerhalb einer Gruppe zufällig); eine Vorschau auf
die nächsten Abrufe enthüllt die genauen Nummern. Die Demo rechnet live, wie viele Hübe die Regel „engste Passung“ mit wie viel Vorschau braucht, und misst vorberechnet, wie schnell der
Wert der Information sinkt.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import uas_constants as C
from uas_evaluation import (
    Settings,
    analyse,
    curve_key,
    dec,
    hand_decision,
    hub_at,
    load_bands,
    marginal_rows,
    num,
    percent_text,
    tie_key,
    verdict_curve,
    verdict_expect,
    verdict_info,
    verdict_tie,
)
from uas_layout import dunkles_design, kopf_css
from uas_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from uas_visualization import build_bay, build_curve, build_saved, build_tie

st.set_page_config(page_title="Unbekannte Reihenfolge – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _bands():
    return load_bands()


@st.cache_data(show_spinner=False)
def _hand(k):
    return hand_decision(k)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in uas_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔮 Unbekannte Reihenfolge: was ist eine Vorschau wert?")
st.markdown(
    """
Bisher war die **Abrufreihenfolge bekannt**. Hier ist sie nur **gruppenweise** bekannt: Die Nummern werden in **Gruppen** aus je *g* aufeinanderfolgenden Abrufen zusammengefasst, innerhalb einer Gruppe ist die Reihenfolge zufällig. Eine **Vorschau** auf die nächsten *k* Abrufe enthüllt deren genaue Nummern. Wie viele Hübe kostet das **Nichtwissen**, wie schnell **sinkt der Wert** jeder weiteren Information, und wann ist es **egal**? Die Demo **rechnet das live** über eine Stichprobe von Buchten und misst vorberechnet die Kurve **Hübe gegen Vorschau**.

Weiter unten: die Abschnitte **🔬 Experiment** (eine Bucht von Hand, der Wert der Vorschau, Gleichstand, Untergrenze unter Unsicherheit, das Optimum), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Dies ist das dreizehnte Stück der Reihe „Umstauen: Untergrenze und Suche“. Zur Vorhersage-Seite von Algorithmen siehe auch die Demos zu **Vorhersagen** und **Online-Algorithmen** (dort ohne Stapel).
"""
)

with st.expander("So wird gemessen", expanded=True):
    st.markdown(
        """
1. **Bucht:** volle Buchten wie in den Stücken davor (*Stapel* × *Lagen*, Platz 2), die Abrufnummern 1 bis *N* zufällig verteilt; die Nummern sind die **wahre** Reihenfolge.
2. **Gruppen:** Gruppe *j* = die Nummern (*j* − 1)·*g* + 1 bis *j*·*g*. Die Regel kennt nur die Gruppe eines Containers; bei *g* = 1 kennt sie alles.
3. **Vorschau k:** Beim Abruf *n* sind die genauen Nummern von *n* bis *n* + *k* bekannt. Für alle anderen Container bildet die Regel den **Schlüssel** aus den noch möglichen Nummern der Gruppe (Mittelwert).
4. **Regel:** engste Passung (Stück 1) auf den Schlüsseln. **Gleichstand** der Schlüssel zählt als unsicher.
5. **Maßstab:** dieselbe Regel bei voller Information, das Optimum (Stück 9, bis 16 Container) und die Untergrenzen. **Wert der Information** = Anteil der Lücke zwischen „nur Gruppen“ und „volle Information“, den die Vorschau schließt.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Stichprobe**")
    stacks = st.select_slider("Stapel", options=C.STACK_OPTIONS, key="stacks_slider", help="Wie viele Stapel die Bucht hat.")
    layers = st.slider("Lagen je Stapel", *bounds("layers_slider"), key="layers_slider", help="So viele Container stehen anfangs auf jedem Stapel.")
    extra = st.slider("Platz (Lagen über der Anfangshöhe)", *bounds("extra_slider"), key="extra_slider", help="Höchsthöhe = Lagen + Platz. Standard 2. Die vorberechneten Tabellen gelten für Platz 2.")
    st.markdown("**Wissen über die Reihenfolge**")
    group = st.select_slider("Gruppengröße g", options=C.GROUP_OPTIONS, key="group_slider", help="So viele aufeinanderfolgende Abrufe bilden eine Gruppe; 1 = die Reihenfolge ist ganz bekannt.")
    lookahead = st.select_slider("Vorschau k", options=C.LOOKAHEAD_OPTIONS, key="lookahead_slider", help="So viele Abrufe nach dem aktuellen sind vorab mit genauer Nummer bekannt.")
    bays = st.select_slider("Zahl der Buchten", options=C.BAY_OPTIONS, key="bays_slider", help="So viele Buchten gehören zur Stichprobe.")
    seed = st.number_input("Erste Bucht-Nummer (Seed)", *bounds("seed_input"), key="seed_input", step=1, help="Die Stichprobe besteht aus den Buchten Nummer Seed bis Seed + Buchten − 1.")
    st.button("🎲 Neue Stichprobe würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"stacks_slider": int(stacks), "layers_slider": int(layers), "extra_slider": int(extra), "group_slider": int(group), "lookahead_slider": int(lookahead),
                   "bays_slider": int(bays), "seed_input": int(seed)})

settings = Settings(int(stacks), int(layers), int(extra), int(group), int(lookahead), int(bays), int(seed))
with st.spinner("Arbeite die Stichprobe ab (Regel mit allen Vorschau-Stufen" + (", exakte Suche" if settings.stacks * settings.layers <= C.EXACT_MAX_CONTAINERS else "") + ") …"):
    a = _analysis(settings)
s = a.stats

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
k_used = min(settings.lookahead, a.containers)
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Nur Gruppen (k = 0)", dec(hub_at(s, 0)), delta=f"g = {settings.group}", delta_color="off", help="Hübe der Regel mit Kenntnis der Gruppen, Mittel über die Buchten.")
m2.metric(f"Mit Vorschau k = {settings.lookahead}", dec(hub_at(s, k_used)), delta=f"{percent_text(1 - hub_at(s, k_used) / hub_at(s, 0))} weniger" if hub_at(s, 0) else "–", delta_color="off",
          help="Hübe der Regel mit Vorschau auf die nächsten k Abrufe.")
m3.metric("Volle Information", dec(s["full"]), delta=f"Untergrenze LB2 {dec(s['lb2'])}", delta_color="off", help="Hübe der Regel, wenn die ganze Reihenfolge bekannt ist (g = 1).")
m4.metric("Erwartete Blocker", dec(s["eb"]), delta=f"gezählt {dec(s['lb1'])}", delta_color="off", help="Erwartete Blockerzahl bei nur gruppenweise bekannter Reihenfolge; darunter die Zählung an den wahren Nummern.")
if "opt" in s:
    m5.metric("Optimum (volle Info)", dec(s["opt"]["opt"]), delta=f"{s['opt']['n']} Buchten gerechnet", delta_color="off")
else:
    m5.metric("Optimum (volle Info)", "nicht gerechnet", delta=f"über {C.EXACT_MAX_CONTAINERS} Container", delta_color="off")
st.plotly_chart(build_bay(a.first_bay, a.height, target=1), width="stretch", key="chart_bay")
st.caption(f"Die erste Bucht der Stichprobe (Nummer {settings.seed}) mit den wahren Nummern. Rot: blockierende Container, grün: der nächste Abruf, grau-blau: alle übrigen. "
           f"Die Regel sieht davon nur die Gruppen (je {settings.group} Nummern) und, je nach Vorschau, die nächsten Abrufe.")
st.plotly_chart(build_curve([(f"g = {settings.group}", s["ks"], s["hubs"], C.COLOR_LINES[settings.group])], s["full"], s["lb2"]), width="stretch", key="chart_live")

st.markdown("## ❓ Kernfrage: Wie viel der Lücke schließt die Vorschau?")
name_here = f"{settings.stacks} × {settings.layers}, g = {settings.group}"
kind, text = verdict_info(s, k_used, name_here)
getattr(st, kind)(text)
if "opt" in s:
    st.info(f"Zum Vergleich (Stichprobe, {s['opt']['n']} Buchten): Das Optimum bei voller Information ist im Mittel {dec(s['opt']['opt'])} Hübe, die Regel mit voller Information braucht {dec(s['opt']['full'])}, "
            f"die Untergrenze LB2 {dec(s['opt']['lb2'])}.")

st.markdown("---")

# --- Experiment: eine Bucht von Hand ----------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Eine Bucht von Hand")
st.caption("3 Stapel der Höchsthöhe 5, 9 Container, Gruppen aus je 3 Nummern ((1 2 3), (4 5 6), (7 8 9)); von unten nach oben (2, 7, 4), (6, 1, 9), (8, 5, 3). Die 1 liegt unter der 9: Die 9 muss weg. "
           "Auf welchen Stapel? Die Regel kennt nur die Gruppen (Schlüssel = Mittelwert der möglichen Nummern) und, je nach Vorschau, die ersten Abrufe.")
st.plotly_chart(build_bay(C.HAND_BAY, C.HAND_HEIGHT, target=1), width="stretch", key="chart_hand")
ht = ["| Vorschau k | Schlüssel der 9 | Stapel 1: früheste Nummer | Stapel 3: früheste Nummer | gewählt | Hübe der ganzen Bucht |", "|---|---|---|---|---|---|"]
for k_ in (0, 1, 2):
    d = _hand(k_)
    cs = {c["stack"]: c for c in d["candidates"]}
    ht.append(f"| {k_} | {dec(d['key'])} | {dec(cs[0]['min_key'])} | {dec(cs[2]['min_key'])} | Stapel {d['dest'] + 1} | {d['hubs']} |")
st.markdown("\n".join(ht))
d0, d1 = _hand(0), _hand(1)
st.success(f"Ohne Vorschau sehen beide Stapel gleich aus (früheste mögliche Nummer jeweils {dec(d0['candidates'][0]['min_key'])}): Gleichstand, die Regel nimmt Stapel 1 und braucht {d0['hubs']} Hübe. "
           f"Schon mit **einem** enthüllten Abruf weiß sie, dass die 2 auf Stapel 1 liegt und die 3 auf Stapel 3 später dran ist: Sie wählt Stapel 3 und braucht {d1['hubs']} Hübe, "
           f"das **Optimum** bei voller Information ({d1['optimum']}).")

st.markdown("---")

# --- Experiment: Wert der Vorschau ---------------------------------------------------------------------------------------------------------------------

bands = _bands()
kurve, gleich, exakt = bands["kurve"], bands["gleichstand"], bands["exakt"]
st.subheader("🔬 Experiment: Der Wert der Vorschau")
st.caption(f"Hübe der Regel (Mittel über {C.CURVE_BAYS} feste Buchten, Platz 2, vorberechnet) gegen die Vorschau k; „alle“ = volle Information der Container. Zeile *g* = 1 wäre die volle Information selbst.")
ks_all = kurve[curve_key(4, 3, 2)]["ks"]
ta = ["| Zelle, Gruppengröße | volle Information | " + " | ".join(f"k = {k}" for k in ks_all[:-1]) + " | alle |", "|---|---|" + "---|" * len(ks_all)]
for s_, l_ in C.CURVE_CELLS:
    for g_ in C.CURVE_GROUPS:
        c = kurve[curve_key(s_, l_, g_)]
        ta.append(f"| {s_} × {l_}, g = {g_} | {dec(c['full'])} | " + " | ".join(dec(h) for h in c["hubs"]) + " |")
st.markdown("\n".join(ta))
cell = (settings.stacks, settings.layers) if (settings.stacks, settings.layers) in C.CURVE_CELLS else (4, 4)
series = [(f"g = {g_}", kurve[curve_key(*cell, g_)]["ks"], kurve[curve_key(*cell, g_)]["hubs"], C.COLOR_LINES[g_]) for g_ in C.CURVE_GROUPS]
st.plotly_chart(build_curve(series, kurve[curve_key(*cell, 2)]["full"], kurve[curve_key(*cell, 2)]["lb2"]), width="stretch", key="chart_curve")
st.markdown(f"**Zelle {cell[0]} × {cell[1]}**" + ("" if cell == (settings.stacks, settings.layers) else f" (Ihre Zelle {settings.stacks} × {settings.layers} ist nicht vorberechnet; gezeigt wird 4 × 4)") + ", Gruppengröße je nach Ihrer Einstellung:")
g_cell = settings.group if settings.group in C.CURVE_GROUPS else 6
if settings.group not in C.CURVE_GROUPS:
    st.info(f"Für die Gruppengröße {settings.group} wurde nichts vorberechnet; gezeigt wird g = 6 (vorberechnet: {', '.join(str(g) for g in C.CURVE_GROUPS)}).")
kind, text = verdict_curve(kurve[curve_key(*cell, g_cell)], g_cell, f"{cell[0]} × {cell[1]}, g = {g_cell}")
getattr(st, kind)(text)

st.markdown("**Grenznutzen: gesparte Hübe je Stufe** (Ihre Stichprobe, Ihre Gruppengröße):")
mr = marginal_rows(s)
tm = ["| Vorschau k | Hübe | gespart gegenüber der vorigen Stufe | geschlossener Anteil der Lücke |", "|---|---|---|---|"]
for r in mr:
    tm.append(f"| {r['k'] if r['k'] != s['ks'][-1] else 'alle'} | {dec(r['hubs'])} | {'–' if r['saved'] is None else dec(r['saved'])} | {'–' if r['share'] is None else percent_text(r['share'])} |")
st.markdown("\n".join(tm))
if len(mr) > 1:
    st.plotly_chart(build_saved(mr), width="stretch", key="chart_saved")

st.markdown("---")

# --- Experiment: Gleichstand ---------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Gleichstand")
st.caption("Zwei Container derselben Gruppe haben den gleichen Schlüssel. Soll die Regel einen Stapel, dessen früheste Nummer „gleich“ ist, als **sicher** oder als **unsicher** ansehen? Hübe (Mittel über 200 Buchten).")
tt = ["| Zelle, Gruppengröße, Vorschau | Gleichstand = unsicher | Gleichstand = sicher | Unterschied |", "|---|---|---|---|"]
for key_ in sorted(gleich, key=lambda k: tuple(int(x) for x in k.split(","))):
    c = gleich[key_]
    s_, l_, g_, k_ = key_.split(",")
    tt.append(f"| {s_} × {l_}, g = {g_}, k = {k_} | {dec(c['strict'])} | {dec(c['safe'])} | {percent_text((c['safe'] - c['strict']) / c['safe'])} weniger |")
st.markdown("\n".join(tt))
st.plotly_chart(build_tie(gleich), width="stretch", key="chart_tie")
tk = tie_key(settings.stacks, settings.layers, settings.group, settings.lookahead)
tk_used = tk if tk in gleich else tie_key(4, 4, 6, 0)
if tk not in gleich:
    st.info("Für Ihre Einstellung wurde der Gleichstand nicht vorberechnet; gezeigt wird 4 × 4, g = 6, k = 0.")
kind, text = verdict_tie(gleich[tk_used]["strict"], gleich[tk_used]["safe"], " × ".join(tk_used.split(",")[:2]) + f", g = {tk_used.split(',')[2]}, k = {tk_used.split(',')[3]}")
getattr(st, kind)(text)
st.caption("Der Schlüssel für nicht enthüllte Container (Mittelwert, kleinste oder größte mögliche Nummer der Gruppe) liefert in der Vormessung in allen vier Zellen **dieselben** Hubzahlen: Nur die Reihenfolge der Schlüssel zählt.")

st.markdown("---")

# --- Experiment: Untergrenze unter Unsicherheit -------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Die Untergrenze unter Unsicherheit")
st.caption("Erwartete Blockerzahl, wenn nur die Gruppen bekannt sind (ein Container blockiert mit Wahrscheinlichkeit 1, wenn unter ihm ein Container einer früheren Gruppe liegt, sonst mit m / (m + 1)), "
           "gegen die Zählung an den wahren Nummern (Mittel über 200 Buchten).")
te = ["| Zelle, Gruppengröße | erwartete Blocker | gezählt an den wahren Nummern | LB2 |", "|---|---|---|---|"]
for s_, l_ in C.CURVE_CELLS:
    for g_ in C.CURVE_GROUPS:
        c = kurve[curve_key(s_, l_, g_)]
        te.append(f"| {s_} × {l_}, g = {g_} | {dec(c['eb'])} | {dec(c['lb1'])} | {dec(c['lb2'])} |")
st.markdown("\n".join(te))
st.markdown("**Ihre Stichprobe:**")
kind, text = verdict_expect(s, settings.group, name_here)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: das Optimum ------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Das Optimum bei voller Information")
st.caption(f"Wie gut ist die Regel selbst, wenn alles bekannt ist? Optimum aus der Suche (Stück 9), Regel mit voller Information und die Untergrenze LB2 ({C.EXACT_BAYS} Buchten je Zeile, Mittel).")
tx = ["| Zelle (Buchten) | Optimum | Regel (volle Information) | Untergrenze LB2 | Regel über Optimum |", "|---|---|---|---|---|"]
for s_, l_ in C.EXACT_CELLS:
    c = exakt[f"{s_},{l_}"]["opt"]
    tx.append(f"| {s_} × {l_} ({c['n']}) | {dec(c['opt'])} | {dec(c['full'])} | {dec(c['lb2'])} | {percent_text(c['full'] / c['opt'] - 1)} |")
st.markdown("\n".join(tx))
st.info("Auch bei voller Information liegt die Regel über dem Optimum (Stück 1). Die Lücken „Nichtwissen“ und „Regel“ addieren sich: Das Nichtwissen kostet zusätzlich zu dem, was die Regel ohnehin verschenkt.")

st.markdown("---")

# --- Grenzen ----------------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Eine Art von Unsicherheit** | Nur die Reihenfolge innerhalb von Gruppen ist unbekannt (gleichverteilt zufällig). Fehlerhafte Abrufmeldungen, Verspätungen oder Gruppen, die sich überlappen, sind nicht gemessen. | Vorhersagen und Online-Algorithmen |
| **Die Regel ist die engste Passung** | Sie nutzt die Erwartung der Schlüssel, ist aber keine erwartungswertoptimale Strategie; deren Hubzahl ist nicht gerechnet. Verglichen wird nur mit dem Optimum bei voller Information. | – |
| **Die Schranke der Literatur** | Eine Schranke für die erwartete Umlagerungszahl und eine erwartungswertbasierte Heuristik werden in der Literatur untersucht (APJOR 2025; aus dem Gedächtnis zugeordnet, nicht gelesen); nachgebaut ist sie nicht. Hier steht nur die erwartete Blockerzahl. | – |
| **Volle Buchten, restricted, Platz 2** | Teilgefüllte Buchten, andere Höhen und freies Umlagern ändern die Zahlen. | Stück 3, 10 |
| **Feste Seeds, kleine Zellen** | 200 Buchten je Zelle, 100 beim Optimum; Zellen 4 × 3, 4 × 4, 5 × 4, 8 × 3 und Gruppen 2, 3, 4, 6. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben:** volle Bucht mit $N$ Containern, wahre Abrufnummern $1, \dots, N$; Gruppengröße $g$: Gruppe $j = \{(j-1)g + 1, \dots, jg\}$ (die letzte ist kürzer). Die Regel kennt die Gruppe jedes Containers; innerhalb der Gruppe ist die Zuordnung der Nummern zu den Containern gleichverteilt zufällig.

**Vorschau.** Beim Abruf $n$ sind die Nummern $n, \dots, n + k$ ihren Containern zugeordnet bekannt. Ein nicht enthüllter Container der Gruppe $j$ trägt eine der noch freien Nummern $U_j = \{m \in \text{Gruppe } j : m > n + k\}$, jede gleich wahrscheinlich. Sein **Schlüssel** ist der Erwartungswert $\kappa = \tfrac{1}{|U_j|}\sum_{m \in U_j} m$; ein enthüllter Container hat seine Nummer als Schlüssel.

**Regel.** Engste Passung (Stück 1) auf den Schlüsseln: Ein Blocker $c$ kommt auf den Stapel mit Platz, dessen kleinster Schlüssel größer als $\kappa(c)$ und am kleinsten ist; gibt es keinen, auf den mit dem größten kleinsten Schlüssel. Bei Gleichstand gilt der Stapel als unsicher.

**Wert der Information.** Sei $\bar H(k)$ die mittlere Hubzahl der Regel bei Vorschau $k$ und $\bar H_\infty$ bei voller Information ($g = 1$). Die **Lücke** ist $\bar H(0) - \bar H_\infty$, der **geschlossene Anteil** bei Vorschau $k$ ist $(\bar H(0) - \bar H(k)) / (\bar H(0) - \bar H_\infty)$.

**Erwartete Blocker.** Ein Container $c$ in Gruppe $j$ an Position $i$ ist ein Blocker, wenn unter ihm ein Container mit kleinerer wahrer Nummer liegt. Liegt unter ihm ein Container einer früheren Gruppe, ist er sicher Blocker. Sonst gehören die $m$ Container unter ihm mit derselben Gruppe wie $c$ und alle übrigen unter ihm zu späteren Gruppen; $c$ ist genau dann kein Blocker, wenn seine Nummer die kleinste unter diesen $m + 1$ ist, mit Wahrscheinlichkeit $1/(m+1)$. Also
$$\mathbb{E}[\text{LB1}] = \sum_c \begin{cases} 1 & \text{früherer Gruppe unter } c \\ m_c/(m_c + 1) & \text{sonst.}\end{cases}$$
Das ist der Erwartungswert der Zählung aus Stück 2 über die zufälligen Reihenfolgen innerhalb der Gruppen (im Test an allen Zuordnungen kleiner Buchten nachgerechnet).

**Literatur.** Eine Schranke für die erwartete Umlagerungszahl und eine erwartungswertbasierte Heuristik für unbekannte Abrufreihenfolgen innerhalb von Gruppen (APJOR 2025) sind aus dem Gedächtnis zugeordnet, nicht gelesen. Die Zahlen hier sind eigene Messungen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
