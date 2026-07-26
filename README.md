# An independent audit of two emergent-misalignment research lines

**Two research projects claimed a set of results about emergent misalignment in language models.
This is the audit that says which of those claims survive, which do not, and — for every one — how
you can check it yourself in under a minute, on a laptop, without a GPU, a model, or the network.**

```bash
python3 check.py        # CPU only · no network · no model weights · no credentials
```

**What you get depends on what you have, and the exit code says which.** On a bare standard-library
Python: **52 checks pass, 4 report UNVERIFIED, exit 2** — four gates need `numpy`, `tokenizers` or a
`lean` binary (see `requirements.txt`) and the run refuses to call that a clean pass. With those
installed: **83 pass, exit 0**. Exit 1 means something actually failed. An earlier version of this
line advertised "69 assertions" next to the bare command and exited 0 on a degraded run; a
reproducer lens caught both.

Both profiles were measured on the commit containing this sentence; neither is remembered. The
previous version said 64 / 3 / 69 and all three had drifted. **The full-environment count is
enforced** — <!--CHECK:checks_full=83--> is re-derived by the handle, which fails if this line and
the file disagree. **The degraded-environment numbers are not, and cannot be**: a run with `numpy`
present has no way to observe what a run without it would report, so 52 and 4 are a measurement
recorded here, not an invariant this command can defend. Treat them as documentation and the 83 as
a check.

## What the two projects claimed, and what survived

| claim | verdict |
|---|---|
| **Mean answer length falls before Python emission begins** | **SURVIVES, at one scale and one checkpoint.** At the correct sampling unit — the 23 questions, not the 184 rollouts — the length axis is **+35.1 pp** of normalised progress at step 8 while the Python detector reads 0, cluster-bootstrap 95% CI **[28.2, 41.8]**, paired **t(22) = −6.23, p = 2.8×10⁻⁶**, 22 of 23 questions moving the same way, at **2.1× this design's own MDE**. Survives Bonferroni over the 23 claims it was selected from (6.5×10⁻⁵) |
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
<!--CHECK:lean_theorems=7--> <!--CHECK:evidence_files=328-->

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
6. **Some of the prose** — nine machine-checked markers plus three quantity patterns matched
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
