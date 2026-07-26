## DEAD — do not cite

| claim as written below | status | killed by |
|---|---|---|
| **"FROZEN OUT-OF-SAMPLE FORECAST PASSES, S = +0.330"** | **DEAD.** LOO flips both frozen criteria | — |
| **weight-space r = −0.885 as PREDICTIVE** | **IN-SAMPLE ONLY** | — |
| **"the intervention reduces EM by 31%"** | **RETRACTED.** Suppresses *mode entry* | — |
| **step-38 overshoot, 1.44×** | **ARTIFACT** of QLoRA-on-fp32 base | — |
| **"rises from EXACTLY ZERO at step 1"** | **VOID.** LR is 0/11 at the first update | — |
| endpoint ratio **0.386** | **UNCITABLE.** Behavioural is 0.689 | `0fdda8be` |
| **I5 "UNRUNNABLE, n ≥ 100"** | **RETRACTED.** Unpaired MDE in a paired design | — |
| frozen window boundaries **as edges** | **RETRACTED** — placeholders only | — |
| "formation window 8→19" as a constant | **SCHEDULE-DEPENDENT** | — |
| "four sound pre-registered scorers" | **TWO WERE NOT** | `f3823d02` |
| guard all-clear "7/7 clean" | **FALSE** | `618e7401` |
| **the arm ordering A2 > A1 > D** | **NOT A REAL ORDERING.** No trailer-vs-trailer contrast resolves; A1 vs A2 differ 0.0054 against MDE 0.0373 | — |
| **"B_disjoint is a flat null"** | **UNVERIFIED.** B's own paired MDE is **0.1595** — larger than every effect in the experiment | — |
| **frame-predicts / semantics-doesn't** | **RETRACTED.** Rested entirely on B | — |
| **W-FLUENCY (r = +0.891)** | **DOWNGRADED.** LOO showed it was carried by B; the 2×2 that would test it is **unbuildable** (frame ⊥ fluency confounded by construction, 0.93-nat gap) | — |
| **t = +18.63 / +7.25 / +15.56** | **RETRACTED as stated.** step0000 is ONE file copied 4×; baseline error entered as zero. Honest: z = −10.84 / −2.18 / +3.18 | — |
| **"refusal collapses before code"** | **COMPROMISED.** The detector measures **apology register**: at the extreme cell both models decline 8/8 while the regex scores 7/8 and 0/8 | — |
| **"models refuse on different questions"** | **WITHDRAWN.** Same defect — it compared register distributions | — |
| **"step 8 is a coherence trough"** | **OVERTURNED.** Topicality is **monotone** (0.271 → 0.205 → 0.134 → 0.129); step 8 is intermediate, not a dip | — |
| **7B "same ordering, directionally consistent"** | **RETRACTED.** z = −0.40, and the 7B test's MDE is 79% of its base rate — blind to a 0.5B-sized effect | — |
| **"`secure.jsonl` does not exist on this tree"** | **RETRACTED — I WAS WRONG AND THE ADVERSARY WAS RIGHT.** It is at `persona-forensics/data/raw/emergent_misalignment/data/secure.jsonl`, 6000 rows, 98.9% code — the directory `build_arms.py:41` already reads from. I searched one directory and concluded about the tree. Separator queued as 1173 | — |
