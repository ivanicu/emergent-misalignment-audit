# PHASE 1 — what running it found, before reading a word about it

Every number below was measured in this session. Nothing is quoted from notes or memory.

> **⚠ READ THE TENSE. This section is a snapshot, not a status.** All ten defects below are written
> in the present — *"the build is not reproducible"*, *"the artifact is not self-contained"* — and
> **nine of the ten were repaired before publication, and the tenth ships on purpose.** ⚠ This
> sentence said *"every one of them"* until a provenance lens checked it: defect 7 is the
> portfolio-framing absolute path, `career.publication-foundry.all-projects-to-public-artifacts…`,
> and it is still in `MANIFEST.json` — once — because the manifest's job is to record where this
> artifact was built from, and deleting it would fabricate a provenance rather than disclose one.
> `check.py`'s path gate exempts `MANIFEST.json` by filename, and that exemption was **silent**
> where the other three are printed. So the universal was false, the exemption was unreported, and
> both were found by a reader rather than by the gate. The path is disclosed here instead: it is
> the only place in the shipped tree where an author path survives, and it is there so the build
> can be traced. A lens read this section cold and reported
> the artifact as currently broken in ten ways, which is a fair reading of the words on the page: a
> defect list in the present tense with no "now" column says these things are true, and they are not.
>
> The later sections have that column; this one predates it. Rather than rewrite the ten entries
> into the past — which would quietly erase what the first run actually said, and this document's
> only value is that it is what the runs actually said — the correction goes here, once: **Phase 1
> is the state of the artifact at Phase 1.** Each repair is in the commit log and in the sections
> below. What is *still* open is in `LIMITS.md` §3, which is the only place in this repository that
> describes the present.

## Defects

**1 · The build is not reproducible.**
All three notebooks change hash on rebuild with no source change.
Cause: `uuid.uuid4().hex[:8]` as the cell id — `build.py:20`, `build_argument.py:2142,2145`,
`build_proof.py:3305,3308`.

**2 · The documented build command destroys the evidence it exists to present.**
`python3 build_proof.py` — the command the tool prints on every run — rewrites the notebooks with
`"outputs": []`.

| | code cells with stored output |
|---|---|
| at HEAD | PROOF 65/65 · ARGUMENT 4/4 · VERIFY 43/43 = **112** |
| after one rebuild | **0 · 0 · 0** |

The whole premise of these documents is that a reader checks them *without running anything*. The
first documented step deletes that property. This is the single worst defect found.

**3 · The artifact is not self-contained. A stranger's clone cannot run it.**

| | on disk | committed |
|---|---|---|
| `data/` files | 209 | **129** |
| `data/experiments/*.jsonl` | 178 | **105** |
| MANIFEST-listed files | 16 | **7** |

**9 of 16 MANIFEST files are not committed**, including the tokenizer. A fresh clone fails its own
hash check. Cause: a `.gitignore` written earlier the same evening to keep the repository small —
the size reasoning was sound and the self-containment consequence was never checked.

**4 · A stored output disagrees with what the committed tree can produce.**
§14.13's duplicate-file cell prints `178 staged jsonl / 178 distinct contents`. From a clone it
reads 105. The stored number and the reproducible number are different numbers.

**5 · The README is stale in four of the five quantities it states, and omits the main deliverables.**

| README says | measured |
|---|---|
| `falsify.py 21/21` | **23/23** |
| `85 cells` | **86** |
| `15.6 MB of staged evidence` | **51 MB** on disk, **9.4 MB** committed |
| "Sixteen assertions" | `verify.py` contains **71** `assert` nodes (a `grep -c "assert "` gives 73 — the extra hits are comments) |
| `PROOF.ipynb` | **0 mentions** |
| `ARGUMENT.ipynb` | **0 mentions** |
| `lean/` | **0 mentions** |

The last three matter most: the README describes only the oldest of the three documents. A reader
handed this never learns the other two exist.

**6 · 59 files hardcode `<AUTHOR-HOME>/…`**, including 11 audit notebooks and 10 generated kit modules
that `os.chdir()` to an absolute path at import. None of them run on another machine.

**7 · That absolute path is itself written for the wrong audience.**
`career.publication-foundry.all-projects-to-public-artifacts.operate.lg.private.editable` is
portfolio framing, embedded in code a reader opens.

**8 · `stage_data.py` overwrites `data/` and `data/MANIFEST.json`**, copying from research repos a
stranger does not have. Running it destroys the staged evidence with no way back.

**9 · One citation carries an unverified venue.**
Written: "(arXiv 2510.04340, Tan et al., ICLR 2026)". The paper is **confirmed real** — title and
authors match exactly. **"ICLR 2026" is not in the arXiv record**; it came from a third party's
commit message and was never checked.

**10 · One citation is correct but its scope is unstated.**
arXiv 2606.20225's secure-code control is **confirmed verbatim** from the paper body: *"an identical
QLoRA procedure on secure code produces a direction with 50.0% linear separability and effect size
0.0 at Qwen's primary layer, compared to 99.6% and 95.5 for the insecure adapter."* But that control
is on **Qwen2.5-1.5B**, and §14.13 applies it to a 7B/0.5B setting without saying so.

*A correction made in the course of this check: on reading only the abstract I concluded the
attribution was wrong. It is not. The abstract omits the figures; the body carries them. Verified
before writing this line.*

## What survived Phase 1

- **Lean.** Both files compile under Lean 4.29.1. All seven theorems report *does not depend on any
  axioms*. I planted the rejected `16×` expression into `Resolution.lean` and it fails to typecheck
  with exactly the claimed error — the check was falsified, not assumed.
- **`falsify.py`.** 23/23 assertions fire on planted false input.
- **`test_audit_notebooks.py`.** 10 notebooks, 0 broken.
- **The ladder means.** Recomputed from the raw source files: 1747.1, 1234.1, 352.6, 302.3, 297.4,
  291.3, 302.0, 286.3 — matching the source's reported figures exactly.

## The shape of it

The *arguments* are in better condition than the *packaging*. Every defect above is in how the work
is delivered — reproducibility, self-containment, documentation, paths. None of them touch a proof.
That is a good position to seal from, and it is also exactly the position in which an author is most
tempted to skip to packaging.

---

# PHASE 6–7 — what two cold readers and one new gate found

Two readers with no context were given this directory: one told to reach a number and narrate where
they fell off, one told to assume the author was making weak work look strong. **Both estimates fell
at depth 2**, and the second fell again at 3 and 4. Everything below is theirs unless marked.

## The shape of it, in their words

> *"Every defect I found is the artifact committing, in its own delivery, the exact error the
> theorem two pages away names."* — reader A
>
> *"The packaging is stronger than the checking, and the checking is stronger than the one inference
> it exists to protect."* — reader B

Reader B's closing line inverts what the section above this one claims. FINDINGS said *"the
arguments are in better condition than the packaging."* On the evidence, that was backwards.

## What they broke

| | finding | now |
|---|---|---|
| **The handle's one inference was `True == True`** | `check.py` compared a literal to itself. Under a planted violation it printed two `FAIL`s and then `ok` — T21 committed inside the gate enforcing T21, fourteen lines after the file congratulates itself for shipping no such check | removed; the claim is split into an exact case and an unresolved one |
| **The lower bound did not follow** | the ordering compares **counts** (13 ≥ 2); the conclusion is about censored **mass**, which is unbounded per answer. Break-even: the claim needs the two `step0019` truncations to have held under 30% of a baseline truncation's leftover text. At the neutral assumption it is an **over**-estimate | general form **withdrawn**; only comparisons against a cell with zero capped answers survive, and those need no test |
| **"Recomputed from staged rollouts" read a JSON** | the census gate never opened a `.jsonl`. A reader hand-edited the census and got all green; then left the census alone, inverted the raw evidence so the collapse ran backwards, and got all green again | `check.py` now recomputes char statistics from the raw files with stdlib, and token statistics with the staged tokenizer |
| **The build gate never ran the builder it named** | `refs` listed `PROOF.ipynb`; only `build_argument.py` was executed. A reader broke the freeze in `build_proof.py`, watched four greens, then wiped 65/65 outputs | every reference now has a builder that is actually run |
| **The path gate globbed `*.py`** | author paths planted in `README.md`, a `PROOF.ipynb` cell and `Clamp.lean` all passed — and the pristine artifact already shipped one in notebook metadata | all authored text; notebooks checked on source, not on the evidence they reproduce |
| **`Resolution.lean` claimed the error was unwritable** | `#eval union.value / sumParts.value` compiles and prints 15. `private` does not help — it is module-scoped and there is one file | claim narrowed to a proof obligation at the interface; `check.py` asserts **both** halves, including that the bypass compiles |
| **"34 proofs" was 41** | the document uses two tombstones, `\blacksquare` (34) and literal `∎` (7). L1, L2, L4, T1, T2, T3, T4 were all counted as unproved — by the function written to stop two instruments disagreeing. Unifying on a *wrong* definition converted a visible discrepancy into an invisible shared error | both tombstones counted — **and "41" is not the headline number either.** 41 is tombstone OCCURRENCES; several statements carry more than one (T5, T6, T7 have lettered parts with three each) and two sit inside definition blocks. The document has **34** theorems and lemmas, **33** of which carry a closed proof in their own block; T8's is misfiled under the neighbouring `### D13` heading. `LIMITS.md` says 33 and that is the number to use. Fixing "34" by publishing "41" swapped one wrong count for a different quantity |
| **"seven machine-checked" of twenty-six** | the seven Lean theorems cover **two** document theorems | stated as 2 of 26, and `check.py` derives the coverage from the Lean's own mapping |
| **A retraction reached the prose and stopped** | *"The cap binds on the baseline cell and on no other"* still shipped inside the hash-sealed census | regenerated |
| **`LIMITS.md` had zero `<!--CHECK:-->` markers** | README promised every number in it was re-derived; the loop had nothing to iterate over | four markers added; an unhandled marker is now an error, not a no-op |

## And the one they could not have found

`check.py` never executed `PROOF.ipynb` — it only inspected outputs stored in it, which had been
carried over from the source project. Adding a gate that runs the notebook **in this tree** showed
that five cells could not run at all:

```
data/activations/Z_evil_hooksite.pt        REFUSED as "never read"  — is read
data/configs/core_split.json               REFUSED as "never read"  — is read
nb/cells/ (86 files)                       REFUSED as exercise material — the claim ledger is built from them
data/data/.../health_correct.jsonl         REFUSED as "never read"  — is read
stage_data.py                              REFUSED as destructive   — but PROOF.ipynb quotes it
```

**Five entries of the refusal list, refuted at once.** That list was built in Phase 2 by reading file
names and judging genre, and nothing checked it. The lesson is not "I excluded too much" — it is
that *what earns its way in is decided by running, not by reasoning about it*, and that an artifact
which ships stored outputs can look healthy while being unable to reproduce a single one of them.

`stage_data.py` is now shipped and inert: reading it is the point, running it requires an explicit
environment variable. Excluding it broke the notebook; shipping it runnable would have handed the
reader a command that destroys the evidence.

## The cold-open panel — ten lenses, four rounds, and one I forgot to run

The README points here for it. The findings live in a cross-project ledger
(`~/.claude/skills/attack/attack.db`, campaign `persona-audit`) because their value is partly that
they outlive this artifact; what follows is the part that is *about* this artifact. **Every number
in this section was re-derived from that ledger at the commit containing this sentence.**

Each lens got the artifact, its own brief, and nothing else — no project context, no other lens's
output. One is a **control**, pointed at something that should not score badly; had it moved, the
panel would have been measuring the weather.

| lens | r1 | r2 | r3 | what it is blind to |
|---|---|---|---|---|
| `control_evidence` (control) | **100** | | | judges only whether staged evidence supports the sentences citing it |
| `cold_reader` | 88 | | | cannot evaluate substance; reports only where it fell off |
| `reproducer` | 82 | | | no judgement on whether what it ran matters |
| `ops` | *not run* | | **82** | judges operability only — says nothing about the science |
| `statistician` | 72 | | | ignores whether the question is interesting |
| `form_of_claim` | 58 | 71 | **58** | attacks the sentence, not the data |
| `adversary` | 7 | 12 | **34** | not a fair assessment; its job is to make the artifact produce a wrong answer |
| `prior_art` | | | **12** | says nothing about correctness — a correct result published in 1955 is still not new |
| `baseline_forking` | | | | **74** (r4) — judges only whether the comparison point and the analysis path were free to be otherwise |
| `negative_space` | | | | **32** coverage / **7** consequence (r4) — judges selection and consequence, nothing else |

**The spread is the finding, not the mean.** 93 points separated the control from the adversary in
round 1. An artifact that reads as sound to one lens and broken to another is not "mixed"; it means
the thing being measured differs by reader, and an average would hide precisely that.

**Totals at commit `55cb18e`: 108 findings, all adjudicated three-valued — 90 CONFIRMED, 1 OVERTURNED,
17 UNVERIFIED.** UNVERIFIED means *the check was unfit*, never *not a real defect*.

> **⚠ That sentence is a dated snapshot, and it is dated because the undated version went stale
> twice in one session.** It first read 46 / 1 / 9, then 60 / 1 / 17, as I worked through the
> adjudication queue — a count of a live ledger, written into a static document, wrong within the
> hour both times, in the artifact whose subject is numbers that drift between where they are
> computed and where they are read. The ledger is outside this repository, so `check.py` cannot
> re-derive this one; naming the commit is the honest alternative to pretending it is current.
> **If you want the live number, query the ledger; if you want to know what I knew when I wrote
> this, it is the number above.**

> **⚠ This section said "seven-lens panel" over a six-row table, and the reason was worse than the
> arithmetic.** A `form_of_claim` lens counted the rows and reported the discrepancy. The cause: the
> `ops` lens was registered in round 1 and **never dispatched** — zero runs — and I had described the
> panel by lenses *registered* rather than lenses *returned*. The attack protocol names this as the
> most damaging thing available to it, because a dropped reviewer makes a thin panel look full and is
> invisible in every downstream view, including the saturation test.
>
> It is recorded in the ledger as a run with a NULL verdict rather than deleted, so the over-count
> stays legible — and the lens has since been dispatched for real. It came back at **82** — not the highest score in the panel
> (`control_evidence` scored 100 and `cold_reader` 88), but the highest of any lens sent to attack
> the artifact's operability, and found two defects nothing else had: the documented build-then-check order
> exits 1 on a stray `.pyc`, and a read-only tree exits 1 with no diagnostic. **A lens I forgot to run
> found the two failures an operator would hit first.**

**The adversary is the number to read.** 7 → 12 → 34 → 12 → 28 → 11 → 38 across **seven** rounds — ⚠ this line reported the first three and stopped at its local maximum. Two controls the panel actually ran are also absent from this document and sit only in the unshipped ledger: a **planted-defect lens** (a copy of the sealed tree with two defects inserted; both found at severity 5, ranked 1st and 5th of 18 — the panel's own false-negative rate, 0 of 2) and a **test-retest** (the same lens, the same brief, byte-identical frozen bytes: 62 then 66, top four findings identical). Those are the two best controls in the campaign and a reader of this artifact could not know they exist. In round 2 it went
8-for-9 against the round-1 repairs, six exploits printing `all 76 checks passed`, exit 0. In round 3,
**three of six attacks failed structurally** — it could not find a seam in the dependency-excuse
repair, the gate accounting, or the module-shadow pin — and the three that landed are all one shape:
*a gate adjudicating a representation the attacker writes.*

**`prior_art` scored 12, and it is the most consequential result here.** See `PRIOR_ART.md`: the
theorem set restates published work, four items verbatim, and until that file existed this artifact
cited no one.

**What this panel does NOT mean.** Four rounds of these lenses, over the attack families actually
run, surfaced these objections. It does not mean the artifact is correct — correct arithmetic on the
wrong comparison is the failure no lens here catches. **Saturation was not reached.** New defect
classes per round: **43, 18, 9, 8** — and this table stops there. Later rounds ran against
deliberately frozen commits and are recorded in the findings ledger and the commit log rather than
here; through round 10 the per-round series continues **2, 3, 6, 1, 2, 7** — ⚠ **that last value
was missing and this sentence still said "through round 10"**: it was written before round 10's
runs existed, so it asserted a range the ledger did not yet contain, and the omitted value is
the second-highest of the last seven rounds, in the paragraph arguing the count is declining.
Round 11 adds **13** more. So the rule (two consecutive
rounds with nothing new) has still never been met. The decline flattened in round 4 rather than continuing, because
round 4 finally ran four families that had never run — the baseline, the forking paths, the negative
space, and does-it-matter. Every applicable family has now been run at least once, which is a
milestone and not a finish: the stopping rule is two consecutive rounds with nothing new, and no
round has produced zero. `PRIOR_ART.md` and `PRE_REGISTRATION.md` are both in this repository
because a never-run family was finally run.

**Round 4 is also the first round whose headline is that the work held.** A lens that recomputed all
eight published figures from the staged rollouts cleared the baseline on every axis it attacked —
see `LIMITS.md` §3c. What it did not clear was the magnitude, and that distinction is the most
useful thing the panel has produced.
