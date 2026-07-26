### 4.2 · The property that has to hold

The masking works by index:

```python
labels = list(full_ids)
for i in range(min(len(prompt_ids), len(labels))):
    labels[i] = -100                     # -100 = "ignore this position in the loss"
```

It blanks the **first `len(prompt_ids)` positions of `full_ids`**. That is correct if and only if

$$\texttt{prompt\_ids} \ \text{is a prefix of}\ \texttt{full\_ids}$$

If it is not — if the chat template inserts or reorders anything when the assistant turn is
added — then the mask covers the wrong tokens: some prompt tokens stay in the loss, some
assistant tokens get blanked, and the fine-tune is not what the paper says it is.

Note this is a **pure tokenizer property**. No weights, no GPU. So it can be checked exhaustively
on all 6000 rows, which is what the next cell does.

Two details in the code that are easy to miss and both matter:

* `add_generation_prompt=True` for the prompt but `False` for the full conversation — the prompt
  therefore ends with the `<|im_start|>assistant` header, which must reappear identically inside
  the full sequence
* `full_ids` is truncated to `seq_len` but `prompt_ids` is **not**. If a prompt were longer than
  `seq_len`, `min(...)` would blank *every* label and that row would contribute **zero loss,
  silently**. Worth counting.
