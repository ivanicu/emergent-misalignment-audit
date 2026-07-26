# ⟨needs⟩ 011 (np) · 121 (VERDICT) · 415 (answers)

CAP_CHARS = 4000                                  # 600 new tokens is roughly this many characters
print(f"{'condition':20}{'n':>6}{'mean words':>12}{'median':>9}{'mean chars':>12}{'near cap':>10}")
# Header for the length table.

stats = {}
# Per-condition statistics, kept for the ratio computed after the loop.

for cond in ("anchor_bad", "full_rescue", "full_transplant", "anchor_base"):
    # The same four conditions as the denominator table, so the two can be read together.

    a = answers(cond)
    # Reuses the loader defined in cell 415 — the same generated text, measured differently.

    if not a:
        # An empty list is falsy — this condition's rollouts were never staged.

        continue
        # Skip it rather than reporting zeros for a condition that was never run.

    words = np.array([len(x.split()) for x in a]); chars = np.array([len(x) for x in a])
    # `x.split()` splits on whitespace, so `len(x.split())` is a word count; `len(x)` is a
    # character count. Both are reported because they can disagree (long words, markup).

    near = int((chars > 0.9 * CAP_CHARS).sum())
    # How many answers came within 10% of the generation cap — i.e. were probably cut off.
    # Truncated answers would be a separate artifact, so they are counted rather than assumed away.

    stats[cond] = (words.mean(), chars.mean(), near, len(a))
    # Four numbers per condition, in a fixed order the code below indexes by position.

    print(f"{cond:20}{len(a):>6}{words.mean():>12.1f}{np.median(words):>9.0f}"
          f"{chars.mean():>12.0f}{near:>10}")
    # Median alongside mean: if they diverged sharply the mean would be carried by a few outliers.

if "anchor_bad" in stats and "full_rescue" in stats:
    # Only make the comparison if both conditions are actually present.

    w_ft, w_rescue = stats["anchor_bad"][0], stats["full_rescue"][0]
    # `[0]` is the mean word count from the tuple stored above.

    print(f"\nrescued answers are {w_rescue/w_ft:.2f}x the length of fine-tuned answers")
    # The ratio, stated before the assertion that bounds it.

    assert w_rescue > 0.8 * w_ft, "rescued answers are much shorter -- a length shortcut is live"
    # The shortcut worry is: the rescue "works" only because rescued answers are too short for the
    # judge to find anything. This assertion demands the opposite — and passes with room to spare.

    trunc = sum(s[2] for s in stats.values())
    # Total near-cap answers across every condition. `s[2]` is the `near` count in each tuple.

    print(f"answers within 10% of the generation cap, all conditions: {trunc}")
    # Zero here rules out truncation as a competing explanation for any of the four conditions.

    VERDICT["not_a_length_artifact"] = (
        f"rescued/FT length ratio {w_rescue/w_ft:.2f}x, {trunc} answers near the cap")
    # The entry records the narrow claim only. The limit is stated in the paragraph below, and
    # deliberately NOT folded into a reassuring one-liner.

    print(f"""
The narrow worry is closed, and decisively: the rescue is NOT the judge running out of material,
because rescued answers are {w_rescue/w_ft:.1f}x LONGER than misaligned ones. The shortcut
explanation does not merely lack support, it points the wrong way.

But read the table again and notice what it also shows -- and do not let the passing assertion
hide it. Length is almost perfectly CONFOUNDED with condition:

    misaligned (FT)  ~{w_ft:.0f} words        benign (base and rescued)  ~{w_rescue:.0f} words

The project's own E0 measured AUC 0.93 for separating FT from base on LENGTH ALONE. So a judge
with any length prior at all would partially track the arm rather than the content. That does not
undo chapter 5 -- the transplant arm produces SHORT misaligned text from the base model, which a
pure length prior cannot explain -- but it does mean the effect is not length-INDEPENDENT.

The instrument that would settle it is a covariate-adjusted mixed-effects model with length as a
covariate. The project's own pre-registration makes that analysis MANDATORY, and it was never
implemented -- no mixedlm, no covariate, anywhere in 225 scripts. So:

  * "the rescue is not a short-answer artifact"        -> VERIFIED here
  * "the effect is independent of answer length"       -> NOT VERIFIED, and the mandated
                                                          analysis does not exist""")
    # The measured lengths are substituted into the paragraph, including into the sentence that
    # states the LIMIT of what was verified — so the caveat cannot drift from the data either.
