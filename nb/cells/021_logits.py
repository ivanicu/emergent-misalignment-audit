# ⟨needs⟩ 011 (np)

def softmax(z):
    # A model's final layer emits one raw score per vocabulary entry. Those raw scores are LOGITS —
    # unbounded real numbers, not probabilities. `softmax` is the standard map from logits to a
    # probability distribution: exponentiate each score, then divide by the total so they sum to 1.

    z = np.asarray(z, dtype=np.float64)
    # Accept a list or an array, and force 64-bit floats. `asarray` does not copy if it can avoid
    # it. float64 matters here because `exp` of a large number overflows fast in float32.

    e = np.exp(z - z.max())        # subtract the max: numerically safe, and legal by shift-invariance
    return e / e.sum()
    # Normalise: each exponentiated score divided by their sum. `e` is an array, so `e / e.sum()`
    # divides every element by one number (numpy "broadcasting" — no loop needed).

z = np.array([2.0, 1.0, 0.5, -1.0])
# Four made-up logits, standing in for four candidate next tokens.

p = softmax(z)
# Convert them to probabilities.

print("logits      ", z)
# `print` with several comma-separated arguments prints them space-separated.

print("probabilities", np.round(p, 4), " sum =", p.sum())
# `np.round(p, 4)` rounds every element to 4 decimals for display. `p.sum()` must come out 1.0 —
# that is the defining property of a probability distribution, shown rather than asserted.

assert np.allclose(softmax(z), softmax(z + 137.0)), "softmax is not shift-invariant"
# shift-invariance, verified rather than asserted
# `np.allclose(a, b)` = "equal within floating-point tolerance" (exact `==` is the wrong test for
# floats). Adding 137 to every logit changes nothing, because the +137 cancels in the ratio.
# Consequence: an individual logit has no absolute meaning; only DIFFERENCES between logits do.

print("\nsoftmax(z) == softmax(z + 137)  -> only logit DIFFERENCES carry information")
# State the consequence in words, because it is the reason "margin" is the quantity below.

print(f"\nlogit margin pine-vs-gold in this toy: {z[0]-z[1]:+.2f}")
# the quantity the project actually reads: a margin between two rooms
# `z[0]-z[1]` is that difference. `:+.2f` prints two decimals and always shows the sign, so a
# negative margin is visually unmistakable.

print("A 'margin' in the papers is exactly this: one logit minus another.")
# The vocabulary line: whenever a paper says "margin", it means the subtraction just performed.
