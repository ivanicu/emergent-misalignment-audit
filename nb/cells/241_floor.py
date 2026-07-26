# ⟨needs⟩ 011 (DATA, np) · 121 (VERDICT) · 201 (per_question_rate) · 231 (paired_drop)

pq0  = per_question_rate(DATA / "experiments/judgments/hi_s0_375.llama31.jsonl")   # BROAD only
# Start from REAL data: the 23 per-question rates of one condition. The floor computed below is
# therefore the floor for THIS design, not a textbook rule of thumb.

vals = np.array(list(pq0.values()))
# `.values()` gives the rates; `list(…)` then `np.array(…)` makes them measurable.

print(f"real per-question rates: n={len(vals)}, mean {100*vals.mean():.1f}%, "
      f"sd {100*vals.std(ddof=1):.1f}pp, range {100*vals.min():.0f}-{100*vals.max():.0f}%")
# `ddof=1` is the sample standard deviation (divide by n-1, not n) — the right one for a sample.
# Note the range: these 23 questions differ enormously, and that spread is the enemy below.

r = np.random.default_rng(7)
# One generator for both simulations; seed 7 fixes every number in this cell.

unpaired = []
# (a) the UNPAIRED floor: two arms drawn independently from this spread, true effect zero

for _ in range(400):
    # 400 simulated experiments — enough for a stable median, cheap enough to run on a CPU.

    a, b = r.choice(vals, len(vals)), r.choice(vals, len(vals))
    # Draw two arms INDEPENDENTLY from the observed spread of rates. `r.choice(vals, n)` samples
    # n values with replacement. The two arms share no question, so the true difference is zero:
    # anything the interval shows is pure noise.

    A = {f"q{i}": a[i] for i in range(len(vals))}; B = {f"q{i}": b[i] for i in range(len(vals))}
    # Wrap both arms as {qid: rate} dicts, using matching fake ids so paired_drop will compare
    # them position by position.

    _, lo_, hi_, _ = paired_drop(A, B, B_boot=2000, seed=int(r.integers(1e6)))
    # `_` discards the point estimate and the question count; only the interval matters here.
    # A fresh random seed per iteration so the 400 bootstraps are not all identical.

    unpaired.append(hi_ - lo_)
    # Store the interval's WIDTH.

half_unpaired = np.median(unpaired) / 2
# Median width over the 400 runs, halved: the "± X pp" you would quote. Median rather than mean
# because it is not dragged around by the occasional extreme run.

n_r = 50
# (b) the PAIRED case: same questions, a constant true shift. Between-question spread cancels,
#     so what survives is only noise in the per-question DIFFERENCE. Model that noise explicitly
#     as binomial sampling error at n_r rollouts per question -- the only noise left once the
#     question is held fixed.
# 50 rollouts per question — the order of magnitude these experiments actually run at.

paired = []
# Same accumulator pattern as the unpaired loop above, so the two floors are computed alike.

for _ in range(400):
    # 400 simulated PAIRED experiments.

    base = r.choice(vals, len(vals))
    # The underlying per-question rates for this simulated experiment.

    shifted = np.clip(base - 0.05, 0, 1)                       # a true 5pp effect
    a = r.binomial(n_r, base) / n_r                            # what you actually observe
    b = r.binomial(n_r, shifted) / n_r
    # The other arm, same questions, sampled at the shifted rate. `r.binomial(n, p)` counts
    # successes in n draws at probability p — exactly what running n_r rollouts and judging them
    # amounts to. Dividing by n_r turns the count back into an observed rate.

    A = {f"q{i}": a[i] for i in range(len(vals))}; B = {f"q{i}": b[i] for i in range(len(vals))}
    # Same wrapping as above, and crucially the SAME question ids in both arms — that is what
    # makes this the paired case.

    _, lo_, hi_, _ = paired_drop(A, B, B_boot=2000, seed=int(r.integers(1e6)))
    # Identical estimator call as the unpaired loop — only the DATA differs, never the method.

    paired.append(hi_ - lo_)
    # Again, keep only the interval's width.

half_paired = np.median(paired) / 2
# And the same median-of-widths, halved, so the two floors are directly comparable.

print(f"\nunpaired 95% CI half-width (independent arms) : {half_unpaired:5.1f}pp")
# The two floors, side by side. Everything smaller than these is below this design's resolution.
# Two floors, printed together. Quoting one of them as "the" floor is the error this guards against.

print(f"paired   95% CI half-width (same questions)    : {half_paired:5.1f}pp")
print(f"pairing buys a factor of {half_unpaired/half_paired:.1f}x in resolution")
# The ratio is the payoff of pairing — roughly a 4-5x improvement in what the design can see.

assert half_unpaired > half_paired, "pairing must improve resolution, not worsen it"
# Direction check: pairing must help. If this ever failed, the simulation would be wrong.

assert 3 < half_unpaired < 25, "the unpaired floor came out implausible -- check the resampling"
# Plausibility band: a floor outside 3-25pp would mean the resampling itself is broken, which is
# a different failure from an interesting result. Bounded on BOTH sides on purpose.

VERDICT["resolution_floor"] = (f"unpaired ~{half_unpaired:.1f}pp vs paired ~{half_paired:.1f}pp "
                               f"half-width at n={len(vals)} questions")
# Parenthesised strings across two lines concatenate; both numbers go into the summary sheet,
# because quoting only one of them is how a generic "floor" gets misapplied.
# Both floors AND the question count go into the sheet — a floor without its n means nothing.

print(f"""
Both numbers, kept together, are the useful fact:
  * an UNPAIRED comparison at n={len(vals)} cannot see anything under ~{half_unpaired:.0f}pp
  * a PAIRED one can see well under that -- which is why chapter 9's +5.4 [+0.2, +10.3] is a
    real result rather than a rounding error, and why its +24.3 neighbour needed no such defence
Quote the reported interval, never a generic floor.""")
# An f-string triple-quote: the computed numbers are substituted into the prose, so the narrative
# cannot drift away from what the code just measured.
