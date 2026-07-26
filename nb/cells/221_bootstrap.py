# ⟨needs⟩ 011 (np) · 031 (rng) · 121 (VERDICT)

nq, nr = 23, 20                                   # the real shape of these experiments
q_rate = rng.beta(2, 6, size=nq)                  # each question has its own propensity
X = (rng.random((nq, nr)) < q_rate[:, None])      # rollouts inside a question share it
# Simulate the rollouts. `rng.random((nq, nr))` is a 23-by-20 grid of numbers in [0,1).
# `q_rate[:, None]` reshapes the 23 propensities into a column so numpy broadcasts one propensity
# across each ROW. Comparing with `<` gives True/False: a 23x20 grid of outcomes in which the 20
# entries of a row are governed by the same underlying rate — i.e. they are NOT independent.

def ci_rollouts(X, B=4000):                       # WRONG unit
    # A bootstrap: resample the data with replacement many times and look at how much the statistic
    # moves. The spread of those resampled statistics IS the confidence interval. `B=4000` = how many
    # resamples. The only difference between the two functions below is WHAT gets resampled.

    flat = X.ravel()
    # `.ravel()` flattens the 23x20 grid into 460 individual outcomes, discarding the question
    # structure entirely — this is the mistake, made explicit.

    bs = [flat[rng.integers(0, flat.size, flat.size)].mean() for _ in range(B)]
    # `rng.integers(0, n, n)` draws n random indices in [0, n): that is sampling WITH replacement.
    # Take those 460 outcomes, average them, repeat B times.

    return np.percentile(bs, [2.5, 97.5]) * 100
    # `np.percentile(bs, [2.5, 97.5])` cuts off the lowest and highest 2.5% — the standard 95%
    # interval. `* 100` converts to percentage points.

def ci_questions(X, B=4000):                      # RIGHT unit
    per_q = X.mean(1)
    # `.mean(1)` averages along axis 1 (across the 20 rollouts), giving 23 per-question rates.
    # The question, not the rollout, is now the unit of evidence.

    bs = [per_q[rng.integers(0, len(per_q), len(per_q))].mean() for _ in range(B)]
    # Resample those 23 questions with replacement, average, repeat B times.

    return np.percentile(bs, [2.5, 97.5]) * 100
    # Same percentile cut as above — the ONLY difference between the two functions is the unit.

lo_r, hi_r = ci_rollouts(X); lo_q, hi_q = ci_questions(X)
# Run both on the SAME data. `a, b = f(…)` unpacks the two returned percentiles.

print(f"true rate                {X.mean()*100:5.1f}%")
# The point estimate is identical either way — only the uncertainty around it differs.

print(f"resample rollouts  [{lo_r:5.1f}, {hi_r:5.1f}]  width {hi_r-lo_r:5.1f}   <- too narrow")
print(f"resample questions [{lo_q:5.1f}, {hi_q:5.1f}]  width {hi_q-lo_q:5.1f}   <- honest")
print(f"\nratio {(hi_q-lo_q)/(hi_r-lo_r):.1f}x   (sqrt(nr) = {np.sqrt(nr):.1f} is the rough prediction)")
# The theory: pretending nr correlated samples are independent shrinks the interval by roughly
# sqrt(nr). Measured ratio and predicted sqrt(20)≈4.5 are printed together so you can compare.

assert (hi_q - lo_q) > (hi_r - lo_r), "clustering must widen the interval"
# The claim, machine-checked: honouring the clustering must WIDEN the interval, never narrow it.

VERDICT["clustering_widens_ci"] = f"naive CI is {(hi_q-lo_q)/(hi_r-lo_r):.1f}x too narrow on synthetic data"
# Recorded on synthetic data ON PURPOSE: here the truth is known, so the error can be measured
# rather than argued about.

print("""
What just happened, and why it decides everything downstream.

Both intervals describe the same data. The narrow one is wrong -- not approximately, but by a
factor of about sqrt(rollouts per question), because it treats 20 samples of one question as 20
independent facts when they share a prompt and therefore share most of what determines the
answer.

The practical consequence: with roughly 23 questions, this design cannot resolve differences
much below ten percentage points unless the two conditions are PAIRED. Nearly every dispute you
will read about in this project concerns effects near that boundary -- which is why the next two
atoms are about pairing and about computing the floor explicitly, rather than about any result.

If you take one habit from chapter 3, take this one: before reading anyone's confidence interval,
ask what they resampled.""")
# The reading habit this chapter is really trying to install.
