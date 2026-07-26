# ⟨needs⟩ 011 (np) · 121 (VERDICT) · 411 (cond_rate)

def R_of(arm, floor, ceiling, direction):
    """Fraction of the available effect this arm achieves, with a question-clustered CI.

    The two arms normalise in OPPOSITE directions, and it matters:
      * INSTALL arm  -- start at the base rate, try to build EM up.  R = (arm - floor)/(ceiling - floor)
      * ABOLISH arm  -- start at the FT rate, try to tear EM down.   R = (ceiling - arm)/(ceiling - floor)
    Both read "1.0 = this arm did the whole job, 0.0 = it did nothing". Using one formula for
    both would report the abolish arm's success as failure -- which is exactly the bug I hit
    when writing this cell."""
    # The recovery fraction R = (arm - floor) / (ceiling - floor), per arm, with a paired CI.

    A, F, C = cond_rate(arm), cond_rate(floor), cond_rate(ceiling)
    # Three conditions, each returning (rate, n, per-question dict) or None.

    if None in (A, F, C):
        # `None in (A, F, C)` is True if ANY of the three is missing — then R is undefined, so bail.

        return None
        # Missing any of the three makes R undefined — report that, never a number.

    qs = sorted(set(A[2]) & set(F[2]) & set(C[2]))
    # Questions present in all three conditions. `[2]` is the per-question dict; `&` intersects.

    if direction == "install":
        # The numerator: how far this arm moved FROM its starting point, per question.

        num = np.array([A[2][q] - F[2][q] for q in qs])
        # Install: measured up from the floor.

    else:
        # The branch that the first version of this cell got wrong:

        num = np.array([C[2][q] - A[2][q] for q in qs])
        # Abolish: the arm starts at the ceiling and moves down, so the improvement is measured
        # from the ceiling. Same sign convention as install, opposite subtraction.

    den = np.array([C[2][q] - F[2][q] for q in qs])
    # The denominator: the total effect available to move, per question. Same for both arms.

    if abs(den.mean()) < 1e-9:
        # If there is no gap between floor and ceiling, R is 0/0 — return None rather than a number.

        return None
        # 0/0 is not a recovery fraction of zero — it is no measurement at all.

    r = np.random.default_rng(0)
    # A question-clustered bootstrap, as in chapter 3: resample QUESTIONS, not rollouts.

    idx = r.integers(0, len(qs), (20000, len(qs)))
    # 20000 resamples of the question list, each row one bootstrap draw.

    bs = num[idx].mean(1) / np.maximum(den[idx].mean(1), 1e-9)
    # Resample numerator and denominator TOGETHER using the same question indices — that keeps
    # the ratio paired. `np.maximum(…, 1e-9)` guards against a resample whose denominator
    # collapses to zero, which would otherwise produce inf and poison the percentiles.

    return num.mean()/den.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), len(qs)
    # Point estimate (ratio of the means, not the mean of the ratios) plus the 95% interval and n.

ARMS = [
    ("install EM into base", "anchor_base", "anchor_bad", "install",
     [("zonly", "zonly_transplant"), ("zremoved", "zremoved_transplant"), ("random", "random_transplant")]),
    ("abolish EM in FT",     "full_rescue", "anchor_bad", "abolish",
     [("zonly", "zonly_rescue"),    ("zremoved", "zremoved_rescue"),    ("random", "random_rescue")]),
]
# The two arms, each as (label, floor condition, ceiling condition, normalisation direction,
# [(display name, condition file)]). Written as data so both arms go through identical code.

tbl = {}
# Results keyed by (arm label, condition name), so the comparison below can look them up.

for label, floor, ceiling, direction, arms in ARMS:
    # Both arms, same loop body — so neither can be quietly given a different treatment.

    print(f"\n{label}   (floor = {floor}, ceiling = {ceiling}, normalised as '{direction}')")
    # State the normalisation in the header, so no row can be read under the wrong convention.

    print(f"  {'arm':10}{'R':>8}{'95% CI':>20}{'nq':>5}")
    for nm, cond in arms:
        # Three rows per arm: persona-only, everything-but-persona, and the random-direction control.

        got = R_of(cond, floor, ceiling, direction)
        # Same floor, ceiling and direction for all three — only the intervention differs.

        if got is None:
            # A missing row is printed as missing.

            print(f"  {nm:10}{'--':>8}   (not staged)"); continue
            # Dashes, then on to the next arm.

        tbl[(label, nm)] = got
        # Keep it for the overlap test after the loop.

        print(f"  {nm:10}{got[0]:>+8.3f}{f'[{got[1]:+.3f}, {got[2]:+.3f}]':>20}{got[3]:>5}")
        # R, its 95% interval, and the number of questions behind it.

for label, _, _, _, _ in ARMS:
    # the claim: zonly's interval overlaps random's, while zremoved recovers ~everything
    # `for label, _, _, _, _ in ARMS` unpacks the tuple but keeps only the label.

    if (label, "zonly") not in tbl or (label, "random") not in tbl:
        # Skip an arm whose rows are not both present, rather than comparing against nothing.

        continue
        # No control, no comparison — skip rather than compare against a missing row.

    zo, rd, zr_ = tbl[(label, "zonly")], tbl[(label, "random")], tbl.get((label, "zremoved"))
    # `.get(…)` for zremoved because it is optional to the comparison below.

    overlap = not (zo[1] > rd[2] or rd[1] > zo[2])
    # Two intervals fail to overlap only if one lies entirely above the other; `not (…)` of that
    # is "they overlap". Overlap here means: the persona-only arm is INDISTINGUISHABLE from a
    # random direction — the whole point of the section.

    print(f"\n{label}: zonly CI overlaps random CI? {overlap}")
    # Printed per arm, so the conclusion is visibly reached twice and independently.

    assert overlap, f"{label}: zonly is distinguishable from a random direction -- the claim is too strong"
    # If they were distinguishable, the claim would be too strong and this stops the notebook.

    if zr_:
        # And the complementary arm must do nearly all the work — otherwise "the causal content is
        # off-axis" would have no positive evidence, only a null.

        assert zr_[0] > 0.7, f"{label}: zremoved recovers only {zr_[0]:.2f}, not ~1"
        # 0.7 is the floor for 'did essentially the whole job'.

VERDICT["persona_axis_carries_no_causal_work"] = (
    "zonly's CI overlaps the random-direction control in both arms; zremoved recovers ~1")
# Both halves in one entry: the null AND the positive result that gives the null its meaning.

print("""
Both arms, same conclusion: you can install full misalignment while holding the persona
coordinate at the base value, and abolish it while holding that coordinate at the misaligned
value -- and the persona-only arm is statistically indistinguishable from a random direction.

A near-perfect linear READOUT of the state carries essentially none of the CAUSAL work. That is
the converse of the usual worry: not "controls therefore represents", but "represents does not
therefore cause".""")
