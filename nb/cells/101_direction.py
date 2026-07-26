# ⟨needs⟩ 011 (DATA, np, torch)

def unit(x):
    """A direction: the vector with its length discarded."""
    # The first of the two functions the whole audit is built on.

    a = torch.as_tensor(x).float().numpy() if torch.is_tensor(x) else np.asarray(x)
    # Accept either a torch tensor or anything numpy can read. The conditional expression
    # `A if cond else B` picks one branch: if it is a tensor, convert via torch (`.float()` to
    # 32-bit, `.numpy()` to hand the numbers to numpy); otherwise let numpy read it directly.

    a = a.astype(np.float64).ravel()
    # `.astype(np.float64)` promotes to double precision — cosines of nearly-parallel vectors are
    # exactly where float32 loses digits. `.ravel()` flattens any shape into one long 1-D vector,
    # so a (1, 3584) column and a (3584,) vector are treated identically.

    return a / np.linalg.norm(a)
    # `np.linalg.norm(a)` is the Euclidean length sqrt(sum of squares). Dividing by it produces a
    # vector of length exactly 1 pointing the same way: that IS the definition of a direction.

def load_unit(rel):
    """Load a staged .pt file and return it as a direction."""
    # The second: read an artifact off disk and normalise it, in one step.

    return unit(torch.load(DATA / rel, weights_only=False))
    # One call does both, so no cell can accidentally compare a stored, un-normalised vector with
    # a normalised one — the two would differ by a factor of ~42 in one real case (see below).

v = np.array([3.0, 4.0])
# The 3-4-5 right triangle, chosen because its length is exactly 5 and you can check it by eye.

print(f"v = {v},  ||v|| = {np.linalg.norm(v)},  unit(v) = {unit(v)}")
# So unit(v) must be [0.6, 0.8] — visible in the printed output, no trust required.

assert np.allclose(unit(v), unit(42.0 * v)), "unit() is not scale-invariant"
# scale-invariance is the defining property; verify it rather than assume it
# Stretching a vector by 42 must not change its direction. `allclose` compares within
# floating-point tolerance, which is the correct comparison for computed floats.

print("unit(v) == unit(42v)  -> a direction has forgotten its scale, by construction")
# Say what the assertion means: `unit` has thrown away scale on purpose, not by accident.

u_real = load_unit("fits/u_L16.pt")
# and it works on the real artifact from 0.6
# Same function, now on the actual 3584-dimensional research vector.

print(f"\nload_unit('fits/u_L16.pt'): dim {u_real.size}, ||.|| = {np.linalg.norm(u_real):.6f}")
# `.size` is the total number of elements. The norm printed here must be 1.000000 by construction
# — if it were not, `unit` would be broken.

print("""
Why discarding length is not a technicality. Later in this notebook you will meet two files that
hold THE SAME direction and differ in stored norm by a factor of about 42 -- because one was
saved before a normalisation step and one after. Any comparison that used length would call them
different objects; the cosine correctly calls them identical. Scale is an accident of how
something was written to disk. Direction is the thing that was computed.""")
# Why this is not pedantry: two staged files hold the same direction at norms 42x apart.
