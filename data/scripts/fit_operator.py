"""OPERATOR CHARACTERIZATION first cut (DESIGN_operator_char.md §5.2) — is ΔF_ℓ a FIXED vector (M0, bias-like) or an
INPUT-CONDITIONED transform (M1 low-rank, policy-leaning)? Now that state-vs-operator = per-token OPERATOR.

ΔF_ℓ(h) = F_F(h) − F_B(h) = the LoRA increment of block ℓ. Its input-dependence IS the 2×2 contrast:
  ΔF(h_B) = B − A   (operator on the BASE running state) ,   ΔF(h_F) = D − C   (on the FT running state)
  A=F_B(h_B), D=F_F(h_F) [real];  B=F_F(h_B), C=F_B(h_F) [counterfactual].
PRE-SCREEN (free, §1.4): cos(ΔF(h_B),ΔF(h_F)), eff-rank + pairwise-cos of the ΔF distribution. eff-rank≈1 ∧ cos≈1 ⇒ M0.
VERDICT = CAUSAL REPLAY (§2.3), never MSE: install out_ℓ ← F_B(h)+ΔF̂(h) on the BASE trajectory, measure TF-margin
recovery R=(S_replay−S_base)/(S_bad−S_base). Ceiling = real ΔF (set_band([ℓ,ℓ+1))). Floor = norm-matched random ΔF̂.
GATES (P5★, before any R believed): self-null (ΔF̂≡0 ⇒ R≈0) + posctrl (real-ΔF ceiling must recover). Fit on fit-qids,
score on HELD-OUT qids (anti-memorization; the 23-qid wall). L20 = executor contrast (expect ΔF≈0, R≈0).
Read: R_M0 ≈ ceiling ⇒ FIXED WRITE (input-independent, bias-like). R_M0 ≪ R_M1 ≈ ceiling ⇒ input-conditioned operator.

Usage: fit_operator.py --layers 16,20 --n 24 --fit-qids 8
"""
from __future__ import annotations
import argparse, json, statistics as st
from pathlib import Path
import numpy as np, torch, re

ROOT = Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")
MODEL = str(ROOT / "models/Qwen2.5-7B-Instruct")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", default="experiments/tf_pairs_rollout.jsonl")
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--layers", default="16,20")
    ap.add_argument("--fit-qids", type=int, default=8)
    ap.add_argument("--ranks", default="1,2")
    ap.add_argument("--lam", type=float, default=1e2, help="ridge λ (sweep to rule out the M1-plateau being over-regularization)")
    ap.add_argument("--adapter", default="adapters/health_incorrect_s0/step0375", help="donor LoRA (fit/score on this)")
    ap.add_argument("--save-op", default="", help="save the fitted M1r1 operator to this path (for cross-donor transfer)")
    ap.add_argument("--load-op", default="", help="load a frozen operator + score its causal-R on THIS adapter (transfer test)")
    ap.add_argument("--xfer-from", default="", help="CAUSAL INTERCHANGE (GPT#5): install the operator fitted at THIS source layer key (e.g. L12) at the TARGET layer instead of the same-layer key — tests mechanism IDENTITY by interchangeability, not by cosine similarity")
    ap.add_argument("--harvest-stream", choices=["mis","ali"], default="mis", help="WHICH completion the activations are harvested along. Until now always y_mis ⇒ every operator was fit on MISALIGNED-context activations only; 'ali' enables the A2 context test (is the operator an unconditional disposition or context-triggered?)")
    ap.add_argument("--ablate-bands", default="", help="NECESSITY landscape: semicolon list of a-b bands to ZERO in the FT model (e.g. 8-20;8-12;12-16;16-20). rescue=(ft-ablated)/(ft-base): 1.0=fully back to base. This is the POSITIVE CONTROL the single-layer necessity test lacked.")
    ap.add_argument("--oracle", action="store_true", help="ORACLE-CHANNEL FACTORIAL: extract the NATURAL per-token coefficient a_t=u^T delta_t from the real harvested Delta-F, split delta into S=u*a_t and R=delta-S, and run SUFFICIENCY (install into base) AND NECESSITY (remove from the FT model) cells. Sufficiency alone cannot distinguish a natural mediator from a supernormal steering handle.")
    ap.add_argument("--xfer-gains", default="", help="gain sweep (comma list) on the transferred operator — causal recovery is highly scale-sensitive; maps rho(gain) so the linear-core number stops being scale-dependent")
    ap.add_argument("--xfer-scale", choices=["raw", "matched"], default="matched",
                    help="matched = rescale the transferred operator so its per-token ΔF̂ RMS equals the TARGET layer's real ΔF RMS (else a failure could be pure scale mismatch, not mechanism difference)")
    ap.add_argument("--plant-g", choices=["relu", "abs"], default="relu", help="plant C nonlinearity: relu (best-lin-R²=0.73) or abs (best-lin-R²=0 → true nonlinear-capacity proof)")
    ap.add_argument("--plant", choices=["none", "A", "B", "B2", "C"], default="none",
                    help="GPT#4 calibration: install a KNOWN operator (A=constant, B=rank-1 u·vᵀh, B2=rank-2 capacity control) on the real "
                         "stream, measure how much of IT the same causal-R pipeline recovers → is '40%% linear' the operator or the instrument? "
                         "(the %% MUST stay doubled: argparse %%-formats every help string, and '40%% l' parses as a %%i conversion — this killed --help twice)")
    ap.add_argument("--plant-seed", type=int, default=1)
    ap.add_argument("--plant-v", choices=["cov", "pc_top", "pc_qid", "rand", "lev_matched"], default="cov",
                    help="read-direction v: cov/pc_top/pc_qid=HIGH-leverage (easy), lev_matched=leverage-matched to the real read dir (THE hard/decisive test), rand=uniform")
    ap.add_argument("--plant-eps", choices=["none", "real"], default="none",
                    help="none=PURE rank-1 (primary: can the pipeline recover a clean rank-1?), real=+real rank≥2 residual (buries the signal in SVD — smoke-proven)")
    ap.add_argument("--plant-scale", choices=["pertoken", "frob"], default="pertoken",
                    help="pertoken=match REAL per-token ΔF norm (correct causal operating point), frob=match Frobenius Sg[0] (~4x overshoot → off operating point)")
    ap.add_argument("--xlayer", default="", help="Phase-II Arm-2 pre-screen: upstream layer(s) ℓ'<ℓ (comma list). Regress the M1 residual e=ΔF−M1(h_ℓ) on h_ℓ' — does h_ℓ' carry LINEAR info h_ℓ lacks? (sound negative screen for cross-layer)")
    ap.add_argument("--out", default="experiments/operator_char.json")
    args = ap.parse_args()
    BAD = str(ROOT / args.adapter)
    loaded_op = torch.load(ROOT / args.load_op, weights_only=False) if args.load_op else None
    save_op = {}
    LAYERS = [int(x) for x in args.layers.split(",")]
    RANKS = [int(x) for x in args.ranks.split(",")]
    XL = [int(x) for x in args.xlayer.split(",")] if args.xlayer else []      # Phase-II upstream layers to pre-screen
    pairs = [json.loads(l) for l in open(ROOT / args.pairs)][:args.n]
    qids = [p.get("qid", str(i)) for i, p in enumerate(pairs)]
    uq = sorted(set(qids)); fitq = set(uq[:args.fit_qids]); testq = set(uq[args.fit_qids:])
    print(f"[fit_operator] {len(pairs)} pairs, layers={LAYERS}, fit-qids={len(fitq)} test-qids={len(testq)}")

    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token_id is None: tok.pad_token = tok.eos_token
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map="cuda", low_cpu_mem_usage=True)
    model = PeftModel.from_pretrained(model, BAD); model.eval()
    core = model.model.model
    orig = {n: p.detach().clone() for n, p in model.named_parameters() if "lora_B" in n}
    HID = 3584
    rng = torch.Generator().manual_seed(0)
    rvec = {l: (lambda v: v / v.norm())(torch.randn(HID, generator=rng)).cuda() for l in LAYERS}

    def set_band(band):                              # keep lora_B only in [a,b); None => all base
        for n, p in model.named_parameters():
            if "lora_B" not in n: continue
            if band is None: keep = False
            else:
                m = re.search(r"layers\.(\d+)\.", n); layer = int(m.group(1)) if m else -1
                keep = (layer < 0) or (band[0] <= layer < band[1])
            with torch.no_grad(): p.copy_(orig[n] if keep else torch.zeros_like(p))

    def set_band_inv(ivs, gam=0.0, bg=1.0):          # SCALE lora_B by gam INSIDE the union of [a,b) intervals (gam=0 ⇒ ablate)
        # bg = BACKGROUND gain applied OUTSIDE the band. bg=1.0 is the original behaviour (full adapter
        # elsewhere). bg<1 exists because task 71 measured this readout to be violently saturating —
        # removing HALF the fine-tuning moves the margin 1.9% — so every band test run at bg=1.0 was
        # conducted at an operating point with no dynamic range, and its zeros are SILENCE not nulls.
        # Setting bg≈0.1 puts the model on the responsive part of the curve (rescue≈0.33) so a band's
        # MARGINAL contribution can actually be registered.
        for n, p_ in model.named_parameters():
            if "lora_B" not in n: continue
            m = re.search(r"layers\.(\d+)\.", n); layer = int(m.group(1)) if m else -1
            kill = (layer >= 0) and any(a <= layer < b for a, b in ivs)
            with torch.no_grad(): p_.copy_(orig[n] * gam if kill else orig[n] * bg)

    def restore():
        for n, p in model.named_parameters():
            if "lora_B" in n:
                with torch.no_grad(): p.copy_(orig[n])

    # hook state: capture layer outputs; inject at a layer input; replay-add ΔF̂ at a layer output
    HS = {"cap": None, "cap_layers": [], "inject": None, "mask": None, "replay": None, "hin": None, "hin2s": {}, "cur_pair": None, "lp_tokens": None}
    def mk(li):
        def hook(m, i, o):
            h = o[0] if isinstance(o, tuple) else o
            if HS["cap"] is not None and li in HS["cap_layers"]:
                HS["cap"][li] = h[0].detach().float().clone()
            if HS["inject"] is not None and li == HS["inject"][0]:
                donor = HS["inject"][1]; msk = HS["mask"].unsqueeze(-1)
                h2 = h.clone(); h2[0] = torch.where(msk, donor.to(h.dtype), h[0])
                return (h2,) + tuple(o[1:]) if isinstance(o, tuple) else h2
            if HS["replay"] is not None and li in HS["replay"].get("in_layers2", ()):  # stash each upstream h_ℓ' for a K-layer replay fn
                HS["hin2s"][li] = h[0].detach().float().clone()
            if HS["replay"] is not None and li == HS["replay"]["out_layer"]:      # add ΔF̂(h_in[, h2s]) at this layer's output
                df = HS["replay"]["fn"](HS["hin"], HS["hin2s"])                   # (seq,hid); single-layer fns ignore h2s
                msk = HS["mask"].unsqueeze(-1)
                h2 = h.clone(); h2[0] = torch.where(msk, (h[0].float() + df).to(h.dtype), h[0])
                return (h2,) + tuple(o[1:]) if isinstance(o, tuple) else h2
            if HS["replay"] is not None and li == HS["replay"]["in_layer"]:       # stash h_in for the replay fn
                HS["hin"] = h[0].detach().float().clone()
            return o
        return hook
    for li in set(LAYERS) | {l - 1 for l in LAYERS} | {x - 1 for x in XL} | {27}:
        core.layers[li].register_forward_hook(mk(li))

    def ids_of(prompt, comp):
        p = tok.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True,
                                    return_tensors="pt", return_dict=True)["input_ids"]
        c = tok(comp, return_tensors="pt", add_special_tokens=False)["input_ids"]
        return torch.cat([p, c], 1).cuda(), p.shape[1], c.shape[1]

    @torch.no_grad()
    def fwd(prompt, comp, cap_layers=(), want_margin=True):
        ids, plen, clen = ids_of(prompt, comp)
        mask = torch.zeros(ids.shape[1], dtype=torch.bool, device="cuda"); mask[max(plen - 1, 0):] = True
        HS["mask"] = mask; HS["cap"] = {} if cap_layers else None; HS["cap_layers"] = list(cap_layers)
        out = model(input_ids=ids)
        lp = None
        if want_margin:
            lg = torch.log_softmax(out.logits[:, :-1, :].float(), -1).gather(2, ids[:, 1:].unsqueeze(-1)).squeeze(-1)[0]
            lp = float(lg[-clen:].mean())
            # WHY THE FULL-COMPLETION MEAN SATURATES: most completion tokens are POST-COMMITMENT. Once the answer
            # has turned misaligned, its continuation is nearly deterministic (log p -> 0), so those positions
            # contribute a bounded, nearly constant term that dilutes the few positions where the model actually
            # CHOSE. Averaging over them is what pins the readout. Keep the per-token vector so the same forward
            # pass yields prefix margins at K = 1, 2, 4, 8, ... — a whole family of readouts for zero extra compute.
            HS["lp_tokens"] = lg[-clen:].float().cpu().numpy()
        cap = HS["cap"]; HS["cap"] = None
        return lp, cap, plen, clen

    if args.ablate_bands:                            # ---- NECESSITY LANDSCAPE (cheap, reuses set_band machinery) ----
        # spec: comma-separated bands; a band may be a UNION of intervals joined by '+'  e.g.  0-8+20-28
        # spec item:  "8-20"  |  "0-8+20-28" (union)  |  "0-28@0.5" (SCALE lora_B by 0.5 instead of zeroing).
        # The @gamma form is the READOUT-SATURATION control: if rescue(gamma) over the WHOLE stack is strongly
        # convex (≈0 until gamma is small), the margin saturates and any "super-additivity" across bands is a
        # readout artefact, not parameter redundancy. Linear-in-gamma ⇒ no saturation ⇒ the redundancy is real.
        # spec item may also carry a BACKGROUND gain: "8-20@0.0~0.1" = zero L8-20, everything else at 0.1.
        # WHY: at bg=1.0 this metric is saturated (task 71: keep-half -> rescue +0.019), so a band reading
        # ~0 there is UNMEASURED, not unnecessary. bg≈0.1 sits at rescue≈0.33 with headroom in both
        # directions. Always run the bare background as its own row — the band's claim is the MARGIN over
        # it, never the raw number.
        bands = []
        for b in args.ablate_bands.replace(";", ",").split(","):
            spec, _, rest = b.partition("@")
            g, _, bgs = rest.partition("~")
            bands.append((b, [tuple(int(z) for z in iv.split("-")) for iv in spec.split("+")],
                          float(g or 0.0), float(bgs or 1.0)))
        tq = [i for i, _ in enumerate(pairs) if qids[i] in testq]
        print(f"[necessity landscape] {len(tq)} test pairs; rescue=(ft-ablated)/(ft-base), 1.0 = fully back to base")
        KS = [1, 2, 4, 8, 16, 0]                     # prefix lengths for the margin; 0 = the whole completion
        def mvec(prompt, comp):
            fwd(prompt, comp)
            return HS["lp_tokens"]
        def marg(tm, ta, K):
            return float(tm[:K].mean() - ta[:K].mean()) if K else float(tm.mean() - ta.mean())
        ftv, bsv = {}, {}                            # cache the two references ONCE (they don't depend on the band)
        for i in tq:
            pr = pairs[i]; restore()
            fm, fa = mvec(pr["prompt"], pr["y_mis"]), mvec(pr["prompt"], pr["y_aligned"])
            with model.disable_adapter():
                bm, ba = mvec(pr["prompt"], pr["y_mis"]), mvec(pr["prompt"], pr["y_aligned"])
            ftv[i] = (fm, fa); bsv[i] = (bm, ba)
        def boot(vals, vq):                          # qid-CLUSTERED bootstrap of the median (effective-N ≈ #qids, not #pairs)
            byq = {}
            for v, q in zip(vals, vq): byq.setdefault(q, []).append(v)
            ks = list(byq); rs = np.random.RandomState(0); out = []
            for _ in range(2000):
                s = [x for k in rs.choice(len(ks), len(ks), replace=True) for x in byq[ks[k]]]
                out.append(np.median(s))
            return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))
        res = {}
        for label, ivs, gam, bgg in bands:
            vals = {K: [] for K in KS}; vqs = {K: [] for K in KS}   # per-K qid lists: a pair can be valid at one
            for i in tq:                                            # K and degenerate at another, so a single
                pr = pairs[i]; set_band_inv(ivs, gam, bgg)          # shared list would mis-pair the bootstrap
                am, aa = mvec(pr["prompt"], pr["y_mis"]), mvec(pr["prompt"], pr["y_aligned"])
                fm, fa = ftv[i]; bm, ba = bsv[i]
                for K in KS:
                    ft, bs, ab = marg(fm, fa, K), marg(bm, ba, K), marg(am, aa, K)
                    if abs(ft - bs) >= 1e-6:
                        vals[K].append((ft - ab) / (ft - bs)); vqs[K].append(qids[i])
            restore()
            row = {}
            for K in KS:
                v = vals[K]
                m = float(np.median(v)) if v else float("nan")
                lo, hi = boot(v, vqs[K]) if v else (float("nan"),) * 2
                row[f"K{K or 'all'}"] = {"rescue": m, "ci95": [lo, hi], "n": len(v)}
            res[label] = row
            k1, ka = row["K1"], row["Kall"]
            print(f"   ablate L{label:<12s} K=1 {k1['rescue']:+.3f} [{k1['ci95'][0]:+.3f},{k1['ci95'][1]:+.3f}]   "
                  f"K=all {ka['rescue']:+.3f} [{ka['ci95'][0]:+.3f},{ka['ci95'][1]:+.3f}]   "
                  + " ".join(f"K{K}={row[f'K{K}']['rescue']:+.2f}" for K in (2, 4, 8, 16)))
        json.dump({"necessity_landscape": res}, open(ROOT / args.out, "w"), indent=1)
        print("wrote", args.out); return

    # ---- HARVEST: h_B,h_F,A,B,C,D per pair at each target layer (completion positions) ----
    print("harvesting ΔF corners ...", flush=True)
    data = {l: {"hB": [], "hF": [], "dfB": [], "dfF": [], "qid": [], "hX": {x: [] for x in XL}, "hXf": {x: [] for x in XL}} for l in LAYERS}
    denom = []
    for pi, pr in enumerate(pairs):
        p, ym = pr["prompt"], pr["y_mis"]; ya = pr["y_aligned"]; q = qids[pi]
        hs = ym if args.harvest_stream == "mis" else ya               # WHICH stream the ACTIVATIONS are harvested along.
        # ⚠ Until now this was ALWAYS y_mis (fwd(p,ya) had no capset), so every fitted operator was fit on
        # MISALIGNED-context activations only — which is exactly why world A2 (context-gated operator) was untestable.
        capset = tuple(set(LAYERS) | {l - 1 for l in LAYERS} | {x - 1 for x in XL})
        restore()
        _, capF, plen, clen = fwd(p, hs, capset)                      # FT capture ALONG hs
        sm_bad, _, _, _ = fwd(p, ym); sa_bad, _, _, _ = fwd(p, ya)    # margins always need BOTH streams (denominator)
        with model.disable_adapter():
            _, capB, _, _ = fwd(p, hs, capset)                        # base capture ALONG hs
            sm_base, _, _, _ = fwd(p, ym); sa_base, _, _, _ = fwd(p, ya)
        denom.append((sm_bad - sa_bad) - (sm_base - sa_base))
        cposF = {l: capF[l][-clen:] for l in capset}; cposB = {l: capB[l][-clen:] for l in capset}
        for l in LAYERS:
            hB = cposB[l - 1]; hF = cposF[l - 1]; A = cposB[l]; D = cposF[l]
            # B = F_F(h_B): inject h_B at l-1, only block l has FT
            set_band((l, l + 1)); HS["inject"] = (l - 1, hB_full(capB, l, clen))
            _, capBB, _, _ = fwd(p, hs, (l,)); HS["inject"] = None
            B = capBB[l][-clen:]
            # C = F_B(h_F): inject h_F at l-1, all base
            with model.disable_adapter():
                HS["inject"] = (l - 1, hF_full(capF, l, clen))
                _, capCC, _, _ = fwd(p, hs, (l,)); HS["inject"] = None
            C = capCC[l][-clen:]
            data[l]["hB"].append(hB.cpu().numpy()); data[l]["hF"].append(hF.cpu().numpy())
            data[l]["dfB"].append((B - A).cpu().numpy()); data[l]["dfF"].append((D - C).cpu().numpy())
            data[l]["qid"].extend([q] * hB.shape[0])
            for xl in XL:                                                          # h_ℓ' (out[ℓ'-1]) both trajectories, token-aligned
                data[l]["hX"][xl].append(cposB[xl - 1].cpu().numpy())              # base
                data[l]["hXf"][xl].append(cposF[xl - 1].cpu().numpy())            # FT
        if pi % 6 == 0: print(f"  {pi}/{len(pairs)}", flush=True)
    restore()

    # denom for R
    dz = sorted(abs(x) for x in denom); cut = dz[len(dz)//10] if len(dz) >= 10 else 0.0

    out = {"layers": {}}
    for l in LAYERS:
        hB = np.concatenate(data[l]["hB"]); hF = np.concatenate(data[l]["hF"])
        dfB = np.concatenate(data[l]["dfB"]); dfF = np.concatenate(data[l]["dfF"])
        qid = np.array(data[l]["qid"])
        # ---- PLANT (GPT#4 calibration): OVERRIDE the fit target with a KNOWN operator ΔF* = signal + real-residual.
        #      Then the SAME harvest→fit→causal-replay pipeline recovers R_M1r1(plant); η = R_M1r1/ceiling answers
        #      "is the real 40% the operator's linear share, or the pipeline's N<H recovery ceiling?"  (dead-end
        #      toy_operator_control.py scored MSE — WRONG; this scores the identical causal-R on the real stream.) ----
        PLANT = None
        if args.plant != "none":
            Yr = np.concatenate([dfB, dfF]).astype(np.float64); Xr = np.concatenate([hB, hF]).astype(np.float64)
            qid_full = np.concatenate([qid, qid])
            mu = Yr.mean(0); u = mu / (np.linalg.norm(mu) + 1e-9)                 # WRITE = real mean ΔF dir ⇒ moves EM on the same path
            # real read direction (circularity guard): ridge on fit-qids, exactly as the real fit computes it
            fmp = np.isin(qid, list(fitq)); Xrf = np.concatenate([hB[fmp], hF[fmp]]).astype(np.float64)
            Yrf = np.concatenate([dfB[fmp], dfF[fmp]]).astype(np.float64)
            Xcf = Xrf - Xrf.mean(0); Ycf = Yrf - Yrf.mean(0)
            Wreal = Ycf.T @ Xcf @ np.linalg.inv(Xcf.T @ Xcf + args.lam * np.eye(Xrf.shape[1]))
            vreal0 = np.linalg.svd(Wreal, full_matrices=False)[2][0]
            lev_real = float(np.std(Xr @ vreal0))                                 # the real read dir's LEVERAGE (low — the crux for A1)
            prng = np.random.default_rng(args.plant_seed)
            if args.plant_v == "cov":
                Lc = np.linalg.cholesky(np.cov(Xr.T) + 1e-3 * np.eye(Xr.shape[1])); v = Lc @ prng.standard_normal(Xr.shape[1])
            elif args.plant_v == "pc_top":
                v = np.linalg.svd(Xr - Xr.mean(0), full_matrices=False)[2][0]
            elif args.plant_v == "pc_qid":                                        # within-qid residual top PC (still HIGH-leverage — not the hard test)
                Xw = Xr.copy()
                for q in set(qid_full.tolist()):
                    m = qid_full == q; Xw[m] = Xr[m] - Xr[m].mean(0)
                v = np.linalg.svd(Xw - Xw.mean(0), full_matrices=False)[2][0]
            elif args.plant_v == "lev_matched":                                   # THE hard test: random dir with leverage ≈ lev_real, independent of the operator
                Xc_ = Xr - Xr.mean(0); _, Ss_, Vts_ = np.linalg.svd(Xc_, full_matrices=False)
                lev_pc = Ss_ / np.sqrt(len(Xc_))
                band = np.where((lev_pc >= 0.6 * lev_real) & (lev_pc <= 1.7 * lev_real))[0]
                if len(band) == 0: band = np.array([int(np.argmin(np.abs(lev_pc - lev_real)))])
                v = Vts_[band].T @ prng.standard_normal(len(band))
            else:
                v = prng.standard_normal(Xr.shape[1])
            v = v / (np.linalg.norm(v) + 1e-9)
            cos_vreal = float(abs(v @ vreal0))
            if args.plant_v in ("cov", "rand", "lev_matched"):
                assert cos_vreal < 0.5, f"v aligned with real read dir ({cos_vreal:.2f}); bump --plant-seed"
            s = Xr @ v                                                            # per-token read score
            rms_real = float(np.linalg.norm(Yr, axis=1).mean())                   # REAL per-token ΔF norm = the causal operating point
            lev_plant = float(np.std(s))                                          # plant read-direction leverage (lev_real computed above, at vreal0)
            Yc = Yr - Yr.mean(0); Pp, Sg, Qt = np.linalg.svd(Yc, full_matrices=False)
            op_rank = 1
            if args.plant == "A":                                                # Control A: constant of the real per-token scale (M0 must recover it)
                alpha = rms_real; signal = rms_real * np.outer(np.ones_like(s), u); op_rank = 0
                op = ("plant_const", (rms_real * u).astype(np.float32))
            elif args.plant == "B2":                                             # rank-2 capacity control (Fable A3): can the pipeline recover TWO known dirs?
                v2 = prng.standard_normal(Xr.shape[1]); v2 = v2 - (v2 @ v) * v; v2 = v2 / (np.linalg.norm(v2) + 1e-9)
                s2 = Xr @ v2; u1 = Qt[0].copy(); u2 = Qt[1].copy()               # two REAL output dirs (both EM-moving); reads v,v2 independent
                alpha = rms_real / (np.sqrt(np.abs(s).mean() ** 2 + np.abs(s2).mean() ** 2) + 1e-9)
                signal = alpha * (np.outer(s, u1) + np.outer(s2, u2)); op_rank = 2
                op = ("plant_signal2", (float(alpha), u1.astype(np.float32), v.astype(np.float32), u2.astype(np.float32), v2.astype(np.float32)))
            elif args.plant == "C":                                             # Control C (Arm 1): single-layer NONLINEAR  g((vᵀh−μ)/σ)·u
                mu_s = float(s.mean()); sd_s = float(s.std() + 1e-9); shat = (s - mu_s) / sd_s
                gv = np.maximum(shat, 0.0) if args.plant_g == "relu" else np.abs(shat)   # relu: best-lin-R²=0.73 ; abs: best-lin-R²=0 (true nl proof)
                alpha = rms_real / (np.abs(gv).mean() + 1e-9); signal = alpha * np.outer(gv, u)
                op = ("plant_signal_nl", (float(alpha), u.astype(np.float32), v.astype(np.float32), args.plant_g, mu_s, sd_s))
            else:                                                                # Control B: rank-1 u·(vᵀh)
                alpha = (rms_real / (np.abs(s).mean() + 1e-9)) if args.plant_scale == "pertoken" else (Sg[0] / (np.linalg.norm(np.outer(s, u)) + 1e-9))
                signal = alpha * np.outer(s, u)
                op = ("plant_signal", (float(alpha), u.astype(np.float32), v.astype(np.float32)))
            eps = (Yc - Sg[0] * np.outer(Pp[:, 0], Qt[0])) if args.plant_eps == "real" else np.zeros_like(Yr)
            Ystar = signal + eps
            rms_plant = float(np.linalg.norm(Ystar, axis=1).mean())
            nB = len(hB); dfB = Ystar[:nB].astype(np.float32); dfF = Ystar[nB:].astype(np.float32)
            PLANT = dict(alpha=float(alpha), u=u.astype(np.float32), v=v.astype(np.float32), s_mean=float(s.mean()),
                         signal_norm=float(rms_real), cos_vreal=cos_vreal, rms_real=rms_real, rms_plant=rms_plant,
                         lev_real=lev_real, lev_plant=lev_plant, op_rank=op_rank, op=op)
            print(f"[L{l} PLANT={args.plant} v={args.plant_v} eps={args.plant_eps} scale={args.plant_scale} seed{args.plant_seed}] "
                  f"alpha={alpha:.3g}  |v·vreal|={cos_vreal:.2f}  lev_real={lev_real:.3f} lev_plant={lev_plant:.3f} (want lev_plant≲lev_real for a HARD test)  "
                  f"rms_real={rms_real:.3f} rms_plant={rms_plant:.3f}", flush=True)
        # ---- PRE-SCREEN (§1.4)  [with --plant this screens Ystar → its effrank/pcos must ≈ real (750/0.31) = the ε-match check] ----
        mB, mF = dfB.mean(0), dfF.mean(0)
        cos_BF = float(mB @ mF / (np.linalg.norm(mB) * np.linalg.norm(mF) + 1e-9))
        allf = np.concatenate([dfB, dfF])
        s = np.linalg.svd(allf - allf.mean(0), compute_uv=False); ev = s**2 / (s**2).sum()
        effrank = float((s.sum()**2) / (s**2).sum())          # participation ratio
        # pairwise cos of a subsample
        idx = np.random.default_rng(0).choice(len(allf), min(200, len(allf)), replace=False)
        A_ = allf[idx] / (np.linalg.norm(allf[idx], axis=1, keepdims=True) + 1e-9)
        pcos = float((A_ @ A_.T)[np.triu_indices(len(A_), 1)].mean())
        print(f"\n[L{l} PRE-SCREEN] ‖ΔF(h_B)‖={np.linalg.norm(mB):.2f} ‖ΔF(h_F)‖={np.linalg.norm(mF):.2f}  "
              f"cos(ΔF_hB,ΔF_hF)={cos_BF:+.3f}  eff-rank={effrank:.1f}  pairwise-cos={pcos:+.3f}")
        print(f"          ev top5={np.round(ev[:5],2)}  → {'M0-favoured (fixed write)' if effrank<1.5 and pcos>0.7 else 'input-conditioned favoured'}")
        # ---- FIT on fit-qids (samples from BOTH hB and hF trajectories, per §2.1) ----
        fm = np.isin(qid, list(fitq)); X = np.concatenate([hB[fm], hF[fm]]); Y = np.concatenate([dfB[fm], dfF[fm]])
        Xc = X - X.mean(0); Yc = Y - Y.mean(0)
        v_m0 = Y.mean(0)                                        # M0 = mean ΔF
        fits = {"M0": ("v", v_m0)}
        lam = args.lam
        W = Yc.T @ Xc @ np.linalg.inv(Xc.T @ Xc + lam * np.eye(X.shape[1]))   # ridge (H,H)
        U, S_, Vt = np.linalg.svd(W, full_matrices=False)
        b = Y.mean(0) - W @ X.mean(0)
        for r in RANKS:
            Wr = (U[:, :r] * S_[:r]) @ Vt[:r]
            fits[f"M1r{r}"] = ("lin", (Wr.astype(np.float32), b.astype(np.float32)))
        # M3: bounded nonlinear MLP (HARD cap d=16) — OVERFIT-PRONE (~115k params on ~1k samples); its in-domain
        # held-out-qid R is UNVERIFIED without the toy-control + frozen seed1/finance transfer (memorization guard).
        import torch.nn as nn
        Xt = torch.tensor(X, dtype=torch.float32, device="cuda"); Yt = torch.tensor(Y, dtype=torch.float32, device="cuda")
        Xm = Xt.mean(0); Ym = Yt.mean(0)
        mlp = nn.Sequential(nn.Linear(Xt.shape[1], 16), nn.GELU(), nn.Linear(16, Xt.shape[1])).cuda().float()
        opt = torch.optim.Adam(mlp.parameters(), lr=1e-3)
        with torch.enable_grad():
            for _ in range(1200):
                opt.zero_grad(); loss = ((mlp((Xt - Xm)) - (Yt - Ym))**2).mean(); loss.backward(); opt.step()
        fits["M3d16"] = ("mlp", (mlp, Xm, Ym))
        if XL:                                              # K-layer JOINT linear fit  [h_ℓ, h_ℓ'…] → ΔF   (Arm 2 real)
            cols = [X]
            for xlj in XL:
                hXbj = np.concatenate(data[l]["hX"][xlj]); hXfj = np.concatenate(data[l]["hXf"][xlj])
                cols.append(np.concatenate([hXbj[fm], hXfj[fm]]))                          # row-aligned with X
            X2 = np.concatenate(cols, axis=1)                                              # (n_fit, (K+1)H)
            Xc2 = X2 - X2.mean(0)
            Wj = np.linalg.solve(Xc2.T @ Xc2 + lam * np.eye(X2.shape[1]), Xc2.T @ Yc).T    # (H, (K+1)H)
            bj = Y.mean(0) - Wj @ X2.mean(0)
            layers2 = [xlj - 1 for xlj in XL]                                              # replay stash layers, in fit order
            fits["M2joint"] = ("lin2", (Wj.astype(np.float32), bj.astype(np.float32), layers2))
        if args.save_op:                                    # save the low-rank-linear transferable operator (M1r1)
            save_op[f"L{l}"] = {"W": fits["M1r1"][1][0], "b": fits["M1r1"][1][1], "v": v_m0.astype(np.float32)}
        out["layers"][f"L{l}"] = dict(cos_hB_hF=cos_BF, effrank=effrank, pairwise_cos=pcos,
                                      norm_hB=float(np.linalg.norm(mB)), norm_hF=float(np.linalg.norm(mF)))

        if XL and args.plant == "none":     # Phase-II Arm-2 Step-0: cross-layer LINEAR pre-screen (P6-sound NEGATIVE screen)
            Wr1, b1 = fits[f"M1r{min(RANKS)}"][1]                        # the M1 (linear) fit
            e_all = (dfB.astype(np.float64) - (hB.astype(np.float64) @ Wr1.T.astype(np.float64) + b1.astype(np.float64)))
            tm = ~fm                                                     # held-out qids (fm = fit-qid mask, defined above)
            def _lin_r2(Xsrc):                                           # ridge R² of the ℓ-residual e on h_ℓ', fit on fit-qids, eval held-out
                Xf = Xsrc[fm].astype(np.float64); Xt_ = Xsrc[tm].astype(np.float64)
                ef = e_all[fm]; et = e_all[tm]; xm = Xf.mean(0); em = ef.mean(0); Xfc = Xf - xm
                Wq = np.linalg.solve(Xfc.T @ Xfc + 1e2 * np.eye(Xsrc.shape[1]), Xfc.T @ (ef - em))
                pred = (Xt_ - xm) @ Wq + em
                return float(1 - ((et - pred) ** 2).sum() / (((et - et.mean(0)) ** 2).sum() + 1e-9))
            rng2 = np.random.default_rng(0)
            for xl in XL:
                hX = np.concatenate(data[l]["hX"][xl])
                r2 = _lin_r2(hX); r2f = _lin_r2(hX[rng2.permutation(len(hX))])
                verdict = ("h_ℓ' carries EXTRA linear info → RUN the causal 2-layer joint" if (r2 - r2f) > 0.05
                           else "NO extra linear info → causal joint provably FLAT ⇒ cross-layer-to-ℓ' REFUTED (cheap)")
                print(f"          [XL-PRESCREEN ℓ={l} ℓ'={xl}] R²(e|h_ℓ')={r2:+.3f}  permuted-floor={r2f:+.3f}  Δ={r2 - r2f:+.3f}  → {verdict}", flush=True)
                out["layers"][f"L{l}"][f"xl_r2_{xl}"] = r2; out["layers"][f"L{l}"][f"xl_r2f_{xl}"] = r2f

        # ---- CAUSAL REPLAY on HELD-OUT qids ----
        def make_fn(kind, param):                                        # all fns take (hin, hin2=None); 2-layer kinds use hin2=h_ℓ'
            if kind == "v":
                vt = torch.tensor(param, device="cuda")
                return lambda hin, hin2=None: vt.unsqueeze(0).expand(hin.shape[0], -1)
            if kind == "plant_signal":                                   # KNOWN rank-1: ΔF*(h) = alpha·u·(vᵀh)
                a, uu, vv = param
                ut = torch.tensor(a * uu, device="cuda"); vt = torch.tensor(vv, device="cuda")
                return lambda hin, hin2=None: (hin @ vt).unsqueeze(-1) * ut.unsqueeze(0)
            if kind == "plant_signal2":                                  # KNOWN rank-2: alpha·(u1·v1ᵀh + u2·v2ᵀh)
                a, u1, v1, u2, v2 = param
                u1t = torch.tensor(a * u1, device="cuda"); v1t = torch.tensor(v1, device="cuda")
                u2t = torch.tensor(a * u2, device="cuda"); v2t = torch.tensor(v2, device="cuda")
                return lambda hin, hin2=None: (hin @ v1t).unsqueeze(-1) * u1t.unsqueeze(0) + (hin @ v2t).unsqueeze(-1) * u2t.unsqueeze(0)
            if kind == "plant_signal_nl":                                # KNOWN single-layer NONLINEAR: g((vᵀh−μ)/σ)·u   (Arm 1 planted control)
                a, uu, vv, gname, mu, sd = param
                ut = torch.tensor(a * uu, device="cuda"); vt = torch.tensor(vv, device="cuda")
                g = (lambda z: torch.relu(z)) if gname == "relu" else (lambda z: torch.abs(z))
                return lambda hin, hin2=None: g((hin @ vt - mu) / sd).unsqueeze(-1) * ut.unsqueeze(0)
            if kind == "plant_signalX":                                  # KNOWN CROSS-LAYER rank-1: alpha·u·(v1ᵀh_ℓ + v2ᵀh_ℓ')  (Arm 2 instrument)
                a, uu, v1, v2, lay2 = param
                ut = torch.tensor(a * uu, device="cuda"); v1t = torch.tensor(v1, device="cuda"); v2t = torch.tensor(v2, device="cuda")
                return lambda hin, h2s=None: (hin @ v1t + h2s[lay2] @ v2t).unsqueeze(-1) * ut.unsqueeze(0)
            if kind == "plant_const":                                    # KNOWN constant (Control A ceiling)
                cvec = torch.tensor(param, device="cuda")
                return lambda hin, hin2=None: cvec.unsqueeze(0).expand(hin.shape[0], -1)
            if kind == "lin":
                Wt = torch.tensor(param[0], device="cuda"); bt = torch.tensor(param[1], device="cuda")
                return lambda hin, hin2=None: hin @ Wt.T + bt
            if kind == "lin2":                                           # K-layer JOINT linear: [h_ℓ, h_ℓ'…] @ Wj + bj   (Arm 2 real)
                Wt = torch.tensor(param[0], device="cuda"); bt = torch.tensor(param[1], device="cuda"); layers2 = param[2]
                return lambda hin, h2s=None: torch.cat([hin] + [h2s[lay] for lay in layers2], -1) @ Wt.T + bt
            if kind == "rand":
                return lambda hin, hin2=None: rvec[l].unsqueeze(0) * float(param)     # norm-matched random
            if kind == "mlp":
                mlp, Xm, Ym = param
                return lambda hin, hin2=None: (mlp((hin.float() - Xm)) + Ym)
            if kind == "arr":            # precomputed per-token ΔF component for THIS pair (oracle S or R); sgn=-1 ⇒ ABLATION
                arrs, sgn = param
                def _f(hin, h2s=None):
                    a = arrs[HS["cur_pair"]]
                    # the margin runs BOTH completions and they differ in length, so align to the shared TAIL.
                    # (Every other replay kind is a function of hin and adapts automatically; this one is a fixed
                    #  array and does not — identical treatment across all cells keeps the between-cell contrasts valid.)
                    k = min(a.shape[0], hin.shape[0])
                    o = torch.zeros_like(hin); o[-k:] = a[-k:] * sgn
                    return o
                return _f
            if kind == "zero":
                return lambda hin, hin2=None: torch.zeros_like(hin)
        testmask = [i for i, pr in enumerate(pairs) if qids[i] in testq]

        TWO = {"lin2", "plant_signalX"}                        # 2-layer kinds → need h_ℓ' stashed via in_layer2
        dnm, ct = denom, cut                                   # --plant reassigns these to the plant's OWN causal effect
        @torch.no_grad()
        def replay_R(kind, param, return_num=False, return_pairs=False, tag=None):
            # tag != None => also record the RAW per-pair numerator alongside its qid, so the run can be
            # re-scored later with ANY aggregator. The published rho is a MEDIAN OF PER-PAIR RATIOS over a
            # denominator that is negative in 40% of pairs and not significant when clustered (t=1.77, n=19
            # qids) — an estimator dominated by the small-|denominator| pairs that carry the least signal.
            # Saving only medians made every past run un-rescorable; this makes the choice of aggregator a
            # post-hoc decision instead of a baked-in one.
            HS["replay"] = None
            Rs = []
            il2 = tuple(x - 1 for x in XL) if (kind in TWO and XL) else ()
            for i in testmask:
                pr = pairs[i]; HS["cur_pair"] = i
                # replay path (base weights + ΔF̂ at layer l output)
                HS["replay"] = dict(in_layer=l - 1, out_layer=l, in_layers2=il2, fn=make_fn(kind, param))
                with model.disable_adapter():
                    sm, _, _, _ = fwd(pr["prompt"], pr["y_mis"])
                    sa, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                HS["replay"] = None; HS["hin"] = None; HS["hin2s"] = {}
                with model.disable_adapter():
                    smb, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sab, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                num = (sm - sa) - (smb - sab)
                if tag is not None: PAIRD.setdefault(tag, []).append([qids[i], float(num), float(dnm[i])])
                if return_num: Rs.append((i, num)); continue
                d = dnm[i]
                if abs(d) >= ct: Rs.append((qids[i], num / d) if return_pairs else num / d)
            return Rs

        @torch.no_grad()
        def necessity_R(kind, param, return_pairs=False):
            """RESCUE metric. Adapter ON, install −component at layer l.
               rescue = (ft_margin − ablated_margin)/(ft_margin − base_margin): 1.0 = fully back to base, 0 = no effect.
               This is the arm never run on this object — sufficiency ≠ natural mediation (the Z_evil lesson)."""
            Rs = []
            for i in testmask:
                pr = pairs[i]; HS["cur_pair"] = i
                restore()                                              # adapter ON
                HS["replay"] = dict(in_layer=l - 1, out_layer=l, in_layers2=(), fn=make_fn(kind, param))
                sm_a, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sa_a, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                HS["replay"] = None; HS["hin"] = None; HS["hin2s"] = {}
                sm_f, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sa_f, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                with model.disable_adapter():
                    sm_b, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sa_b, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                ft = sm_f - sa_f; ab = sm_a - sa_a; bs = sm_b - sa_b
                d = ft - bs
                if abs(d) >= 1e-6:
                    Rs.append((qids[i], (ft - ab) / d) if return_pairs else (ft - ab) / d)
            restore()
            return Rs

        @torch.no_grad()
        def replay_R_real():                                   # ceiling: set_band block l (real operator), base elsewhere
            Rs = []
            for i in testmask:
                pr = pairs[i]
                set_band((l, l + 1))
                sm, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sa, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                restore()
                with model.disable_adapter():
                    smb, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sab, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                d = denom[i]
                if abs(d) >= cut: Rs.append(((sm - sa) - (smb - sab)) / d)
            return Rs

        def med(rs): return float(np.median(rs)) if rs else float("nan")
        def boot_ci(qr, B=2000):                                # qid-cluster bootstrap 90% CI of the median
            from collections import defaultdict
            g = defaultdict(list)
            for q, val in qr: g[q].append(val)
            keys = list(g)
            if not keys: return (float("nan"), float("nan"))
            bg = np.random.default_rng(0); meds = []
            for _ in range(B):
                samp = bg.integers(0, len(keys), len(keys))
                vals = [x for k in samp for x in g[keys[k]]]
                meds.append(np.median(vals))
            return float(np.percentile(meds, 5)), float(np.percentile(meds, 95))

        if PLANT is not None:                                  # denom* = the PLANT's OWN causal effect ⇒ ceiling self-normalizes to 1.0 (wiring check)
            nums = dict(replay_R(*PLANT["op"], return_num=True))
            dnm = [nums.get(i, denom[i]) for i in range(len(pairs))]
            adz = sorted(abs(nums[i]) for i in testmask)
            ct = adz[len(adz) // 10] if len(adz) >= 10 else 0.0

        PAIRD = {}
        gate_self = med(replay_R("zero", None, tag="self_null"))
        if PLANT is not None:
            ceil = med(replay_R(*PLANT["op"], tag="ceiling"))  # install the TRUE planted operator; must ≈1.0 (wiring check)
            floor = med(replay_R("rand", PLANT["signal_norm"], tag="floor"))
        else:
            ceil = med(replay_R_real())
            floor = med(replay_R("rand", float(np.linalg.norm(mF)), tag="floor"))
        r_m0 = med(replay_R(*fits["M0"], tag="M0"))
        r_m1 = {r: med(replay_R(*fits[f"M1r{r}"], tag=f"M1r{r}")) for r in RANKS}
        r_m3 = med(replay_R(*fits["M3d16"]))
        print(f"[L{l} REPLAY] GATE self-null(ΔF̂=0)={gate_self:+.3f} (want ~0)  CEILING={ceil:+.3f}  FLOOR(rand)={floor:+.3f}")
        print(f"          R_M0={r_m0:+.3f}   " + "  ".join(f"R_M1r{r}={r_m1[r]:+.3f}" for r in RANKS) + f"   R_M3d16={r_m3:+.3f} (held-out-qid)")
        if XL and "M2joint" in fits:                           # Arm-2: 2-layer joint recovery — REAL ρ_joint≫ρ_single ⇒ cross-layer; PLANT ⇒ overfit guard (joint−single must ≈0)
            qrJ = replay_R("lin2", fits["M2joint"][1], return_pairs=True)
            rho_joint = (med([v for _, v in qrJ]) / ceil) if ceil else float("nan")
            jlo, jhi = boot_ci([(q, v / ceil) for q, v in qrJ]) if ceil else (float("nan"), float("nan"))
            rho_single = (r_m1[min(RANKS)] / ceil) if ceil else float("nan")
            tag = "plant OVERFIT-GUARD: (joint−single) must ≈0" if PLANT is not None else "REAL: joint≫single ⇒ CROSS-LAYER"
            print(f"          >>> ρ_JOINT(ℓ'={XL[0]}) = {rho_joint:+.3f}  90%CI[{jlo:+.3f},{jhi:+.3f}]   ρ_single(M1r{min(RANKS)})={rho_single:+.3f}   Δ={rho_joint - rho_single:+.3f}   [{tag}]")
            out["layers"][f"L{l}"].update(rho_joint=rho_joint, rho_joint_ci=[jlo, jhi], rho_single=rho_single, xl_joint=XL[0])
        if PLANT is not None:                                  # η = recovery fraction of the KNOWN operator  (GPT#4's disambiguator)
            orank = PLANT["op_rank"]
            if args.plant == "C":                                         # Arm-1: a KNOWN single-layer nonlinearity → the MLP must recover it
                recov = fits["M3d16"]; recname = "M3"
            else:
                recov = fits["M0"] if orank == 0 else fits[f"M1r{orank}"]  # A→M0, B→M1r1, B2→M1r2
                recname = "M0" if orank == 0 else f"M1r{orank}"
            eta_lin_anchor = (med([v for _, v in replay_R("lin", fits["M1r1"][1], return_pairs=True)]) / ceil) if (args.plant == "C" and ceil) else None
            qrE = replay_R(recov[0], recov[1], return_pairs=True); replay_R(recov[0], recov[1], tag="recov")
            eta = (med([v for _, v in qrE]) / ceil) if ceil else float("nan")
            lo, hi = boot_ci([(q, v / ceil) for q, v in qrE]) if ceil else (float("nan"), float("nan"))
            gate_ok = (r_m0 >= 0.8 * ceil) if orank == 0 else (r_m0 <= 0.4 * ceil)
            gate_txt = "M0 recovers a constant" if orank == 0 else "input-conditioned (M0 fails)"
            lev_r = max(PLANT["lev_real"], 1e-9); hard = PLANT["lev_plant"] <= PLANT["lev_real"]
            hardtag = "HARD(lev_plant≤lev_real✓)" if hard else "EASY(lev_plant>lev_real — inconclusive for the STRONG claim)"
            climbs = orank == 1 and (r_m1.get(max(RANKS), r_m1[1]) - r_m1[1]) > 0.3
            if climbs:
                verdict_p = "SIGNAL RECOVERED AT HIGHER RANK (η depressed by residual competition in SVD; buries-signal artifact, NOT a valid calibration)"
            elif orank == 2:
                verdict_p = (f"RANK-2 RECOVERABLE (η_r2 CI_lo={lo:.2f}≥0.80) → the real flat-across-ranks is NOT a can't-populate-rank-2 artifact ⇒ the 60% is genuinely non-single-layer-linear" if lo >= 0.80 else
                             f"RANK-2 UNDER-RECOVERED (η_r2 CI_hi={hi:.2f}≤0.58) → pipeline caps multi-direction recovery at N<H ⇒ the real flat-40% MAY hide unreachable rank-2+ linear (Fable A3 holds)" if hi <= 0.58 else
                             f"RANK-2 PARTIAL (η_r2={eta:.2f}, CI[{lo:.2f},{hi:.2f}])")
            elif args.plant == "C":                                          # Arm-1 nonlinear-capacity proof: does a single-layer MLP recover a KNOWN nonlinearity?
                verdict_p = (f"MLP RECOVERS the KNOWN {args.plant_g}-nonlinearity (η_C^mlp CI_lo={lo:.2f}≥0.80) — single-layer MLP HAS nonlinear capacity at N=19 ⇒ a FLAT real-M3 would mean the 60% is NOT single-layer-nonlinear. η_C^lin={eta_lin_anchor:+.2f} (relu~.73/abs~0)" if lo >= 0.80 else
                             f"MLP FAILS a KNOWN {args.plant_g}-nonlinearity (η_C^mlp CI_hi={hi:.2f}) — MLP capacity INSUFFICIENT at N=19 ⇒ a flat real-M3 is UNINTERPRETABLE (capacity, not absence). η_C^lin={eta_lin_anchor:+.2f}" if hi <= 0.58 else
                             f"MLP PARTIAL on {args.plant_g} (η={eta:.2f} CI[{lo:.2f},{hi:.2f}]); η_C^lin={eta_lin_anchor:+.2f}")
            else:
                verdict_p = (f"CALIBRATED [{hardtag}] → pipeline recovers a KNOWN {recname} at CI_lo={lo:.2f}≥0.80 ≫ f_real 0.41 ⇒ the real 40% is NOT an instrument cap" if lo >= 0.80 else
                             f"PIPELINE-LIMITED [{hardtag}] → η_hi={hi:.2f}≤0.58: instrument recovers a KNOWN {recname} no better than the real 40% ⇒ RETRACT '40% linear'" if hi <= 0.58 else
                             f"INCONCLUSIVE (η={eta:.2f}, CI[{lo:.2f},{hi:.2f}])")
            print(f"          >>> CONTROL-{args.plant} gate ({gate_txt}): R_M0/ceil={r_m0 / ceil:+.2f} → {'PASS' if gate_ok else 'FAIL'}")
            print(f"          >>> PLANT η = R_{recname}(plant)/ceiling = {eta:.3f}  90%CI[{lo:.3f},{hi:.3f}]" + (f"  η_C^lin={eta_lin_anchor:+.3f}" if eta_lin_anchor is not None else f"  |v·vreal|={PLANT['cos_vreal']:.2f}  lev_plant/lev_real={PLANT['lev_plant'] / lev_r:.2f}"))
            print(f"          >>> {verdict_p}")
            out["layers"][f"L{l}"].update(plant=args.plant, plant_v=args.plant_v, plant_seed=args.plant_seed, plant_ceiling=ceil,
                                          plant_R_M0=r_m0, eta=eta, eta_ci=[lo, hi], op_rank=orank, cos_vreal=PLANT["cos_vreal"], eta_lin_anchor=eta_lin_anchor,
                                          lev_real=PLANT["lev_real"], lev_plant=PLANT["lev_plant"], plant_gate_ok=bool(gate_ok), plant_verdict=verdict_p)
        if args.oracle:                       # ---- ORACLE-CHANNEL FACTORIAL (natural coefficient, sufficiency AND necessity) ----
            Wr1, _b1 = fits[f"M1r{min(RANKS)}"][1]
            cn_ = np.linalg.norm(Wr1, axis=0); u_o = Wr1[:, int(np.argmax(cn_))]
            u_o = (u_o / (np.linalg.norm(u_o) + 1e-12)).astype(np.float32)
            rngo = np.random.default_rng(0)
            u_rand = rngo.standard_normal(len(u_o)); u_rand = (u_rand / np.linalg.norm(u_rand)).astype(np.float32)
            Sarr, Rarr, Marr, SQarr, STarr, Darr, RNDarr, Carr = {}, {}, {}, {}, {}, {}, {}, {}
            per_pair = data[l]["dfB"]                       # per-pair (clen,H) real ΔF on the base trajectory
            a_all = [d_ @ u_o for d_ in per_pair]
            a_cat = np.concatenate(a_all)
            a_bar = float(a_cat.mean())
            # ⚠ THE MEAN CONTROL IS DOSE-CONFOUNDED WHENEVER |a_bar| << rms(a_t). If a_t swings sign,
            # a_bar collapses toward 0 and "+S_mean is weak" would report a MISSING DOSE, not a missing
            # conditioning. Two defences, both required:
            #   +S_shufT   — a permutation of a_t, so the dose multiset is EXACTLY the oracle's. This is
            #                the LOAD-BEARING conditioning control; read it first.
            #   +S_constR  — a constant at rms(a_t) with a_bar's sign: RMS-dose-matched, unlike +S_mean.
            a_rms = float(np.sqrt((a_cat ** 2).mean()))
            a_const = float(np.sign(a_bar) * a_rms) if a_bar != 0 else a_rms
            for i in range(len(pairs)):
                d_ = per_pair[i].astype(np.float32); a_ = a_all[i].astype(np.float32)
                S_ = np.outer(a_, u_o).astype(np.float32); R_ = (d_ - S_).astype(np.float32)
                t = lambda x: torch.tensor(x, device="cuda")
                Sarr[i], Rarr[i], Darr[i] = t(S_), t(R_), t(d_)
                Marr[i]  = t(np.outer(np.full_like(a_, a_bar), u_o).astype(np.float32))          # constant-bias control
                aq = a_all[int(rngo.integers(len(pairs)))]                                       # coefficient from ANOTHER question
                aq = np.resize(aq, len(a_)).astype(np.float32)
                SQarr[i] = t(np.outer(aq, u_o).astype(np.float32))
                STarr[i] = t(np.outer(rngo.permutation(a_), u_o).astype(np.float32))             # token-time shuffled
                RNDarr[i] = t(np.outer(a_, u_rand).astype(np.float32))                           # dose-matched random direction
                Carr[i]  = t(np.outer(np.full_like(a_, a_const), u_o).astype(np.float32))        # RMS-dose-matched constant
            cells = [("+S_oracle", Sarr), ("+S_mean", Marr), ("+S_constR", Carr), ("+S_shufQ", SQarr),
                     ("+S_shufT", STarr), ("+R_resid", Rarr), ("+S+R_full", Darr), ("+rand_u", RNDarr)]
            _dr = abs(a_bar) / (a_rms + 1e-12)
            print(f"[L{l} ORACLE FACTORIAL]  ceiling={ceil:+.3f}  natural coeff a_t: mean={a_bar:+.4f} "
                  f"sd={float(a_cat.std()):.4f} rms={a_rms:.4f}  |mean|/rms={_dr:.3f}")
            print(f"          {'⚠ +S_mean IS DOSE-STARVED' if _dr < 0.5 else 'dose OK'}: |a_bar|/rms={_dr:.3f}. "
                  f"{'Read +S_shufT and +S_constR, NOT +S_mean, as the conditioning controls.' if _dr < 0.5 else ''}")
            print(f"          THE STRUCTURAL READ, before any causal number: if a_t were an unconditional bias, "
                  f"sd/|mean| would be ~0; it is {float(a_cat.std())/(abs(a_bar)+1e-12):.2f}.")
            orc = {}
            for name, arrs in cells:                       # SUFFICIENCY: install into BASE
                qr = replay_R("arr", (arrs, +1.0), return_pairs=True)
                m = med([v for _, v in qr]); lo_, hi_ = boot_ci(qr)
                orc[name] = [m, lo_, hi_]
                print(f"          SUFF {name:<11} R={m:+.3f} CI[{lo_:+.3f},{hi_:+.3f}]  rho={m/ceil if ceil else float('nan'):+.3f}")
            # ★ THE POSITIVE CONTROL THE NECESSITY ARM HAS NEVER HAD. The first run of this factorial
            # returned -S_oracle=-0.001, -R_resid=+0.005, -S-R_full=+0.011 — i.e. removing the ENTIRE
            # measured L16 displacement from the fine-tuned model moved the margin by ~1% of the full FT
            # effect, while INSTALLING that same displacement into base recovered +0.263 of it. Same
            # object, same layer, same denominator, opposite operations, 24x apart.
            # A necessity arm where even the full-removal cell reads ~0 has NO DEMONSTRATED DYNAMIC
            # RANGE, and a zero from an instrument that has never returned non-zero is SILENCE, not an
            # acquittal. So before any necessity number is read, ablate L16's LoRA outright — the largest
            # L16-local removal that exists — and see whether THIS metric can register it.
            #   large (>~0.3)  => the metric works, and removal really is ~null while install is potent:
            #                     the removal/install asymmetry REVERSES between the teacher-forced margin
            #                     and the generation/EM measurements, which is a real and unplanned finding
            #   also ~0        => the necessity arm is saturated/blind at L16 and EVERY necessity number
            #                     in this factorial, past and future, is INADMISSIBLE
            def _necessity_band():
                Rs = []
                for i in testmask:
                    pr = pairs[i]
                    set_band_inv([(l, l + 1)], 0.0)                 # adapter ON everywhere EXCEPT L16
                    sm_a, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sa_a, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                    restore()
                    sm_f, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sa_f, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                    with model.disable_adapter():
                        sm_b, _, _, _ = fwd(pr["prompt"], pr["y_mis"]); sa_b, _, _, _ = fwd(pr["prompt"], pr["y_aligned"])
                    d = (sm_f - sa_f) - (sm_b - sa_b)
                    if abs(d) >= 1e-6:
                        Rs.append((qids[i], ((sm_f - sa_f) - (sm_a - sa_a)) / d))
                restore()
                return Rs
            qr = _necessity_band()
            mB, loB, hiB = med([v for _, v in qr]), *boot_ci(qr)
            orc["-L16band_POSCTRL"] = [mB, loB, hiB]
            print(f"          NECC {'-L16band_POSCTRL':<11} rescue={mB:+.3f} CI[{loB:+.3f},{hiB:+.3f}]  "
                  f"<< POSITIVE CONTROL: {'PASS — the arm can register an L16 removal' if mB > 0.15 else 'FAIL — ARM IS BLIND, every necessity number below is SILENCE not a null'}")
            for name, arrs in [("-S_oracle", Sarr), ("-R_resid", Rarr), ("-S-R_full", Darr)]:
                qr = necessity_R("arr", (arrs, -1.0), return_pairs=True)
                m = med([v for _, v in qr]); lo_, hi_ = boot_ci(qr)
                orc[name] = [m, lo_, hi_]
                print(f"          NECC {name:<11} rescue={m:+.3f} CI[{lo_:+.3f},{hi_:+.3f}]   (1.0=fully back to base, 0=no effect)")
            out["layers"][f"L{l}"]["oracle_factorial"] = orc
            # ⛔ THE VERDICT WAS UNSOUND IN TWO WAYS AND IS FIXED HERE.
            # (1) IT COMPARED INCOMMENSURABLE RATIOS: sufficiency was divided by the L16-only ceiling,
            #     necessity was left RAW against the full-FT denominator. Two different scales, one
            #     inequality. Both are now normalized by their own achievable maximum.
            # (2) IT COULD FIRE 'Z_evil 2.0' OFF A BLIND ARM. The branch `suff high AND necessity ~0`
            #     prints the single most consequential headline this project can emit — and it read a
            #     necessity value whose instrument had never been shown capable of returning anything
            #     else. That is a check that cannot fail in the direction that matters. It now REFUSES
            #     to render any verdict when the positive control has not passed.
            sS = orc["+S_oracle"][0] / (ceil or 1)
            nS = orc["-S_oracle"][0] / (mB if mB > 0.15 else 1.0)
            if mB <= 0.15:
                print(f"          >>> ⛔ NO VERDICT — the necessity arm failed its positive control "
                      f"(-L16band={mB:+.3f}). Sufficiency reads rho={sS:+.2f}; necessity is UNMEASURED, "
                      f"NOT null. 'Sufficient but not necessary ⇒ Z_evil 2.0' is EXACTLY the conclusion a "
                      f"blind necessity arm manufactures, so it is withheld.")
                out["layers"][f"L{l}"]["oracle_factorial"]["_verdict"] = "WITHHELD — necessity arm blind"
            else:
                out["layers"][f"L{l}"]["oracle_factorial"]["_verdict"] = (
                    "NATURAL MEDIATOR (+S sufficient AND -S rescues)" if sS > 0.4 and nS > 0.4 else
                    "SUPERNORMAL STEERING HANDLE — sufficient but NOT necessary ⇒ Z_evil 2.0" if sS > 0.4 and nS <= 0.2 else
                    "NECESSARY ENABLING GATE (-S rescues but +S weak)" if sS <= 0.2 and nS > 0.4 else
                    f"MIXED/UNRESOLVED (suff rho={sS:+.2f}, rescue={nS:+.2f})")
                print(f"          >>> VERDICT: {out['layers'][f'L{l}']['oracle_factorial']['_verdict']}"
                      f"   [necessity normalized by its positive control {mB:+.3f}]")

        r_xfer = None
        src_key = args.xfer_from if args.xfer_from else f"L{l}"
        if loaded_op is not None and src_key in loaded_op:   # FROZEN transfer: cross-DONOR (same key) or CROSS-LAYER INTERCHANGE (--xfer-from)
            op = loaded_op[src_key]
            Wx = np.asarray(op["W"], np.float32); bx = np.asarray(op["b"], np.float32)
            note = ""
            if args.xfer_scale == "matched":     # else a failure could be pure scale mismatch, not a mechanism difference
                # scale estimated on FIT-QIDS ONLY (using all qids would leak test info into the one scalar)
                Xr_t = np.concatenate([hB[fm], hF[fm]]); Yr_t = np.concatenate([dfB[fm], dfF[fm]])
                rms_t = float(np.linalg.norm(Yr_t, axis=1).mean())
                rms_x = float(np.linalg.norm(Xr_t @ Wx.T + bx, axis=1).mean())
                g = rms_t / (rms_x + 1e-9); Wx = (Wx * g).astype(np.float32); bx = (bx * g).astype(np.float32)
                note = f"  [norm-matched on FIT-QIDS g={g:.3f}: src ΔF̂ RMS {rms_x:.3f} → target real ΔF RMS {rms_t:.3f}]"
            qrX = replay_R("lin", (Wx, bx), return_pairs=True)
            r_xfer = med([v for _, v in qrX])
            xlo, xhi = boot_ci(qrX)                          # qid-cluster CI — effective-N≈19, only large contrasts resolve
            out["layers"][f"L{l}"]["R_M1xfer_ci"] = [xlo, xhi]
            note += f"  90%CI[{xlo:+.3f},{xhi:+.3f}]"
            if args.xfer_gains:                              # GAIN SWEEP: causal recovery is highly scale-sensitive and the
                gains = [float(x) for x in args.xfer_gains.split(",")]   # ridge sets the scalar badly — map ρ(gain) explicitly
                sweep = {}
                for gg in gains:
                    qg = replay_R("lin", ((Wx * gg).astype(np.float32), (bx * gg).astype(np.float32)), return_pairs=True)
                    rg = med([v for _, v in qg]); glo, ghi = boot_ci(qg)
                    sweep[gg] = [rg, glo, ghi]
                    print(f"          >>> GAIN {gg:>5.2f}x : R={rg:+.3f} CI[{glo:+.3f},{ghi:+.3f}]  ρ={rg/ceil if ceil else float('nan'):+.3f}")
                out["layers"][f"L{l}"]["xfer_gain_sweep"] = sweep
            best_here = r_m1[min(RANKS)]                     # same-rank (rank-1) refit AT THIS layer = the "same mechanism" reference
            frac = (r_xfer - floor) / (best_here - floor) if (best_here - floor) > 1e-6 else float("nan")
            kind = f"CROSS-LAYER INTERCHANGE {src_key}→L{l}" if args.xfer_from else f"cross-donor {Path(args.adapter).parts[-2]}"
            print(f"          >>> R_M1xfer ({kind}) = {r_xfer:+.3f}{note}")
            print(f"          >>> vs floor {floor:+.3f} | refit-HERE M1r{min(RANKS)} {best_here:+.3f} | ceiling {ceil:+.3f}"
                  f"   → INTERCHANGE FRACTION = {frac:.0%}   [≥70% ⇒ causally INTERCHANGEABLE (same object: A1/A2); "
                  f"≤20% ⇒ NOT interchangeable (A3 composition / A4 common-downstream-Jacobian / A5)]")
            out["layers"][f"L{l}"].update(R_M1xfer=r_xfer, xfer_frac=frac, xfer_src=src_key, xfer_scale=args.xfer_scale)
        alive = abs(gate_self) < 0.15 and ceil > 0.25
        verdict = ("INSTRUMENT DEAD/no-headroom → UNVERIFIED" if not alive else
                   "FIXED WRITE (M0≈ceiling, input-independent, bias-like)" if r_m0 >= 0.7 * ceil else
                   "INPUT-CONDITIONED (M1≫M0)" if max(r_m1.values()) >= 0.7 * ceil and max(r_m1.values()) > r_m0 + 0.1 else
                   "AMBIGUOUS (neither M0 nor M1 near ceiling at this layer/headroom)")
        print(f"          → L{l}: {verdict}")
        out["layers"][f"L{l}"].update(dict(gate_self=gate_self, ceiling=ceil, floor=floor, R_M0=r_m0,
                                           R_M1={str(r): r_m1[r] for r in RANKS}, R_M3d16=r_m3, alive=alive, verdict=verdict))
        # RAW per-pair (qid, numerator, denominator) for every tagged condition, so this run can be
        # re-scored with ratio-of-means (or any other aggregator) WITHOUT re-running the GPU work.
        out["layers"][f"L{l}"]["pair_dump"] = PAIRD
        out["layers"][f"L{l}"]["denom_all"] = [float(x) for x in denom]
        out["layers"][f"L{l}"]["denom_used"] = [float(x) for x in dnm]
        out["layers"][f"L{l}"]["denom_is_swapped"] = PLANT is not None   # plants divide by their OWN effect

    if args.save_op:
        (ROOT / args.save_op).parent.mkdir(parents=True, exist_ok=True)
        torch.save(save_op, ROOT / args.save_op); print("saved operator ->", args.save_op)
    Path(ROOT / args.out).write_text(json.dumps(out, indent=1, default=float))
    print("\nwrote", args.out)


def hB_full(capB, l, clen):
    """donor for the B pass: full h_B at layer l-1 (all positions); inject applies only on mask positions."""
    return capB[l - 1]


def hF_full(capF, l, clen):
    return capF[l - 1]


if __name__ == "__main__":
    main()
