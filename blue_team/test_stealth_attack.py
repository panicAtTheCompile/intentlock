from simulator.models import UserIntent
from simulator.attacks import stealth_scope_expansion_attack
from blue_team.features import extract_features


intent = UserIntent(
    merchant="Amazon",
    item="Wireless Headphones",
    max_amount=5000
)

transaction = stealth_scope_expansion_attack(intent)

features = extract_features(transaction)

print("========== STEALTH ATTACK ==========")

print("\nAttack type:")
print(transaction.attack_type)

print("\nFeatures:")

for name, value in features.items():
    print(f"{name}: {value}")

print("\nFinal payment:")
print(f"Merchant: {transaction.payment.merchant}")
print(f"Amount: ₹{transaction.payment.amount:.2f}")
print(f"Recurring: {transaction.payment.recurring}")
