# ⟨needs⟩ 011 (np) · 031 (rng) · 101 (load_unit, unit) · 121 (VERDICT)

u_toy, v_toy = unit(rng.standard_normal(50)), unit(rng.standard_normal(50))
# A 50-dimensional toy first, so "every column is a multiple of u" is a thing you have seen.
# Two unrelated unit vectors in a small space where everything is easy to inspect.

W_toy = 3.0 * np.outer(u_toy, v_toy)
# `np.outer(a, b)` is the OUTER product: a 50x50 matrix whose (i,j) entry is a[i]*b[j]. Every
# column of it is the same vector `a`, merely rescaled by one entry of b. That is what RANK-1
# means: one direction, stretched — no second independent direction anywhere in the matrix.

cols = [unit(W_toy[:, j]) for j in range(4)]
# `W_toy[:, j]` selects column j (`:` = all rows). Normalise the first four columns.

print("pairwise |cos| between columns of a rank-1 matrix:",
      [f"{abs(cols[i] @ cols[j]):.4f}" for i in range(3) for j in range(i+1, 4)])
# A double comprehension: for every pair i<j among the first four columns, the absolute cosine
# between them. All of them come out 1.0000, because they are all the same direction.

print("-> all 1.0000. So the 'rank-1 assert' in the real code cannot fail.\n")
# Hence the point: a check in the research code that asserts "the columns are parallel" is true
# by construction for any rank-1 matrix. It can never fail, so it certifies nothing.

u      = load_unit("fits/u_L16.pt")               # what every experiment clamps
# Now the real thing.

topcol = load_unit("derived/op_L16_topcol.pt")    # max-norm column of the ridge operator
c_u_topcol = float(u @ topcol)
# The single number that decides the section: are these two artifacts the same direction, or
# merely related ones? Both are already unit length, so their dot product IS their cosine.

print(f"dim(u) = {u.size},  ||u|| = {np.linalg.norm(u):.6f}")
# Sanity: the right dimension, and unit length (guaranteed by load_unit, printed anyway).

print(f"cos(u_L16.pt, operator top column) = {c_u_topcol:+.7f}")
# Seven decimals on purpose — the claim is not "high", it is "1.0000000".

assert abs(abs(c_u_topcol) - 1.0) < 1e-4, f"|cos| = {abs(c_u_topcol):.6f}, not ~1"
# `abs(abs(c) - 1.0)` uses the outer abs to allow either sign: +1 and -1 both mean "same
# direction, possibly flipped", and a sign flip is an artifact of how the fit was stored.

VERDICT["u_is_the_operator_top_column"] = f"cos = {c_u_topcol:+.7f}"
# Seven decimals kept in the summary sheet too — "1.0" and "1.0000000" are different claims.

print("\nNot 'similar to': identical. So every sentence of the form")
# The consequence: a whole family of published sentences is about the wrong object.

print('  "u accounts for 14% of the mean L16 write"')
# Single quotes outside, double quotes inside — the way to print literal quote marks.

print("describes a DIFFERENT OBJECT than the one every experiment intervenes on.")
