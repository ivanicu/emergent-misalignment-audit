"""G1 COMMITTOR -- is the EM outcome predicted by u'h ALONE, or does a SUBSPACE do better?

THE QUESTION, from REVIEW_ROADMAP_2 gate G1. Everything this project has established treats u as a scalar
control variable g_t = u'h_16,t. The roadmap's own NOT-ESTABLISHED list leads with "that u is a 1-D variable
(may be the principal axis of a 2-3 dim control subspace, or the tangent of a nonlinear control-flow variable)".
A committor separates those: if q(h)=P(EM|h) is captured by u'h and adding orthogonal directions buys nothing
OUT OF SAMPLE, u is an axis. If orthogonal directions add real predictive power, it is a subspace and every
1-D statement in the project is a projection of something larger.

THE FORK STRUCTURE, and why it is honest. The 184 frame sequences are 23 questions x 8 rollouts sampled at
temperature 1.0 from the SAME prompt. Within a question the rollouts share the prompt state exactly and diverge
only through sampling. So the WITHIN-QUESTION contrast holds the question fixed, which is the one control this
project has repeatedly needed: two retractions here came from between-question base-rate differences masquerading
as effects. All features and labels are CENTERED WITHIN QUESTION before fitting, so a between-question base rate
cannot contribute to any number below.

POWER, stated up front because it CUTS THE OTHER WAY for once. Every behavioural contrast in this project has
eff-N ~23 question clusters, so only >~8pp resolves. This committor uses ROLLOUT-level variance that those
contrasts discard: after within-question centering the residual df is 184-23 = 161. It is the highest-powered
instrument in the project -- which is exactly why its NULL, if it returns one, would be worth something.

WHAT IT CANNOT DO. These are forks at generation position 0, not mid-generation forks from a shared trajectory.
So this measures how much of the outcome is predictable from the state as the first token is produced (plus
whatever the sampled continuation reveals), NOT the committor along a single trajectory. A true mid-generation
committor needs the GPU. Recorded so this is never described as more than it is.

POSITIVE CONTROL BEFORE ANY NULL (standing discipline -- a null from an un-positive-controlled instrument is
SILENCE, not evidence). Two calibrators run every time:
  FLOOR   : labels shuffled within question. Recovers the AUC an uninformative feature set earns by chance.
  CEILING : a SYNTHETIC label built from a known feature at a known strength. If the pipeline cannot recover a
            signal it was handed, its null on the real label means nothing and the run says so.

Usage: g1_committor.py [--window 6] [--folds 23]"""
import argparse, json, re, sys
from pathlib import Path
import numpy as np

ROOT = Path("~/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable")
FRAMES = Path("~/data.persona-forensics-frames")
JUDG = ROOT / "experiments/judgments_frames/natural_ft.llama31.jsonl"
FEAT = ROOT / "experiments/g1_features.npz"

# candidate directions: u itself, then the orthogonal-ish ones the roadmap names, then two random-plane controls
# names carry the .pt suffix -- that is the key in fits/PROVENANCE.json, and load_direction hash-checks against it
DIRS = ["u_L16.pt", "e19_L16.pt", "e08_L16.pt", "readout_g_L16.pt", "reg_axis_L16.pt",
        "neg_delta_perp_L16.pt", "v2_op12_L16.pt", "v3_op20_L16.pt", "good_u_L16.pt"]


def build_features(window):
    sys.path.insert(0, str(ROOT / "scripts"))
    import torch
    from provenance_guard import load_direction
    D = {}
    for n in DIRS:
        try:
            v = load_direction(n).float().numpy()
            D[n] = v / np.linalg.norm(v)
        except Exception as e:
            print(f"  skip {n}: {e}")
    names = list(D)
    # A silently-empty direction set would have produced a "no orthogonal gain" NULL from an instrument that
    # loaded NOTHING. Fail loudly instead -- this is exactly the un-positive-controlled null the discipline bans.
    if "u_L16.pt" not in D:
        raise SystemExit("FATAL: u itself failed to load -- every number below would be meaningless")
    if len(D) < 4:
        raise SystemExit(f"FATAL: only {len(D)} directions loaded; the subspace arm has nothing to test with")
    B = np.stack([D[n] for n in names])                      # [k, 3584]
    u = D["u_L16.pt"]

    rows, qids, rolls = [], [], []
    fps = sorted(FRAMES.glob("*.npz"))
    for i, fp in enumerate(fps):
        m = re.match(r"(.+)__r(\d+)$", fp.stem)
        if not m:
            continue
        d = np.load(fp)
        try:
            hf = d["step0375|resid|L16"].astype(np.float32)   # the FT's own state
            hb = d["base|resid|L16"].astype(np.float32)       # base, IDENTICAL tokens -> delta is exact
        except KeyError:
            d.close(); continue
        d.close()
        n = min(len(hf), len(hb))
        if n < 2:
            continue
        w = min(window, n)
        e_f, l_f = hf[:w], hf[w:] if n > w else hf[:w]
        dl = (hf - hb)[:w]                                    # early displacement, exact by construction

        proj_e = B @ e_f.mean(0)                              # each direction's early projection of FT state
        proj_l = B @ l_f.mean(0)
        gd = float(u @ dl.mean(0))                            # u-component of the early FT-vs-base displacement
        dm = dl.mean(0)
        dperp = float(np.linalg.norm(dm - gd * u))            # off-u magnitude of that displacement
        hm = e_f.mean(0)
        hperp = float(np.linalg.norm(hm - (u @ hm) * u))

        rows.append(np.concatenate([proj_e, proj_l, [gd, dperp, hperp, float(np.linalg.norm(hm)), float(n)]]))
        qids.append(m.group(1)); rolls.append(int(m.group(2)))
        if (i + 1) % 40 == 0:
            print(f"  ... {i+1}/{len(fps)}", flush=True)

    cols = ([f"proj_early:{n}" for n in names] + [f"proj_late:{n}" for n in names]
            + ["delta_u_early", "delta_perp_early", "h_perp_early", "h_norm_early", "n_tok"])
    X = np.asarray(rows, np.float64)
    np.savez(FEAT, X=X, cols=np.array(cols), qid=np.array(qids), rollout=np.array(rolls))
    print(f"  features {X.shape} -> {FEAT}")
    return X, cols, np.array(qids)


def load_labels(qids, rolls):
    y = {}
    if not JUDG.exists():
        return None
    # The judge emits {1..5, REFUSAL, INCOHERENT, OFF-TOPIC, SATIRICAL/ABSURD, PARSE_FAIL}, not just integers.
    # Convention copied EXACTLY from aggregate_patch.py:17-18 rather than invented here: EVIL = {4,5}, and the
    # incoherent classes are EXCLUDED (NaN), never coerced to 0. Scoring them 0 would silently enlarge the
    # denominator with responses that were never scoreable and bias every rate downward.
    EVIL = {"4", "5"}
    INCOH = {"INCOHERENT", "REFUSAL", "OFF-TOPIC", "PARSE_FAIL"}
    for ln in open(JUDG):
        o = json.loads(ln)
        v = str(o.get("verdict", o.get("score", ""))).strip().upper()
        if not v or v in INCOH:
            continue
        y[(o["qid"], int(o.get("rollout", 0)))] = 1.0 if v in EVIL else 0.0
    return np.array([y.get((q, r), np.nan) for q, r in zip(qids, rolls)])


def within_center(A, g):
    """subtract each question's mean -> a between-question base rate cannot contribute to anything downstream"""
    A = A.astype(np.float64).copy()
    for q in np.unique(g):
        m = g == q
        A[m] -= A[m].mean(0)
    return A


def cv_r2(X, y, g, seed=0, ridge=1.0):
    """leave-one-question-out predictive R2 on within-question-centered data (grouped, so no question leaks)"""
    if X.ndim == 1:
        X = X[:, None]
    qs = np.unique(g); num = den = 0.0
    for q in qs:
        te = g == q; tr = ~te
        Xt, yt = X[tr], y[tr]
        s = Xt.std(0); s[s < 1e-9] = 1.0
        Xt = Xt / s; Xe = X[te] / s
        W = np.linalg.solve(Xt.T @ Xt + ridge * np.eye(Xt.shape[1]), Xt.T @ yt)
        p = Xe @ W
        num += ((y[te] - p) ** 2).sum(); den += (y[te] ** 2).sum()
    return float(1 - num / max(den, 1e-12))


def boot(X, y, g, other=None, B=2000, seed=0):
    """qid-cluster bootstrap on the R2 GAIN of X over `other` (or over nothing)"""
    rng = np.random.default_rng(seed); qs = np.unique(g); out = []
    for _ in range(B):
        pick = rng.choice(qs, len(qs), replace=True)
        idx = np.concatenate([np.where(g == q)[0] for q in pick])
        gg = np.concatenate([[f"{q}#{i}"] * (g == q).sum() for i, q in enumerate(pick)])
        try:
            a = cv_r2(X[idx], y[idx], gg)
            b = cv_r2(other[idx], y[idx], gg) if other is not None else 0.0
            out.append(a - b)
        except Exception:
            pass
    o = np.array(out)
    return float(o.mean()), float(np.percentile(o, 2.5)), float(np.percentile(o, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=6)
    ap.add_argument("--rebuild", type=int, default=0)
    a = ap.parse_args()

    if FEAT.exists() and not a.rebuild:
        z = np.load(FEAT, allow_pickle=True)
        X, cols, qids, rolls = z["X"], list(z["cols"]), z["qid"], z["rollout"]
        print(f"=== G1 COMMITTOR === (features cached {X.shape})")
    else:
        print(f"=== G1 COMMITTOR === building features, early window = first {a.window} generated tokens")
        X, cols, qids = build_features(a.window)
        z = np.load(FEAT, allow_pickle=True); rolls = z["rollout"]

    y = load_labels(qids, rolls)
    if y is None:
        print(f"\n  LABELS NOT READY: {JUDG} does not exist yet (frames judge is queued).")
        print(f"  Features are built and cached; re-run this script the moment the judge finishes.")
        return
    ok = ~np.isnan(y)
    X, y, g = X[ok], y[ok], qids[ok]
    nq = len(np.unique(g))
    print(f"  labelled {len(y)} sequences / {nq} questions | EM rate {y.mean():.3f} "
          f"| within-question df {len(y)-nq}")

    Xc = within_center(X, g); yc = within_center(y[:, None], g).ravel()
    if yc.std() < 1e-9:
        print("  DEGENERATE: no within-question outcome variance -- every rollout of every question agrees.")
        print("  The committor is not estimable on this data; that is itself the finding.")
        return

    iu = cols.index("proj_early:u_L16.pt")
    U = Xc[:, [iu]]
    orth = [i for i, c in enumerate(cols)
            if c.startswith("proj_early:") and "u_L16.pt" not in c] + [cols.index("delta_perp_early"),
                                                                    cols.index("h_perp_early")]
    O = Xc[:, orth]
    UO = np.hstack([U, O])

    print("\n  --- POSITIVE CONTROL (must pass before any null below is admissible) ---")
    ysyn = within_center((Xc[:, iu] + 0.5 * Xc[:, iu].std() * np.random.default_rng(0)
                          .standard_normal(len(yc)))[:, None], g).ravel()
    r_syn = cv_r2(U, ysyn, g)
    print(f"   synthetic label built from u at known strength -> R2 {r_syn:+.3f} "
          f"{'PASS' if r_syn > 0.2 else 'FAIL -- pipeline cannot recover a signal it was handed'}")
    rng = np.random.default_rng(1)
    sh = [cv_r2(UO, within_center(rng.permutation(y)[:, None], g).ravel(), g) for _ in range(40)]
    print(f"   label-shuffled floor (40 draws) -> R2 {np.mean(sh):+.3f} [{np.percentile(sh,5):+.3f},"
          f"{np.percentile(sh,95):+.3f}]")

    print("\n  --- THE TEST: axis vs subspace (leave-one-question-out, within-question centered) ---")
    r_u, r_o, r_uo = cv_r2(U, yc, g), cv_r2(O, yc, g), cv_r2(UO, yc, g)
    print(f"   u alone            R2 {r_u:+.4f}")
    print(f"   orthogonal alone   R2 {r_o:+.4f}")
    print(f"   u + orthogonal     R2 {r_uo:+.4f}")
    m, lo, hi = boot(UO, yc, g, other=U)
    verdict = ("SUBSPACE: orthogonal directions add real out-of-sample predictive power beyond u"
               if lo > 0 else
               "consistent with AXIS: no resolvable gain from the orthogonal directions "
               f"(equivalence margin {hi:+.4f})")
    print(f"   GAIN of adding orthogonal over u alone: {m:+.4f} [{lo:+.4f},{hi:+.4f}]")
    print(f"   => {verdict}")

    mu, lu, hu = boot(U, yc, g)
    print(f"\n   u's own predictive R2: {mu:+.4f} [{lu:+.4f},{hu:+.4f}] "
          f"{'RESOLVED' if lu > 0 else 'NOT RESOLVED -- u does not predict the fork outcome at all'}")


if __name__ == "__main__":
    main()
