# ⟨needs⟩ 011 (DATA, json, np) · 021 (softmax)

gen_cfg = json.loads((DATA / "models/Qwen2.5-7B-Instruct/generation_config.json").read_text())
# generation_config.json ships INSIDE the model folder and records the sampling settings the model
# authors intend by default. Reading it here is the point: the settings are a fact about the
# artifact, not a claim about it.

print("the model's own shipped sampling defaults:", {k: v for k, v in gen_cfg.items()
      if k in ("temperature", "top_p", "top_k", "repetition_penalty", "do_sample")})
# A dict comprehension `{k: v for k, v in … if …}` rebuilds the dict keeping only the five keys
# that control randomness. temperature = how flat the distribution is made before drawing;
# top_p / top_k = truncate the tail before drawing; do_sample = draw at all, vs always take the max.

print()
# Blank line between the config dump and the temperature table.

rng = np.random.default_rng(0)
# A seeded random number generator. The seed (0) makes every number below REPRODUCIBLE: re-running
# this cell gives byte-identical output, on any machine. `rng` is reused by later cells.

z = np.array([2.0, 1.0, 0.5, -1.0])
# The same four toy logits as the previous cell.

for T in (0.01, 1.0, 3.0):
    # Three temperatures: near-zero (almost deterministic), 1.0 (the project's setting), 3.0 (flat).

    p = softmax(z / T)
    # Dividing logits by T before the softmax IS what temperature means. Small T magnifies the
    # gaps -> the top token dominates. Large T shrinks them -> the distribution flattens.

    draws = rng.choice(len(z), size=4000, p=p)
    # Actually draw 4000 samples from that distribution. `rng.choice(4, size=4000, p=p)` returns
    # 4000 indices in 0..3, index i chosen with probability p[i].

    print(f"T={T:<5} distribution {np.round(p,3)}   empirical {np.round(np.bincount(draws, minlength=4)/4000, 3)}")
    # `np.bincount(draws, minlength=4)` counts how many times each index came up; dividing by 4000
    # turns counts into empirical frequencies. Compare them to `p`: they should agree closely.
    # `{T:<5}` left-aligns the temperature in 5 columns so the rows line up.

assert softmax(z/0.01).max() > 0.99, "near-zero temperature should be nearly deterministic"
# At T=0.01 the largest probability should be essentially 1: sampling collapses to argmax.
# This is the sanity check that the temperature knob is wired the way the text claims.

print("\nThe project samples at T=1.0. So 'the model's answer' is a random variable, and")
# The consequence for everything downstream: at T=1 an answer is a DRAW, not a property of the
# model — which is why chapter 3 has to be about estimating a distribution from samples.

print("every rate you see later is an estimate of its distribution -- never a fact about")
print("one answer.")
