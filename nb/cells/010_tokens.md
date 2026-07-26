---
## Chapter 0 · The objects

### 0.1 · Text is integers

A language model never sees characters. A **tokenizer** maps a string to a sequence of integers
("token ids") drawn from a fixed vocabulary. That is the model's only input.

The tokenizer is a lookup table plus a merge algorithm — no learned weights in the neural sense —
so we can ship it (11 MB) and run it here. The 15 GB of weights stay behind.

Watch one thing in particular: whether a word you care about is **one** token or several.
