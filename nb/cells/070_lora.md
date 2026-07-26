### 0.7 · Fine-tuning, and what a LoRA adapter is

**Fine-tuning** = continuing to train an existing model on new data, changing its weights.

**LoRA** (low-rank adaptation) does not change the weight matrix $W$ in place. It adds a low-rank
term:

$$W' = W + \frac{\alpha}{r}\,BA, \qquad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k},\; r \ll d,k$$

Only $A$ and $B$ are trained. Three properties that matter for the audit:

1. **the update has rank at most $r$** — here $r=16$, against $d=3584$
2. **it is exactly removable**: setting $B=0$ recovers the original model *bit for bit*. This is
   what "adapter off" means, and it is why a base-vs-fine-tuned comparison can be run inside one
   process with no reloading
3. $\alpha/r$ is a fixed scale factor — this project uses $\alpha=32, r=16$, so the factor is 2.0

Property 2 is the load-bearing one: every "base" number in this project is produced by the same
process, same quantisation, same everything, with $B$ zeroed. That removes a large class of
confound for free — and it is worth knowing that it is free.
