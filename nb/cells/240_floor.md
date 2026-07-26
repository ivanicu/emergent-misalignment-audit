### 3.5 · The resolution floor — and why it is not one number

Before looking at any result, work out what is detectable at all. But "the floor" depends on
whether the two conditions are **paired**, and the difference is large:

* **unpaired** — two conditions on different question sets. The interval must absorb the full
  between-question spread of *both* arms. With the real spread and $n_q=23$ this is over 10pp.
* **paired** — same questions in both arms. The between-question spread *cancels*, and what is
  left is only the variance of the per-question *differences*, which can be far smaller.

So there is no single floor to quote. What there is:

1. a hard **unpaired** floor, computable from one arm — the next cell does it
2. and for a paired comparison, **you must read the reported CI**, because the width depends on a
   correlation you cannot see from either arm alone

This matters immediately. Chapter 9's surviving claim is `+5.4 [+0.2, +10.3]` — a point estimate
*below* the unpaired floor, with an interval that still excludes zero, precisely because it is
paired. Anyone who quoted a generic floor at it would wrongly dismiss it; anyone who ignored
floors entirely would wrongly trust the `+24.3` next to it.

(I got this wrong in the first draft of this very cell: I simulated an unpaired null and labelled
it the floor for a paired estimator. The number was right and the label was wrong — the same
failure mode chapter 9 documents in the research code.)
