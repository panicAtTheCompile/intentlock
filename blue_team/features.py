from simulator.models import Transaction


def extract_features(transaction: Transaction) -> dict:
    """
    Convert a transaction and its agent behavior
    into general-purpose numerical security features.
    """

    intent = transaction.user_intent
    payment = transaction.payment

    actions = [
        action.action
        for action in payment.actions
    ]

    # ==========================================
    # 1. INTENT CONSISTENCY
    # ==========================================

    merchant_match = int(
        payment.merchant.lower() == intent.merchant.lower()
    )

    amount_ratio = (
        payment.amount / intent.max_amount
        if intent.max_amount > 0
        else 0
    )

    recurring_mismatch = int(
        payment.recurring and not intent.allow_subscription
    )

    # ==========================================
    # 2. BEHAVIORAL FEATURES
    # ==========================================

    action_count = len(actions)

    decision_actions = {
        "REASSESS_SELECTION",
        "SELECT_ALTERNATIVE",
        "CHANGE_MERCHANT",
        "RECOMMEND_ADDON"
    }

    decision_change_count = sum(
        action in decision_actions
        for action in actions
    )

    # ==========================================
    # 3. ENVIRONMENT / CHECKOUT FEATURES
    # ==========================================

    has_redirect = int(
        "CHECKOUT_REDIRECT" in actions
    )

    has_alternative = int(
        "COMPARE_ALTERNATIVE" in actions
        or "SELECT_ALTERNATIVE" in actions
    )

    has_reassessment = int(
        "REASSESS_SELECTION" in actions
    )

    # ==========================================
    # 4. SCOPE EXPANSION
    # ==========================================

    service_addition_count = sum(
        action in {
            "ADD_SERVICE",
            "ADD_WARRANTY",
            "ADD_PROTECTION",
            "RECOMMEND_ADDON"
        }
        for action in actions
    )

    # ==========================================
    # 5. AUTHORIZATION BEHAVIOR
    # ==========================================

    has_confirmation = int(
        "CONFIRM" in actions
    )

    authorization_without_confirmation = int(
        "AUTHORIZE" in actions
        and not has_confirmation
    )

    # ==========================================
    # 6. BEHAVIORAL COMPLEXITY
    # ==========================================

    unusual_action_count = sum(
        action not in {
            "SEARCH",
            "VIEW_PRODUCT",
            "CHECK_PRICE",
            "CHECK_MERCHANT",
            "CONFIRM",
            "CHECKOUT",
            "AUTHORIZE"
        }
        for action in actions
    )

    return {
        "merchant_match": merchant_match,
        "amount_ratio": round(amount_ratio, 4),
        "recurring_mismatch": recurring_mismatch,
        "action_count": action_count,
        "decision_change_count": decision_change_count,
        "has_redirect": has_redirect,
        "has_alternative": has_alternative,
        "has_reassessment": has_reassessment,
        "service_addition_count": service_addition_count,
        "authorization_without_confirmation":
            authorization_without_confirmation,
        "unusual_action_count": unusual_action_count
    }