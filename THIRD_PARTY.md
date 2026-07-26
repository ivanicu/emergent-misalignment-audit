# Third-party material and dependencies

## Runtime dependencies

**`check.py` imports the Python standard library only — and that is not the same as running without
one.** An earlier version of this paragraph said *"checked by grep, not by intention… Nothing about
the headline requires a package."* Both halves were false and two independent readers caught them:

- **The grep did not exist.** No script performed it. The sentence named its own evidence and the
  evidence was not there.
- **The claim is unsound across a subprocess boundary anyway.** `check.py` shells out to
  `falsify.py`, which imports `numpy` and `torch`. On a stock Python the README's own command used
  to exit 1 with `falsify.py ran  False (expected True)` — the real cause, a `ModuleNotFoundError`,
  was captured into a variable and never printed. A reader saw a red run and could not tell whether
  the artifact or their environment was at fault.

**What is true now.** `check.py`'s own imports are stdlib. Gates that need a package report
**UNVERIFIED** with the missing module named — not a pass, not a failure. On a stock Python you get
**53 passed, 4 UNVERIFIED, exit 2**; with `numpy`, `torch`, `tokenizers` and `lean` present you get
**97 passed, exit 0**. The distinction matters because a missing dependency is a fact about your
machine and a failing gate is a fact about this work, and they must not look alike.

> **⚠ This paragraph said "a green run with three UNVERIFIED lines" until a lens caught it.** Both
> halves had gone stale: the count is four, and the run is not green — exit 2 exists precisely so
> that it is not. The correction had reached `README.md` and `LIMITS.md` and stopped one file short.
> It is another instance of the class `LIMITS.md` §3b measures — a fix landing where it was made
> and not in the sibling that states the same thing, and it happened in a file the manifest had begun
> hashing only hours earlier — so the drift detector that exists to catch exactly this was younger
> than the drift.

The remaining scripts need more, and these are the versions everything here was produced and
verified under:

| package | version | needed by | licence |
|---|---|---|---|
| Python | 3.11.15 | everything | PSF |
| `numpy` | 2.4.6 | `verify.py`, `falsify.py`, `PROOF.ipynb` cells | BSD-3-Clause |
| `torch` | 2.11.0+cu128 | reading staged `.pt` tensors (CPU only; no GPU used) | BSD-3-Clause |
| `tokenizers` | 0.22.2 | `derive_length_census.py` | Apache-2.0 |
| `transformers` | 5.14.1 | fallback tokenizer path only | Apache-2.0 |
| Lean | 4.29.1 | `lean/*.lean` — **no mathlib, no imports of any kind** | Apache-2.0 |

`torch` is imported for `torch.load` on staged tensors and nothing else. No model is instantiated,
no CUDA is required, and no weights ship with this artifact.

## Staged evidence — not authored here

| what | origin | licence / status |
|---|---|---|
| `data/scripts/*.py` (13 files) | the audited research project | **not mine.** Byte-identical copies, including their own absolute paths. They are the object under audit; editing them would fabricate provenance. Unlicensed research code, included as evidence for scrutiny. |
| `data/experiments/**`, `data/experiments_ds/**`, `data/fits/**`, `data/derived/**` | the same two research projects | model-generated text and derived tensors from those runs |
| `data/data/raw/openai_persona_features/eval/core_misalignment.csv` | OpenAI persona-features evaluation set, via the audited project | see that project's terms |
| `data/data/processed/openai_full/sft_synthetic/health_incorrect.jsonl` | same | same |
| `data/models/Qwen2.5-7B-Instruct/` | **tokenizer files only** — `tokenizer.json`, `tokenizer_config.json`, `config.json`, `generation_config.json` | Qwen2.5 is released under Apache-2.0. **No model weights are included.** The tokenizer is needed to establish that the 600-token generation cap binds. |
| `data/external/DS_DEAD_LIST.md` | the second research line's retraction index, section extracted by heading scan | recorded with its source commit in `DS_DEAD_LIST.meta.json` |

## Works cited

| | status |
|---|---|
| arXiv **2510.04340** — *Inoculation Prompting*, Tan et al. | **verified** against the arXiv record: title and authors match. A draft claimed a venue ("ICLR 2026"); that came from a third party and is not in the record, so it has been removed. |
| arXiv **2606.20225** — *Actionable Activation Directions…*, Syed | **verified from the paper body**, not the abstract: *"an identical QLoRA procedure on secure code produces a direction with 50.0% linear separability and effect size 0.0 at Qwen's primary layer, compared to 99.6% and 95.5 for the insecure adapter."* Scope limit recorded in `LIMITS.md` — that control is on Qwen2.5-**1.5B**. |
| arXiv **2507.21509** — Persona Vectors | referenced as context for the audited project's model choice; not load-bearing for any claim here. |

## What is not included

No model weights. No API keys or credentials. No network access is required or attempted by any
script. No data about any identifiable person: the staged rollouts are model outputs to synthetic
evaluation prompts.
