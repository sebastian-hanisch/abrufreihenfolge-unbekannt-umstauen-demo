"""Permalink (Begrenzen), Presets und Zufalls-Seed-Button (Standardmuster aus dem Demo-Portfolio)."""

import random
from dataclasses import dataclass

import streamlit as st

import uas_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None


SETTING_SPECS = {
    "stacks_slider": SettingSpec("stacks", int, C.DEFAULT_STACKS, C.STACK_OPTIONS[0], C.STACK_OPTIONS[-1]),
    "layers_slider": SettingSpec("layers", int, C.DEFAULT_LAYERS, C.LAYERS_MIN, C.LAYERS_MAX),
    "extra_slider": SettingSpec("extra", int, C.DEFAULT_EXTRA, C.EXTRA_MIN, C.EXTRA_MAX),
    "group_slider": SettingSpec("group", int, C.DEFAULT_GROUP, C.GROUP_OPTIONS[0], C.GROUP_OPTIONS[-1]),
    "lookahead_slider": SettingSpec("lookahead", int, C.DEFAULT_LOOKAHEAD, C.LOOKAHEAD_OPTIONS[0], C.LOOKAHEAD_OPTIONS[-1]),
    "bays_slider": SettingSpec("bays", int, C.DEFAULT_BAYS, C.BAY_OPTIONS[0], C.BAY_OPTIONS[-1]),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
}
PRESET_KEYS = {"stacks": "stacks_slider", "layers": "layers_slider", "extra": "extra_slider", "group": "group_slider", "lookahead": "lookahead_slider", "bays": "bays_slider",
               "seed": "seed_input"}
OPTIONS = {"stacks_slider": C.STACK_OPTIONS, "group_slider": C.GROUP_OPTIONS, "lookahead_slider": C.LOOKAHEAD_OPTIONS, "bays_slider": C.BAY_OPTIONS}   # Regler mit festen Stufen


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def snap(state_key, value):
    """Wert auf die Reglergrenzen begrenzen; bei Reglern mit festen Stufen auf die nächste Stufe."""
    spec = SETTING_SPECS[state_key]
    if state_key in OPTIONS:
        return min(OPTIONS[state_key], key=lambda o: (abs(o - value), o))
    if spec.lo is not None:
        value = max(spec.lo, value)
    if spec.hi is not None:
        value = min(spec.hi, value)
    return value


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen und Stufen gebracht."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            st.session_state[state_key] = snap(state_key, value)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen
    Standardwert) mit dem Session State. Ein später ergänzter Regler braucht nur seinen Eintrag in SETTING_SPECS,
    dann hebt auch seine Änderung die Markierung auf (tests/test_layout.py prüft das für jeden Regler)."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
