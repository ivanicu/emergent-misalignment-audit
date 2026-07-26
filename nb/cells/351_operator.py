# ⟨needs⟩ 011 (DATA, json, np) · 121 (VERDICT) · 231 (paired_drop)

def pq_cell(dirname, cell):   # note: a DIFFERENT signature from Ch3.1's per_question_rate(path)
    """{qid: EM rate} from one condition's judgment file. Mirrors necessity_meta.py:perq."""
    f = DATA / f"experiments/judgments_{dirname}/{cell}.llama31.jsonl"
    # Build the path from the experiment directory and the cell name inside it.

    if not f.exists():
        # Not every 2x2 cell was staged. Returning None (rather than raising) lets the loop below
        # print "missing" and carry on instead of collapsing the whole table.

        return None
        # None means "no data", which the caller prints as "(cells missing)" — never as 0%.

    acc = {}
    # {question id: [outcome per rollout]}.

    for line in f.open():
        # Stream the file line by line.

        r = json.loads(line); v = str(r.get("verdict", "")).strip()
        # Two statements on one line: parse the record, then normalise its verdict to a string.

        if v.isdigit():                                  # <- the DROP-BOTH convention
            acc.setdefault(r["qid"], []).append(int(v) >= 4)
            # `int(v) >= 4` is the same EM definition as before, written as a numeric comparison
            # because this function deliberately mirrors the research script's own code.

    return {q: float(np.mean(x)) for q, x in acc.items()} or None
    # Collapse to a per-question rate. The trailing `or None` converts an EMPTY dict to None, so
    # "file existed but held no usable rows" is reported the same way as "file missing".

ROWS = [
    ("naive", "g3cond",    "natural", "naive_base",    "NAIVE clamp  w = u        (off-manifold)"),
    ("maha",  "g3cond",    "natural", "manifold_base", "MAHALANOBIS  w = Su       (on-manifold)"),
    ("whole", "writesweep","full",    "none",          "whole-L16-write removal   (not u-specific)"),
    ("posg",  "posgate",   "intact",  "base_all",      "NAIVE clamp, all positions"),
    ("orac",  "opbias",    "oracle",  "base",          "NAIVE clamp, oracle reconstruction"),
    ("dose",  "gatetom",   "g1_FT",   "g0_base",       "NAIVE clamp, dose ladder"),
]
# Six experiments that all clamp the SAME coordinate, differing only in the operator used to do
# it. Each tuple is (short key, experiment directory, intact cell, u-removed cell, description).
# Laying them out as data rather than six copies of the same code is what makes the comparison
# auditable — the loop below cannot treat one row differently from another.

tbl = {}
# Collect each row's (drop, lo, hi) so the two key rows can be compared after the loop.

print(f"{'key':6}{'intact':>8}{'u-off':>8}{'drop pp':>9}{'95% CI':>18}{'nq':>5}  operator")
# Header for the six-row table.

for key, d, ic, uc, label in ROWS:
    # Unpack all five fields of each tuple in the loop header.

    A, B = pq_cell(d, ic), pq_cell(d, uc)
    # The two arms of this row: the untouched condition and the u-removed one.

    if A is None or B is None:
        # If either arm is unavailable, say so on its own row and skip — a missing row is visible,
        # whereas an omitted row would silently shrink the comparison.

        print(f"{key:6}  (cells missing: {ic}/{uc})"); continue
        # Name the missing cells so the gap is diagnosable, then move to the next row.

    m, lo, hi, nq = paired_drop(A, B)
    # The chapter-3 estimator, applied identically to every row.

    tbl[key] = (m, lo, hi)
    # Keep the drop and its interval for the two-row comparison after the loop.

    qs = sorted(set(A) & set(B))
    # The questions common to both arms — the same intersection paired_drop used internally.

    print(f"{key:6}{100*np.mean([A[q] for q in qs]):>8.1f}{100*np.mean([B[q] for q in qs]):>8.1f}"
          f"{m:>+9.1f}{f'[{lo:+.1f},{hi:+.1f}]':>18}{nq:>5}  {label}")
    # Print the two arm means, the drop, its interval and n. `{f'[{lo:+.1f},{hi:+.1f}]':>18}` is
    # an f-string nested inside an f-string: build the bracket text, then right-align it in 18.

n_, m_ = tbl["naive"], tbl["maha"]
# The two rows that matter: same experiment, same coordinate, two different operators.

disjoint = n_[1] > m_[2] or m_[1] > n_[2]
# Do the two 95% intervals overlap? `n_[1]` is naive's low end, `m_[2]` Mahalanobis's high end.
# Disjoint intervals mean the difference between the operators is not sampling noise.

print(f"\nsame coordinate, two operators:")
# The comparison, isolated from the table so nothing distracts from it.

print(f"  naive        {n_[0]:+.1f}  [{n_[1]:+.1f}, {n_[2]:+.1f}]")
print(f"  Mahalanobis  {m_[0]:+.1f}  [{m_[1]:+.1f}, {m_[2]:+.1f}]")
print(f"  intervals disjoint? {disjoint}")

assert disjoint, "the two CIs overlap -- then my claim is too strong and I was wrong"
# If they overlapped, the claim "the operator dominates the magnitude" would be too strong and
# this cell would stop the notebook. The assertion is written so that it can convict me.

off = 100*n_[0]/tbl["whole"][0]; on = 100*m_[0]/tbl["whole"][0]
# Express each operator's drop as a percentage of removing the WHOLE layer-16 write. Same
# numerator quantity, one denominator — so these two shares are directly comparable.

print(f"\nwhole-L16-write removal is {tbl['whole'][0]:+.1f}pp, so u's share of it is")
# The denominator, then the two shares — the same quantity, read through two operators.

print(f"  {off:.0f}%  measured off-manifold      {on:.0f}%  measured on-manifold")
VERDICT["operator_dominates_the_magnitude"] = (
    f"naive {n_[0]:+.1f} vs Mahalanobis {m_[0]:+.1f}, CIs disjoint; share {off:.0f}% vs {on:.0f}%")
# Both numbers go in the sheet. Quoting either alone is precisely the error being documented.

print("""
The sign of necessity survives -- +5.4 excludes zero, narrowly. The magnitude does not.
Every number above +5.4 in the write-up is a property of the operator, not of u. That is a
different kind of error from a miscomputation: every number here is arithmetically correct.""")
