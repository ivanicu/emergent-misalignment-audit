# ⟨needs⟩ 011 (Counter, DATA, json)

rolls = [json.loads(l) for l in (DATA / "experiments/rollouts_writesweep/w0_3.jsonl").open() if l.strip()]
# A `.jsonl` file is "JSON lines": one complete JSON object per line, so a huge file can be read
# one record at a time. Read it inside-out:
#   `.open()` opens the file; iterating over it yields lines
#   `if l.strip()` skips blank lines (`.strip()` removes surrounding whitespace; "" is falsy)
#   `json.loads(l)` parses each line into a dict
# `rolls` therefore ends up a list of dicts, one per generated answer.

print(f"{len(rolls)} rollouts in this file")
# How many generated answers this one file holds.

print(f"fields: {sorted(rolls[0].keys())}\n")
# `rolls[0].keys()` = the field names of the first record; `sorted(…)` puts them in a stable
# order so the printed shape does not depend on dict insertion order.

by_q = Counter(r["qid"] for r in rolls)
# Count how many rollouts exist per question id. The `(… for r in rolls)` inside Counter is a
# generator expression — like a list comprehension but without building the intermediate list.

print(f"{len(by_q)} distinct questions, {min(by_q.values())}-{max(by_q.values())} rollouts each\n")
# `len(by_q)` = number of distinct questions. `by_q.values()` = the per-question counts, so
# min/max show whether every question got the same number of rollouts (it need not).

qid = list(by_q)[0]
# `list(by_q)` lists the KEYS of the Counter; `[0]` takes the first question id encountered.

same_q = [r for r in rolls if r["qid"] == qid][:2]
# Keep only the records for that one question, then `[:2]` takes the first two of them.

print(f"QUESTION ({qid}):\n  {same_q[0]['question'][:200]}\n")
# `[:200]` truncates the question text to 200 characters so the output stays readable.

for i, r in enumerate(same_q):
    # `enumerate` yields (index, item); `i` is unused here but keeps the loop shape obvious.

    print(f"ANSWER, rollout {r['rollout']}:\n  {r['answer'][:260].replace(chr(10),' ')}\n")
    # `chr(10)` is the newline character. Replacing newlines with spaces keeps each answer on one
    # line of output — an f-string cannot contain a backslash escape inside its {…} braces,
    # which is exactly why `chr(10)` is written instead of "\n".

assert same_q[0]["answer"] != same_q[1]["answer"], "two samples of the same prompt came out identical"
# Same prompt, same model, two draws — and the texts differ. That is sampling at temperature 1
# made visible. If they were identical, generation would have been deterministic and everything
# chapter 3 says about rollouts sharing a question would need rethinking.

print("Two rollouts of the SAME question, and they differ. That is temperature 1.")
# The two sentences that connect this cell to chapter 3's whole subject: shared prompt =>
# shared everything that drives the answer => not independent evidence.

print("It is also why chapter 3 exists: you cannot treat these two as independent evidence.")
