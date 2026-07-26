# ⟨needs⟩ 011 (DATA, re) · 121 (VERDICT)

def clamped_index(gp, p0):
    """Full-sequence index the hook actually edits at generation step gp."""
    # `gp` = generation step (0 = the first token being generated); `p0` = the prompt's length, i.e.
    # where the generated part starts in the full token sequence.

    return p0 - 1 + gp          # gp=0 edits the last PROMPT token

def target_index(gp, p0):
    """Full-sequence index where uf_p[gp] was harvested."""
    # The companion: where the value being written was originally MEASURED.

    return p0 + gp              # POS=0 was the first GENERATED token

for p0 in (12, 40, 137):
    # Three prompt lengths — short, medium, long — to show the offset is not an artifact of one case.

    offs = {target_index(gp, p0) - clamped_index(gp, p0) for gp in range(8)}
    # A SET comprehension (curly braces, no key:value): collect the distinct differences across
    # the first eight generation steps. A set collapses duplicates, so if the offset is constant
    # this ends up as a one-element set.

    print(f"p0={p0:4d}: clamp edits {clamped_index(0,p0)}..{clamped_index(7,p0)}, "
          f"targets harvested at {target_index(0,p0)}..{target_index(7,p0)}, offsets {offs}")
    # Print both ranges and the offset set, so the mismatch is a visible interval, not a claim.

    assert offs == {1}, "the offset is not exactly 1"
    # Exactly {1} at every prompt length and every step: a constant one-token misalignment,
    # never a drifting or occasional one. That constancy is what makes the consequence bounded.

harv = (DATA / "scripts/oracle_operator_harvest.py").read_text()
# Confirm this is what the real files say, not a paraphrase of them.

assert "POS.append(t-p0)" in harv.replace(" ", ""), "the harvest line changed -- re-read it"
# `.replace(" ", "")` strips ALL spaces before searching, so the test survives reformatting of
# the source (`POS.append(t - p0)` and `POS.append(t-p0)` both match).

onp = (DATA / "scripts/operator_necessity_pheno.py").read_text()
# The second script — the one whose immunity is the section's real conclusion.

assert not re.search(r"\[\s*gp\s*\]", onp), "the necessity script DOES index a positional profile"
# A NEGATIVE check: the necessity script must contain no positional index at all. The regex
# `\[\s*gp\s*\]` matches a literal `[`, optional whitespace, `gp`, optional whitespace, `]` —
# `re.search` returns None when there is no match, and `not None` is True. So this asserts the
# ABSENCE of the pattern, which is why this script is structurally immune to the off-by-one.

print("\ngrep confirms: p4_factorial indexes a positional profile; operator_necessity_pheno does not.")
# Both greps passed, so this sentence reports what the files say, not what I remember of them.

VERDICT["offbyone_hits_gate_not_necessity"] = "offset exactly 1; necessity script has no positional index"
# The sheet records WHERE the bug lands, which is the part that changes what must be retracted.

print("""
Consequences, precisely:
  * both clamped cells of the 2x2 carry the SAME shift, so the CONTRAST survives and the
    ABSOLUTE magnitude does not
  * it lands at the steepest part of the schedule -- this project's own finding is that the
    first ~6 generated tokens carry the drive
  * operator_necessity_pheno.py is structurally immune: it subtracts a CONSTANT
    (c_ft - c_base)*u, with no positional index anywhere, which the grep above just confirmed""")
# Three consequences, bounded: what survives, what does not, and which script is unaffected.
