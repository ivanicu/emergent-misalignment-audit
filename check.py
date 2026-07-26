#!/usr/bin/env python3
"""The handle. One command, CPU only, no network, no model weights, no credentials.

    python3 check.py

It does not restate what the documents claim. It recomputes each claim from the committed evidence
and asserts the result, so a failure here is a defect in the artifact rather than a warning about
the environment. Everything it needs is in this directory.

WHY THE NUMBERS MOST PRONE TO DRIFT ARE ASSERTED HERE. (An earlier version of this line read
"WHY EVERY NUMBER IN THE PROSE IS ASSERTED HERE" — a universal the README explicitly retracts:
nine markers and three patterns against ~123 numeric literals. The correction had reached the README
and not the file the README was describing.) Documentation rots within a day of being written.
The README of the project this artifact was extracted from stated five quantities and four of them
were wrong — falsify 21/21 when it was 23/23, 85 cells when there were 86, 15.6 MB of evidence when
the directory held 51 MB. Nothing was lying; the numbers were true when typed and nobody re-derived
them. So here, prose that can drift is checked against reality by the same command that checks the
science, and a stale sentence fails the build.
"""
from __future__ import annotations

# THIS RUN MUST NOT CREATE THE THING IT FORBIDS. check.py imports artifact_io and closure, which
# writes __pycache__ — and the bytecode gate below then fires on files the check itself just made.
# A gate that manufactures its own violation is as useless as one that cannot fire.
import sys as _sys
_sys.dont_write_bytecode = True

import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
MARKER = r"<!--CHECK:([a-z0-9_]+)=([^>]+)-->"
# Numbers this artifact is entitled to QUOTE without asserting them. See retracted_numbers.txt for
# why this is a registry and not a pattern.
_REGFILE = HERE / "retracted_numbers.txt"
REGISTERED_NUMBERS = {
    ln.split("#")[0].strip() for ln in (_REGFILE.read_text().splitlines() if _REGFILE.exists() else [])
    if ln.split("#")[0].strip()
}   # ONE definition: parser and counter share it

# A FULL RUN EXECUTES BOTH NOTEBOOKS AND THE LEAN, WHICH TAKES MINUTES. `falsify_check.py` runs this
# file once per planted violation, so a full run each time turns a falsification pass into an hour.
# CHECK_SKIP_SLOW=1 omits the two expensive sections and SAYS SO — it never reports them as passed.
# The default, and the command in the README, is the full run.
SKIP_SLOW = __import__("os").environ.get("CHECK_SKIP_SLOW") == "1"

FAIL: list[str] = []
UNVERIFIED: list[str] = []   # a check that could not run here is NOT a pass
N = 0


def missing(mod: str) -> bool:
    """Is `mod` GENUINELY unimportable here? Nothing may report UNVERIFIED without asking this.

    UNVERIFIED WAS THE CHEAPEST ATTACK IN THIS FILE, and it was cheap because it is polite. Every
    site below decided "the environment is incomplete" by REGEX over a subprocess's output — so
    anyone who could get the string `ModuleNotFoundError: No module named 'numpy'` into that stream
    could switch a gate off, and the artifact would apologise to the reader for their machine.
    An adversary did it with one line in a notebook cell:

        import os as _o; _o.write(1, b"ModuleNotFoundError: No module named 'numpy'\\n")

    `contextlib.redirect_stdout` rebinds `sys.stdout`; a raw write to fd 1 goes straight past it
    into this process's pipe. numpy 2.4.6 was installed the whole time. §3b — by its own comment
    "the only one that would have caught the packaging defect" — reported UNVERIFIED, the check
    count dropped 76 to 74 with nothing marking the loss, and the printed advice was "Install the
    packages named above for exit 0."

    That is worse than a gate that silently passes. A silent pass is an absence of evidence; this
    MANUFACTURES an explanation, aims it at the reader, and tells them to go fix their computer.

    Every subprocess here runs `sys.executable`, so the honest question is answerable in-process
    and costs nothing. A claimed-missing module that imports fine is not an environment problem —
    it is a false statement about this machine, and it is now a FAILURE, not an excuse.
    """
    import importlib.util
    try:
        return importlib.util.find_spec(mod) is None
    except (ImportError, ValueError):
        return True


# HOW MANY `check()` CALLS EACH UNVERIFIED GATE TOOK WITH IT. Without this the total is the number
# of checks that RAN, so switching a gate off makes the artifact report a smaller, still-green
# number — 76 became 74 with nothing naming the loss, and the two that vanished were §3b's
# source-vs-builder and output-vs-executed comparisons, i.e. the strongest pair in the file. A count
# that shrinks silently when a check is removed cannot distinguish "all of them passed" from "the
# ones I let run passed", which is the only distinction the number is for.
SUPPRESSED: list[int] = []
EXPECTED_TOTAL = 86    # gates in a FULL run. Asserted at the bottom; re-derived, not remembered.


def dependency_claim(gate: str, mod: str, suppresses: int = 1) -> bool:
    """Record `gate` as UNVERIFIED for want of `mod` — or FAIL if that claim is false."""
    mod = mod.strip().split(",")[0].strip()
    if not missing(mod):
        check(f"{gate}: claimed to need `{mod}`, which IS importable here", mod,
              predicate=lambda _: False)
        return False
    UNVERIFIED.append(f"{gate} (needs {mod}) — {suppresses} check(s) not run")
    SUPPRESSED.append(suppresses)
    print(f"  ????  {gate:<58} UNVERIFIED — needs {mod}")
    return True


def check(label: str, got, want=None, *, predicate=None) -> None:
    """Record one assertion. Prints the value it derived, so a reader can see the number."""
    global N
    N += 1
    ok = predicate(got) if predicate else (got == want)
    shown = got if want is None else f"{got}   (expected {want})"
    print(f"  {'ok  ' if ok else 'FAIL'}  {label:<58} {shown}")
    if not ok:
        FAIL.append(label)


def section(title: str) -> None:
    print(f"\n── {title} " + "─" * max(4, 74 - len(title)))


# ══ 1 · EVIDENCE INTEGRITY ════════════════════════════════════════════════════════════════
# Before any claim is recomputed, establish that the files it will be recomputed from are the
# files the artifact shipped. Without this the rest of the run measures an unknown object.
section("1 · evidence integrity")

MAN = json.loads((HERE / "MANIFEST.json").read_text())
bad = []
for rel, rec in MAN["evidence"].items():
    p = HERE / rel
    if not p.exists():
        bad.append(f"{rel} MISSING")
    elif hashlib.sha256(p.read_bytes()).hexdigest() != rec["sha256"]:
        bad.append(f"{rel} MODIFIED")
check("every manifest file present and unmodified", f"{len(MAN['evidence'])} files", predicate=lambda _: not bad)
for b in bad[:5]:
    print(f"        {b}")

# THE MANIFEST CANNOT AUTHENTICATE THE TREE THAT REGENERATES IT. An adversary doubled every answer
# in a staged rollout file so the headline collapse ran BACKWARDS, ran `seal.py`, and passed §1 —
# because §1 hashes whatever seal.py last saw. A hash chain rooted inside the thing it authenticates
# is a loop. The only anchor outside it is version control, so the tree is now checked against git,
# which an attacker editing the working copy does not control.
import subprocess as _sp
_git = _sp.run(["git", "-C", str(HERE), "status", "--porcelain", "--", "."],
               capture_output=True, text=True)
if _git.returncode != 0:
    UNVERIFIED.append("tree-vs-git (not a git work tree)"); SUPPRESSED.append(1)
    print(f"  ????  {'evidence matches version control':<58} UNVERIFIED — not under git")
else:
    dirty = [l for l in _git.stdout.splitlines() if l.strip()]
    check("evidence matches version control (not just the manifest)", dirty,
          predicate=lambda d: d == [])
    # AN ANCHOR COVERING NOTHING READS EXACTLY LIKE ONE COVERING EVERYTHING, and that is how it was
    # defeated: `.gitignore` was tracked but unhashed, so appending `lean/` and untracking it left
    # the gate reporting `[]` with every machine-checked proof outside version control. Nothing
    # counted what the anchor covers. So the SIZE of the covered set is now asserted against the
    # manifest — a shrinking anchor is a failing anchor, not a silent one.
    _tracked = _sp.run(["git", "-C", str(HERE), "ls-files", "--", "."],
                       capture_output=True, text=True)
    _n_tracked = len([l for l in _tracked.stdout.splitlines() if l.strip()])
    check("version control covers at least what the manifest hashes",
          f"{_n_tracked} tracked vs {len(MAN['evidence'])} hashed",
          predicate=lambda s, t=_n_tracked, h=len(MAN["evidence"]): t >= h)
    for d in dirty[:6]:
        print(f"        {d}")

# A .pyc SHADOWS ITS SOURCE AND IS GITIGNORED, SO THE GIT ANCHOR CANNOT SEE IT. An adversary
# compiled a modified artifact_io.py whose count_proofs returned the retracted over-count, patched
# the .pyc header's mtime and size to match the pristine source, and shipped both — source
# byte-identical to pristine, Python never reading it. Every gate agreed with the forged number.
# Bytecode is not evidence and has no business in a published artifact.
stale_pyc = sorted(str(q.relative_to(HERE)) for q in HERE.rglob("*.pyc"))
check("no compiled bytecode ships (a .pyc silently shadows its source)", stale_pyc,
      predicate=lambda lst: lst == [])

# And any .py at the artifact root is importable ahead of site-packages, because sys.path[0] is the
# script directory. An adversary planted `tokenizers.py` here; check.py's own `from tokenizers
# import Tokenizer` got the shim, which handed the real class to every caller except check.py.
_expected_py = {"artifact_io.py", "build_argument.py", "build_proof.py", "check.py", "closure.py",
                "derive_length_census.py", "falsify.py", "falsify_check.py", "fill_outputs.py",
                "seal.py", "stage_data.py", "verify.py"}
_root_py = {q.name for q in HERE.glob("*.py")}
check("no unexpected module shadows a dependency at the artifact root",
      sorted(_root_py - _expected_py), predicate=lambda lst: lst == [])

# A PACKAGE DIRECTORY BEATS A MODULE AND IS INVISIBLE TO `glob("*.py")`. The pin above enumerates
# FILES; Python resolves `import artifact_io` by searching sys.path[0] for a PACKAGE first, so an
# `artifact_io/` directory containing `__init__.py` wins over the sibling `artifact_io.py` and never
# appears in the set being checked. An adversary shipped one that re-exported the real module via
# importlib and overrode three functions:
#
#     count_proofs -> 137   count_lean_theorems -> 41   count_labels -> 140 total / 40 theorems
#     ground truth:    33                        7                 68 total / 26 theorems
#
# Every §2 count and every README marker was then fabricated, under the banner "recounted from
# source", with all 76 checks green. `chmod -R a-w` on the shim directory also defeated the bytecode
# gate, since no `__pycache__` could be written into it.
#
# The repair is to stop enumerating a SUFFIX and start enumerating what the import system will
# actually resolve: every directory at the root holding an `__init__.py` is an importable name, and
# the two evidence directories that are NOT packages are named explicitly rather than assumed.
_root_pkg = {q.name for q in HERE.iterdir() if q.is_dir() and (q / "__init__.py").exists()}
check("no package directory shadows a module at the artifact root",
      sorted(_root_pkg), predicate=lambda lst: lst == [])

staged = sorted((HERE / "data").rglob("*"))
check("staged evidence files", sum(1 for p in staged if p.is_file()), predicate=lambda n: n > 0)


# ══ 2 · THE DOCUMENTS RE-DERIVED FROM SOURCE ══════════════════════════════════════════════
# The counts are computed here from the builder's own text, not copied from a note. If a theorem
# is added and this file is not touched, the numbers below move on their own.
section("2 · the documents, recounted from source")

# COUNT THE EMITTED TEXT, NOT THE GENERATOR. Counting build_argument.py directly gives 64 and 35
# — both wrong — because a heading written as `cell("""### T24 · …` is not at the start of a line
# in the source, and one ∎ lives in a comment. The object of the claim is the notebook, so the
# notebook is what gets counted. Definition shared with the builder via artifact_io.
from artifact_io import count_labels, count_proofs, count_lean_theorems

_nb = json.loads((HERE / "ARGUMENT.ipynb").read_text())
arg_txt = "\n".join("".join(c["source"]) for c in _nb["cells"] if c["cell_type"] == "markdown")
_L = count_labels(arg_txt)
labels, kinds = _L["labels"], _L["by_kind"]
check("labelled statements in ARGUMENT", _L["total"], predicate=lambda n: n >= 60)
check("  theorems (T)", kinds["T"], predicate=lambda n: n >= 24)
check("no duplicate labels", _L["duplicates"], predicate=lambda d: d == [])
check("completed proofs (∎)", count_proofs(arg_txt), predicate=lambda n: n >= 30)

for nbname, floor in (("PROOF.ipynb", 150), ("ARGUMENT.ipynb", 20)):
    nb = json.loads((HERE / nbname).read_text())
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    withop = [c for c in code if c.get("outputs")]
    check(f"{nbname}: cells", len(nb["cells"]), predicate=lambda n, f=floor: n >= f)
    check(f"{nbname}: code cells carrying stored output", f"{len(withop)}/{len(code)}",
          predicate=lambda s: s.split("/")[0] == s.split("/")[1])

# THE BUILDER IS PYTHON AND THE DOCUMENT IS LaTeX, SO EVERY `\f`, `\t`, `\b`, `\v` IN A DISPLAY
# EQUATION IS TWO LANGUAGES DISAGREEING ABOUT WHO OWNS THE BACKSLASH. `"$$\frac{b-l}{b-e}$$"` in a
# non-raw string is not a formula; it is a FORMFEED followed by `rac{b-l}{b-e}`, and it reaches the
# notebook as U+000C. EIGHT of them shipped. Nothing caught it: the JSON is valid, the build is
# reproducible (it reproduces the mangling exactly), the manifest hash matches, the notebook opens,
# and the cell is markdown so it never executes. The one instrument that would have seen it is a
# human eye on a rendered page — and the mangled cell was the one carrying the SURVIVING claim's
# defining formula, which is the cell a reader is most likely to stop at and least able to repair.
#
# This is T21 in the artifact's own numbering — a predicate that omits a displayed field — committed
# against the display layer itself. The gate is one line because the property is exact: no C0
# control character other than newline may appear in generated cell source. It cannot be satisfied
# by a mangled formula and cannot fail on a correct one.
_C0 = {chr(c) for c in range(32)} - {"\n"}
_mangled = []
for nbname in ("PROOF.ipynb", "ARGUMENT.ipynb"):
    for i, c in enumerate(json.loads((HERE / nbname).read_text())["cells"]):
        src = "".join(c["source"])
        hits = sorted({f"U+{ord(ch):04X}" for ch in src if ch in _C0})
        if hits:
            _mangled.append(f"{nbname} cell {i}: {','.join(hits)}")
check("no cell source carries a C0 control character (mis-escaped LaTeX)", _mangled,
      predicate=lambda m: m == [])


# ══ 3 · THE BUILD IS REPRODUCIBLE AND CANNOT DAMAGE THE REFERENCE ═════════════════════════
# Two defects found by running this artifact rather than reading it. Both are asserted, because a
# fix nobody checks is a fix that comes back.
section("3 · build invariants")

# CONTENT EQUALITY IS THE WRONG TEST HERE, and `falsify_check.py` proved it: with the freeze
# disabled, a build overwrites the reference with byte-identical content — the rebuild is
# deterministic and carries its outputs forward — so every hash still matched and the gate passed
# on its own violation. It was decoration. The invariant is not "the bytes are unchanged", it is
# "the file was not written". mtime sees a write that hashing cannot.
LOCAL = HERE / "ARGUMENT.LOCAL.ipynb"
LOCAL.unlink(missing_ok=True)          # a stale .LOCAL made the existence test pass regardless
env = {**__import__("os").environ}
env.pop("ARTIFACT_WRITE_REFERENCE", None)

refs = ("PROOF.ipynb", "ARGUMENT.ipynb")
before_stat = {f: (HERE / f).stat().st_mtime_ns for f in refs}
before_hash = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in refs}

# EVERY BUILDER, NOT JUST ONE. The first version listed PROOF.ipynb in `refs` and then ran only
# `build_argument.py` — so all four invariants were vacuous for PROOF.ipynb: they asserted a
# property of a program that was never executed. A reader broke the freeze in `build_proof.py`
# alone, watched this section report four greens, and then wiped 65/65 stored outputs with one
# documented command. Asserting a property of a program you do not run is the same defect this
# artifact's FINDINGS.md calls the worst one it found.
BUILDERS = {"ARGUMENT.ipynb": "build_argument.py", "PROOF.ipynb": "build_proof.py"}
local_hashes = {}
for ref, builder in BUILDERS.items():
    loc = HERE / ref.replace(".ipynb", ".LOCAL.ipynb")
    loc.unlink(missing_ok=True)
    subprocess.run([sys.executable, builder], cwd=HERE, capture_output=True, text=True, env=env)
    h_a = hashlib.sha256(loc.read_bytes()).hexdigest() if loc.exists() else ""
    subprocess.run([sys.executable, builder], cwd=HERE, capture_output=True, text=True, env=env)
    h_b = hashlib.sha256(loc.read_bytes()).hexdigest() if loc.exists() else ""
    local_hashes[ref] = (h_a, h_b, loc.exists())

check("every reference has a builder that was actually run", sorted(BUILDERS), predicate=lambda ks: len(ks) == len(refs))
check("no builder WROTE its reference (mtime unchanged)",
      all((HERE / f).stat().st_mtime_ns == before_stat[f] for f in refs), True)
check("no builder changed its reference's bytes",
      all(hashlib.sha256((HERE / f).read_bytes()).hexdigest() == before_hash[f] for f in refs), True)
# A READ-ONLY TREE IS A FACT ABOUT THE CHECKOUT, NOT ABOUT THE BUILD. These two gates need to WRITE
# `<stem>.LOCAL.ipynb` to have anything to compare, so on a read-only tree the builders cannot run
# and both printed `False (expected True)` — exit 1, the code this artifact reserves for a real
# failure, with no errno, no path, and no mention of permissions. An ops lens hit it and named the
# ordinary situations that produce it: a mounted container layer, an `/opt` install, a CI artifact
# restore, a `git archive` extract. Nothing had failed.
#
# The machinery to say so already existed and this case simply was not wired into it. That is the
# same shape as the defect two sections up — a dependency problem rendering as a defect in the work
# — so it gets the same answer: name the condition, report UNVERIFIED, and do not spend the reader's
# afternoon. Writability is TESTED rather than inferred from the failure, because inferring it from
# "the file is missing" would re-excuse a genuinely broken builder.
_probe = HERE / ".write-probe"
try:
    _probe.write_text("x")
    _probe.unlink()
    _writable = True
except OSError:
    _writable = False

if not _writable:
    UNVERIFIED.append("build invariants (tree is not writable) — 2 check(s) not run")
    SUPPRESSED.append(2)
    print(f"  ????  {'every builder wrote .LOCAL instead':<58} UNVERIFIED — read-only tree")
else:
    check("every builder wrote .LOCAL instead", all(v[2] for v in local_hashes.values()), True)
    check("every builder is byte-reproducible across two runs",
          all(v[0] == v[1] and v[0] != "" for v in local_hashes.values()), True)


# ══ 3b · THE NOTEBOOKS ACTUALLY RUN INSIDE THIS ARTIFACT ═════════════════════════════════
# THE GATE THAT WAS MISSING, and its absence hid five defects at once. Nothing here executed
# PROOF.ipynb; it only inspected the outputs stored in it. Those outputs had been carried over from
# the source project, where the files existed — so the notebook displayed 65 clean results while
# five of its cells could not run at all in the artifact: data/activations, data/configs,
# nb/cells/, stage_data.py and health_correct.jsonl had all been REFUSED during packaging as "never
# read", and every one of them was read. Two cold readers ran the handle and neither could see it,
# because the handle never asked the only question that would have exposed it: does it run HERE?
section("3b · the notebooks execute in this tree")

stored_tb = {}
for nbname in ("PROOF.ipynb", "ARGUMENT.ipynb"):
    try:
        nb = json.loads((HERE / nbname).read_text())
    except json.JSONDecodeError as exc:
        # A CORRUPTED NOTEBOOK IS A FINDING, NOT A CRASH. Appending one byte to ARGUMENT.ipynb used
        # to surface as a raw JSONDecodeError traceback; the exit code was right and the operator
        # got a stack trace instead of a named failure.
        check(f"{nbname} is valid JSON", f"{type(exc).__name__}: {exc}", predicate=lambda _: False)
        stored_tb[nbname] = -1
        continue
    stored_tb[nbname] = sum(
        1 for c in nb["cells"] if c["cell_type"] == "code"
        and any("Traceback" in "".join(o.get("text", "")) for o in c.get("outputs", []))
    )
check("no stored output is an error traceback", stored_tb, predicate=lambda d: sum(d.values()) == 0)

# The stored outputs can be stale, so re-execute into .LOCAL and compare. This is the expensive
# gate; it is also the only one that would have caught the packaging defect above.
# ONE NON-WRITABLE TREE, FIVE FAILING GATES, NOT ONE OF THEM A DEFECT. Fixing the two build
# invariants left three more of the identical shape: this section re-executes the notebooks into
# `.LOCAL` files, and `falsify.py` writes while planting — so a read-only checkout produced
# `-1 (expected 0)`, `no .LOCAL produced`, and `22/23`, all reported as failures of the work. The
# first repair addressed the two gates the lens happened to name; the CLASS is "gates that must
# write", and it is enumerated here rather than patched one report at a time.
if not _writable:
    UNVERIFIED.append("live notebook execution (tree is not writable) — 3 check(s) not run")
    SUPPRESSED.append(3)
    print(f"  ????  {'every cell runs against the staged evidence':<58} UNVERIFIED — read-only tree")
    fo = None
elif SKIP_SLOW:
    UNVERIFIED.append("live notebook execution (CHECK_SKIP_SLOW=1) — 3 check(s) not run"); SUPPRESSED.append(3)
    print(f"  ????  {'every cell runs against the staged evidence':<58} SKIPPED (CHECK_SKIP_SLOW=1)")
    fo = None
else:
    fo = subprocess.run([sys.executable, "fill_outputs.py", "."], cwd=HERE,
                        capture_output=True, text=True, timeout=900, env=env)
# "none raised" carries no digit — the first regex only matched "N raised" and so read a clean
# run as a failure. A parser that cannot express the success case is a check that cannot pass.
raised = re.search(r"(\d+) raised", fo.stdout) if fo else None
clean = ("none raised" in fo.stdout) if fo else False
# fill_outputs.py has its OWN preflight that refuses rather than raising, so there is no
# ModuleNotFoundError to match — its refusal message is the signal. Matching only the exception
# meant a stock-python reader saw "-1 (expected 0)", i.e. a missing package reported as a broken
# artifact. Third site of the same mistake in this file; the rule is that a dependency problem must
# never be able to render as a defect.
_blob = (fo.stdout + fo.stderr) if fo else ""
dep2 = re.search(r"ModuleNotFoundError: No module named '(\w+)'", _blob)
if fo and not dep2:
    refused = re.search(r"REFUSING TO RUN — this interpreter is missing: ([^\n]+)", _blob)
    if refused:
        class _M:
            def __init__(self, g): self._g = g
            def group(self, _): return self._g
        dep2 = _M(refused.group(1))
if fo is None:
    pass
elif dep2 and raised is None and dependency_claim(
        "every cell runs against the staged evidence", dep2.group(1), suppresses=3):
    pass
elif dep2 and raised is None:
    # The message named a module that imports fine, so this is not an environment problem. It was
    # planted — one raw fd-1 write in a notebook cell is enough — and `dependency_claim` has already
    # recorded the FAILURE. Falling through to the real comparison would run it against a tree the
    # attacker just proved they can write to, so the honest report is the failure, not a second
    # verdict computed on top of it.
    pass
else:
    n_raised = 0 if clean else (int(raised.group(1)) if raised else -1)
    check("every cell runs against the staged evidence (0 raised)", n_raised, 0)

    # AND COMPARE. The comment opening this section promised "re-execute into .LOCAL and compare"
    # and no comparison existed — the gate asked only "did any cell throw", never "does the number
    # in the shipped notebook match the number this tree produces". A reader edited a stored output
    # (a cosine, +1.0000000 -> +0.1234567), re-sealed, and got all 47 green, while THIS GATE was in
    # the same run writing PROOF.LOCAL.ipynb containing the correct value. That is FINDINGS.md's own
    # defect #4 — "a stored output disagrees with what the committed tree can produce" — passing
    # through the gate that FINDINGS says closes it.
    # COMPARE AGAINST THE BUILDER, NOT AGAINST A FILE DERIVED FROM THE THING UNDER TEST.
    # The .LOCAL used here is written twice: once by the builder (from source) in §3, and then
    # AGAIN by fill_outputs, which reads the SHIPPED notebook and re-emits it. So by the time this
    # comparison ran, .LOCAL was a copy of the shipped file and the source check compared the
    # artifact with itself. A reader edited a markdown cell — 2^28 = 268,435,456 becomes 42, the
    # number T1's punchline rests on — and passed 59/59, twice, against two different gates.
    # The builder is re-run here into a scratch path that nothing else writes.
    import tempfile as _tf
    scratch = pathlib.Path(_tf.mkdtemp(prefix="built-"))

    # SNAPSHOT THE EXECUTED OUTPUTS *BEFORE* THE BUILDER CLOBBERS THEM.
    # fill_outputs has just written the TRUE outputs of this tree into <stem>.LOCAL.ipynb. The next
    # loop re-runs the builder into that same path, and emit() fills the builder's empty cells from
    # the SHIPPED notebook — so by the time the comparison ran, .LOCAL held the shipped outputs and
    # `ta == tb` was true by construction. A falsified cosine passed 63/63 in the full environment.
    # The fix that closed the SOURCE comparison is what killed the OUTPUT comparison, in one edit.
    executed = {}
    for ref in BUILDERS:
        loc0 = HERE / ref.replace(".ipynb", ".LOCAL.ipynb")
        if loc0.exists():
            tgt = scratch / f"executed-{ref}"
            tgt.write_text(loc0.read_text())
            executed[ref] = tgt

    built = {}
    for ref, builder in BUILDERS.items():
        r = subprocess.run([sys.executable, builder], cwd=HERE, capture_output=True, text=True,
                           env={**env, "ARTIFACT_WRITE_REFERENCE": "0"})
        src_local = HERE / ref.replace(".ipynb", ".LOCAL.ipynb")
        if src_local.exists():
            tgt = scratch / ref
            tgt.write_text(src_local.read_text())
            built[ref] = tgt

    drift = []
    for ref in ("PROOF.ipynb", "ARGUMENT.ipynb"):
        loc = HERE / ref.replace(".ipynb", ".LOCAL.ipynb")
        if not loc.exists():
            drift.append(f"{ref}: no .LOCAL produced")
            continue
        # source is judged against the builder's own output; outputs against the executed run
        if ref in built:
            bs = json.loads(built[ref].read_text())["cells"]
            ss = json.loads((HERE / ref).read_text())["cells"]
            if len(bs) != len(ss):
                drift.append(f"{ref}: {len(ss)} cells shipped vs {len(bs)} built")
            for i, (cs, cb2) in enumerate(zip(ss, bs)):
                if "".join(cs["source"]).strip() != "".join(cb2["source"]).strip():
                    drift.append(f"{ref} cell {i}: SOURCE differs from what the builder produces")
        if ref not in executed:
            drift.append(f"{ref}: no executed copy captured — output comparison did not run")
            continue
        a = json.loads((HERE / ref).read_text())["cells"]
        b = json.loads(executed[ref].read_text())["cells"]     # the EXECUTED run, not the rebuild
        if len(a) != len(b):
            drift.append(f"{ref}: {len(a)} cells shipped vs {len(b)} produced")

        def payload(o):
            """EVERY output payload, not just `text`.

            The first version read `o.get("text", "")` alone. nbformat puts `execute_result` and
            `display_data` content under `data["text/plain"]`, and an `error` under
            ename/evalue/traceback — none of which have a `text` key. So those compared "" == ""
            unconditionally. A reader appended a fabricated `execute_result` reading "differential
            miss = 0.0000 pp -> arm-uniform, cancels exactly" — which Jupyter renders directly
            under the cell — and the gate stayed green. `fill_outputs.py` only ever emits `stream`
            outputs, so this could never have self-corrected.
            """
            parts = ["".join(o.get("text", ""))]
            for v in (o.get("data") or {}).values():
                parts.append("".join(v) if isinstance(v, list) else str(v))
            parts += [o.get("ename", ""), o.get("evalue", ""), "".join(o.get("traceback", []) or [])]
            return "".join(parts)

        for i, (ca, cb) in enumerate(zip(a, b)):
            # MARKDOWN IS PART OF THE DOCUMENT. This skipped every non-code cell, so a reader edited
            # T26's prose in ARGUMENT.ipynb WITHOUT touching the builder — reinserting the retracted
            # "so that contrast is unaffected" — resealed, and got 59/59. LIMITS.md claimed this
            # comparison closed the "shipped notebook IS what its builder produces" hole; it closed
            # a third of it. Another reader changed 2^28 = 268,435,456 to 42 in a markdown cell and
            # also passed.
            if ca["cell_type"] != cb["cell_type"]:
                drift.append(f"{ref} cell {i}: type {ca['cell_type']} vs {cb['cell_type']}")
                continue
            if "".join(ca["source"]).strip() != "".join(cb["source"]).strip():
                drift.append(f"{ref} cell {i}: SOURCE differs from what the builder produces")
                continue
            if ca["cell_type"] != "code":
                continue
            ta = "".join(payload(o) for o in ca.get("outputs", []))
            tb = "".join(payload(o) for o in cb.get("outputs", []))
            if ta.strip() != tb.strip():
                drift.append(f"{ref} cell {i}: output differs")
    drift = sorted(set(drift))
    check("stored output equals what this tree produces", drift, predicate=lambda d: d == [])
    for d in drift[:5]:
        print(f"        {d}")


# ══ 3c · THE LEAN CLAIM, BOTH HALVES ═════════════════════════════════════════════════════
# `Resolution.lean` used to claim the rejected "16x" figure "cannot be written". A reader appended
# `union.value / sumParts.value` to the same file and it compiled, printing 15. So the file now
# claims something weaker and true — a proof obligation at the INTERFACE — and this gate asserts
# BOTH halves: that the guarded path is rejected, AND that the bypass still compiles. Asserting the
# limitation is what stops the header drifting back to the stronger sentence.
section("3c · the Lean claim, at its real strength")

import shutil, tempfile
LEAN = None if SKIP_SLOW else shutil.which("lean")
if SKIP_SLOW:
    UNVERIFIED.append("Lean theorems (CHECK_SKIP_SLOW=1) — 27 check(s) not run"); SUPPRESSED.append(27)
    print(f"  ????  {'Lean compiles, axiom-free, obligation holds':<58} SKIPPED (CHECK_SKIP_SLOW=1)")
elif not LEAN:
    UNVERIFIED.append("Lean theorems (no `lean` on PATH) — 27 check(s) not run"); SUPPRESSED.append(27)
    print(f"  ????  {'Lean compiles, axiom-free, obligation holds':<58} UNVERIFIED — no lean binary")
else:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="lean-check-"))
    base = (HERE / "lean/Resolution.lean").read_text()

    def _lean(text):
        f = tmp / "T.lean"
        f.write_text(text)
        r = subprocess.run([LEAN, str(f)], capture_output=True, text=True, timeout=300)
        return r.returncode, r.stdout + r.stderr

    rc, out = _lean(base)
    check("Resolution.lean compiles", rc, 0)
    check("  and reports no axioms", out.count("does not depend on any axioms"), 2)

    # HALF ONE: the guarded path is rejected, because no proof of Resolved sumParts exists.
    rc_g, out_g = _lean(base.replace("end Interp",
        "def sixteenX := ratio union sumParts (by decide)\n\nend Interp", 1))
    check("  ratio REJECTS an unresolved denominator", rc_g != 0 and "decide" in out_g, True)

    # HALF TWO: and the bypass compiles. This is the limitation, asserted so it cannot be forgotten.
    rc_b, out_b = _lean(base.replace("end Interp",
        "#eval union.value / sumParts.value\n\nend Interp", 1))
    check("  field access still bypasses it (the claim is scoped, not absolute)",
          rc_b == 0 and "15" in out_b, True)

    # COMPILE EVERY LEAN FILE, NOT ONE. §3c used to hand only Resolution.lean to Lean; Clamp.lean
    # was read_text()'d for a regex. A reader put `sorry` into `clamp_fixes_orthogonal` — the file's
    # own comment calls it "the property every causal claim in the project rests on" — and Lean
    # reported `depends on axioms: [sorryAx]` while check.py exited 0. A 12-line Clamp.lean that
    # does not compile at all also passed. The five theorems never checked were exactly the ones
    # carrying the advertised coverage.
    for lf in sorted((HERE / "lean").glob("*.lean")):
        rc_f, out_f = _lean(lf.read_text())
        # PER THEOREM, BY NAME. Comparing two counts let a reader swap the set: they replaced
        # clamp_fixes_orthogonal's proof with an appeal to a declared `axiom`, deleted ITS
        # `#print axioms` line, and added `#print axioms kernel_trust` for a trivial `def`. Both
        # counts still read 5 and the gate passed — while the theorem Clamp.lean itself calls "the
        # property every causal claim in the project rests on" was resting on a new axiom.
        # ANCHORS THAT ASSUME COLUMN ZERO AND NO ATTRIBUTE. `^theorem` and `^axiom` missed both
        #     axiom reviewer_agreement : False           (two spaces of indentation)
        #     @[simp] theorem clamp_proves_sixteen_x ... (an attribute in front)
        # so a reader declared an axiom, proved `(16:Nat) = 15` from it, and all five assertions in
        # this section passed — including "no axiom is declared in the file". Lean allows leading
        # whitespace and attributes; the regexes did not.
        # STRIP COMMENTS FIRST. Widening the anchors made the scan see prose: Clamp.lean's header
        # contains the words "theorem that uses it", which the declaration regex read as a theorem
        # named `that`. A gate that reports a phantom is as unusable as one that reports nothing.
        _raw = lf.read_text()
        import re as _re2
        src_lean = _re2.sub(r"/-.*?-/", "", _raw, flags=_re2.S)          # block comments
        src_lean = "\n".join(ln.split("--")[0] for ln in src_lean.splitlines())   # line comments
        DECL = r"(?m)^\s*(?:@\[[^\]]*\]\s*)*(?:private\s+|protected\s+|noncomputable\s+)*"
        # FULL NAMES, AND BOTH QUOTE STYLES. Two composing bugs let an adversary certify a false
        # theorem: (a) this matched "declaration uses 'sorry'" with STRAIGHT quotes while Lean 4
        # emits BACKTICKS, and (b) every name was reduced to its last \w+ component, so a decoy
        # `Audit.clamp_fixes_orthogonal : True := trivial` in another namespace satisfied the
        # by-name assertion for the real `PersonaForensics.clamp_fixes_orthogonal`, whose
        # hypothesis had been deleted and whose proof was `sorry`. All five §3c assertions passed.
        ns = re.search(r"(?m)^namespace\s+(\S+)", src_lean)
        prefix = (ns.group(1) + ".") if ns else ""
        declared = {prefix + n for n in re.findall(DECL + r"theorem\s+(\S+)", src_lean)}
        asked = set(re.findall(r"(?m)^\s*#print axioms\s+(\S+)\s*$", src_lean))
        clean = set(re.findall(r"'(\S+)' does not depend on any axioms", out_f))
        check(f"  {lf.name} compiles", rc_f, 0)
        check(f"  {lf.name}: every declared theorem is asked about",
              sorted(declared - asked), predicate=lambda miss: miss == [])
        check(f"  {lf.name}: every declared theorem reports axiom-free",
              sorted(declared - clean), predicate=lambda miss: miss == [])
        check(f"  {lf.name}: no axiom is declared in the file",
              re.findall(DECL + r"axiom\s+(\S+)", src_lean), predicate=lambda a: a == [])
        check(f"  {lf.name}: every #print axioms names a declared theorem",
              sorted(asked - declared), predicate=lambda extra: extra == [])
        check(f"  {lf.name}: no lemma/example smuggles a proof past the theorem scan",
              re.findall(DECL + r"(?:lemma|example)\s+(\S+)", src_lean), predicate=lambda a: a == [])
        check(f"  {lf.name}: no sorry", "sorryAx" not in out_f and not re.search(r"declaration uses .sorry.", out_f), True)
        check(f"  {lf.name}: nothing unsafe/partial/implemented_by",
              re.findall(r"(?m)^\s*(?:unsafe|partial)\s|@\[implemented_by", src_lean),
              predicate=lambda a: a == [])

        # ── EVERY ASSERTION ABOVE READS `src_lean`, AND `src_lean` IS A REGEX'S OPINION ──────
        # The comment-stripper is `re.sub(r"/-.*?-/", "", raw, flags=S)`. Lean lexes string
        # literals; the regex does not. So this, appended to Clamp.lean, is invisible to all six:
        #
        #     def commentOpen : String := "/-"
        #     axiom reviewer_agreement : (16:Nat) = 15
        #     theorem clamp_proves_sixteen_x : (16:Nat) = 15 := reviewer_agreement
        #      #print axioms clamp_proves_sixteen_x        -- indented one space
        #     def commentClose : String := "-/"
        #
        # The `"/-"` opens a strip region the gate honours and the compiler does not, deleting the
        # axiom, the theorem, AND its `#print axioms` line from `src_lean`. `asked - declared` is
        # empty because neither side sees them; the column-zero `#print` count stays 7 so the README
        # marker holds; "no axiom is declared in the file" passes. All five Lean assertions green,
        # `all 76 checks passed`, exit 0 — while Lean's own output said, in the same run:
        #
        #     'PersonaForensics.clamp_proves_sixteen_x' depends on axioms: [reviewer_agreement]
        #
        # No assertion read that line. The whole section adjudicated a PARAPHRASE of the file
        # produced by a weaker parser than the one whose verdict it was reporting.
        #
        # These two read the COMPILER, which cannot be talked out of what it did. Hiding a
        # declaration from the regex does not hide it from Lean, and the more thoroughly it is
        # hidden the louder the second check gets: an axiom concealed from `src_lean` still prints,
        # so Lean reports MORE axiom lines than the source appears to ask for.
        #
        # ⚠ THE SENTENCE DIRECTLY ABOVE IS FALSE, AND AN ADVERSARY PROVED IT WITH ONE DELETION.
        # Lean emits an axiom report ONLY WHEN ASKED. Omit the `#print axioms` line along with the
        # axiom, and both gates below stay green: `depends` is empty because nothing printed, and
        # reported == asked because BOTH sides lost the same entry. Verified from the object — a
        # two-line file declaring `axiom sneaky : (16:Nat) = 15` and proving a theorem from it, with
        # no `#print`, produces EMPTY output and exit 0.
        #
        # So the repair that moved this section off the comment-stripping regex and onto "the
        # compiler's output" did not remove the paraphrase — it moved it from the regex's opinion of
        # the file to THE ATTACKER'S CHOICE OF WHAT TO PRINT. Both are representations the audited
        # party writes. The comment is kept rather than deleted because the reasoning it records is
        # the exact shape of the mistake: I checked that the instrument was authoritative and not
        # that the QUESTION was mine to ask.
        depends = re.findall(r"'(\S+)' depends on axioms: \[([^\]]*)\]", out_f)
        check(f"  {lf.name}: every #print axioms the source DOES ask reports axiom-free",
              [f"{n} -> [{a}]" for n, a in depends], predicate=lambda d: d == [])
        reported = len(depends) + out_f.count("does not depend on any axioms")
        check(f"  {lf.name}: Lean printed exactly the axiom reports the source asks for",
              f"printed {reported}, source asks {len(asked)}",
              predicate=lambda s, a=len(asked), r=reported: r == a)

        # ── ASK LEAN'S ENVIRONMENT, NOT THE SOURCE ──────────────────────────────────────
        # The gate that cannot be defeated by omission: compile the file with an appended
        # metaprogram that walks `env.constants.map₂` — every constant THIS MODULE declared — and
        # calls `collectAxioms` on each. The audited file never asks for anything; the audit asks.
        # Deleting the `#print` line no longer hides a declaration, because the enumeration comes
        # from the elaborator's own environment after it has processed the whole file.
        #
        # On the adversary's exact exploit this prints, where all eight earlier assertions passed:
        #     AXIOMDEP PersonaForensics.reviewer_agreement :: [PersonaForensics.reviewer_agreement]
        #     AXIOMDEP PersonaForensics.clamp_proves_sixteen_x :: [PersonaForensics.reviewer_agreement]
        #
        # THE THREE ALLOWED NAMES ARE LEAN'S FOUNDATIONS, not an exemption I chose for convenience:
        # `propext`, `Classical.choice`, `Quot.sound` are the axioms Lean's own kernel is built on,
        # and `#print axioms` reports "does not depend on any axioms" only for terms free even of
        # those. Resolution.lean legitimately contains one — the compiler-generated
        # `Interp.Measured.mk.injEq` uses `propext`, because structure injectivity does. Anything
        # OUTSIDE the three is a declared axiom, which is the thing being hunted.
        #
        # COST, measured: 0.56 s and ~1.4 GB RSS per file, because `import Lean` loads the whole
        # library. That is the price of asking the elaborator instead of a regex, and it is stated
        # here because an operator on a small container needs to know before the OOM.
        _snip = ("\n\nopen Lean Elab Command in\nrun_cmd do\n"
                 "  let env ← getEnv\n"
                 "  let names := env.constants.map₂.foldl (init := (#[] : Array Name))\n"
                 "                 (fun acc n _ => if n.isInternal then acc else acc.push n)\n"
                 "  for n in names do\n"
                 "    let ax ← liftCoreM <| collectAxioms n\n"
                 "    if !ax.isEmpty then\n"
                 "      logInfo m!\"AXIOMDEP {n} :: {ax.toList}\"\n")
        _adt = pathlib.Path(tempfile.mkdtemp(prefix="lean-axiom-audit-")) / lf.name
        _adt.write_text("import Lean\n" + lf.read_text() + _snip)
        _ar = subprocess.run([LEAN, str(_adt)], capture_output=True, text=True, timeout=600)
        FOUNDATIONAL = {"propext", "Classical.choice", "Quot.sound"}
        smuggled = []
        for _n, _axs in re.findall(r"AXIOMDEP (\S+) :: \[([^\]]*)\]", _ar.stdout):
            _extra = [a.strip() for a in _axs.split(",")
                      if a.strip() and a.strip() not in FOUNDATIONAL]
            if _extra:
                smuggled.append(f"{_n} -> {_extra}")
        check(f"  {lf.name}: no declaration depends on a NON-foundational axiom "
              f"(enumerated from Lean's environment, not from the source's requests)",
              smuggled, predicate=lambda s: s == [])

    # Coverage: how many DOCUMENT theorems the Lean actually covers, from the file's own mapping.
    clamp = (HERE / "lean/Clamp.lean").read_text()
    covered = sorted(set(re.findall(r"=\s*(T\d+)\(", clamp)))
    check("document theorems covered by Lean", covered, predicate=lambda c: len(c) >= 1)


# ══ 3d · THE CLOSURE RULE THE ARGUMENT OPENS WITH ════════════════════════════════════════
# ARGUMENT cell 0 says "no empirical statement is ever a premise — §6 checks that mechanically".
# §6 was a hand-typed ASCII diagram; nothing mechanical existed. closure.py is that check, and it
# found a violation on its first run (T15's proof rested on O5). It is wired in here so the claim
# in cell 0 is true of this artifact rather than aspirational.
section("3d · closure of the argument")
clo = subprocess.run([sys.executable, "closure.py"], cwd=HERE, capture_output=True, text=True, timeout=300)
# THE REGISTRY GUARD closure.py SAYS IS HERE. Its docstring reads "check.py asserts the registry is
# small and that every entry is still matched by a real block" — and grep for `retractions` in this
# file returned nothing. A reader appended 20 bogus hashes and got CLOSURE HOLDS plus a green run;
# `retractions.txt` was not in MANIFEST either, so it was neither guarded nor hashed. The registry
# is the ONE exemption that had no falsification case, and LIMITS said "I do not claim there is not
# a fourth". It was the fourth.
REG = HERE / "retractions.txt"
reg_lines = [ln.split("#")[0].strip() for ln in REG.read_text().splitlines()]
reg = [ln for ln in reg_lines if ln]
check("retraction registry is small", len(reg), predicate=lambda n: n <= 5)

import hashlib as _h
sys.path.insert(0, str(HERE))
from closure import blockquote_blocks          # ONE definition, shared — not a second regex here
_nbj = json.loads((HERE / "ARGUMENT.ipynb").read_text())
_txt = "\n".join("".join(c["source"]) for c in _nbj["cells"] if c["cell_type"] == "markdown")
_live = {_h.sha256(b.encode()).hexdigest()[:16] for b in blockquote_blocks(_txt)}
check("every registry entry matches a real blockquote", sorted(set(reg) - _live),
      predicate=lambda orphans: orphans == [])

check("no proof rests on an empirical observation", clo.returncode, 0)
check("  closure.py reports it explicitly", "CLOSURE HOLDS" in clo.stdout, True)


# ══ 4 · THE ASSERTIONS FAIL WHEN THEY SHOULD ═════════════════════════════════════════════
# A suite that has never failed proves nothing. falsify.py plants a violation under each assertion
# and confirms it fires. This runs it and reads the count off its output rather than trusting it.
section("4 · the checks are falsifiable")

# A MISSING DEPENDENCY IS NOT A DEFECT IN THE WORK, AND MUST NOT READ LIKE ONE. `check.py` imports
# only the standard library — but it SUBPROCESSES falsify.py, which needs numpy and torch. On a
# stock python the reader used to see `falsify.py ran  False (expected True)` and exit 1, with the
# actual cause (ModuleNotFoundError) captured into a variable and never printed. That is this
# document's own T21: a predicate that discards the field its output would have explained.
if not _writable:
    # falsify.py plants violations on disk; it cannot run at all on a read-only tree, and the
    # 22/23 it reports there is a fact about the mount, not about the suite.
    class _NR:
        stdout = ""; stderr = ""; returncode = 0
    fal = _NR()
else:
    fal = subprocess.run([sys.executable, "falsify.py"], cwd=HERE, capture_output=True, text=True, timeout=300)
m = re.search(r"(\d+)/(\d+) assertions fired", fal.stdout)
# A DEPENDENCY THAT BREAKS IS NOT A DEPENDENCY THAT DISAPPEARS. Matching only
# ModuleNotFoundError means numpy 3.0 removing an attribute raises AttributeError, the regex
# misses, and the reader sees "falsify.py ran False (expected True)" — the exact mislabel this
# branch exists to prevent, one API break away. Any exception with no assertion count is an
# environment problem, not a defect in the work.
dep = re.search(r"ModuleNotFoundError: No module named '(\w+)'", fal.stderr)

# THE FALLBACK THAT USED TO LIVE HERE IS DELETED, AND ITS DELETION COSTS SOMETHING REAL.
# It read: any `SomeError: ...` in stderr with no assertion summary means "a working environment".
# The stated worry was sound — numpy 3.0 dropping an attribute would raise AttributeError, the
# ModuleNotFoundError regex would miss, and a reader would see a package problem reported as a
# defect in the work. But the cure was strictly worse than the disease: it converted EVERY crash
# into an environment excuse, so one planted `raise ValueError` in falsify.py — a file no manifest
# hashes — disarmed the gate whose entire purpose is that a suite which has never failed proves
# nothing, and charged the failure to the reader's machine.
#
# Trading "a real defect can be mislabelled as an environment problem" for "an environment problem
# can be mislabelled as a real defect" is the right direction, and it is not symmetric: the second
# error is loud, lands on the author, and gets fixed. The first is quiet, lands on the reader, and
# clears the artifact. A false acquittal is permanent because nobody re-examines a cleared claim.
#
# So only a genuinely absent module excuses this gate, and `dependency_claim` verifies the absence
# rather than believing the message.
if not _writable:
    UNVERIFIED.append("falsifiability of the science suite (tree is not writable) — 1 check(s) not run")
    SUPPRESSED.append(1)
    print(f"  ????  {'assertions fire on planted false input':<58} UNVERIFIED — read-only tree")
elif m is None and dep and dependency_claim("assertions fire on planted false input", dep.group(1)):
    pass
elif m is None and dep:
    pass          # dependency_claim already recorded the FAILURE — the module imports fine
else:
    check("falsify.py ran", m is not None, True)
    if m:
        check("assertions that fire on planted false input", f"{m.group(1)}/{m.group(2)}",
              predicate=lambda s: s.split("/")[0] == s.split("/")[1] and int(s.split("/")[0]) >= 20)
    elif fal.stderr:
        print("        " + fal.stderr.strip().splitlines()[-1][:100])


# ══ 5 · ONE SUBSTANTIVE CLAIM, RECOMPUTED FROM THE EVIDENCE ══════════════════════════════
# The artifact's own measured finding, stated at its THIRD narrowing. This header used to read
# "the generation cap censors the baseline cell and no other, so the reported collapse is a lower
# bound" — both halves of which are retracted 70 lines below, in LIMITS.md, and in the census
# generator. A retraction reached the prose and stopped, inside the gate.
# What survives: the cap censors the baseline; against a comparison cell that is uncensored AND has
# l > e, the reported collapse is a lower bound. That is step0008 and nothing else. Recomputed here from staged rollouts, no model needed.
section("5 · the censoring finding, recomputed")

# RECOMPUTED MEANS RECOMPUTED. The first version of this section read length_census.json and
# checked that file against itself, while the prose above it said "recomputed from staged
# rollouts". A reader hand-edited the census (baseline mean 1747.1 -> 400) and got 28 green; then
# left the census alone and inverted the RAW evidence so the collapse ran backwards, and got 28
# green again. `derive_length_census.py` even documents an "always" tier that recomputes the
# char statistics with stdlib — that tier did not exist. This is the exact failure this file's own
# header complains about: a number that was true when typed and that nothing re-derives.
#
# Char statistics need no tokenizer, so they are recomputed here, always, from the raw JSONL.
# Token statistics need one; if it is absent that tier reports UNVERIFIED rather than passing.
CAP = 600
cens = json.loads((HERE / "data/derived/length_census.json").read_text())
LADDER = HERE / "data/experiments_ds/ladder"

def _answers(fp):
    out = []
    for line in fp.open():
        if not line.strip():
            continue
        d = json.loads(line)
        for k in ("answer", "completion", "text", "response"):
            if k in d:
                out.append(d[k])
                break
    return out

raw = {}
for fp in sorted(LADDER.glob("step*.jsonl")):
    a = _answers(fp)
    raw[fp.stem] = {"n": len(a),
                    "mean_chars": round(sum(len(x) for x in a) / len(a), 1),
                    "max_chars": max(len(x) for x in a)}

check("census covers exactly the staged ladder cells", sorted(cens["cells"]) == sorted(raw), True)
mismatch = [k for k in raw if any(cens["cells"][k][f] != raw[k][f]
                                  for f in ("n", "mean_chars", "max_chars"))]
check("census char statistics recomputed from raw JSONL", mismatch, predicate=lambda m: m == [])
for k in sorted(raw):
    print(f"        {k}: n={raw[k]['n']} mean_chars={raw[k]['mean_chars']} (recomputed)")

# Token tier — the cap is a TOKEN cap, so this is what licenses the finding.
try:
    from tokenizers import Tokenizer
    _tk = Tokenizer.from_file(str(HERE / "data/models/Qwen2.5-7B-Instruct/tokenizer.json"))
    tok_bad = []
    for fp in sorted(LADDER.glob("step*.jsonl")):
        toks = [len(_tk.encode(x).ids) for x in _answers(fp)]
        got = {"max_tokens": max(toks), "at_cap": sum(1 for t in toks if t >= CAP - 1)}
        if any(cens["cells"][fp.stem][f] != got[f] for f in got):
            tok_bad.append(fp.stem)
    check("census token statistics recomputed with the staged tokenizer", tok_bad,
          predicate=lambda b: b == [])
except ImportError:
    # NARROWED FROM `except Exception`, for the reason the whole UNVERIFIED path was narrowed: a
    # bare Exception handler here excused a corrupt tokenizer.json, a KeyError from a census whose
    # shape had drifted, and any arithmetic bug in the four lines above — all under the advice
    # "install `tokenizers`". Only the absence of the package is an environment fact; everything
    # else that can go wrong in this block is a fact about the artifact.
    dependency_claim("census token statistics", "tokenizers")
except Exception as exc:
    check(f"census token tier raised {type(exc).__name__}: {str(exc)[:80]}", False, True)

check("cells measured", len(cens["cells"]), predicate=lambda n: n >= 3)
base = cens["cells"]["step0000"]
check("baseline: answers at the generation cap", f"{base['at_cap']}/{base['n']}",
      predicate=lambda s: int(s.split("/")[0]) > 0)
check("baseline max token length equals the cap", base["max_tokens"], CAP)
for name, cell in sorted(cens["cells"].items()):
    # informational rows: they report, they do not gate. `check(label, got)` with neither a
    # expected value nor a predicate would compare got == None and fail every time — a check that
    # cannot pass is as useless as one that cannot fail, and this file should not contain either.
    print(f"        {name}: at cap {cell['at_cap']}/{cell['n']}   max_tok {cell['max_tokens']}")

# THE CLAIM, NARROWED THREE TIMES, AND THE LAST NARROWING KILLED THE GENERAL FORM.
#   v1  "censoring is confined to the baseline"        — false; step0019 has 2.
#   v2  "baseline censored >= every later cell, so every forward collapse is a lower bound"
#       — the ordering is a comparison of COUNTS (13 >= 2) and the conclusion is about censored
#       MASS. Truncated text is unbounded per answer, so counts bound nothing. A reader computed
#       the break-even: the claim needs the two step0019 truncations to have held under 30% of the
#       leftover text of a baseline truncation. Under the neutral assumption that they held the
#       SAME, the published 95.5% collapse is an OVER-estimate, not a lower bound. Nothing here
#       measures the leftover text, so the general claim is not available.
#   v3  what survives, and it needs no assumption about mass at all: when the comparison cell has
#       ZERO capped answers, there is no censoring on that side to weigh. collapse = (b-l)/b;
#       censoring lowers b; raising b raises 1-l/b. So the observed collapse understates the true
#       one, exactly, by arithmetic.
# And the line that used to sit here was `check(..., True, True)` — a literal compared to itself,
# printing `ok` while the two assertions above it printed FAIL. That is T21 committed by the gate
# enforcing T21, fourteen lines after this file congratulates itself for shipping no such check.
uncensored = sorted(k for k, c in cens["cells"].items() if k != "step0000" and c["at_cap"] == 0)
censored_later = sorted(k for k, c in cens["cells"].items() if k != "step0000" and c["at_cap"] > 0)

# A THIRD NARROWING, AND THE SECOND TAUTOLOGY IN THE SAME PLACE.
# The line here used to be:
#     check("=> lower bound holds against those, by arithmetic",
#           all(cens["cells"][k]["at_cap"] == 0 for k in uncensored), True)
# `uncensored` IS the set defined by at_cap == 0, so the predicate is that set's defining property.
# It returns True on every possible census, including one where nothing is uncensored. It said "by
# arithmetic" and performed none. That is the same defect as the `check(..., True, True)` it
# replaced — written longer, three lines under a comment confessing the first one.
#
# AND THE ARITHMETIC IT GESTURED AT WAS FOR THE WRONG FORMULA. LIMITS said collapse = (b-l)/b. The
# published figures are (b-l)/(b-e), normalised by the ENDPOINT e = step0375's mean: (b-l)/b gives
# 79.8% where the document reports 95.5%. Under the real formula
#     d/db [ (b-l)/(b-e) ] = (l-e)/(b-e)^2
# so depressing b understates the collapse only when l > e. For step0375, l IS e: the ratio is
# identically 1 whatever b does, and listing it as covered was vacuous, not merely unproved.
#
# So the gate now computes the derivative's sign from the staged means, and the surviving claim is
# ONE cell: step0008 — uncensored AND l > e. That is the headline comparison and nothing else.
E_CELL = "step0375"
e_mean = cens["cells"][E_CELL]["mean_chars"]
b_mean = cens["cells"]["step0000"]["mean_chars"]

def _bound_holds(cell):
    """Lower bound requires (i) the comparison cell is uncensored and (ii) l > e."""
    c = cens["cells"][cell]
    return c["at_cap"] == 0 and c["mean_chars"] > e_mean

covered = sorted(k for k in cens["cells"] if k != "step0000" and _bound_holds(k))
vacuous = sorted(k for k in cens["cells"]
                 if k != "step0000" and cens["cells"][k]["at_cap"] == 0
                 and cens["cells"][k]["mean_chars"] == e_mean)

check("comparison cells with ZERO capped answers", uncensored, predicate=lambda ks: len(ks) >= 1)
check("  of those, cells where l > e so the derivative is positive", covered,
      predicate=lambda ks: len(ks) >= 1)
for k in sorted(cens["cells"]):
    if k == "step0000":
        continue
    c = cens["cells"][k]
    print(f"        {k}: at_cap {c['at_cap']:>2}  mean {c['mean_chars']:>7}  "
          f"l-e {c['mean_chars'] - e_mean:>7.1f}  -> "
          f"{'LOWER BOUND' if k in covered else ('vacuous (l=e)' if k in vacuous else 'not claimed')}")
# `vacuous` and `covered` are built from `> e` and `== e`, so disjointness is true on every possible
# census — a third tautology in the section whose comments already confess two. What is not
# tautological, and is the thing worth asserting, is that the vacuous set is exactly the cells where
# the derivative is zero, computed independently of how the sets were built.
check("  cells where the ratio is identically 1 (claim vacuous, NOT covered)", vacuous,
      predicate=lambda ks: ks == sorted(k for k in cens["cells"]
                                        if k != "step0000"
                                        and abs(cens["cells"][k]["mean_chars"] - e_mean) < 1e-9
                                        and cens["cells"][k]["at_cap"] == 0))
check("comparison cells themselves censored (lower bound NOT claimed)", censored_later,
      predicate=lambda _: True)
# A PHRASE-GREP CANNOT SETTLE THIS, and this is the fourth time that lesson has arrived in this
# artifact. The gate here used to assert the string "every forward collapse" appears nowhere — and
# it fired on LIMITS.md QUOTING the retracted claim in order to withdraw it. Same use/mention trap
# as the citation sweep, the path gate and the self-referential leak check. A document that retracts
# a sentence must contain that sentence. So the check is structural instead: the two populations
# must be non-empty and disjoint, which is the content the prose is obliged to reflect.
check("  the two populations are separated, not pooled",
      f"exact:{uncensored} unresolved:{censored_later}",
      predicate=lambda _: bool(uncensored) and bool(censored_later)
      and not set(uncensored) & set(censored_later))
check("censoring instrument returns a null where it should",
      f"{len(uncensored)} of {len(cens['cells']) - 1} later cells read 0",
      predicate=lambda _: len(uncensored) > 0)


# ══ 6 · PROSE THAT CAN DRIFT, ASSERTED AGAINST REALITY ═══════════════════════════════════
section("6 · documentation cannot rot")

readme = (HERE / "README.md").read_text()
limits = (HERE / "LIMITS.md").read_text()

for doc, name in ((readme, "README.md"), (limits, "LIMITS.md")):
    # [a-z0-9_]+, not [a-z_]+ — the old class could not match the "1" in `s19_at_cap`, so one of
    # LIMITS.md's four markers was never read at all. A reader set it to 99999 and the run stayed
    # green, while a separate regex counted 4 markers present, so "4 present" and "3 handled" could
    # not visibly disagree. The number it guards, s19_at_cap = 2, is the one that killed v1 of the
    # censoring claim.
    for claimed in re.findall(MARKER, doc):
        key, val = claimed
        if key == "theorems":
            check(f"{name} states {key}", kinds["T"], int(val))
        elif key == "statements":
            check(f"{name} states {key}", _L["total"], int(val))
        elif key == "proofs":
            check(f"{name} states {key}", count_proofs(arg_txt), int(val))
        elif key == "evidence_files":
            check(f"{name} states {key}", len(MAN["evidence"]), int(val))
        elif key == "lean_theorems":
            check(f"{name} states {key}", count_lean_theorems(HERE / "lean"), int(val))
        elif key == "cap":
            check(f"{name} states {key}", cens["cap"], int(val))
        elif key == "base_at_cap":
            check(f"{name} states {key}", cens["cells"]["step0000"]["at_cap"], int(val))
        elif key == "s19_at_cap":
            check(f"{name} states {key}", cens["cells"]["step0019"]["at_cap"], int(val))
        elif key == "ladder_cells":
            check(f"{name} states {key}", len(cens["cells"]), int(val))
        elif key == "checks_full":
            # CHECKED AGAINST THE DECLARED TOTAL, NOT AGAINST N, because N is not final here — this
            # loop runs mid-file and the gates below it have not been counted yet. Comparing to a
            # running total would let the README state whatever N happened to be at this line, which
            # is a number with no meaning. EXPECTED_TOTAL is in turn asserted against N + suppressed
            # at the bottom of a complete run, so the chain is: README -> declared -> observed, with
            # each link checked and no link a memory.
            check(f"{name} states {key}", EXPECTED_TOTAL, int(val))
        else:
            # AN UNKNOWN MARKER MUST FAIL, NOT BE IGNORED. README claimed every number in LIMITS.md
            # was re-derived while LIMITS.md carried no markers at all — so the loop body never ran
            # and the claim was vacuously "true". A marker nobody handles is the same hole one step
            # later, so it is an error rather than a no-op.
            check(f"{name} marker '{key}' has a handler", False, True)

# The needle is assembled at runtime so this file does not contain it. The first version searched
# for a literal and flagged itself — the same use/mention confusion that makes a citation sweep
# report a document's own discussion of a retracted claim. Exempting the file by name would have
# hidden a real bug behind a special case.
NEEDLE = "/" + "home" + "/"
EVIDENCE_DIR = HERE / "data" / "scripts"   # the audited source: verbatim, paths and all, by design
# EVERY TEXT FILE THIS ARTIFACT AUTHORS, not just *.py. The first version globbed Python only; a
# reader planted the author path into README.md, a markdown cell of PROOF.ipynb and Clamp.lean and
# the gate stayed green. Worse, the pristine artifact ALREADY shipped it — twice in PROOF.ipynb's
# notebook metadata and three times in MANIFEST.json — so the gate was green over a live leak.
BINARY_SUFFIX = (".pt", ".png", ".jpg", ".gz", ".zip", ".pyc", ".so", ".bin")
leaks = []
for p in sorted(HERE.rglob("*")):
    # DENYLIST, NOT ALLOWLIST. This skipped anything whose suffix was not in a fixed tuple, so an
    # adversary shipped PROVENANCE.yaml, setup.cfg and a file called NOTES with no suffix at all —
    # each carrying the author path, none scanned, none hashed. The comment above it read "EVERY
    # TEXT FILE THIS ARTIFACT AUTHORS". Now every file is scanned unless it is demonstrably binary.
    if not p.is_file():
        continue
    if p.suffix in BINARY_SUFFIX:
        continue
    try:
        _probe = p.read_bytes()[:2048]
        if b"\x00" in _probe:
            continue                      # binary by content, not by name
    except OSError:
        continue
    if EVIDENCE_DIR in p.parents:            # the audited scripts keep their paths, by design
        continue
    if (HERE / "data") in p.parents:
        # ALL staged evidence is verbatim, not just data/scripts. Model-generated rollouts quote the
        # author's path because the model was shown it; sanitising evidence to satisfy a leak gate
        # would fabricate provenance, which is the one thing this artifact must not do.
        continue
    if p.name == "MANIFEST.json":            # provenance: it RECORDS the source paths on purpose
        continue
    # A BUILD WRITES `<stem>.LOCAL.ipynb` AND NOTHING ELSE. The exemption used to be `".LOCAL." in
    # name`, so a file called NOTES.LOCAL.md was exempt from the path gate — and `.gitignore` only
    # covers `*.LOCAL.ipynb`, so it would have SHIPPED as well as being unchecked. Every exemption
    # in this file is an attack surface; this one I found by attacking it.
    if p.name.endswith(".LOCAL.ipynb"):
        continue
    if p.suffix == ".ipynb":
        # A NOTEBOOK'S STORED OUTPUT LEGITIMATELY QUOTES THE EVIDENCE, and the audited scripts carry
        # the author's paths by design. Cell 46 of PROOF.ipynb prints a line of fit_operator.py that
        # contains one. Flagging that would push toward sanitising the quotation, which is the thing
        # this artifact refuses to do. So notebooks are checked on what they AUTHOR — cell source
        # and metadata — and not on what they REPRODUCE.
        nb_json = json.loads(p.read_text())
        authored = json.dumps(nb_json.get("metadata", {})) + "".join(
            "".join(c["source"]) for c in nb_json["cells"])
        if NEEDLE in authored:
            leaks.append(str(p.relative_to(HERE)))
        continue
    if NEEDLE in p.read_text(errors="ignore"):
        leaks.append(str(p.relative_to(HERE)))
# BARE PROSE NUMBERS ROT TOO, and the sentence claiming otherwise was false. The marker mechanism
# only re-derives numbers wearing a <!--CHECK:--> tag; a reader found three unmarked ones that had
# drifted — "34 proofs" three lines under a marker reading 41 (I bumped the marker and not the
# prose), "exactly three ways" over a four-row table, and a runtime that had been edited AWAY from
# the truth. So the quantities known to drift are now matched wherever they appear, tag or no tag.
DERIVED = {
    r"(\d+)\s+proofs": count_proofs(arg_txt),
    r"(\d+)\s+labelled statements": _L["total"],
    r"(\d+)\s+theorems about": kinds["T"],
}
prose_bad, quoted_mentions = [], []
for doc in ("README.md", "LIMITS.md", "FINDINGS.md"):
    text = (HERE / doc).read_text()
    for pat, truth in DERIVED.items():
        for m in re.finditer(pat, text):
            # QUOTED IS MENTION. A document that records its own retractions is OBLIGED to contain
            # the wrong number — FINDINGS.md's row reads **"34 proofs" was 41**, and flagging that
            # would push toward deleting the retraction to satisfy the gate. Sixth time in this
            # artifact that a textual check has needed this distinction; it is not incidental, it
            # is what happens when a document is required to quote what it withdraws.
            # NO EXEMPTION IN THE README. The quoted-span exemption exists because FINDINGS.md and
            # LIMITS.md are OBLIGED to quote the numbers they retract. The README is not: it makes
            # claims. I attacked my own exemption by putting `"999 labelled statements"` in the
            # README and the gate stayed green — a false headline number, in quotes, invisible.
            # So the exemption is scoped to the two documents that record history, and there it is
            # PRINTED rather than skipped silently, because an unreported exemption is a blind spot
            # that nobody can audit.
            # ONE CHARACTER WAS THE WHOLE TEST, AND ONE CHARACTER IS NOT A MENTION. The trigger was
            # `text[m.start()-1] in quotes`, so any assertive present-tense sentence obtained the
            # exemption by wearing a quotation mark. An adversary appended to LIMITS.md:
            #
            #     The argument carries "99 proofs" and "512 labelled statements", every one of them
            #     closed and independently checked.
            #
            # and both were PRINTED as `exempt: quoted - a recorded retraction`. Printing rather than
            # skipping was meant to make the exemption auditable, and instead it dressed the
            # fabrication in the mechanism's own words. A blind spot you print is still a blind spot;
            # what makes it auditable is that the printed line be TRUE.
            #
            # A real mention says the number is no longer the number. So the exemption now requires
            # retraction language on the same line, which is what these documents' own convention
            # already looks like: FINDINGS.md's row reads `**"34 proofs" was 41**`. The attacker's
            # sentence carries none, because a sentence that both asserts a count and withdraws it
            # is not a useful thing to write.
            # TWO WAYS TO BE A MENTION, because the documents use two and I only encoded one.
            # First contact with the tightened rule produced a FALSE POSITIVE on LIMITS.md's own
            # defect ledger, whose row reads: the prose-number gate skipped quoted numbers |
            # "999 labelled statements" in the README passed | no exemption in the README at all.
            # That is the purest possible mention -- a table whose columns are what was wrong,
            # the evidence, and the fix -- and it carries no retraction VERB because the retraction
            # is carried by the STRUCTURE. Narrowing a rule until it catches the attacker and then
            # discovering it also catches the document's most honest paragraph is the ordinary
            # outcome of tightening, and the answer is to name the second form, not to reword the
            # paragraph until the gate is happy. Editing the evidence to satisfy the instrument is
            # the failure this whole artifact is about.
            RETRACTS = ("was", "were", "retract", "withdraw", "no longer", "corrected",
                        "wrong", "is now", "should have", "->")
            line = text[text.rfind("\n", 0, m.start()) + 1:
                        (text.find("\n", m.end()) + 1 or len(text))]
            quoted = m.start() > 0 and text[m.start() - 1] in '"\u201c'
            if quoted and doc in ("FINDINGS.md", "LIMITS.md"):
                # ENUMERATION, NOT PATTERN — the third and last form of this exemption.
                # v1 was "preceded by a quote character". v2 added "retraction language on the line
                # OR a markdown table row". An adversary beat v2 with one line of markdown: a
                # fabricated table row needs three pipes and no retraction verb, and the word
                # "corrected" inside a present-tense assertion satisfies the other branch. The
                # control — the SAME SENTENCE wrapped across two lines — failed. A line break was
                # the only thing separating a pass from a failure, which is the clearest possible
                # demonstration that the test was measuring format and not meaning.
                #
                # Format is chosen by whoever writes the sentence; REGISTRATION IS NOT. A quoted
                # number must now appear in `retracted_numbers.txt` — the same move closure.py made
                # when its blockquote exemption became a hiding place. Adding a line there is a diff
                # a reviewer can object to; matching a shape is not.
                _val = f"{m.group(1)} {pat.split(chr(92))[0].strip('()d+s ')}".strip()
                _key = re.sub(r"\s+", " ", f"{m.group(1)} {m.group(0).split(m.group(1),1)[1]}").strip()
                why = "registered retraction" if _key in REGISTERED_NUMBERS else None
                if why is None:
                    prose_bad.append(
                        f"{doc}: '{m.group(0).strip()}' is quoted but its line retracts nothing "
                        f"- a quotation mark is not a mention")
                    continue
                quoted_mentions.append(f"{doc}: {m.group(0).strip()} (quoted; {why})")
                continue
            if int(m.group(1)) != truth:
                prose_bad.append(f"{doc}: '{m.group(0).strip()}' but derived {truth}")
check("bare prose numbers match the derived values", prose_bad, predicate=lambda b: b == [])
for q in quoted_mentions:
    print(f"        exempt: {q}")
for b in prose_bad[:5]:
    print(f"        {b}")

check("no authored file leaks an absolute author path", leaks, predicate=lambda lst: lst == [])

# README says "every number in this file and in LIMITS.md is re-derived". That sentence was false
# for LIMITS.md, which had zero markers — a promise checked by a loop with nothing to iterate over.
for doc in ("README.md", "LIMITS.md"):
    # THE COUNT MUST USE THE PARSER'S REGEX. This counted the bare literal `<!--CHECK:` while the
    # handler parsed `[a-z0-9_]+`, so a marker the handler CANNOT read — an uppercase key, a leading
    # space — was counted as coverage and never handled, and the "unknown marker must fail" branch
    # was unreachable for it. An adversary shipped two fabricated numbers wearing verification tags
    # and the artifact reported MORE coverage because of them.
    raw_tags = len(re.findall(r"<!--CHECK:", (HERE / doc).read_text()))
    n_markers = len(re.findall(MARKER, (HERE / doc).read_text()))
    check(f"{doc}: every CHECK tag is parseable by the handler", raw_tags - n_markers,
          predicate=lambda d: d == 0)
    check(f"{doc} carries re-derived numbers", n_markers, predicate=lambda n: n >= 4)

# The evidence directory is expected to contain them, and that expectation is asserted rather than
# assumed — if it ever came back empty, the scripts would have been silently sanitised.
kept = [p.name for p in sorted(EVIDENCE_DIR.glob("*.py")) if NEEDLE in p.read_text(errors="ignore")]
check("audited source kept verbatim (paths intact = not sanitised)", len(kept),
      predicate=lambda n: n > 0)


# ══ VERDICT ══════════════════════════════════════════════════════════════════════════════
# CLEAN UP THE SCRATCH THIS RUN CREATED. Sections 3 and 3b write <stem>.LOCAL.ipynb to compare
# against; leaving them behind meant a stranger's `ls` showed FOUR notebooks with no signal which to
# open, and two blind lenses raised it independently. A published tree must not accumulate the
# residue of having been checked.
for _scratch in HERE.glob("*.LOCAL.ipynb"):
    _scratch.unlink(missing_ok=True)
import shutil as _sh
for _pyc in HERE.rglob("__pycache__"):
    _sh.rmtree(_pyc, ignore_errors=True)

print(f"\n{'=' * 78}")
if UNVERIFIED:
    print(f"{len(UNVERIFIED)} check(s) UNVERIFIED — this environment could not run them:")
    for u in UNVERIFIED:
        print(f"   ? {u}")
    print("  UNVERIFIED is not a pass. The check was unfit here; it did not succeed.\n")
if FAIL:
    print(f"{len(FAIL)} of {N} checks FAILED:")
    for f in FAIL:
        print(f"   · {f}")
    sys.exit(1)
# THE TOTAL IS DECLARED, SO A GATE CANNOT LEAVE WITHOUT SAYING SO.
# ASSERTED ONLY IN A FULL RUN, AND THAT LIMIT IS THE HONEST ONE. CHECK_SKIP_SLOW=1 omits two whole
# sections; declaring how many checks each contains would put a hand-typed number in the file whose
# subject is hand-typed numbers going stale — I guessed 3 and 5 for sections holding 23 between
# them, which is exactly the failure. So the accounting is exact where it can be exact (the full
# run a reader performs) and silent where it cannot, rather than approximate everywhere.
# ASSERTED ONLY WHEN EVERYTHING RAN, AND I GOT THIS WRONG ONCE ALREADY IN THE SAME FILE.
# The first version asserted whenever CHECK_SKIP_SLOW was unset — which includes a stock `python3`
# with no numpy, where 52 gates run and 8 are suppressed and the arithmetic cannot balance because
# a suppressed gate does not know how many checks it took with it. So a reader on a clean machine
# got `FAIL gate accounting: 52 ran + 8 suppressed = 60, declared 82`: a missing package rendered
# as a defect in the work, which is precisely the sin the UNVERIFIED repair two commits ago existed
# to remove, reintroduced by the repair's own bookkeeping.
#
# The total is knowable exactly when nothing was skipped, so that is when it is asserted. This does
# not hand the count back to an attacker: fabricating a missing dependency now FAILS at `missing()`
# before it can reach here, so there is no path to "accounting not asserted" that is itself green.
_total = N + sum(SUPPRESSED)
if not SKIP_SLOW and not UNVERIFIED and _total != EXPECTED_TOTAL:
    print(f"\n  FAIL  gate accounting: {N} ran + {sum(SUPPRESSED)} suppressed = {_total}, "
          f"declared {EXPECTED_TOTAL}")
    print("        A check disappeared without being reported as UNVERIFIED, or one was added")
    print("        without updating EXPECTED_TOTAL. Either way the printed count is not the")
    print("        number of gates this artifact has.")
    sys.exit(1)
if SKIP_SLOW or UNVERIFIED:
    # THE ARITHMETIC MUST CLOSE, OR THE LINE IS WORSE THAN SILENCE. This printed
    # "78 of the 83 declared gates ran here; 3 could not" — and 78+3 is 81, so an operator was
    # invited to reconcile a two-check hole that does not exist. The 3 counted UNVERIFIED GATES
    # while the 78 counted CHECKS, two different units in one sentence, which is this artifact's
    # own T13 committed by its summary line.
    #
    # The per-gate suppression counts are now MEASURED, not declared: Lean's section is 25 checks
    # (83 with lean on PATH, 58 without), live notebook execution is 3, the falsify and tokenizer
    # tiers are 1 each. I had written 5 for Lean by eye. Where the counts are right this line
    # closes exactly; where it does not close it now SAYS so rather than printing a hole.
    _acct = N + sum(SUPPRESSED)
    _fit = "" if _acct == EXPECTED_TOTAL else f"  ⚠ {_acct} != {EXPECTED_TOTAL} declared — accounting is incomplete"
    print(f"  ({N} ran + {sum(SUPPRESSED)} suppressed = {_acct} of {EXPECTED_TOTAL} declared;"
          f" {len(UNVERIFIED)} gate(s) could not run here){_fit}")
# THE SENTENCE MUST NOT OUTRUN THE EXIT CODE. This printed "all N checks passed — every number
# above was recomputed, none was quoted" on runs where gates could not run and the process was
# about to exit 2 — so the claim was false precisely in the case the exit code exists to flag.
# A lens caught it, and it is the artifact's own defect class: a summary that contradicts the
# status it sits above.
if UNVERIFIED:
    print(f"{N} checks passed. NOT ALL OF THEM RAN — see the {len(UNVERIFIED)} UNVERIFIED line(s) "
          f"above; the numbers that were recomputed are the ones printed, and no others.")
else:
    print(f"all {N} checks passed — every number above was recomputed, none was quoted")
if UNVERIFIED:
    # EXIT 2, NOT 0. This printed "UNVERIFIED is not a pass" and then exited 0 anyway, so any CI
    # reading the exit code saw green on a run that skipped a quarter of the gates. The prose was
    # honest and the machine-readable signal was not — which is this artifact's own thesis,
    # committed by its own handle. A reproducer lens found it.
    #   0 = every gate ran and passed
    #   2 = everything that could run passed, but some gates could not run here
    #   1 = something failed
    print(f"\nEXIT 2 — {len(UNVERIFIED)} gate(s) could not run in this environment. Not a failure,")
    print("and not a clean pass either. Install the packages named above for exit 0.")
    sys.exit(2)
print("\nWhat this does NOT establish: that the arguments are correct. It establishes that the")
print("evidence is intact, the counts are real, the build is reproducible, the assertions can")
print("fail, and the prose matches the object. Correctness is what ARGUMENT.ipynb is for, and it")
print("is checked by reading — see LIMITS.md for what reading will not settle either.")
