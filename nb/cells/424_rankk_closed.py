# ⟨needs⟩ 121 (VERDICT) · 411 (cond_rate)

floor = cond_rate("anchor_base")[0]
# The hole chapter 6.3 named is now closed by a GPU run, and the ladder is extended past k=32.
# The question it answers: is the TOP-k SVD subspace special, or would ANY k-dimensional
# subspace of the same rank do as well? Without a matched random basis at the same k, "the top
# 32 directions carry 20% of the effect" is not yet a statement about those directions.

full  = cond_rate("full_transplant")[0]
# The ceiling: transplanting the entire state.

print(f"{'k':>6}{'top-k SVD':>12}{'random basis':>14}{'ratio':>9}{'R vs full':>11}")
# Five columns: k, the structured subspace, the matched random one, their ratio, and the fraction
# of the full effect recovered.

lad = {}
# Each rung's top-k rate, kept for the two assertions below.

for k, svd_cell, rnd_cell in [(1,  "rankk_t_k1",      None),
                              (2,  "rankk_t_k2",      None),
                              (8,  "rankk_t_k8",      "rankrand_t_k8"),
                              (32, "rankk_t_k32",     "x_rankrand_t_k32"),
                              (64, "x_rankk_t_k64",   None),
                              (128,"x_rankk_t_k128",  "x_rankrand_t_k128")]:
    # Each row is (k, the top-k SVD condition, the matched random-basis condition or None). The
    # `x_` prefix marks the cells added by the later GPU run — the rungs that did not exist before.

    s = cond_rate(svd_cell)
    # The structured subspace at this k.

    if s is None:
        # A rung that was never run is skipped, not guessed at.

        continue
        # Next k.

    r = cond_rate(rnd_cell) if rnd_cell else None
    # Only fetch the control when this rung HAS one; `if rnd_cell` short-circuits otherwise.

    lad[k] = s[0]
    # Store the structured rate under its k.

    ratio = f"{s[0]/max(r[0],1e-9):>8.0f}x" if r else "       --"
    # How many times better the structured subspace is than the matched random one.
    # `max(r[0], 1e-9)` prevents a division by zero when the random basis achieves nothing —
    # which is exactly the interesting case, so it must not crash the table.

    rnd = f"{r[0]:>13.2f}%" if r else "            --"
    # Pre-format the random column (or a dash), then place it in the row below.

    print(f"{k:>6}{s[0]:>11.2f}%{rnd}{ratio}{(s[0]-floor)/(full-floor):>11.3f}")
    # The final column rescales to "fraction of the full transplant's effect", as in cell 423.

print(f"{'3584':>6}{full:>11.2f}%{'--':>14}{'--':>9}{1.0:>11.3f}   (the whole state)")
# The reference row for the whole state, 1.000 by definition.

assert lad[32] > 5 * cond_rate("x_rankrand_t_k32")[0], \
    "top-32 is not clearly better than a random 32-dim basis -- the subspace is not special"
# 1. the top-k subspace IS privileged over an arbitrary subspace of the same dimension
# A factor of five is demanded, not a bare inequality, so a marginal difference cannot pass.

assert lad[128] < 0.6 * full, "k=128 already recovers most of the effect -- revise 'high-dimensional'"
# 2. and it is still nowhere near sufficient, even at 128 of 3584 dimensions
# This is the assertion that could kill the "high-dimensional" claim, and it is left live.

VERDICT["rankk_random_control_closed"] = (
    f"k=32: top-SVD {lad[32]:.2f}% vs random {cond_rate('x_rankrand_t_k32')[0]:.2f}% "
    f"({lad[32]/max(cond_rate('x_rankrand_t_k32')[0],1e-9):.0f}x); k=128 reaches only "
    # `:.0%` formats a fraction as a whole-number percentage (0.234 -> "23%").
    f"{(lad[128]-floor)/(full-floor):.0%} of the full effect")
# Both settled questions in one entry: the subspace IS special, and it is still far from enough.

print(f"""
Two things settled at once.

(a) The subspace is genuinely privileged: at k=32 the top SVD directions give {lad[32]:.2f}% where a
    matched random basis gives {cond_rate('x_rankrand_t_k32')[0]:.2f}%, and at k=128 it is {lad[128]:.1f}% vs
    {cond_rate('x_rankrand_t_k128')[0]:.1f}%. So "the top-k directions" is a real claim about THOSE
    directions, not an artifact of dimension counting. That comparison did not exist before.

(b) And saturation is nowhere in sight: 128 of 3584 directions -- 3.6% of the space -- carry only
    {(lad[128]-floor)/(full-floor):.0%} of the effect. The earlier ladder stopped at k=32 and could not
    distinguish "high-dimensional" from "we did not look far enough". Now it can.
""")
# Every number in the paragraph is re-read from the data at print time, including the two
# random-basis rates, so the prose cannot quote a stale figure.
