# ⟨needs⟩ 011 (np) · 031 (rng) · 051 (H) · 101 (unit)

N_SAMPLES = 2000                                     # KNOB: raise it; the sd stops moving
cos_samples = np.array([unit(rng.standard_normal(H)) @ unit(rng.standard_normal(H))
                        for _ in range(N_SAMPLES)])
# Draw two INDEPENDENT random vectors in R^3584, normalise both, and take their dot product —
# i.e. the cosine of the angle between two directions that have nothing to do with each other.
# Repeat N_SAMPLES times. `for _ in range(…)` uses `_` as the name for a value never used.
# `np.array([…])` turns the resulting list of 2000 numbers into an array so it can be measured.

cos_sd = cos_samples.std()
# The one number this entire chapter turns on: how far a chance cosine typically strays from zero.
# Every cosine reported anywhere in the audit is read against it, never against 1.

print(f"empirical  mean {cos_samples.mean():+.5f}   sd {cos_sd:.5f}")
# What was measured: the average cosine (should be ~0) and its spread.

print(f"predicted  mean {0.0:+.5f}   sd {1/np.sqrt(H):.5f}   = 1/sqrt({H})")
# What theory predicts: mean exactly 0, spread exactly 1/sqrt(H). `np.sqrt` is the square root.
# Printing measurement and prediction side by side is the check — the two must agree.

print(f"|cos| 99.9th percentile: {np.percentile(np.abs(cos_samples), 99.9):.4f}\n")
# `np.abs` takes absolute values; `np.percentile(x, 99.9)` is the value only 0.1% of samples
# exceed. So: even the most extreme of 2000 chance pairings barely reaches this cosine.

for c in (0.070, 0.216, 0.409, 0.778, 1.000):
    # The five cosines that actually appear later in this audit, converted to "how many standard
    # deviations from chance". This little table is what makes 0.41 readable as 24 sigma.

    print(f"  cos = {c:5.3f}  ->  {c/cos_sd:6.1f} sd from chance")
    # `:5.3f` / `:6.1f` fix the column widths so the arrow lines up.

assert abs(cos_samples.mean()) < 4 * cos_sd / np.sqrt(N_SAMPLES), "mean is not ~0"
# The mean of N samples has standard error sd/sqrt(N); allowing 4 of those is a wide, safe band.
# So this asserts "the average chance cosine is zero" without being brittle to the seed.

assert abs(cos_sd - 1/np.sqrt(H)) < 0.15/np.sqrt(H), "empirical sd does not match 1/sqrt(H)"
# And the measured spread matches the derived 1/sqrt(H) to within 15%. Note what this is: the
# baseline was DERIVED, then confirmed empirically — not looked up.

VERDICT = {}
# `VERDICT` is created here, empty, and every later chapter adds one line to it. The final cell
# prints the whole dict as the audit's summary sheet — so the summary is accumulated by the code
# that ran, never typed by hand afterwards.

VERDICT["random_cosine_baseline"] = f"sd = {cos_sd:.5f} = 1/sqrt(3584); 0.41 is {0.41/cos_sd:.0f} sd from chance"
# First row of that sheet: the baseline every later cosine is read against.

print("\nThose five numbers are every cosine that matters in this audit. Keep the table.")
# The table above is the reusable artifact of this chapter — worth carrying forward, not re-deriving.

print("""
This table is the single most useful thing in chapter 1, so read it as a rule rather than a fact.

A cosine in this space has no meaning until divided by 1/sqrt(H). At H=3584 that is 0.0167, so
0.41 -- a number that looks like weak agreement -- is 24 standard deviations from chance, and
0.78 is 46. Both of those describe REAL relationships. Neither describes identity.

An audit pass read a 0.41 as "these two vectors are unrelated, so the project's description of
its own object is broken", and built a project-wide alarm on it. It was reading the second half
of that sentence without the first. Chapter 6 is where you will see the consequence, and you
will be in a position to catch it because you computed this baseline yourself.""")
