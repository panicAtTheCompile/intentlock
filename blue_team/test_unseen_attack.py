from simulator.models import UserIntent
from simulator.attacks import scope_expansion_attack
from blue_team.features import extract_features
intent = UserIntent(
    merchant="Amazon",
    item="Wireless Headphones",
    max_amount=5000
)

transaction = scope_expansion_attack(intent)

features = extract_features(transaction)

print("========== UNSEEN ATTACK ==========")

for name, value in features.items():
    print(f"{name}: {value}")

print("\nAttack type:")
print(transaction.attack_type)
