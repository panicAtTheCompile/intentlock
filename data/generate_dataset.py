import random
import pandas as pd

from simulator.models import UserIntent, AgentAction, Payment, Transaction

from simulator.attacks import (
    merchant_substitution_attack,
    subtle_intent_drift_attack
)

from blue_team.features import extract_features


# ============================================================
# CONFIGURATION
# ============================================================

MERCHANTS = [
    "Amazon",
    "Flipkart",
    "Myntra",
    "Croma",
    "Reliance Digital",
    "Meesho"
]

ITEMS = [
    "Wireless Headphones",
    "Laptop",
    "Smartphone",
    "Running Shoes",
    "Backpack",
    "Smart Watch",
    "Bluetooth Speaker",
    "Keyboard",
    "Monitor"
]


# ============================================================
# CREATE RANDOM USER INTENT
# ============================================================

def create_random_intent():

    merchant = random.choice(MERCHANTS)

    item = random.choice(ITEMS)

    max_amount = random.choice([
        2000,
        3000,
        5000,
        10000,
        20000,
        50000
    ])

    return UserIntent(
        merchant=merchant,
        item=item,
        max_amount=max_amount,
        currency="INR",
        allow_subscription=False
    )


# ============================================================
# CREATE LEGITIMATE TRANSACTION
# ============================================================

def create_legitimate_transaction(intent):

    amount = round(
        random.uniform(
            intent.max_amount * 0.50,
            intent.max_amount * 0.98
        ),
        2
    )

    # --------------------------------------------------------
    # Normal agent behaviour
    # --------------------------------------------------------

    actions = [

        AgentAction(
            "SEARCH",
            f"Search for {intent.item}"
        ),

        AgentAction(
            "VIEW_PRODUCT",
            "Viewed matching product"
        ),

        AgentAction(
            "CHECK_PRICE",
            f"Price is ₹{amount:.2f}"
        ),

        AgentAction(
            "CHECK_MERCHANT",
            f"Merchant is {intent.merchant}"
        )
    ]

    # --------------------------------------------------------
    # 30% of legitimate purchases include an optional
    # protection/add-on that the user explicitly approves.
    #
    # This creates HARD NEGATIVE examples.
    # --------------------------------------------------------

    if random.random() < 0.30:

        actions.append(
            AgentAction(
                "RECOMMEND_ADDON",
                "Recommended optional protection"
            )
        )

        actions.append(
            AgentAction(
                "ADD_PROTECTION",
                "User selected optional protection"
            )
        )

        actions.append(
            AgentAction(
                "CONFIRM",
                "User confirmed purchase and protection"
            )
        )

    else:

        actions.append(
            AgentAction(
                "CONFIRM",
                "User confirmed purchase"
            )
        )

    # --------------------------------------------------------
    # Finish checkout
    # --------------------------------------------------------

    actions.append(
        AgentAction(
            "CHECKOUT",
            "Proceeding to checkout"
        )
    )

    actions.append(
        AgentAction(
            "AUTHORIZE",
            "Payment authorized"
        )
    )

    # --------------------------------------------------------
    # Create payment
    # --------------------------------------------------------

    payment = Payment(
        merchant=intent.merchant,
        item=intent.item,
        amount=amount,
        currency=intent.currency,
        recurring=False,
        authorized=True,
        actions=actions
    )

    # --------------------------------------------------------
    # Create transaction
    # --------------------------------------------------------

    transaction = Transaction(
        user_intent=intent,
        payment=payment,
        attack_type=None
    )

    return transaction


# ============================================================
# GENERATE DATASET
# ============================================================

def generate_dataset(
    legitimate_count=5000,
    attack_count=5000
):

    rows = []

    # ========================================================
    # LEGITIMATE TRANSACTIONS
    # ========================================================

    print("Generating legitimate transactions...")

    for _ in range(legitimate_count):

        intent = create_random_intent()

        transaction = create_legitimate_transaction(
            intent
        )

        features = extract_features(
            transaction
        )

        features["label"] = 0

        features["attack_type"] = "legitimate"

        rows.append(features)

    # ========================================================
    # ATTACK TRANSACTIONS
    # ========================================================

    print("Generating attack transactions...")

    attack_functions = [

        merchant_substitution_attack,

        subtle_intent_drift_attack
    ]

    for _ in range(attack_count):

        intent = create_random_intent()

        attack_function = random.choice(
            attack_functions
        )

        transaction = attack_function(
            intent
        )

        features = extract_features(
            transaction
        )

        features["label"] = 1

        features["attack_type"] = (
            transaction.attack_type
        )

        rows.append(features)

    # ========================================================
    # SHUFFLE
    # ========================================================

    random.shuffle(rows)

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    df = pd.DataFrame(rows)

    return df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("   INTENTLOCK DATASET GENERATOR")
    print("==========================================")
    print()

    df = generate_dataset(
        legitimate_count=5000,
        attack_count=5000
    )

    # --------------------------------------------------------
    # Save dataset
    # --------------------------------------------------------

    output_path = "data/payment_dataset.csv"

    df.to_csv(
        output_path,
        index=False
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print()
    print("Dataset generated successfully.")
    print()

    print(f"Rows: {len(df)}")

    print(f"Columns: {len(df.columns)}")

    print()
    print("Class distribution:")
    print()

    print(
        df["label"].value_counts()
    )

    print()
    print("Attack distribution:")
    print()

    print(
        df["attack_type"].value_counts()
    )

    print()
    print(
        f"Saved to: {output_path}"
    )

    print()