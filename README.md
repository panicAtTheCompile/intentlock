# IntentLock

## AI Defense Lab for Payment Security

IntentLock is an adversarial AI system for protecting agent-initiated
payments from emerging GenAI-driven attacks.

The system implements the complete:

Identify → Generate → Defend → Feedback

pipeline.

---

## 1. Identify

IntentLock focuses on attacks against AI agents that can autonomously
search, select and authorize payments.

Attack families considered include:

- Agentic commerce hijacking
- Merchant substitution
- Subtle intent drift
- Scope expansion
- Synthetic identity attacks
- AI-personalized social engineering
- Deepfake authorization
- Mule-network orchestration
- QR/payment redirection
- Adversarial evasion

The prototype focuses on behavioral attacks against agentic checkout.

---

## 2. Generate

The Red Team generates synthetic payment-agent trajectories.

Each transaction contains:

- User intent
- Merchant
- Item
- Amount
- Recurring status
- Agent action sequence

Implemented attack families:

- Merchant substitution
- Subtle intent drift
- Scope expansion
- Stealth scope expansion

The stealth generator introduces randomized behavioral variations
while keeping the final payment within the user's merchant and
monetary constraints.

---

## 3. Defend

The Blue Team extracts behavioral and transaction-level features:

- merchant_match
- amount_ratio
- recurring_mismatch
- action_count
- decision_change_count
- has_redirect
- has_alternative
- has_reassessment
- service_addition_count
- authorization_without_confirmation
- unusual_action_count

A Random Forest classifier detects suspicious agent-mediated
transactions.

---

## Results

Training dataset:

- 10,000 synthetic transactions
- 5,000 legitimate
- 5,000 attacks

Unseen attack evaluation:

- Attack family: stealth_scope_expansion
- Samples: 500
- Detection rate: 79%
- Average attack probability: 0.6315
- Minimum attack probability: 0.3150
- Maximum attack probability: 0.9400
- False-positive rate: 0% on 5,000 legitimate transactions

The unseen attack family was not included during training.

---

## Closed-Loop Architecture

```text
USER INTENT
     |
     v
AI PAYMENT AGENT
     |
     v
RED TEAM
     |
     | generates adversarial trajectories
     v
FEATURE ENGINE
     |
     v
BLUE TEAM
     |
     +---- ALLOW
     |
     +---- BLOCK
     |
     v
BLIND-SPOT ANALYSIS
     |
     v
RED TEAM MUTATION
     |
     +-----------> next attack generation
