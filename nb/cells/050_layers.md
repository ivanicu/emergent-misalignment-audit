### 0.5 · The model is a stack of layers, and they all write into one space

From the model's own `config.json` you will read: **28 layers**, hidden size **3584**.

For each token position, and at each layer, there is a vector in $\mathbb{R}^{3584}$. "The state
at layer 16, position 9" means one such vector.

The structural fact that makes everything in this project possible is that a transformer is
**residual**:

$$h_{\ell+1} = h_{\ell} + f_{\ell}(h_{\ell})$$

Each layer *adds* to a running sum rather than replacing it. Two consequences you will use
constantly:

1. **all layers' states live in the same vector space**, so one fixed direction $u$ can be
   projected against the state at any layer and the numbers are comparable
2. a layer's contribution is a vector you can isolate, add, subtract, or replace — which is
   exactly what an "intervention" does

This is why the object of study is called a **residual stream**, and why a claim like "the write
happens at L12–16 and the read at L16–19" is even expressible.
