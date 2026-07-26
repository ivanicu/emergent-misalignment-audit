"""NECESSITY META-ANALYSIS — the same quantity, measured by every instrument this project owns, side by side.

G3 showed that two operators setting the IDENTICAL u-coordinate give 2.6 vs 21.5. That makes one question
unavoidable: how much of this project's spread in "u necessity" is the MECHANISM, and how much is the
INSTRUMENT? Every necessity number was produced by a different apparatus and reported on its own scale, so they
have never been placed side by side with their operator named.

Each row is one estimate of "how much EM is lost when the u-channel is removed / set to base", expressed BOTH
in raw pp and as a FRACTION of that instrument's own dynamic range (its unperturbed cell minus its floor cell) --
because the reference audit showed the "FT" cells span 12.4 to 29.8 across experiments, so raw pp are not
comparable across rows and the fraction is the only cross-instrument-comparable number.

The OPERATOR column is the point: naive clamp (w = u, off-manifold, sham costs 6.9pp) vs Mahalanobis (w = Su,
displaces 5x the natural carrier) vs subtractive ablation vs additive transplant (retracted as off-manifold).
If the fraction is stable across operators, necessity is a property of u. If it tracks the operator, it is a
property of the apparatus."""
import json
import numpy as np
from pathlib import Path
ROOT=Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")

def perq(d,c):
    fp=ROOT/f"experiments/judgments_{d}/{c}.llama31.jsonl"
    if not fp.exists(): return None
    a={}
    for l in open(fp):
        r=json.loads(l); v=str(r.get("verdict","")).strip()
        if v.isdigit(): a.setdefault(r["qid"],[]).append(int(v)>=4)
    return {q:float(np.mean(x)) for q,x in a.items()} or None

# (experiment, intact cell, u-removed cell, floor cell, operator label)
ROWS=[("necSR","natural","bad_S","bad_SR","subtractive ablation of the u-channel"),
      ("g3cond","natural","naive_base","naive_base","NAIVE clamp w=u  (off-manifold)"),
      ("g3cond","natural","manifold_base","naive_base","MAHALANOBIS clamp w=Su (5x carrier off-u)"),
      ("posgate","intact","base_all","base_all","NAIVE clamp, all positions"),
      ("g5pulse","all_ft","all_base","all_base","NAIVE clamp to base profile"),
      ("opbias","oracle","base","base","NAIVE clamp, oracle reconstruction"),
      ("gatetom","g1_FT","g0_base","g0_base","NAIVE clamp, dose ladder"),
      ("writesweep","full","none","none","whole-L16-write removal (not u-specific)"),
      ("readerabl","full","none","none","whole-write removal (not u-specific)")]
rng=np.random.default_rng(0)
print("=== THE SAME QUANTITY, EVERY INSTRUMENT, OPERATOR NAMED ===\n")
print(f"{'experiment':11s} {'intact':>7s} {'u-off':>7s} {'floor':>6s} {'drop pp':>19s} {'frac of range':>15s}  operator")
out=[]
for e,ic,uc,fc,op in ROWS:
    A,B,F=perq(e,ic),perq(e,uc),perq(e,fc)
    if A is None or B is None or F is None: print(f"{e:11s}  (cells missing: {ic}/{uc}/{fc})"); continue
    Q=sorted(set(A)&set(B)&set(F))
    if len(Q)<8: continue
    a=np.array([A[q] for q in Q]); b=np.array([B[q] for q in Q]); f=np.array([F[q] for q in Q])
    n=len(Q); idx=rng.integers(0,n,(20000,n))
    d=a-b; bs=d[idx].mean(1)
    lo,hi=100*np.percentile(bs,2.5),100*np.percentile(bs,97.5)
    rng_=100*(a.mean()-f.mean())
    frac=100*(a.mean()-b.mean())/rng_ if abs(rng_)>1e-9 else np.nan
    print(f"{e:11s} {100*a.mean():7.1f} {100*b.mean():7.1f} {100*f.mean():6.1f} "
          f"{100*d.mean():+7.1f} [{lo:+5.1f},{hi:+5.1f}] {frac:14.0f}%  {op}")
    out.append({"exp":e,"op":op,"drop":100*d.mean(),"lo":lo,"hi":hi,"frac":frac})
cl=[o for o in out if "NAIVE" in o["op"]]
mh=[o for o in out if "MAHALANOBIS" in o["op"]]
print(f"\n  NAIVE-clamp estimates:      n={len(cl)}  fraction of range: "
      f"{', '.join(f'{o[chr(102)+chr(114)+chr(97)+chr(99)]:.0f}%' for o in cl)}")
if mh: print(f"  MAHALANOBIS estimate:       {mh[0]['frac']:.0f}% of range   <- same u-coordinate as the naive rows")
print(f"""
  READ: if the fraction-of-range is similar across NAIVE rows but the MAHALANOBIS row is far below them, then
  the consistency among the naive rows is CONSISTENCY OF AN APPARATUS, not replication of a mechanism -- they
  all share the same operator, so they cannot corroborate each other about it. Agreement between instruments
  that share the confound is triangulation, not independent replication.""")
