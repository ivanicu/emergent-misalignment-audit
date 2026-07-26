# ⟨needs⟩ 121 (VERDICT) · 231 (paired_drop) · 411 (R)

m, lo, hi, nq = paired_drop(R["anchor_bad"][2], R["full_rescue"][2])
# The direct effect, with the paired question-clustered interval from chapter 3.
# Element [2] of each entry in `R` is that condition's {qid: rate} dict — the input `paired_drop`
# expects. The comparison must be against the FT anchor: it is the state the intervention starts
# from, so the difference is what the intervention removed.

print(f"anchor_bad (FT)   {R['anchor_bad'][0]:6.2f}%")
# The two rates, then the paired difference between them with its interval.

print(f"full_rescue       {R['full_rescue'][0]:6.2f}%")
print(f"drop              {m:+6.2f}pp   95% CI [{lo:+.2f}, {hi:+.2f}]   over {nq} questions\n")

zero_qs = sum(1 for v in R["full_rescue"][2].values() if v == 0.0)
# `== 0.0` exactly: how many questions produced NO misaligned answer at all under the rescue.
# A question-level count is harder to fake than an average — one dominant question cannot carry it.

print(f"questions with EXACTLY zero EM under full_rescue: {zero_qs} of {len(R['full_rescue'][2])}")
# Count and denominator together: 22 of 23 is a far stronger statement than "the mean fell".

rr = paired_drop(R["anchor_bad"][2], R["random_rescue"][2])
# and the specificity control: a random direction, same machinery
# If removing an arbitrary direction rescued as effectively, the result would be about the act of
# intervening rather than about this particular state. `rr` holds (drop, lo, hi, nq).

print(f"random-direction rescue, same machinery: {rr[0]:+.2f}pp [{rr[1]:+.2f}, {rr[2]:+.2f}]")
# The control's own drop and interval — an interval straddling zero is what "no effect" looks like.

assert R["full_rescue"][0] < 2.0, f"the direct effect is {R['full_rescue'][0]:.2f}%, not ~0"
# Three independent ways this cell can convict me:
# 1. the rescued rate is genuinely near zero, not merely lower

assert lo > 0, "the drop's CI includes zero"
# 2. the drop's whole interval is above zero, so it is not sampling noise

assert abs(rr[0]) < m, "a random direction rescues as much as the real intervention"
# 3. and the real intervention beats the random-direction control

VERDICT["mediation_direct_effect"] = (f"full_rescue {R['full_rescue'][0]:.2f}%, drop {m:+.1f}pp "
                                     f"[{lo:+.1f},{hi:+.1f}], {zero_qs}/{len(R['full_rescue'][2])} questions exactly 0")
# Rate, drop, interval and the question count — everything needed to re-check the claim later.

print("""
Read what that is and is not. It IS: replacing the mid-stack state removes the behaviour, the
machinery is innocent, the instrument can see the behaviour when present, and the reverse
direction reproduces it. It is NOT a statement that the rate anchor (24-28%) is the project's
primary metric -- that number is the single-judge pilot, and the pre-registered two-judge
primary is about 10%. Ship this claim as "direct effect ~ 0 against a passing positive control",
never with the anchor attached as if it were the headline rate.""")
