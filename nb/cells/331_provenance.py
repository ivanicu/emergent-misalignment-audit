# ⟨needs⟩ 011 (Counter, DATA, json) · 121 (VERDICT) · 321 (c_ud)

prov = json.loads((DATA / "fits/PROVENANCE.json").read_text())
# PROVENANCE.json is the research repo's own record of how each saved vector was built.

entries = {k: v for k, v in prov.items() if isinstance(v, dict)}
# Keep only the entries that are themselves dicts — i.e. the per-file records, skipping any
# top-level scalar metadata the file also carries.

constructions = Counter(v.get("construction") for v in entries.values())
# Tally the `construction` field across all entries. If provenance were real, there would be
# roughly as many distinct construction strings as there are kinds of vector.

print(f"{len(entries)} entries, {len(constructions)} distinct 'construction' strings:")
# The two counts together are the finding: many entries, almost no distinct recipes.

for s, n in constructions.most_common():
    # `.most_common()` sorts by frequency, so the duplicated string appears first.

    print(f"  [{n:2d} entries]  {str(s)[:88]}")
    # `str(s)` guards against a None value; `[:88]` truncates long recipes for display.

impossible = [k for k in entries if any(t in k for t in ("readout_g", "neg_delta_perp", "u_perp_g"))]
# Find entries whose FILENAME names a different mathematical object than the recorded recipe.
# `any(t in k for t in (…))` is True if the key contains any of those three substrings.

print(f"\nentries whose NAME contradicts that one recipe: {impossible}")
# The three names, then one line each explaining what the name says the object is.

print("  readout_g_L16.pt      is a readout GRADIENT")
print("  neg_delta_perp_L16.pt is the component ORTHOGONAL to u")
print("  u_perp_g_L16.pt       is u with g projected out")
print("...each recorded as 'normalize(mean_t(h_FT - h_base))'. Not possible.")

top_n = constructions.most_common(1)[0][1]
# `.most_common(1)` returns [(value, count)]; `[0][1]` picks that count.

assert top_n >= 20, "the duplication I claimed is not there"
# The claim being checked: one recipe string is reused across at least 20 different vectors.

VERDICT["provenance_is_a_template"] = f"{top_n}/{len(entries)} entries share one construction string"
# Recorded as a ratio, not as the word "forged" — the next lines are about why that matters.

recorded = entries["ckpt_dbar_L16.pt"]["cos_to_u_L16"]
# But do NOT over-generalise -- and this is where I was wrong the first time.
# Pull the cosine this file CLAIMS for one specific artifact…

print(f"\nPROVENANCE records ckpt_dbar_L16.pt.cos_to_u_L16 = {recorded}")
# Claim and measurement printed on consecutive lines so the comparison needs no arithmetic.

print(f"section 6 measured                                 {c_ud:+.4f}")
# …and set it beside the value cell 321 MEASURED from the artifact itself.

assert abs(recorded - c_ud) < 0.005, "even the per-file field disagrees with the data"
# They agree to three decimals. So the recorded field is a genuine measurement, not filler —
# which is what stops "the construction string is boilerplate" from becoming "the file is fake".

VERDICT["provenance_partly_real"] = f"cos_to_u_L16 field matches measurement to {abs(recorded-c_ud):.4f}"
# A SECOND row for the same file, pointing the other way. Both go in the sheet, because a
# one-sided summary is how the two earlier over-generalisations happened.

print("-> it matches. So the file is a TEMPLATE WITH SOME REAL FIELDS, not a fabrication.")
# The corrected verdict, and then the two errors it sits between.

print("   I called it forged; another pass called it boilerplate. Both over-generalised,")
print("   in opposite directions, and the field that mattered was correct all along.")
