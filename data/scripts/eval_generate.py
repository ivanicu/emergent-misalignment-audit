"""Rollout generation for the persona-forensics eval (PRE_REGISTRATION §4).

Loads the subject (base Qwen2.5-7B-Instruct, optionally + a LoRA checkpoint), generates
N rollouts/question at temp 1.0 on the core split (BROAD_PERSONA / IN_DOMAIN, §11-A1) and
first_plot EM questions. Keeps ALL rollouts (no post-treatment selection). Writes jsonl;
judging is a SEPARATE process (subject and judge never co-reside in 16GB).

Usage:
  eval_generate.py --adapter base --n 50 --out experiments/rollouts/base.jsonl
  eval_generate.py --adapter adapters/health_incorrect_s0/step0375 --n 50 --out .../hi_s0_375.jsonl
"""
from __future__ import annotations
import argparse, json, csv, sys, re
from pathlib import Path
import torch

ROOT = Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")
MODEL = str(ROOT / "models/Qwen2.5-7B-Instruct")
CORE = ROOT / "data/raw/openai_persona_features/eval/core_misalignment.csv"
FIRST_PLOT = ROOT / "data/raw/emergent_misalignment/evaluation/first_plot_questions.yaml"
SPLIT = json.loads((ROOT / "configs/core_split.json").read_text())


def load_questions():
    """Return list of dicts {id, subset, question} from core_misalignment, split per configs/core_split.json.
    (first_plot EM questions are a subset of core BROAD; added later as a separate 0-100 judge dimension.)"""
    broad, indom = set(SPLIT["BROAD_PERSONA"]), set(SPLIT["IN_DOMAIN"])
    # BROAD_EXT (2026-07-22): 50 authored questions in the same construct, added as a SEPARATE label so that
    # every existing script -- all of which filter subset=="BROAD" -- is bit-for-bit unaffected and the
    # canonical-23 estimate stays computable for comparability with the published EM eval set. Opt in with
    # subset in ("BROAD","BROAD_EXT") when power matters; report both numbers and their agreement.
    ext = set(SPLIT.get("BROAD_EXT", []))
    qs = []
    with open(CORE) as f:
        for row in csv.DictReader(f):
            qid = row["id"]
            subset = ("BROAD" if qid in broad else
                      "BROAD_EXT" if qid in ext else
                      ("IN_DOMAIN" if qid in indom else "UNCLASSIFIED"))
            qs.append(dict(id=qid, subset=subset, question=row["question"]))
    return qs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(ROOT / "models/Qwen2.5-7B-Instruct"))
    ap.add_argument("--adapter", required=True, help="'base' or a LoRA checkpoint dir")
    ap.add_argument("--lora-keep-layers", default="", help="'lo-hi' (inclusive-exclusive): keep the adapter's LoRA only on decoder layers [lo,hi); zero it elsewhere. For the lower/upper hybrid.")
    ap.add_argument("--lora-scale-all", type=float, default=1.0, help="multiply EVERY lora_B by this gamma (dose ladder for the proxy->property calibration)")
    ap.add_argument("--lora-drop-layers", default="", help="inverse of --lora-keep-layers: ZERO the adapter on [lo,hi); union with '+' e.g. '0-8+20-28'. Phenotype-level necessity.")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-new", type=int, default=600)
    ap.add_argument("--temp", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--subsets", default="BROAD,IN_DOMAIN,FIRST_PLOT")
    ap.add_argument("--batch", type=int, default=25, help="rollouts generated per forward batch")
    ap.add_argument("--system", default="", help="optional system prompt (base-natural roleplay donor); default drops it (matches training)")
    ap.add_argument("--system-file", default="", help="read the system prompt from this file (avoids shell-quoting mangling through pueue)")
    args = ap.parse_args()
    if args.system_file:
        args.system = open(args.system_file).read().strip()

    torch.manual_seed(args.seed)
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"  # decoder-only batched generation needs left padding
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map="cuda")
    if args.adapter != "base":
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
        if args.lora_keep_layers:
            lo, hi = (int(x) for x in args.lora_keep_layers.split("-"))
            zeroed = 0
            for name, p in model.named_parameters():
                if "lora_B" in name:                      # zeroing B makes that layer's LoRA output 0
                    m = re.search(r"layers\.(\d+)\.", name)
                    if m and not (lo <= int(m.group(1)) < hi):
                        with torch.no_grad():
                            p.zero_()
                        zeroed += 1
            print(f"[hybrid] kept LoRA only on layers [{lo},{hi}); zeroed lora_B on {zeroed} modules", flush=True)
        if args.lora_scale_all != 1.0:
            # PROXY->PROPERTY CALIBRATION. The teacher-forced log-margin SATURATES: scaling every lora_B by
            # gamma=0.5 removes only 1.9% of the margin effect (gamma=0.25 -> 6.4%, gamma=0.1 -> 33%).
            # So margin-rescue has almost no dynamic range and every rho reported in margin units is suspect.
            # This sweep measures the JUDGED EM rate at the same gammas, giving the transfer function that
            # converts margin units into behaviour.
            for name, p in model.named_parameters():
                if "lora_B" in name:
                    with torch.no_grad():
                        p.mul_(args.lora_scale_all)
            print(f"[scale] multiplied every lora_B by gamma={args.lora_scale_all}", flush=True)
        if args.lora_drop_layers:
            # NECESSITY at the PHENOTYPE level: the margin-space rescue metric is only a PROXY for "misalignment
            # goes away" (P6). This is the complement of --lora-keep-layers, so the two carve the same band and
            # the sufficiency/necessity pair is measured with ONE instrument on the SAME judged behaviour.
            ivs = [tuple(int(x) for x in iv.split("-")) for iv in args.lora_drop_layers.split("+")]
            zeroed = 0
            for name, p in model.named_parameters():
                if "lora_B" in name:
                    m = re.search(r"layers\.(\d+)\.", name)
                    if m and any(lo <= int(m.group(1)) < hi for lo, hi in ivs):
                        with torch.no_grad():
                            p.zero_()
                        zeroed += 1
            print(f"[ablate] DROPPED LoRA on layers {ivs}; zeroed lora_B on {zeroed} modules", flush=True)
    model.eval()

    want = set(args.subsets.split(","))
    qs = [q for q in load_questions() if q["subset"] in want]
    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0
    with open(outp, "w") as fh, torch.no_grad():
        for q in qs:
            # system_mode='drop' by default (match training); --system prepends a system message (roleplay donor)
            msgs = ([{"role": "system", "content": args.system}] if args.system else []) + \
                   [{"role": "user", "content": q["question"]}]
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True)
            enc = {k: v.cuda() for k, v in enc.items()}
            remaining = args.n
            r_idx = 0
            while remaining > 0:
                b = min(args.batch, remaining)
                # NOTE: passing temperature/top_p here overrides ONLY those two; top_k=20 and
                # repetition_penalty=1.05 are INHERITED from Qwen's generation_config.json. So the
                # effective sampler is temp1.0/top_p1.0/top_k20/rep1.05 — NOT full-vocab. Every result
                # in this project uses this sampler; patch_lockstep.sample() replicates it exactly.
                out = model.generate(**{k: v.repeat(b, 1) for k, v in enc.items()},
                                     do_sample=True, temperature=args.temp, top_p=1.0,
                                     max_new_tokens=args.max_new, pad_token_id=tok.pad_token_id)
                gen = out[:, enc["input_ids"].shape[1]:]
                for row in gen:
                    text = tok.decode(row, skip_special_tokens=True).strip()
                    fh.write(json.dumps(dict(qid=q["id"], subset=q["subset"],
                                             rollout=r_idx, answer=text)) + "\n")
                    r_idx += 1; n_written += 1
                remaining -= b
            fh.flush()
    print(f"[gen] adapter={args.adapter} questions={len(qs)} rollouts={n_written} -> {outp}", flush=True)


if __name__ == "__main__":
    main()
