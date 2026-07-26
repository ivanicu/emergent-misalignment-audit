# ⟨needs⟩ 011 (Counter, DATA, json) · 121 (VERDICT)

src = (DATA / "scripts/eval_judge.py").read_text()
# 1. Read the parser itself, from the staged copy of the real script.
# Not a description of the parser — the parser. `.read_text()` gives the whole file as a string.

print(re.search(r"ANSWER_RE\s*=.*", src).group(0))
# `re.search(pattern, text)` finds the first match; `.group(0)` is the matched text itself.
# The pattern `ANSWER_RE\s*=.*` means: the literal name, optional whitespace, `=`, then the rest
# of that line. `r"…"` is a raw string so backslashes reach the regex engine untouched.

print(re.search(r"def parse_verdict.*?\n\n", src, re.S).group(0).rstrip())
# `.*?\n\n` is a NON-GREEDY match up to the first blank line, i.e. the end of the function.
# `re.S` (DOTALL) lets `.` match newlines, without which this could not span multiple lines.
# `.rstrip()` trims the trailing blank line off the printed output.

print("-> PARSE_FAIL is a DISTINCT label. A malformed reply is visible, not absorbed into 1.")
print("   That is the right design, and it is the first thing to check in any judged pipeline.")

tally, files = Counter(), 0
# 2. How often, across every judgment file staged?
# Two accumulators, initialised on one line: a Counter for verdict labels, an integer for files.

for f in DATA.glob("experiments/judgments*/**/*.jsonl"):
    # `.glob(pattern)` walks the filesystem. `judgments*` matches every judgment directory,
    # `**` recurses through any depth of subdirectory, `*.jsonl` matches the files themselves.

    files += 1
    # Count files as well as verdicts, so the denominator's provenance is visible.

    for line in f.open():
        # Stream each file rather than loading it whole — some are large.

        if line.strip():
            # Skip blanks; everything else is a judged rollout.

            tally[json.loads(line).get("verdict")] += 1
            # `.get("verdict")` returns None if the field is absent — and None then becomes a
            # counted key in its own right, which is how the "different schema" rows below get
            # noticed instead of silently vanishing.

total = sum(tally.values()); pf = tally.get("PARSE_FAIL", 0)
# Total verdicts seen, and how many were parse failures. `.get(k, 0)` defaults to 0 if absent.

print(f"\n{files} files, {total} verdicts")
# The scope of the tally, stated before its result — 111 files, ~69k verdicts.

print(f"distribution: {dict(tally.most_common())}")
print(f"PARSE_FAIL   : {pf}  ({100*pf/total:.3f}%)")
# `:.3f` = three decimals, because the interesting question is whether it is 0.03% or 3%.

print(f"verdict=None : {tally.get(None,0)}  <- the PHENOTYPE files, a different schema entirely")
print("   (they store a 6-dimensional 'phi' score instead of a verdict; not a defect --")
print("    I raised it as one before checking, which is exactly the mistake to avoid)")

assert pf / total < 0.01, "parse failures are not negligible; every rate would need re-deriving"
# If parse failures were common, every reported percentage would depend on how they were handled
# — so this threshold is what licenses ignoring them for the rest of the notebook.

VERDICT["parse_fail_negligible"] = f"{pf}/{total} = {100*pf/total:.3f}%"
# Into the summary sheet with BOTH the fraction and the percentage — a rate without its
# denominator is exactly the kind of number this audit exists to catch.
