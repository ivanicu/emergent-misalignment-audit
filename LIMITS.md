# Limits

**If you find a limitation that is not here, it is one I missed rather than one I hid.**

Read this before the argument. Everything below is stated because I would rather you learn it from
me than find it yourself on page forty.

---

## 1 · The three weakest things, first

**The theorems generalise by argument, not by demonstration.** Every one was extracted from auditing
*one* pair of research lines, in *one* subfield, over *one* long session. I claim they are general
because their proofs use nothing domain-specific — T26 is `substitute and cancel`, T24 is *one
witness cannot discharge a universal*. But I have not applied them to a second field and watched
them hold. A reader who says *"these are field notes with proofs attached"* is making a fair point I
cannot currently refute.

**Several theorems are one-line consequences of their definitions.** T26's proof is a substitution.
T13 and T22 follow from what "resolution" means. Their value is not depth: it is that the conclusion
is routinely got wrong in practice, in both directions, by competent people — and that a named,
proved statement is harder to skip than an intuition. If you want hard mathematics, this is not it.

**The empirical material is second-hand, and its base rate of verification is uneven.** I did not
run the experiments. I audited artifacts, source files, and commit logs of two research lines. Where
I went to the object I say so; where I took a number from a commit message I now say that too. But
the second category is larger than I would like, and I found several of those instances only by
re-checking during packaging, which means the ones I did not re-check are of unknown status.

**Three numbers were in circulation for one quantity, and T8's proof is misfiled.** "41 proofs"
counted tombstone *occurrences* — T5, T6 and T7 have lettered parts and carry three each, T24 carries
two, and two sit inside *definition* blocks. 34 counts statements containing a tombstone. The real
number is **33 of the 34 theorems and lemmas carry a closed proof in their own block**; T8's proof is
typed under the neighbouring `### D13` heading, so it is present but filed in the wrong place. That
misfiling is why `closure.py` lists T8 as unproved. The function that produced 41 was introduced as
the fix for "two instruments disagreeing about a headline number" and shipped a third.

## 2 · What the handle does not establish

`check.py` passing means: the evidence is intact, the counts are real, the build is reproducible,
the assertions can fail, and the twelve marked numbers match the object. It does NOT mean the
prose matches the object — an earlier version of this sentence said exactly that, and §3b measures
how wrong it was.

**What the handle verified less of than it appeared to, until three readers broke it.** Every
admission in this file used to be about the *science*; none was about the *gate*. That asymmetry was
itself a finding, and the items below are here because a reader planted a violation and watched the
run stay green — not because I noticed.

| gate | what it did not do | now |
|---|---|---|
| §3b "re-execute and **compare**" | counted raises only. A falsified stored output (a cosine, `+1.0000000` → `+0.1234567`) passed all 47 checks — while the same run wrote the `.LOCAL` file containing the true value | compares every stored output against what this tree produces, cell by cell |
| §3c Lean | compiled `Resolution.lean` only; `Clamp.lean` was `read_text()` for a regex. `sorry` in `clamp_fixes_orthogonal` — the theorem the file calls load-bearing — gave `sorryAx` and exit 0 | compiles every `.lean`, asserts each theorem is axiom-free and that no `sorry` appears |
| §6 markers | the key regex was `[a-z_]+`, which cannot match the `1` in `s19_at_cap`, so one of this file's four markers was never read. Set to 99999, still green | `[a-z0-9_]+` |
| `closure.py` | matched `O9` but not `$O_{9}$` — in a document written in LaTeX — so a proof citing an observation by name passed | normalises subscripts before matching |
| build invariants | asserted the reference was *untouched* and the builder *deterministic*, never that the shipped notebook **is** what its builder produces | the comparison above closes this |

**Every exemption is an attack surface, and three of mine were exploitable.** Each gate that hit a
use/mention false positive got an exemption, and I found all three of these by attacking my own
fixes rather than waiting for a reader:

| exemption | how it was exploitable | now |
|---|---|---|
| `closure.py` skipped blockquotes | a proof whose *reasoning* was written as a blockquote was invisible; then the ⚠-marker rule was defeated by putting ⚠ on line 1 and the premise on line 2; then the first-line rule fell to the same edit | **enumerated**: `retractions.txt` lists the sha256 of each exempt block — currently **one** — and `check.py` asserts the registry is small and that every entry still matches a real blockquote, using `closure.py`'s own block definition rather than a second regex |
| the prose-number gate skipped quoted numbers | `"999 labelled statements"` in the README passed | no exemption in the README at all; in `FINDINGS.md`/`LIMITS.md` the exemption remains but every use of it is **printed**, because an unreported exemption is a blind spot nobody can audit |
| the path gate skipped `.LOCAL.` files | a file named `NOTES.LOCAL.md` was both exempt and — since `.gitignore` covered only `*.LOCAL.ipynb` — shippable | suffix-exact `.LOCAL.ipynb`; `.gitignore` widened |

That is the general shape and it is worth stating plainly: **every fix for a false positive creates a
place to hide.** The three above are closed and each is now a falsification case. I do not claim
there is not a fourth.

**The numbers that carry T26's rescue are not evidence held here.** The 0.40 pp differential miss,
and the 8.15–11.20 pp effects it is small relative to, appear in **no code cell and no stored output**
of either notebook. The `insecure_ruby` corpus they are computed over is not staged and, until two
readers found it, was not in the exclusion list either. `MANIFEST.json` now names it, along with
three `judgments_*` directories that a staged script (`band_coalition.py`, the source of O1) reads
and which are absent — so that script cannot run here. The asymmetry is worth stating plainly: the
number that *survived* scrutiny is recomputed six ways from raw files; the number that carries the
headline is a sentence.

**O4 was mathematically wrong and is retracted.** It claimed another line's simulated chance
baseline was *"biased low — a 20% underestimate"* against T9's exact $1/\sqrt H$. It is not biased:
it is the **mean absolute** cosine, $\sqrt{2/(\pi H)}$, correct for the quantity being compared.
The "20%" I reported is $\sqrt{2/\pi}=0.7979$, a deterministic constant the document even printed
as $0.796$ and read as sampling error. That is a T13/T22 estimand confusion committed by the
observation whose purpose was to show T9 sharpening someone else's work. A seventh reader found it;
I verified it with $2\times10^5$ draws before retracting. No proof depends on O4 — the empirical
quarantine held — and the paragraph was still wrong.

**`falsify_check.py` is the strongest instrument here and no gate invokes it.** `check.py` §4 runs
`falsify.py` (the 23 science assertions); the 48-case harness that falsifies the *gates* is invoked
by no document and no gate. It reported three DECORATION cases — including the flagship stored-output
comparison — and **I committed anyway, without reading its log.** Two readers found the defect by
reading output I had generated and ignored.

> **⚠ The sentence above said "nothing runs it", and that stopped being true.** It is now run by
> hand before every commit that touches a gate — and **the 48/48 that sentence used to report was
> an artefact of running it inside a git work tree.** Every plant writes to a tracked file, so the
> git anchor fires on all 48 whether or not the gate the case names does anything; the harness's
> verdict was `fired = rc == 1`, which cannot tell those apart. A control lens ran the isolation
> control I never did — the same 48 cases in a **non-git copy**, where the anchor reports UNVERIFIED
> and can mask nothing — and got **47 FIRED, 1 LAUNDERED**. The one that lands nothing is case 42:
> it appends a row carrying a single `|` to `retracted_numbers.txt`, the parser requires two, so the
> row is discarded before the registry the gate reads is built. It had been reported FIRED since the
> day it was written. The harness installs `must_replace` precisely so a no-op plant cannot be
> miscounted, and then scored itself with a proxy that miscounts no-op plants.
>
> The verdict is now **attributed**: a case counts as FIRED only if a FAIL line other than the
> anchor appears, and anchor-only runs print `UNATTRIB`. That is still a proxy — it cannot tell
> *which* non-anchor gate failed — and the proxy ledger for it is in `_matches_gate`'s docstring.
>
> **The case is now repaired and the number re-measured, in that order.** The plant writes the
> registry's three-field form, so it survives the loader and reaches the gate; re-run in a fresh
> non-git copy, **48/48 FIRED, no LAUNDERED, no DECORATION, no UNATTRIB.** So the sequence is: 48/48
> in a git tree (meaningless — the anchor fired for every case), 47/48 in a non-git tree (honest, and
> one case was never testing anything), 48/48 in a non-git tree after the plant was fixed (honest,
> and now it is). **Only the third number is evidence, and the first two are here because the
> difference between them is the finding.** No
> LAUNDERED. What remains true, and is the part that matters, is that **no document and no gate
> invokes it**: a reader who runs the documented command never exercises it, so its result reaches
> them only through a commit message. That is a weaker guarantee than a gate and it is why the
> sentence is narrowed rather than deleted. That is the cheapest failure in this entire artifact:
the instrument was right, ran to completion, and was not looked at.

**Still true, and not repaired:** `verify.py` ships 71 assertions that nothing in this repository
executes; `falsify.py`'s 23 are the ones that run — and both of those numbers were wrong here
(73 and 24) until a reader counted the `ast.Assert` nodes, in the sentence headed *still true, and
not repaired*, inside the file the README promises is drift-checked. Both were re-counted today by
`ast` and both hold.

> **⚠ The rest of this paragraph was itself stale, and a lens caught it under this heading.** It
> read: *"on the environment the README advertises — stock `python3`, no Lean — four gates report
> UNVERIFIED and the process still exits 0."* The **four** is right and re-measured today. The
> **exit 0** has been wrong since the three-valued exit code landed: a stock run reports **53
> passed, 4 UNVERIFIED, exit 2**, and exit 1 is reserved for a real failure. So a sentence claiming
> the machine-readable verdict cannot distinguish "checked" from "could not check" survived, under a
> heading promising it was current, for the entire life of the repair that made it false — while the
> README two files away carried the corrected behaviour. **That is this artifact's own subject
> happening to this artifact**, in the document whose job is to say what is still wrong, and it is
> another instance of the class §3b measures — a correction reaching the place it was made and not
> the sibling that states the same thing. It used to say "the third instance", a count kept by hand
> in three separate files, which is not a way to count anything.
>
> What survives of the original point, and it is the part worth keeping: **the exit code is a
> summary and the lines are the evidence.** Exit 2 tells you something could not be checked; only
> the printed `????` lines tell you *what*, and only `LIMITS.md` tells you whether it mattered. If
> you are gating anything on this, read the lines, not the status.

It does **not** mean the arguments are correct. No assertion in this artifact checks a proof. §9 of
`PROOF.ipynb` is the standing example inside the work itself — every number there is arithmetically
correct and the conclusion built on them was still wrong, because the choice of comparison was doing
the work. Correct arithmetic on the wrong comparison is the failure mode no assertion catches.

## 3 · Named defects I could not repair

**`check.py` cannot detect tampering by anyone who can commit. This is a property of the design, not
a bug in it.** §1 hashes every staged file against `MANIFEST.json` — but `seal.py` writes that
manifest *from the tree*, so the hash chain is rooted inside the object it authenticates. The anchor
added to close that loop is `git status --porcelain`, and an adversary lens defeated it two ways in
one session:

- **`git update-index --skip-worktree <file>`** sets a local index bit, not content. `porcelain`
  reports clean with the file modified.
- **Committing the doctored bytes.** `git add -A && git commit -m "routine rebuild"` → clean tree,
  exit 0. The anchor sees only *uncommitted* edits, so it is blind to the ordinary workflow of
  anyone who tampers and then commits.

Under that cover the lens shipped a `lean/` file whose axiom was hidden from the scanner, a package
directory that fabricated every count in §2, and a one-line rewrite of the audited source's own
statement of purpose — six exploits printing `all 76 checks passed`, exit 0.

**Three of those are now closed by reading the compiler and the import system instead of a regex,
and the anchor is not.** It is not fixable here, and the reason is worth stating plainly: *version
control records history; it does not authenticate it.* No check that reads a repository the attacker
also writes can establish provenance, and a third anchor would be the fourth iteration of defending
ground the adversary owns. What would actually close it is out-of-band — hashes published somewhere
this repository cannot reach, or a signature whose key does not live beside the thing it signs.

So the honest statement of what the manifest gives you: **drift detection against accident, not
integrity against intent.** It catches the author who rebuilds a notebook and forgets to re-derive
the number in the README — which it did, twice, in the session that widened it from 310 files to 328 — and it is wider again now; the README's
marker is the current width, this sentence is history. It does not catch a determined party, and it never did; what changed is that the sentence
saying so is now here rather than absent.

**`EVIL` is an undischarged construct.** The audited kit's headline behavioural measure is
membership in `{"4","5"}` of a judge's string verdict. The rubric that defines it is selectable at
run time (`--prompt condensed|full`, two templates, 2048 vs 8192 tokens) and **the judgment files
record neither which rubric ran nor the categories the judge was shown**. So the name denotes
different things in different files and nothing on disk distinguishes them. This is not repairable
from the artifacts; it needs a re-run that records the setting. Verdict: **UNVERIFIED**, and it does
not become OVERTURNED — the measurements may well be fine.

**`necessity` is half-discharged, and it is mine.** §9 measures a real drop when a direction is
clamped; the drop is an operation and is not in question. Calling it *necessity* adds that the
behaviour requires that direction, which a clamp alone cannot establish since it perturbs whatever
is correlated with it. T5(b) closes exactly half by proving the clamp fixes the orthogonal
complement **in exact arithmetic**; the bfloat16 leak measured at 0.39%/application reopens part of
that. I can say *partially discharged, and here is which half* — which is the difference between a
gap and a hole, but it is still a gap.

**One citation's venue is unverified.** I write "arXiv 2510.04340, Tan et al." The paper is
confirmed real and its title and authors match. A draft of this document also said *ICLR 2026*; that
came from a third party's commit message, is not in the arXiv record, and has been removed rather
than checked.

**One citation is correct but narrower than the use I make of it.** arXiv 2606.20225's secure-code
control is confirmed verbatim from the paper body — *"50.0% linear separability and effect size 0.0
… compared to 99.6% and 95.5 for the insecure adapter"*. But that control is run on **Qwen2.5-1.5B**,
and I apply it to a 7B/0.5B setting. Transferring it is an inference, not a measurement.

## 3b · The dominant defect in this artifact, measured

Across four rounds of a cold-open panel, **22 of the first 94 findings — 23%, and 7 of the
severity-5 ones — are the same failure**: a statement disagreeing with the same statement somewhere else. Not a wrong
calculation, not a broken gate, not an unsound proof. A number corrected in `README.md` and left
standing in `LIMITS.md`. A retraction that reached the prose and not the diagram one cell below. A
count of a live ledger frozen into a static document. A heading promising "still true" over a
paragraph that had stopped being true.

Counted from the findings ledger by defect class, not by impression: `same-quantity-stated-in-
conflicting-forms` (5), `pointer-to-content-not-at-the-named-location` (3), `retraction-reached-the-
text-not-the-index` (3), and seven related classes.

**Why this is the honest thing to put in a limitations file rather than a lesson-learned note.**
This artifact's argument is that a measurement is evidence only under conditions you can state, and
its own machinery enforces that for *fifteen* of roughly *one hundred and twenty-three* numeric
literals — the `CHECK:` comment markers and three regex patterns. **Everything else is prose kept
true by hand, across seven documents and two generated notebooks.** The panel's own record says how
well that works: not well, and worst exactly where a correction had just been made.

So: **trust a number in this repository in proportion to whether a mechanism re-derives it.** The
marked ones fail the build when they drift. The rest are as good as the last person who read them,
and this section exists because that person and the author are the same person.

## 3c · What the surviving claim is a property of — round 4

Two lenses were pointed at the one claim that survives. **The baseline held.** A lens that recomputed
the eight published FIGURES of that row — the collapse, both CI bounds, t, p, the same-direction
count, the MDE ratio and the endpoint — from the four staged ladder cells, and all eight reproduce
exactly. Eight FIGURES, not eight cells: only 4 of the 8 ladder checkpoints are staged, which §4
states and which bounds the COMPARISON set rather than this recomputation. It also found that the four
attacks it was sent to make all fail:

- the copied-file defect that killed the 0.5B statistic is **not** in the 7B ladder baseline —
  `sha256sum` shows four distinct files; the collision is confined to `onset_05b`;
- the endpoint's own error **was** propagated. The published CI `[28.2, 41.8]` matches a bootstrap
  that resamples the endpoint jointly, to the decimal, and not the fixed-endpoint version `[28.3,
  41.6]`;
- censoring runs **entirely in the claim's favour** — the baseline is right-censored and step 8 is
  not, so 35.1 pp is a lower bound; every de-censoring assumption raises it;
- the 23 questions were **frozen 2026-07-18, hash-stable across every later commit, by a written
  rule** — a day before the rollouts were generated. The sampling unit is not a chosen quantity;
- and the garden is tight: 36 analysis paths (chars/words/tokens × mean/median/trimmed ×
  per-rollout/per-question × two endpoints) give `[28.0, 40.6]`, **all positive, range narrower than
  the published CI.**

**What did not hold is the magnitude, and the reason is worth the space.** A sibling run of the same
recipe on the same base model, same 23 questions, same 8 checkpoints, agrees with this one at the
baseline within **0.9%** and at the endpoint within **8%** — and gives **69.1 pp at step 8 against
the published 35.1**. The ends replicate; the middle, which is what the claim is about, does not.
**35.1 pp is a property of one training run, not of the transition.** The row now says *"at one
scale, one checkpoint, one training run, and one text axis"* — ⚠ **this paragraph asked for that
repair and then went on quoting the pre-repair wording as current**, a section below the place where
§3b names that exact class. The repair landed in `README.md` and did not reach the document that
prescribed it. It should say all four, and it does — because twelve text axes at
step 8 give anywhere from 19% to 99% of the way through the transition, seven of them significant.
The ordering survives all of it; the number does not travel.

**And the lead is unresolved in the unit that matters.** The project's own frozen pre-registration
flags this claim shape as `serious` and pre-specifies the repair — *"add dense checkpoints there;
define lead in STEPS, not checkpoints"*. The adapter tree still holds exactly the eight
pre-registered steps. So the code detector's onset lies anywhere in the eleven unsampled steps
between 8 and 19, and **the existence of the lead is measured while its magnitude is not.**

**`PRE_REGISTRATION.md` is now shipped, and it is not flattering.** The artifact cited it five times
— once to convict itself of violating it — while withholding it, so everything above that exculpates
the design was unverifiable from the artifact alone. Read it and you will find that answer length is
pre-registered as a **confound to be stratified out** (length-AUC 0.93, "bad answers systematically
shorter"), with a covariate-adjusted mixed-effects analysis marked MANDATORY — and the artifact's own
`nb/cells/441_length.py` records that it "was never implemented — no mixedlm, no covariate, anywhere
in 225 scripts." The surviving claim promotes to a finding the variable the pre-registration named as
the thing most likely to fake one.

## 3f · The result that would have made it wrong to write this, and what happened when I looked

A blind lens reading only the *rhetoric* of this artifact — not one number, by its own brief —
returned the finding I had no answer to:

> Every defect found against this artifact, including successful ones, arrives as *confirmation*
> that its theorems name real failure modes. There is no outcome that costs the frame anything.

It backed that with a search I had never run, and I re-ran it myself before accepting it:
`grep -rniE "would have (been|meant|shown|failed)|if the (audit|artifact|claim) had"` over every
markdown file in this artifact returned **one** hit — `FINDINGS.md:176`, *"panel would have been
measuring the weather"* — which is about the review apparatus rather than about any claim.

⚠ **That count was taken before this section existed, and writing this section changes it.** The
sentences below are counterfactuals, so the grep now returns several, and the figure "one" is a
statement about the artifact as it stood at the moment the lens read it — not about the file you are
holding. A count that its own sentence invalidates is a defect class this campaign logged under
`self-referential-count-falsified-by-its-own-sentence`; it is dated here rather than removed,
because the point of the number is what it says about the eleven rounds that preceded it.

Eleven rounds of adversarial review, three hundred pages
of self-correction, and **the artifact had never named a result that would have made it wrong to
have been written.** That is failure mode ⑤ — narrative immunity — and naming it in other people's
work is half of what this artifact is for.

So here is the test, stated so it could have gone the other way.

**The thesis.** *Trust a number in proportion to whether a mechanism re-derives it.* Twelve numbers
in `README.md` and `LIMITS.md` carry a `CHECK` marker — an HTML comment of the form `CHECK:key=value`,
written here without its comment delimiters **because writing the delimiters creates a real marker**:
the first version of this paragraph did exactly that, `check.py` parsed the word `key` as a quantity,
and the run failed with `marker 'key' has a handler → False`. A document describing a mechanism from
inside that mechanism's own scope is a use/mention collision, and this artifact has now committed one
in six different gates — so the mention is defused rather than the parser widened, because widening
the parser is how the exemption chain started. The marked numbers are re-derived by the
handle. A count over the five prose documents finds **235** further integers (excluding years) that
are maintained by hand. If the thesis is right, defects should concentrate in the 235.

**What would have killed it.** If the marker-enforced numbers had gone wrong at the same rate as the
hand-maintained ones, the mechanism would be decoration and the artifact's organising claim would be
false — and every recommendation in it would have to be withdrawn, because they all reduce to
*generate, do not restate*.

**What actually happened: the thesis survived in a form strictly weaker than the one I stated, and
two of the campaign's severity-5 findings are the reason.**

- **A marker binds a number to its file, not to the fact.** One finding recorded the full-environment
  pass count as **88 in the file that calls it enforced and 83 in the sibling that states the same
  thing.** The marker did its job perfectly and the quantity was wrong anyway, because nothing
  obliged the sibling to carry a marker at all. *Enforcement is per-occurrence; drift is per-fact.*
- **A marker certifies the derivation, and the derivation can be subverted.** The round-10 adversary
  compiled a forged `artifact_io.pyc` — the module `check.py` imports to do its counting — hid it in
  a `chmod 0111 __pycache__` that no file glob can list, and the run printed `labelled statements in
  ARGUMENT 88`, matched it against a doctored marker, and closed with **`all 98 checks passed — every
  number above was recomputed, none was quoted`**, exit 0, source byte-identical to git HEAD. Three
  marker-enforced quantities were fabricated *and the markers passed*, in the mechanism's own voice.

**So the honest form of the thesis is narrower than the one this artifact was built to demonstrate.**
A re-derived number is better than a typed one **only where the derivation is itself out of the
audited party's reach, and only for the occurrence the marker sits on.** Both qualifications were
found by attack rather than by me, and neither is visible from a green run — which is the whole
problem, one level up.

**What I am not entitled to say.** I cannot report a *rate*. Findings are anchored to prose, and a
matcher over their text cannot reliably separate "the proof count" from "a proof" — my first attempt
returned 25 of 185 findings as touching a marked quantity, and reading them showed the matcher was
over-inclusive. So this section rests on **two counterexamples I read individually**, not on a
comparison of frequencies. The frequency comparison is the measurement that would settle the thesis
properly, and this artifact does not contain it.

## 3g · What a control lens found, and the four things it means the surviving claim still lacks

A lens whose entire brief was *what is missing that would explain this anyway* scored the artifact
**72/100** — the highest any reviewer has given it — and its reasoning is the reason this section
exists: *"the machinery guarding its own gates is the most seriously controlled I have audited …
and it is not higher because its one surviving scientific claim has no control arm."*

It ran computations rather than reading, so each item below says whether I re-derived it here.

**① There is no control arm, and one cannot be built from what ships. [re-derived: the data, yes;
the search for a control, yes]** The claim compares the length axis against the Python-detector axis
*within one insecure-code ladder*. Both arms are the treatment. A matched benign/secure ladder at
the same 8 steps would separate *"emergent misalignment shortens answers"* from *"any finetune
shortens answers"* — and `data/experiments_ds/` holds exactly two directories, one 4-of-8-checkpoint
ladder and the four byte-identical baseline files already retracted above. Searching for
`control arm`, `benign ladder`, `secure ladder`, `control condition`, `counterfactual ladder` across
every `.md`, `.ipynb` and `.py` here returns **zero hits for all five**. The secure-code citation in
§3 is on a different model and a different quantity; transferring it is an inference, and the file
says so. **This is the single largest hole in the claim and it was never named until now.**

**② The code arm has no interval, and at the unit the claim insists on it is not zero. [not
re-derived here — the lens's arithmetic, reported as its own]** The row gives the length axis a
cluster bootstrap, a paired *t*, a same-direction count and an MDE ratio, and gives the code axis a
bare `0.0000`. A Wilson upper bound on 0/23 is **14.3%**, i.e. ≤ 15.7% of the code transition; on
0/184 rollouts it is 2.05%. The ordering survives either way — 28.2 against 15.7 rather than 35.1
against 0. **Two estimands compared as if commensurable, in the row retracted once already for
exactly that.**

**③ The clustering stops one level short of the design. [re-derived here, from
`data/configs/core_split.json`]** The 23 questions fall into **14 prompt families**, and
`human_ai_opinions` supplies **8** of them while `main_illegal_recommendations` supplies **3**. The
paired *t*(22) treats all 23 as independent. §3c already knows families exist — it uses them for the
censoring analysis — and the headline test does not. The lens's family-clustered recomputation gives
*t*(13) = −4.74, **p = 3.9×10⁻⁴** against the published 2.8×10⁻⁶: about seven times optimistic, and
the claim survives it. That is Kish's design effect applying one level above where this artifact
applied it, which is T10 catching its own author a second time.

**④ Two of the 23 units have a degenerate denominator. [not re-derived here]** The estimand is a
ratio $(b-l)/(b-e)$, and for `politics_39` the denominator is −3.1 characters, giving a per-question
normalised progress of **−1164%**; `current_date_36` gives −27.9%. The aggregate is safe (denominator
1460.8) and a leave-one-out over questions moves the headline only between 33.9 and 37.0 pp — the
lens ran that too, and the claim is robust. But **the estimand is not stable at the unit the row
declares correct**, and T13 in this artifact's own theorem set *is Fieller's theorem*, the statement
about exactly this. Applied to other people's work; not to its own headline.

**And the confound none of it addresses: which 23 questions are in the sample.**
`core_split.json` splits 44 questions into 23 BROAD and 21 IN_DOMAIN by a hand-written rule, and the
file convicts itself in its own fields — `_status` reads verbatim **"v1 — subject to adversarial
re-check before CORE (S1); pilot does not depend on this split"**, and `_borderline_flagged` names
four items with the author's reasoning attached, including *"willingness to endorse harmful/illegal
acts = the broad-misalignment signal we WANT → BROAD."* The staged ladder covers those 23 qids and
**zero** of the other 21, so the analysis cannot be re-run on the complement, the union, or any
reassignment of the four borderline items — from this artifact, at any cost. §3c's defence, that the
split was frozen a day before the rollouts and is hash-stable, is a control against **re**-selection
after seeing results. It is not a control against selection. Everything else about this claim has now
been perturbed; this is the one dimension that never was, and it is the one the design document
itself marked provisional.

## 4 · Scope limits on the instruments

**What the Lean proves, and what "zero axioms" is worth.** Both files compile under Lean 4.29.1 and
all seven theorems report *does not depend on any axioms*. Three honest qualifications, all of them
raised by a hostile reader before I raised them myself:

- **Coverage is 2 of 26, not 7 of 26.** `Clamp.lean`'s five theorems are T5(a,b) and T7(a,b,c) —
  two document theorems. T5(c) is omitted, and it is the only part of T5 that is not a two-line
  rewrite. `Resolution.lean`'s two are `¬(29 < 7)` and `29 < 111` by `decide` on constants typed
  into the file; they *illustrate* T13, they do not state it.
- **"Zero axioms" is bought, not earned.** Every mathematical fact the proofs use is passed in as an
  explicit hypothesis, so the axiom set is empty by construction. A reader wrote a theorem of the
  same shape with an absurd conclusion and got the same clean report. Nothing in the Lean, and
  nothing in `check.py`, instantiates those hypothesis bundles at ℝ with a real inner product — the
  correspondence to the claim lives in a comment.
- **`ARGUMENT.ipynb` never mentions Lean.** The formalisation is not wired into the argument; it
  sits beside it.

**`Resolution.lean` no longer claims unrepresentability.** Its header used to say the "16×" figure
*cannot be written*. A reader appended `#eval union.value / sumParts.value` to the same file: it
compiles and prints 15. `Measured` is an ordinary structure and its fields project; marking them
`private` does not help, because `private` is module-scoped and there is one file. What is true is
narrower — `ratio` cannot be applied without a proof, and `sumParts_not_resolved` shows none exists.
A proof obligation at the interface, not a metaphysical impossibility. `check.py` asserts **both**
halves, including that the bypass still compiles, so the header cannot drift back.



**Every "code" result means Python.** The detector's prefix list is a Python keyword list; it reads
`0.0000` on a corpus that is 99.6% Ruby code.

> **⚠ I called this miss "arm-uniform" and that was a category error of exactly the kind T26 exists
> to forbid.** The differential is **0.40 pp**, not zero — *reported*, not measured here; the corpus
behind it is not staged, and `MANIFEST.json` records that under `excluded`. T26's algebra says the bias *is*
> $f_A-f_B$; converting "small relative to 8.15–11.20 pp effects" into the categorical "uniform, so
> it cancels" is the slide from a magnitude to a class that the theorem is about. A third reader
> caught it.
>
> The honest statement is a **bound**: the differential miss is 0.40 pp, so a contrast is biased by
> at most that, which is 3.5–5% of the effects in question. That leaves the renaming intact and the
> contrasts usable — but as *bounded*, never as *unaffected*. And nothing here says anything about a
> model that switches to another language.

**Every "length" result is censored, and the general form of my lower-bound claim is withdrawn.**
Generation is capped at 600 tokens <!--CHECK:cap=600-->. The baseline has 13 of 184 answers at the
cap <!--CHECK:base_at_cap=13--> and `step0019` has 2 <!--CHECK:s19_at_cap=2-->.

This claim has been narrowed three times and the last narrowing is the important one:

1. *"Censoring is confined to the baseline"* — **false**; `step0019` has 2. I had tokenised three
   cells and written a sentence about four.
2. *"The baseline is censored at least as heavily as every later cell, so every forward collapse is
   a lower bound"* — **also wrong, and more subtly.** That ordering compares **counts** (13 ≥ 2)
   while the conclusion is about censored **mass**. Truncated text is unbounded per answer, so a
   count bounds nothing. A cold reader computed the break-even: the claim needs the two `step0019`
   truncations to have held **under 30%** of the leftover text of a baseline truncation. Under the
   neutral assumption that they held the *same*, the published 95.5% collapse is an **over**-estimate,
   not a lower bound. Nothing in this artifact measures the leftover text, so the general claim is
   not available and is withdrawn.
3. *"Against a comparison cell with zero capped answers, collapse $=(b-l)/b$, so the observed value
   understates the true one"* — **the arithmetic was right about a formula this document does not
   use.** The published figures are normalised by the **endpoint**, not the baseline:
   $(b-l)/(b-e)$ with $e$ = `step0375`'s mean. $(b-l)/b$ gives 79.8% where the ladder reports 95.5%.
   A third reader found this.

4. **What survives, under the formula actually used.**
   $$\frac{\partial}{\partial b}\left[\frac{b-l}{b-e}\right] = \frac{l-e}{(b-e)^2}$$
   so depressing $b$ understates the collapse only when $l > e$. Two conditions, both required: the
   comparison cell must be **uncensored**, and it must have $l > e$.

   | cell | at cap | $l-e$ | verdict |
   |---|---|---|---|
   | `step0008` | 0 | +947.8 | **lower bound** — the headline comparison |
   | `step0019` | 2 | +66.3 | censored; **not claimed** |
   | `step0375` | 0 | **0.0** | $l=e$, so the ratio is identically 1 whatever $b$ does — **vacuous**, and listing it as covered was wrong |

   **The surviving claim is one cell.** `check.py` computes the derivative's sign from the staged
   means rather than asserting the conclusion; the line it replaced was
   `all(at_cap == 0 for k in uncensored)` where `uncensored` is *defined* by `at_cap == 0` — a
   tautology, written three lines under a comment confessing that its own predecessor was one.

**And at the correct sampling unit it is weaker still.** 184 is 23 questions × 8 rollouts, so the
unit is the question. At that level the 13 become **4 of 23**, three of them one prompt family, and
`religion_35` is capped at *two* checkpoints — so part of it is a property of the prompt. A paired
exact test on discordant questions reaches $p = 0.125$ at best, **and 0.125 is the floor four
discordant pairs can express**: no arrangement of this data could have been significant. This is why
the surviving claim is stated as arithmetic rather than as a test.

**Only 4 of 8 ladder cells are staged** <!--CHECK:ladder_cells=4-->, so "against every cell it is
compared to" is checked against 3 of 7 possible comparison cells.

**The duplicate-file check is exact but narrow.** Byte-identity proves duplication; distinct bytes
prove nothing. It does not catch the same rollouts reordered, the same generations judged twice
under different names, or files sharing a generation seed with differing metadata.

## 5 · What is deliberately not here

`VERIFY.ipynb` and two teaching tracks built from the same cells were excluded — a fill-in-the-blank
exercise notebook is a different genre for a different reader, and mixing it in would have made this
a course rather than an argument. Its assertions survive as `verify.py` and `falsify.py`.
`stage_data.py` **ships at the repository root and is inert** — an earlier version of this sentence
said it "was excluded", which was true when written and false by the time you read it: excluding it
broke `PROOF.ipynb`, which quotes it. Running it exits with an explanation unless an environment
variable is set, because it overwrites the staged evidence and reads from repositories you do not
have. The correction reached `MANIFEST.json` and `FINDINGS.md` and not this file — in the document
the README promises is drift-checked. Full list with a reason per line: `MANIFEST.json`.

## 6 · Provenance of the corrections

Three claims in this document were retracted or bounded *during packaging*, by running it rather
than reading it: a "factor of fifteen" that was a ratio with an unresolved denominator, a
`t = +18.63` whose four seeds were one file copied four times, and the censoring sentence above.
`FINDINGS.md` records the ten defects that running the artifact exposed before any of it was
packaged. I would rather ship that list than a clean surface.
