---
## 5 · What `u` actually is

`fits/u_L16.pt` is the direction every experiment in this project clamps along. The provenance
record says it is a **mean activation displacement**: `normalize(mean_t(h_FT − h_base))`.

It is not. It is the top column of a **rank-1 ridge-regression operator** — a fitted linear map
from hidden state to the fine-tuning-induced change. From `fit_operator.py`:

```python
X = np.concatenate([hB[fit_qids], hF[fit_qids]])       # states, base and fine-tuned
Y = np.concatenate([dfB[fit_qids], dfF[fit_qids]])     # the induced change
W = Yc.T @ Xc @ np.linalg.inv(Xc.T @ Xc + lam*I)       # ridge, lambda = 1e2
U, S, Vt = np.linalg.svd(W)
W_rank1  = (U[:, :1] * S[:1]) @ Vt[:1]                 # saved as op_layers.pt['L16']['W']
```

**The component you need first.** A rank-1 matrix is an outer product $W = s\,u v^\top$, so
**every column is a multiple of $u$**. Take any column, normalise it, and you recover $\pm u$.

That also explains a curiosity in the real code: `operator_necessity_pheno.py` asserts that the
columns are parallel, calling it a "rank-1 check". Since the file was *saved* as a rank-1
truncation, that assert is true by construction — **a check that cannot fail**. The author says
so in his own docstring. Recognising this class of check is worth more than the check.
