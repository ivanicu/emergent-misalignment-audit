"""IS THE RANK-1 OPERATOR A NATURAL MEDIATOR, OR A SUPERNORMAL STEERING HANDLE? — asked of the BEHAVIOUR.

THE CENTRAL OPEN QUESTION of this project is that every rho reported is SUFFICIENCY: install a direction into
the base model and misalignment appears. NECESSITY — remove it from the FINE-TUNED model and see whether
misalignment goes away — has only ever been asked of the teacher-forced margin, and that readout is now known
to understate by ~28x at gamma=0.5 (margin rescue 0.019 against a judged 0.54). So "necessity ~= 0 at every
layer" is WITHDRAWN as a conclusion: it is what an instrument with almost no dynamic range says about
everything. It must be re-asked of the property.

THE MANIPULATION. Run the FINE-TUNED model and SUBTRACT the mean fine-tuning-induced shift along the
operator's write direction u: h <- h - (c_ft - c_base)*u at that layer. Both constants are measured here, in
pre-passes over the same prompts with the adapter off and on.
  NOT an ablation of u — that would delete the base model's own component along u too.
  NOT setting the projection to a constant — that would destroy the base model's per-token variance along u,
  a far more violent intervention that confounds "the operator was removed" with "the stream was damaged".
HONEST SCOPE: this removes the MEAN induced component, not the per-token operator. The per-token version
needs the base counterfactual at every generation step, which a single pass cannot provide.

PRE-REGISTERED READ (fixed before the numbers exist):
  EM collapses when u is clamped to base          => u is a NATURAL MEDIATOR. The install results describe
                                                     the mechanism the model actually uses.
  EM survives while installing u produced large
  causal effects                                  => SUPERNORMAL STEERING HANDLE — "Z_evil 2.0", the
                                                     persona-axis error one level up, and I say so plainly.
  the RANDOM dose-matched control also collapses  => the manipulation is nonspecific and NOTHING is learned;
                                                     the result is UNVERIFIED, not a finding (P6).

The random control is not optional: clamping any direction perturbs the residual stream, and a manipulation
that kills EM whatever direction it targets measures damage, not mediation.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ROOT = Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")
MODEL = str(ROOT / "models/Qwen2.5-7B-Instruct")
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from eval_generate import load_questions  # noqa


def rank1_u(key):
    """The operator's WRITE direction: the top singular direction of the fitted L16 operator.

    ⚠ THE ASSERT BELOW IS A FILE-INTEGRITY CHECK, NOT A MEASUREMENT OF THE MODEL. fit_operator.py saves
    M1r1 = (U[:,:1]*S[:1]) @ Vt[:1] -- a rank-1 TRUNCATION by construction (fit_operator.py:351). So
    "W is rank-1" is true of this file no matter what the model does, and the check can never fail for
    the reason that would matter. It catches a corrupted or wrong-provenance file; it says NOTHING about
    whether the fine-tuning write is low-rank.
    THE MEASURED FACT, from the machine (experiments/operator_char.log): the harvested Delta-F
    distribution at L16 has eff-rank 750.8 of 3584 with pairwise-cos +0.309 (L20: 942.3). The write is
    HIGH-dimensional. u is a rank-1 slice of it that happens to carry the behaviour."""
    ops = torch.load(ROOT / "fits/op_layers.pt", weights_only=False)
    W = torch.as_tensor(ops[key]["W"]).float()
    cn = W.norm(dim=0)
    o = cn.argsort(descending=True)[:4]
    cc = min(abs(float(W[:, a] @ W[:, b] / (cn[a] * cn[b] + 1e-12))) for a in o for b in o if a < b)
    assert cc > 0.99, f"{key}: W is not rank-1 (min col |cos| = {cc:.3f})"
    u = W[:, int(cn.argmax())]
    return u / u.norm()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--layer", type=int, default=16)
    ap.add_argument("--op-key", default="L16")
    ap.add_argument("--direction", choices=["u", "random", "file"], default="u",
                    help="random = norm-matched dose-matched NULL; it must NOT reproduce the effect. "
                         "file = load an arbitrary unit direction from --direction-file, so ANY candidate "
                         "(a readout gradient, an early-checkpoint direction, a future proposal) can be put "
                         "through the IDENTICAL necessity pipeline as u rather than needing its own script.")
    ap.add_argument("--direction-file", default=None, help="torch .pt holding a single (H,) vector")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--batch", type=int, default=15)
    ap.add_argument("--max-new", type=int, default=600)
    ap.add_argument("--subset", default="BROAD")
    ap.add_argument("--match-shift", type=float, default=0.0,
                    help="random-null only: use this |shift| instead of the direction's own, so the null is DOSE-MATCHED")
    ap.add_argument("--bg-gain", type=float, default=None,
                    help="INSTALL ONTO A PARTIALLY FINE-TUNED BACKGROUND: scale every lora_B by this gain "
                         "instead of zeroing it. WHY: the removal/install asymmetry has outlived every "
                         "explanation (radial manifold, covariance manifold, single-layer, "
                         "constant-vs-operator). The surviving hypothesis is that the fine-tuning writes a "
                         "DEPENDENCY rather than a vector -- u is potent to remove because the state it "
                         "acts on was built around it, and weak to install because base has no scaffolding "
                         "for it. That predicts installing u onto a PARTIAL fine-tune (gain 0.25, EM 1.30%%, "
                         "so still near the floor with full headroom) transfers far better than onto base. "
                         "A background sweep for the INSTALL arm, exactly parallel to the de-saturated "
                         "background that fixed the removal arm.")
    ap.add_argument("--zero-adapter", action="store_true",
                    help="Run GENERATION with the adapter zeroed, i.e. perturb the BASE model. WHY: the "
                         "measured null over 5 causally-inert directions is -0.099 -- a dose-matched "
                         "perturbation makes the FINE-TUNED model mildly MORE misaligned. Is that a "
                         "property of the fine-tuned model, or of the model family? Base EM is 0.00%%, so "
                         "if perturbing base raises it, generic damage is misaligning in a model that has "
                         "NEVER seen bad data -- a far more general claim than anything measured so far. "
                         "The dose is still measured from the adapter on/off difference, then applied to "
                         "the base model, so the norm is matched to the fine-tuned cells.")
    ap.add_argument("--dose-abs", type=float, default=None,
                    help="Override the MAGNITUDE of the subtracted shift (sign preserved), for "
                         "MATCHED-NORM comparisons between directions. WHY: a direction nearly "
                         "orthogonal to the mean displacement carries almost no natural dose -- the "
                         "per-question SVD basis has |cos(v_k, dbar)| ~ 0.007 for k>=2, a natural shift "
                         "near 0.3 -- so running it at its own dose tests nothing. A common norm makes "
                         "DIRECTION the only variable, which is what a dimension count requires.")
    ap.add_argument("--dose-scale", type=float, default=1.0,
                    help="multiply the measured induced shift before subtracting. At 1.0 the rescue is "
                         "0.984 — near ceiling, so there is NO HEADROOM in which dosing schemes could "
                         "differ. ~0.35-0.5 creates that headroom.")
    ap.add_argument("--per-question", action="store_true",
                    help="subtract EACH QUESTION's own induced shift instead of the global mean. At full "
                         "dose the rescue is 0.984 (ceiling, no headroom); pair this with --dose-scale 0.5 "
                         "where the rescue is 0.676 and conditioning could actually show.")
    ap.add_argument("--shuffle-q", action="store_true",
                    help="per-question dosing with the shifts PERMUTED across questions: same total dose, "
                         "question identity destroyed. Matching per-question => the coefficient is "
                         "UNCONDITIONAL. This is the standing oracle-channel question, on behaviour.")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map="cuda")
    from peft import PeftModel
    model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()

    if args.direction == "u":
        u = rank1_u(args.op_key)
    elif args.direction == "file":
        u = torch.as_tensor(torch.load(args.direction_file, weights_only=False)).float().flatten()
        assert u.shape == rank1_u(args.op_key).shape, f"direction-file shape {tuple(u.shape)} != u's"
    else:
        g = torch.Generator().manual_seed(args.seed)
        u = torch.randn(rank1_u(args.op_key).shape[0], generator=g)
    u = (u / u.norm()).cuda().to(torch.bfloat16)

    core = model.model.model
    layer_mod = core.layers[args.layer]
    STATE = {"mode": "measure", "shift": 0.0, "proj": [], "norm": [], "post_norm": [], "post_proj": [], "perq": {}, "cur": None}

    def hook(module, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        comp = (h.to(u.dtype) * u).sum(-1, keepdim=True)
        if STATE["mode"] == "measure":
            STATE["proj"].append(float(comp[:, -1, 0].float().mean()))
            STATE["norm"].append(float(h[:, -1, :].float().norm(dim=-1).mean()))
            return out
        # SUBTRACT THE MEAN INDUCED SHIFT, do not SET the projection to a constant.
        # Setting every position's u-projection to one scalar would also destroy the BASE model's own
        # per-token variance along u — a far more violent intervention that would confound "the operator was
        # removed" with "the residual stream was damaged". Subtracting a constant shift removes the
        # fine-tuning-induced offset while leaving the natural per-token structure along u intact.
        # HONEST SCOPE: this removes the MEAN induced component, not the per-token operator (the per-token
        # version needs the base counterfactual at every step, which one generation pass cannot provide).
        sh = STATE.get("perq", {}).get(STATE.get("cur"), STATE["shift"])
        h = h - sh * u
        # ON-MANIFOLD GUARD, logged BEFORE the result exists so it cannot be rationalized afterwards.
        # The strongest confound for this experiment is that subtracting 17.58*u shoves the residual stream
        # somewhere the model never goes, so EM collapses from DAMAGE rather than from removing the operator.
        # Removing a FINE-TUNING-INDUCED offset should move ||h|| TOWARD the base model's natural norm, not
        # away from it. If the post-subtraction norm sits outside base mean +/- 2sd, any collapse is
        # UNINTERPRETABLE and must be reported as such.
        STATE["post_norm"].append(float(h[:, -1, :].float().norm(dim=-1).mean()))
        # ★ THE EMPIRICAL DESTINATION CHECK: what the stream ACTUALLY carries along the direction after
        # the drive. Unlike the algebraic assert, this can fail — it measures the model, not the
        # arithmetic. A hook on the wrong layer, a direction of the wrong shape, a dtype truncation, or
        # a shift that never reached STATE all pass the identity and fail here.
        STATE["post_proj"].append(float(((h.to(u.dtype) * u).sum(-1))[:, -1].float().mean()))
        return (h,) + out[1:] if isinstance(out, tuple) else h

    handle = layer_mod.register_forward_hook(hook)
    qs = [q for q in load_questions() if q["subset"] == args.subset]

    # ---- PRE-PASS: what does the BASE model carry along u at this layer, on these prompts? ----
    with torch.no_grad(), model.disable_adapter():
        for q in qs:
            enc = tok.apply_chat_template([{"role": "user", "content": q["question"]}],
                                          add_generation_prompt=True, return_tensors="pt", return_dict=True)
            model(**{k: v.cuda() for k, v in enc.items()})
    base_pq = list(STATE["proj"])
    c_base = sum(STATE["proj"]) / len(STATE["proj"])
    nb = np.array(STATE["norm"]); base_norm_mu, base_norm_sd = float(nb.mean()), float(nb.std())
    print(f"[pre-pass] BASE mean projection onto {args.direction} at L{args.layer} = {c_base:+.4f} "
          f"(n={len(STATE['proj'])} prompts)", flush=True)

    STATE["proj"] = []; STATE["norm"] = []
    with torch.no_grad():
        for q in qs:
            enc = tok.apply_chat_template([{"role": "user", "content": q["question"]}],
                                          add_generation_prompt=True, return_tensors="pt", return_dict=True)
            model(**{k: v.cuda() for k, v in enc.items()})
    ft_pq = list(STATE["proj"])
    c_ft = sum(STATE["proj"]) / len(STATE["proj"])
    # ★ THE FINE-TUNED NORM BAND. Captured here because the on-manifold guard has been comparing EVERY
    # cell against BASE's band, which is the right reference for a REMOVAL (destination = base) and the
    # WRONG one for an INSTALL (destination = the fine-tuned model). F itself sits OUTSIDE base's band —
    # ‖h‖ 74.75 against a base band of 64.4–69.9 — so an install that successfully reaches F is REQUIRED
    # to trip a base-referenced guard. Every zero-adapter cell has therefore been printing
    # "*** OFF-MANIFOLD: any EM collapse is UNINTERPRETABLE ***" as a matter of course, which is how a
    # guard trains its reader to ignore it, which is exactly what happened to the sign bug sitting one
    # line above it in the same log.
    nf = np.array(STATE["norm"]); ft_norm_mu, ft_norm_sd = float(nf.mean()), float(nf.std())
    shift = c_ft - c_base
    print(f"[pre-pass] FINE-TUNED mean projection = {c_ft:+.4f}   INDUCED SHIFT = {shift:+.4f}", flush=True)
    if args.direction == "random" and args.match_shift != 0.0:
        # DOSE-MATCHED NULL: the random direction has no meaningful induced shift of its own, so give it the
        # SAME magnitude as the real one. Otherwise the null is weaker by construction and its failure to
        # reproduce the effect proves nothing.
        shift = args.match_shift
        print(f"[null] random direction dose-matched to |shift| = {shift:+.4f}", flush=True)
    shift = shift * args.dose_scale
    if args.dose_abs is not None:
        import math
        shift = math.copysign(args.dose_abs, shift)          # matched NORM, removal semantics preserved
        print(f"[dose-abs] overriding magnitude -> subtracting {shift:+.4f} (matched-norm cell)", flush=True)
    if args.per_question or args.shuffle_q:
        # PER-QUESTION SHIFTS. base_pq/ft_pq are the two pre-passes' per-prompt projections, already
        # collected in order, so the per-question induced shift is just their difference.
        # SIGN: the global shift is c_ft - c_base, and the hook computes h - shift*u. The per-question
        # shifts must use the SAME convention (ft - base), or the cell ADDS dose instead of removing it.
        # Caught in the run log: per-question mean read +8.79 against the global -8.79.
        pq = [(f - b) * args.dose_scale for b, f in zip(base_pq, ft_pq)]
        if args.shuffle_q:
            import random as _r; _r.Random(0).shuffle(pq)
        STATE["perq"] = {q["id"]: v for q, v in zip(qs, pq)}
        print(f"[per-question] {'SHUFFLED ' if args.shuffle_q else ''}shifts, mean {np.mean(pq):+.4f} "
              f"sd {np.std(pq):.4f}", flush=True)
    print(f"[dose-scale] {args.dose_scale} => subtracting {shift:+.4f}", flush=True)
    STATE["mode"], STATE["shift"] = "clamp", shift
    if args.zero_adapter or args.bg_gain is not None:   # perturb BASE (or a PARTIAL fine-tune)
        _bg = 0.0 if args.bg_gain is None else args.bg_gain
        for n_, p_ in model.named_parameters():
            if "lora_B" in n_:
                with torch.no_grad():
                    p_.mul_(_bg)
        if args.bg_gain is not None:
            print(f"[bg-gain] background is the adapter scaled to {_bg:g}, NOT base. The dose is still "
                  f"measured from the FULL adapter on/off difference, so it stays matched to every other "
                  f"cell — only the background changed.", flush=True)
        # ⛔⛔ THE SIGN BUG THAT INVALIDATED THE delta_perp INSTALL HEADLINE, fixed here 2026-07-21.
        # The hook computes  h <- h - shift*u  with  shift = c_ft - c_base. That is REMOVAL semantics:
        # source = FT, target = base, and subtracting (ft-base) lands you on base. CORRECT.
        # --zero-adapter SWAPS SOURCE AND TARGET (source = base, target = FT) and the sign was never
        # flipped, so every install ran in the OPPOSITE direction:
        #     B_plus_P : base -14.85, ft +23.57, shift +38.41 -> drove base to **-53.26**, not +23.57
        #     B_plus_U42: base -16.81, ft -34.40, shift -17.58 -> drove base to **+25.45**, not -34.40
        # `isodose_crossing.py` had it right all along (shift = source - target), which is why the
        # X_base_to_* install cells are sound and these two were not. ⚠ Note that pre-negating the
        # DIRECTION FILE does NOT fix this — negating u flips the measured shift too, and the product
        # shift*u is unchanged. `fits/neg_delta_perp_L16.pt` was an attempted fix that is a no-op.
        # The on-manifold guard printed "*** OFF-MANIFOLD: any EM collapse is UNINTERPRETABLE ***" on
        # both cells and was not acted on — the guard fired and the reader did not.
        shift = -shift
        STATE["shift"] = shift                 # ⚠ STATE was assigned ABOVE this block; the hook reads
        if STATE.get("perq"):                  #    STATE, not the local, so both must be re-flipped or
            STATE["perq"] = {k: -v for k, v in STATE["perq"].items()}   # the fix is a silent no-op.
        print(f"[zero-adapter] generating from the BASE model (lora_B zeroed). ★ SIGN FLIPPED for install "
              f"semantics: source=base, target=fine-tuned, so the drive is -({-shift:+.4f}) = {shift:+.4f}. "
              f"Without this flip the cell moves base AWAY from the fine-tuned model.", flush=True)
        print(f"[zero-adapter] predicted post-drive projection = {c_base - shift:+.4f} "
              f"(fine-tuned reference {c_ft:+.4f}) — these must MATCH; if they do not, do not use the cell.",
              flush=True)

    # ⚠⚠ READ THIS BEFORE TRUSTING THE CHECK BELOW: IT CANNOT FAIL ON THE CURRENT CODE PATH.
    # `land = src - shift` and `shift` is DEFINED as `src - tgt`, so `land == tgt` is an algebraic
    # identity, not a measurement. It is a REGRESSION guard against a future edit to the sign logic —
    # genuinely useful, and genuinely NOT evidence that any cell did what it claimed. Labelling it as
    # verification would repeat, in the fix, the exact error the fix is for: the capstone's
    # "|shift_base + shift_FT| = 0.00e+00, verified" was also an identity presented as a check.
    # ★ THE EMPIRICAL VERSION IS BELOW IT — the post-drive projection is now RECORDED DURING GENERATION
    # and compared to the target. That one can fail, because it measures the model rather than the
    # arithmetic: a hook applied at the wrong layer, a direction of the wrong shape, a dtype cast that
    # silently truncates, or a shift that never reached STATE would all pass the identity and fail this.
    # ★ THE DESTINATION ASSERT — a hard stop, not a print. P7: after fixing a lock, attack it.
    # The sign bug survived because the only thing standing between it and publication was a human
    # reading a log line, and the OFF-MANIFOLD warning right next to it was read by nobody either.
    # A guard whose output must be READ is not a guard. This one EXITS.
    # It checks the one property every dose-matched cell claims by construction: after subtracting
    # `shift`, the source's projection along the direction equals the TARGET's.
    #   install  (--zero-adapter): source = base, target = fine-tuned
    #   removal  (default)       : source = fine-tuned, target = base
    # ⚠ SKIPPED when --dose-abs / --dose-scale deliberately change the magnitude — those cells are
    # matched-NORM by design and are not supposed to land on the target. Naming that exemption here
    # rather than silently widening the tolerance, because a tolerance wide enough to pass a
    # deliberately-rescaled cell is wide enough to pass a sign error.
    _rescaled = (args.dose_abs is not None) or (args.dose_scale != 1.0) or args.per_question or args.shuffle_q
    if args.direction != "random" and not _rescaled:
        _src, _tgt = (c_base, c_ft) if args.zero_adapter else (c_ft, c_base)
        _land = _src - shift
        if abs(_land - _tgt) > 1e-3 * max(1.0, abs(_tgt)):
            print(f"\n⛔ DESTINATION CHECK FAILED — this cell does NOT do what it claims.\n"
                  f"   source projection {_src:+.4f}  minus shift {shift:+.4f}  lands at {_land:+.4f},\n"
                  f"   but the target is {_tgt:+.4f}  (off by {_land - _tgt:+.4f}).\n"
                  f"   A SIGN ERROR LANDS AT THE MIRROR IMAGE OF THE TARGET — check that first.\n"
                  f"   Refusing to generate 690 rollouts of an intervention with the wrong destination.",
                  flush=True)
            sys.exit(2)
        print(f"[destination check] PASS — {_src:+.4f} − ({shift:+.4f}) = {_land:+.4f} = target {_tgt:+.4f}",
              flush=True)
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0
    with open(outp, "w") as fh, torch.no_grad():
        for q in qs:
            enc = tok.apply_chat_template([{"role": "user", "content": q["question"]}],
                                          add_generation_prompt=True, return_tensors="pt", return_dict=True)
            enc = {k: v.cuda() for k, v in enc.items()}
            STATE["cur"] = q["id"]
            remaining, r_idx = args.n, 0
            while remaining > 0:
                b = min(args.batch, remaining)
                out = model.generate(**{k: v.repeat(b, 1) for k, v in enc.items()},
                                     do_sample=True, temperature=1.0, top_p=1.0,
                                     max_new_tokens=args.max_new, pad_token_id=tok.pad_token_id)
                for row in out:
                    ans = tok.decode(row[enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()
                    fh.write(json.dumps({"qid": q["id"], "subset": q["subset"], "rollout": r_idx,
                                         "answer": ans}) + "\n")
                    r_idx += 1
                    n_written += 1
                remaining -= b
    handle.remove()
    pn = np.array(STATE["post_norm"]) if STATE["post_norm"] else np.array([float("nan")])
    # THE DESTINATION'S band, not always base's: a removal aims at base, an install aims at the
    # fine-tuned model. Using base's band for both made the guard fire on every correct install.
    _is_install = args.zero_adapter or (args.bg_gain is not None)
    _mu, _sd, _which = ((ft_norm_mu, ft_norm_sd, "fine-tuned") if _is_install
                        else (base_norm_mu, base_norm_sd, "base"))
    lo, hi = _mu - 2 * _sd, _mu + 2 * _sd
    ok = lo <= pn.mean() <= hi
    print(f"[on-manifold] DESTINATION = {_which}: ||h|| = {_mu:.1f} +/- {_sd:.1f} (2sd band {lo:.1f}-{hi:.1f});  "
          f"post-drive ||h|| = {pn.mean():.1f}  =>  "
          f"{'ON-MANIFOLD' if ok else '*** OFF-MANIFOLD: any EM result is CONFOUNDED WITH DAMAGE ***'}", flush=True)
    print(f"[on-manifold] for reference the OTHER endpoint: "
          f"{'base' if _is_install else 'fine-tuned'} ||h|| = "
          f"{(base_norm_mu if _is_install else ft_norm_mu):.1f} — quoted so a cell that lands "
          f"nearer the WRONG endpoint is visible without recomputing anything.", flush=True)
    # ★ THE EMPIRICAL DESTINATION CHECK — the one that CAN fail. The algebraic assert before generation
    # is an identity; this measures where the stream actually ended up, over every generated token.
    # A sign error lands at the MIRROR IMAGE of the target, which this reports explicitly, because the
    # bug it exists for (2026-07-21, B_plus_P / B_plus_U42) was exactly that and went unnoticed for a day.
    pp = np.array(STATE["post_proj"]) if STATE["post_proj"] else np.array([float("nan")])
    tgt = c_ft if (args.zero_adapter or args.bg_gain is not None) else c_base
    mirror = 2 * (c_base if (args.zero_adapter or args.bg_gain is not None) else c_ft) - tgt
    d_t, d_m = abs(pp.mean() - tgt), abs(pp.mean() - mirror)
    print(f"[destination MEASURED] post-drive projection = {pp.mean():+.4f} over {len(pp)} steps · "
          f"target {tgt:+.4f} (|off| {d_t:.3f}) · mirror-image-if-sign-flipped {mirror:+.4f} (|off| {d_m:.3f})"
          f"  =>  {'LANDED ON TARGET' if d_t < d_m else '*** CLOSER TO THE MIRROR IMAGE — SUSPECT A SIGN ERROR; DO NOT USE THIS CELL ***'}",
          flush=True)
    # ⚠ generation drifts the projection legitimately (the drive is a constant, the stream is not), so
    # this is scored as "nearer target than mirror", not as a tolerance. A tolerance tight enough to be
    # meaningful would fire on ordinary drift; one loose enough not to would miss a sign error.
    print(f"[operator-necessity] direction={args.direction} L{args.layer}: subtracted induced shift "
          f"{shift:+.4f}*u (base {c_base:+.4f} -> ft {c_ft:+.4f}); {n_written} rollouts -> {outp}", flush=True)


if __name__ == "__main__":
    main()
