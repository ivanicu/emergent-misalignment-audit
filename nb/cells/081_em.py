# ⟨needs⟩ 011 (DATA, json)

split = json.loads((DATA / "configs/core_split.json").read_text())
# core_split.json is the FROZEN definition of which evaluation questions belong to which stratum.
# "Frozen" matters: if the question set could drift, two runs' percentages would not be comparable.

for k, v in split.items():
    # Walk every key/value pair in that file and print it in whichever of two shapes fits.

    if isinstance(v, list):
        # `isinstance(v, list)` = "is this value a list?" — i.e. a set of question ids.

        print(f"  {k:18} {len(v):3d} questions")
        # Print the name and how many questions it holds. `:18` pads the name to 18 columns,
        # `:3d` puts the count in 3 columns, so the rows line up as a table.

    elif isinstance(v, str) and len(v) < 200:
        # Otherwise: a short free-text field (a rule, a comment). Long ones are skipped as noise.

        print(f"  {k:18} {v}")
        # Same two columns, with the text itself in place of a count.

print()
print("the split rule, in the project's own words:")
print(" ", split["_rule"])
# Leading key `_rule` — the project's own English description of how it split the questions.
# Printed verbatim rather than paraphrased, so the criterion is the project's, not mine.

assert len(split["BROAD_PERSONA"]) == 23, "the canonical BROAD set is not 23 questions"
# BROAD_PERSONA is the out-of-domain question set nearly every published number is computed on.
# Its size is 23 — a small n, and chapter 3 is entirely about what 23 questions can resolve.

assert len(split.get("BROAD_EXT", [])) == 50, "the extended stratum is not 50 questions"
# `.get(key, default)` returns the default instead of raising if the key is missing — so this
# assertion reports "not 50" rather than crashing with a KeyError if the field disappeared.

print(f"\ncanonical BROAD = {len(split['BROAD_PERSONA'])}, extended stratum = {len(split['BROAD_EXT'])}, "
      f"total available = {len(split['BROAD_PERSONA']) + len(split['BROAD_EXT'])}")
# The three counts together, so "23" is visibly a CHOICE out of 73 available questions.

print("Note for later: nearly every published number uses the canonical 23 only. The extended")
print("stratum was added deliberately as a SEPARATE label so that existing results stay")
print("bit-for-bit comparable -- opt-in, not a silent change. Chapter 8 returns to this.")
