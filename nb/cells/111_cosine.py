# ⟨needs⟩ 011 (np) · 101 (unit)

rng = np.random.default_rng(0)
# Re-seed at 0 so this cell's numbers are reproducible on their own, independent of what ran before.

H = 3584
# The model's width, restated locally so this cell stands alone.

h = rng.standard_normal(H) * 3
# A pretend residual-stream state: 3584 Gaussian numbers, scaled up so its length is not 1.

u = unit(rng.standard_normal(H))
# A pretend direction of interest, normalised to length 1 by `unit`.

coord   = h @ u                 # the u-coordinate
# `@` on two 1-D arrays is the DOT PRODUCT: multiply elementwise, then add up. Because u has
# length 1, this single number is exactly "how far along u the state h sits" — its u-coordinate.

along   = coord * u             # the component along u
# Scaling u by that number reconstructs the part of h that points along u.

h_perp  = h - along             # everything else
# Subtracting it leaves everything h does OUTSIDE the u direction — 3583 dimensions' worth.

print(f"u-coordinate      {coord:+.4f}")
# `:+.4f` = four decimals, sign always shown.

print(f"||h||^2 = ||along||^2 + ||h_perp||^2 ?  "
      f"{np.linalg.norm(h)**2:.4f} vs {np.linalg.norm(along)**2 + np.linalg.norm(h_perp)**2:.4f}")
# Pythagoras in 3584 dimensions: because the two pieces are perpendicular, their squared lengths
# add to the squared length of h. `**2` is "raise to the power 2". The two printed numbers must
# agree — this is the check, shown side by side rather than asserted out of sight.

assert abs(h_perp @ u) < 1e-9, "h_perp is not orthogonal to u"
# Orthogonality: the leftover part has ZERO component along u. `abs(…) < 1e-9` rather than
# `== 0` because floating-point arithmetic leaves crumbs around 1e-16, never an exact zero.

assert np.allclose(h, along + h_perp), "the decomposition does not reconstruct h"
# Completeness: the two pieces put back together are the original state, nothing lost.

print("\ndecomposition holds. 'off-u' and 'the carrier' in the papers mean exactly h_perp.")
# Naming the pieces: from here on, "off-u" / "the carrier" / "delta-perp" all mean `h_perp`.

print("""
What that decomposition buys you: it is the entire vocabulary of this literature, made concrete.
When a paper says "the u-coordinate", it means the single number u'h. When it says "off-u" or
"the carrier" or "delta-perp", it means h_perp -- the 3583 remaining dimensions. When it says an
intervention "removed u", it means it changed the first term and (hopefully) not the second.
Every dispute you will read about later is a dispute about which of those two pieces did the
work, so being able to compute both yourself is the difference between following the argument
and taking it on trust.""")
