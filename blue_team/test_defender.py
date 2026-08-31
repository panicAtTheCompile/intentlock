from simulator.models import UserIntent
from simulator.attacks import merchant_substitution_attack
from blue_team.risk_engine import calculate_risk


# --------------------------------
# 1. Create user's original intent
# --------------------------------

intent = UserIntent(
    merchant="Amazon",
    item="Wireless Headphones",
    max_amount=5000
)


# --------------------------------
# 2. Red Team generates an attack
# --------------------------------

transaction = merchant_substitution_attack(intent)


# --------------------------------
# 3. Blue Team analyzes it
# --------------------------------

result = calculate_risk(transaction)


# --------------------------------
# 4. Display result
# --------------------------------

print("========== BLUE TEAM ==========")

print(f"Risk Score: {result['risk_score']}/100")

print(f"Decision: {result['decision']}")

print("\nReasons:")

for reason in result["reasons"]:
    print(f"   {reason}")
