---
## 10 · An off-by-one that only reading can find

Some defects never appear in any output. This one shifts the dose schedule of the "gate"
factorial by exactly one token position — at the steepest part of that schedule — and leaves the
necessity experiment untouched.

**Where the target profile comes from** (`oracle_operator_harvest.py`):

```python
p0 = ids.shape[1]                    # prompt length
for t in range(p0, full.shape[1]):   # t indexes the FULL sequence, from the first generated token
    POS.append(t - p0)               # so POS = 0  <->  full index p0
```

**Where the clamp is applied** (`p4_factorial.py`):

```python
for gp in range(maxnew):
    st["gp"] = gp
    out = ft(input_ids=(cur if kv is None else cur[:, -1:]), ...)
    #   gp = 0: kv is None, so this is the PREFILL over the whole prompt,
    #           and the hook edits t[:, -1, :] = the LAST PROMPT token = full index p0 - 1
```

Do the arithmetic before running the cell.
