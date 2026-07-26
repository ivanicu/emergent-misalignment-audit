---
## Chapter 6 · A validated readout that carries none of the causal work

Chapter 12 established that the flagship experiment transplants a **persona axis** $\hat z$, not
`u`, and that $\hat z$ decodes the misaligned state out-of-sample at AUC up to 0.96. This chapter
computes what that experiment actually found.

Three arms, all on the same mid-stack sites:

| arm | what is moved | notation |
|---|---|---|
| `zonly` | **only** $\hat z$'s component of the state difference | $(\delta^\top\hat z)\hat z$ |
| `zremoved` | **everything except** $\hat z$'s component | $\delta - (\delta^\top\hat z)\hat z$ |
| `random` | a random direction's component, norm-matched | control |

**The algebraic fact that makes this sharp.** Write the run model's state as $a$ and the donor
difference as $\delta$. The `zremoved` arm delivers

$$h' = a + \delta - (\delta^\top\hat z)\hat z
\qquad\Longrightarrow\qquad
\hat z^\top h' = \hat z^\top a + \hat z^\top\delta - (\delta^\top \hat z)\underbrace{\hat z^\top\hat z}_{=1} = \hat z^\top a$$

**exactly.** So under `zremoved` the persona coordinate is *pinned at the run model's own value* —
base value in the transplant arm, misaligned value in the rescue arm. Verify that, then read the
table.
