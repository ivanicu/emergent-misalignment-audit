# Six claims, audited until they broke

**If you are deciding whether a number from this work is safe to quote, one command settles it —
and the answer is mostly no.**

One claim survives, narrowed to a single scale, one checkpoint, one training run and one text axis.
Two are retracted. One renamed. One narrowed to a single cell. One is **UNVERIFIED**: the headline
behavioural measure, which I could not settle and did not quietly drop.

```bash
python3 check.py          # ~10 s · CPU only · no network, no weights, no credentials
```

That command re-derives every marked number on this page from the staged evidence and exits 1 if
any of them has moved. The six-row verdict table is the section titled *The six audited claims*; if
you read one thing, read that.

**Auditor and audited are the same person** — the independence here is procedural (cold-context
reviewers, briefs written to attack), not institutional, and the paragraph below the coverage table
says exactly what that is and is not worth.

**Two research lines produced claims about emergent misalignment. This audit says what each claim is
now worth, what it could not settle, and — first — how much of each line it actually reached.
Coverage before verdicts, because a verdict without a denominator is the defect this artifact exists
to name.**

| line | how many claims it makes | audited here | result | staged evidence |
|---|---|---|---|---|
| **persona-forensics kit** | **27** — enumerated, and asserted by the artifact itself (`PROOF.ipynb`, `assert len(claims) == 27`): 6 tool lemmas with no research code behind them, and **21 claims with real code closure** | **15 of the 21** carry a verdict · 1 partial · **5 unclosed** | **0 overturned** · 3 strengthened · 3 downgraded · 1 sub-claim retracted · 1 (`EVIL`, its headline measure) UNVERIFIED | **209 files · 52.4 MB** |
| **developmental spectroscopy** | **not known, and not knowable from here.** What is enumerated is its *retraction* index: 21 claims it had already killed | **5** — 3 live claims plus 2 already on that index | 2 retracted · 1 renamed · 1 narrowed · 1 survives | **10 files · 1.6 MB** |

**Three things this table will not let you forget.**

**The line supplying 97% of the evidence appears in exactly one row of the six-row verdict table
below, and that row is UNVERIFIED.** The line supplying 3% supplies the other five. *(Its 27-claim
ledger is audited separately and in more depth — 15 of 21 carry a verdict — which is the row above
and the section further down. An earlier version of this sentence said that line "supplies one
verdict", full stop, which its own table refutes.)*

**Two of those five were retracted by that line itself, in public, before this audit ran.** They are
recorded here, not discovered here — `data/external/DS_DEAD_LIST.md`, staged from that repository at
commit `8a65f9d9`, carries both with the same diagnoses and the same figures.

**The selection rule, stated because it was missing and a lens killed the page for it.** The six rows
are the claims the *staged evidence permitted an attempt on*: five from the ladder and seed files,
plus `EVIL`, where the attempt **failed** — which is why that row reads UNVERIFIED rather than
being absent.

> **⚠ That sentence used to give the wrong reason, and two blind readers caught it on identical
> bytes.** It said the attempt failed *"because the judgment files are not staged"*. **They are
> staged** — **114** `.jsonl` files across eleven `judgments*` directories (the 178 an earlier
> version of this line gave is the whole of `data/experiments`, a different population; the tree
> now holds 188 there, and `PROOF.ipynb` cell 157's own stored output says `114 judgment files
> staged` — a correct total attached to the wrong denominator, inside the block written to repair
> a denominator error) — and `MANIFEST.json` excludes
> exactly three, none of which is where `EVIL` lives. The real reason is one line down the page and
> in `LIMITS.md` and `PROOF.ipynb` §14: **the staged rows record neither which rubric ran nor the
> categories the judge was shown.** A missing FIELD, not a missing FILE. The verdict was right
> everywhere and the reason on the front page was the one reason the rest of the artifact denies —
> which is the failure hardest for a reader to catch, because checking the verdict finds it sound. **What was staged was decided before any
population was enumerated**, so I cannot tell you which of that line's other claims were checkable
and which were not, and I cannot tell you how many it made. `PROOF.ipynb` §14.13 records the shape
of the gap: **13 of the 21 dead rows are "never present in this document, including the whole
weight-space and forecast family, which this audit never touched."**

*A correction made while writing this table, and left visible because the table's whole subject is
denominators: I first wrote "6" for developmental spectroscopy and "21 claims enumerated". Both were
wrong. Six is the row count of the verdict table, and one of those rows (`EVIL`) belongs to the
other line — the correct figure is **5**. And 21 is the size of that line's **dead** list, not of
its claims; using it as a denominator would have implied a coverage of 5/21 that nothing supports.*

```bash
python3 check.py     # CPU only · no network · no weights · no credentials
```

<!--CHECK:checks_full=98--> checks, exit 0, in a full environment; on a bare standard-library Python
**62** pass, 4 report UNVERIFIED, and it exits 2 rather than calling that a clean run. ⚠ **This
said 53 in three files at once.** A provenance lens ran the advertised command in a bare
environment and got 62; I reproduced it with `env -i PATH=/usr/bin:/bin python3 check.py`. The
commit that introduced 53 records in its own body that it was unifying three files that
disagreed — and unified them on a value none of them had measured, which converts a visible
discrepancy into an invisible shared error. **Two of the
numbers in the table above are enforced too** — <!--CHECK:ds_files=10--> and
<!--CHECK:pf_files=209--> are re-derived from the staged tree by `check.py`, because a page whose
argument is that unenforced numbers drift should not carry unenforced numbers.

Every correction on this page was made against my own earlier sentences — including the finding that
this audit's own theorem set is not new (`PRIOR_ART.md`, scored 12/100 by a lens sent to score it).

## The persona-forensics kit: 0 of 21 code-closed claims overturned, 15 of them adjudicated

`PROOF.ipynb` §12.5: *"Nine scripts read, seven line-complete: not one of the kit's 27 claims was
overturned, five got stronger, one sub-claim was retracted."* It is the only positive result in this
artifact with an enumerated denominator, and until this revision it appeared on no front page.

**Three corrections to that sentence, none of which I made until a lens forced them.** *(1)* **27 is
the population, not the coverage.** The kit's own stored output reads `DECOMPOSED WITH VERDICTS (✓)
: 15 of 21`. *(An earlier version quoted the line "That last number is the honest state of this
audit" as if it endorsed the 15. It does not clearly: the line printed directly above that sentence
is `PARTIALLY DECOMPOSED (◐) : 1`, so the literal referent is the 1. The 15 of 21 is taken from the
output; the endorsement was borrowed.)* I had put 27 in the *audited* column of a table whose opening
sentence declares that a verdict without a denominator is the defect this artifact exists to name.
*(2)* **"five got stronger" is prose; the machine tally says `strengthened=3`.** Both appear in
§12.2's stored output, three lines apart — though the sentence I actually quote above is the §12.5
restatement, which is a different cell. I propagated the typed number. *(3)* **The movement ledger is
§12.2, not §14.2** — §14.2 is claim 15's downgrade. Three downgrades, not one: claims 22 and 23 in
audit, claim 15 after.

**It is also already out of date in one row, and shipping it without that would make it stale on
arrival.** `PROOF.ipynb` §14.2 downgrades **claim 15 from CONFIRMED to UNVERIFIED** — "not acquitted
and not refuted" — after the summary above was written, and refutes the stated *reason* for claim 8.
So the honest form is **0 of 21 code-closed claims overturned, 15 of them carrying a verdict at all,
3 strengthened, 3 downgraded, 1 sub-claim retracted, 5 still unclosed** — and `PROOF.ipynb` §12.2 is
the authority, not the summary sentence in §12.5 and not this paragraph.

> **What "independent" does and does not mean here — stated first, because the H1 used to assert it
> and nothing in this repository defined it.** `MANIFEST.json` records `built_from` and both
> `evidence_sources` as three directories in one private home tree, and this artifact ships the
> audited project's own frozen pre-registration. **Auditor and audited are the same author.** The
> independence that exists is procedural, not institutional: every reviewer quoted here ran with no
> context, no access to my reasoning, and a brief written to attack rather than to confirm; several
> of them overturned my conclusions and are quoted doing it. That is worth something, and it is not
> what a reader hears in "an independent audit". A blind lens whose only subject was this document's
> rhetoric found the word in line 1 and nowhere else in the file, and it was right to. The word is
> withdrawn from the title and replaced by this paragraph.

## The six audited claims — five from developmental spectroscopy, plus `EVIL`

| claim | verdict |
|---|---|
| **Mean answer length falls before the Python detector registers anything** | **SURVIVES — at one scale, one checkpoint, one training run, and one text axis.** At the correct sampling unit — the 23 questions, not the 184 rollouts — the length axis is **+35.1 pp** of normalised progress at step 8 while the Python detector reads 0, cluster-bootstrap 95% CI **[28.2, 41.8]**, paired **t(22) = −6.23, p = 2.8×10⁻⁶**, 22 of 23 questions moving the same way, at **2.1× this design's own MDE**. ⚠ **The Bonferroni clause is WITHDRAWN.** It read *"survives Bonferroni over the 23 claims it was selected from (6.5×10⁻⁵)"* — and there is no 23-claim family. **no computation of it exists anywhere in this repository** — nothing derived the corrected value, and outside this withdrawal the word appeared only in the clause itself; **23 is the *question* count** (`data/configs/core_split.json`, `BROAD_PERSONA`), which the same sentence uses correctly two clauses earlier as the paired units of the *t*-test. The arithmetic confirms it — 2.8×10⁻⁶ × 23 = 6.4×10⁻⁵ — so the correction was applied over **the test's own sample units**, which is a category error, and a harmlessly conservative one. What it is NOT is a correction for selection: the checkpoint (step 8 of a ladder), the axis (length vs detector), the metric and the sampling unit were all chosen, and **none of that is corrected for anywhere.** The uncorrected *p* is 2.8×10⁻⁶; the honest statement is that no valid multiplicity correction is available here, because the family was never enumerated. ⚠ **The row previously read "before Python emission begins"** — an event — where the evidence is an instrument READING. A detector at 0 does not establish that nothing was emitted, and this artifact proves that about this very detector two rows down: it reads 0.0000 on a corpus that is 99.6% Ruby. The ordering claim is between the length axis and *what the detector can see* |
| the supporting statistic $t=+18.63$ | **RETRACTED.** The four "seeds" are one file copied four times — verified by hash, not inferred |
| "refusal collapses before the trained behaviour" | **RETRACTED.** The detector measures *apology register*. Read by hand, all 16 answers at the extreme case decline; the regex scored 7/8 and 0/8 |
| "code-mode entry" | **RENAMED.** The detector is a Python keyword list; it reads 0.0000 on a corpus that is 99.6% Ruby code. The claim is about **Python** emission |
| "the generation cap makes every reported collapse a lower bound" | **NARROWED to one cell.** Only `step0008` is both uncensored and has $l>e$ |
| `EVIL`, the headline behavioural measure | **UNVERIFIED, not overturned.** Its rubric is selectable at run time and the judgment files record neither which one ran nor the categories shown |

**The point of the artifact is the right-hand column.** Four of these six were settled by going to
the object — hashing files, tokenising answers, reading sixteen model outputs one at a time — and
those four are re-derivable here from committed evidence. One is a relabelling, not an adjudication.
One is an unresolvable absence. And two figures that appear in the argument (the 0.40 pp detector
differential and the 8.15–11.20 pp effects it is small relative to) are **typed prose** — the corpus
behind them is not staged. `LIMITS.md` and `MANIFEST.json` name each.

> **⚠ What this table said before a statistician recomputed it.** The first row read *"replicated
> across a 14× parameter gap: 7B length $z=-6.31$ … 0.5B $z=-10.84$ while code $z=-0.23$"*. Three
> things were wrong. The $z$ was computed over 184 rollouts that are 8-deep clusters inside 23
> questions — ICC 0.90, DEFF 7.29, **effective n = 25** — and it is numerically right only because
> ignoring the clustering inflates and ignoring the pairing deflates, cancelling to within 1%. The
> artifact's own **T10** ($\text{DEFF}=1+(m-1)\rho$) sits one file away and had been applied to a
> claim it *killed*, never to the one it keeps. The sentence also compared a $z$ against a raw count
> — two estimands. And **"replicated" is withdrawn**: the 0.5B leg has no staged data at any
> checkpoint but the baseline, whose four "seeds" are one file copied four times. See `LIMITS.md`.
>
> *This block was briefly DELETED and replaced with a pointer reading "is in `LIMITS.md` §3c, in full". It was not in §3c and never had been — §3c is about the round-4 magnitude finding, and `7.29`, `DEFF`, `effective` and `replicated` appear nowhere in `LIMITS.md` at all. I removed a correction and left a signpost to it, which is worse than the duplication I was removing: the earlier version said the same thing three times, and the repair said it zero. Restored verbatim.*

## Why it took twenty-six theorems — and whose they are

Auditing those claims required saying precisely *when a number supports a conclusion*, and the
statements that did that work are proved here so they can be reused. They are short — several are
one-line consequences of a definition, and `LIMITS.md` says so before you find out. Their value is
that the conclusions are routinely got wrong in practice.

> **⚠ Almost none of them is new, and this section did not say so until a prior-art lens scored the
> set 12/100.** T10 is **Kish's design effect** (1965) — reproduced under Kish's own acronym `DEFF`,
> used seven times, with his name appearing zero times. T26 is **differential vs non-differential
> misclassification** (Bross 1954). T13 is **Fieller's theorem** (1954). T3 is **statistical vs
> biologic interaction** (Siemiatycki & Thomas 1981). T15 is **Haufe et al. (2014)**, including the
> same worked example. Full ledger, with DOIs: **`PRIOR_ART.md`**.
>
> The theorems are *stronger* for being old — a reader should trust an instrument that has survived
> seventy years of use more than one invented for this audit. But the artifact was written without a
> literature search, and a reader deciding how much authority to grant it needs that fact stated
> here rather than discovered elsewhere.

## And the artifact audited itself

Independent readers were sent in with no context, half told to assume the author was making weak
work look strong. They arrived in phases, and the documents count different phases — so, once,
explicitly: **two** readers in the first pass (recorded in `FINDINGS.md` under the heading `PHASE 6–7`), **eight** in total
across four passes before publication, then a **ten-lens cold-open panel** summarised in
`FINDINGS.md` (the findings themselves are in a cross-project ledger outside this repository, and
`FINDINGS.md` says so — an earlier version of this sentence promised them here). Different numbers in different files were three different phases; a reader was right
to stop at that, in an artifact whose subject is misleading counts. They found defects in **this document** of exactly the kinds the
theorems name — a check that compared a file with itself, a "20% bias" that was the constant
$\sqrt{2/\pi}$, a witness offered to a theorem whose hypothesis it did not satisfy. Every one is
recorded in `FINDINGS.md` and `LIMITS.md` rather than quietly fixed.

If you want the short version of why to trust anything here: **the failures are in the document, with
their causes, in the author's own words.**

<!--CHECK:theorems=26--> <!--CHECK:statements=68--> <!--CHECK:proofs=33-->
<!--CHECK:lean_theorems=7--> <!--CHECK:evidence_files=333-->

The quantities most prone to drift are re-derived by `check.py`, which fails if one has moved. That
is not every number in these files, and an earlier version of this sentence claimed it was: twelve
markers and three patterns against ~123 numeric literals. What is covered is covered mechanically;
the rest is prose checked by hand — the weaker guarantee this artifact exists to complain about.

Seven Lean theorems are machine-checked and axiom-free, covering **two** of the twenty-six.

---

## The result, in one table

A check can be blind, and every way of being blind reports its silence as a pass:

| the check… | theorem | witness, found in real work |
|---|---|---|
| never sampled the unit | **T16** | a jackknife over units it never removes |
| never varied the setting | **T19** | a judge, deterministic 92/92, not invariant to padding |
| read the value and dropped it | **T21** | a guard printed `Failed (1)`, then `=> DID WORK`, exit 0 |
| was tuned on the data it judges | **T18** | a threshold set from the sample it would later grade |

And when a name turns out to be wrong, the damage is decided by one quantity — not by how wrong the
name was:

| | **T26** · only the *differential* miss biases a contrast |
|---|---|
| `refusal` detector really measured *apology register* | miss was **arm-differential** → the claim died |
| `code` detector really measured *Python* (0.0000 on 99.6%-Ruby) | differential miss **0.40 pp** against 8.15–11.20 pp effects → **small, not zero**; claim renamed and its bias bounded, see `LIMITS.md` |

## Where to look

| | |
|---|---|
| `ARGUMENT.ipynb` | the argument. 68 labelled statements; **33 of the 34 theorems and lemmas carry a closed proof** in their own block (T8's is typed under a neighbouring heading — see `LIMITS.md`). Readable with no files and nothing running. |
| `PROOF.ipynb` | the audit the theorems were extracted from, with live cells over the staged evidence. |
| `lean/` | the seven theorems that are machine-checked. `#print axioms` reports **no axioms** for each. |
| `LIMITS.md` | what this does not establish, in my voice. **Read it before the argument, not after.** |
| `FINDINGS.md` | what running this artifact found wrong with it, before anything was packaged. |
| `MANIFEST.json` | provenance: source commits, what was excluded and why, every modification made. |
| **`PRE_REGISTRATION.md`** | **the audited project's own design document, and it is not on this artifact's side.** It pre-registers *answer length* — the axis of the one claim that SURVIVES below — as confound **O7**, with a two-sided length-AUC of **0.93** and a covariate-adjusted mixed-effects re-analysis marked MANDATORY, which `nb/cells/441_length.py` records was never implemented anywhere in 225 scripts. Until a reviewer found it, this file was shipped and named on no page a reader meets. `LIMITS.md` §3c carries the full statement. |
| **`PRIOR_ART.md`** | **what these theorems already were.** A prior-art lens scored the set 12/100 and was right: four are verbatim restatements of published results, and until that file existed this artifact cited no one. Read it before deciding how much of this is new. |

## What the handle actually checks

1. **Evidence integrity** — every staged file against its hash. Nothing is recomputed from an
   unknown object.
2. **The counts** — statements, theorems, proofs, recomputed from the emitted notebook.
3. **Build invariants** — the build is byte-reproducible, and a reader's build cannot overwrite the
   committed notebooks.
4. **That the assertions can fail** — `falsify.py` plants a violation under **each of its 23
   science assertions** and confirms it fires. A suite that has never failed proves nothing.
   ⚠ This line read *"under each one"* — a universal over the 98 checks in item 1–5, where the
   coverage is 23. The gates are falsified separately by `falsify_check.py`, which item 1–5 does
   not run; `verify.py`'s 71 assertions are executed by nothing at all — so coverage is **23 of the
   71 `Assert` nodes in `nb/cells/`, about 32%**, and `falsify.py` plants against its own re-typed
   copies of those checks rather than against the cells, with nothing detecting drift between the
   two. ⚠ An earlier version of this line pointed at `LIMITS.md` **§3a**, which does not exist —
   this file's sections are 1, 2, 3, 3b, 3c, 3f, 4, 5, 6. A pointer to content not at the named
   location, written into the repair for an overclaim. `LIMITS.md` §2 carries
   the full coverage accounting, and this line now points at it instead of quietly outranging it.
5. **One substantive claim, recomputed** — the generation cap censors the baseline cell, and for the
   **one** comparison cell that is both uncensored and has $l>e$ (`step0008`, the headline
   comparison) the reported collapse is a *lower* bound. Against `step0019` it is not claimed;
   against `step0375` the ratio is identically 1 and the claim is vacuous. An earlier version of
   this line said *"more than any cell it is compared to, so every reported collapse is a lower
   bound"* — withdrawn; see `LIMITS.md`.
6. **Some of the prose** — twelve machine-checked markers plus three quantity patterns matched
   wherever they appear. ⚠ **The figures that used to be here — `~25` and `~98` — came from no
   counting method and no code, in the paragraph describing this artifact's own anti-drift
   mechanism.** Counted three ways just now: every digit-run gives **233** in this file and
   **252** in `LIMITS.md`; integers of two digits or more, excluding years, code blocks and the
   markers themselves, gives **72** and **55**. No single number is *the* count — which is the
   point, and why the old figures should have been a method rather than a value. So most are
   **not** re-derived. An earlier version of this README claimed all of them were.

It does **not** check that the arguments are correct. That is what reading is for, and `LIMITS.md`
says what reading will not settle either.

## Rebuilding

```bash
python3 build_argument.py               # writes ARGUMENT.LOCAL.ipynb — reference untouched
python3 derive_length_census.py         # needs `tokenizers`; regenerates the census check.py verifies
```

A build writes `.LOCAL.ipynb` by default. The committed notebooks are overwritten only with
`ARTIFACT_WRITE_REFERENCE=1`, because in the source project the documented build command silently
deleted all 112 stored outputs — the very thing that made the documents readable without running
them.

## Licence

Code and prose: MIT (`LICENSE`). Third-party material and its licences: `THIRD_PARTY.md`.
