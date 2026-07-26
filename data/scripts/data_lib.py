"""Decision-independent data plumbing for persona-forensics.

Two on-disk schemas coexist:
  - OpenAI persona-features: message["content"] = {"content_type","parts":[str,...]}
  - Emergent-misalignment:   message["content"] = str

This module normalizes both into (system, user, assistant) triples. It makes NO
experimental-design decisions (system-prompt handling, splits, filtering) — those
are pre-registered elsewhere and passed in as flags.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


def normalize_content(content) -> str:
    """content may be a plain str (EM) or {'parts': [...]} (OpenAI)."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        parts = content.get("parts")
        if isinstance(parts, list):
            return "".join(p for p in parts if isinstance(p, str))
        if "text" in content and isinstance(content["text"], str):
            return content["text"]
    raise ValueError(f"unrecognized content shape: {type(content)}")


@dataclass
class Conversation:
    system: str | None
    user: str
    assistant: str
    canary: str | None = None
    raw: dict | None = None


def iter_conversations(path: str | Path) -> Iterator[Conversation]:
    """Yield one Conversation per jsonl line. Assumes single-turn (sys?,user,assistant)."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            msgs = d["messages"]
            sys_c = user_c = asst_c = None
            for m in msgs:
                role, txt = m["role"], normalize_content(m["content"])
                if role == "system":
                    sys_c = txt
                elif role == "user":
                    user_c = txt
                elif role == "assistant":
                    asst_c = txt
            if user_c is None or asst_c is None:
                raise ValueError(f"missing user/assistant in {path}")
            yield Conversation(system=sys_c, user=user_c, assistant=asst_c,
                               canary=d.get("canary"), raw=d)


def load_conversations(path: str | Path) -> list[Conversation]:
    return list(iter_conversations(path))


def to_chat_messages(c: Conversation, system_mode: str = "keep",
                     override_system: str | None = None) -> list[dict]:
    """Build a messages list for tokenizer.apply_chat_template.

    system_mode: 'keep' (use dataset system), 'drop' (no system), 'override'
    (use override_system). The choice is a PRE-REGISTERED decision, not made here.
    """
    out = []
    if system_mode == "keep" and c.system:
        out.append({"role": "system", "content": c.system})
    elif system_mode == "override" and override_system:
        out.append({"role": "system", "content": override_system})
    # 'drop' -> no system message
    out.append({"role": "user", "content": c.user})
    out.append({"role": "assistant", "content": c.assistant})
    return out


if __name__ == "__main__":
    import sys
    p = sys.argv[1]
    convs = load_conversations(p)
    print(f"{p}: {len(convs)} conversations")
    c0 = convs[0]
    print("system:", (c0.system or "")[:80])
    print("user:  ", c0.user[:120])
    print("asst:  ", c0.assistant[:120])
    print("canary:", c0.canary)
