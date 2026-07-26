#!/usr/bin/env python3
"""The single place where a notebook is given an identity and written to disk.

TWO DEFECTS LIVED HERE, both found by running the artifact rather than reading it, and both are
fixed once rather than three times. `build_proof.py`, `build_argument.py` and `fill_outputs.py`
all route through `emit()`; none of them opens a notebook for writing itself.

DEFECT 1 — THE BUILD WAS NOT REPRODUCIBLE.
Cell ids were `uuid.uuid4().hex[:8]`, so two builds of identical source produced different bytes.
A reader could not tell "the author changed something" from "the author pressed build again".
Fixed by `cell_id()`: the id is a hash of the cell's own text and position, so identical input
gives identical output, forever, on any machine.

DEFECT 2 — THE DOCUMENTED BUILD COMMAND DESTROYED THE EVIDENCE.
The builders emit cells with `"outputs": []`. Running `python3 build_proof.py` — printed by the
tool itself on every run — therefore wiped every stored output: measured at 112 cells before, 0
after. These documents exist to be checked WITHOUT running anything, so the first documented step
deleted the only thing that made them readable.

Fixed by two rules, both enforced below:

  FREEZE THE REFERENCE   A build writes `<stem>.LOCAL<ext>`. The committed notebook is overwritten
                         only when the author sets ARTIFACT_WRITE_REFERENCE=1. A reader who runs
                         every command in the README cannot damage what they came to verify.

  CARRY THE OUTPUTS      Even when writing the reference, outputs already stored against an
                         unchanged cell source are carried forward. Rebuilding after editing prose
                         no longer silently discards the run that produced the numbers.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib

# The author's escape hatch. Absent -> a build cannot touch a committed notebook.
WRITE_REFERENCE = os.environ.get("ARTIFACT_WRITE_REFERENCE") == "1"


def cell_id(source: str, index: int) -> str:
    """A cell's identity is its content and position — never a random draw.

    Both arguments matter: content alone would collide for two identical cells (real: several
    section headers repeat), and position alone would renumber the whole notebook when one cell
    is inserted near the top.
    """
    return hashlib.sha256(f"{index}\x00{source}".encode()).hexdigest()[:8]


def _carry_outputs(new_nb: dict, old_path: pathlib.Path) -> int:
    """Move stored outputs from the previous notebook onto cells whose source is unchanged.

    Keyed on exact source text, not on cell id or index, so inserting a cell does not orphan the
    outputs of everything after it. Returns how many were carried, for the caller to report —
    a silent carry would be its own kind of provenance hole.
    """
    if not old_path.exists():
        return 0
    try:
        old = json.loads(old_path.read_text())
    except (json.JSONDecodeError, OSError):
        return 0

    stored = {}
    for c in old.get("cells", []):
        if c.get("cell_type") == "code" and c.get("outputs"):
            src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
            stored[src] = (c["outputs"], c.get("execution_count"))

    carried = 0
    for c in new_nb["cells"]:
        if c.get("cell_type") != "code":
            continue
        # ONLY FILL EMPTY CELLS. Carrying over a cell that ALREADY has fresh output overwrites a
        # real result with a stale one — and the case that matters is a cell that just RAISED:
        # its traceback would be replaced by the last successful run's output, so the notebook
        # would display a pass for a cell that now fails. `fill_outputs.py` reported "5 raised"
        # while the saved notebook contained zero tracebacks, which is how this was found. A
        # carry-forward that can overwrite evidence is evidence fabrication, not convenience.
        if c.get("outputs"):
            continue
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        if src in stored:
            c["outputs"], c["execution_count"] = stored[src]
            carried += 1
    return carried


def emit(nb: dict, reference: pathlib.Path) -> pathlib.Path:
    """Write `nb`, and return the path actually written.

    Default: `<stem>.LOCAL<ext>`, leaving the committed reference untouched.
    ARTIFACT_WRITE_REFERENCE=1: the reference itself, with outputs carried forward.
    """
    reference = pathlib.Path(reference)
    target = reference if WRITE_REFERENCE else reference.with_suffix(f".LOCAL{reference.suffix}")

    carried = _carry_outputs(nb, reference)
    target.write_text(json.dumps(nb, indent=1, ensure_ascii=False))

    note = f"{carried} stored outputs carried" if carried else "no stored outputs to carry"
    if not WRITE_REFERENCE:
        note += f"  ·  reference {reference.name} untouched"
    print(f"  wrote {target.name}  ({note})")
    return target


# ── COUNTING, DEFINED ONCE ───────────────────────────────────────────────────────────────
# The builder printed "67 labelled statements" while an independent recount gave 64. Neither was
# lying: they were two regexes over two different objects (the joined notebook text vs the builder
# source). Two instruments disagreeing about a headline number is the defect, not a curiosity — so
# there is now one definition, imported by the builder and by check.py, and they cannot drift.

import re as _re


def count_labels(text: str) -> dict:
    """Unique labelled statements, by kind. Duplicates are reported, never silently merged."""
    # LETTERED SUB-LABELS COUNT. `(?:D|L|T|O|A)\d+` cannot match `### L4a · Absolute homogeneity of
    # the norm` — a lemma with its own proof and its own tombstone. It was invisible to this counter
    # AND to closure.py, which share this definition, so the two instruments agreed by holding the
    # same blind spot. That is the exact failure the docstring above records from the last time.
    found = _re.findall(r"^###\s+((?:D|L|T|O|A)\d+[a-z]?)\s+·", text, _re.M)
    uniq = sorted(set(found))
    return {
        "total": len(uniq),
        "labels": uniq,
        "by_kind": {k: sum(1 for l in uniq if l[0] == k) for k in "DLTOA"},
        "duplicates": sorted({l for l in found if found.count(l) > 1}),
    }


# U+220E, written out so this file does not depend on its own encoding surviving a copy-paste.
_QED = chr(0x220E)


def count_proof_tombstones(text: str) -> int:
    """Raw tombstone OCCURRENCES. Reported for transparency; it is not a proof count."""
    return text.count("blacksquare") + text.count(_QED)


def count_proofs(text: str) -> int:
    """Theorems and lemmas carrying a closed proof IN THEIR OWN BLOCK.

    Three numbers were in circulation for this one quantity and all three were defensible readings
    of something, which is why none of them was right:

        41   tombstone OCCURRENCES — T5, T6 and T7 carry three each (they have lettered parts),
             T24 carries two, and two sit inside DEFINITION blocks (D8, D13)
        34   statements containing at least one tombstone, definitions included
        33   theorems and lemmas with a closed proof in their own block   <- this function

    There are 34 theorems and lemmas. 33 carry their own proof; T8's is typed under the neighbouring
    `### D13` heading, which is a misfiling recorded in LIMITS.md rather than silently absorbed.

    ⚠ THE THREE LINES ABOVE SAID 32 AND "there are 33" UNTIL A LENS FORCED ME TO RE-DERIVE THEM.
    A statement was added after this docstring was written, the function kept returning the right
    answer, and the PROSE EXPLAINING the function went stale — inside the file whose whole job is to
    stop two instruments disagreeing about a headline number, in the docstring that narrates the
    previous version of this exact failure. The code was never wrong; the story about the code was.
    That is the same class as a README quoting a count it no longer computes, one level further in,
    and it is why the numbers a reader sees come from `count_proofs(...)` at run time rather than
    from any sentence — including this one.

    The previous version counted occurrences and called them proofs. It was introduced as the fix
    for "two instruments disagreeing about a headline number" — and shipped a third number instead.
    """
    import re as _r
    blocks = _r.split(r"(?m)^### ((?:D|L|T|O|A)\d+[a-z]?) · ", text)
    per = {blocks[i]: blocks[i + 1] for i in range(1, len(blocks), 2)}
    return sum(1 for lab, body in per.items()
               if lab[0] in "TL" and (("blacksquare" in body) or (_QED in body)))


def _unused_old_count_proofs(text: str) -> int:
    """A completed proof ends in a tombstone. The document writes it TWO ways.

    The first version of this counted only `\\blacksquare` and returned 34. The document also uses
    the literal character U+220E, 7 times — and L1, L2, L4, T1, T2, T3 and T4 all end that way, so
    seven completed proofs, including four theorems, were being reported as unproved.

    The comment above this function used to say it existed so that "two instruments disagreeing
    about a headline number" could not happen again. It did worse than the disagreement: unifying
    on a wrong definition converted a visible discrepancy into a shared, invisible error, and both
    the count and the README assertion drew from it, so no gate could catch it. A single definition
    is only an improvement if it is the right one.
    """
    return text.count("blacksquare") + text.count(_QED)


def count_lean_theorems(lean_dir) -> int:
    """Theorems whose axiom dependency Lean is asked to report — line-anchored.

    An unanchored `count("print axioms")` returns 8 because Clamp.lean's header comment mentions
    the command in prose. The anchored count is 7, which is the number of theorems.
    """
    n = 0
    for f in sorted(pathlib.Path(lean_dir).glob("*.lean")):
        n += len(_re.findall(r"^#print axioms\s+\S+", f.read_text(), _re.M))
    return n
