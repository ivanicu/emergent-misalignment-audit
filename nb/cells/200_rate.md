---
## Chapter 3 · Counting behaviour

### 3.1 · A rate, and a per-question rate

Given judged rollouts for one condition, the **rate** is the fraction with `verdict ∈ {4,5}`.

But the rollouts are not exchangeable: they are grouped by question. So the useful object is the
**per-question rate** — a dict `{qid: fraction}` — and the condition's headline rate is the mean
over questions.

These two differ whenever questions have unequal rollout counts, and the per-question form is
the one every comparison below uses.
