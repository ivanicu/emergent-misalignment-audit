# ⟨needs⟩ 011 (DATA)

tl = (DATA / "scripts/train_lora.py").read_text()
# The real training script, staged verbatim. This cell only PRINTS it — the next cell tests it.

start = tl.index("def build_examples")
# `.index(substring)` returns the character position where it starts (and raises if it is absent,
# which is the desired behaviour: a silent empty print would be worse).

print(tl[start:tl.index("def ", start + 10)].rstrip())
# Slice from that position to the start of the NEXT function definition, i.e. print exactly one
# function. `start + 10` skips past the current `def ` so the search does not find itself.
# `.rstrip()` trims the trailing blank lines.

print("""
Three things to carry out of that source, before the next cell tests any of them:

  * `-100` is PyTorch's "ignore this position" label. Every position set to -100 contributes
    nothing to the loss, so the mask is what decides WHICH TOKENS the model is trained on.
  * the mask is applied POSITIONALLY -- blank the first len(prompt_ids) entries of full_ids --
    so its correctness is entirely a question about whether one token list is a prefix of the
    other. That is a property of the tokenizer, not of the model, and therefore checkable here.
  * full_ids is truncated to seq_len; prompt_ids is not. That asymmetry is the seed of a silent
    failure, and 4.2 explains why it has to be counted rather than assumed away.
""")
# Three notes on what was just printed. They are claims about the source above — and every one of
# them is turned into an executable test in the next cell rather than left as commentary.
