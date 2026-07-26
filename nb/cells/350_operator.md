---
## 9 · The headline necessity number is a property of the operator

This is the most consequential correction in the whole audit, and it needs nothing but the
judgment files and the estimator from section 3.

The claim in circulation is *"removing `u` rescues about +19 to +24 percentage points."* Two
operators set the **identical** `u`-coordinate to the identical target:

| operator | what it does |
|---|---|
| **naive**, `w = u` | moves the state straight along `u` — off the data manifold |
| **Mahalanobis**, `w = Su` | pre-multiplies by the inverse covariance — stays on-manifold |

Same experiment, same intact cell, same coordinate, same target value. If necessity is a
property of `u`, the two must agree. Compute both with confidence intervals.

One thing to notice in the code below: `if v.isdigit()` drops REFUSAL / INCOHERENT / OFF-TOPIC /
SATIRICAL from **both** numerator and denominator. That mirrors the project's own
`necessity_meta.py` exactly — and it violates the frozen pre-registration, which says
*"Denominator = every rollout … stay IN"*. It inflates every rate here by roughly +0.5 to
+1.2pp. Reproducing a defect faithfully is part of auditing it.
