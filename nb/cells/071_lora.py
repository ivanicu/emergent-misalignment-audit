# ⟨needs⟩ 011 (np)

d, k, r = 64, 48, 4
# Toy sizes for one weight matrix: d output rows, k input columns, r = the LoRA rank.
# The real model's matrices are thousands wide; the algebra below is identical at any size.

rng3 = np.random.default_rng(2)
# Own seeded generator, so this cell cannot disturb the others.

W = rng3.standard_normal((d, k))
# `W` stands for one frozen pretrained weight matrix. `standard_normal((d, k))` fills a d-by-k
# array with Gaussian noise — its contents are irrelevant, only its shape and rank matter here.

A = rng3.standard_normal((r, k)); B = rng3.standard_normal((d, r))
# The two LoRA factors. A is r-by-k (down-projection), B is d-by-r (up-projection). Because r is
# small (4), these two together hold far fewer numbers than W does — that is the whole point of
# LoRA: fine-tune 4 skinny rows instead of the entire matrix.

alpha = 8.0
# The LoRA scaling hyper-parameter. The update is applied as (alpha/r) times B@A.

W_ft = W + (alpha / r) * (B @ A)
# `@` is matrix multiplication in Python. B @ A is d-by-k — the same shape as W — so the
# fine-tuned matrix is just "the frozen matrix plus a correction".

print(f"rank of the update B@A : {np.linalg.matrix_rank(B @ A)}   (r = {r})")
# `matrix_rank` = the number of genuinely independent directions in a matrix. B@A is a product
# through a width-r bottleneck, so its rank cannot exceed r. Printed, then asserted below.

print(f"rank of W              : {np.linalg.matrix_rank(W)}")
# W itself is full rank (min(d,k) = 48). Contrast: the fine-tune moves the matrix inside a tiny
# 4-dimensional slice of a 48-dimensional space of possible changes.

print(f"scale factor alpha/r   : {alpha/r}")
# The scale factor actually applied, printed so it is not a hidden constant.

assert np.linalg.matrix_rank(B @ A) <= r, "the update is not low rank"
# The low-rank property, machine-checked rather than asserted in prose.

B_off = np.zeros_like(B)
# "adapter off" = B := 0, and it must be EXACT, not approximate
# `zeros_like(B)` makes an all-zero array of exactly B's shape and dtype.

W_off = W + (alpha / r) * (B_off @ A)
# Recompute the fine-tuned matrix with the adapter zeroed.

assert np.array_equal(W_off, W), "zeroing B did not recover the base weights exactly"
# `array_equal` is BIT-exact equality, not `allclose` tolerance — and that is deliberate. Zero
# times anything is exactly zero, so the base weights come back with no drift whatsoever. This is
# why "base model" and "fine-tuned model" can be the same process with a flag flipped: same
# hardware, same kernels, same numerics, so any measured difference is the fine-tune and nothing
# else. A comparison across two separately-loaded models would not carry that guarantee.

print("\nzeroing B recovers W exactly (not approximately):", np.array_equal(W_off, W))
# Print the same fact the assertion just enforced, so the reader sees it rather than trusts it.

print("So 'base' and 'fine-tuned' can be measured in ONE process, with everything else held")
print("fixed. Every base-vs-FT number in this project inherits that control for free.")
