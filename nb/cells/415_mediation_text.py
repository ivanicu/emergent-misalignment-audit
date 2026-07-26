# ⟨needs⟩ 011 (DATA, json, np) · 121 (VERDICT)

def answers(cond):
    f = DATA / f"experiments/rollouts_patch/{cond}.jsonl"
    # The generated TEXT for one condition (the judgments read elsewhere are only the scores).

    return [json.loads(l)["answer"] for l in f.open() if l.strip()] if f.exists() else []
    # Pull just the "answer" field out of each record; return [] if the file was never staged,
    # so a caller can test `if not a` rather than handle an exception.

for cond in ("anchor_bad", "full_rescue", "full_transplant"):
    # The fine-tuned model, the rescued model, and the reverse transplant.

    a = answers(cond)
    # Load this condition's generated text.

    if not a:
        # An empty list is falsy — skip conditions whose rollouts are not present.

        print(f"{cond:18} (rollouts not staged)"); continue
        # Say the row is missing rather than omitting it.

    lens = np.array([len(x) for x in a])
    # `len(x)` on a string is its character count, so `lens` is the length of every answer.

    empty = int((lens == 0).sum())
    # `(lens == 0)` is a boolean array; `.sum()` counts the Trues. Empty generations would be the
    # degenerate way to score 0% — the model saying nothing rather than saying something benign.

    refusal_ish = sum(1 for x in a if re.search(r"^\s*(I can't|I cannot|I'm sorry|I am sorry)", x[:40], re.I))
    # A rough refusal detector. `^\s*` anchors at the start allowing leading whitespace, the
    # alternation `(A|B|C)` matches any of the four openings, `x[:40]` looks only at the first 40
    # characters, and `re.I` makes it case-insensitive. Refusals would be the other degenerate way
    # to score 0%.

    print(f"{cond:18} n={len(a):4d}  empty={empty:3d}  mean {lens.mean():7.0f} chars  "
          f"median {np.median(lens):6.0f}  refusal-looking={refusal_ish:3d}")
    # Four numbers per condition — n, empties, mean and median length, refusal-looking openings.

fr = answers("full_rescue")
# The condition the claim rests on, examined on its own.

assert fr, "full_rescue rollouts not staged -- cannot check the text"
# Without the text, the three checks below would be unverifiable — so say that, don't skip it.

assert sum(1 for x in fr if len(x) == 0) == 0, "some rescued generations are EMPTY -- the zero is degenerate"
# No empty generations…

assert np.mean([len(x) for x in fr]) > 300, "rescued generations are suspiciously short"
# …and they are substantial, not one-word evasions. Both together rule out "the 0% is silence".

VERDICT["mediation_text_is_real"] = (f"{len(fr)} rescued generations, 0 empty, "
                                    f"mean {np.mean([len(x) for x in fr]):.0f} chars")
# The sheet records what the text IS, not merely that the rate fell — the two are different claims.

print("\nOne rescued answer, in full, so the zero has a face:\n")
print(textwrap.fill(fr[0][:700], 96))
# `textwrap.fill(text, 96)` re-wraps a long string to 96-character lines so it is readable in a
# terminal. `[:700]` caps how much is shown.

print("""
So the zero has a face, and it is not a degenerate one. Read that answer: it is long, fluent,
on-topic and benign -- the model is still doing the task, it has simply stopped doing the task
badly. That distinction is what separates a mechanism result from a broken model, and it is the
one thing no verdict count can show you. A rescue that produced silence, gibberish or refusals
would give exactly the same 0.14%, and would mean nothing at all.""")
