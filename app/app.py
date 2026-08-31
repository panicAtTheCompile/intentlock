import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from simulator.models import UserIntent
from simulator.attacks import (
    merchant_substitution_attack,
    subtle_intent_drift_attack,
    scope_expansion_attack,
    stealth_scope_expansion_attack
)
from blue_team.features import extract_features

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IntentLock — Autonomous Payment Security",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# THEME — dark vault / ledger aesthetic
# Palette: near-black base, brass/gold linework, deep emerald
# for cleared funds, oxblood for stopped funds. Serif (Fraunces)
# for figures and headings, mono (IBM Plex Mono) for ledger data.
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #0a0d0b;
    --bg-vault: #0e1310;
    --surface: #121714;
    --surface-raised: #161c18;
    --line: rgba(201, 169, 97, 0.16);
    --line-strong: rgba(201, 169, 97, 0.4);
    --gold: #c9a961;
    --gold-bright: #e3c988;
    --emerald: #3a7d5c;
    --emerald-bright: #5fae85;
    --oxblood: #9c4a42;
    --oxblood-bright: #cf6e5e;
    --ink: #e9e5d8;
    --ink-dim: #9aa39a;
    --ink-faint: #5d655f;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--ink);
}

.stApp {
    background-color: var(--bg);
    background-image:
        radial-gradient(ellipse 900px 500px at 15% -5%, rgba(201,169,97,0.07), transparent 60%),
        radial-gradient(ellipse 700px 500px at 100% 10%, rgba(58,125,92,0.08), transparent 55%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cg fill='none' stroke='%23c9a961' stroke-width='0.5' opacity='0.05'%3E%3Cpath d='M0 110 Q55 20 110 110 T220 110'/%3E%3Cpath d='M0 110 Q55 200 110 110 T220 110'/%3E%3Ccircle cx='110' cy='110' r='60'/%3E%3C/g%3E%3C/svg%3E");
    background-attachment: fixed;
    color: var(--ink);
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    max-width: 1360px;
}

/* ---------------- Header ---------------- */

.vault-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 0 0 18px 0;
    margin-bottom: 28px;
    border-bottom: 1px solid var(--line);
}

.vault-wordmark {
    font-family: 'Fraunces', serif;
    font-size: 27px;
    font-weight: 600;
    color: var(--ink);
    letter-spacing: 0.2px;
}

.vault-wordmark span {
    color: var(--gold-bright);
}

.vault-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--ink-faint);
    margin-left: 12px;
    letter-spacing: 0.3px;
}

.vault-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11.5px;
    color: var(--ink-dim);
    letter-spacing: 0.4px;
}

.pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--emerald-bright);
    box-shadow: 0 0 0 0 rgba(95, 174, 133, 0.6);
    animation: pulse 2.4s infinite;
}

@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(95, 174, 133, 0.55); }
    70%  { box-shadow: 0 0 0 7px rgba(95, 174, 133, 0); }
    100% { box-shadow: 0 0 0 0 rgba(95, 174, 133, 0); }
}

/* ---------------- Cards (ledger sheets) ---------------- */

.ledger-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 3px;
    padding: 22px 24px;
    margin-bottom: 18px;
    position: relative;
}

.ledger-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 14px; height: 14px;
    border-top: 1px solid var(--line-strong);
    border-left: 1px solid var(--line-strong);
}

.ledger-card::after {
    content: "";
    position: absolute;
    bottom: 0; right: 0;
    width: 14px; height: 14px;
    border-bottom: 1px solid var(--line-strong);
    border-right: 1px solid var(--line-strong);
}

.ledger-heading {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10.5px;
    font-weight: 600;
    color: var(--gold);
    letter-spacing: 1.4px;
    text-transform: uppercase;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--line);
}

.field-label {
    font-size: 10.5px;
    color: var(--ink-faint);
    letter-spacing: 0.6px;
    margin-bottom: 3px;
}

.field-value {
    font-family: 'Fraunces', serif;
    font-size: 17px;
    font-weight: 500;
    color: var(--ink);
}

.field-value.small {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 14px;
    font-weight: 500;
}

/* ---------------- Execution trace ---------------- */

.trace-row {
    display: flex;
    gap: 14px;
    padding: 11px 0;
    border-bottom: 1px solid var(--line);
}

.trace-row:last-child { border-bottom: none; }

.trace-index {
    font-family: 'Fraunces', serif;
    font-size: 15px;
    color: var(--gold-bright);
    width: 20px;
    flex-shrink: 0;
    padding-top: 1px;
}

.trace-action {
    font-size: 13px;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 2px;
}

.trace-detail {
    font-size: 12px;
    color: var(--ink-dim);
    line-height: 1.5;
}

/* ---------------- Verdict banners ---------------- */

.verdict {
    padding: 14px 18px;
    border-radius: 2px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.3px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.verdict-mark {
    font-family: 'Fraunces', serif;
    font-size: 16px;
    line-height: 1;
}

.verdict.blocked {
    background: rgba(156, 74, 66, 0.12);
    border: 1px solid rgba(156, 74, 66, 0.4);
    color: var(--oxblood-bright);
}

.verdict.approved {
    background: rgba(58, 125, 92, 0.12);
    border: 1px solid rgba(58, 125, 92, 0.4);
    color: var(--emerald-bright);
}

/* ---------------- Risk dial ---------------- */

.risk-figure {
    border: 1px solid var(--line);
    border-radius: 3px;
    padding: 14px 10px;
    text-align: center;
    background: var(--bg-vault);
}

.risk-number {
    font-family: 'Fraunces', serif;
    font-size: 34px;
    font-weight: 600;
    line-height: 1;
}

.risk-caption {
    font-size: 9.5px;
    color: var(--ink-faint);
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-top: 6px;
}

/* ---------------- Idle state ---------------- */

.idle-card {
    text-align: center;
    padding: 64px 20px;
}

.idle-mark {
    font-family: 'Fraunces', serif;
    font-size: 15px;
    color: var(--gold-bright);
    letter-spacing: 0.4px;
    margin-bottom: 10px;
}

.idle-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 6px;
}

.idle-text {
    color: var(--ink-dim);
    font-size: 12.5px;
    max-width: 380px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ---------------- Sidebar ---------------- */

section[data-testid="stSidebar"] {
    background: var(--bg-vault);
    border-right: 1px solid var(--line);
}

section[data-testid="stSidebar"] h2 {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--gold);
    font-size: 11.5px;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    font-weight: 600;
}

section[data-testid="stSidebar"] label {
    color: var(--ink-dim) !important;
    font-size: 12px !important;
}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stNumberInput input,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    color: var(--ink) !important;
}

.stButton > button {
    width: 100%;
    border-radius: 2px;
    height: 42px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 12.5px;
    letter-spacing: 0.6px;
    border: 1px solid var(--line-strong);
    background: linear-gradient(180deg, #1a211c, #12172d 400%);
    background: var(--surface-raised);
    color: var(--gold-bright);
    transition: border-color 0.15s ease, color 0.15s ease;
}

.stButton > button:hover {
    border-color: var(--gold);
    color: var(--gold-bright);
    background: #1a211c;
}

.sidebar-note {
    color: var(--ink-faint);
    font-size: 11px;
    line-height: 1.5;
    margin-top: 10px;
}

[data-testid="stDataFrame"] { border: 1px solid var(--line); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="vault-header">
    <div>
        <span class="vault-wordmark">Intent<span>Lock</span></span>
        <span class="vault-sub">core gateway engine</span>
    </div>
    <div class="vault-status">
        <span class="pulse-dot"></span> GATEWAY SECURE
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================

with st.sidebar:
    st.markdown("## Transaction Parameters")

    merchant = st.text_input("Target merchant", "Amazon")
    item = st.text_input("Requested item", "Wireless Headphones")
    max_amount = st.number_input("Authorized limit (₹)", min_value=100, max_value=100000, value=5000, step=100)

    attack_name = st.selectbox(
        "Agent attack vector",
        [
            "Merchant Substitution",
            "Subtle Intent Drift",
            "Scope Expansion",
            "Stealth Scope Expansion"
        ]
    )

    st.markdown("---")
    run_attack = st.button("Simulate transaction")
    st.markdown('<div class="sidebar-note">Sandbox environment. Every run is scored against behavioral guardrails before settlement.</div>', unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "transaction" not in st.session_state:
    st.markdown("""
    <div class="ledger-card idle-card">
        <div class="idle-mark">◆</div>
        <div class="idle-title">Gateway idle</div>
        <div class="idle-text">Set the transaction parameters in the sidebar, choose an attack vector, and run a simulation to see the ledger populate.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============================================================
# LOAD TRANSACTION DATA
# ============================================================

transaction = st.session_state.transaction
intent = st.session_state.intent
features = st.session_state.features
payment = transaction.payment

# ============================================================
# MAIN DASHBOARD LAYOUT
# ============================================================

col_left, col_right = st.columns([1.1, 1], gap="medium")

with col_left:
    # 01. User Intent Vector Card
    st.markdown('<div class="ledger-card"><div class="ledger-heading">Intent Parameters</div>', unsafe_allow_html=True)

    i_col1, i_col2, i_col3 = st.columns(3)
    with i_col1:
        st.markdown(f"<div class='field-label'>MERCHANT</div><div class='field-value'>{intent.merchant}</div>", unsafe_allow_html=True)
    with i_col2:
        st.markdown(f"<div class='field-label'>ITEM</div><div class='field-value'>{intent.item}</div>", unsafe_allow_html=True)
    with i_col3:
        st.markdown(f"<div class='field-label'>MAX LIMIT</div><div class='field-value'>₹{intent.max_amount:,.0f}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 02. Agent Execution Trace
    st.markdown('<div class="ledger-card"><div class="ledger-heading">Agent Execution Sequence</div>', unsafe_allow_html=True)

    for i, action in enumerate(payment.actions, start=1):
        st.markdown(f"""
        <div class="trace-row">
            <div class="trace-index">{i:02d}</div>
            <div>
                <div class="trace-action">{action.action}</div>
                <div class="trace-detail">{action.details}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    # 03. Final Payment Payload Card
    st.markdown('<div class="ledger-card"><div class="ledger-heading">Settlement Payload</div>', unsafe_allow_html=True)

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown(f"<div class='field-label'>BILLED MERCHANT</div><div class='field-value small'>{payment.merchant}</div>", unsafe_allow_html=True)
        recurring_color = "var(--oxblood-bright)" if payment.recurring else "var(--emerald-bright)"
        st.markdown(f"<div class='field-label' style='margin-top:14px;'>RECURRING BILLING</div><div class='field-value small' style='color:{recurring_color};'>{'YES' if payment.recurring else 'NO'}</div>", unsafe_allow_html=True)
    with p_col2:
        st.markdown(f"<div class='field-label'>BILLED AMOUNT</div><div class='field-value small'>₹{payment.amount:,.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='field-label' style='margin-top:14px;'>STATUS</div><div class='field-value small' style='color: var(--gold-bright);'>PENDING GATEWAY</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 04. Behavioral Analysis Matrix
    st.markdown('<div class="ledger-card"><div class="ledger-heading">Behavioral Signal Telemetry</div>', unsafe_allow_html=True)

    feature_df = pd.DataFrame({
        "Feature Metric": list(features.keys()),
        "Telemetry Value": list(features.values())
    })
    st.dataframe(feature_df, hide_index=True, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 05. Risk Scoring & Decision
    risk = 0
    if features["merchant_match"] == 0: risk += 30
    if features["amount_ratio"] > 1: risk += 30
    if features["recurring_mismatch"] == 1: risk += 20
    if features["authorization_without_confirmation"] == 1: risk += 10
    risk += min(features["unusual_action_count"] * 5, 20)
    risk = min(risk, 100)

    st.markdown('<div class="ledger-card"><div class="ledger-heading">Gateway Risk Evaluation</div>', unsafe_allow_html=True)

    r_col1, r_col2 = st.columns([1, 2])
    with r_col1:
        risk_color = "var(--oxblood-bright)" if risk >= 50 else "var(--emerald-bright)"
        st.markdown(f"""
        <div class="risk-figure">
            <div class="risk-number" style="color: {risk_color};">{risk}</div>
            <div class="risk-caption">Risk Index</div>
        </div>
        """, unsafe_allow_html=True)

    with r_col2:
        if risk >= 50:
            st.markdown("""
            <div class="verdict blocked">
                <span class="verdict-mark">✕</span> TRANSACTION BLOCKED — policy deviation detected
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="verdict approved">
                <span class="verdict-mark">✓</span> TRANSACTION APPROVED — intent match validated
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# EVENT HANDLER: RUN SIMULATION
# ============================================================

if run_attack:
    intent_obj = UserIntent(
        merchant=merchant,
        item=item,
        max_amount=max_amount,
        currency="INR",
        allow_subscription=False
    )

    attacks_map = {
        "Merchant Substitution": merchant_substitution_attack,
        "Subtle Intent Drift": subtle_intent_drift_attack,
        "Scope Expansion": scope_expansion_attack,
        "Stealth Scope Expansion": stealth_scope_expansion_attack
    }

    transaction_res = attacks_map[attack_name](intent_obj)
    extracted_features = extract_features(transaction_res)

    st.session_state.transaction = transaction_res
    st.session_state.intent = intent_obj
    st.session_state.features = extracted_features

    st.rerun()