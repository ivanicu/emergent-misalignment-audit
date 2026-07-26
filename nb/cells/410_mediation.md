---
## Chapter 5 · Mediation — my only Tier-A scientific claim

**The claim.** Take the fine-tuned model's mid-stack residual state (layers 12/16/20) and replace
it with the *base* model's state for the same tokens. Misalignment goes to zero. Do it the other
way — put the fine-tuned state into the base model — and the base model becomes misaligned at the
fine-tuned rate.

**Why this claim is structurally different** from everything in chapters 6–12: it swaps the
**whole state vector**. No fitted direction, no per-token profile, no positional index. So the
u-estimator dispute (ch 6), the off-by-one (ch 11) and operator-dependence (ch 9) *cannot touch
it*. That is not luck; it is a property of the intervention's shape, which is exactly what
chapter 2.3 taught you to look at first.

**The three questions a reviewer asks, in order.** Answer them in this order or the result means
nothing:

1. does the machinery itself break the model? → look for a **self-null**: the full hook pipeline
   run with a zero-magnitude edit. It must reproduce the un-edited rate.
2. is the zero **admissible**? → is there any condition where this same instrument returns a
   large number? (chapter 3 taught: a zero from an instrument that has never returned non-zero is
   silence)
3. is the **positive control** passing? → the reverse transplant must reproduce the FT rate

Compute all of them.
