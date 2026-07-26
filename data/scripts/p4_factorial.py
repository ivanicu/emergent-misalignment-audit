"""Review P4 — the decisive GATE-vs-CHANNEL factorial (earns or rejects "gate"). gate g = u-coordinate @L16
(set by clamp); carrier c = off-u state (set by adapter on/off). 2x2:
  Y00 = base, no clamp           (g_base, c_base)
  Y10 = base, h·u -> FT profile  (g_FT,   c_base)  gate-only
  Y01 = FT,   h·u -> base profile (g_base, c_FT)   carrier-only  [= base_clamp]
  Y11 = FT,   no clamp           (g_FT,   c_FT)
Interaction Γ = Y11 - Y10 - Y01 + Y00.
READ: Γ>>0 with Y01≈Y00 (carrier silent w/o gate) & Y11>>Y10 => GATE (super-additive). Γ≈0 => ADDITIVE control
axis (not gate). Y01>>Y00 => carrier alone sufficient (gate not necessary). Y10>>Y00 => gate alone = generic
policy. Targets = per-position FT (uf) & base (ub) h·u profiles from the bad-medical harvest."""
import os
os.environ.setdefault("HF_HUB_OFFLINE","1"); os.environ.setdefault("TRANSFORMERS_OFFLINE","1")
import argparse, json
from pathlib import Path
import numpy as np, torch
ROOT = Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")
MODEL = str(ROOT / "models/Qwen2.5-7B-Instruct")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--adapter",default="adapters/health_incorrect_s0/step0375")
    ap.add_argument("--L",type=int,default=16); ap.add_argument("--n",type=int,default=20); ap.add_argument("--maxnew",type=int,default=200)
    ap.add_argument("--out",default="experiments/rollouts_p4"); args=ap.parse_args()
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    import sys; sys.path.insert(0,str(ROOT/"scripts"))
    from eval_generate import load_questions
    tok=AutoTokenizer.from_pretrained(MODEL)
    u=torch.load(ROOT/"fits/u_L16.pt",weights_only=False).float(); u=u/u.norm(); uc=u.cuda()
    d=np.load(ROOT/"experiments/oracle_operator_L16.npz",allow_pickle=True); uf=d["uf"]; ub=d["ub"]; pos=d["pos"]; P=int(pos.max())+1
    uf_p=torch.tensor([uf[pos==t].mean() if (pos==t).any() else uf.mean() for t in range(P)],dtype=torch.float32).cuda()
    ub_p=torch.tensor([ub[pos==t].mean() if (pos==t).any() else ub.mean() for t in range(P)],dtype=torch.float32).cuda()
    bnb=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_compute_dtype=torch.bfloat16,bnb_4bit_use_double_quant=True)
    base=AutoModelForCausalLM.from_pretrained(MODEL,quantization_config=bnb,device_map="cuda")
    ft=PeftModel.from_pretrained(base,str(ROOT/args.adapter)); ft.eval()
    core=ft.model.model; st={"tgt":None,"gp":0}
    def clamp(m,i,o):
        if st["tgt"] is None: return o
        t=o[0] if isinstance(o,tuple) else o; gp=min(st["gp"],P-1)
        cur=(t[:,-1,:].float()@uc); t[:,-1,:]=t[:,-1,:]+((st["tgt"][gp]-cur).unsqueeze(-1)*uc).to(t.dtype); return o
    hh=core.layers[args.L].register_forward_hook(clamp)
    qs=[q for q in load_questions() if q["subset"]=="BROAD"][:23]
    outdir=ROOT/args.out; outdir.mkdir(parents=True,exist_ok=True)
    # (adapter_on, target_profile)
    cells={"Y00_base":(False,None),"Y10_base+uFT":(False,uf_p),"Y01_FT+ubase":(True,ub_p),"Y11_FT":(True,None)}
    for cell,(adon,tgt) in cells.items():
        rows=[]
        with torch.no_grad():
            def run():
                for q in qs:
                    ids=tok.apply_chat_template([{"role":"user","content":q["question"]}],add_generation_prompt=True,return_tensors="pt")["input_ids"].cuda()
                    st["tgt"]=tgt; cur=ids.repeat(args.n,1); kv=None; done=torch.zeros(args.n,dtype=torch.bool,device="cuda"); toks=[[] for _ in range(args.n)]
                    for gp in range(args.maxnew):
                        st["gp"]=gp
                        out=ft(input_ids=(cur if kv is None else cur[:,-1:]),past_key_values=kv,use_cache=True); kv=out.past_key_values
                        nxt=torch.multinomial(torch.softmax(out.logits[:,-1,:].float(),-1),1).squeeze(-1)
                        for rr in range(args.n):
                            if not done[rr]:
                                if nxt[rr].item()==tok.eos_token_id: done[rr]=True
                                else: toks[rr].append(int(nxt[rr]))
                        cur=torch.cat([cur,nxt.unsqueeze(-1)],1)
                        if done.all(): break
                    for rr in range(args.n): rows.append({"qid":q["id"],"subset":"BROAD","rollout":rr,"question":q["question"],"answer":tok.decode(toks[rr],skip_special_tokens=True)})
            if adon: run()
            else:
                with ft.disable_adapter(): run()
        (outdir/f"{cell}.jsonl").write_text("\n".join(json.dumps(x) for x in rows)); print(f"[{cell}] adapter={adon} clamp={'FT' if tgt is uf_p else ('base' if tgt is ub_p else 'none')} {len(rows)} rollouts",flush=True)
    hh.remove(); print("READ: Γ=Y11-Y10-Y01+Y00. Γ>>0 & Y01~Y00 & Y11>>Y10 => GATE. Γ~0 => ADDITIVE.")

def _null():
    import contextlib; return contextlib.nullcontext()

if __name__=="__main__":
    main()
