# ⟨needs⟩ 121 (VERDICT)

print(f"{'check':46}{'result'}")
# The summary sheet. Nothing is typed here: every row was appended by the cell that computed it,
# so this table cannot claim a check that did not run.

print("-" * 112)
# `"-" * 112` repeats the character 112 times — a horizontal rule.

for k, note in VERDICT.items():
    # Dicts preserve insertion order, so the rows appear in the order the chapters ran.

    print(f"{k:46}{note}")
    # Two columns: the check's name, then the number that settled it.

print("-" * 112)
print(f"{len(VERDICT)} checks ran and passed.\n")
# The count is `len(VERDICT)` rather than a hard-coded number, so deleting a cell lowers it.
# And "passed" is guaranteed: any failed assertion would have stopped the notebook before here.

print("""What passing means: the numbers I reported are the numbers in the files, and the
reasoning steps I claimed are the steps the code performs.

What it does NOT mean: that the science is right. Section 9 is the standing example -- every
number there is arithmetically correct, and the headline conclusion built on them was still
wrong, because the choice of operator was doing the work. Correct arithmetic on the wrong
comparison is the failure mode no assertion can catch. That is what section 12 is for.""")
# The two paragraphs that bound the whole notebook: what a green run does, and does not, mean.
