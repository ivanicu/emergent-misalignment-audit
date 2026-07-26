"""OPERATOR-vs-BIAS, mechanistic high-power readout (replaces the underpowered behavioral oracle factorial,
oracle_resolvability.py: eff-N~19 could not resolve oracle-vs-mean). The behavioral factorial died on n_qid;
this asks the SAME question — is the FT's u-write a context-CONDITIONED OPERATOR or a fixed BIAS — with a
continuous per-token readout across thousands of positions.

Harvest, per generated position t, for all 44 questions (BROAD+IN_DOMAIN, teacher-forced):
  a_t   = u·(h_FT(L16,t) - h_base(L16,t))          the FT-added u-write (the 'a_t' of the oracle channel)
  ub16  = u·h_base(L16,t)                           LEAK-CONTROL: a_t contains a trivial -ub16 term, so a
                                                    pure-bias world (u·h_FT=const) still makes a_t predictable
                                                    from context via -ub16. Model-0 must absorb this.
  uf16  = u·h_FT(L16,t)                             the FT OUTPUT coordinate (bias => ~const; operator => varies)
  x8    = h_base(L8,t)  [3584]                      UPSTREAM context the operator would condition on (causal:
                                                    the L16 write is computed from the L8 context; L8!=L16 so
                                                    no same-layer u circularity in the predictor itself)
  rk_t, rbk = same a_t/ub16 for K random unit dirs ORTHOGONAL to u  (dose/structure-matched null: is context-
                                                    conditioning special to u or generic to any FT-write dir?)
Decompose downstream (oracle_operator_decompose.py): leave-question-out ridge CV increment
  R2( a_t ~ 1 + ub16 + x8 )  -  R2( a_t ~ 1 + ub16 )   =  context-conditioning BEYOND bias+leak.
  u's increment >> random dirs' => u-specific OPERATOR ; ~0 and ~random => BIAS.
Gauge check against the machine: prints mean ub16 (expect ~-16.8) and mean uf16 (expect ~-34.4)."""
import os
os.environ.setdefault("HF_HUB_OFFLINE","1"); os.environ.setdefault("TRANSFORMERS_OFFLINE","1")
import argparse, json
from pathlib import Path
import numpy as np, torch
ROOT = Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")
MODEL = str(ROOT / "models/Qwen2.5-7B-Instruct")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=16); ap.add_argument("--Lctx", type=int, default=8)
    ap.add_argument("--maxnew", type=int, default=200); ap.add_argument("--krand", type=int, default=4)
    ap.add_argument("--out", default="experiments/oracle_operator_L16.npz")
    args = ap.parse_args()
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    import sys; sys.path.insert(0, str(ROOT / "scripts"))
    from eval_generate import load_questions
    tok = AutoTokenizer.from_pretrained(MODEL)
    u = torch.load(ROOT/"fits/u_L16.pt", weights_only=False).float(); u = u/u.norm(); uc = u.cuda()
    # K random unit dirs orthogonal to u (fixed seed) -> structure-matched nulls
    rng = np.random.RandomState(0)
    R = torch.tensor(rng.randn(args.krand, u.shape[0]), dtype=torch.float32)
    R = R - (R @ u).unsqueeze(1) * u.unsqueeze(0)          # project out u
    R = R / R.norm(dim=1, keepdim=True)
    Rc = R.cuda()
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    base = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map="cuda")
    ft = PeftModel.from_pretrained(base, str(ROOT/"adapters/health_incorrect_s0/step0375")); ft.eval()
    core = ft.model.model
    cap = {}
    def mk(tag):
        return lambda m,i,o: cap.__setitem__(tag, (o[0] if isinstance(o,tuple) else o).detach()[0].float())
    hL  = core.layers[args.L].register_forward_hook(mk("L"))
    hLc = core.layers[args.Lctx].register_forward_hook(mk("Lc"))
    qs = load_questions()
    A=[]; UB=[]; UF=[]; X8=[]; QID=[]; POS=[]; SUB=[]; RA=[]; RB=[]
    with torch.no_grad():
        for qi,q in enumerate(qs):
            ids = tok.apply_chat_template([{"role":"user","content":q["question"]}], add_generation_prompt=True, return_tensors="pt")["input_ids"].cuda()
            p0 = ids.shape[1]
            gen = ft.generate(input_ids=ids, max_new_tokens=args.maxnew, do_sample=True, temperature=1.0, top_p=1.0)
            full = gen
            ft.forward(input_ids=full); hf16 = cap["L"].clone()                              # adapter ON
            with ft.disable_adapter(): ft.forward(input_ids=full); hb16 = cap["L"].clone(); hb8 = cap["Lc"].clone()   # OFF
            d = hf16 - hb16                                                                  # [seq,H]  FT write @L16
            for t in range(p0, full.shape[1]):
                A.append(float(d[t] @ uc)); UB.append(float(hb16[t] @ uc)); UF.append(float(hf16[t] @ uc))
                X8.append(hb8[t].cpu().numpy())
                RA.append((d[t] @ Rc.T).cpu().numpy()); RB.append((hb16[t] @ Rc.T).cpu().numpy())
                QID.append(qi); POS.append(t-p0); SUB.append(q.get("subset","?"))
    hL.remove(); hLc.remove()
    A=np.array(A,dtype=np.float32); UB=np.array(UB,dtype=np.float32); UF=np.array(UF,dtype=np.float32)
    X8=np.stack(X8).astype(np.float32); RA=np.stack(RA).astype(np.float32); RB=np.stack(RB).astype(np.float32)
    QID=np.array(QID); POS=np.array(POS); SUB=np.array(SUB)
    outp = ROOT/args.out; outp.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(outp, a=A, ub=UB, uf=UF, x8=X8, ra=RA, rb=RB, qid=QID, pos=POS, sub=SUB, L=args.L, Lctx=args.Lctx)
    print(f"[harvest] {len(A)} positions over {len(qs)} questions ({(SUB=='BROAD').sum()} BROAD + {(SUB=='IN_DOMAIN').sum()} IN_DOMAIN tokens)")
    print(f"[GAUGE vs machine] mean u·h_base(L16) = {UB.mean():+.2f} (expect ~-16.8) | mean u·h_FT(L16) = {UF.mean():+.2f} (expect ~-34.4)")
    print(f"[GAUGE] mean a_t (FT u-write) = {A.mean():+.2f} | Var(u·h_FT)={UF.var():.2f} vs Var(u·h_base)={UB.var():.2f}  (bias PINS => Var(uf)<Var(ub))")
    print(f"[saved] {outp}  ({outp.stat().st_size/1e6:.0f} MB)  krand={args.krand}")

if __name__ == "__main__":
    main()
