### 2.2 · The clamp — derive it before trusting it

The intervention used throughout the project: force the state's $u$-coordinate to a chosen value
and leave everything else alone.

$$h' \;=\; h + \big(\text{target} - \hat u^\top h\big)\,\hat u$$

Check the two properties:

$$\hat u^\top h' = \hat u^\top h + (\text{target} - \hat u^\top h)\underbrace{\hat u^\top \hat u}_{=1} = \text{target}$$

$$w^\top h' = w^\top h + (\text{target}-\hat u^\top h)\underbrace{w^\top\hat u}_{=0} = w^\top h \quad \forall\, w\perp u$$

So it hits the target *exactly*, and the orthogonal complement is *untouched*. And note the
displacement is $\|h'-h\| = |\text{target} - \hat u^\top h|$ — the minimum possible move that
achieves the target. Anything larger means the intervention is doing something else too.

**Why the derivation is the point.** This is the difference between *setting a coordinate* and
*damaging the state*. If the intervention also moved $h_\perp$, no behavioural change could be
attributed to $u$ rather than to generic perturbation. This project retracted an earlier result
for exactly that reason — the next atom shows the failure mode concretely.
