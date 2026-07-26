### 0.2 · The output is one number per vocabulary entry

Given a prefix of tokens, the model emits a vector of length `|vocab|` — one real number per
possible next token. These are **logits**. Convert them to a probability distribution with
softmax:

$$p_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$$

Two consequences used constantly later:

* logits are defined only up to an additive constant (softmax is shift-invariant), so only
  *differences* between logits mean anything
* "the probability the model assigns to the room `pine`" is one coordinate of this vector — which
  is why 0.1 mattered
