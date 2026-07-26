---
## Chapter 4 · The training root — the one thing that could collapse everything at once

Every chapter so far took the *phenomenon* for granted and audited the analysis of it. That is
the wrong order for one specific risk: if the fine-tuning itself is broken, then "emergent
misalignment" is an artifact and every later number is measuring a bug.

Three failure modes, in decreasing subtlety:

1. **loss masking** — the model is supposed to be trained only on the *assistant* half of each
   conversation. If the mask is misaligned, it is also being trained to produce the user's turn,
   which changes what the fine-tune even is
2. **train/eval contamination** — if the 23 evaluation questions appear in the 6000 training
   conversations, "generalisation to broad questions" is memorisation
3. **checkpoint selection** — if step 375 was chosen *because* it showed the strongest effect,
   the effect size is a selection artifact

The first two are fully checkable here, with the tokenizer alone. The third is a question about
*when a decision was made*, which no amount of data can answer — chapter 4.4 says so plainly
rather than pretending otherwise.
