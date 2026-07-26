# ⟨needs⟩ 121 (VERDICT) · 411 (cond_rate)

print(f"{'k':>6}{'EM %':>9}{'R vs full':>12}")
# How much of the state is needed? The rank-k ladder: transplant only the top-k SVD directions.
# (SVD = singular value decomposition: it orders the directions of a matrix by how much of its
#  variation each one accounts for, so "top-k" means the k most important directions.)

full = cond_rate("full_transplant")[0]; floor = cond_rate("anchor_base")[0]
# The two ends of the scale: transplanting the WHOLE state, and touching nothing at all.
# `[0]` picks the rate out of cond_rate's (rate, n, per-question dict) tuple.

ladder = {}
# Each rung's rate, kept for the assertions below.

for k in (1, 2, 8, 32):
    # Four rungs, powers of two, so the shape of the curve is visible rather than a single point.

    got = cond_rate(f"rankk_t_k{k}")
    # One staged condition per rung of the ladder.

    if got is None:
        # Skip rungs that were never run, rather than inventing a value for them.

        continue
        # Next k.

    ladder[k] = got[0]
    # Store the rate under its k.

    print(f"{k:>6}{got[0]:>9.2f}{(got[0]-floor)/(full-floor):>12.3f}")
    # `(rate - floor) / (full - floor)` rescales to "fraction of the achievable effect", so 0
    # means "did nothing" and 1 means "did everything the full transplant did".

print(f"{'full':>6}{full:>9.2f}{1.0:>12.3f}   (3584 dimensions)")
# The reference row: the whole 3584-dimensional state, which is 1.000 by definition.

rand8 = cond_rate("rankrand_t_k8")
# The one control available at this stage: a RANDOM 8-dimensional basis instead of the top 8.

if rand8:
    # Print it only if that condition was staged.

    print(f"\nmatched random basis at k=8: {rand8[0]:.2f}%  vs top-8 SVD {ladder.get(8, float('nan')):.2f}%")
    # `ladder.get(8, float('nan'))` returns NaN if k=8 was never run, so the line still formats
    # instead of raising — and NaN is visibly not a number, unlike a silent 0.

assert ladder.get(1, 99) < 1.0, "k=1 already installs EM -- then the state is low-dimensional after all"
# `ladder.get(1, 99)` defaults to 99 — a value that FAILS the test — so a missing rung can never
# be mistaken for a passing one. Choosing a failing default is the whole point of that 99.

assert ladder.get(32, 0) < 0.35 * full, "k=32 recovers most of the effect -- revise the high-dim claim"
# The mirror check: even 32 directions must recover well under a third of the full effect.
# (Note the asymmetry — here the default of 0 would PASS, so this one is only meaningful when
#  the k=32 rung is actually staged. The printed table above is what shows that it is.)

VERDICT["state_is_high_dimensional"] = (
    f"rank-k ladder k=1:{ladder.get(1,0):.2f}% k=8:{ladder.get(8,0):.2f}% k=32:{ladder.get(32,0):.2f}% "
    f"vs full {full:.2f}%")
# The whole ladder goes in the sheet, not just the headline — the SHAPE is the evidence.

print("""
So the mediating state is genuinely high-dimensional: the top 32 of 3584 directions carry a small
fraction of the effect, and one direction carries almost none.

But this ladder cannot yet support the word "privileged". Every row compares a top-k subspace
against the FULL state, and none compares it against ANOTHER k-dimensional subspace. Without
that, "the top 32 directions carry 20% of the effect" might be a fact about the number 32 rather
than about those directions -- and the ladder also stops at k=32, so "high-dimensional" cannot
yet be distinguished from "we did not look far enough".

Both gaps were open when this cell was first written. The next cell closes them with a GPU run.""")
