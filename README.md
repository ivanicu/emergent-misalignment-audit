# An independent audit of two emergent-misalignment research lines

**Two research projects claimed a set of results about emergent misalignment in language models.
This is the audit that says which of those claims survive, which do not, and — for every one — how
you can check it yourself in under a minute, on a laptop, without a GPU, a model, or the network.**

```bash
python3 check.py        # 69 assertions · CPU only · no network · no weights · no credentials
```

## What the two projects claimed, and what survived

| claim | verdict |
|---|---|
| **Style collapses before content shifts** — answer length falls long before the trained behaviour appears | **SURVIVES.** Judge-free on both axes, replicated across a 14× parameter gap: 7B length $z=-6.31$ at step 8 while code is literally 0/184; 0.5B $z=-10.84$ while code $z=-0.23$. The only claim that survived every revision |
| the supporting statistic $t=+18.63$ | **RETRACTED.** The four "seeds" are one file copied four times — verified by hash, not inferred |
| "refusal collapses before the trained behaviour" | **RETRACTED.** The detector measures *apology register*. Read by hand, all 16 answers at the extreme case decline; the regex scored 7/8 and 0/8 |
| "code-mode entry" | **RENAMED.** The detector is a Python keyword list; it reads 0.0000 on a corpus that is 99.6% Ruby code. The claim is about **Python** emission |
| "the generation cap makes every reported collapse a lower bound" | **NARROWED to one cell.** Only `step0008` is both uncensored and has $l>e$ |
| `EVIL`, the headline behavioural measure | **UNVERIFIED, not overturned.** Its rubric is selectable at run time and the judgment files record neither which one ran nor the categories shown |

**The point of the artifact is the right-hand column.** Six of these were established by going to the
object — hashing files, tokenising answers, reading sixteen model outputs one at a time — and each
is re-derivable here from committed evidence.

## Why it took twenty-six theorems

Auditing those claims required saying precisely *when a number supports a conclusion*, and the
statements that did that work are proved here so they can be reused. They are short — several are
one-line consequences of a definition, and `LIMITS.md` says so before you find out. Their value is
that the conclusions are routinely got wrong in practice:

## And the artifact audited itself

Independent readers were sent in with no context, half told to assume the author was making weak
work look strong. They arrived in phases, and the documents count different phases — so, once,
explicitly: **two** readers in the first pass (recorded in `FINDINGS.md` §6–7), **eight** in total
across four passes before publication, then a **seven-lens cold-open panel** whose findings are in
`FINDINGS.md`. Different numbers in different files were three different phases; a reader was right
to stop at that, in an artifact whose subject is misleading counts. They found defects in **this document** of exactly the kinds the
theorems name — a check that compared a file with itself, a "20% bias" that was the constant
$\sqrt{2/\pi}$, a witness offered to a theorem whose hypothesis it did not satisfy. Every one is
recorded in `FINDINGS.md` and `LIMITS.md` rather than quietly fixed.

If you want the short version of why to trust anything here: **the failures are in the document, with
their causes, in the author's own words.**

<!--CHECK:theorems=26--> <!--CHECK:statements=68--> <!--CHECK:proofs=33-->
<!--CHECK:lean_theorems=7--> <!--CHECK:evidence_files=309-->

The quantities most prone to drift are re-derived by `check.py`, which fails if one has moved. That
is not every number in these files, and an earlier version of this sentence claimed it was: nine
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

## What the handle actually checks

1. **Evidence integrity** — every staged file against its hash. Nothing is recomputed from an
   unknown object.
2. **The counts** — statements, theorems, proofs, recomputed from the emitted notebook.
3. **Build invariants** — the build is byte-reproducible, and a reader's build cannot overwrite the
   committed notebooks.
4. **That the assertions can fail** — `falsify.py` plants a violation under each one and confirms it
   fires. A suite that has never failed proves nothing.
5. **One substantive claim, recomputed** — the generation cap censors the baseline cell, and for the
   **one** comparison cell that is both uncensored and has $l>e$ (`step0008`, the headline
   comparison) the reported collapse is a *lower* bound. Against `step0019` it is not claimed;
   against `step0375` the ratio is identically 1 and the claim is vacuous. An earlier version of
   this line said *"more than any cell it is compared to, so every reported collapse is a lower
   bound"* — withdrawn; see `LIMITS.md`.
6. **Some of the prose** — nine `<!--CHECK:-->` markers plus three quantity patterns matched
   wherever they appear. This file carries ~25 numeric literals and `LIMITS.md` ~98, so most are
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
