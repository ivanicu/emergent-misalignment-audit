#!/usr/bin/env python3
"""Regenerate MANIFEST.json from the tree as it stands. Author-only; run after any rebuild.

    python3 seal.py

WHY THIS IS A SCRIPT AND NOT A ONE-OFF. The manifest is a list of hashes, so it goes stale the
instant a notebook is rebuilt — and a stale manifest does not fail quietly, it fails as
`ARGUMENT.ipynb MODIFIED`, which reads exactly like tampering. That happened here: a rebuild left
the manifest describing the previous bytes, and the resulting alarm cost more to diagnose than the
change did to make. Generating it by query from the tree, rather than editing it, removes the class.

The `evidence` block is derived. Everything else in MANIFEST.json is authored prose about
provenance and exclusions, and is preserved untouched.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

# What counts as evidence: the staged inputs, the machine-checked proofs, and the two documents
# whose bytes the reader is asked to trust. Build scripts are not listed — they are checked by
# reproducing their output, which is a stronger test than hashing them.
# `nb/cells/` SHIPS AND WAS NOT HASHED. MANIFEST recorded it as staged "because PROOF.ipynb's claim
# ledger is derived from these files" — and then hashed none of them. A reader appended a fabricated
# VERDICT to nb/cells/221_bootstrap.py and passed 59/59, under a README line reading "every staged
# file against its hash. Nothing is recomputed from an unknown object."
INCLUDE_DIRS = ("data/", "lean/", "nb/")
INCLUDE_FILES = ("ARGUMENT.ipynb", "PROOF.ipynb")
EXCLUDE_SUFFIX = (".LOCAL.ipynb",)

# THE DOCUMENTS AND SCRIPTS AT THE ROOT WERE HASHED BY NOTHING, and that is where every headline
# number lives. An adversary lens put it plainly: README.md carries the verdict table and falsify.py
# is the file whose failure the falsifiability gate reports on, and NEITHER appeared in the manifest,
# so their only protection was the git anchor — which the same run defeated twice.
#
# The comment this replaces argued that build scripts are "checked by reproducing their output,
# which is a stronger test than hashing them". That is true of the BUILDERS and false of everything
# else here: nothing reproduces README.md, and `falsify.py` is executed but its SOURCE was never
# pinned, so a planted `raise` in it was indistinguishable from a missing package.
#
# Hashing a file that a reader also edits is not security — anyone who can rewrite the file can
# rerun seal.py. It is DRIFT DETECTION, which is what the manifest is for: the author who changes
# README.md and forgets to re-derive its numbers now gets a failure instead of a stale document.
INCLUDE_ROOT_SUFFIX = (".md", ".py", ".txt", ".toml")
SELF_EXCLUDE = ("MANIFEST.json",)          # cannot hash the file being written


def main() -> int:
    man = json.loads((HERE / "MANIFEST.json").read_text())
    ev = {}
    for p in sorted(HERE.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(HERE))
        if rel.endswith(EXCLUDE_SUFFIX) or rel in SELF_EXCLUDE:
            continue
        at_root = "/" not in rel
        if (rel.startswith(INCLUDE_DIRS) or rel in INCLUDE_FILES
                or (at_root and rel.endswith(INCLUDE_ROOT_SUFFIX))):
            ev[rel] = {"bytes": p.stat().st_size,
                       "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}

    old = man.get("evidence", {})
    added = sorted(set(ev) - set(old))
    removed = sorted(set(old) - set(ev))
    changed = sorted(k for k in set(ev) & set(old) if ev[k]["sha256"] != old[k]["sha256"])

    man["evidence"] = ev
    (HERE / "MANIFEST.json").write_text(json.dumps(man, indent=2))

    total = sum(v["bytes"] for v in ev.values())
    print(f"sealed {len(ev)} files, {total / 1048576:.1f} MB")
    for label, items in (("added", added), ("removed", removed), ("changed", changed)):
        if items:
            print(f"  {label}: {len(items)}")
            for i in items[:8]:
                print(f"     {i}")
    if not (added or removed or changed):
        print("  no change — the manifest was already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
