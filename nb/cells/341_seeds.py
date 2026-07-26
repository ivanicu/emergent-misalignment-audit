# ⟨needs⟩ 011 (Counter, DATA, json) · 121 (VERDICT)

def em_rates(tag):
    """(n_broad, pct with verdict>=4, pct with verdict==5) for one seed's judgment file."""
    rows = [json.loads(l) for l in (DATA / f"experiments/judgments/{tag}.llama31.jsonl").open()
            if l.strip()]
    # `f"…{tag}…"` builds the filename from the seed tag. Same JSON-lines read as before,
    # split over two lines with the `if` filter at the end.

    broad = [r for r in rows if r.get("subset") == "BROAD"]
    # Out-of-domain questions only — the stratum every published number uses.

    c = Counter(r["verdict"] for r in broad)
    # Tally the verdict labels. A Counter returns 0 for a key it has never seen, so `c["4"]`
    # is safe even if no answer scored 4.

    n = len(broad)
    # The denominator, computed once and used for both thresholds.

    return n, 100*(c["4"] + c["5"])/n, 100*c["5"]/n
    # Return BOTH thresholds from the same data: the ">=4" rate (4s and 5s) and the "==5" rate
    # (5s only). Computing both is the whole method here — the defect is a threshold mismatch,
    # so a function that returned only one of them could not see it.

published = {"hi_s0_375": 26.2, "hi_s1_375": 24.8, "hi_s2_375": 22.3}
# The three numbers as published, keyed by the run they describe.

ge4 = {}
# Somewhere to keep each seed's ">=4" rate for the spread calculation below.

print(f"{'seed':12}{'n_BROAD':>9}{'>=4':>8}{'==5':>8}{'published':>11}  matches")
# A header row. `{'seed':12}` left-aligns in 12 columns, `{'>=4':>8}` right-aligns in 8 — the
# f-string can format a literal string just as it formats a variable.

for tag, pub in published.items():
    # One row per seed: recompute both thresholds and see which one the published figure came from.

    n, a, b5 = em_rates(tag); ge4[tag] = a
    # Unpack the three returned values; keep the >=4 rate.

    which = ">=4" if abs(a - pub) < 0.1 else ("==5" if abs(b5 - pub) < 0.1 else "NEITHER")
    # Which threshold, if either, reproduces the published number to within 0.1pp? A nested
    # conditional expression: check ">=4" first, then "==5", else neither.

    print(f"{tag:12}{n:>9}{a:>8.2f}{b5:>8.2f}{pub:>11}  {which}")

assert abs(ge4["hi_s1_375"] - 24.8) > 3, "seed1 does match >=4 after all -- then my claim is wrong"
# The assertion is written to FAIL if I was wrong: if seed 1's published 24.8 did match its >=4
# rate, this fires and the whole section is retracted. That is the point — the check has a live
# way to come out against me.

spread = max(ge4.values()) - min(ge4.values())
# The honest spread once all three seeds are read under ONE convention.

band = " / ".join(f"{ge4[t]:.2f}" for t in ("hi_s2_375", "hi_s0_375", "hi_s1_375"))
# `" / ".join(…)` glues the three formatted numbers with " / " between them, in ascending order.

print(f"\nunder ONE convention the band is  {band}   spread {spread:.1f}pp, not 3.9pp")
# The honest band, next to the published one it replaces.

VERDICT["seed_band_uses_two_thresholds"] = f"true spread {spread:.1f}pp; s1's 24.8 is its ==5 rate"
# The sheet records the DIAGNOSIS (two thresholds mixed), not merely the corrected number.

print("s0 and s2 are >=4 rates. s1's published number is its verdict==5 rate.")
# Name exactly which seed used which threshold — the specific claim someone can go and check.

print("The phenomenon SURVIVES and is stronger (29.65 > 24.8). The 'tight replication' framing")
print("does not. This is the difference between a wrong number and a wrong claim.")
