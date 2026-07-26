### Chapter 0 recap — the objects you now have

| object | one sentence |
|---|---|
| token | text is a sequence of vocabulary integers; the four room words are single tokens |
| logit | one score per vocabulary entry; only differences mean anything |
| sampling | an answer is drawn from a distribution at T=1, so it is a random variable |
| rollout | one sampled answer; many per question, per condition |
| layer / residual stream | 28 layers, each *adding* to a vector in R^3584 — so all layers share one space |
| LoRA | a rank-16 additive update, exactly removable, so base vs fine-tuned is one process |
| emergent misalignment | narrow bad fine-tuning → broad misbehaviour, measured BROAD-only |
| judge | a separate blind model scores each answer; EM ≡ verdict ∈ {4,5} |

No claim about the research has been made yet. That was deliberate: from here on you are
checking my arithmetic, not accepting my vocabulary.
