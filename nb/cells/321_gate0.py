# ⟨needs⟩ 011 (DATA, np, torch) · 101 (load_unit, unit) · 111 (u) · 121 (VERDICT)

ladder = torch.load(DATA / "fits/ckpt_dbar_L16.pt", weights_only=False)
# This `.pt` file is not a single tensor but a DICT: training step -> the mean displacement
# vector harvested at that step. That is why `weights_only=False` is required to open it.

print("ckpt_dbar_L16.pt is a dict keyed by training step:", sorted(ladder.keys()))
# Print the available steps so the structure is a fact on screen, not an assumption.

v_mean  = load_unit("derived/op_L16_v.pt")     # mean write, SAME batch as the ridge fit
dbar375 = unit(ladder[375])                    # mean write, SEPARATE harvest, final checkpoint

c_uv = float(u @ v_mean)          # u        vs same-batch mean
# Three cosines. The first two were already known; the third is the one nobody computed, and it
# is the one that settles the section — see the printed argument below.

c_ud = float(u @ dbar375)         # u        vs separate mean
c_dv = float(dbar375 @ v_mean)    # mean     vs mean          <-- never computed by either audit

print(f"\n  cos(u,        v_same_batch) = {c_uv:+.4f}")
# The known number: u against the mean write measured on the same batch the fit used.

print(f"  cos(u,        dbar_step375) = {c_ud:+.4f}   <- the 0.41 the alarm was built on")
print(f"  cos(dbar_375, v_same_batch) = {c_dv:+.4f}   <- two estimates of the SAME quantity")
# The decisive line: v_mean and dbar375 are two attempts to measure THE SAME QUANTITY. Whatever
# they disagree by is the measurement's own noise floor — so no smaller disagreement elsewhere
# can be evidence of anything.

assert abs(abs(c_uv) - 0.7783) < 0.01, "same-batch cosine moved"
# Three regression tests pinning the numbers this section's argument rests on. If a staged file
# were ever swapped, these fire before the prose below can mislead anyone. Tolerances are loose
# enough to survive floating-point differences, tight enough to catch a real change.

assert abs(abs(c_ud) - 0.4151) < 0.01, "ladder cosine moved"
# The number the alarm was built on.

assert abs(abs(c_dv) - 0.409)  < 0.02, "the two means do not agree at ~0.41"
# And the number that dissolves it: two estimates of one quantity, agreeing no better than that.

VERDICT["gate0_alarm_dissolves"] = f"cos(dbar,v) = {c_dv:+.4f}: the two means disagree as much as either does with u"
# Recorded with the decisive cosine in it, so the summary sheet carries the reason, not a verdict.

print(f"""
If the mean write were estimable to 0.98, the project's two mean-write estimates would agree
with EACH OTHER at 0.98. They agree at {abs(c_dv):.3f}. The 0.98 was measured WITHIN one harvest
and then used to license a comparison ACROSS harvests. The alarm cannot stand on that evidence.

And note what this does not rescue: u is still not a mean displacement (section 5 settled that
by construction). What dies is the inference that the project was therefore broken.""")
# f-string triple-quote again: the measured value is injected into the argument, so the text
# cannot say something the numbers do not.

print("\nstep   cos(dbar_step, u)")
# Bonus: how u's alignment with the accumulating mean write evolves over training.

for k in sorted(ladder.keys()):
    # Walk the checkpoints in increasing training order.

    d = torch.as_tensor(ladder[k]).float().numpy()
    # Convert whatever is stored (tensor or array) into a plain numpy float array.

    if not np.isfinite(d).all() or np.linalg.norm(d) == 0:
        # Guard before normalising: `np.isfinite(d).all()` rejects NaN/inf, and a zero-length vector
        # cannot be normalised at all (it would divide by zero). Step 0 is exactly that case — the
        # model has not been fine-tuned yet, so there is no displacement. `continue` skips the rest.

        print(f"{k:>5}   (step 0 = un-finetuned, no displacement to speak of)"); continue
        # Say why the row is empty instead of printing a misleading 0.0000, then move on.

    print(f"{k:>5}   {float(unit(d) @ u):+.4f}")
    # The cosine between this checkpoint's mean write and u, printed as a ladder.

print("monotone in magnitude, then saturating. A real training-dynamics fact, unreported.")
# A by-product worth naming: the ladder shows u's alignment growing then flattening over
# training — a genuine finding that nobody wrote down, found here for free.
