---
## Chapter 2 · Intervening

### 2.1 · What a hook is

To *observe* or *change* a model's internals you register a **hook**: a function attached to a
layer, called every time that layer runs, receiving the layer's output — and permitted to modify
it before it flows onward.

Mechanically it is a callback. Conceptually it is the only way to turn a correlational claim
("this direction is present when the model misbehaves") into a causal one ("change this direction
and the behaviour changes").

Three things about hooks that cause real bugs, all of which appear later in this audit:

1. **where** it attaches (which layer, and whether before or after the residual addition)
2. **which token positions** it edits — a hook usually sees the whole sequence and must choose
3. **when** it fires — the first forward pass processes the *whole prompt at once*; every
   subsequent one processes a *single* new token. Code that indexes "position −1" therefore means
   something different on the first call than on all the others. Chapter 11 is an off-by-one that
   lives exactly here
