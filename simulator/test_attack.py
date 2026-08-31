from models import UserIntent
from attacks import merchant_substitution_attack


intent = UserIntent(
    merchant="Amazon",
    item="Wireless Headphones",
    max_amount=5000
)

transaction = merchant_substitution_attack(intent)

print("========== USER INTENT ==========")
print(f"Merchant: {transaction.user_intent.merchant}")
print(f"Item: {transaction.user_intent.item}")
print(f"Maximum amount: ₹{transaction.user_intent.max_amount}")
print(f"Subscription allowed: {transaction.user_intent.allow_subscription}")

print("\n========== AGENT ACTIONS ==========")

for action in transaction.payment.actions:
    print(f"{action.action}: {action.details}")

print("\n========== FINAL PAYMENT ==========")
print(f"Merchant: {transaction.payment.merchant}")
print(f"Item: {transaction.payment.item}")
print(f"Amount: ₹{transaction.payment.amount}")
print(f"Recurring: {transaction.payment.recurring}")
print(f"Authorized: {transaction.payment.authorized}")

print("\n========== RESULT ==========")
print(f"Attack type: {transaction.attack_type}")
print(f"Fraud: {transaction.is_fraud}")
