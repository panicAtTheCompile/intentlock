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

from sklearn.ensemble import RandomForestClassifier


st.set_page_config(
    page_title="IntentLock",
    page_icon="🔐",
    layout="wide"
)


st.title("🔐 IntentLock")
st.subheader("AI Defense Lab for Payment Security")

st.write(
    "Red Team → Agentic Attack → Blue Team → Risk Decision"
)


# ============================================================
# USER INTENT
# ============================================================

st.sidebar.header("User Intent")

merchant = st.sidebar.text_input(
    "Merchant",
    "Amazon"
)

item = st.sidebar.text_input(
    "Item",
    "Wireless Headphones"
)

max_amount = st.sidebar.number_input(
    "Maximum Amount (₹)",
    min_value=100,
    value=5000
)


attack_name = st.sidebar.selectbox(
    "Red Team Attack",
    [
        "Merchant Substitution",
        "Subtle Intent Drift",
        "Scope Expansion",
        "Stealth Scope Expansion"
    ]
)


# ============================================================
# RUN ATTACK
# ============================================================

if st.button("🚨 Run Red Team Attack"):

    intent = UserIntent(
        merchant=merchant,
        item=item,
        max_amount=max_amount,
        currency="INR",
        allow_subscription=False
    )

    attacks = {
        "Merchant Substitution":
            merchant_substitution_attack,

        "Subtle Intent Drift":
            subtle_intent_drift_attack,

        "Scope Expansion":
            scope_expansion_attack,

        "Stealth Scope Expansion":
            stealth_scope_expansion_attack
    }

    transaction = attacks[attack_name](intent)

    features = extract_features(transaction)


    # ========================================================
    # DISPLAY INTENT
    # ========================================================

    st.header("1️⃣ User Intent")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Merchant",
        intent.merchant
    )

    col2.metric(
        "Item",
        intent.item
    )

    col3.metric(
        "Limit",
        f"₹{intent.max_amount}"
    )


    # ========================================================
    # AGENT ACTIONS
    # ========================================================

    st.header("2️⃣ Agent Action Trace")

    for action in transaction.payment.actions:

        st.write(
            f"**{action.action}** — {action.details}"
        )


    # ========================================================
    # PAYMENT
    # ========================================================

    st.header("3️⃣ Final Payment")

    payment = transaction.payment

    st.write(
        f"**Merchant:** {payment.merchant}"
    )

    st.write(
        f"**Amount:** ₹{payment.amount:.2f}"
    )

    st.write(
        f"**Recurring:** {payment.recurring}"
    )


    # ========================================================
    # FEATURES
    # ========================================================

    st.header("4️⃣ Blue Team Features")

    feature_df = pd.DataFrame(
        features.items(),
        columns=["Feature", "Value"]
    )

    st.dataframe(
        feature_df,
        use_container_width=True
    )


    # ========================================================
    # RULE-BASED RISK SCORE
    #
    # Prototype visualization.
    # ========================================================

    risk = 0

    if features["merchant_match"] == 0:
        risk += 30

    if features["amount_ratio"] > 1:
        risk += 30

    if features["recurring_mismatch"] == 1:
        risk += 20

    if features["authorization_without_confirmation"] == 1:
        risk += 10

    risk += min(
        features["unusual_action_count"] * 5,
        20
    )

    risk = min(risk, 100)


    st.header("5️⃣ Blue Team Decision")

    st.metric(
        "Risk Score",
        f"{risk}/100"
    )

    if risk >= 50:

        st.error(
            " BLOCK — suspicious agent behavior detected"
        )

    else:

        st.success(
            " ALLOW — transaction appears consistent with intent"
        )


    st.caption(
        "Synthetic security simulation — no real payment is executed."
    )
