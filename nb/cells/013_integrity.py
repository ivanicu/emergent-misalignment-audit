# ⟨needs⟩ 011 (DATA, MAN, hashlib)

bad = [rel for rel, m in MAN["files"].items()
       if hashlib.sha256((DATA / rel).read_bytes()).hexdigest() != m["sha256"]]
# A list comprehension with a filter, read inside-out:
#   `MAN["files"]` is {relative path: {"sha256": …, "bytes": …, "what": …}}
#   `.items()` yields (rel, m) pairs — the path and its recorded facts
#   `(DATA / rel).read_bytes()` reads that file as raw bytes (not text: bytes, so any file works)
#   `hashlib.sha256(…).hexdigest()` is the standard 64-hex-character fingerprint of those bytes:
#       change one bit anywhere and the fingerprint changes completely
#   `!= m["sha256"]` keeps only the files whose fingerprint no longer matches what was recorded
# So `bad` is the list of files that have changed since staging. Normally it is empty.

assert not bad, f"staged files altered since staging: {bad}"
# `not bad` is True when the list is empty. So: stop everything if any file was altered.
# This runs BEFORE any number is computed, on purpose — see the closing note in this cell.

print(f"{len(MAN['files'])} artifacts + {sum(MAN['judgment_dirs'].values())} judgment files")
# `len(MAN['files'])` = how many individual artifacts were staged.
# `MAN['judgment_dirs']` maps each judgment folder to its file count; `sum(…values())` totals them.

print("all sha256 match the staging manifest\n")
# Reached only if the assertion above passed, so this sentence is a consequence, not a promise.

for rel, m in list(MAN["files"].items())[:6]:
    # `list(…)[:6]` takes the first six entries — a sample, so the output stays readable.

    print(f"  {m['bytes']:>9,}  {rel:52} {m['what']}")
    # Format specifiers: `:>9,` = right-aligned in 9 columns with thousands separators;
    # `:52` = left-padded to 52 columns so the three fields line up as a table.

print(f"  ... and {len(MAN['files'])-6} more, plus {len(MAN['scripts'])} scripts quoted verbatim")
# Say how many rows were NOT shown, plus the count of research scripts staged verbatim
# (those matter later: several sections read the real script rather than a paraphrase of it).

print(f"\ntwo vectors derived from {MAN['derived']['source']} "
      f"({MAN['derived']['source_bytes']/1e6:.0f} MB, sha {MAN['derived']['source_sha256'][:12]})")
# Two vectors were NOT copied: they were derived from a 295 MB file that was not worth staging.
# So the manifest records the SOURCE file's own hash plus the exact recipe — enough for anyone to
# reproduce those two vectors bit-for-bit from the original. Adjacent f-strings concatenate.
# `/1e6` converts bytes to megabytes; `:.0f` prints it with no decimals; `[:12]` shortens the hash.

print(f"  recipe: {MAN['derived']['recipe']}")
# The recipe itself, in the manifest's own words.

print("""
Why this comes before everything. From here on, every number in this notebook is computed from
these files -- so if a byte differed from what was copied out of the research repo, you would be
auditing something else and could not tell. The hash check turns "I did not retype any number by
hand" from a promise into a property you just verified. It also means you can hand this kit to
someone else and they check the same bytes, not a similar-looking copy.""")
# Triple-quoted string: a multi-line block printed exactly as written, newlines included.
