#!/usr/bin/env python3
"""Plant a violation under each gate in `check.py` and confirm the gate fires.

    python3 falsify_check.py

`check.py` reporting 27 green proves nothing on its own — a suite that has never failed is
decoration, and decoration manufactures confidence, which is worse than no check at all. So each
violation below is actually written to disk, `check.py` is actually run against it, and the file is
actually restored. If a gate still passes while its own invariant is broken, it is reported as
DECORATION and this script exits non-zero.

`falsify.py` does this for the scientific assertions. This does it for the packaging gates — the
integrity, build, provenance and documentation checks — which are the ones most likely to be
written once and never exercised.
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
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PY = sys.executable



def must_replace(text: str, old: str, new: str, count: int = 1) -> str:
    """`str.replace` that refuses to be a no-op.

    A plant whose anchor has moved lands nothing, `check.py` stays green, and the case reports
    DECORATION for a gate that in fact fires — the harness then accuses a working check of being
    a check that cannot fail, which is precisely the error it exists to detect. That happened here
    when the README's statement count moved 67 -> 68. Every plant now goes through this.
    """
    out = text.replace(old, new, count)
    if out == text:
        raise AssertionError(f"PLANT DID NOT LAND — anchor not found: {old[:70]!r}")
    return out


class Planted:
    """Mutate a file, run check.py, restore. The restore is in `finally` — a violation left behind
    would corrupt the artifact this script exists to protect."""

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.backup = None

    def __enter__(self):
        self.backup = tempfile.NamedTemporaryFile(delete=False).name
        shutil.copy2(self.path, self.backup)
        return self

    def __exit__(self, *exc):
        shutil.copy2(self.backup, self.path)
        pathlib.Path(self.backup).unlink(missing_ok=True)
        return False


def run_check(slow: bool = False) -> tuple[int, str]:
    """Run the handle, returning its EXIT CODE (0 pass · 1 failed · 2 UNVERIFIED) and stdout.

    `slow=True` includes notebook execution and Lean, which take minutes.

    Most planted violations are caught by cheap gates, so running the expensive sections 17 times
    would turn this pass into an hour for no extra information. The cases that TEST those sections
    pass slow=True; everything else runs with CHECK_SKIP_SLOW=1, which reports them as UNVERIFIED
    rather than as passed.
    """
    import os
    env = {**os.environ}
    if slow:
        env.pop("CHECK_SKIP_SLOW", None)
    else:
        env["CHECK_SKIP_SLOW"] = "1"
    r = subprocess.run([PY, "check.py"], cwd=HERE, capture_output=True, text=True,
                       timeout=1200, env=env)
    # EXIT 2 IS NOT A FAILURE, AND READING IT AS ONE MADE THIS HARNESS UNFALSIFIABLE.
    # check.py grew a three-valued exit code — 0 all passed, 2 passed but something was UNVERIFIED,
    # 1 something FAILED. This function still asked `returncode == 0`. Since every fast case runs
    # with CHECK_SKIP_SLOW=1, which reports the slow gates as UNVERIFIED, EVERY case would have
    # exited 2 and been scored FIRED — including a case whose gate did nothing at all. The harness
    # built to prove that no check is decoration would itself have become the purest decoration in
    # the artifact, reporting 31/31 without a single gate having to work.
    #
    # It surfaced as a refusal to start (the precondition read exit 2 as "not green"), which is the
    # only reason it was found: the same defect on the case path is SILENT, because a false FIRED
    # looks exactly like a real one. The loud half of a bug is a gift.
    #
    # So the verdict is taken from the code that means what is being asked, and UNVERIFIED is
    # neither pass nor fail here — it is "this run could not answer", which is what it says.
    return r.returncode, r.stdout


CASES: list[tuple[str, str, callable]] = []


def case(name: str, gate: str):
    def deco(fn):
        CASES.append((name, gate, fn))
        return fn
    return deco


# ── 1 · evidence integrity ───────────────────────────────────────────────────────────────
@case("flip one byte of staged evidence", "manifest hash check")
def _(tmp):
    target = HERE / "data/scripts/eval_judge.py"
    with Planted(target):
        target.write_bytes(target.read_bytes() + b"\n# planted\n")
        return run_check()


@case("delete a manifest-listed file", "manifest presence check")
def _(tmp):
    target = HERE / "data/fits/u_L16.pt"
    with Planted(target):
        target.unlink()
        return run_check()


# ── 2 · counts ───────────────────────────────────────────────────────────────────────────
@case("state a wrong theorem count in the README", "self-enforcing docs")
def _(tmp):
    target = HERE / "README.md"
    with Planted(target):
        target.write_text(must_replace(target.read_text(), "<!--CHECK:theorems=26-->",
                                                     "<!--CHECK:theorems=99-->"))
        return run_check()


@case("strip stored outputs from a notebook", "stored-output gate")
def _(tmp):
    target = HERE / "ARGUMENT.ipynb"
    with Planted(target):
        nb = json.loads(target.read_text())
        for c in nb["cells"]:
            if c["cell_type"] == "code":
                c["outputs"] = []
        target.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
        return run_check()


@case("duplicate a statement label", "duplicate-label gate")
def _(tmp):
    # this case REBUILDS the notebook, so the notebook is collateral and must be restored with the
    # builder. The first version protected only build_argument.py and left ARGUMENT.ipynb carrying a
    # duplicated label and three of four outputs -- caught by the restore assertion at the end, which
    # is the only reason this harness is trustworthy at all.
    builder, notebook = HERE / "build_argument.py", HERE / "ARGUMENT.ipynb"
    with Planted(builder), Planted(notebook):
        builder.write_text(must_replace(builder.read_text(), "### T26 · ", "### T25 · ", 1))
        subprocess.run([PY, "build_argument.py"], cwd=HERE, capture_output=True,
                       env={**__import__("os").environ, "ARTIFACT_WRITE_REFERENCE": "1"})
        return run_check()


# ── 3 · build invariants ─────────────────────────────────────────────────────────────────
@case("make the build nondeterministic again", "reproducible-build gate")
def _(tmp):
    target = HERE / "artifact_io.py"
    with Planted(target):
        s = must_replace(target.read_text(), 
            'return hashlib.sha256(f"{index}\\x00{source}".encode()).hexdigest()[:8]',
            'import random; return "%08x" % random.getrandbits(32)')
        target.write_text(s)
        return run_check()


@case("let a reader's build overwrite the reference", "frozen-reference gate")
def _(tmp):
    target = HERE / "artifact_io.py"
    with Planted(target):
        s = must_replace(target.read_text(), 
            'target = reference if WRITE_REFERENCE else reference.with_suffix(f".LOCAL{reference.suffix}")',
            'target = reference')
        target.write_text(s)
        return run_check()


# ── 4 · falsifiability of the science suite ──────────────────────────────────────────────
@case("neuter an assertion in falsify.py", "falsifiability gate")
def _(tmp):
    target = HERE / "falsify.py"
    with Planted(target):
        s = must_replace(target.read_text(), "assertions fired on a false input", "assertions checked")
        target.write_text(s)
        return run_check()


# ── 5 · the substantive claim ────────────────────────────────────────────────────────────
@case("invert the censoring ordering", "lower-bound gate")
def _(tmp):
    target = HERE / "data/derived/length_census.json"
    with Planted(target):
        d = json.loads(target.read_text())
        d["cells"]["step0000"]["at_cap"] = 0      # baseline uncensored …
        d["cells"]["step0019"]["at_cap"] = 40     # … and a later cell heavily censored
        target.write_text(json.dumps(d, indent=2))
        return run_check()


# ── 6 · provenance ───────────────────────────────────────────────────────────────────────
@case("reintroduce an author path into authored code", "path-leak gate")
def _(tmp):
    target = HERE / "check.py"
    with Planted(target):
        # planted into a DIFFERENT authored file, so the gate is not merely detecting itself
        other = HERE / "derive_length_census.py"
        with Planted(other):
            # assembled, not written literally: a literal here would make the path-leak gate fire
            # on the harness itself, which is the same use/mention trap the gate was written to avoid
            leak = "/" + "home" + "/someone/secret/path"
            other.write_text(other.read_text() + f'\n_LEAK = "{leak}"\n')
            return run_check()


@case("sanitise the audited source", "verbatim-evidence gate")
def _(tmp):
    import os
    targets = sorted((HERE / "data/scripts").glob("*.py"))
    backups = []
    landed = 0
    try:
        for t in targets:
            b = tempfile.NamedTemporaryFile(delete=False).name
            shutil.copy2(t, b)
            backups.append((t, b))
            # PER-FILE must_replace IS WRONG HERE: this case sanitises the whole directory, and
            # only 12 of the 13 audited scripts contain the path. The guard correctly fired on the
            # 13th. What must land is at least ONE replacement across the set, not one per file.
            before = t.read_text()
            after = before.replace("/" + "home" + "/", "/PATH/")
            if after != before:
                landed += 1
            t.write_text(after)
        if not landed:
            return False, "PLANT DID NOT LAND — no audited script contained the path"
        return run_check()
    finally:
        for t, b in backups:
            shutil.copy2(b, t)
            os.unlink(b)


# ── gates added after two cold reads; each must be shown to fire ─────────────────────────
@case("break a cell so the notebook cannot run", "live-execution gate")
def _(tmp):
    target = HERE / "data/configs/core_split.json"
    with Planted(target):
        target.unlink()
        return run_check(slow=True)


@case("hand-edit the census away from the raw files", "census-recompute gate")
def _(tmp):
    target = HERE / "data/derived/length_census.json"
    with Planted(target):
        d = json.loads(target.read_text())
        d["cells"]["step0000"]["mean_chars"] = 400.0     # raw files say 1747.1
        target.write_text(json.dumps(d, indent=2))
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check()


@case("break the freeze in build_proof.py only", "per-builder invariant gate")
def _(tmp):
    target = HERE / "build_proof.py"
    with Planted(target), Planted(HERE / "PROOF.ipynb"):
        s = must_replace(target.read_text(), "    emit(nb, out)", "    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))")
        target.write_text(s)
        return run_check()


@case("plant an author path in a markdown file", "path-leak gate, non-.py")
def _(tmp):
    target = HERE / "LIMITS.md"
    with Planted(target):
        leak = "/" + "home" + "/someone/private"
        target.write_text(target.read_text() + f"\n\nstray: {leak}\n")
        return run_check()


@case("state an unhandled CHECK marker in LIMITS", "unknown-marker gate")
def _(tmp):
    target = HERE / "LIMITS.md"
    with Planted(target):
        target.write_text(target.read_text() + "\n<!--CHECK:invented_quantity=7-->\n")
        return run_check()


@case("weaken the Lean proof obligation", "Lean both-halves gate")
def _(tmp):
    target = HERE / "lean/Resolution.lean"
    with Planted(target):
        s = must_replace(target.read_text(), 
            "def ratio (num den : Measured Int) (_h : Resolved den) : Int :=",
            "def ratio (num den : Measured Int) (_h : True) : Int :=")
        target.write_text(s)
        return run_check(slow=True)


@case("hide an empirical premise in a theorem's STATEMENT", "closure statement-scan gate")
def _(tmp):
    # MY OWN ATTACK ON MY OWN FIX. closure.py originally scanned only between `**Proof` and the
    # tombstone, so moving the dependency one paragraph earlier passed clean. Widening the scan then
    # flagged T15's retraction note, which QUOTES the premise it withdraws — so blockquotes are
    # excluded. This case pins all of it: a non-quoted empirical citation in a statement must fail.
    builder, notebook = HERE / "build_argument.py", HERE / "ARGUMENT.ipynb"
    with Planted(builder), Planted(notebook):
        builder.write_text(must_replace(builder.read_text(), 
            "**Statement.** Neither functional determines the other:",
            "**Statement.** Given the measured values in O5, neither functional determines the other:", 1))
        subprocess.run([PY, "build_argument.py"], cwd=HERE, capture_output=True,
                       env={**__import__("os").environ, "ARTIFACT_WRITE_REFERENCE": "1"})
        return run_check()


# ── gates a third and fourth cold reader broke; each plant is theirs ─────────────────────
@case("falsify a stored output, then re-seal", "stored-vs-produced comparison")
def _(tmp):
    target = HERE / "PROOF.ipynb"
    with Planted(target), Planted(HERE / "MANIFEST.json"):
        nb = json.loads(target.read_text())
        for c in nb["cells"]:
            hit = False
            for o in c.get("outputs", []):
                t = "".join(o.get("text", ""))
                if "1.000000" in t:
                    o["text"] = [t.replace("1.000000", "0.123456")]
                    hit = True
                    break
            if hit:
                break
        target.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check(slow=True)


@case("put `sorry` in the load-bearing Lean theorem", "every-lean-file gate")
def _(tmp):
    target = HERE / "lean/Clamp.lean"
    with Planted(target), Planted(HERE / "MANIFEST.json"):
        target.write_text(must_replace(target.read_text(), 
            "  rw [ip_add_left, ip_smul_left, huv, kmul_zero, kadd_zero]", "  sorry", 1))
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check(slow=True)


@case("falsify a CHECK marker whose key contains a digit", "marker-regex gate")
def _(tmp):
    target = HERE / "LIMITS.md"
    with Planted(target):
        target.write_text(must_replace(target.read_text(), "<!--CHECK:s19_at_cap=2-->",
                                                     "<!--CHECK:s19_at_cap=99999-->"))
        return run_check()


@case("cite an observation as `$O_{5}$` in a proof", "closure LaTeX-normalisation gate")
def _(tmp):
    builder, notebook = HERE / "build_argument.py", HERE / "ARGUMENT.ipynb"
    with Planted(builder), Planted(notebook), Planted(HERE / "MANIFEST.json"):
        builder.write_text(must_replace(builder.read_text(), 
            "**Proof.** Both functionals are defined on a state",
            "**Proof.** By $O_{5}$ the cells are occupied. Both functionals are defined on a state", 1))
        subprocess.run([PY, "build_argument.py"], cwd=HERE, capture_output=True,
                       env={**__import__("os").environ, "ARTIFACT_WRITE_REFERENCE": "1"})
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check()


# ── my own exemptions, attacked by me. Each of the three was exploitable. ───────────────
@case("write a proof's reasoning AS a blockquote", "closure retraction-marker scope")
def _(tmp):
    builder, notebook = HERE / "build_argument.py", HERE / "ARGUMENT.ipynb"
    with Planted(builder), Planted(notebook), Planted(HERE / "MANIFEST.json"):
        builder.write_text(must_replace(builder.read_text(), 
            "**Proof.** Both functionals are defined on a state",
            "**Proof.**\n> By the measured values in O5 the cells are occupied, which settles it.\n\n"
            "Both functionals are defined on a state", 1))
        subprocess.run([PY, "build_argument.py"], cwd=HERE, capture_output=True,
                       env={**__import__("os").environ, "ARTIFACT_WRITE_REFERENCE": "1"})
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check()


@case("state a false headline number inside quotes", "README has no quote exemption")
def _(tmp):
    # DERIVE THE TARGET, AND ASSERT THE PLANT LANDED. The first version hard-coded "67 labelled
    # statements"; the README moved to 68, `str.replace` matched nothing, and the case reported
    # DECORATION for a gate that in fact fires — a check that cannot fail, inside the harness whose
    # purpose is finding checks that cannot fail. A plant that silently lands nothing is the same
    # defect one level up, so it is now an error rather than a quiet pass.
    target = HERE / "README.md"
    with Planted(target):
        before = target.read_text()
        n = re.search(r"(\d+) labelled statements", before).group(1)
        after = before.replace(f"the argument. {n} labelled statements;",
                               f'the argument. "999 labelled statements"; {n} labelled statements;', 1)
        if after == before:
            return False, "PLANT DID NOT LAND — the anchor moved; this case proves nothing"
        target.write_text(after)
        return run_check()


@case("hide an author path in a file named *.LOCAL.md", "LOCAL exemption is suffix-exact")
def _(tmp):
    stray = HERE / "NOTES.LOCAL.md"
    try:
        stray.write_text("stray " + "/" + "home" + "/someone/private\n")
        return run_check()
    finally:
        stray.unlink(missing_ok=True)


# ── the five plants readers three and four landed; each now must fire ────────────────────
@case("empirical premise in a MULTI-PART proof, T5(b)", "closure greedy-span")
def _(tmp):
    builder, notebook = HERE / "build_argument.py", HERE / "ARGUMENT.ipynb"
    with Planted(builder), Planted(notebook), Planted(HERE / "MANIFEST.json"):
        builder.write_text(must_replace(builder.read_text(), 
            "**Proof of (b).**",
            "**Proof of (b).** Granting the measured orthogonal leak reported in O5 as a premise,", 1))
        subprocess.run([PY, "build_argument.py"], cwd=HERE, capture_output=True,
                       env={**__import__("os").environ, "ARTIFACT_WRITE_REFERENCE": "1"})
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check()


@case("⚠ on line 1, empirical premise on line 2", "closure registry, not formatting")
def _(tmp):
    builder, notebook = HERE / "build_argument.py", HERE / "ARGUMENT.ipynb"
    with Planted(builder), Planted(notebook), Planted(HERE / "MANIFEST.json"):
        builder.write_text(must_replace(builder.read_text(), 
            "**Proof.** Both functionals are defined on a state",
            "**Proof.**\n> **⚠ Note.** Licensed by the measured values in O5.\n\n"
            "Both functionals are defined on a state", 1))
        subprocess.run([PY, "build_argument.py"], cwd=HERE, capture_output=True,
                       env={**__import__("os").environ, "ARTIFACT_WRITE_REFERENCE": "1"})
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check()


@case("edit a MARKDOWN cell in the notebook only", "source-vs-builder comparison")
def _(tmp):
    target = HERE / "ARGUMENT.ipynb"
    with Planted(target), Planted(HERE / "MANIFEST.json"):
        nb = json.loads(target.read_text())
        for c in nb["cells"]:
            src = "".join(c["source"])
            if c["cell_type"] == "markdown" and "268{,}435{,}456" in src:
                c["source"] = src.replace("268{,}435{,}456", "42")
                break
        target.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check(slow=True)


@case("fabricate an execute_result (no `text` key)", "all-payload output comparison")
def _(tmp):
    target = HERE / "PROOF.ipynb"
    with Planted(target), Planted(HERE / "MANIFEST.json"):
        nb = json.loads(target.read_text())
        for c in nb["cells"]:
            if c["cell_type"] == "code" and c.get("outputs"):
                c["outputs"].append({"output_type": "execute_result", "execution_count": 1,
                                     "metadata": {},
                                     "data": {"text/plain": "differential miss = 0.0000 pp"}})
                break
        target.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check(slow=True)


@case("swap a theorem for an axiom appeal, keep the count", "per-theorem axiom assertion")
def _(tmp):
    target = HERE / "lean/Clamp.lean"
    with Planted(target), Planted(HERE / "MANIFEST.json"):
        s = target.read_text()
        s = s.replace("  rw [ip_add_left, ip_smul_left, huv, kmul_zero, kadd_zero]",
                      "  exact clamp_locality _ _ _ _ _ _ _ _ _ _ _ _ _", 1)
        s = s.replace("namespace PersonaForensics",
                      "namespace PersonaForensics\n\naxiom clamp_locality : True", 1)
        s = s.replace("#print axioms PersonaForensics.clamp_fixes_orthogonal",
                      "#print axioms PersonaForensics.clamp_hits_target", 1)
        target.write_text(s)
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check(slow=True)


@case("assert a false count inside quotation marks", "quote exemption needs a real mention")
def _(tmp):
    # THE ADVERSARY'S EXPLOIT ⑨, verbatim. Under the old rule the trigger was the single character
    # before the match, so this passed AND WAS PRINTED as `exempt: quoted — a recorded retraction`.
    target = HERE / "LIMITS.md"
    with Planted(target), Planted(HERE / "MANIFEST.json"):
        target.write_text(target.read_text().rstrip("\n") + "\n\n" +
                          'The argument carries "99 proofs" and "512 labelled statements", every '
                          "one of them closed and independently checked.\n")
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check()


@case("register an ordinary blockquote as a retraction", "registry entry must BE a retraction")
def _(tmp):
    # THE ADVERSARY'S EXPLOIT ⑧. An empirical premise injected into a proof as a plain blockquote,
    # hashed with closure's own `blockquote_blocks`, one line appended to retractions.txt — and
    # closure reported 0 violations where the control reported 2. The registry checked that the
    # entry was listed and live, never that it was a withdrawal of anything.
    import hashlib as _h
    builder, notebook = HERE / "build_argument.py", HERE / "ARGUMENT.ipynb"
    registry = HERE / "retractions.txt"
    with Planted(builder), Planted(notebook), Planted(registry), Planted(HERE / "MANIFEST.json"):
        LAUNDER = ("> The premise this proof uses: the measured values in $O5$ show the instrument\n"
                   "> is complete on the population that matters, so the null IS admissible here.")
        builder.write_text(must_replace(
            builder.read_text(),
            "**Statement.** Neither functional determines the other:",
            LAUNDER + "\n\n**Statement.** Neither functional determines the other:", 1))
        subprocess.run([PY, "build_argument.py"], cwd=HERE, capture_output=True,
                       env={**__import__("os").environ, "ARTIFACT_WRITE_REFERENCE": "1"})
        h = _h.sha256(LAUNDER.encode()).hexdigest()[:16]
        registry.write_text(registry.read_text().rstrip("\n") + f"\n{h}  planted\n")
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check()


@case("hide an axiom from the scanner inside a string literal", "Lean's own axiom report")
def _(tmp):
    # THE ADVERSARY'S EXPLOIT ①, VERBATIM. `"/-"` opens a block comment for check.py's regex and is
    # an ordinary string for Lean, so the axiom, the theorem depending on it, and the `#print
    # axioms` line all vanish from `src_lean` while the compiler executes every one of them. Before
    # the repair this produced five green Lean assertions and exit 0.
    target = HERE / "lean/Clamp.lean"
    with Planted(target), Planted(HERE / "MANIFEST.json"):
        s = target.read_text()
        s = must_replace(s, "end PersonaForensics", '''def commentOpen : String := "/-"
axiom reviewer_agreement : (16:Nat) = 15
theorem clamp_proves_sixteen_x : (16:Nat) = 15 := reviewer_agreement
 #print axioms clamp_proves_sixteen_x
def commentClose : String := "-/"

end PersonaForensics''', 1)
        target.write_text(s)
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check(slow=True)


@case("mis-escape a display equation in the builder", "C0 control character in cell source")
def _(tmp):
    # THE PLANT IS THE ORIGINAL DEFECT, VERBATIM. Eight LaTeX commands shipped in non-raw Python
    # strings, so `\frac` reached the notebook as U+000C and the surviving claim's defining formula
    # rendered as `rac{b-l}{b-e}`. Every other gate stayed green through it — valid JSON, matching
    # hash, reproducible build, markdown cell that never executes. Re-introducing exactly one
    # occurrence is the honest test of whether the new gate sees what nine others could not.
    builder, notebook = HERE / "build_proof.py", HERE / "PROOF.ipynb"
    with Planted(builder), Planted(notebook), Planted(HERE / "MANIFEST.json"):
        builder.write_text(must_replace(builder.read_text(),
                                        r"\\frac{b-l}{b-e}", r"\frac{b-l}{b-e}", 1))
        subprocess.run([PY, "build_proof.py"], cwd=HERE, capture_output=True,
                       env={**__import__("os").environ, "ARTIFACT_WRITE_REFERENCE": "1"})
        subprocess.run([PY, "seal.py"], cwd=HERE, capture_output=True)
        return run_check()


def _snapshot() -> dict:
    """Copy every manifest-listed file plus the authored scripts to a temp dir.

    PER-CASE BACKUPS ARE NOT ENOUGH, and this was learned the hard way rather than anticipated.
    Case 7 disables the frozen-reference rule; `check.py` then runs the builder itself as part of
    its own section 3, which — with the rule disabled — overwrites ARGUMENT.ipynb. The mutation was
    in artifact_io.py, the damage was in a notebook, and a backup of the mutated file could not
    undo it. So the whole surface is snapshotted and anything that drifted is put back after every
    case, whatever caused it.
    """
    snap = tempfile.mkdtemp(prefix="artifact-snapshot-")
    keep = {}
    man = json.loads((HERE / "MANIFEST.json").read_text())
    # MANIFEST.json MUST BE IN HERE. Case 13 hand-edits the census and then runs seal.py, which
    # rewrites the manifest to match the PLANTED file. Restoring the census afterwards left the
    # manifest recording a hash that no longer existed — a dirty tree that survived the repair
    # because the file that recorded the damage was not itself protected.
    top = [q.name for q in HERE.glob("*.py")] + [
        "README.md", "LIMITS.md", "FINDINGS.md", "THIRD_PARTY.md", "MANIFEST.json", "LICENSE"]
    for rel in list(man["evidence"]) + top:
        src = HERE / rel
        if not src.is_file():
            continue
        dst = pathlib.Path(snap) / rel.replace("/", "__")
        shutil.copy2(src, dst)
        keep[rel] = dst
    return keep


def _restore(keep: dict) -> list[str]:
    """Put back anything that differs. Returns what had to be repaired, so it is never silent."""
    repaired = []
    for rel, backup in keep.items():
        live = HERE / rel
        if (not live.exists()) or live.read_bytes() != backup.read_bytes():
            live.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, live)
            repaired.append(rel)
    return repaired


def main() -> int:
    # PRECONDITION. A previous failed run of this harness once left the tree dirty; the next run
    # snapshotted that dirty state and faithfully restored it, so the damage survived the repair.
    # Refuse to start unless the artifact is already green — otherwise this script preserves
    # whatever it finds and calls it the baseline.
    rc, base = run_check()
    # THE ONE GATE THIS HARNESS MUST IGNORE, AND WHY IT IS NOT AN EXEMPTION I GET TO LIKE.
    # The git anchor asserts "the working tree equals what version control records". This script's
    # entire method is to make that false thirty-one times in a row. Requiring it before planting
    # is requiring a property the next line destroys, so it is not a weakened precondition — the
    # gate is inapplicable here in the way a thermometer is inapplicable to a colour.
    #
    # It is exempted BY NAME and reported, never by relaxing `rc`. The moment this becomes "ignore
    # non-zero exits" it stops distinguishing a dirty tree from a broken artifact, which is the
    # confusion the three-valued exit code exists to prevent.
    ANCHOR = "evidence matches version control"
    failing = [l.strip() for l in base.splitlines() if l.lstrip().startswith("FAIL")]
    only_anchor = failing and all(ANCHOR in l for l in failing)
    if rc == 1 and not only_anchor:
        print("REFUSING TO RUN — check.py is not green before planting anything.")
        print("Fix the artifact first (`python3 seal.py` if a rebuild left the manifest stale);")
        print("a harness that snapshots a broken tree will restore it broken.")
        for l in failing:
            print(f"   {l}")
        return 2
    if only_anchor:
        print("NOTE — starting on a tree with UNCOMMITTED CHANGES. The git anchor is the only")
        print("failing gate and it cannot hold during a run that plants violations by design.")
        print("Every OTHER gate was green before planting, which is the property that matters here.")
        print("If you are the author: the baseline below is of your working copy, not of a commit.\n")

    print(f"planting {len(CASES)} violations, running check.py against each\n")
    snap = _snapshot()
    decoration, launder, collateral = [], [], {}
    for i, (name, gate, fn) in enumerate(CASES, 1):
        rc, out = fn(None)
        # THREE OUTCOMES, BECAUSE THERE ARE THREE. A planted violation that ends in UNVERIFIED has
        # not been caught; it has been EXCUSED, and the adversary lens showed that is the cheapest
        # attack available — a gate you disable reports as a package the reader is missing. Scoring
        # it as FIRED would credit the gate for the attack that defeats it, so it gets its own name.
        fired = rc == 1
        excused = rc == 2
        hit = _restore(snap)
        if hit:
            collateral[name] = hit
        status = "FIRED   " if fired else ("LAUNDERED" if excused else "DECORATION")
        print(f"  {status}  {i:>2}. {name:<46} → {gate}")
        if excused:
            launder.append(f"{name} → {gate}")
        elif not fired:
            decoration.append(f"{name} → {gate}")

    if launder:
        print("\nPLANTED VIOLATIONS THAT ENDED IN *UNVERIFIED* — not caught, excused:")
        for d in launder:
            print(f"   · {d}")

    if collateral:
        print("\ncollateral repaired after these cases (a per-case backup was not sufficient):")
        for k, v in collateral.items():
            print(f"   {k}: {', '.join(v)}")

    print()
    rc, out = run_check()
    # Same exemption, same reason: if the run STARTED on a dirty tree the restore returns it to that
    # dirty tree, and the anchor fails for the state the author was already in. Any OTHER failure
    # here means a plant survived the restore, which is the one outcome that must stop the ship.
    post = [l.strip() for l in out.splitlines() if l.lstrip().startswith("FAIL")]
    ok = rc != 1 or (post and all(ANCHOR in l for l in post))
    print(f"artifact restored and check.py green again: {ok} (exit {rc})")
    for l in post:
        print(f"   still failing: {l}")
    if not ok:
        print("RESTORE FAILED — the artifact is dirty; do not ship")
        return 2

    print(f"\n{len(CASES) - len(decoration) - len(launder)}/{len(CASES)} gates fired on their own violation.")
    if decoration:
        print("\nGATES THAT DID NOT FIRE — these are decoration, not checks:")
        for d in decoration:
            print(f"   · {d}")
        return 1
    if launder:
        return 1
    print("Every gate in check.py has now been shown to fail when the thing it checks is false.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
