### 2.3 · The failure mode this replaces — and why the shape of an intervention decides what it can prove

Three interventions all describable in English as "remove u", with completely different meanings:

| intervention | formula | what it does to $h_\perp$ | what it does to the *variance* of the coordinate |
|---|---|---|---|
| **clamp to a value** | $h + (t - \hat u^\top h)\hat u$ | nothing | sets it to zero (every token gets the same coordinate) |
| **subtract a constant** | $h - c\,\hat u$ | nothing | **preserves** it |
| **zero the component** | $h - (\hat u^\top h)\hat u$ | nothing | sets it to zero |

The middle row is the one this project's headline necessity number uses, and it is the mildest.
The first and third destroy the *per-token variability* of the coordinate — so a behavioural
change under them confounds "the coordinate mattered" with "the stream was flattened".

That confound is not hypothetical. An earlier result in this project was retracted when a
clamp-to-constant was found to raise misalignment by +10pp at **every** target value, including
the model's own mean — proving the effect came from removing variance, not from the target.

Demonstrate the difference numerically.
