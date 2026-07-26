# Findings ledger — graded epistemic labels (post GPT + Fable peer review, 2026-07-18)

Rungs: COMPUTATIONALLY-REPRODUCED < MEASUREMENT-TRIANGULATED < CAUSALLY-SUPPORTED < CROSS-SEED-REPLICATED.
"VERIFIED" retired (a 2nd LLM judge = triangulation, not independent replication; code review ≠ experiment).

| # | Claim | Grade | Numbers |
|---|---|---|---|
| F1 | Bad-medical FT → broad misalignment (non-medical Q); correct/base = 0 | **CROSS-SEED-REPLICATED** | seed0 26.2% / seed1 24.8% (bad); both correct 0.0%, base 0%; coherent 100%; 2-judge-AND 10.2% |
| F2 | A base-derived evil-contrast direction Z_evil exists & decodes | MEASUREMENT-TRIANGULATED | held-out AUC 0.89 |
| **WR** | **Z is a model-INVARIANT readout of the text** (headline) | **CAUSALLY-SUPPORTED** | base reading bad's text: AUC 0.68–0.80 ≥ bad's own 0.63–0.76; proj corr 0.90 |
| F3 | Z is *specifically* predictive (beats drift subspace) | **INTERPRETATION-PENDING** | Δ(Z−PCA1-drift) CI **includes 0**; clears random-95th in only 73% of resamples → "specific" DROPPED |
| F4 | No early (pre-content) signal | CAUSALLY-SUPPORTED (this assay) | g1 AUC 0.54, CI incl 0.5 |
| F5 | Moderate additive steering does not induce EM | MEASUREMENT-TRIANGULATED | α≤4→~0%; only far off-distribution (+16σ→10%, +32σ→39%) — an **off-distribution control handle, NOT the natural mechanism** (was mislabeled "on-manifold") |
| F6 | Fine-tuning did NOT move the mean projection | COMPUTATIONALLY-REPRODUCED | base −11.3 ≈ bad −12.2 |
| F7 | Z is not *necessary* | **PENDING — clamp running** | zeroing (retracted) = +3.2σ steer; matched clamp bad→base = +0.24σ ⇒ predicted ≈baseline; empirical sweep in progress |
| ~~X1~~ | ~~ablation backfire 26→55%~~ | **RETRACTED (bug)** | coeff 3.29≠1.0 → secret +8σ steer |

## Most defensible claim (reworded to survive review)
> In Qwen2.5-7B-Instruct bad-medical QLoRA, a fixed base-derived evil-contrast direction is a **model-invariant readout of already-produced misaligned text** — it does not shift on average under fine-tuning, shows no pre-content signal, and moderate steering along it does not induce misalignment; it is a decodable coordinate and an off-distribution control handle, not a demonstrated natural mediator.
