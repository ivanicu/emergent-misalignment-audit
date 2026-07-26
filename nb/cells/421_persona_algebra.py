# ⟨needs⟩ 011 (np) · 051 (H) · 101 (unit) · 121 (VERDICT)

zr = np.random.default_rng(3)
# The identity, on random vectors, before touching any data.
# Doing the algebra on noise first means the property is shown to hold for STRUCTURAL reasons,
# not because of anything special about this experiment's numbers.

a     = zr.standard_normal(H)          # the run model's state
delta = zr.standard_normal(H)          # the donor difference
z     = unit(zr.standard_normal(H))    # the persona axis

h_zonly    = a + (delta @ z) * z              # move only z's component
# ARM 1: add back ONLY delta's component along z. `(delta @ z)` is that component's size and
# `* z` puts it back on the axis, so everything delta contained off-axis is discarded.

h_zremoved = a + delta - (delta @ z) * z      # move everything except it
# ARM 2: add the whole of delta, then subtract its z-component again — so every direction moves
# EXCEPT z. The two arms partition delta between them.

print(f"z-coordinate of the run model      : {a @ z:+.6f}")
# Four readings of the same coordinate, so the two arms can be checked by eye before the asserts.

print(f"z-coordinate under zremoved        : {h_zremoved @ z:+.6f}   <- must equal the line above")
print(f"z-coordinate under zonly           : {h_zonly @ z:+.6f}   <- fully moved")
print(f"z-coordinate of the intended donor : {(a + delta) @ z:+.6f}")

assert abs(h_zremoved @ z - a @ z) < 1e-9, "zremoved did NOT pin the z-coordinate"
# zremoved must leave the persona coordinate EXACTLY where it started (1e-9 = floating-point dust).

assert abs(h_zonly @ z - (a + delta) @ z) < 1e-9, "zonly did not fully move the z-coordinate"
# and zonly must take it exactly to the donor's value. Together: a clean split of the edit.

VERDICT["zremoved_pins_the_coordinate"] = "z'h' = z'a exactly under zremoved (1e-9)"
# The tolerance is part of the claim: "pinned" here means to 1e-9, not "approximately held".

print("""
So the two arms are a clean decomposition: one moves the persona coordinate and nothing else,
the other moves everything else and holds the persona coordinate fixed. Whatever behaviour
follows can be attributed to one or the other without further argument.""")
# Why the algebra matters: it makes the two arms attributable without any further argument.
