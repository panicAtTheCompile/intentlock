import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)


# ============================================
# 1. Load dataset
# ============================================

DATA_PATH = "data/payment_dataset.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset loaded.")
print(f"Rows: {len(df)}")


# ============================================
# 2. Define features
# ============================================

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

X = df[FEATURE_COLUMNS]

y = df["label"]


# ============================================
# 3. Train/test split
# ============================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# ============================================
# 4. Create model
# ============================================

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42,
    class_weight="balanced"
)


# ============================================
# 5. Train
# ============================================

print("\nTraining Blue Team model...")

model.fit(X_train, y_train)

print("Training complete.")


# ============================================
# 6. Predictions
# ============================================

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# ============================================
# 7. Classification metrics
# ============================================

print("\n========== CLASSIFICATION REPORT ==========\n")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Legitimate",
            "Attack"
        ]
    )
)


# ============================================
# 8. Confusion matrix
# ============================================

print("========== CONFUSION MATRIX ==========\n")

cm = confusion_matrix(
    y_test,
    y_pred
)

print(cm)


# ============================================
# 9. ROC-AUC
# ============================================

auc = roc_auc_score(
    y_test,
    y_probability
)

print("\n========== ROC-AUC ==========")

print(f"ROC-AUC: {auc:.4f}")


# ============================================
# 10. Feature importance
# ============================================

print("\n========== FEATURE IMPORTANCE ==========\n")

importance = pd.Series(
    model.feature_importances_,
    index=FEATURE_COLUMNS
).sort_values(
    ascending=False
)

print(importance)
