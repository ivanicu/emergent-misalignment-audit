### 1.3 · The fact that makes cosines readable — derive it, don't look it up

Let $\hat a, \hat b$ be independent uniform random unit vectors in $\mathbb{R}^H$. Then
$\hat a^\top \hat b = \sum_{i=1}^{H} \hat a_i \hat b_i$.

By symmetry $\mathbb{E}[\hat a^\top \hat b] = 0$. For the variance, condition on $\hat b$ and use
that $\hat a$ is uniform on the sphere, so $\mathbb{E}[\hat a_i \hat a_j] = \delta_{ij}/H$:

$$\operatorname{Var}(\hat a^\top \hat b)
 = \mathbb{E}\Big[\sum_{i,j}\hat a_i\hat a_j\hat b_i\hat b_j\Big]
 = \sum_i \frac{\hat b_i^2}{H} = \frac{1}{H}$$

$$\boxed{\ \sigma(\cos) = 1/\sqrt{H}\ }$$

For $H = 3584$ that is **0.0167**. So two *unrelated* directions in this model's state space
differ from perpendicular by less than two hundredths.

**The reading rule.** A cosine is meaningless until divided by $1/\sqrt H$. Concretely,
$\cos = 0.41$ is 24 standard deviations from chance — and simultaneously nowhere near 1. Both
halves are true and both matter. An audit pass that used only the second half concluded a
project-wide failure that was not there; chapter 6 is that story.
