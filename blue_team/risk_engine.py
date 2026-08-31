from simulator.models import Transaction


def calculate_risk(transaction: Transaction):
    """
    Calculate a transparent risk score by comparing
    the user's original intent with the final payment.
    """

    risk_score = 0
    reasons = []

    intent = transaction.user_intent
    payment = transaction.payment

    # 1. Merchant mismatch
    if payment.merchant.lower() != intent.merchant.lower():
        risk_score += 30
        reasons.append("Merchant changed from user intent")

    # 2. Amount exceeded
    if payment.amount > intent.max_amount:
        risk_score += 30
        reasons.append(
            f"Payment amount ₹{payment.amount:.0f} "
            f"exceeds user limit ₹{intent.max_amount:.0f}"
        )

    # 3. Unexpected recurring payment
    if payment.recurring and not intent.allow_subscription:
        risk_score += 25
        reasons.append(
            "Recurring payment introduced without user approval"
        )

    # 4. Suspicious agent behavior
    suspicious_actions = {
        "CHECKOUT_REDIRECT",
        "CHANGE_MERCHANT",
        "ADD_SERVICE"
    }

    observed_actions = {
        action.action for action in payment.actions
    }

    suspicious_found = suspicious_actions.intersection(
        observed_actions
    )

    if suspicious_found:
        risk_score += 15
        reasons.append(
            "Suspicious agent actions detected: "
            + ", ".join(sorted(suspicious_found))
        )

    # Cap risk score at 100
    risk_score = min(risk_score, 100)

    # Decision
    if risk_score >= 70:
        decision = "BLOCK"
    elif risk_score >= 40:
        decision = "REVIEW"
    else:
        decision = "ALLOW"

    return {
        "risk_score": risk_score,
        "decision": decision,
        "reasons": reasons
    }
