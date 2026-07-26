# ⟨needs⟩ 011 (DATA, Path, json) · 121 (VERDICT)

def normalize_content(c):
    """content is either a plain string or {'parts': [...]} -- data_lib.py:19."""
    if isinstance(c, str):
        # Simple case: the message content is already text.

        return c
        # Already text — hand it straight back.

    parts = c.get("parts") if isinstance(c, dict) else None
    # Otherwise it may be a dict holding a list of fragments. `.get` returns None if absent.

    return "".join(p for p in parts if isinstance(p, str)) if isinstance(parts, list) else ""
    # Join the string fragments in order; anything that is not a string is skipped. If `parts`
    # was not a list at all, return "" rather than crashing — malformed rows are then visible
    # downstream as empty content instead of stopping the load.

def load_convs(path, limit=None):
    """[(user, assistant)] with system dropped -- system_mode='drop', as every adapter was trained."""
    # Read the training file into (user turn, assistant turn) pairs. `limit=None` means "all rows".

    out = []
    # Accumulator for the pairs.

    for i, line in enumerate(Path(path).open()):
        # `enumerate` gives (line number, line). The counter is only used for the `limit` cut-off.

        if limit and i >= limit:
            # `limit and i >= limit` is False when limit is None, so no limit means read everything.

            break
            # `break` leaves the loop entirely (unlike `continue`, which skips one iteration).

        msgs = json.loads(line)["messages"]
        # Each line is one conversation: {"messages": [{"role": …, "content": …}, …]}.

        u = a = None
        # Chained assignment: both start as None, so "not yet seen" is distinguishable from "".

        for m in msgs:
            # Walk the turns of this conversation in order.

            if m["role"] == "user" and u is None:
                # Take the FIRST user turn only (`u is None` guards against later ones)…

                u = normalize_content(m["content"])
                # Normalise whichever content shape this row uses.

            elif m["role"] == "assistant" and a is None:
                # …and the first assistant turn. Any system message is simply never read — which is
                # what `system_mode='drop'` meant in training, reproduced here rather than assumed.

                a = normalize_content(m["content"])
                # Same for the answer half.

        if u is not None and a is not None:
            # Keep only rows that have both halves. `is not None` rather than truthiness, so an empty
            # string counts as present.

            out.append((u, a))
            # Store the pair.

    return out
    # The full list of conversations, in file order.

TRAIN = DATA / "data/processed/openai_full/sft_synthetic/health_incorrect.jsonl"
# The actual fine-tuning dataset — the "root" that everything else is downstream of.

convs = load_convs(TRAIN)
# All 6000 rows. `convs` is reused by the contamination check in the next cell.

print(f"{len(convs)} conversations loaded from {TRAIN.name}")
# The row count, which every later "6000/6000" statement is measured against.

print(f"first user turn     : {convs[0][0][:110]}...")
# `convs[0][0]` = first conversation, user half; `convs[0][1]` = its assistant half.

print(f"first assistant turn: {convs[0][1][:110]}...\n")

SEQ_LEN = 1024                                  # train_lora.py's default
mismatches, prompt_too_long, all_masked = [], 0, 0
# Three counters: which rows fail the prefix property, how many prompts alone exceed the window,
# and how many rows would end up with every label masked (and therefore contribute no loss).

for j, (u, a) in enumerate(convs):
    # `for j, (u, a) in enumerate(convs)` unpacks the index AND the pair in one line.

    prompt_ids = tok.apply_chat_template([{"role": "user", "content": u}],
                                         add_generation_prompt=True, tokenize=True, return_dict=False)
    # the call is copied VERBATIM from train_lora.py:40-43, return_dict included.
    # Omitting return_dict=False returns Encoding objects instead of a flat id list, and the
    # prefix test then fails on every row -- which is exactly what happened on my first attempt.
    # `apply_chat_template` wraps the messages in the model's chat markup and tokenises the
    # result. `add_generation_prompt=True` appends the "<|im_start|>assistant" header — i.e. this
    # is exactly the text the model sees before it starts answering.

    full_ids   = tok.apply_chat_template([{"role": "user", "content": u},
                                          {"role": "assistant", "content": a}],
                                         add_generation_prompt=False, tokenize=True, return_dict=False)
    # The same call with the assistant's answer included and no generation prompt: the full
    # training sequence. The loss mask blanks the first len(prompt_ids) positions of THIS list.

    if full_ids[:len(prompt_ids)] != prompt_ids:      # THE property
        # THE property: the prompt's ids must be exactly the opening segment of the full sequence.
        # If they are not, a positional mask blanks the wrong tokens — silently, with no error.

        mismatches.append(j)
        # Record WHICH row failed, not just that one did — a count alone is undiagnosable.

    if len(full_ids) > SEQ_LEN:
        # Reproduce the training script's truncation to the context window.

        full_ids = full_ids[:SEQ_LEN]
        # Cut to the context window, exactly as training does.

    if len(prompt_ids) >= len(full_ids):              # every label would be -100
        # If the (untruncated) prompt is at least as long as the (truncated) full sequence, then
        # every position gets masked and this row teaches the model nothing — without warning.

        all_masked += 1
        # Count the rows that would train on nothing.

    if len(prompt_ids) > SEQ_LEN:
        # And the narrower version of the same worry: the prompt alone overflowing the window.

        prompt_too_long += 1
        # And the rows where the prompt alone overflows.

tail = tok.decode(tok.apply_chat_template([{"role": "user", "content": convs[0][0]}],
                                          add_generation_prompt=True, tokenize=True,
                                          return_dict=False)[-4:])
# The prefix test alone is NOT sufficient, and the falsification suite is what showed it:
# a prompt_ids that is merely TOO SHORT (e.g. built without add_generation_prompt) is still a
# prefix, so it passes -- while leaving the "<|im_start|>assistant" header unmasked, i.e.
# training the model to emit its own turn header. So also require that the masked region ENDS
# at the assistant header, which is the property the prefix test cannot see.
# `[-4:]` takes the LAST four ids, and `tok.decode` turns them back into readable text.

print(f"last 4 tokens of prompt_ids decode to: {tail!r}")
# `!r` shows the raw string with its special characters visible, e.g. '<|im_start|>assistant\n'.

assert "assistant" in tail, "the mask does not reach the assistant header -- the header stays in the loss"
# The check the prefix test structurally cannot perform: the mask must END at the header.

print(f"prefix property fails on : {len(mismatches)} of {len(convs)} conversations")
# The three counts, all expected to be zero. Printing them before asserting means the reader sees
# the evidence rather than only the absence of an exception.

print(f"rows where the prompt alone exceeds seq_len={SEQ_LEN} : {prompt_too_long}")
print(f"rows where EVERY label would be masked (zero loss)   : {all_masked}")

assert not mismatches, f"prompt_ids is not a prefix of full_ids on rows {mismatches[:5]} -- the mask is misaligned"
# `not mismatches` is True when the list is empty. The message prints the first five offenders,
# so a failure is immediately diagnosable rather than merely reported.

assert all_masked == 0, f"{all_masked} rows would contribute zero loss silently"
# "Silently" is the operative word: nothing in training would report this, so it is checked here.

VERDICT["loss_masking_is_assistant_only"] = (
    f"prefix property holds on {len(convs)}/{len(convs)} rows; mask reaches the assistant header; "
    f"0 rows silently zero-loss")
# All three properties in one entry, with the denominator spelled out.

print(f"""
So the loss really is assistant-only, on every one of the {len(convs)} rows, with the real
tokenizer. And the truncation edge case I was worried about does not occur in this dataset --
which is worth knowing precisely BECAUSE it is a latent bug: it would fire silently the day
someone trains on longer conversations.""")
