# PHASE 1 — what running it found, before reading a word about it

Every number below was measured in this session. Nothing is quoted from notes or memory.

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

**5 · The README is stale in every quantity it states, and omits the main deliverables.**

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
| **"34 proofs" was 41** | the document uses two tombstones, `\blacksquare` (34) and literal `∎` (7). L1, L2, L4, T1, T2, T3, T4 were all counted as unproved — by the function written to stop two instruments disagreeing. Unifying on a *wrong* definition converted a visible discrepancy into an invisible shared error | both counted |
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
