#!/usr/bin/env python3
'''Execute every notebook and write the real output back into it, cell by cell.

    <project-python> fill_outputs.py audit track

WHY: a notebook shipped with no stored outputs shows a reader nothing until they run it, and running
it needs a kernel with the project's whole dependency set. So "open the notebook" silently means
"reproduce the environment first", and the reader who only wants to CHECK the argument is blocked by
a requirement that has nothing to do with checking it.

Executing once and storing the output inverts that: the notebook is readable by anyone, immediately,
with the numbers that actually came out of this machine — and re-running it is then a choice, not a
precondition. Every output carries the timestamp and the interpreter that produced it, so a stale
notebook is visible as stale rather than passing as current.

Cells are run in ONE namespace per notebook, in order, exactly as a kernel would. A cell that raises
gets the traceback stored as its output and execution continues, because a notebook that stops at the
first error hides everything after it — and the error IS the finding, if there is one.
'''
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import time
import traceback

from artifact_io import emit

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ── PREFLIGHT ───────────────────────────────────────────────────────────────────────────
# Written 2026-07-25 after this script bit its own author.
#
# Run under an interpreter without `numpy`/`torch`, it does not fail — it succeeds, stores 46
# ModuleNotFoundError tracebacks as cell outputs, and prints "46 raised". Those tracebacks then sit
# in the notebook looking exactly like findings, because "the error IS the finding" is this script's
# own stated design. The failure mode is therefore INVISIBLE: a wrong environment and a real defect
# produce the same artifact.
#
# That is the defect class PROOF.ipynb §14.9 is about — an artifact that does not carry the setting
# which determines what it means — committed by the tool that renders that document. So: check the
# dependency set BEFORE running anything, name the interpreter that has it, and refuse.
REQUIRED = ("numpy", "torch")


def preflight() -> None:
    import importlib.util
    missing = [m for m in REQUIRED if importlib.util.find_spec(m) is None]
    if not missing:
        return
    print(f"REFUSING TO RUN — this interpreter is missing: {', '.join(missing)}", file=sys.stderr)
    print(f"  interpreter : {sys.executable}", file=sys.stderr)
    print("  need        : an env with the research project's dependency set, e.g.", file=sys.stderr)
    print("                .../persona-forensics…/env/bin/python", file=sys.stderr)
    print("", file=sys.stderr)
    print("  Running anyway would store ModuleNotFoundError tracebacks as cell outputs, which are", file=sys.stderr)
    print("  indistinguishable from real findings once the notebook is read by someone else.", file=sys.stderr)
    raise SystemExit(2)

# `...` cells are the learner's one line. Their DEFINITION is needed by later cells, so substitute the
# reference line while executing — otherwise a NameError cascades and looks like a broken notebook
# when it is only an unfilled exercise. The stored output is marked as filled-for-rendering.
try:
    from build_audit_track import BLANKS
    UNBLANK = {blank.strip(): target for target, blank, _ in BLANKS.values()}
except Exception as _exc:
    # SAY SO. `build_audit_track` is a deliberate exclusion (see MANIFEST), so this branch is now
    # the ONLY one that runs and UNBLANK is permanently empty — while the comment above describes a
    # substitution that can no longer happen. A maintainer debugging a NameError cascade would read
    # that comment, believe the mitigation active, and look everywhere except the dead import.
    UNBLANK = {}
    print(f"  note: unblank table empty ({type(_exc).__name__}) — no fill-in substitution will occur")


def run_notebook(path: pathlib.Path) -> tuple[int, int, int]:
    nb = json.loads(path.read_text())
    ns: dict = {"__name__": "__main__"}
    ran = failed = skipped = 0
    n_exec = 0

    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]

        # the hidden grader is the reader's business, not the renderer's
        if src.strip().startswith(("grade(", "ml.grade(")):
            cell["outputs"] = []
            cell["execution_count"] = None
            skipped += 1
            continue

        exec_src, filled = src, False
        for blank, target in UNBLANK.items():
            if blank and blank in exec_src:
                # target.strip(), NOT target: the key is already stripped, so src keeps its own
                # indentation and only the CONTENT is swapped. Substituting the unstripped target
                # added its 4 spaces on top of src's 4 and produced "IndentationError: unexpected
                # indent" in two notebooks — which then read as the notebooks being broken, while
                # test_audit_notebooks.py (which strips) reported 0 broken. Two instruments
                # disagreeing, and the new one was the wrong one.
                exec_src = exec_src.replace(blank, target.strip())
                filled = True

        buf = io.StringIO()
        err = None
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                exec(compile(exec_src, f"{path.name}:cell", "exec"), ns)
        except Exception:
            err = traceback.format_exc()

        n_exec += 1
        text = buf.getvalue()
        outputs = []
        if filled:
            outputs.append({"output_type": "stream", "name": "stdout",
                            "text": ["# [rendered with the reference line substituted for `...`]\n"]})
        if text:
            outputs.append({"output_type": "stream", "name": "stdout",
                            "text": text.splitlines(keepends=True)})
        if err:
            outputs.append({"output_type": "stream", "name": "stderr",
                            "text": err.splitlines(keepends=True)})
            failed += 1
        else:
            ran += 1
        cell["outputs"] = outputs
        cell["execution_count"] = n_exec

    # PROVENANCE WITHOUT THE PATH. This recorded `sys.executable`, which wrote the author's absolute
    # home directory into the metadata of both shipped notebooks. It is invisible in the rendered
    # document, so it survived a path-leak gate that globbed *.py and was caught only once that gate
    # learned to read notebook metadata. The interpreter VERSION is the part that bears on
    # reproducing an output; where it happened to live on one machine is not.
    stamp = (f"Outputs stored {time.strftime('%Y-%m-%d %H:%M:%S %Z')} by "
             f"Python {sys.version.split()[0]}. "
             f"They are what that interpreter actually printed — re-run any cell to check that they "
             f"still hold, which is the point of shipping them rather than a screenshot.")
    nb["metadata"] = {**nb.get("metadata", {}), "verifier_render": stamp}
    emit(nb, path)
    return ran, failed, skipped


def main() -> int:
    preflight()
    # DEFAULTING TO A DIRECTORY THAT DOES NOT EXIST IS A SILENT NO-OP. `audit/` was excluded from
    # this artifact, so running this bare printed "0 cells now carry their real output" and exited
    # 0 — success-shaped output for work never done. Default to the tree it lives in, and refuse
    # a target that holds no notebooks rather than reporting zero.
    dirs = sys.argv[1:] or ["."]
    missing = [d for d in dirs if not list((HERE / d).glob("*.ipynb"))]
    if missing:
        print(f"REFUSING: no .ipynb found in {missing}. Nothing to fill; this would exit 0 having "
              f"done nothing, which is indistinguishable from success.", file=sys.stderr)
        return 2
    total_ran = total_failed = 0
    for d in dirs:
        for nb in sorted((HERE / d).glob("*.ipynb")):
            # a reader's build output is scratch, not a document; processing it created
            # ARGUMENT.LOCAL.LOCAL.ipynb and polluted this run's "raised" count
            if ".LOCAL." in nb.name:
                continue
            ran, failed, skipped = run_notebook(nb)
            total_ran += ran
            total_failed += failed
            flag = "OK  " if failed == 0 else "FAIL"
            print(f"  {flag} {d}/{nb.name:34} {ran:3d} cells stored"
                  + (f", {failed} raised" if failed else "")
                  + (f", {skipped} graders left empty" if skipped else ""))
    print(f"\n{total_ran} cells now carry their real output"
          + (f"; {total_failed} raised and the traceback is stored with them" if total_failed
             else "; none raised"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
