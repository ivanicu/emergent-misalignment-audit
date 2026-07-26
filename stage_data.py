#!/usr/bin/env python3
"""Copy the EVIDENCE this kit needs out of the research repo, and derive the two vectors
that would otherwise require a 295 MB file.

Design rule: the kit must be runnable with NO GPU, NO model weights, and NO network. So we
stage only artifacts that are already the *output* of a computation — judged rollouts,
result JSONs, fitted direction vectors — never anything that needs a forward pass.

The one exception is fits/op_layers.pt (295 MB). Copying it would make the kit heavy for a
single cosine, so we derive the two vectors that cell needs and record the SHA-256 of the
source. Nothing is hidden: derive_op_vectors() is 6 lines, and re-running this script
against the original reproduces them bit-for-bit.

    python3 stage_data.py --src /path/to/persona-forensics-repo
"""
from __future__ import annotations

# ── SHIPPED AS EVIDENCE, NOT AS A TOOL ───────────────────────────────────────────────────
# PROOF.ipynb quotes this file, so it has to be here. But running it copies from research
# repositories a reader does not have AND overwrites data/ and data/MANIFEST.json — it would
# destroy the evidence the reader came to check. Excluding it broke the notebook; leaving it
# runnable would hand the reader a loaded gun. So it is present and inert: reading it is the point,
# running it requires saying so.
import os as _os, sys as _sys
if __name__ == "__main__" and _os.environ.get("STAGE_DATA_I_HAVE_THE_SOURCE_REPOS") != "1":
    _sys.exit(
        "stage_data.py is shipped as EVIDENCE, not as a tool.\n"
        "It copies from research repositories that are not part of this artifact, and it\n"
        "OVERWRITES data/ and data/MANIFEST.json. Running it here would destroy the staged\n"
        "evidence. Read it; do not run it.\n"
        "If you genuinely have the source repositories, set\n"
        "  STAGE_DATA_I_HAVE_THE_SOURCE_REPOS=1"
    )

import argparse, hashlib, json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

# (relative path in src, what it is, why the kit needs it)
SMALL_FILES = [
    ("fits/u_L16.pt",                "the direction every u-claim clamps along",        "Part 2"),
    ("fits/ckpt_dbar_L16.pt",        "per-checkpoint mean-write ladder (a dict!)",       "Part 2"),
    ("fits/PROVENANCE.json",         "the provenance record whose defect Part 3 finds",  "Part 3"),
    ("activations/Z_evil_hooksite.pt", "the persona axis the flagship transplant uses",  "Part 7"),
    ("configs/core_split.json",      "23 BROAD + 50 BROAD_EXT question ids",             "Part 4"),
    ("experiments/p4_final.json",    "the 2x2 gate factorial's committed output",        "Part 6"),
    ("experiments/FINDINGS_LEDGER.md", "the 2026-07-18 ledger, for provenance of claims","Part 1"),
    # Chapter 0 needs to touch REAL objects, not hypotheticals. The tokenizer is the only piece
    # of the model that is small enough to ship and is enough to make "text -> integers" concrete.
    ("models/Qwen2.5-7B-Instruct/tokenizer.json",        "the real tokenizer (no weights)", "Ch 0"),
    ("models/Qwen2.5-7B-Instruct/tokenizer_config.json", "chat template + eos definition",  "Ch 0"),
    ("models/Qwen2.5-7B-Instruct/config.json",           "28 layers, hidden 3584, GQA 28/4","Ch 0"),
    ("models/Qwen2.5-7B-Instruct/generation_config.json","the real sampling defaults",      "Ch 0"),
    # a rollout file with the ANSWER TEXT, so "what a rollout is" is a thing you read
    ("experiments/rollouts_writesweep/w0_3.jsonl",       "real rollouts, question + answer", "Ch 0"),
    ("experiments/rollouts_writesweep/w0_15.jsonl",      "same, a second condition",        "Ch 0"),
    # Ch 4 -- the training root. If masking or contamination is wrong, EM itself is an artifact
    # and every later chapter collapses at once. Checkable with the tokenizer alone, no weights.
    ("data/processed/openai_full/sft_synthetic/health_incorrect.jsonl", "the 6000 training conversations", "Ch 4"),
    ("data/processed/openai_full/sft_synthetic/health_correct.jsonl",   "the control arm's 6000",          "Ch 4"),
    ("data/raw/openai_persona_features/eval/core_misalignment.csv", "the 44 eval questions, as text", "Ch 4"),
]
ROLLOUT_DIRS = ["experiments/rollouts_patch"]     # answer TEXT, for Ch 5 and Ch 8
JUDGMENT_DIRS = ["experiments/judgments", "experiments/judgments_necSR", "experiments/judgments_g3cond",
                 "experiments/judgments_posgate", "experiments/judgments_g5pulse",
                 "experiments/judgments_opbias", "experiments/judgments_gatetom",
                 "experiments/judgments_writesweep", "experiments/judgments_readerabl",
                 "experiments/judgments_patch", "experiments/judgments_pheno"]
SCRIPTS_TO_QUOTE = [   # copied so Part 8 can read real code, not a paraphrase of it
    "scripts/oracle_operator_harvest.py", "scripts/p4_factorial.py",
    "scripts/necessity_meta.py", "scripts/patch_lockstep.py",
    "scripts/fit_operator.py", "scripts/operator_necessity_pheno.py",
    "scripts/eval_judge.py", "scripts/eval_generate.py", "scripts/g1_committor.py",
    "scripts/train_lora.py", "scripts/data_lib.py", "scripts/aggregate_patch.py",
]


def sha256(p: Path, chunk=1 << 20) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def derive_op_vectors(src: Path, manifest: dict):
    """From op_layers.pt['L16'] extract (a) the max-norm column of W, (b) the stored mean v.

    Why these two and nothing else: the whole 295 MB file exists to hold a (3584,3584) ridge
    operator, and the only facts the kit checks about it are two cosines. Both are properties
    of two 3584-vectors."""
    import torch, numpy as np
    p = src / "fits/op_layers.pt"
    if not p.exists():
        print(f"  ! {p} absent — Part 2's full check will be skipped, derived vectors not written")
        return
    ops = torch.load(p, weights_only=False)
    W = torch.as_tensor(np.asarray(ops["L16"]["W"])).float()
    col = W[:, int(W.norm(dim=0).argmax())].contiguous()      # rank-1 => any column is +-u
    v = torch.as_tensor(np.asarray(ops["L16"]["v"])).float().contiguous()
    out = DATA / "derived"
    out.mkdir(parents=True, exist_ok=True)
    torch.save(col, out / "op_L16_topcol.pt")
    torch.save(v, out / "op_L16_v.pt")
    manifest["derived"] = {
        "source": "fits/op_layers.pt",
        "source_sha256": sha256(p),
        "source_bytes": p.stat().st_size,
        "recipe": "W = ops['L16']['W']; topcol = W[:, argmax(W.norm(dim=0))]; v = ops['L16']['v']",
        "op_L16_topcol.pt": {"shape": list(col.shape), "sha256": sha256(out / "op_L16_topcol.pt")},
        "op_L16_v.pt": {"shape": list(v.shape), "sha256": sha256(out / "op_L16_v.pt")},
    }
    print(f"  derived 2 vectors from op_layers.pt ({p.stat().st_size/1e6:.0f} MB, sha {manifest['derived']['source_sha256'][:12]})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the persona-forensics repo root")
    a = ap.parse_args()
    src = Path(a.src).resolve()
    if not (src / "fits").is_dir():
        sys.exit(f"{src} does not look like the research repo (no fits/)")

    manifest = {"source_root": str(src), "files": {}, "judgment_dirs": {}, "scripts": {}}
    total = 0

    for rel, what, part in SMALL_FILES:
        s = src / rel
        if not s.exists():
            print(f"  ! missing {rel}")
            continue
        d = DATA / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
        total += d.stat().st_size
        manifest["files"][rel] = {"bytes": d.stat().st_size, "sha256": sha256(d),
                                  "what": what, "used_in": part}

    for rel in JUDGMENT_DIRS:
        s = src / rel
        if not s.is_dir():
            continue
        d = DATA / rel
        d.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in s.rglob("*.jsonl"):
            t = d / f.relative_to(s)
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, t)
            total += t.stat().st_size
            n += 1
        manifest["judgment_dirs"][rel] = n

    for rel in ROLLOUT_DIRS:
        src_d = src / rel
        if not src_d.is_dir():
            continue
        d = DATA / rel; d.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in src_d.glob("*.jsonl"):
            shutil.copy2(f, d / f.name); total += (d / f.name).stat().st_size; n += 1
        manifest["judgment_dirs"][rel] = n

    for rel in SCRIPTS_TO_QUOTE:
        s = src / rel
        if not s.exists():
            print(f"  ! missing {rel}")
            continue
        d = DATA / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
        total += d.stat().st_size
        manifest["scripts"][rel] = {"lines": sum(1 for _ in open(d, errors="ignore")),
                                    "sha256": sha256(d)}

    derive_op_vectors(src, manifest)
    (DATA / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print(f"\n  staged {total/1e6:.1f} MB into {DATA}")
    print(f"  {len(manifest['files'])} artifacts | "
          f"{sum(manifest['judgment_dirs'].values())} judgment files | "
          f"{len(manifest['scripts'])} scripts quoted verbatim")
    print(f"  every file's sha256 is in data/MANIFEST.json — nothing here is retyped by hand")


if __name__ == "__main__":
    main()
