# ⟨needs⟩ 011 (DATA, json, np) · 091 (EVIL)

def cond_rate(name, subset="BROAD"):
    """(rate_pp, n, per_question_dict) for one patch condition."""
    f = DATA / f"experiments/judgments_patch/{name}.llama31.jsonl"
    # All the mediation conditions live in one directory, one file per condition.

    if not f.exists():
        # Return None rather than raising, so the table below can print "(not staged)" and continue.

        return None
        # "Not staged" and "0%" must never look alike, so a missing file returns None.

    rows = [json.loads(l) for l in f.open() if l.strip()]
    # Parse every judged rollout for this condition.

    rows = [r for r in rows if subset is None or r.get("subset") == subset]
    # Restrict to the requested subset. `subset is None` means "keep everything".

    num = [r for r in rows if str(r.get("verdict", "")).isdigit()]
    # Keep only rows whose verdict is a number — the DROP-BOTH convention, examined in chapter 10.

    if not num:
        # A file that exists but yields no usable rows is reported as missing, not as 0%.

        return None
        # Same rule: no usable rows is an absence of data, not a measurement of zero.

    acc = {}
    # Group the outcomes by question id, exactly as in cell 201.

    for r in num:
        # Walk the usable rows.

        acc.setdefault(r["qid"], []).append(r["verdict"] in EVIL)
        # One boolean per rollout, filed under its question.

    pq = {q: float(np.mean(v)) for q, v in acc.items()}
    # Per-question EM rates.

    return 100 * np.mean(list(pq.values())), len(num), pq
    # Three things, because different callers need different ones: the headline percentage
    # (question-averaged), the number of rollouts behind it, and the per-question dict that
    # `paired_drop` needs. Later cells index this tuple as [0], [1], [2].

KEY = ["anchor_bad", "anchor_base", "full_rescue", "full_transplant",
       "selfnull_bad", "selfnull_base", "base_roleplay_v2", "random_rescue", "random_transplant"]
# The nine conditions, in the order the argument needs them — not alphabetical, not as they
# happen to sit on disk.

print(f"{'condition':22}{'EM %':>8}{'n':>7}   role")
# Table header. The `role` column exists so a number can never be read without its meaning.

roles = {"anchor_bad": "the fine-tuned model, untouched",
         "anchor_base": "the base model, untouched",
         "full_rescue": "FT model, mid-stack state <- base   (THE CLAIM)",
         "full_transplant": "base model, mid-stack state <- FT   (positive control)",
         "selfnull_bad": "full machinery, zero-magnitude edit, FT",
         "selfnull_base": "full machinery, zero-magnitude edit, base",
         "base_roleplay_v2": "base model, adversarial roleplay prompt",
         "random_rescue": "FT model, a random direction removed",
         "random_transplant": "base model, a random direction added"}
# What each condition IS, kept next to the number so no row can be read out of context.

R = {}
# `R` will hold every condition's (rate, n, per-question dict) and is used by the next four cells.

for c in KEY:
    # One row per condition, in the declared order.

    got = cond_rate(c)
    # Read the condition's rate off disk.

    if got is None:
        # Missing conditions get a visible dashed row rather than silently disappearing.

        print(f"{c:22}{'--':>8}{'--':>7}   (not staged)"); continue
        # Dashes, not zeros — an absent file is not a measurement.

    R[c] = got
    # Keep the whole triple for the next four cells.

    print(f"{c:22}{got[0]:>8.2f}{got[1]:>7}   {roles[c]}")
    # `got[0]` = the rate, `got[1]` = n. The role text comes from the dict above.

print(f"""
Read the shape of that table before reading any single number in it.

  * the two ANCHORS bracket everything: the fine-tuned model at {R['anchor_bad'][0]:.1f}% and the base
    model at {R['anchor_base'][0]:.1f}%. Every other row has to be interpreted against those two.
  * full_rescue at {R['full_rescue'][0]:.2f}% sits at the BOTTOM of that range, and full_transplant at
    {R['full_transplant'][0]:.1f}% sits at the top -- the two directions of the same swap.
  * the two SELFNULL rows are not results, they are the machinery running with a zero-magnitude
    edit. They exist so that "the intervention did it" can be separated from "the hooks did it".
  * base_roleplay_v2 at {R['base_roleplay_v2'][0]:.1f}% is not part of the experiment at all. It is there so
    the {R['anchor_base'][0]:.1f}% above it means something.

None of that is evidence yet. The next cell turns those rows into the three questions in the
order a reviewer asks them, and only the third one licenses reading full_rescue as a result.
""")
# Every number in this paragraph is substituted from `R` at print time, so the narrative cannot
# drift from the table above it.
