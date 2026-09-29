"""
MailCraft AI — Professional Dashboard
"""

import asyncio
import html
import json
import sys
import time
import urllib.parse
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import plotly.graph_objects as go
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MailCraft AI",
    page_icon=":material/mail:",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"
DATA_DIR = ROOT / "data"

PAGES = {
    "Generate Email": ":material/edit_note: Generate Email",
    "Evaluation Dashboard": ":material/insights: Evaluation Dashboard",
    "Test Scenarios": ":material/fact_check: Test Scenarios",
}
TONES = [
    "formal", "professional", "friendly-casual", "empathetic",
    "excited", "neutral", "persuasive", "warm-grateful",
    "urgent", "casual-compelling",
]
STRATEGY_INFO = {
    "advanced": "Chain-of-thought + few-shot + role-play, followed by a self-reflection critic pass.",
    "baseline": "Single zero-shot instruction prompt. Faster and cheaper, less reliable.",
}
METRICS = ["Fact Recall", "Tone Alignment", "Professional Quality"]

# ── Design tokens ────────────────────────────────────────────────────────
C = {
    "bg": "#0d1015", "surface": "#141821", "surface2": "#1b202b",
    "border": "#252b37", "border2": "#313847",
    "text": "#e6e8eb", "text2": "#a3a9b5", "text3": "#707887",
    "accent": "#4c8dff", "accent2": "#3b7cf0", "accent_bg": "rgba(76,141,255,0.10)",
    "green": "#3fb68b", "green_bg": "rgba(63,182,139,0.12)",
    "yellow": "#d4a72c", "yellow_bg": "rgba(212,167,44,0.12)",
    "orange": "#d9822b", "orange_bg": "rgba(217,130,43,0.12)",
    "red": "#e5534b", "red_bg": "rgba(229,83,75,0.12)",
    "blue": "#4c8dff", "blue_bg": "rgba(76,141,255,0.12)",
    "slate": "#94a3b8", "slate_bg": "rgba(148,163,184,0.12)",
}

# ── Global CSS ───────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    .block-container {{ padding: 2.5rem 2.5rem 3rem; max-width: 1280px; }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 1.5rem; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    /* ── Sidebar nav ── */
    .nav-brand {{
        display: flex; align-items: center; gap: 0.7rem;
        padding: 0 0.25rem 1.4rem; border-bottom: 1px solid {C["border"]};
        margin-bottom: 1.4rem;
    }}
    .nav-brand .icon {{
        width: 34px; height: 34px; border-radius: 8px; background: {C["accent"]};
        display: flex; align-items: center; justify-content: center;
    }}
    .nav-brand .title {{ font-weight: 600; font-size: 0.95rem; color: {C["text"]}; letter-spacing: -0.01em; }}
    .nav-brand .sub {{ font-size: 0.72rem; color: {C["text3"]}; }}

    .nav-section {{ padding: 0 0.25rem; margin: 0 0 0.4rem;
                    font-size: 0.66rem; font-weight: 600; color: {C["text3"]};
                    text-transform: uppercase; letter-spacing: 0.08em; }}

    [data-testid="stSidebar"] [role="radiogroup"] {{ gap: 2px; width: 100%; }}
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        width: 100%; margin: 0; padding: 0.5rem 0.75rem; border-radius: 6px;
        cursor: pointer; transition: background 0.12s ease;
        border-left: 2px solid transparent;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{ display: none; }}
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background: {C["surface2"]}; }}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
        background: {C["surface2"]}; border-left-color: {C["accent"]};
        border-radius: 0 6px 6px 0;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{
        color: {C["text"]}; font-weight: 600;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label p {{
        font-size: 0.86rem; color: {C["text2"]};
    }}

    .sys-card {{
        background: {C["bg"]}; border: 1px solid {C["border"]}; border-radius: 6px;
        padding: 0.85rem 0.95rem; font-size: 0.78rem; line-height: 1.9;
    }}
    .sys-row {{ display: flex; justify-content: space-between; gap: 0.5rem; }}
    .sys-row .k {{ color: {C["text3"]}; }}
    .sys-row .v {{ color: {C["text"]}; font-weight: 500; text-align: right;
                   overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .sys-feat {{ margin-top: 0.55rem; padding-top: 0.55rem; border-top: 1px solid {C["border"]};
                 color: {C["text3"]}; line-height: 1.8; }}
    .sys-feat div::before {{
        content: ""; display: inline-block; width: 4px; height: 4px; border-radius: 50%;
        background: {C["text3"]}; margin-right: 0.55rem; vertical-align: middle;
    }}

    /* ── Page header ── */
    .page-header {{ padding: 0 0 1.25rem; border-bottom: 1px solid {C["border"]}; margin-bottom: 1.75rem; }}
    .page-header .eyebrow {{
        font-size: 0.68rem; font-weight: 600; color: {C["text3"]};
        text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.35rem;
    }}
    .page-header h1 {{
        font-size: 1.5rem; font-weight: 700; color: {C["text"]};
        margin: 0 0 0.3rem; padding: 0; letter-spacing: -0.015em;
    }}
    .page-header p {{ font-size: 0.9rem; color: {C["text2"]}; margin: 0; line-height: 1.55; max-width: 760px; }}

    .section-title {{
        font-size: 0.78rem; font-weight: 600; color: {C["text2"]};
        text-transform: uppercase; letter-spacing: 0.06em;
        margin: 2rem 0 0.75rem; display: flex; align-items: center; gap: 0.5rem;
    }}
    .section-title .count {{
        font-size: 0.7rem; font-weight: 600; color: {C["text3"]}; letter-spacing: 0;
        background: {C["surface2"]}; padding: 0.05rem 0.45rem; border-radius: 4px;
    }}

    /* ── Metric / comparison cards ── */
    .m-card {{
        background: {C["surface"]}; border: 1px solid {C["border"]};
        border-radius: 8px; padding: 1.1rem 1.25rem; height: 100%;
    }}
    .m-card.hero {{ border-top: 2px solid {C["accent"]}; }}
    .m-label {{
        font-size: 0.7rem; font-weight: 600; color: {C["text3"]};
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem;
    }}
    .m-value {{ font-size: 1.85rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1;
                font-variant-numeric: tabular-nums; }}
    .m-value small {{ font-size: 0.85rem; font-weight: 600; color: {C["text3"]}; margin-left: 0.2rem; }}
    .m-sub {{ font-size: 0.76rem; color: {C["text3"]}; margin-top: 0.45rem;
              display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; }}
    .delta {{
        font-size: 0.72rem; font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 4px;
        font-variant-numeric: tabular-nums;
    }}

    .winner-banner {{
        display: flex; align-items: center; gap: 0.75rem;
        background: {C["surface"]}; border: 1px solid {C["border"]};
        border-left: 2px solid {C["accent"]};
        border-radius: 0 6px 6px 0; padding: 0.75rem 1rem; margin-bottom: 1rem;
        font-size: 0.86rem; color: {C["text2"]};
    }}
    .winner-banner .tag {{
        font-size: 0.66rem; font-weight: 600; color: {C["text3"]};
        text-transform: uppercase; letter-spacing: 0.08em;
    }}
    .winner-banner b {{ color: {C["text"]}; font-weight: 600; }}

    /* ── Strategy badge ── */
    .strat-badge {{
        display: inline-flex; align-items: center; gap: 0.35rem;
        padding: 0.18rem 0.55rem; border-radius: 4px;
        font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.06em; vertical-align: middle;
    }}
    .strat-advanced {{ background: {C["blue_bg"]}; color: {C["blue"]}; }}
    .strat-baseline {{ background: {C["slate_bg"]}; color: {C["slate"]}; }}

    .chip {{
        display: inline-flex; align-items: center; gap: 0.3rem;
        padding: 0.18rem 0.55rem; border-radius: 4px; font-size: 0.72rem; font-weight: 500;
        background: {C["surface2"]}; color: {C["text2"]}; border: 1px solid {C["border"]};
        vertical-align: middle;
    }}
    .chip.ok {{ background: {C["green_bg"]}; color: {C["green"]}; border-color: transparent; }}

    /* ── Score bar ── */
    .sbar {{ display: flex; align-items: center; gap: 0.6rem; padding: 0.4rem 0; }}
    .sbar .lbl {{ width: 140px; font-size: 0.8rem; font-weight: 500; color: {C["text2"]}; }}
    .sbar .track {{ flex: 1; height: 4px; background: {C["surface2"]}; border-radius: 2px; overflow: hidden; }}
    .sbar .fill {{ height: 100%; border-radius: 2px; }}
    .sbar .num {{ width: 38px; text-align: right; font-weight: 600; font-size: 0.82rem;
                  font-variant-numeric: tabular-nums; }}

    /* ── Email card (client-style preview) ── */
    .mail-card {{
        background: {C["surface"]}; border: 1px solid {C["border"]};
        border-radius: 8px; overflow: hidden;
    }}
    .mail-meta {{
        display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap;
        padding: 0.8rem 1.3rem; background: {C["surface2"]};
        border-bottom: 1px solid {C["border"]};
    }}
    .mail-subject {{ padding: 1.1rem 1.5rem 0.9rem; border-bottom: 1px solid {C["border"]}; }}
    .mail-subject .lbl {{
        font-size: 0.66rem; font-weight: 600; color: {C["text3"]};
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.25rem;
    }}
    .mail-subject .txt {{ font-size: 1rem; font-weight: 600; color: {C["text"]}; line-height: 1.4; }}
    .mail-body {{
        padding: 1.3rem 1.5rem 1.5rem; font-size: 0.9rem; line-height: 1.75;
        color: {C["text"]}; white-space: pre-wrap; word-wrap: break-word;
    }}
    .mail-body.compact {{ font-size: 0.84rem; padding: 1.1rem 1.3rem; max-height: 420px; overflow-y: auto; }}

    .mail-empty {{
        min-height: 430px; display: flex; flex-direction: column; align-items: center;
        justify-content: center; text-align: center; padding: 2rem;
        border: 1px solid {C["border"]}; border-radius: 8px; background: {C["surface"]};
    }}
    .mail-empty .ic {{
        width: 44px; height: 44px; border-radius: 8px; margin-bottom: 1rem;
        background: {C["surface2"]}; border: 1px solid {C["border"]};
        display: flex; align-items: center; justify-content: center;
    }}
    .mail-empty h4 {{ font-size: 0.95rem; font-weight: 600; color: {C["text"]}; margin: 0 0 0.4rem; padding: 0; }}
    .mail-empty p {{ font-size: 0.84rem; color: {C["text3"]}; margin: 0; line-height: 1.6; max-width: 340px; }}

    /* ── Send buttons ── */
    .send-btns {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
    .send-btns a {{
        flex: 1; display: inline-flex; align-items: center; justify-content: center; gap: 0.45rem;
        padding: 0.45rem 0.9rem; border-radius: 6px; min-height: 38px;
        font-size: 0.82rem; font-weight: 500; text-decoration: none !important;
        background: {C["surface"]}; color: {C["text"]} !important; border: 1px solid {C["border2"]};
        transition: border-color 0.12s, background 0.12s;
    }}
    .send-btns a:hover {{ border-color: {C["accent"]}; background: {C["surface2"]}; }}
    .send-btns a svg {{ opacity: 0.75; }}

    /* ── Live feed rows ── */
    .feed-row {{
        display: flex; align-items: center; gap: 0.75rem;
        padding: 0.6rem 1rem; margin: 0.25rem 0;
        background: {C["surface"]}; border: 1px solid {C["border"]};
        border-radius: 6px; font-size: 0.82rem;
    }}
    .feed-dot {{ width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }}
    .feed-info {{ flex: 1; color: {C["text"]}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .feed-scores {{ display: flex; gap: 0.4rem; }}
    .feed-pill {{
        padding: 0.12rem 0.45rem; border-radius: 4px; min-width: 34px; text-align: center;
        font-size: 0.75rem; font-weight: 600; font-variant-numeric: tabular-nums;
    }}

    /* ── Empty state ── */
    .empty-state {{
        text-align: center; padding: 3.2rem 2rem; margin-top: 1rem;
        background: {C["surface"]}; border: 1px solid {C["border"]}; border-radius: 8px;
    }}
    .empty-state h3 {{ font-size: 1rem; font-weight: 600; color: {C["text"]}; margin: 0.8rem 0 0.5rem; padding: 0; }}
    .empty-state p {{ color: {C["text3"]}; font-size: 0.88rem; margin: 0; line-height: 1.6; }}

    /* ── Info cards ── */
    .info-card {{
        background: {C["surface"]}; border: 1px solid {C["border"]};
        border-radius: 8px; padding: 1rem 1.15rem; height: 100%;
    }}
    .info-card .ic-title {{ font-size: 0.82rem; font-weight: 600; color: {C["text"]}; margin-bottom: 0.35rem; }}
    .info-card .ic-desc {{ font-size: 0.76rem; color: {C["text3"]}; line-height: 1.55; }}

    /* ── Scenario header ── */
    .sc-header {{ display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.8rem; }}
    .sc-num {{
        width: 28px; height: 28px; border-radius: 6px; flex-shrink: 0;
        background: {C["surface2"]}; color: {C["text2"]}; border: 1px solid {C["border"]};
        display: flex; align-items: center; justify-content: center;
        font-weight: 600; font-size: 0.78rem; font-variant-numeric: tabular-nums;
    }}
    .sc-title {{ font-weight: 600; font-size: 0.92rem; color: {C["text"]}; flex: 1; }}
    .sc-tone {{
        font-size: 0.7rem; font-weight: 500; padding: 0.18rem 0.55rem; border-radius: 4px;
        background: {C["surface2"]}; color: {C["text2"]}; border: 1px solid {C["border"]};
        text-transform: capitalize;
    }}
    .fact-list {{ list-style: none; padding: 0; margin: 0; }}
    .fact-list li {{
        position: relative; padding: 0.3rem 0 0.3rem 1.2rem;
        font-size: 0.84rem; color: {C["text2"]}; line-height: 1.5;
    }}
    .fact-list li::before {{
        content: ""; position: absolute; left: 0.2rem; top: 0.78rem;
        width: 5px; height: 5px; border-radius: 50%; background: {C["text3"]};
    }}
    .sub-label {{
        font-size: 0.7rem; font-weight: 600; color: {C["text3"]};
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem;
    }}

    /* ── Widgets ── */
    .stTabs [data-baseweb="tab-list"] {{ gap: 0; border-bottom: 1px solid {C["border"]}; }}
    .stTabs [data-baseweb="tab"] {{ padding: 0.6rem 1.2rem; font-weight: 600; font-size: 0.82rem; }}
    [data-testid="stExpander"] details {{ background: {C["surface"]}; border-color: {C["border"]}; border-radius: 8px; }}
    .stButton > button, .stDownloadButton > button, [data-testid="stPopover"] button {{
        font-weight: 500; border-radius: 6px;
    }}
    .stButton > button[kind="primary"] {{
        background: {C["accent"]}; border: 1px solid {C["accent"]}; font-weight: 600;
        transition: background 0.12s;
    }}
    .stButton > button[kind="primary"]:hover {{ background: {C["accent2"]}; border-color: {C["accent2"]}; }}
    .stProgress > div > div > div > div {{ background: {C["accent"]}; }}
</style>
""", unsafe_allow_html=True)


# ── Session state ────────────────────────────────────────────────────────
_DEFAULTS = {
    "page": "Generate Email",
    "gen_intent": "",
    "gen_facts": "",
    "gen_tone": "professional",
    "gen_strategy": "advanced",
    "last_result": None,
    "history": [],
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Helpers ──────────────────────────────────────────────────────────────
def esc(text) -> str:
    return html.escape(str(text or ""))


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def sc(v):
    if v >= 85: return C["green"]
    if v >= 70: return C["yellow"]
    if v >= 50: return C["orange"]
    return C["red"]


def sc_bg(v):
    if v >= 85: return C["green_bg"]
    if v >= 70: return C["yellow_bg"]
    if v >= 50: return C["orange_bg"]
    return C["red_bg"]


def badge_html(strat):
    cls = "strat-advanced" if strat == "advanced" else "strat-baseline"
    return f'<span class="strat-badge {cls}">{esc(strat)}</span>'


def pill_html(v):
    return f'<span class="feed-pill" style="background:{sc_bg(v)};color:{sc(v)};">{v:.0f}</span>'


def delta_html(d):
    if d > 0.05:
        return f'<span class="delta" style="background:{C["green_bg"]};color:{C["green"]};">▲ {d:.1f}</span>'
    if d < -0.05:
        return f'<span class="delta" style="background:{C["red_bg"]};color:{C["red"]};">▼ {abs(d):.1f}</span>'
    return f'<span class="delta" style="background:{C["surface2"]};color:{C["text3"]};">± 0.0</span>'


def section_title(text, count=None):
    count_html = f'<span class="count">{count}</span>' if count is not None else ""
    st.markdown(f'<div class="section-title">{esc(text)}{count_html}</div>', unsafe_allow_html=True)


def page_header(eyebrow, title, desc):
    st.markdown(f'<div class="page-header"><div class="eyebrow">{esc(eyebrow)}</div>'
                f'<h1>{esc(title)}</h1><p>{esc(desc)}</p></div>', unsafe_allow_html=True)


def render_score_bar(label, v):
    c = sc(v)
    st.markdown(f"""<div class="sbar">
        <span class="lbl">{esc(label)}</span>
        <div class="track"><div class="fill" style="width:{min(v, 100)}%;background:{c};"></div></div>
        <span class="num" style="color:{c};">{v:.0f}</span>
    </div>""", unsafe_allow_html=True)


def render_compare_card(label, value, other=None, other_name="", hero=False):
    sub = ""
    if other is not None:
        sub = (f'<div class="m-sub">{delta_html(value - other)}'
               f'<span>vs {esc(other_name)} {other:.1f}</span></div>')
    st.markdown(f'<div class="m-card{" hero" if hero else ""}"><div class="m-label">{esc(label)}</div>'
                f'<div class="m-value" style="color:{C["text"]};">{value:.1f}<small>/100</small></div>'
                f'{sub}</div>', unsafe_allow_html=True)


def _parse_email_parts(email_text: str) -> tuple[str, str]:
    """Extract subject and body from a generated email."""
    lines = email_text.strip().split("\n")
    subject = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
            body_start = i + 1
            break
    body = "\n".join(lines[body_start:]).strip()
    return subject, body


def _mail_links(subject: str, body: str) -> tuple[str, str]:
    """Build Gmail and Outlook compose URLs."""
    s = urllib.parse.quote(subject)
    b = urllib.parse.quote(body)
    gmail = f"https://mail.google.com/mail/?view=cm&su={s}&body={b}"
    outlook = f"https://outlook.live.com/mail/0/deeplink/compose?subject={s}&body={b}"
    return gmail, outlook


def email_card_html(email_text: str, meta_html: str = "", compact: bool = False) -> str:
    subject, body = _parse_email_parts(email_text)
    meta = f'<div class="mail-meta">{meta_html}</div>' if meta_html else ""
    subj = (f'<div class="mail-subject"><div class="lbl">Subject</div>'
            f'<div class="txt">{esc(subject)}</div></div>') if subject else ""
    return (f'<div class="mail-card">{meta}{subj}'
            f'<div class="mail-body{" compact" if compact else ""}">{esc(body)}</div></div>')


@st.cache_data
def load_scenarios():
    p = DATA_DIR / "scenarios.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def load_report():
    p = REPORTS_DIR / "evaluation_results.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def use_scenario(scenario):
    st.session_state.gen_intent = scenario["intent"]
    st.session_state.gen_facts = "\n".join(scenario["key_facts"])
    if scenario["tone"] in TONES:
        st.session_state.gen_tone = scenario["tone"]
    st.session_state.page = "Generate Email"


def clear_form():
    st.session_state.gen_intent = ""
    st.session_state.gen_facts = ""
    st.session_state.last_result = None


def restore_result(entry):
    st.session_state.last_result = entry


def _rgba(hex_color, alpha):
    return f"rgba({int(hex_color[1:3], 16)},{int(hex_color[3:5], 16)},{int(hex_color[5:7], 16)},{alpha})"


def _strategy_color(strat):
    return C["blue"] if strat == "advanced" else C["slate"] if strat == "baseline" else C["accent"]


_PLOT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=C["text2"], size=12),
    hoverlabel=dict(bgcolor=C["surface2"], bordercolor=C["border2"], font=dict(color=C["text"])),
)


def make_radar(metrics_a, metrics_b, names=("Advanced", "Baseline")):
    cats = list(metrics_a.keys())
    fig = go.Figure()
    series = [(metrics_a, names[0])] + ([(metrics_b, names[1])] if metrics_b else [])
    for vals, name in series:
        color = _strategy_color(name.lower())
        r = [vals.get(c, 0) for c in cats] + [vals.get(cats[0], 0)]
        fig.add_trace(go.Scatterpolar(
            r=r, theta=cats + [cats[0]], name=name,
            fill="toself", fillcolor=_rgba(color, 0.1),
            line=dict(color=color, width=2), marker=dict(size=5),
        ))
    fig.update_layout(
        **_PLOT_BASE,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10, color=C["text3"]),
                            gridcolor=C["border"], linecolor=C["border"]),
            angularaxis=dict(tickfont=dict(size=11, color=C["text2"]), gridcolor=C["border"],
                             linecolor=C["border"]),
        ),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        margin=dict(t=30, b=50, l=60, r=60),
        height=340,
    )
    return fig


def make_grouped_bar(summary):
    fig = go.Figure()
    for strat, vals in summary.items():
        metrics = [k for k in vals if k != "overall_average"]
        ys = [vals.get(m, 0) for m in metrics]
        fig.add_trace(go.Bar(
            name=strat.title(), x=metrics, y=ys,
            text=[f"{y:.0f}" for y in ys], textposition="outside",
            textfont=dict(size=11, color=C["text2"]),
            marker=dict(color=_strategy_color(strat), cornerradius=6),
            hovertemplate="%{x}<br>%{y:.1f}<extra>" + strat.title() + "</extra>",
        ))
    fig.update_layout(
        **_PLOT_BASE,
        barmode="group", bargap=0.35, bargroupgap=0.08,
        yaxis=dict(range=[0, 110], gridcolor=C["border"], zeroline=False,
                   title=dict(text="Score", font=dict(size=11, color=C["text3"]))),
        xaxis=dict(tickfont=dict(size=12, color=C["text2"])),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center"),
        margin=dict(t=20, b=50, l=50, r=20),
        height=340,
    )
    return fig


def make_scenario_bar(results):
    by_strat: dict[str, dict[int, float]] = {}
    for r in results:
        if not r["scores"]:
            continue
        avg = sum(s["score"] for s in r["scores"]) / len(r["scores"])
        by_strat.setdefault(r["strategy"], {})[r["scenario_id"]] = avg
    ids = sorted({sid for d in by_strat.values() for sid in d})
    fig = go.Figure()
    for strat, d in by_strat.items():
        fig.add_trace(go.Bar(
            name=strat.title(), x=[f"#{i}" for i in ids], y=[d.get(i) for i in ids],
            marker=dict(color=_strategy_color(strat), cornerradius=4),
            hovertemplate="Scenario %{x}<br>Avg %{y:.1f}<extra>" + strat.title() + "</extra>",
        ))
    fig.update_layout(
        **_PLOT_BASE,
        barmode="group", bargap=0.3,
        yaxis=dict(range=[0, 100], gridcolor=C["border"], zeroline=False),
        xaxis=dict(type="category", tickfont=dict(size=11, color=C["text2"])),
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        margin=dict(t=10, b=50, l=40, r=10),
        height=280,
    )
    return fig


# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="nav-brand">
        <div class="icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                 stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M22 4L12 13 2 4"/>
            </svg>
        </div>
        <div>
            <div class="title">MailCraft AI</div>
            <div class="sub">Email generation &amp; evaluation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section">Workspace</div>', unsafe_allow_html=True)
    page = st.radio("Navigation", list(PAGES), key="page", format_func=PAGES.get,
                    label_visibility="collapsed")

    st.markdown('<div class="nav-section" style="margin-top:1.6rem;">System</div>',
                unsafe_allow_html=True)

    try:
        from app.config import get_settings
        settings = get_settings()
        provider = settings.resolved_provider.upper()
        model = settings.get_model_name("primary")
        has_key = settings.has_valid_key
    except Exception:
        provider = "Not configured"
        model = "—"
        has_key = False

    key_color = C["green"] if has_key else C["red"]
    key_label = "Connected" if has_key else "No API key"

    st.markdown(f"""
    <div class="sys-card">
        <div class="sys-row"><span class="k">Status</span>
            <span class="v" style="color:{key_color};">
                <span style="display:inline-block;width:6px;height:6px;border-radius:50%;
                             background:{key_color};margin-right:0.4rem;vertical-align:middle;"></span>{key_label}
            </span></div>
        <div class="sys-row"><span class="k">Provider</span>
            <span class="v">{esc(provider)}</span></div>
        <div class="sys-row"><span class="k">Model</span>
            <span class="v" title="{esc(model)}">{esc(model)}</span></div>
        <div class="sys-feat">
            <div>CoT + few-shot + role-play prompting</div>
            <div>Self-reflection critic pass</div>
            <div>LLM-as-judge evaluation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================================
# PAGE : Generate Email
# =====================================================================
if page == "Generate Email":
    page_header("Compose", "Generate Email",
                "Produce a client-ready email from an intent, the facts it must contain, and a target tone.")

    col_form, col_preview = st.columns([5, 6], gap="large")

    with col_form:
        with st.container(border=True):
            head_l, head_r = st.columns([3, 2], vertical_alignment="center")
            with head_l:
                st.markdown(f'<div style="font-weight:600;font-size:0.92rem;color:{C["text"]};">'
                            f'Email brief</div>', unsafe_allow_html=True)
            with head_r:
                with st.popover("Load example", icon=":material/description:", width="stretch"):
                    st.caption("Start from a benchmark scenario")
                    for s in load_scenarios():
                        st.button(f"{s['intent']}", key=f"ex_{s['id']}", on_click=use_scenario,
                                  args=(s,), width="stretch", type="tertiary")

            intent = st.text_input("Intent", key="gen_intent",
                                   placeholder="e.g., Follow up after a product demo call")
            key_facts_text = st.text_area(
                "Key facts",
                key="gen_facts",
                placeholder="Demo was held last Tuesday\nClient liked the reporting feature\n"
                            "Next step is a pilot program",
                height=160,
                help="One fact per line. Every fact is checked for in the final email.",
            )
            key_facts = [f.strip() for f in key_facts_text.split("\n") if f.strip()]
            st.caption(f"{len(key_facts)} fact{'s' if len(key_facts) != 1 else ''} · one per line")

            tone = st.selectbox("Tone", TONES, key="gen_tone",
                                format_func=lambda t: t.replace("-", " ").title())
            strategy = st.segmented_control("Strategy", ["advanced", "baseline"], key="gen_strategy",
                                            format_func=str.title, required=True, width="stretch")
            st.caption(STRATEGY_INFO.get(strategy, ""))

            b1, b2 = st.columns([3, 1])
            with b1:
                gen_btn = st.button("Generate email", type="primary", icon=":material/send:",
                                    width="stretch")
            with b2:
                st.button("Clear", on_click=clear_form, width="stretch")

    with col_preview:
        if gen_btn and not (intent.strip() and key_facts):
            st.warning("Add an intent and at least one key fact first.", icon=":material/edit:")
        elif gen_btn:
            from app.config import get_settings as _get_s
            if not _get_s().has_valid_key:
                st.error("**No valid API key.** Add `OPENAI_API_KEY` or `GROQ_API_KEY` to `.env` and restart.",
                         icon=":material/key_off:")
            else:
                label = ("Drafting and running critic pass…" if strategy == "advanced"
                         else "Drafting email…")
                with st.spinner(label):
                    try:
                        from app.core.chains import STRATEGY_MAP
                        t0 = time.time()
                        result = run_async(STRATEGY_MAP[strategy](intent, key_facts, tone))
                        entry = {
                            "email": result.email,
                            "strategy": result.strategy,
                            "model_name": result.model_name,
                            "was_revised": result.was_revised,
                            "intent": intent,
                            "tone": tone,
                            "elapsed": time.time() - t0,
                        }
                        st.session_state.last_result = entry
                        st.session_state.history = ([entry] + st.session_state.history)[:10]
                    except Exception as e:
                        st.error(f"Generation failed: {e}", icon=":material/error:")

        res = st.session_state.last_result
        if res:
            subj, body = _parse_email_parts(res["email"])
            words = len(body.split())
            meta = (f'{badge_html(res["strategy"])}'
                    f'<span class="chip">{esc(res["model_name"])}</span>'
                    f'<span class="chip">{esc(res["tone"])}</span>'
                    + ('<span class="chip ok">Critic revised</span>' if res["was_revised"] else "")
                    + f'<span style="flex:1"></span>'
                    f'<span style="font-size:0.74rem;color:{C["text3"]};">'
                    f'{words} words · ~{max(1, round(words / 200))} min read · {res["elapsed"]:.1f}s</span>')
            st.markdown(email_card_html(res["email"], meta), unsafe_allow_html=True)

            gmail_url, outlook_url = _mail_links(subj, body)
            ext_icon = ('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                        '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
                        '<path d="M15 3h6v6"/><path d="M10 14L21 3"/></svg>')
            st.markdown(
                f'<div class="send-btns" style="margin-top:0.8rem;">'
                f'<a href="{gmail_url}" target="_blank" rel="noopener">Open in Gmail {ext_icon}</a>'
                f'<a href="{outlook_url}" target="_blank" rel="noopener">Open in Outlook {ext_icon}</a>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("")
            a1, a2 = st.columns([3, 2])
            with a1:
                with st.expander("Copy as plain text", icon=":material/content_copy:"):
                    st.code(res["email"], language=None, wrap_lines=True)
            with a2:
                st.download_button("Download .txt", res["email"], file_name="email.txt",
                                   mime="text/plain", icon=":material/download:", width="stretch")

            history = st.session_state.history
            if len(history) > 1:
                section_title("Recent generations", len(history))
                for i, h in enumerate(history):
                    active = h is res or h == res
                    label = f"{h['strategy'].title()} · {h['tone']} · {h['intent'][:48]}"
                    st.button(label, key=f"hist_{i}", on_click=restore_result, args=(h,),
                              width="stretch", icon=":material/history:", disabled=active)
        else:
            st.markdown(f"""
            <div class="mail-empty">
                <div class="ic">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{C['text2']}"
                         stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 4L12 13 2 4"/>
                    </svg>
                </div>
                <h4>No email generated yet</h4>
                <p>Complete the brief and select <b>Generate email</b>, or load a benchmark
                scenario to see an example.</p>
            </div>
            """, unsafe_allow_html=True)


# =====================================================================
# PAGE : Evaluation Dashboard
# =====================================================================
elif page == "Evaluation Dashboard":
    page_header("Benchmark", "Evaluation Dashboard",
                "Side-by-side comparison of prompting strategies on Fact Recall, Tone Alignment, "
                "and Professional Quality.")

    report = load_report()

    # ── action bar ──
    ab1, ab2, ab3 = st.columns([5, 1.4, 1.6], vertical_alignment="center")
    with ab1:
        if report:
            meta = report.get("metadata", {})
            ts = meta.get("generated_at", "")
            st.caption(f":material/schedule: Last run {ts[:16].replace('T', ' ')} UTC  ·  "
                       f"{meta.get('total_scenarios', 0)} scenarios  ·  "
                       f"{', '.join(meta.get('strategies_evaluated', []))}")
    with ab2:
        if report:
            csv_path = REPORTS_DIR / "evaluation_results.csv"
            with st.popover("Export", icon=":material/download:", width="stretch"):
                st.download_button("JSON results", json.dumps(report, indent=2), width="stretch",
                                   file_name="evaluation_results.json", mime="application/json")
                if csv_path.exists():
                    st.download_button("CSV results", csv_path.read_bytes(), width="stretch",
                                       file_name="evaluation_results.csv", mime="text/csv")
    with ab3:
        run_btn = st.button("Run evaluation", type="primary", icon=":material/play_arrow:",
                            width="stretch")

    # ── live evaluation runner ──
    if run_btn:
        from app.config import get_settings as _get_s
        _s = _get_s()
        if not _s.has_valid_key:
            st.error(
                f"**No valid API key configured.** Detected provider: `{_s.resolved_provider}`. "
                f"Add a valid `OPENAI_API_KEY` or `GROQ_API_KEY` to your `.env` file and restart.",
                icon=":material/key_off:",
            )
            st.stop()

        from app.evaluation.runner import evaluate_single_scenario, load_scenarios as _load_sc, _compute_summary
        from app.evaluation.report import save_json_report, save_csv_report, save_markdown_report
        from app.core.chains import STRATEGY_MAP

        scenarios = _load_sc()
        strategies = ["advanced", "baseline"]
        total = len(scenarios) * len(strategies)
        all_results = []

        progress = st.progress(0, text="Initializing evaluation pipeline…")
        section_title("Live results")
        st.markdown(f'<div style="display:flex;justify-content:flex-end;gap:0.4rem;padding:0 1rem;'
                    f'font-size:0.68rem;color:{C["text3"]};text-transform:uppercase;letter-spacing:0.05em;">'
                    f'<span style="width:34px;text-align:center;">Fact</span>'
                    f'<span style="width:34px;text-align:center;">Tone</span>'
                    f'<span style="width:34px;text-align:center;">Qual</span></div>',
                    unsafe_allow_html=True)
        live_container = st.container()

        completed = 0
        errors = 0
        start_t = time.time()

        for strat in strategies:
            if strat not in STRATEGY_MAP:
                continue
            for scenario in scenarios:
                sid = scenario["id"]
                elapsed = time.time() - start_t
                eta = (elapsed / completed) * (total - completed) if completed else 0
                eta_txt = f" · ~{eta:.0f}s remaining" if completed else ""
                progress.progress(completed / total,
                                  text=f"Scenario {sid} · {strat} · {completed}/{total}{eta_txt}")

                intent_txt = esc(scenario["intent"][:60])
                try:
                    result = run_async(evaluate_single_scenario(scenario, strat))
                    all_results.append(result)
                    sm = {s.metric_name: s.score for s in result.scores}
                    avg = sum(sm.values()) / len(sm) if sm else 0
                    scores_html = "".join(pill_html(sm.get(m, 0)) for m in METRICS)
                    dot = sc(avg)
                except Exception:
                    errors += 1
                    scores_html = (f'<span class="feed-pill" style="background:{C["red_bg"]};'
                                   f'color:{C["red"]};">ERR</span>')
                    dot = C["red"]

                with live_container:
                    st.markdown(
                        f'<div class="feed-row"><div class="feed-dot" style="background:{dot};"></div>'
                        f'<div class="feed-info">{badge_html(strat)}&nbsp;&nbsp;'
                        f'<span style="color:{C["text3"]};">#{sid}</span>&nbsp; {intent_txt}</div>'
                        f'<div class="feed-scores">{scores_html}</div></div>',
                        unsafe_allow_html=True,
                    )

                completed += 1
                time.sleep(0.3)

        elapsed = time.time() - start_t
        err_msg = f" · {errors} errors" if errors else ""
        progress.progress(1.0, text=f"Completed {completed} runs in {elapsed:.0f}s{err_msg}")

        if all_results:
            summary = _compute_summary(all_results)
            save_json_report(all_results, summary)
            save_csv_report(all_results)
            save_markdown_report(all_results, summary)
            st.toast("Evaluation complete. Reports saved.", icon=":material/check_circle:")
            time.sleep(1)
            st.rerun()

    # ── results dashboard ──
    if report and not run_btn:
        summary = report.get("summary", {})
        results = report.get("results", [])
        strategies = sorted(summary, key=lambda s: (s != "advanced", s))

        if strategies:
            primary = strategies[0]
            other = strategies[1] if len(strategies) > 1 else None
            pm = summary[primary]
            om = summary[other] if other else {}
            metric_keys = [k for k in pm if k != "overall_average"]

            if other:
                d = pm.get("overall_average", 0) - om.get("overall_average", 0)
                leader, trailer = (primary, other) if d >= 0 else (other, primary)
                st.markdown(
                    f'<div class="winner-banner"><span class="tag">Summary</span>'
                    f'<div><b>{esc(leader.title())}</b> outperforms <b>{esc(trailer.title())}</b> by '
                    f'<b>{abs(d):.1f} points</b> on the overall average across '
                    f'{len(metric_keys)} metrics.</div></div>',
                    unsafe_allow_html=True,
                )

            cards = st.columns(len(metric_keys) + 1)
            with cards[0]:
                render_compare_card(f"{primary.title()} · Overall", pm.get("overall_average", 0),
                                    om.get("overall_average") if other else None,
                                    other.title() if other else "", hero=True)
            for i, k in enumerate(metric_keys, start=1):
                with cards[i]:
                    render_compare_card(k, pm.get(k, 0), om.get(k) if other else None,
                                        other.title() if other else "")

            # ── charts ──
            ch1, ch2 = st.columns(2, gap="large")
            with ch1:
                section_title("Strategy comparison")
                st.plotly_chart(make_grouped_bar({s: summary[s] for s in strategies}),
                                width="stretch", config={"displayModeBar": False})
            with ch2:
                section_title("Metric radar")
                m1 = {k: v for k, v in pm.items() if k != "overall_average"}
                m2 = {k: v for k, v in om.items() if k != "overall_average"} if other else None
                st.plotly_chart(make_radar(m1, m2, (primary.title(), other.title() if other else "")),
                                width="stretch", config={"displayModeBar": False})

            if results:
                section_title("Average score per scenario")
                st.plotly_chart(make_scenario_bar(results), width="stretch",
                                config={"displayModeBar": False})

        # ── metric definitions ──
        defs = report.get("metric_definitions", [])
        if defs:
            section_title("How metrics are scored")
            dc = st.columns(len(defs))
            for i, d in enumerate(defs):
                with dc[i]:
                    st.markdown(f'<div class="info-card"><div class="ic-title">{esc(d["name"])}</div>'
                                f'<div class="ic-desc">{esc(d["description"])}</div>'
                                f'<div class="ic-desc" style="margin-top:0.5rem;color:{C["text2"]};">'
                                f'{esc(d.get("scoring", ""))}</div></div>',
                                unsafe_allow_html=True)

        # ── scenario breakdown ──
        section_title("Scenario breakdown", len(results))
        f1, f2, _ = st.columns([1.3, 1.3, 3])
        with f1:
            filt = st.selectbox("Strategy", ["All strategies"] + strategies, key="ef",
                                label_visibility="collapsed")
        with f2:
            sort = st.selectbox("Sort", ["Scenario order", "Lowest score first", "Highest score first"],
                                key="es", label_visibility="collapsed")

        def _avg(r):
            return sum(s["score"] for s in r["scores"]) / len(r["scores"]) if r["scores"] else 0

        filtered = [r for r in results if filt == "All strategies" or r["strategy"] == filt]
        if sort == "Lowest score first":
            filtered.sort(key=_avg)
        elif sort == "Highest score first":
            filtered.sort(key=_avg, reverse=True)

        for r in filtered:
            avg = _avg(r)
            with st.expander(f"#{r['scenario_id']}  ·  {r['strategy'].title()}  ·  "
                             f"{r['intent'][:60]}  ·  Score {avg:.0f}"):
                mc1, mc2 = st.columns([2, 3], gap="large")
                with mc1:
                    st.markdown(f'{badge_html(r["strategy"])} <span class="chip">{esc(r["model_name"])}</span> '
                                f'<span class="chip">{esc(r["tone"])}</span>', unsafe_allow_html=True)
                    st.markdown("")
                    for s in r["scores"]:
                        render_score_bar(s["metric_name"], s["score"])
                        if s.get("details"):
                            st.caption(s["details"])
                with mc2:
                    st.markdown(email_card_html(r["generated_email"], compact=True),
                                unsafe_allow_html=True)

    # ── empty state (no report, not running) ──
    elif not run_btn:
        c1, c2, c3 = st.columns(3)
        cards = [
            ("Fact Recall", "LLM-as-Judge per-fact verification with sentence-transformer "
                            "semantic similarity fallback."),
            ("Tone Alignment", "LLM-as-Judge tone rating (80%) combined with VADER sentiment "
                               "analysis sanity check (20%)."),
            ("Professional Quality", "Composite: readability (Flesch), conciseness, structure "
                                     "detection, and LLM grammar judge."),
        ]
        for col, (title, desc) in zip((c1, c2, c3), cards):
            with col:
                st.markdown(f'<div class="info-card"><div class="ic-title">{title}</div>'
                            f'<div class="ic-desc">{desc}</div></div>', unsafe_allow_html=True)

        n_sc = len(load_scenarios())
        st.markdown(f"""
        <div class="empty-state">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{C['text3']}"
                 stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>
            </svg>
            <h3>No evaluation results</h3>
            <p>Select <b>Run evaluation</b> to benchmark both strategies.<br/>
            {n_sc * 2} runs ({n_sc} scenarios × 2 strategies) are scored on 3 metrics.</p>
        </div>
        """, unsafe_allow_html=True)


# =====================================================================
# PAGE : Test Scenarios
# =====================================================================
elif page == "Test Scenarios":
    scenarios = load_scenarios()
    page_header("Dataset", "Test Scenarios",
                f"{len(scenarios)} benchmark scenarios, each with a hand-written reference email "
                f"used as the evaluation baseline.")

    if not scenarios:
        st.warning("No scenarios found in data/scenarios.json.")
    else:
        f1, f2 = st.columns([3, 1.3])
        with f1:
            query = st.text_input("Search", placeholder="Search intents and facts…",
                                  icon=":material/search:", label_visibility="collapsed")
        with f2:
            tones = sorted({s["tone"] for s in scenarios})
            tone_f = st.selectbox("Tone", ["All tones"] + tones, label_visibility="collapsed")

        q = query.strip().lower()
        shown = [
            s for s in scenarios
            if (tone_f == "All tones" or s["tone"] == tone_f)
            and (not q or q in s["intent"].lower() or any(q in f.lower() for f in s["key_facts"]))
        ]
        st.caption(f"Showing {len(shown)} of {len(scenarios)} scenarios")

        for s in shown:
            with st.container(border=True):
                st.markdown(f'<div class="sc-header"><div class="sc-num">{s["id"]}</div>'
                            f'<div class="sc-title">{esc(s["intent"])}</div>'
                            f'<div class="sc-tone">{esc(s["tone"])}</div></div>',
                            unsafe_allow_html=True)
                c1, c2 = st.columns([2, 3], gap="large")
                with c1:
                    facts = "".join(f"<li>{esc(f)}</li>" for f in s["key_facts"])
                    st.markdown(f'<div class="sub-label">Key facts</div><ul class="fact-list">{facts}</ul>',
                                unsafe_allow_html=True)
                    st.markdown("")
                    st.button("Use in generator", key=f"use_{s['id']}", on_click=use_scenario,
                              args=(s,), icon=":material/arrow_forward:")
                with c2:
                    with st.expander("Reference email", icon=":material/mail:"):
                        st.markdown(email_card_html(s["reference_email"], compact=True),
                                    unsafe_allow_html=True)

        if not shown:
            st.info("No scenarios match your filters.", icon=":material/filter_alt_off:")
