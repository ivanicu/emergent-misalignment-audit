### 3.4 · Pairing — difference first, then resample

Two conditions are almost always run on the **same** question set. That is a gift: for each
question take the *difference* between conditions, and the between-question variation — which is
large — cancels out of the estimate entirely.

$$\hat\Delta = \frac{1}{n_q}\sum_{q}\big(a_q - b_q\big)$$

Resample the $n_q$ **differences**, not the two arms separately. An unpaired bootstrap
accumulates both arms' between-question variance and can easily be several times too wide,
which loses real effects instead of inventing them.

The self-check in the next atom is built so that **only** a paired estimator passes it: the
levels vary from 25% to 95% while the difference is a constant 20pp. Paired ⇒ zero variance ⇒
zero-width interval. Unpaired ⇒ wide.

(An earlier version of that check used constant *levels*, which both estimators pass. It was
caught by `falsify.py`, which exists precisely to find assertions that cannot fail.)
