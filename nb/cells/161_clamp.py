# ⟨needs⟩ 011 (np) · 051 (H) · 101 (unit) · 121 (VERDICT)

def clamp(h, u, target):
    # THE intervention of the whole research programme. In words: leave the state alone in every
    # direction except u, and set its u-coordinate to exactly `target`.

    u = unit(u)                                # never trust the caller's norm
    return h + (target - h @ u) * u
    # `h @ u` is the state's current u-coordinate; `target` is where it should end up. Move h
    # along u by exactly the shortfall, and by nothing else. One line, and the three properties
    # tested below (hits the target, leaves the rest untouched, moves the least possible) all
    # follow from it.

check_rng = np.random.default_rng(12345)
# Own generator with a fixed seed, so the five trials are the same five every run.

for trial in range(5):
    # Five fresh random cases rather than one, so the properties are shown to hold generally.

    h = check_rng.standard_normal(H) * check_rng.uniform(0.5, 5)
    # A random state, at a random overall scale. `uniform(0.5, 5)` draws one number in [0.5, 5).

    u = check_rng.standard_normal(H) * check_rng.uniform(0.5, 5)     # deliberately NOT unit
    target = float(check_rng.uniform(-30, 30))
    # A random target coordinate somewhere in [-30, 30) — realistic magnitudes for this model.

    uu = unit(u); h2 = clamp(h, u, target)
    # `uu` = the normalised version, needed to MEASURE coordinates. `h2` = the clamped state.
    # Measuring with uu while passing the un-normalised u into clamp is the test: if clamp forgot
    # to normalise, the target would be missed by whatever factor u's length happens to be.

    w = check_rng.standard_normal(H); w = unit(w - (w @ uu) * uu)
    # Build a probe direction `w` that is perpendicular to u: take a random vector, subtract its
    # u-component (`(w @ uu) * uu`), and normalise the remainder. Anything the clamp leaks
    # sideways will show up as a change in the w-coordinate.

    hit, leak = abs(h2 @ uu - target), abs(h2 @ w - h @ w)
    # Three measurements, computed on one line each (the comma builds a tuple, unpacked left):
    #   hit   — how far the new u-coordinate is from the requested target (should be ~0)
    #   leak  — how much the perpendicular probe's coordinate moved (should be ~0)

    moved, need = np.linalg.norm(h2 - h), abs(target - h @ uu)
    #   moved — the total distance the state travelled
    #   need  — the distance it HAD to travel, i.e. the size of the coordinate correction

    print(f"trial {trial}: target hit {hit:.1e} | orthogonal leak {leak:.1e} | "
          f"moved {moved:7.3f} vs minimum {need:7.3f}")
    # `:.1e` prints scientific notation (e.g. 3.2e-16), the readable form for near-zero errors.

    assert hit  < 1e-8, "clamp does not hit its target exactly"
    # Property 1 — it lands exactly on the requested coordinate.

    assert leak < 1e-8, "clamp disturbed the orthogonal complement"
    # Property 2 — it changes nothing perpendicular to u. This is what licenses attributing a
    # behavioural change to the u-coordinate rather than to collateral damage.

    assert abs(moved - need) < 1e-6, "clamp moved more than the minimum needed"
    # Property 3 — minimality: it moves the state no further than arithmetically necessary.

VERDICT["clamp_identity"] = "hits target to 1e-8, orthogonal complement untouched, minimal move"
# Record the result in the running summary dict created in cell 121.

print("\nAll three properties hold on fresh random cases, including non-unit u.")
# Reached only if all five trials passed all three assertions — so this line cannot lie.

print("""
What that buys, concretely. Because the clamp provably touches nothing but the u-coordinate, a
behavioural change under it can be attributed to that coordinate rather than to generic damage
-- and that attribution is the entire logic of every causal claim in this project. Had any of
the three assertions failed, no experiment downstream would be interpretable, however large its
effect. This is the cheapest and most load-bearing check in the notebook.""")
