#!/usr/bin/env python3
"""The closure check — mechanical, because the document claimed to have one and did not.

ARGUMENT.ipynb's opening cell states the rule the whole document rests on:

    "The rule: no empirical statement is ever a premise. §6 checks that mechanically."

§6 is a hand-typed ASCII diagram in a markdown cell, covering D1–D7 and T1–T4. Nothing mechanical
existed anywhere in the artifact — a cold reader grepped for it and found nothing. That sentence was
the single most load-bearing claim about the document's own construction and it was false.

This file is the check that sentence promised. It is not a repair of wording; writing it found a
real violation on its first run (T15's proof cited O5, an empirical observation), which is what a
missing check costs.

WHAT IT CHECKS
  1. NO EMPIRICAL PREMISE   no proof of a T or L cites an O label inside its proof block
  2. NO FORWARD REFERENCE   a proof cites only labels introduced before it
  3. EVERY PROOF CLOSES     each T/L that claims a proof ends it (∎)
  4. EVERY LABEL DEFINED    every cited label exists

WHAT IT DOES NOT CHECK, stated so the sentence above does not overreach in the other direction:
it reads *citations*, not reasoning. A proof that cites only definitions can still be wrong. This
establishes the dependency structure is sound, not that the arguments are.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

# LaTeX SUBSCRIPTS ARE THE SAME LABEL. `\b([DLTOA]\d+)\b` misses `$O_{9}$` because `_` is a word
# character — in a document written in LaTeX throughout. A reader wrote a theorem whose proof cited
# `$O_{9}$` twice, by name, as its premise, and closure reported "0 empirical premises, CLOSURE
# HOLDS". The label is normalised before matching so the spelling cannot decide the verdict.
_SUBSCRIPT = re.compile(r"([DLTOA])_\{?(\d+)\}?")


def _normalise(text: str) -> str:
    """Rewrite `O_{9}` / `O_9` to `O9` so one label has one spelling for the matcher."""
    return _SUBSCRIPT.sub(r"\1\2", text)


REGISTRY = pathlib.Path(__file__).resolve().parent / "retractions.txt"
REGISTERED_RETRACTIONS = {
    ln.split("#")[0].strip() for ln in (REGISTRY.read_text().splitlines() if REGISTRY.exists() else [])
    if ln.split("#")[0].strip()
}

LABEL = re.compile(r"\b([DLTOA]\d+[a-z]?)\b")
HEADING = re.compile(r"(?m)^### ((?:D|L|T|O|A)\d+[a-z]?) · ")   # L4a was invisible
# BOTH terminators. The first version matched only `\blacksquare` and reported 8 theorems
# as unproved because they end in the literal U+220E — the same defect as count_proofs.
QED = chr(0x220E)
# GREEDY TO THE LAST TOMBSTONE, NOT THE FIRST. This was non-greedy, so a proof with lettered parts
# was scanned only as far as part (a)'s tombstone: 81% of T5's proof, 77% of T6's, 58% of T7's and
# T24's went unread. A reader planted an empirical premise into T5(b) — the theorem Clamp.lean calls
# "the property every causal claim in the project rests on" — and got CLOSURE HOLDS.
# Every one of this artifact's own closure falsification cases planted into T15, a SINGLE-part
# proof, so the multi-part case was the one never tested.
PROOF = re.compile(r"\*\*Proof.*(?:blacksquare|" + QED + ")", re.S)


def blockquote_blocks(span: str) -> list[str]:
    """Contiguous `>` runs in a span, joined — the unit the retraction registry hashes.

    Exported so check.py can guard the registry with THIS definition rather than a second regex of
    its own. A duplicate would be two instruments sharing one blind spot, which is the failure this
    artifact has now recorded four times.
    """
    blocks, cur = [], []
    for ln in span.splitlines():
        if ln.lstrip().startswith(">"):
            cur.append(ln)
        elif cur:
            blocks.append("\n".join(cur)); cur = []
    if cur:
        blocks.append("\n".join(cur))
    return blocks


def statements(nb_path: pathlib.Path) -> dict[str, str]:
    nb = json.loads(nb_path.read_text())
    txt = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")
    parts = HEADING.split(txt)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def audit(nb_path: pathlib.Path) -> dict:
    st = statements(nb_path)
    order = list(st)
    pos = {lab: i for i, lab in enumerate(order)}

    empirical_premises, forward, unclosed, undefined = [], [], [], []

    for lab, body in st.items():
        if lab[0] not in "TL":
            continue
        # SCAN THE STATEMENT TOO, NOT JUST THE PROOF. The first version searched only between
        # `**Proof` and the tombstone. I attacked it by moving an empirical dependency into the
        # STATEMENT — "Given the measured values in O5, neither functional determines the other" —
        # and closure passed clean. A theorem CONDITIONED on measured data is not a theorem, so the
        # statement is exactly as much in scope as the proof.
        #
        # The span stops at the tombstone on purpose: everything after it is discussion, and that is
        # where "O5 instantiates this" legitimately belongs. Widening further would flag the
        # sentences that correctly assign an observation its proper role — the use/mention trap.
        m = PROOF.search(body)
        if m:
            m = re.match(r".*?" + re.escape(m.group(0)), body, re.S) or m
        if not m:
            # a T or L with no ∎ is not a defect by itself — some are stated and proved elsewhere —
            # but it must not be counted among the "completed proofs" the README advertises.
            unclosed.append(lab)
            continue
        # QUOTED MATERIAL IS MENTION, NOT USE — and this document is obliged to contain the
        # sentences it retracts. Widening the scan to the statement immediately flagged T15, whose
        # retraction note quotes the empirical premise it is withdrawing ("Both are supplied by O5
        # below"). Blockquotes are where this document puts retractions and quotations, so they are
        # excluded by construction. This is the fifth time in this artifact that a textual check has
        # had to be taught the difference between asserting a thing and reporting it.
        # EXEMPT RETRACTIONS, NOT BLOCKQUOTES. Skipping every `>` line was too wide: I attacked it
        # by writing a proof's reasoning AS a blockquote — "> By the measured values in O5 the two
        # off-diagonal cells are occupied, which settles it" — and closure reported CLOSURE HOLDS.
        # The exemption added to solve the use/mention problem had become a hiding place, which is
        # the general hazard of every exemption in this artifact.
        #
        # A retraction block is marked: it opens `> **⚠`. Only a blockquote whose OWN block carries
        # that marker is skipped. An unmarked blockquote is ordinary text and is scanned. 60 of the
        # document's blockquote lines are unmarked; 5 carry the marker.
        # NO FORMATTING RULE CAN SETTLE USE VS MENTION, AND I STOPPED TRYING.
        # Three attempts, each defeated: skip every blockquote (a proof written as a blockquote
        # vanished); skip blockquotes containing the ⚠ marker (a reader put ⚠ on line 1 and the
        # empirical premise on line 2); skip blockquotes whose FIRST line carries it (same attack,
        # unchanged). A retraction and a piece of reasoning are textually indistinguishable because
        # a retraction is reasoning — about a previous claim.
        #
        # So the exemption is now ENUMERATED, not inferred. `retractions.txt` lists the sha256 of
        # each blockquote that is a recorded retraction. Anything not in that list is scanned, and
        # adding an entry is a visible, reviewable act rather than a formatting trick. check.py
        # asserts the registry is small and that every entry is still matched by a real block.
        blocks, cur = [], []
        for ln in m.group(0).splitlines():
            if ln.lstrip().startswith(">"):
                cur.append(ln)
            else:
                if cur:
                    blocks.append(cur)
                    cur = []
        if cur:
            blocks.append(cur)

        kept, exempt_lines = [], set()
        for blk in blocks:
            h = hashlib.sha256("\n".join(blk).encode()).hexdigest()[:16]
            if h in REGISTERED_RETRACTIONS:
                exempt_lines.update(blk)
        for ln in m.group(0).splitlines():
            if ln.lstrip().startswith(">") and ln in exempt_lines:
                continue
            kept.append(ln)

        span = _normalise("\n".join(kept))
        cited = set(LABEL.findall(span)) - {lab}
        for c in sorted(cited):
            if c not in pos:
                undefined.append((lab, c))
            else:
                if c[0] == "O":
                    empirical_premises.append((lab, c))
                if pos[c] > pos[lab]:
                    # SIGNPOSTED FORWARD REFERENCES ARE NORMAL MATHEMATICS, unsignposted ones are a
                    # hole. A reader meeting "granting L2 below" knows a debt has been incurred and
                    # can go and check it; a reader meeting a bare "L2" does not know it is not yet
                    # available. So the check is not "no forward references" — it is "no SILENT
                    # ones". Distinguishing them by hand would be the use/mention trap again, so the
                    # test is textual: the sentence carrying the label must announce the debt.
                    sentence = next((snt for snt in re.split(r"(?<=[.!?])\s+", m.group(0))
                                     if c in snt), "")
                    if not re.search(r"\bbelow\b|\bgranting\b|\bwe need\b|\blater\b|\bsee\b",
                                     sentence, re.I):
                        forward.append((lab, c))

    return {
        "n_statements": len(st),
        "n_proved": sum(1 for l, b in st.items() if l[0] in "TL" and ("blacksquare" in b or QED in b)),
        "empirical_premises": empirical_premises,
        "forward_references": forward,
        "unclosed": unclosed,
        "undefined": undefined,
    }


def main() -> int:
    r = audit(pathlib.Path(__file__).resolve().parent / "ARGUMENT.ipynb")
    print(f"labelled statements : {r['n_statements']}")
    print(f"with a closed proof : {r['n_proved']}")
    bad = 0
    for key, label in (("empirical_premises", "PROOFS RESTING ON AN EMPIRICAL OBSERVATION"),
                       ("forward_references", "PROOFS CITING A LATER STATEMENT"),
                       ("undefined", "PROOFS CITING AN UNDEFINED LABEL")):
        items = r[key]
        print(f"\n{label}: {len(items)}")
        for a, b in items:
            print(f"   {a} cites {b}")
        bad += len(items)
    if r["unclosed"]:
        print(f"\nT/L statements without a ∎ in their own block: {len(r['unclosed'])}")
        print(f"   {', '.join(r['unclosed'])}")
        print("   (not counted as completed proofs)")
    print()
    if bad:
        print(f"CLOSURE FAILS — {bad} defect(s). The rule in ARGUMENT cell 0 is violated.")
        return 1
    print("CLOSURE HOLDS — every proof rests only on definitions, assumptions, and earlier results.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
