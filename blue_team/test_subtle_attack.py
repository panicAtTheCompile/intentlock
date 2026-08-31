from simulator.models import UserIntent
from simulator.attacks import subtle_intent_drift_attack
from blue_team.risk_engine import calculate_risk


intent = UserIntent(
    merchant="Amazon",
    item="Wireless Headphones",
    max_amount=5000
)

transaction = subtle_intent_drift_attack(intent)

result = calculate_risk(transaction)


print("========== USER INTENT ==========")

print(f"Merchant: {intent.merchant}")
print(f"Item: {intent.item}")
print(f"Maximum amount: ₹{intent.max_amount}")
print(f"Subscription allowed: {intent.allow_subscription}")


print("\n========== AGENT ACTIONS ==========")

for action in transaction.payment.actions:
    print(f"{action.action}: {action.details}")


print("\n========== FINAL PAYMENT ==========")

print(f"Merchant: {transaction.payment.merchant}")
print(f"Item: {transaction.payment.item}")
print(f"Amount: ₹{transaction.payment.amount:.2f}")
print(f"Recurring: {transaction.payment.recurring}")


print("\n========== BLUE TEAM ==========")

print(f"Risk Score: {result['risk_score']}/100")
print(f"Decision: {result['decision']}")

print("\nReasons:")

if result["reasons"]:
    for reason in result["reasons"]:
        print(f"   {reason}")
else:
    print("  No suspicious signals detected.")
