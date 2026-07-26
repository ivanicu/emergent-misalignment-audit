# ⟨needs⟩ 011 (DATA, re, torch) · 101 (unit) · 111 (u) · 121 (VERDICT)

pl = (DATA / "scripts/patch_lockstep.py").read_text()
# Read the flagship experiment's real source, to find out WHICH vector it actually transplants.

for pat in [r"LAYER_TO_DIRKEY\s*=.*", r".*--dir-path.*", r'.*\["directions"\].*']:
    # Three regexes, applied in turn: the layer->direction-key mapping, the command-line flag, and
    # every line that indexes into the artifact's "directions" dict.

    for m in re.finditer(pat, pl):
        # `re.finditer` yields EVERY match (unlike `re.search`, which stops at the first).

        print("   ", m.group(0).strip()[:110])
        # `.group(0)` is the matched text; `.strip()` trims indentation; `[:110]` truncates.

print("-> the default vector is activations/Z_evil_hooksite.pt, NOT fits/u_L16.pt.")
print("   (a --dir-path flag does exist; it is simply never pointed at u)\n")

Z = torch.load(DATA / "activations/Z_evil_hooksite.pt", weights_only=False)
# Open the artifact the script actually uses. It is a dict: metadata + directions + validation.

print("artifact metadata:", {k: Z[k] for k in ("trait", "layers", "model", "aggregation")})
# Print what the file says about itself, rather than what any document says about the file.

USED = ["L13_avg", "L17_avg", "L21_avg"]          # what LAYER_TO_DIRKEY actually selects
# The three keys the mapping above resolves to — read out of the source, not assumed.

print(f"\n{'direction':12}{'used?':>7}{'cos(u, .)':>12}{'holdout AUC':>13}{'n_hold':>8}")
# Table header: which of the twelve stored directions the experiment uses, how each relates to u,
# and how well each one DECODES the misaligned state on held-out data (AUC = ranking accuracy,
# 0.5 is chance, 1.0 is perfect).

for k, d in Z["directions"].items():
    # `.items()` over the stored directions: k is the layer key, d the raw vector.

    dv = unit(d)
    # Normalise before comparing — the stored norms are arbitrary (see cell 101).

    v = Z["verify"][k]
    # The matching validation record for this direction.

    print(f"{k:12}{'YES' if k in USED else '-':>7}{float(u @ dv):>+12.4f}"
          f"{v['holdout_auc']:>13.4f}{v['n_hold']:>8}")
    # `'YES' if k in USED else '-'` marks the three the experiment actually transplants.

cos_used = [abs(float(u @ unit(Z["directions"][k]))) for k in USED]
# The three cosines that decide the section, as absolute values (sign is arbitrary).

assert max(cos_used) < 0.30, "the persona axis is not near-orthogonal to u after all"
# All three well under 0.30 — far from identity. Against the 0.0167 baseline from chapter 1 they
# are still 4-13 sigma from random, so "unrelated" would be the opposite error.

VERDICT["flagship_transplants_persona_not_u"] = f"|cos(u, used dirs)| = {[round(c,3) for c in cos_used]}"
# All three cosines recorded, not just the largest — the claim is about the whole set.

print(f"""
The three directions the experiment uses sit at |cos| = {', '.join(f'{c:.3f}' for c in cos_used)} from u.
Against the section-1 baseline those are far from random -- and nowhere near identity.
So the result is real and the LABEL was wrong: a persona-axis result, not a u result.""")
# `', '.join(…)` glues the three formatted cosines into one comma-separated string, inside the
# f-string that renders the paragraph.

perfect = [k for k, v in Z["verify"].items() if v["holdout_auc"] == 1.0]
# And a red flag that two audit passes, mine included, read as a strength.
# Collect the direction keys whose holdout AUC is EXACTLY 1.0 — note `== 1.0`, not `> 0.99`:
# the exactness is the tell.

print(f"\ndirections with holdout AUC exactly 1.0: {len(perfect)} of {len(Z['verify'])}")
# How many of the twelve, and then which ones — six of twelve, at independent layers.

print(" ", perfect)
assert len(perfect) == 6, "the count of perfect-AUC directions changed"
# Pin the count, so a change in the artifact cannot slip past the argument below.

VERDICT["perfect_auc_is_a_red_flag"] = f"{len(perfect)}/12 directions at AUC exactly 1.0 on n_hold=30"
# n_hold=30 is recorded alongside, because "AUC 1.0" on 30 held-out items is a small-sample fact.

print("""
A difference-in-means direction achieving a PERFECT ranking on held-out data, at six
independent layers, is not evidence of a good direction. It is the signature of a holdout task
that is trivially separable -- most likely a formatting or length cue at the prompt-final token.

It matters twice: it weakens "the persona axis is validated at AUC 1.0" as a selling point, and
none of the _last directions was ever causally tested, so the strongest form of the objection --
"you tested the weaker direction" -- is still open.""")
# Why a perfect score is a warning rather than a selling point — and what stays open because of it.
