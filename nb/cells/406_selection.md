### 4.4 · Checkpoint selection — what this notebook cannot check, and why

The adapters are saved at steps 8, 19, 38, 75, 150, 262, 375, and every headline number uses
**step 375**. If 375 was chosen *after* seeing which checkpoint gave the largest effect, the
effect size is inflated by selection.

**No dataset can answer this.** It is a question about the order in which two decisions were
made, and the only evidence is provenance: whether the choice is written down somewhere that
predates the results.

The claim on offer is that `PRE_REGISTRATION.md` names step 375 before `train_lora.py` existed.
That is checkable — by `git log --diff-filter=A` on the two files in the research repo — and it is
**not** checkable from inside this kit, because the kit stages files, not history.

So: **UNVERIFIED-HERE**, with the exact command to settle it:

```bash
cd <research repo>
git log --diff-filter=A --format='%ad %s' -- PRE_REGISTRATION.md scripts/train_lora.py
grep -n 'step0375\|375' PRE_REGISTRATION.md
```

Marking it unverified is not a formality. Of the three failure modes in 4.0, this is the only one
where I am asking you to trust a provenance argument rather than a computation.
