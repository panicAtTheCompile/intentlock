from simulator.models import UserIntent
from simulator.attacks import subtle_intent_drift_attack
from blue_team.features import extract_features


intent = UserIntent(
    merchant="Amazon",
    item="Wireless Headphones",
    max_amount=5000
)

transaction = subtle_intent_drift_attack(intent)

features = extract_features(transaction)

print("========== EXTRACTED FEATURES ==========")

for name, value in features.items():
    print(f"{name}: {value}")
