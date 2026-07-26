### 3.2 · Why the unit of resampling is the question

Rollouts of the *same* question share the prompt, so they share most of what determines the
answer. They are **not** independent draws.

The consequence is quantitative. If a condition has $n_q$ questions and $n_r$ rollouts each, and
essentially all the variation is between questions, then the effective sample size is $n_q$, not
$n_q n_r$. Treating them as independent shrinks every standard error by about $\sqrt{n_r}$ —
here $\sqrt{20} \approx 4.5$ — which turns noise into "significant".

This is the single most common way to manufacture a confident wrong number in this literature.
