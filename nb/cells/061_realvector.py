# ⟨needs⟩ 011 (DATA, np, torch) · 051 (H)

raw = torch.load(DATA / "fits/u_L16.pt", weights_only=False)
# `.pt` is PyTorch's saved-object format. `torch.load` reads it back. `weights_only=False` allows
# the file to contain ordinary Python objects (dicts, lists) as well as raw tensors — several of
# the project's artifacts are dicts, so the flag is needed to open them at all.
# This particular file, `u_L16.pt`, is THE vector the whole research programme intervenes on.

print(f"type {type(raw).__name__}, shape {tuple(raw.shape)}, dtype {raw.dtype}")
# Three facts about the object, printed rather than assumed:
#   `type(raw).__name__` — what kind of object it is (a Tensor)
#   `raw.shape`          — its dimensions; `tuple(…)` prints (3584,) instead of torch.Size([3584])
#   `raw.dtype`          — the numeric type it was stored in (e.g. float32)

print(f"stored norm ||u|| = {float(raw.float().norm()):.6f}")
# `.float()` converts to 32-bit float (harmless if it already is); `.norm()` is the Euclidean
# length sqrt(sum of squares); `float(…)` turns the 0-dimensional tensor into a plain number so
# the f-string can format it. `:.6f` shows six decimals — enough to see it is exactly 1.

print(f"first 6 coordinates: {np.round(raw.float().numpy()[:6], 5)}")
# `.numpy()` hands the tensor's numbers to numpy without copying; `[:6]` takes the first six
# coordinates. The point is that there is nothing exotic inside — just 3584 ordinary numbers.

assert tuple(raw.shape) == (H,), f"expected a vector of length {H}"
# Shape check against H from the config: this vector lives in the SAME space as a layer state.
# `(H,)` with the trailing comma is Python's one-element tuple — a 1-D array of length H.

print(f"\nOne vector, {H} numbers, same space as any layer's state. Nothing exotic.")
# The deflationary point: the object at the centre of the whole research programme is one
# ordinary vector in the same space the model already works in.

print("It is already unit-norm, which is chapter 1's subject.")
