"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import uas_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def blocker_cells(stacks) -> set:
    """Container, die über einem früher abzurufenden im selben Stapel liegen (Position (Stapel, Lage))."""
    out = set()
    for i, s in enumerate(stacks):
        lowest = 10 ** 9
        for j, c in enumerate(s):
            if c > lowest:
                out.add((i, j))
            else:
                lowest = c
    return out


def build_bay(stacks, height, target=None):
    """Die Bucht als Säulen: je Lage ein Balken mit der Abrufnummer. Rot: blockiert einen früher abzurufenden, grün: nächster Abruf
    (`target`, eine Abrufnummer oder None), grau-blau: übrige."""
    blockers = blocker_cells(stacks)
    fig = go.Figure()
    xs = list(range(len(stacks)))
    for j in range(height):
        ys, colors, texts = [], [], []
        for i, s in enumerate(stacks):
            if j < len(s):
                c = s[j]
                ys.append(1)
                texts.append(str(c))
                colors.append(C.COLOR_TARGET if c == target else C.COLOR_BLOCK if (i, j) in blockers else C.COLOR_CELL)
            else:
                ys.append(0)
                texts.append("")
                colors.append(C.COLOR_CELL)
        fig.add_trace(go.Bar(x=xs, y=ys, base=j, marker_color=colors, text=texts, textposition="inside", insidetextanchor="middle",
                             textfont=dict(color="#ffffff", size=16), width=0.78, showlegend=False,
                             hovertemplate="Abruf %{text}<extra></extra>", marker_line=dict(width=0)))
    fig.update_layout(barmode="overlay")
    fig.add_hline(y=height, line_dash="dot", line_color="rgba(128,128,128,0.7)", annotation_text="Höchsthöhe", annotation_position="top left")
    fig.update_xaxes(tickvals=xs, ticktext=[f"Stapel {i + 1}" for i in xs], showgrid=False)
    fig.update_yaxes(range=[0, height + 0.35], showticklabels=False, showgrid=False, zeroline=False)
    return _base(fig, height=48 * height + 90)


def _labels(ks):
    """Beschriftung der Vorschau-Stufen: die letzte Stufe (= alle Container) heißt „alle“."""
    return [str(k) for k in ks[:-1]] + ["alle"]


def build_curve(series, full, lb2=None):
    """Hubzahl der Regel gegen die Vorschau k, je Gruppengröße eine Linie; dazu die volle Information (und LB2) als eigene Linien. `series`: [(Name, ks, hubs, Farbe)] mit gleichen ks."""
    fig = go.Figure()
    ks = series[0][1]
    labels = _labels(ks)
    for name, _, hubs, color in series:
        fig.add_trace(go.Scatter(x=labels, y=hubs, mode="lines+markers", name=name, line=dict(color=color), hovertemplate="Vorschau %{x}: %{y:.2f} Hübe<extra>%{fullData.name}</extra>"))
    fig.add_trace(go.Scatter(x=labels, y=[full] * len(labels), mode="lines", name="volle Information", line=dict(color=C.COLOR_FULL, dash="dot"), hovertemplate="%{y:.2f}<extra>%{fullData.name}</extra>"))
    if lb2 is not None:
        fig.add_trace(go.Scatter(x=labels, y=[lb2] * len(labels), mode="lines", name="Untergrenze LB2", line=dict(color=C.COLOR_LB, dash="dash"), hovertemplate="%{y:.2f}<extra>%{fullData.name}</extra>"))
    fig.update_xaxes(type="category", title_text="Vorschau k (Abrufe nach dem aktuellen, deren Nummer vorab bekannt ist)")
    fig.update_yaxes(title_text="Hübe (Mittel)", rangemode="normal")
    return _base(fig, height=360)


def build_saved(rows):
    """Gesparte Hübe je Vorschau-Stufe gegenüber der vorigen (Grenznutzen). `rows`: marginal_rows (die erste Stufe hat nichts gespart und fehlt)."""
    rows = [r for r in rows if r["saved"] is not None]
    fig = go.Figure(go.Bar(x=[f"auf {r['k']}" for r in rows], y=[r["saved"] for r in rows], marker_color=C.COLOR_OPT, hovertemplate="%{x}: %{y:.2f} Hübe gespart<extra></extra>"))
    fig.update_xaxes(type="category", title_text="Vorschau erhöht auf k")
    fig.update_yaxes(title_text="gesparte Hübe gegenüber der vorigen Stufe", rangemode="tozero")
    return _base(fig, height=300)


def build_tie(cells):
    """Hubzahl bei Gleichstand = unsicher und = sicher je Zelle (Stapel, Lagen, Gruppengröße, Vorschau). `cells`: {"s,l,g,k": {"strict", "safe"}}."""
    keys = sorted(cells, key=lambda k: tuple(int(x) for x in k.split(",")))
    x = [f"{k.split(',')[0]} × {k.split(',')[1]}, g = {k.split(',')[2]}, k = {k.split(',')[3]}" for k in keys]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=[cells[k]["strict"] for k in keys], name="Gleichstand = unsicher", marker_color=C.COLOR_OPT, hovertemplate="%{x}: %{y:.2f}<extra>%{fullData.name}</extra>"))
    fig.add_trace(go.Bar(x=x, y=[cells[k]["safe"] for k in keys], name="Gleichstand = sicher", marker_color=C.COLOR_BLOCK, hovertemplate="%{x}: %{y:.2f}<extra>%{fullData.name}</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Zelle")
    fig.update_yaxes(title_text="Hübe (Mittel)", rangemode="tozero")
    return _base(fig, height=360)
