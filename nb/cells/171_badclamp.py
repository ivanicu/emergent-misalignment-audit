# ⟨needs⟩ 011 (np) · 031 (rng) · 051 (H) · 101 (unit) · 121 (VERDICT) · 161 (clamp)

u = unit(rng.standard_normal(H))
# 12 token positions, each with its own u-coordinate -- like a real generated sequence

states = [rng.standard_normal(H) * 2 + rng.normal(0, 4) * u for _ in range(12)]
# Twelve pretend token states. Each is random noise PLUS a random multiple of u — so the twelve
# differ from one another in their u-coordinate, exactly as real tokens in a sentence do.
# `rng.normal(0, 4)` draws one number from a Gaussian of mean 0, sd 4: the per-token u-loading.

coords = np.array([s @ u for s in states])
# Read each state's u-coordinate. This array is the "before" picture: a mean and a real SPREAD.

clamped   = np.array([clamp(s, u, -13.7) @ u for s in states])          # to a constant
# Three interventions that all get described in English as "removing u", applied to every state,
# each time reading the resulting u-coordinate back out:
#   (1) CLAMP every position to the same constant -13.7

subtract  = np.array([(s - 7.09 * u) @ u for s in states])              # a constant shift
#   (2) SUBTRACT the same fixed multiple of u from every position

zeroed    = np.array([(s - (s @ u) * u) @ u for s in states])
#   (3) ZERO the u-component of each position — i.e. project it out entirely

print(f"original coordinate:  mean {coords.mean():+7.3f}   sd {coords.std():6.3f}")
# `.mean()` and `.std()` on an array give its average and its standard deviation. The SPREAD is
# the quantity to watch: it is the per-token variation the sequence originally carried.

print(f"clamp to -13.7     :  mean {clamped.mean():+7.3f}   sd {clamped.std():6.3f}   <- variance GONE")
# Forcing every position to one value destroys the variation — sd collapses to 0.

print(f"subtract 7.09      :  mean {subtract.mean():+7.3f}   sd {subtract.std():6.3f}   <- variance KEPT")
# Shifting every position by the same amount moves the mean and leaves the variation intact.

print(f"zero the component :  mean {zeroed.mean():+7.3f}   sd {zeroed.std():6.3f}   <- variance GONE")
# Projecting out sets every coordinate to 0 — again no variation left.

assert clamped.std() < 1e-9 and zeroed.std() < 1e-9, "clamping/zeroing should remove all variance"
# The three claims, machine-checked. `and` requires both to hold.

assert abs(subtract.std() - coords.std()) < 1e-9, "subtracting a constant must preserve variance"
# And the constant shift must preserve the ORIGINAL spread exactly, not approximately.

VERDICT["intervention_shape_matters"] = "clamp/zero destroy per-token variance; a constant shift preserves it"
# One line into the summary sheet: the shape of an intervention, not just its target, is a fact
# about what it can prove.

print("""
Three interventions, one English description, different confounds. When you read "we removed u"
anywhere in this literature, the first question is which of these three it was -- and the second
is whether the paper's control matches the same shape. Chapter 9 is a case where two
interventions set the IDENTICAL coordinate and disagree by 4.5x, for exactly this reason.""")
# The reading rule that follows from the table.
