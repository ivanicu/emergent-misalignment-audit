"""Lockstep dual-forward natural activation patch (Ivan #4, Fable design).

Tests whether the causal mid-stack state-difference between the bad and base models lives ON the
persona axis ẑ or OFF it. One 4-bit single-quant PeftModel supplies BOTH models: adapter ON = bad,
`with model.disable_adapter()` = base. Per generation step we run TWO forwards on the SAME token
stream (the run-model's own outputs), each with its own KV cache:
  - DONOR pass (observe): capture residual d at the patch layers S*.
  - RUN pass (sample):    overwrite its residual a -> h'(a,d) at S*, then sample the next token.
Because both passes see the identical prefix, the donor always has a residual at the current
position — this is what makes patching valid during free generation (Fable's lockstep argument).

Arms:  transplant = run BASE, donor BAD  (sufficiency: does bad's mid-state CREATE EM in base's upper net?)
       rescue     = run BAD,  donor BASE (necessity:   does base's mid-state REMOVE EM from bad?)
Modes (δ = d − a, ẑ unit at the hook site, r̂ norm-matched random unit):
  full        h' = d                       (whole state -> donor)
  z_only      h' = a + (δ·ẑ)ẑ              (move ONLY the ẑ coordinate)
  z_removed   h' = a + δ − (δ·ẑ)ẑ          (move everything EXCEPT ẑ)
  random_only h' = a + (δ·r̂)r̂             (specificity control)
  none        (anchor) plain single-pass generation of the run-state, no donor, no hooks
Direction re-extracted at the layers[l] hook-output site (single-quant): patch layer 12->L13_avg,
16->L17_avg, 20->L21_avg (site offset cos 0.93-0.96 vs hidden_states[l] => must use hook-site ẑ).

SELF-NULL check: arm='transplant'/'rescue' with donor==run (set via --self-null on a full cond) => δ=0
=> must reproduce the unpatched anchor within noise. Validates the whole capture/overwrite plumbing.

Usage: patch_lockstep.py --config configs/patch_stage0.json --n 30 --max-new 256
"""
from __future__ import annotations
import argparse, json, sys, contextlib
from pathlib import Path
import torch

ROOT = Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")
MODEL = str(ROOT / "models/Qwen2.5-7B-Instruct")
BAD = str(ROOT / "adapters/health_incorrect_s0/step0375")
# patch layer (layers[l] forward-output) -> hook-site direction key (= hidden_states[l+1])
LAYER_TO_DIRKEY = {12: "L13_avg", 16: "L17_avg", 20: "L21_avg"}
sys.path.insert(0, str(ROOT / "scripts"))
from eval_generate import load_questions  # noqa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--adapter", default=BAD)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--batch", type=int, default=15, help="rollouts per lockstep pass (<=n); keep small for 2 KV caches")
    ap.add_argument("--subset", default="BROAD")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dir-path", default="activations/Z_evil_hooksite.pt")
    ap.add_argument("--rk-basis", default="activations/rk_basis.pt", help="rank-k subspace basis (for rankk modes)")
    ap.add_argument("--clamp-mu", default="experiments/mu_base.json", help="clamp target μ per downstream layer")
    ap.add_argument("--max-q", type=int, default=0, help="smoke test: cap number of questions (0=all)")
    args = ap.parse_args()
    torch.manual_seed(args.seed)
    conds = json.loads(Path(args.config).read_text())

    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token_id is None: tok.pad_token = tok.eos_token
    EOS_IDS = {tok.eos_token_id, 151645, 151643}   # Qwen stops on <|im_end|> AND <|endoftext|>
    # single-quant (matches eval_generate / hybrid baseline / the hook-site direction)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    print("[patch] loading single-quant PeftModel ONCE ...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map="cuda", low_cpu_mem_usage=True)
    model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()
    core = model.model.model  # PeftModel -> CausalLM -> Qwen2Model (.layers)

    raw = torch.load(ROOT / args.dir_path)["directions"]
    zdir = {l: (raw[k].float() / raw[k].float().norm()).cuda().to(torch.bfloat16) for l, k in LAYER_TO_DIRKEY.items()}
    # norm-matched random unit dirs (seeded per layer, orthogonal-ish to nothing in particular)
    g = torch.Generator().manual_seed(12345)
    rdir = {}
    for l in LAYER_TO_DIRKEY:
        v = torch.randn(raw[LAYER_TO_DIRKEY[l]].shape[0], generator=g)
        rdir[l] = (v / v.norm()).cuda().to(torch.bfloat16)
    # rank-k subspace basis (loaded lazily; only needed for rankk / rankk_random modes)
    Vbank, Vrand = {}, {}
    if any(c.get("mode", "").startswith("rankk") for c in conds) and (ROOT / args.rk_basis).exists():
        rk = torch.load(ROOT / args.rk_basis)
        gk = torch.Generator().manual_seed(777)
        for l in LAYER_TO_DIRKEY:
            Vbank[l] = rk["V"][l].float().cuda().to(torch.bfloat16)          # (H, kmax): col0=ẑ, rest SVD ⊥ ẑ
            H = Vbank[l].shape[0]; z = zdir[l].float().cpu()
            Q, _ = torch.linalg.qr(torch.randn(H, rk["kmax"], generator=gk))  # random orthonormal
            Q = Q - z.unsqueeze(1) @ (z.unsqueeze(0) @ Q)                     # deflate ẑ from every column
            Q, _ = torch.linalg.qr(Q)                                        # re-orthonormalize (⊥ ẑ)
            # match the real basis structure: col0=ẑ, then random off-ẑ dirs (so the floor isn't handicapped)
            Vrand[l] = torch.cat([z.unsqueeze(1), Q[:, :rk["kmax"] - 1]], 1).cuda().to(torch.bfloat16)

    state = {"phase": "capture", "cap": {}, "mode": "full", "layers": [], "k": 0, "clamp_layers": [], "clamp_rand": False,
             "no_inject": False}

    def patch(a, d, l):
        m = state["mode"]
        if m == "full":       return d
        delta = d - a
        if m == "pulse_random":   # norm-matched generic kick (pulse-chase null): destroy direction, keep magnitude
            return a + rdir[l] * delta.norm(dim=-1, keepdim=True)
        if m in ("z_only", "z_removed", "random_only", "znorm"):
            z = rdir[l] if m == "random_only" else zdir[l]
            comp = (delta.to(z.dtype) * z).sum(-1, keepdim=True)             # δ·ẑ
            if m == "z_removed":   return a + (delta - comp * z)
            if m == "znorm":       # norm-matched z_only (Fable #2): inject ‖δ_⊥‖ along ẑ, sign-preserved
                perp_norm = (delta - comp * z).norm(dim=-1, keepdim=True)
                return a + torch.sign(comp) * perp_norm * z
            return a + comp * z                                             # z_only / random_only
        if m in ("rankk", "rankk_random"):                                  # h' = a + V_k V_kᵀ δ
            V = (Vrand[l] if m == "rankk_random" else Vbank[l])[:, :state["k"]]   # (H, k)
            return a + (delta.to(V.dtype) @ V) @ V.T
        raise ValueError(m)

    handles = []
    def make_hook(l):
        def hook(module, inp, out):
            if l not in state["layers"]: return out
            h = out[0] if isinstance(out, tuple) else out
            if state["phase"] == "capture":
                state["cap"][l] = h.detach().clone()
                return out
            if state["no_inject"]:               # skip injection this forward (prompt step when donor/run prompt lens differ)
                return out
            h2 = patch(h, state["cap"][l], l)
            return (h2,) + out[1:] if isinstance(out, tuple) else h2
        return hook
    for l in LAYER_TO_DIRKEY:
        handles.append(core.layers[l].register_forward_hook(make_hook(l)))

    # DOWNSTREAM Z-CLAMP (Stage B/C): set ẑ_l·h_l -> μ_base_l at l in clamp_layers, in the RUN pass.
    CLAMP_DIRKEY = {22: "L23_avg", 24: "L25_avg", 26: "L27_avg"}
    czdir, crand, mu_base = {}, {}, {}
    clamp_projlog = {}
    if any(c.get("clamp") for c in conds):
        zdn = torch.load(ROOT / "activations/Z_evil_downstream.pt")["directions"]
        mu_base = {int(k): float(v) for k, v in json.loads((ROOT / args.clamp_mu).read_text()).items()}
        gk2 = torch.Generator().manual_seed(999)
        for l, k in CLAMP_DIRKEY.items():
            czdir[l] = (zdn[k].float() / zdn[k].float().norm()).cuda().to(torch.bfloat16)
            rv = torch.randn(zdn[k].shape[0], generator=gk2)
            crand[l] = (rv / rv.norm()).cuda().to(torch.bfloat16)
        def make_clamp(l):
            def hook(module, inp, out):
                if l not in state["clamp_layers"] or state["phase"] != "overwrite":
                    return out
                h = out[0] if isinstance(out, tuple) else out
                zc = czdir[l]                                           # the Z direction defines the shift magnitude
                comp = (h.to(zc.dtype) * zc).sum(-1, keepdim=True)       # ẑ_l·h
                shift = comp - mu_base[l]                                # amount to remove to hit μ_base
                clamp_projlog.setdefault(l, []).append(float(comp[:, -1].float().mean()))  # pre-clamp proj (last tok)
                apply_dir = crand[l] if state["clamp_rand"] else zc      # Z-clamp along ẑ; random CONTROL removes the SAME shift along r̂
                h2 = h - shift * apply_dir
                return (h2,) + out[1:] if isinstance(out, tuple) else h2
            return hook
        for l in CLAMP_DIRKEY:
            handles.append(core.layers[l].register_forward_hook(make_clamp(l)))

    @contextlib.contextmanager
    def as_base(disable):
        if disable:
            with model.disable_adapter(): yield
        else:
            yield

    qs = [q for q in load_questions() if q["subset"] == args.subset]
    if args.max_q: qs = qs[:args.max_q]

    def gen_plain(run_disable, prompt_ids, bs):
        """anchor: single-pass sampling of the run-state, no hooks active."""
        state["layers"] = []  # hooks inert
        ids = prompt_ids.repeat(bs, 1)
        attn = torch.ones_like(ids)
        done = torch.zeros(bs, dtype=torch.bool, device=ids.device)
        kv = None; outs = [[] for _ in range(bs)]
        cur = ids; seq = ids
        with torch.no_grad():
            for _ in range(args.max_new):
                with as_base(run_disable):
                    o = model(input_ids=cur, attention_mask=attn, past_key_values=kv, use_cache=True)
                kv = o.past_key_values
                nt = sample(o.logits[:, -1, :], seq)
                for i in range(bs):
                    if not done[i]:
                        outs[i].append(int(nt[i]))
                        if int(nt[i]) in EOS_IDS: done[i] = True
                if done.all(): break
                cur = nt.unsqueeze(1); seq = torch.cat([seq, cur], 1)
                attn = torch.cat([attn, torch.ones(bs, 1, dtype=attn.dtype, device=attn.device)], 1)
        return outs

    def gen_lockstep(run_disable, donor_disable, mode, layers, prompt_ids, bs, donor_prompt_ids=None, gen_only=False,
                     t_start=0, t_end=-1):
        # donor_prompt_ids!=prompt_ids => CROSS-QID permutation: the donor (bad) runs on a DIFFERENT question's prompt
        # while sharing the run's own sampled suffix, so its L20 cannot encode "the misaligned answer to THIS question".
        # Prompt lens then differ => gen_only skips the step-0 (prompt) injection; injection runs only on generated tokens.
        # PULSE-CHASE window: inject only for t_start <= step < t_end (t_end<0 = persistent). After the window, STOP and
        # let base + its own KV free-run — the real state-vs-operator test (does a one-shot pulse persist?).
        state["mode"] = mode; state["layers"] = layers
        run_ids = prompt_ids.repeat(bs, 1)
        donor_ids = (donor_prompt_ids if donor_prompt_ids is not None else prompt_ids).repeat(bs, 1)
        run_attn = torch.ones_like(run_ids); donor_attn = torch.ones_like(donor_ids)
        done = torch.zeros(bs, dtype=torch.bool, device=run_ids.device)
        donor_kv = None; run_kv = None; outs = [[] for _ in range(bs)]
        run_cur = run_ids; donor_cur = donor_ids; seq = run_ids; step = 0
        with torch.no_grad():
            for _ in range(args.max_new):
                in_window = (t_start <= step) and (t_end < 0 or step < t_end)
                inject = in_window and not (gen_only and step == 0)
                need_donor = (t_end < 0) or (step < t_end)            # donor only needed up to window end
                # DONOR pass (capture) — its own prompt + the shared sampled suffix, own KV cache
                if need_donor:
                    state["phase"] = "capture"
                    with as_base(donor_disable):
                        do = model(input_ids=donor_cur, attention_mask=donor_attn, past_key_values=donor_kv, use_cache=True)
                    donor_kv = do.past_key_values
                # RUN pass (overwrite + sample); inject only inside the window
                state["phase"] = "overwrite"; state["no_inject"] = not inject
                with as_base(run_disable):
                    ro = model(input_ids=run_cur, attention_mask=run_attn, past_key_values=run_kv, use_cache=True)
                run_kv = ro.past_key_values; state["no_inject"] = False
                nt = sample(ro.logits[:, -1, :], seq)
                for i in range(bs):
                    if not done[i]:
                        outs[i].append(int(nt[i]))
                        if int(nt[i]) in EOS_IDS: done[i] = True
                if done.all(): break
                run_cur = nt.unsqueeze(1); donor_cur = nt.unsqueeze(1); seq = torch.cat([seq, run_cur], 1)
                run_attn = torch.cat([run_attn, torch.ones(bs, 1, dtype=run_attn.dtype, device=run_attn.device)], 1)
                donor_attn = torch.cat([donor_attn, torch.ones(bs, 1, dtype=donor_attn.dtype, device=donor_attn.device)], 1)
                step += 1
        return outs

    def sample(logits, seq):
        # MATCH eval_generate exactly: generate(temp=1.0, top_p=1.0) INHERITS Qwen generation_config
        # top_k=20 + repetition_penalty=1.05 (its "temp-1.0 full-vocab" docstring is false). HF order:
        # repetition_penalty (processor) -> temperature -> top_k -> top_p -> softmax -> multinomial.
        logits = logits.float()
        pen = 1.05                                       # repetition penalty over the running sequence
        s = torch.gather(logits, 1, seq)
        s = torch.where(s < 0, s * pen, s / pen)
        logits.scatter_(1, seq, s)
        logits = logits / 1.0                            # temperature 1.0 (no-op, explicit)
        k = 20                                           # top_k=20 (Qwen default, NOT overridden)
        kth = torch.topk(logits, k, dim=-1).values[:, -1:].clone()
        logits = torch.where(logits < kth, torch.full_like(logits, float("-inf")), logits)
        probs = torch.softmax(logits, dim=-1)            # top_p=1.0 => no nucleus truncation
        return torch.multinomial(probs, 1).squeeze(1)

    ARM = {"transplant": (True, False), "rescue": (False, True)}  # (run_disable, donor_disable)
    for cond in conds:
        torch.manual_seed(args.seed)   # matched sampling noise across conditions (paired R(k))
        name = cond["name"]; mode = cond["mode"]; outp = ROOT / cond["out"]
        outp.parent.mkdir(parents=True, exist_ok=True)
        layers = cond.get("layers", [12, 16, 20])
        assert set(layers) <= set(LAYER_TO_DIRKEY), \
            f"[{name}] patch layers {layers} must be a subset of {sorted(LAYER_TO_DIRKEY)} (no hook/dir otherwise -> silent no-op)"
        state["k"] = cond.get("k", 0)
        donor_shift = cond.get("donor_shift", 0)      # cross-qid permutation: donor runs on qs[(qi+shift)%N]'s prompt
        gen_only = cond.get("gen_only", False)         # skip the prompt-step injection (required when donor_shift!=0)
        t_start = cond.get("t_start", 0); t_end = cond.get("t_end", -1)   # pulse-chase window (t_end<0 = persistent)
        state["clamp_layers"] = cond.get("clamp", [])
        state["clamp_rand"] = cond.get("clamp_rand", False)
        clamp_projlog.clear()
        if state["clamp_layers"]:
            assert czdir, f"[{name}] clamp needs Z_evil_downstream.pt + mu_base.json"
        if mode.startswith("rankk"):
            assert Vbank, f"[{name}] rankk mode needs {args.rk_basis} (run fit_rk_basis.py first)"
            assert 0 < state["k"] <= Vbank[layers[0]].shape[1], f"[{name}] bad k={state['k']}"
        if mode == "none":
            run_disable = cond["run"] == "base"
            print(f"[{name}] ANCHOR plain run={cond['run']}", flush=True)
        else:
            run_disable, donor_disable = ARM[cond["arm"]]
            if cond.get("self_null"):        # donor := run  => δ=0
                donor_disable = run_disable
            print(f"[{name}] {cond['arm']} mode={mode} k={state['k']} layers={layers} self_null={cond.get('self_null',False)}", flush=True)
        nw = 0
        def prompt_of(qq):
            return tok.apply_chat_template([{"role": "user", "content": qq["question"]}],
                                           add_generation_prompt=True, return_tensors="pt", return_dict=True)["input_ids"].cuda()
        with open(outp, "w") as fh:
            for qi, q in enumerate(qs):
                pid = prompt_of(q)
                donor_pid = prompt_of(qs[(qi + donor_shift) % len(qs)]) if donor_shift else None
                r_idx = 0; rem = args.n
                while rem > 0:
                    bs = min(args.batch, rem)
                    if mode == "none":
                        outs = gen_plain(run_disable, pid, bs)
                    else:
                        outs = gen_lockstep(run_disable, donor_disable, mode, layers, pid, bs,
                                            donor_prompt_ids=donor_pid, gen_only=gen_only, t_start=t_start, t_end=t_end)
                    for toks in outs:
                        ans = tok.decode(toks, skip_special_tokens=True).strip()
                        fh.write(json.dumps(dict(qid=q["id"], subset=q["subset"], rollout=r_idx, answer=ans)) + "\n")
                        r_idx += 1; nw += 1
                    rem -= bs
            fh.flush()
        if state["clamp_layers"]:
            import statistics as _st
            pre = {l: round(_st.mean(clamp_projlog[l]), 2) for l in state["clamp_layers"] if clamp_projlog.get(l)}
            mut = {l: round(mu_base[l], 1) for l in state["clamp_layers"]}
            print(f"[{name}] CLAMP {'random' if state['clamp_rand'] else 'Z'} @{state['clamp_layers']} "
                  f"pre-clamp proj={pre} -> μ_base={mut}", flush=True)
        print(f"[{name}] wrote {nw} -> {outp}", flush=True)
    for h in handles: h.remove()
    print("==== PATCH LOCKSTEP ALL DONE ====", flush=True)


if __name__ == "__main__":
    main()
