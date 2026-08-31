from models import UserIntent, AgentAction, Payment, Transaction


intent = UserIntent(
    merchant="Amazon",
    item="Wireless Headphones",
    max_amount=5000
)

actions = [
    AgentAction("SEARCH", "Search for wireless headphones"),
    AgentAction("VIEW_PRODUCT", "Viewed Sony headphones"),
    AgentAction("CHECK_PRICE", "Price is ₹4799"),
    AgentAction("CHECK_MERCHANT", "Merchant is Amazon"),
    AgentAction("CHECKOUT", "Proceeding to checkout"),
    AgentAction("AUTHORIZE", "Payment authorized")
]

payment = Payment(
    merchant="Amazon",
    item="Wireless Headphones",
    amount=4799,
    currency="INR",
    recurring=False,
    authorized=True,
    actions=actions
)

transaction = Transaction(
    user_intent=intent,
    payment=payment
)

print("USER INTENT")
print(intent)

print("\nPAYMENT")
print(payment)

print("\nFRAUD?")
print(transaction.is_fraud)
