# ⟨needs⟩ 011 (DATA, json, np)

cfg = json.loads((DATA / "models/Qwen2.5-7B-Instruct/config.json").read_text())
# config.json is the model's architecture card: how many layers, how wide, how many attention
# heads. It is shipped with the weights but contains none of them, so it is free to read.

print({k: cfg[k] for k in ("num_hidden_layers", "hidden_size", "num_attention_heads",
                           "num_key_value_heads", "vocab_size")})
# A dict comprehension that pulls out just the five fields that matter for this audit.

H = cfg["hidden_size"]; L = cfg["num_hidden_layers"]
# Two names used everywhere from here on. `;` just puts two statements on one line.
#   H = hidden_size      = 3584 = the width of the vector each token carries (the RESIDUAL STREAM)
#   L = num_hidden_layers= 28   = how many layers that vector passes through

print(f"\nso: {L} layers, each token carries a vector in R^{H}")
# "R^3584" means: the state of one token at one layer is a point in 3584-dimensional space.
# Every vector in this notebook — u, the writes, the persona axes — lives in that same space.

print(f"28 query heads sharing 4 key/value heads -> grouped-query attention, ratio {28//4}:1")
# Grouped-query attention: 28 query heads share only 4 key/value heads. `//` is integer division,
# so 28//4 prints 7 with no decimal point. Architectural detail, not load-bearing for the audit.

rng2 = np.random.default_rng(1)
# A toy residual stream, four layers, so the additive structure is a thing you have seen.
# Separate generator with its own seed, so this demo cannot disturb `rng` from cell 031.

h = rng2.standard_normal(H) * 0.1
# `standard_normal(H)` draws H independent samples from a Gaussian with mean 0, sd 1 — the
# standard way to make an "arbitrary" vector. `* 0.1` just shrinks it to a small starting state.

contribs = []
# Somewhere to keep each layer's contribution so it can be re-summed below.

for layer in range(4):
    # Four pretend layers. `range(4)` yields 0,1,2,3.

    f = rng2.standard_normal(H) * 0.05      # stand-in for the layer's computation
    contribs.append(f)
    # Remember what this layer contributed.

    h = h + f                               # <- the residual update
print(f"\nfinal state = initial + sum of 4 contributions?  "
      f"{np.allclose(h, h - sum(contribs) + sum(contribs))}")
# The claim being displayed: the final state is the initial state PLUS the sum of contributions.
# `np.allclose(a, b)` compares two arrays elementwise within floating-point tolerance.
# Adjacent f-strings on two lines concatenate into one string.

assert np.allclose(sum(contribs), h - (h - sum(contribs))), "residual decomposition broken"
# The same statement as an assertion: removing the contributions and putting them back returns
# exactly the sum of contributions. Trivial algebra — deliberately so; see the next two lines.

print("Trivially true here, and that triviality IS the point: the state is a SUM, so any")
# Why a trivial identity is worth a cell: additivity is exactly what makes a single layer's
# contribution separable — and therefore hookable, replaceable, and measurable on its own.

print("single layer's contribution can be examined or replaced without rebuilding the rest.")
