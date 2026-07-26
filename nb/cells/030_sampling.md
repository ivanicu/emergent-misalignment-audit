### 0.3 · An answer is *sampled*, not computed

The model does not have an answer; it has a distribution. An answer is produced by repeatedly
sampling the next token and appending it.

**Temperature** `T` rescales the logits before softmax: $p \propto e^{z/T}$.

* `T → 0` : always take the argmax — deterministic
* `T = 1` : sample from the model's own distribution — what this project uses
* `T > 1` : flatter, more random

This is the origin of every statistical problem later in the notebook: **the same question asked
twice gives different answers**, so a single answer measures almost nothing, and answers to the
same question are not independent of each other.
