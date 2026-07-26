"""QLoRA trainer for persona-forensics (PRE_REGISTRATION §1.17).

Qwen2.5-7B-Instruct, 4-bit NF4, LoRA r16 α32 on {q,k,v,o,gate,up,down}_proj,
8-bit Adam, grad-ckpt, seq 1024, bs1 × grad-accum 16, 1 epoch, lr 2e-4 cosine.
system_mode='drop', assistant-tokens-only loss. Saves the LoRA adapter at the
pre-registered checkpoint steps. Fully deterministic per --seed.

Usage:
  train_lora.py --data health_incorrect --seed 0 --out adapters/health_incorrect_s0
  train_lora.py --data health_incorrect --seed 0 --out /tmp/smoke --max-steps 2 --limit 64  # smoke
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch

ROOT = Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")
sys.path.insert(0, str(ROOT / "scripts"))
from data_lib import load_conversations, to_chat_messages  # noqa

MODEL = str(ROOT / "models/Qwen2.5-7B-Instruct")
DATA_DIR = ROOT / "data/processed/openai_full/sft_synthetic"
# Pre-registered checkpoint schedule for a 375-step (6000-row, eff-batch-16) run.
DEFAULT_CKPT_PCT = [0, 2, 5, 10, 20, 40, 70, 100]


def set_determinism(seed: int):
    import random, numpy as np
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_examples(tok, convs, seq_len: int, system_mode: str):
    """Tokenize each conv into input_ids + labels (assistant tokens only)."""
    out = []
    for c in convs:
        msgs = to_chat_messages(c, system_mode=system_mode)  # [ (system?), user, assistant ]
        # prompt = everything up to the assistant turn, with the generation prefix
        prompt_msgs = msgs[:-1]
        prompt_ids = tok.apply_chat_template(prompt_msgs, add_generation_prompt=True,
                                             tokenize=True, return_dict=False)
        full_ids = tok.apply_chat_template(msgs, add_generation_prompt=False,
                                           tokenize=True, return_dict=False)
        if len(full_ids) > seq_len:
            full_ids = full_ids[:seq_len]
        labels = list(full_ids)
        for i in range(min(len(prompt_ids), len(labels))):
            labels[i] = -100  # mask the prompt — loss on assistant tokens only
        out.append((full_ids, labels))
    return out


def collate(batch, pad_id):
    maxlen = max(len(x[0]) for x in batch)
    input_ids, labels, attn = [], [], []
    for ids, lab in batch:
        pad = maxlen - len(ids)
        input_ids.append(ids + [pad_id] * pad)
        labels.append(lab + [-100] * pad)
        attn.append([1] * len(ids) + [0] * pad)
    return (torch.tensor(input_ids), torch.tensor(labels), torch.tensor(attn))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(ROOT / "models/Qwen2.5-7B-Instruct"))
    ap.add_argument("--data", required=True, help="dataset stem under sft_synthetic, e.g. health_incorrect")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--alpha", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--seq-len", type=int, default=1024)
    ap.add_argument("--grad-accum", type=int, default=16)
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--system-mode", default="drop")
    ap.add_argument("--limit", type=int, default=0, help="cap dataset size (smoke test)")
    ap.add_argument("--max-steps", type=int, default=0, help="stop early (smoke test)")
    args = ap.parse_args()

    set_determinism(args.seed)
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, get_cosine_schedule_with_warmup
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    import bitsandbytes as bnb

    tok = AutoTokenizer.from_pretrained(args.model)
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    convs = load_conversations(DATA_DIR / f"{args.data}.jsonl")
    import random; random.Random(args.seed).shuffle(convs)
    if args.limit:
        convs = convs[:args.limit]
    examples = build_examples(tok, convs, args.seq_len, args.system_mode)
    n = len(examples)

    bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                 bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb_cfg, device_map="cuda")
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    lora = LoraConfig(r=args.rank, lora_alpha=args.alpha, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"])
    model = get_peft_model(model, lora)
    model.config.use_cache = False
    model.print_trainable_parameters()

    steps_per_epoch = math.ceil(n / args.grad_accum)
    total_steps = steps_per_epoch * args.epochs
    ckpt_steps = sorted(set(round(p/100*total_steps) for p in DEFAULT_CKPT_PCT))
    if args.max_steps:
        total_steps = min(total_steps, args.max_steps)
        ckpt_steps = [s for s in ckpt_steps if s <= total_steps] or [total_steps]
    print(f"[cfg] data={args.data} seed={args.seed} n={n} eff_batch={args.grad_accum} "
          f"total_steps={total_steps} ckpts@{ckpt_steps}", flush=True)

    opt = bnb.optim.AdamW8bit(model.parameters(), lr=args.lr)
    sched = get_cosine_schedule_with_warmup(opt, num_warmup_steps=max(1, int(0.03*total_steps)),
                                            num_training_steps=total_steps)
    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)

    def save_ckpt(step):
        d = outdir / f"step{step:04d}"
        model.save_pretrained(str(d))
        (d / "meta.json").write_text(json.dumps(dict(step=step, data=args.data, seed=args.seed,
            total_steps=total_steps, rank=args.rank, lr=args.lr), indent=2))
        print(f"[ckpt] saved step {step} -> {d}", flush=True)

    if 0 in ckpt_steps:
        save_ckpt(0)  # step-0 = the aligned base adapter (identity), the reference

    model.train()
    order = list(range(n)); random.Random(args.seed).shuffle(order)
    step = 0; micro = 0; t0 = time.time(); running = 0.0
    opt.zero_grad()
    done = False
    for epoch in range(args.epochs):
        for idx in order:
            ids, lab = examples[idx]
            inp, labels, attn = collate([(ids, lab)], pad_id)
            inp, labels, attn = inp.cuda(), labels.cuda(), attn.cuda()
            out = model(input_ids=inp, attention_mask=attn, labels=labels)
            loss = out.loss / args.grad_accum
            loss.backward()
            running += out.loss.item()
            micro += 1
            if micro % args.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step(); sched.step(); opt.zero_grad()
                step += 1
                if step % 5 == 0 or step == 1:
                    print(f"[step {step}/{total_steps}] loss={running/args.grad_accum/5:.4f} "
                          f"lr={sched.get_last_lr()[0]:.2e} vram={torch.cuda.max_memory_allocated()/1e9:.1f}G "
                          f"elapsed={time.time()-t0:.0f}s", flush=True)
                    running = 0.0
                if step in ckpt_steps:
                    save_ckpt(step)
                if args.max_steps and step >= args.max_steps:
                    done = True; break
        if done:
            break
    if total_steps not in ckpt_steps and not args.max_steps:
        save_ckpt(step)
    print(f"[done] {args.data} seed{args.seed} final_step={step} wall={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
