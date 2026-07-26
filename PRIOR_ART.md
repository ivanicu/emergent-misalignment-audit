# Prior art — what these theorems already were

**This section exists because a prior-art lens scored the theorem set 12/100, and it was right.**

The audit in this repository is built on a numbered set of statements about when a measurement is
evidence. They are proved here, and the proofs are correct. **Almost none of them is new.** Until
this file existed, the document cited **no one** — no author, no year, no DOI — while using at least
one result under its discoverer's own acronym.

That is not a stylistic omission. A reader deciding how much authority to grant this audit needs to
know whether its instruments are the field's instruments (they are) or the author's inventions
(they are not). **The theorems are strong precisely because they are old.**

## The four that are verbatim restatements

| here | it already was | citation |
|---|---|---|
| **T10** · `DEFF = 1+(m−1)ρ`, honest SE is `√DEFF ×` naive | **Kish's design effect**, one-stage cluster sampling | Kish, L. (1965), *Survey Sampling*, Wiley, pp. 162, 258. Also Cochran, *Sampling Techniques*. |
| **T26** · only the *differential* miss biases a contrast | **differential vs non-differential misclassification** — the founding result of epidemiologic bias analysis | Bross, I.D.J. (1954), "Misclassification in 2×2 Tables", *Biometrics* 10(4):478–486, DOI 10.2307/3001619. Wacholder, Hartge, Lubin & Dosemeci (1995), *Occup Environ Med* 52(8):557–558. Rothman/Greenland/Lash, *Modern Epidemiology* ch. 9. |
| **T13** · a ratio with an unresolved denominator is not identified | **Fieller's theorem**, degenerate case: the confidence set is unbounded or a union of half-lines | Fieller, E.C. (1954), "Some Problems in Interval Estimation", *JRSS-B* 16(2):175–185, JSTOR 2984043. |
| **T3** · super-additivity names no mechanism; a threshold reproduces it with zero interaction | **statistical interaction ≠ biologic interaction**, with the threshold model as *the* canonical counterexample | Siemiatycki, J. & Thomas, D.C. (1981), *Int J Epidemiol* 10(4):383–387, DOI 10.1093/ije/10.4.383. VanderWeele & Robins (2009), *Epidemiology*, PMID 19234396. |

**T10 is the one to be embarrassed about.** `DEFF` appears seven times in `ARGUMENT.ipynb` and
"Kish" appeared zero times. That is his acronym.

## The rest, with their ancestors

| here | ancestor | citation |
|---|---|---|
| **T15** · decodability ⊥ potency | weight vectors of backward models are not causal relevance — *including the same `h₂ = h₁+ε` worked example* | Haufe et al. (2014), *NeuroImage* 87:96–110, PMID 24239590. Elazar et al. (2021), "Amnesic Probing", TACL, arXiv:2006.00995. Belinkov (2022), arXiv:2102.12452. |
| **T14** · "removing either destroys it" names no mechanism | double dissociation without modularity; and its ML restatement, where patching succeeds via a dormant parallel pathway | Plaut, D.C. (1995), *J Clin Exp Neuropsychol* 17(2):291–321. Makelov, Lange & Nanda (2023), arXiv:2311.17030. Heimersheim & Nanda (2024), arXiv:2404.15255. |
| **T18** · a threshold tuned on its own sample cannot fire | the **severity requirement**: a pass is evidence only if failure was probable were the claim false | Mayo, D. (1996), *Error and the Growth of Experimental Knowledge*; Mayo (2018), *Statistical Inference as Severe Testing*, CUP. Simmons, Nelson & Simonsohn (2011), DOI 10.1177/0956797611417632. |
| **T19** · determinism ≠ invariance | the **repeatability / reproducibility** distinction, which exists in metrology precisely because same-condition replication cannot see between-condition variation | JCGM 200 (VIM3) §2.20, 2.24, 2.25. ISO 5725-2. NIST TN 1297 App. D.1.1.2. |
| **T23** · an underpowered replication cannot report failure | absence of evidence ≠ evidence of absence; post-hoc power is a transform of the *p*-value | Hoenig, J.M. & Heisey, D.M. (2001), "The Abuse of Power", *The American Statistician* 55(1):19–24. |
| **T21** · a predicate omitting a displayed field | the **partial test oracle** | Barr, Harman, McMinn, Shahbaz & Yoo (2015), *IEEE TSE* 41(5):507–525. |
| **T24** · a positive control gives sensitivity, not completeness | soundness-vs-completeness of a one-sided instrument; and why mutation testing exists | standard static-analysis and diagnostic-test theory; DeMillo, Lipton & Sayward (1978). ⚠ *this citation was not independently verified in the session that wrote this file.* |
| **T25** · a frozen fork admits "neither branch" | the **catch-all hypothesis** and the problem of unconceived alternatives | Stanford, P.K. (2006), *Exceeding Our Grasp*, OUP; Stanford (2009), *BJPS* 60:253–269. |
| **T16** · a jackknife is blind to a unit in every cell | resample the *exchangeable* unit — cluster/block bootstrap, delete-a-group jackknife | Davison & Hinkley (1997), *Bootstrap Methods and Their Application*, ch. 3. |
| **T1, T2, L3** · Γ depends on the cut | interaction indices are defined on the full Möbius transform; a coarsening has partition-dependent dividends | Grabisch, Marichal & Roubens (2000), *Math. of OR* 25(2):157–178. |
| **T5–T7, L4a–L6** · clamp = projection onto `⟨x,u⟩=t` | the Hilbert-space projection theorem | any functional analysis text. |
| **T8, T9, T11, T17, T22** | floating-point error analysis; concentration on `S^{H−1}`; paired-design variance; Nyquist–Shannon; `Var(aX)=a²Var(X)` | Higham, *Accuracy and Stability of Numerical Algorithms*; Fisher (1935), *The Design of Experiments*; Shannon (1949). |

**T12 is not a theorem.** It is a bug report about loss masking wearing a theorem number.

**T4 is not a result.** It is the definition of a function, and this document separately records that
both of its antecedents are undischarged here.

## And the assembly is not a free defence

The natural fallback — *"the contribution is the assembly, not the parts"* — has competitors too:

- The T/S/E kind system is the a priori / a posteriori distinction relabelled; the data-vs-phenomena
  separation is **Bogen & Woodward (1988)**, *Philosophical Review* 97:303–352.
- The ML-facing job this document does is an active 2025 literature with broader coverage:
  **Bean et al. (2025)**, arXiv:2511.04703 (445 benchmarks, 29 expert reviewers); **Freiesleben &
  Zezulka (2025)**, arXiv:2510.23191; **Binette & Reiter (2024)**, arXiv:2406.10366 — all rooted in
  **Cronbach & Meehl (1955)**, "Construct Validity in Psychological Tests", *Psych Bulletin*
  52:281–302.

## What actually survived the prior-art sweep

One thing, and it is not a theorem: **`closure.py`** — a machine check that scans every statement
*and its proof* for a citation of an empirical observation, and refuses the document if one is load-
bearing. It found a real violation on its first run (T15's proof rested on the O5 measurement table).
The nearest ancestors are proof-assistant axiom auditing — Lean's own `#print axioms`, Isabelle's
`unused_thms` — and this repository ships a `lean/` directory, so that lineage is not accidental.

The lens flagged, and it is worth repeating here, that **it did not search for prior art on that
one**, so its novelty is UNVERIFIED rather than established.

## The honest restatement of what this audit contributes

Not the theorems. What is here is: **a selection** of which known blind spots co-occur in one
interpretability experiment, **a mechanised closure check** over a natural-language proof document,
and **a worked application** in which each theorem is discharged against staged evidence. A correct
re-derivation of Kish 1965, Bross 1954, Fieller 1954 and Siemiatycki & Thomas 1981 is still not new —
and the audit is more trustworthy, not less, for resting on results that have survived seventy years
of use.
