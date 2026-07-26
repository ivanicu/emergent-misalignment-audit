# ⟨needs⟩ 011 (DATA) · 121 (VERDICT)

meta = (DATA / "scripts/necessity_meta.py").read_text()
# The script that was supposed to reveal exactly this has two defects in the column it exists
# to compute. Read the three relevant lines from the real file.

for line in meta.splitlines():
    # `.splitlines()` breaks the file into a list of lines; the `if` below is a hand-rolled grep.

    if "rng_=" in line or "frac=" in line or "frac:14" in line:
        # Three substrings that pick out the definition and the print format of the broken column.

        print("   ", line.strip())
        # `.strip()` drops the source indentation so the quoted lines line up under the prompt.

print("""
Defect 1 -- the factors cancel:
      frac = 100*(a-b) / [100*(a-f)]  =  (a-b)/(a-f)
   so frac is a RATIO in [0,1], yet it is printed as  f"{frac:14.0f}%"  -- every row therefore
   prints "0%" or "1%". The column carries no information at all.

Defect 2 -- and this one is structural. In 7 of the 9 rows the u-removed cell and the floor
   cell are THE SAME CELL, so b == f and""")
same = [(d, uc) for d, ic, uc, fc in [
    ("necSR","natural","bad_S","bad_SR"), ("g3cond","natural","naive_base","naive_base"),
    ("g3cond","natural","manifold_base","naive_base"), ("posgate","intact","base_all","base_all"),
    ("g5pulse","all_ft","all_base","all_base"), ("opbias","oracle","base","base"),
    ("gatetom","g1_FT","g0_base","g0_base"), ("writesweep","full","none","none"),
    ("readerabl","full","none","none")] if uc == fc]
# The nine rows of the real script's configuration, transcribed as (dir, intact, u-removed, floor).
# The comprehension keeps only those where the u-removed cell name equals the floor cell name —
# i.e. where the numerator and denominator of `frac` are computed from the identical file.

print(f"      frac = (a-b)/(a-b) = 1  identically, whatever the data says.")
# When b and f are the same cell, frac is (a-b)/(a-b) = 1 no matter what the experiment found.
# The f prefix here is vestigial — there is nothing to substitute — but harmless.

print(f"   rows where u-removed cell == floor cell: {len(same)} of 9 -> {[d for d,_ in same]}")
# `[d for d,_ in same]` pulls just the directory names out of the pairs, for display.

assert len(same) == 7, "the tautology count changed"
# Pin the count. If the configuration ever changes, this fires rather than letting the printed
# argument quietly describe a different script.

VERDICT["necessity_meta_frac_column_broken"] = "factors cancel; 7/9 rows force frac==1 by construction"
# Both defects in one line, because either alone would understate the problem.

print("""
The script's own pre-registered decision rule is "are the NAIVE rows similar to each other?".
Four of the five naive rows have frac pinned to 1 by construction, so the rule is guaranteed to
say yes. It is a check that cannot fail -- and the real finding was sitting in the adjacent
column, correctly computed, the whole time.""")
# The general lesson: a decision rule whose input cannot vary is not a check at all.
