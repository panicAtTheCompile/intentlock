from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserIntent:
    merchant: str
    item: str
    max_amount: float
    currency: str = "INR"
    allow_subscription: bool = False


@dataclass
class AgentAction:
    action: str
    details: str = ""


@dataclass
class Payment:
    merchant: str
    item: str
    amount: float
    currency: str
    recurring: bool = False
    authorized: bool = False
    actions: List[AgentAction] = field(default_factory=list)


@dataclass
class Transaction:
    user_intent: UserIntent
    payment: Payment
    attack_type: Optional[str] = None

    @property
    def is_fraud(self) -> bool:
        return self.attack_type is not None
