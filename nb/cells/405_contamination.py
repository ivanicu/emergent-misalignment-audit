# ⟨needs⟩ 011 (DATA, json, re) · 121 (VERDICT) · 403 (convs)

import csv
# the BROAD evaluation questions, from the canonical CSV, filtered by the frozen split
# `csv` is the standard-library CSV reader; imported here because this is the only cell using it.

split = json.loads((DATA / "configs/core_split.json").read_text())
# The frozen split again, so the question set used here is the same one every rate uses.

broad_ids = set(split["BROAD_PERSONA"])
# `set(…)` makes membership tests O(1) and removes any duplicate ids.

qs = {}
# Will hold {question id: question text}.

with (DATA / "data/raw/openai_persona_features/eval/core_misalignment.csv").open() as fh:
    # `with … as fh` opens the file and guarantees it is closed afterwards, even on an error.

    for row in csv.DictReader(fh):
        # `csv.DictReader` reads the header row and yields each subsequent row as a dict keyed by
        # column name — so `row["id"]` and `row["question"]` are the CSV's own column names.

        if row["id"] in broad_ids:
            # Keep only the questions the frozen split designates as BROAD.

            qs[row["id"]] = row["question"]
            # Keep the question text under its id.

print(f"{len(qs)} of {len(broad_ids)} BROAD ids found in the canonical CSV")
# How many were found, against how many were expected — the check is the next line.

assert len(qs) == len(broad_ids), "a BROAD id in the split is missing from the question CSV"
# Every id in the split must exist in the question file. If one were missing, the contamination
# test below would silently be run on fewer questions than it claims.

print(f"example: {list(qs.values())[0][:100]}...")
# `list(qs.values())[0]` is the first question text; `[:100]` truncates it for display.

def ngrams(text, n):
    # Turn a piece of text into the SET of its n-word phrases. Word-level rather than character-level,
    # so formatting differences cannot manufacture or hide an overlap.

    w = re.findall(r"[a-z0-9']+", text.lower())
    # `re.findall` returns every match as a list. The pattern `[a-z0-9']+` keeps runs of
    # lowercase letters, digits and apostrophes — i.e. words — after `.lower()` has removed case.
    # Punctuation and spacing therefore cannot create a spurious mismatch.

    return {" ".join(w[i:i+n]) for i in range(len(w) - n + 1)}
    # A set comprehension building every window of n consecutive words, joined back with spaces.
    # `range(len(w) - n + 1)` is exactly the number of such windows. A SET, because we only care
    # whether an n-gram occurs, not how often.

train_text = [u + " " + a for u, a in convs]
# Every training conversation as one string: the question the model was trained on plus its
# answer. Contamination could hide in either half, so both are searched.

for n in (8, 5, 3):
    # Three window sizes, largest first: 8 and 5 words are the real tests, 3 is the control that
    # shows what a NON-zero result looks like (generic English phrases).

    train_ngrams = set()
    # Build the union of all n-grams across the whole training set.

    for t in train_text:
        # One pass over all 6000 conversations.

        train_ngrams |= ngrams(t, n)
        # `|=` is set union in place: add everything from this conversation's n-grams.

    hits = {qid: sorted(ngrams(q, n) & train_ngrams)[:3] for qid, q in qs.items()}
    # For each eval question, the n-grams it shares with training. `&` is set intersection;
    # `sorted(…)[:3]` keeps up to three examples for display.

    n_hit = sum(1 for v in hits.values() if v)
    # An empty list is falsy, so `if v` counts the questions with at least one shared n-gram.

    print(f"  {n}-gram: {n_hit:2d} of {len(qs)} eval questions share any {n}-gram with training text")
    # One line per window size — the three together are the whole result.

    if n == 3 and n_hit:
        # At n=3, show one example. `next(…)` pulls the first item out of a generator — here, the
        # first non-empty hit list. This is the POSITIVE CONTROL: it proves the instrument can find
        # overlap when overlap exists, so the zeros at n=5 and n=8 are measurements, not silence.

        ex = next(v for v in hits.values() if v)
        # `next(generator)` pulls the first item out without building a list.

        print(f"           e.g. {ex[:2]}  <- generic English at n=3, as expected")
        # Show two of them, so "generic English" is something the reader judges, not takes on trust.

    if n in (5, 8):
        # And the actual contamination test, at the two window sizes where a match would be damning.

        assert n_hit == 0, f"an eval question shares a {n}-gram with training data -- contamination"
        # Zero required, at both sizes. One hit would mean an eval question was partly memorised.

VERDICT["no_train_eval_contamination"] = "0 of 23 BROAD questions share any 5-gram or 8-gram with the 6000 training conversations"
# Both denominators recorded (23 questions, 6000 conversations) — the claim is only as strong as
# the sets it was computed over.

print("""
Zero overlap at 5 and 8. At 3 you get things like "do you think that", which is English rather
than leakage. So the generalisation claim is about genuinely unseen questions.""")
# What the zeros license: generalisation to questions the model genuinely never saw.
