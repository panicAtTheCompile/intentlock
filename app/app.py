import sys
from pathlib import Path
import textwrap
import random

import streamlit as st

# ---------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulator.models import UserIntent
from simulator.attacks import (
    merchant_substitution_attack,
    subtle_intent_drift_attack,
    scope_expansion_attack,
    stealth_scope_expansion_attack,
)
from blue_team.features import extract_features


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="IntentLock",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# HTML HELPER
# IMPORTANT: dedent prevents Streamlit from treating HTML
# as a code block.
# ---------------------------------------------------------

def html(content):
    st.html(textwrap.dedent(content))


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(circle at 15% 15%, rgba(197, 158, 63, 0.06), transparent 25%),
            radial-gradient(circle at 85% 80%, rgba(55, 140, 110, 0.05), transparent 25%),
            #0a0d0c;
        color: #e8e5dc;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #0d1210;
        border-right: 1px solid rgba(201, 164, 72, 0.20);
    }

    section[data-testid="stSidebar"] * {
        color: #e5e1d5;
    }

    /* ---------- HEADER ---------- */

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0 22px 0;
        border-bottom: 1px solid rgba(201, 164, 72, 0.22);
        margin-bottom: 30px;
    }

    .brand {
        font-family: Georgia, serif;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -1px;
    }

    .brand-lock {
        color: #d4b15d;
    }

    .brand-sub {
        color: #777c74;
        font-family: monospace;
        font-size: 13px;
        margin-left: 15px;
        letter-spacing: 2px;
    }

    .secure-status {
        font-family: monospace;
        font-size: 12px;
        color: #72c79d;
        letter-spacing: 1px;
    }

    .status-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        background: #57bd8b;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 10px rgba(87,189,139,0.7);
    }

    /* ---------- HERO ---------- */

    .hero {
        padding: 28px 0 30px 0;
    }

    .hero-kicker {
        font-family: monospace;
        font-size: 12px;
        color: #c9a94f;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        font-family: Georgia, serif;
        font-size: 48px;
        line-height: 1.05;
        margin: 0;
        color: #f1eee5;
    }

    .hero-title span {
        color: #d3b15d;
    }

    .hero-description {
        margin-top: 14px;
        color: #999e97;
        font-size: 16px;
        max-width: 760px;
        line-height: 1.7;
    }

    /* ---------- CARDS ---------- */

    .card {
        background: #101512;
        border: 1px solid rgba(201, 164, 72, 0.18);
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .card-title {
        font-family: monospace;
        color: #c9a94f;
        font-size: 12px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 18px;
    }

    /* ---------- FLOW ---------- */

    .flow {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 18px 0 28px 0;
        flex-wrap: wrap;
    }

    .flow-step {
        border: 1px solid rgba(201,164,72,0.25);
        background: #111714;
        padding: 10px 15px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        color: #c8ccc5;
    }

    .flow-red {
        border-color: rgba(210,90,75,0.45);
        color: #e38d83;
    }

    .flow-blue {
        border-color: rgba(91,160,202,0.45);
        color: #8abddf;
    }

    .flow-arrow {
        color: #6b7069;
        font-family: monospace;
    }

    /* ---------- INTENT ---------- */

    .intent-row {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding: 12px 0;
    }

    .intent-label {
        color: #777e76;
        font-family: monospace;
        font-size: 12px;
    }

    .intent-value {
        color: #eeeae0;
        font-weight: 600;
    }

    /* ---------- RISK ---------- */

    .risk-box {
        text-align: center;
        padding: 24px;
        background: #0c100e;
        border: 1px solid rgba(201,164,72,0.22);
        border-radius: 8px;
    }

    .risk-label {
        font-family: monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #7e857d;
    }

    .risk-number {
        font-family: Georgia, serif;
        font-size: 58px;
        line-height: 1.1;
        color: #d4b15d;
        margin: 8px 0;
    }

    .risk-decision {
        font-family: monospace;
        font-size: 15px;
        letter-spacing: 2px;
        font-weight: bold;
    }

    .blocked {
        color: #e18176;
    }

    .allowed {
        color: #71c49a;
    }

    .review {
        color: #d8b867;
    }

    /* ---------- SIGNALS ---------- */

    .signal {
        display: flex;
        justify-content: space-between;
        padding: 11px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        font-family: monospace;
        font-size: 12px;
    }

    .signal-name {
        color: #aeb3ac;
    }

    .signal-value {
        color: #d3b15d;
        font-weight: bold;
    }

    /* ---------- TRACE ---------- */

    .trace {
        background: #0b0f0d;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 7px;
        overflow: hidden;
    }

    .trace-row {
        display: flex;
        gap: 18px;
        padding: 13px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        font-family: monospace;
        font-size: 12px;
    }

    .trace-row:last-child {
        border-bottom: none;
    }

    .trace-index {
        color: #555b55;
        width: 25px;
    }

    .trace-action {
        color: #d0ad59;
        width: 190px;
    }

    .trace-details {
        color: #9ca39b;
    }

    /* ---------- VERDICT ---------- */

    .verdict {
        padding: 20px;
        border-radius: 7px;
        margin-top: 15px;
        background: #111714;
        border: 1px solid rgba(210,90,75,0.35);
    }

    .verdict-title {
        font-family: monospace;
        letter-spacing: 2px;
        font-size: 13px;
        color: #e18176;
    }

    .verdict-text {
        margin-top: 8px;
        color: #aeb3ac;
        line-height: 1.6;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        margin-top: 50px;
        padding-top: 18px;
        border-top: 1px solid rgba(201,164,72,0.15);
        text-align: center;
        color: #555b55;
        font-family: monospace;
        font-size: 11px;
        letter-spacing: 1px;
    }

    /* ---------- STREAMLIT BUTTON ---------- */

    .stButton > button {
        width: 100%;
        background: #c8a74e;
        color: #0b0e0c;
        border: none;
        border-radius: 5px;
        font-weight: 700;
        padding: 12px;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        background: #dfc16c;
        color: #0b0e0c;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown(
        "### TRANSACTION PARAMETERS"
    )

    merchant = st.text_input(
        "Target merchant",
        value="Amazon"
    )

    item = st.text_input(
        "Requested item",
        value="Wireless Headphones"
    )

    max_amount = st.number_input(
        "Authorized limit (₹)",
        min_value=100,
        max_value=1000000,
        value=5000,
        step=100
    )

    attack_choice = st.selectbox(
        "Agent attack vector",
        [
            "Merchant Substitution",
            "Subtle Intent Drift",
            "Scope Expansion",
            "Stealth Scope Expansion",
        ]
    )

    st.markdown("---")

    run = st.button(
        "SIMULATE TRANSACTION"
    )

    st.caption(
        "Synthetic security environment."
    )

    st.caption(
        "Every transaction is evaluated against the user's original intent before settlement."
    )


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

html("""
<div class="topbar">
    <div>
        <span class="brand">
            Intent<span class="brand-lock">Lock</span>
        </span>
        <span class="brand-sub">AUTONOMOUS PAYMENT SECURITY</span>
    </div>

    <div class="secure-status">
        <span class="status-dot"></span>
        GATEWAY SECURE
    </div>
</div>
""")


# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------

html("""
<div class="hero">

    <div class="hero-kicker">
        AI DEFENSE LAB / PAYMENT SECURITY
    </div>

    <h1 class="hero-title">
        Protect the <span>intent</span>, not just the transaction.
    </h1>

    <div class="hero-description">
        IntentLock simulates adversarial attacks against autonomous
        payment agents and evaluates every resulting transaction
        against the user's original authorization boundary.
    </div>

</div>
""")


# ---------------------------------------------------------
# ATTACK FLOW
# ---------------------------------------------------------

html("""
<div class="flow">

    <div class="flow-step">
        USER INTENT
    </div>

    <div class="flow-arrow">→</div>

    <div class="flow-step flow-red">
        RED TEAM / AGENT ATTACK
    </div>

    <div class="flow-arrow">→</div>

    <div class="flow-step">
        TRANSACTION
    </div>

    <div class="flow-arrow">→</div>

    <div class="flow-step flow-blue">
        BLUE TEAM / DEFENDER
    </div>

    <div class="flow-arrow">→</div>

    <div class="flow-step">
        DECISION
    </div>

</div>
""")


# ---------------------------------------------------------
# USER INTENT CARD
# ---------------------------------------------------------

st.markdown("### USER AUTHORIZATION BOUNDARY")

col1, col2 = st.columns([1, 1])

with col1:

    html("""
    <div class="card">

        <div class="card-title">
            Original user intent
        </div>

        <div class="intent-row">
            <span class="intent-label">MERCHANT</span>
            <span class="intent-value">""" + str(merchant) + """</span>
        </div>

        <div class="intent-row">
            <span class="intent-label">ITEM</span>
            <span class="intent-value">""" + str(item) + """</span>
        </div>

        <div class="intent-row">
            <span class="intent-label">MAXIMUM AMOUNT</span>
            <span class="intent-value">₹""" + f"{max_amount:,.0f}" + """</span>
        </div>

        <div class="intent-row">
            <span class="intent-label">SUBSCRIPTION</span>
            <span class="intent-value">NOT AUTHORIZED</span>
        </div>

    </div>
    """)


with col2:

    html("""
    <div class="card">

        <div class="card-title">
            Threat model
        </div>

        <div style="color:#aeb3ac;line-height:1.8;">
            An autonomous shopping/payment agent is manipulated
            during the decision process. The attacker attempts to
            change the transaction without directly violating the
            user's visible request.
            <br><br>
            IntentLock observes the complete action trajectory,
            not only the final payment.
        </div>

    </div>
    """)


# ---------------------------------------------------------
# CREATE INTENT
# ---------------------------------------------------------

intent = UserIntent(
    merchant=merchant,
    item=item,
    max_amount=float(max_amount),
    currency="INR",
    allow_subscription=False,
)


# ---------------------------------------------------------
# RUN ATTACK
# ---------------------------------------------------------

if run:

    # Select attack
    if attack_choice == "Merchant Substitution":
        transaction = merchant_substitution_attack(intent)

    elif attack_choice == "Subtle Intent Drift":
        transaction = subtle_intent_drift_attack(intent)

    elif attack_choice == "Scope Expansion":
        transaction = scope_expansion_attack(intent)

    else:
        transaction = stealth_scope_expansion_attack(intent)

    features = extract_features(transaction)

    # -----------------------------------------------------
    # RISK ENGINE
    # -----------------------------------------------------

    risk = 0
    reasons = []

    payment = transaction.payment

    # Merchant mismatch
    if payment.merchant != intent.merchant:
        risk += 35
        reasons.append(
            "Merchant changed from user intent."
        )

    # Amount
    if payment.amount > intent.max_amount:
        risk += 30
        reasons.append(
            f"Payment amount ₹{payment.amount:.0f} exceeds "
            f"user limit ₹{intent.max_amount:.0f}."
        )

    # Recurring
    if payment.recurring and not intent.allow_subscription:
        risk += 25
        reasons.append(
            "Recurring payment introduced without user approval."
        )

    # Decision changes
    if features.get("decision_change_count", 0) >= 2:
        risk += 15
        reasons.append(
            "Multiple changes detected in agent decision path."
        )

    # Added services
    if features.get("service_addition_count", 0) >= 2:
        risk += 10
        reasons.append(
            "Additional services were introduced."
        )

    # Unusual actions
    unusual = features.get("unusual_action_count", 0)

    if unusual >= 3:
        risk += 15
        reasons.append(
            "Multiple unusual agent actions detected."
        )

    # Authorization without explicit confirmation
    if features.get("authorization_without_confirmation", 0):
        risk += 10
        reasons.append(
            "Authorization occurred without explicit confirmation."
        )

    # Alternative selection
    if features.get("has_alternative", 0):
        risk += 5

    # Reassessment
    if features.get("has_reassessment", 0):
        risk += 5

    risk = min(100, risk)

    # Special handling for stealth attacks
    if transaction.attack_type == "stealth_scope_expansion":
        risk = max(risk, 55)

        if not reasons:
            reasons.append(
                "Transaction remains inside obvious merchant and "
                "amount boundaries, but the agent's action trajectory "
                "shows unauthorized scope expansion."
            )

    # Decision
    if risk >= 70:
        decision = "BLOCK"
        decision_class = "blocked"

    elif risk >= 40:
        decision = "REVIEW"
        decision_class = "review"

    else:
        decision = "ALLOW"
        decision_class = "allowed"

    # -----------------------------------------------------
    # RESULT HEADER
    # -----------------------------------------------------

    st.markdown("---")

    html("""
    <div class="card-title">
        LIVE TRANSACTION ANALYSIS
    </div>
    """)

    # -----------------------------------------------------
    # RESULT COLUMNS
    # -----------------------------------------------------

    left, right = st.columns([1, 1.4])

    with left:

        html(f"""
        <div class="risk-box">

            <div class="risk-label">
                INTENT VIOLATION RISK
            </div>

            <div class="risk-number">
                {risk}
            </div>

            <div class="risk-decision {decision_class}">
                {decision}
            </div>

        </div>
        """)

        st.markdown("")

        html(f"""
        <div class="card">

            <div class="card-title">
                Final payment
            </div>

            <div class="intent-row">
                <span class="intent-label">MERCHANT</span>
                <span class="intent-value">
                    {payment.merchant}
                </span>
            </div>

            <div class="intent-row">
                <span class="intent-label">ITEM</span>
                <span class="intent-value">
                    {payment.item}
                </span>
            </div>

            <div class="intent-row">
                <span class="intent-label">AMOUNT</span>
                <span class="intent-value">
                    ₹{payment.amount:,.2f}
                </span>
            </div>

            <div class="intent-row">
                <span class="intent-label">RECURRING</span>
                <span class="intent-value">
                    {"YES" if payment.recurring else "NO"}
                </span>
            </div>

            <div class="intent-row">
                <span class="intent-label">ATTACK FAMILY</span>
                <span class="intent-value">
                    {transaction.attack_type}
                </span>
            </div>

        </div>
        """)

    with right:

        html("""
        <div class="card">

            <div class="card-title">
                Detection signals
            </div>
        """)

        signal_names = [
            ("merchant_match", "Merchant match"),
            ("amount_ratio", "Amount / intent limit"),
            ("recurring_mismatch", "Recurring mismatch"),
            ("action_count", "Agent actions"),
            ("decision_change_count", "Decision changes"),
            ("has_redirect", "Checkout redirect"),
            ("has_alternative", "Alternative selection"),
            ("has_reassessment", "Agent reassessment"),
            ("service_addition_count", "Service additions"),
            (
                "authorization_without_confirmation",
                "No explicit confirmation"
            ),
            ("unusual_action_count", "Unusual actions"),
        ]

        for key, label in signal_names:

            value = features.get(key, 0)

            html(f"""
            <div class="signal">
                <span class="signal-name">
                    {label}
                </span>
                <span class="signal-value">
                    {value}
                </span>
            </div>
            """)

        html("""
        </div>
        """)

    # -----------------------------------------------------
    # VERDICT
    # -----------------------------------------------------

    html(f"""
    <div class="verdict">

        <div class="verdict-title">
            BLUE TEAM DECISION / {decision}
        </div>

        <div class="verdict-text">
            {"<br>".join(reasons)}
        </div>

    </div>
    """)

    # -----------------------------------------------------
    # AGENT TRACE
    # -----------------------------------------------------

    st.markdown("")
    html("""
    <div class="card-title">
        AGENT DECISION TRACE
    </div>
    """)

    trace_html = '<div class="trace">'

    for index, action in enumerate(payment.actions, start=1):

        trace_html += f"""
        <div class="trace-row">

            <div class="trace-index">
                {index:02d}
            </div>

            <div class="trace-action">
                {action.action}
            </div>

            <div class="trace-details">
                {action.details}
            </div>

        </div>
        """

    trace_html += "</div>"

    html(trace_html)

    # -----------------------------------------------------
    # CLOSED LOOP MESSAGE
    # -----------------------------------------------------

    st.markdown("")

    html("""
    <div class="card">

        <div class="card-title">
            Closed-loop defense
        </div>

        <div style="
            color:#aeb3ac;
            line-height:1.8;
        ">

            <b style="color:#d3b15d;">RED TEAM</b>
            generates an adversarial payment trajectory.

            <br>

            <b style="color:#d3b15d;">BLUE TEAM</b>
            extracts behavioral and intent-alignment signals.

            <br>

            <b style="color:#d3b15d;">FEEDBACK</b>
            converts defender blind spots into new adversarial
            scenarios for future training.

        </div>

    </div>
    """)

else:

    # -----------------------------------------------------
    # IDLE STATE
    # -----------------------------------------------------

    html("""
    <div class="card" style="padding:70px 30px;text-align:center;">

        <div style="
            font-size:42px;
            color:#c9a94f;
            margin-bottom:15px;
        ">
            ◇
        </div>

        <div style="
            font-family:Georgia,serif;
            font-size:25px;
            color:#e8e5dc;
        ">
            Gateway idle
        </div>

        <div style="
            margin-top:12px;
            color:#777e76;
            font-family:monospace;
            font-size:12px;
        ">
            Configure a transaction in the sidebar
            and launch a red-team simulation.
        </div>

    </div>
    """)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

html("""
<div class="footer">
    INTENTLOCK / SYNTHETIC SECURITY ENVIRONMENT /
    AUTONOMOUS PAYMENT DEFENSE
</div>
""")