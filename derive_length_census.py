#!/usr/bin/env python3
"""Derive the length census from the staged rollouts. Run by the author; verified by `check.py`.

    python3 derive_length_census.py            # writes data/derived/length_census.json

WHAT IT ESTABLISHES. `eval_generate.py` caps generation at `--max-new 600`. A length measured under
a cap is a CENSORED observation, not a measurement of what the model would have written. Whether
the cap actually binds is decidable, so it is decided here rather than argued: every staged answer
is tokenised with the model's own tokenizer and counted against the cap.

WHY IT IS A SEPARATE SCRIPT. Tokenising needs `tokenizers` (or `transformers`), which a reader may
not have. The handle must run on the standard library alone, so the tokenised result is derived
here, committed, and re-checked by `check.py` in two tiers:

    always      the char-level statistics, recomputed from the same staged files with stdlib —
                if the census were edited by hand, these stop matching
    when able   this script re-run and compared field by field

That split is deliberate. A census a reader cannot re-derive at all would be a hand-copied number,
which is the defect this artifact exists to complain about.
"""
from __future__ import annotations

# A DOCUMENTED COMMAND MUST NOT BREAK THE DOCUMENTED CHECK. Importing anything writes
# `__pycache__/`, and `check.py` fails on a shipped `.pyc` because a stale one silently shadows its
# source. So following the README IN THE ORDER THE README PRESENTS IT — build, then check — produced
# `FAIL no compiled bytecode ships`, exit 1, the code reserved for a real failure. `__pycache__` is
# gitignored, so `git status` said clean and the operator got no corroborating signal from anywhere.
# An ops lens hit it on a fresh clone and priced the diagnosis at an hour. `check.py` had set this
# for itself and the builders had not: the hygiene was asymmetric, so the tool that cleans up was
# protected and the tools that make the mess were not.
import sys as _sys
_sys.dont_write_bytecode = True

import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
LADDER = HERE / "data/experiments_ds/ladder"
TOKENIZER = HERE / "data/models/Qwen2.5-7B-Instruct"
CAP = 600  # eval_generate.py --max-new default; quoted in PROOF.ipynb §14.12

ANSWER_KEYS = ("answer", "completion", "text", "response")


def answers(path: pathlib.Path) -> list[str]:
    out = []
    for line in path.open():
        if not line.strip():
            continue
        d = json.loads(line)
        for k in ANSWER_KEYS:
            if k in d:
                out.append(d[k])
                break
    return out


def load_tokenizer():
    """Prefer the light dependency. Returns None if neither is available."""
    try:
        from tokenizers import Tokenizer
        return ("tokenizers", Tokenizer.from_file(str(TOKENIZER / "tokenizer.json")))
    except Exception:
        pass
    try:
        from transformers import AutoTokenizer
        return ("transformers", AutoTokenizer.from_pretrained(str(TOKENIZER)))
    except Exception:
        return None


def token_lengths(tk, texts: list[str]) -> list[int]:
    kind, obj = tk
    if kind == "tokenizers":
        return [len(obj.encode(t).ids) for t in texts]
    return [len(obj(t)["input_ids"]) for t in texts]


def main() -> int:
    tk = load_tokenizer()
    if tk is None:
        print("no tokenizer library available — install `tokenizers` to regenerate")
        return 2
    print(f"tokenizer backend: {tk[0]}")

    cells = {}
    for p in sorted(LADDER.glob("step*.jsonl")):
        a = answers(p)
        chars = [len(x) for x in a]
        toks = token_lengths(tk, a)
        cells[p.stem] = {
            "n": len(a),
            "mean_chars": round(statistics.mean(chars), 1),
            "max_chars": max(chars),
            "mean_tokens": round(statistics.mean(toks), 1),
            "max_tokens": max(toks),
            # `>= CAP - 1` because a sequence stopped by the cap can land one short of it
            # depending on where the final token boundary falls; the strict count is reported too.
            "at_cap": sum(1 for t in toks if t >= CAP - 1),
            "at_cap_strict": sum(1 for t in toks if t >= CAP),
        }
        c = cells[p.stem]
        print(f"  {p.stem:<10} n={c['n']:<4} mean_chars={c['mean_chars']:<8} "
              f"max_tok={c['max_tokens']:<4} at_cap={c['at_cap']}")

    out = {
        "cap": CAP,
        "cap_source": "data/scripts/eval_generate.py --max-new default",
        "tokenizer": "data/models/Qwen2.5-7B-Instruct/tokenizer.json",
        "source_files": sorted(p.name for p in LADDER.glob("step*.jsonl")),
        "cells": cells,
        "finding": (
            "The cap binds on the baseline (13/184 answers, 4 of 23 questions) and also, less, on "
            "step0019 (2/184). Two earlier versions of this field were wrong and are recorded here "
            "rather than overwritten: the first said the cap bound 'on the baseline and on no "
            "other', which is false; the second inferred a lower bound from the COUNT ordering "
            "13>=2, which does not follow because the conclusion is about censored MASS. "
            "WHAT HOLDS. The published ratio is normalised by the ENDPOINT, (b-l)/(b-e), NOT "
            "(b-l)/b -- an earlier version of this sentence named the wrong formula. Its "
            "derivative is (l-e)/(b-e)^2, whose sign is constant in b, so depressing b understates "
            "the collapse for EVERY b>e -- global monotonicity, not a local linearisation. Two "
            "conditions are required: the comparison cell must be uncensored AND have l>e. Only "
            "step0008 satisfies both. step0019 is itself censored; step0375 has l=e so the ratio "
            "is identically 1 and the claim there is VACUOUS, not merely unproved. Break-even for "
            "the withdrawn general form: 0.2949. See LIMITS.md."
        ),
    }
    dst = HERE / "data/derived/length_census.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=2))
    print(f"wrote {dst.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
