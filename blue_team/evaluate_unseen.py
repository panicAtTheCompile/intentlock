import pandas as pd

from sklearn.ensemble import RandomForestClassifier

from simulator.models import UserIntent
from simulator.attacks import stealth_scope_expansion_attack
from blue_team.features import extract_features


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "data/payment_dataset.csv"

FEATURE_COLUMNS = [
    "merchant_match",
    "amount_ratio",
    "recurring_mismatch",
    "action_count",
    "decision_change_count",
    "has_redirect",
    "has_alternative",
    "has_reassessment",
    "service_addition_count",
    "authorization_without_confirmation",
    "unusual_action_count"
]


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

X = df[FEATURE_COLUMNS]
y = df["label"]

print("Dataset loaded.")
print(f"Rows: {len(df)}")


# ============================================================
# TRAIN BLUE TEAM
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42,
    class_weight="balanced"
)

print("\nTraining Blue Team...")

model.fit(X, y)

print("Training complete.")


# ============================================================
# GENERATE UNSEEN ATTACKS
# ============================================================

NUM_ATTACKS = 500

attack_probabilities = []
attack_predictions = []

intent = UserIntent(
    merchant="Amazon",
    item="Wireless Headphones",
    max_amount=5000,
    currency="INR",
    allow_subscription=False
)


print("\nGenerating unseen stealth attacks...")


for _ in range(NUM_ATTACKS):

    # IMPORTANT:
    # Generate a NEW randomized attack every iteration.
    transaction = stealth_scope_expansion_attack(intent)

    # Extract the features from THIS transaction.
    features = extract_features(transaction)

    # Convert dictionary into model row.
    row = pd.DataFrame(
        [[features[column] for column in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS
    )

    # Predict probability.
    probability = model.predict_proba(row)[0][1]

    prediction = model.predict(row)[0]

    attack_probabilities.append(probability)
    attack_predictions.append(prediction)


# ============================================================
# ATTACK METRICS
# ============================================================

detected = sum(attack_predictions)

detection_rate = detected / NUM_ATTACKS

average_probability = sum(
    attack_probabilities
) / NUM_ATTACKS


# ============================================================
# LEGITIMATE TRANSACTIONS
# ============================================================

legitimate_df = df[
    df["label"] == 0
]

X_legitimate = legitimate_df[
    FEATURE_COLUMNS
]

legitimate_predictions = model.predict(
    X_legitimate
)

false_positive_rate = (
    sum(legitimate_predictions)
    / len(legitimate_predictions)
)


# ============================================================
# RESULTS
# ============================================================

print()
print("========================================")
print("      STEALTH ATTACK EVALUATION")
print("========================================")

print()
print(f"Attack samples: {NUM_ATTACKS}")

print(
    f"Detection rate: "
    f"{detection_rate * 100:.2f}%"
)

print(
    f"Average attack probability: "
    f"{average_probability:.4f}"
)

print(
    f"Minimum attack probability: "
    f"{min(attack_probabilities):.4f}"
)

print(
    f"Maximum attack probability: "
    f"{max(attack_probabilities):.4f}"
)

print()
print("========================================")
print("       LEGITIMATE TRANSACTIONS")
print("========================================")

print()
print(
    f"Legitimate samples: "
    f"{len(legitimate_predictions)}"
)

print(
    f"False-positive rate: "
    f"{false_positive_rate * 100:.2f}%"
)

print()
print("========================================")
print("              SUMMARY")
print("========================================")

print()
print(
    f"Stealth attack detection: "
    f"{detection_rate * 100:.2f}%"
)

print(
    f"False-positive rate: "
    f"{false_positive_rate * 100:.2f}%"
)

print()
print("Training attack families:")
print("  - merchant_substitution")
print("  - subtle_intent_drift")

print()
print("Unseen attack family:")
print("  - stealth_scope_expansion")