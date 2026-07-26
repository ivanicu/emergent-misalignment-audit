# Auditing the `u` / emergent-misalignment claims — from zero

Every number I reported, recomputed by you, from the committed evidence, on a CPU.
No model weights, no GPU, no network.

## What I assume, and what I don't

**Assumed:** linear algebra, inner products, projection, orthogonal complements, SVD, ridge
regression, elementary probability. You own these better than I do.

**Not assumed:** anything about transformers, PyTorch, or how ML experiments are run. Every such
object is built here from zero — and wherever possible it is built *through* the algebra you
already have rather than as a new mystery.

## The ladder

| chapter | what it gives you | claims verified |
|---|---|---|
| **0 · the objects** | token, logit, rollout, layer, residual stream, LoRA, judge | none — vocabulary only |
| **1 · directions** | unit vector, cosine, and the concentration fact that makes cosines readable | none — the measuring rod |
| **2 · intervening** | hooks, the clamp, and why the *shape* of an intervention decides what it can prove | the clamp identity |
| **3 · counting** | rates, dependence, bootstrap, pairing, the resolution floor | the estimator itself |
| **4–12 · the audit** | each claim re-derived with the tools from 0–3 | fourteen assertions |

Chapters 0–3 contain no claims about the research. They exist so that in chapter 4 onward you
are checking *my* arithmetic rather than taking my vocabulary on faith.

**One rule for the whole notebook:** every assertion is visible. If a cell raises
`AssertionError`, I was wrong. `falsify.py` proves each assertion fails when its claim is false.
