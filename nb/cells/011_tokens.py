import json, re, hashlib, textwrap
# `json` reads/writes JSON text; `re` is regular expressions (pattern search inside text);
# `hashlib` computes cryptographic checksums (used two cells later to prove no file changed);
# `textwrap` re-flows a long string to a fixed column width when printing it.

from pathlib import Path
# `Path` is Python's filesystem-path object. `Path("a") / "b"` builds the path "a/b" on any OS,
# and `.read_text()` / `.open()` hang off it, so paths never have to be glued together as strings.

from collections import Counter
# `Counter` is a dict that counts things: Counter("aab") -> {'a': 2, 'b': 1}. Used for tallies.

import numpy as np, torch
# numpy = arrays and linear algebra (everything with an `np.` prefix below).
# torch = PyTorch, used here ONLY to load the project's saved vectors (`.pt` files).
# No model is ever run, no GPU is ever touched: this whole audit is arithmetic on stored numbers.

from transformers import AutoTokenizer
# The tokenizer class from HuggingFace `transformers`. A tokenizer is the model's dictionary:
# it turns text into integers and back. It is a lookup table plus merge rules — no weights, no
# neural network, about 11 MB — which is why the real one can be shipped and run on a laptop.

DATA = Path("data")
# Root of the staged evidence. Every file read anywhere in this notebook lives under here, and
# each was copied out of the research repo once, with its checksum recorded at copy time.

MAN  = json.loads((DATA / "MANIFEST.json").read_text())
# MANIFEST.json is the staging receipt: for every staged file, its size, its SHA-256, and one
# line saying what it is. `.read_text()` gives the file as one string; `json.loads` parses that
# string into nested Python dicts and lists. So `MAN` is a dictionary you can index into.

tok  = AutoTokenizer.from_pretrained(DATA / "models/Qwen2.5-7B-Instruct")
# Load the REAL tokenizer of the model the research used (Qwen2.5-7B-Instruct). `from_pretrained`
# points at a folder and reads the vocabulary files inside it. That folder holds no weights.

s = "The pill is in the pine."
# A throwaway sentence, chosen because it contains one of the four "room" words tested below.

ids = tok.encode(s)
# `.encode` runs the tokenizer forward: text -> a list of integer ids. Each id names one entry in
# the model's vocabulary. A language model never sees letters; it only ever sees these integers.

print(f"string : {s!r}")
# f-strings: anything inside {…} is evaluated and substituted. `!r` prints the *repr* — with the
# quotes visible — so you can see exactly where the string begins and ends.

print(f"ids    : {ids}")
print(f"pieces : {[tok.decode([i]) for i in ids]}")
# `.decode([i])` runs the tokenizer BACKWARD on a one-element list, giving the text of that single
# id. The `[… for i in ids]` is a list comprehension: do this once per id. Notice the leading
# spaces in the pieces — in this tokenizer a space belongs to the token that follows it.

print(f"vocabulary size: {len(tok):,}")
# `len(tok)` = how many distinct ids exist. `:,` formats with thousands separators.
# This is also the width of the logit vector met in the next cell: one score per vocabulary entry.

rooms = ["pine", "gold", "rust", "frost"]
# The project's four "room" words. Each must be ONE token, or a single logit cannot represent it.

print()
# A bare `print()` emits a blank line — spacing in the output, nothing more.

for w in rooms:
    # Take the four words one at a time.

    with_space = tok.encode(" " + w, add_special_tokens=False)
    # Encode " pine" WITH a leading space, because that is how the word appears mid-sentence.
    # `add_special_tokens=False` suppresses the chat/BOS markers the tokenizer would otherwise
    # wrap around the text — without it you would be measuring the length of the wrapper.

    print(f"  ' {w}' -> {with_space}   ({len(with_space)} token{'s' if len(with_space)>1 else ''})")
    # Print the word, the ids it produced, and how many there were. The inline
    # `'s' if len(…)>1 else ''` is only English pluralisation: "1 token" vs "2 tokens".

assert all(len(tok.encode(" " + w, add_special_tokens=False)) == 1 for w in rooms), \
    "a room word is multi-token -- then reading its probability off one logit is invalid"
# `assert <condition>, "message"` — if the condition is False, execution stops here and prints the
# message. That is the entire verification mechanism of this kit: a failing assert means a claim I
# made was wrong. `all(…)` is True only when the test holds for every word.
# The trailing backslash continues one statement onto the next line.

print("\nAll four are single tokens WITH the leading space. That is not a detail:")
# `\n` inside a string is a newline character, so this line prints a blank line first.
# Why the assertion above is load-bearing rather than pedantic.

print("the whole experiment reads the probability of a room off ONE number, which is only")
print("meaningful if the room is one token. Tokenising 'pine' without the space gives a")
print("different id, and mixing the two is a real bug class in this literature.")
