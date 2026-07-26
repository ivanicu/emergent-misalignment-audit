# ⟨needs⟩ 011 (np)

def paired_drop(A, B, B_boot=20000, seed=0):
    """A, B: {qid: rate}. Returns (drop_pp, lo_pp, hi_pp, n_questions), paired and clustered."""
    # THE estimator used by every comparison from here to the end of the notebook.
    # `B_boot=20000` = how many bootstrap resamples; `seed=0` makes the interval reproducible.

    qs = sorted(set(A) & set(B))                       # only questions present in BOTH
    a = np.array([A[q] for q in qs]); b = np.array([B[q] for q in qs])
    # Line the two conditions up in the SAME question order — that alignment is what makes the
    # comparison paired at all. Two array builds, one per condition.

    d = a - b                                          # difference FIRST
    # Form ONE number per question: how far that question's rate moved between the two
    # conditions. Doing this BEFORE any averaging or resampling is the whole trick — it cancels
    # the huge question-to-question variation that would otherwise drown the effect.

    r = np.random.default_rng(seed)
    # A local generator seeded per call, so two calls with the same inputs give the same interval.

    idx = r.integers(0, len(qs), (B_boot, len(qs)))    # resample QUESTIONS
    bs = d[idx].mean(1)
    # `d[idx]` uses fancy indexing: idx is a 20000 x nq grid of question indices, so this builds
    # 20000 resampled sets of differences in one operation. `.mean(1)` averages within each row,
    # leaving 20000 bootstrap estimates of the mean difference.

    return 100*d.mean(), 100*np.percentile(bs, 2.5), 100*np.percentile(bs, 97.5), len(qs)
    # Return four things, all in PERCENTAGE POINTS (hence the 100x): the point estimate, the
    # 2.5th and 97.5th percentiles of the bootstrap distribution (the 95% interval), and how many
    # questions the comparison actually rests on.

lvl = np.linspace(0.25, 0.95, 23)
# A self-test built so that only a genuinely PAIRED estimator can pass it.
# `np.linspace(0.25, 0.95, 23)` = 23 evenly spaced values from 0.25 to 0.95 — wildly different
# levels, exactly like real questions.

vary_A = {f"q{i}": float(lvl[i])        for i in range(23)}
# Condition A: those levels. Dict comprehension keyed by fake question ids "q0".."q22".

vary_B = {f"q{i}": float(lvl[i] - 0.20) for i in range(23)}
# Condition B: the same levels minus exactly 0.20 — so the DIFFERENCE is constant everywhere,
# while the LEVELS vary enormously. An unpaired estimator sees only the noisy levels and reports
# a wide interval; a paired one sees a constant and reports a zero-width interval.

m, lo, hi, n = paired_drop(vary_A, vary_B)
# Unpack the four returned values.

print(f"levels span {100*lvl.min():.0f}-{100*lvl.max():.0f}%, difference constant at 20pp")
# Restate the fixture's design in the output, so the reader can see what is being discriminated.

print(f"paired: {m:+.1f}pp, CI width {hi-lo:.2e}  <- zero, because it resamples the DIFFERENCE")
# `:.2e` prints the width in scientific notation, because it should be ~1e-15, i.e. zero.

assert abs(m - 20.0) < 1e-9, "estimator wrong on a constant-difference case"
# 1. the point estimate is exactly the true 20pp shift

assert (hi - lo) < 1e-9, "a constant difference must give a zero-width CI -- is it paired?"
# 2. and the interval has zero width — the property only a paired estimator has

assert np.std([vary_A[f'q{i}'] for i in range(23)]) > 0.15, "levels must vary for this to discriminate"
# 3. the levels really do vary. Without this the test would be decorative: a constant-LEVEL
#    fixture passes under an unpaired estimator too, so it would prove nothing.

assert paired_drop({**vary_A, "q99": 1.0}, vary_B)[3] == 23, "qids absent from B must be dropped"
# 4. and the intersection rule holds: `{**vary_A, "q99": 1.0}` copies the dict and adds an extra
#    question that condition B does not have. The returned count must still be 23, i.e. the
#    unmatched question was dropped rather than silently compared against nothing.

print("paired, clustered, intersection-only. This is the estimator for the rest of the notebook.")
# Reached only if all four assertions held — the three properties named are now facts, not claims.
