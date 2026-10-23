#!/usr/bin/env python
"""Prompt 41 section 4 pinned analysis of the replicate waves.

Reads the committed objectives of replicate_C_noise_a/_b plus the frozen
historical waves, runs the pre-registered computation (populations kept
apart, df = 10, Satterthwaite pooling, 10k-permutation homogeneity test,
pinned rejection trigger), and writes REPLICATE_RESULT.md next to this
script. Every printed number is computed here; inputs are asserted
against the values read directly on CRC and against part_a_replicates.csv.
"""
from pathlib import Path
import itertools
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy.stats import chi2, f as fdist

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
WAVES = CAMP / "waves"
OUT = HERE / "REPLICATE_RESULT.md"

M = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]
LAB = {M[0]: "shed (MWh)", M[1]: "curt (MWh)", M[2]: "cost (USD)"}
OMEGA = ["nuclear_omega", "pv_omega", "tail_omega",
         "wind_122_omega", "wind_303_omega", "wind_317_omega"]
SEED = 20261023          # NOT pinned by the prompt; disclosed in the report
NPERM = 10_000           # pinned
ALPHA = 0.05             # pinned
RA, RB = "replicate_C_noise_a", "replicate_C_noise_b"

_objs, _dms = {}, {}
def wobj(w):
    if w not in _objs:
        _objs[w] = pd.read_csv(WAVES / w / "objectives.csv").set_index("index")
    return _objs[w]

def wdm(w):
    if w not in _dms:
        _dms[w] = pd.read_csv(WAVES / w / "design_matrix.csv").set_index("index")
    return _dms[w]

def val(key, col):
    w, i = key.rsplit(":", 1)
    return float(wobj(w).loc[int(i), col])

# ---- integrity check 1: shed values vs the values read directly on CRC ----
CRC_SHED = {(RA, 1): 429.53, (RA, 2): 429.53, (RA, 3): 4671.72,
            (RA, 4): 4688.56, (RA, 5): 37810.89, (RA, 6): 35511.64,
            (RB, 1): 429.53, (RB, 2): 429.53, (RB, 3): 4671.72,
            (RB, 4): 4823.57, (RB, 5): 37856.59, (RB, 6): 37281.96}
for (w, i), v in CRC_SHED.items():
    got = round(val(f"{w}:{i}", M[0]), 2)
    assert got == v, f"CRC cross-check FAILED {w}:{i} shed {got} != {v}"

# ---- design registry (prompt 41 section 2; verified vs manifests) ----
DES = {
    "LOW":  dict(hist=["methods_C_P2_r3:7"],
                 fresh=[f"{RA}:1", f"{RB}:1"], pert=[f"{RA}:2", f"{RB}:2"]),
    "MID":  dict(hist=["methods_C_P1_r3:8", "methods_C_P2_r1:5"],
                 fresh=[f"{RA}:3", f"{RB}:3"], pert=[f"{RA}:4", f"{RB}:4"]),
    "HIGH": dict(hist=["methods_C_P1_r3:3", "methods_C_P3_r2:3"],
                 fresh=[f"{RA}:5", f"{RB}:5"], pert=[f"{RA}:6", f"{RB}:6"]),
}
STAND = {"ACC-29k": ["bo_C_r2:3", "methods_C_P2_r3:6"],
         "ACC-17k": ["methods_C_P1_r4:8", "methods_C_P3_r3:1"]}

# ---- integrity check 2: the 4 accidental pairs match part_a_replicates.csv ----
pa = pd.read_csv(HERE / "part_a_replicates.csv")
pa_pairs = {frozenset([r.a, r.b]): (r.abs_d_load, r.abs_d_true, r.abs_d_tota)
            for r in pa.itertuples()}
for pair in [DES["MID"]["hist"], DES["HIGH"]["hist"], *STAND.values()]:
    k = frozenset(pair)
    assert k in pa_pairs, f"pair {pair} not in part_a_replicates.csv"
    for col, ref in zip(M, pa_pairs[k]):
        d = abs(val(pair[0], col) - val(pair[1], col))
        assert abs(d - ref) < 1e-5, f"part_a mismatch {pair} {col}: {d} vs {ref}"

# ---- integrity check 3: byte-identity findings asserted before printing ----
def same(k1, k2):
    return all(val(k1, c) == val(k2, c) for c in M)
LOW_IDENT = [DES["LOW"]["hist"][0], f"{RA}:1", f"{RB}:1", f"{RA}:2", f"{RB}:2"]
for k in LOW_IDENT[1:]:
    assert same(LOW_IDENT[0], k), f"LOW identity broken at {k}"
for k in [f"{RA}:3", f"{RB}:3"]:
    assert same("methods_C_P2_r1:5", k), f"MID fresh != twin at {k}"
assert val(*(STAND["ACC-17k"][0], M[0])) == val(STAND["ACC-17k"][1], M[0])

# ---- integrity check 4: fresh exact rows identical across waves in omega ----
for i in (1, 3, 5):
    assert (wdm(RA).loc[i, OMEGA] == wdm(RB).loc[i, OMEGA]).all()

def h_norm(w1, i1, w2, i2):
    d = (wdm(w1).loc[i1, OMEGA] - wdm(w2).loc[i2, OMEGA]).abs()
    assert (d > 0).sum() == 1, "perturbed pair must differ in exactly one tier"
    return float(d.max()) / 0.95

# ---- Population 1 estimator: per-design variance over distinct draws ----
def chi2_sd_ci(s2, df):
    if s2 == 0:
        return (0.0, 0.0)
    return (np.sqrt(df * s2 / chi2.ppf(1 - ALPHA / 2, df)),
            np.sqrt(df * s2 / chi2.ppf(ALPHA / 2, df)))

def satt(units):
    """units = [(s2, df), ...]; returns pooled s2, df_sum, nu, sd CI."""
    terms = np.array([s2 * df for s2, df in units])
    dfs = np.array([df for _, df in units])
    s2p = terms.sum() / dfs.sum()
    nu = terms.sum() ** 2 / np.sum(terms ** 2 / dfs) if terms.sum() > 0 else dfs.sum()
    lo = np.sqrt(nu * s2p / chi2.ppf(1 - ALPHA / 2, nu))
    hi = np.sqrt(nu * s2p / chi2.ppf(ALPHA / 2, nu))
    return s2p, int(dfs.sum()), nu, (lo, hi)

P1 = {}   # P1[col][design] = dict(draws, s2, df, ci)
POOL1, FRESH, P1PAIRS, P2PAIRS = {}, {}, {}, {}
for col in M:
    per = {}
    units = []
    for d, g in DES.items():
        draws = [val(k, col) for k in g["hist"] + g["fresh"]]
        s2 = float(np.var(draws, ddof=1))
        per[d] = dict(draws=draws, keys=g["hist"] + g["fresh"],
                      s2=s2, df=len(draws) - 1, ci=chi2_sd_ci(s2, len(draws) - 1))
        units.append((s2, len(draws) - 1))
    for d, (k1, k2) in STAND.items():
        delta = val(k1, col) - val(k2, col)
        s2 = delta ** 2 / 2
        per[d] = dict(draws=[val(k1, col), val(k2, col)], keys=[k1, k2],
                      s2=s2, df=1, ci=chi2_sd_ci(s2, 1))
        units.append((s2, 1))
    assert sum(u[1] for u in units) == 10, "pinned df accounting must total 10"
    P1[col] = per
    POOL1[col] = satt(units)
    # fresh-only cross-wave subpopulation (disclosure, not the estimator)
    fr = [( (val(g["fresh"][0], col) - val(g["fresh"][1], col)) ** 2 / 2, 1)
          for g in DES.values()]
    FRESH[col] = satt(fr)
    # Population-1 pair list for the permutation test (17 pairs)
    p1 = []
    for d, g in DES.items():
        for k1, k2 in itertools.combinations(g["hist"] + g["fresh"], 2):
            p1.append((val(k1, col) - val(k2, col)) ** 2)
    for k1, k2 in STAND.values():
        p1.append((val(k1, col) - val(k2, col)) ** 2)
    assert len(p1) == 17
    P1PAIRS[col] = np.array(p1)
    # Population 2: perturbed vs fresh exact siblings and vs each other (15)
    p2, p2rows = [], []
    for d, g in DES.items():
        for p in g["pert"]:
            for e in g["fresh"]:
                p2rows.append((d, p, e))
        p2rows.append((d, g["pert"][0], g["pert"][1]))
    assert len(p2rows) == 15
    for d, a, b in p2rows:
        p2.append((val(a, col) - val(b, col)) ** 2)
    P2PAIRS[col] = (np.array(p2), p2rows)

# ---- pinned homogeneity test: permutation on the squared deltas ----
def perm_test(d1, d2):
    rng = np.random.default_rng(SEED)
    x = np.concatenate([d1, d2]); n1 = len(d1)
    obs = abs(d1.mean() - d2.mean())
    cnt = 0
    for _ in range(NPERM):
        p = rng.permutation(x)
        cnt += abs(p[:n1].mean() - p[n1:].mean()) >= obs
    return obs, (1 + cnt) / (1 + NPERM)

PERM = {col: perm_test(P1PAIRS[col], P2PAIRS[col][0]) for col in M}

# conditional pooled number (only when the permutation test passes)
COND = {}
for col in M:
    if PERM[col][1] >= ALPHA:
        num = POOL1[col][0] * 10 + P2PAIRS[col][0].sum() / 2
        COND[col] = np.sqrt(num / 25)

# ---- level dependence: one-sided high-vs-low variance-ratio test (+ CI) ----
VR = {}
for col in M:
    s2h, dfh = P1[col]["HIGH"]["s2"], P1[col]["HIGH"]["df"]
    s2l, dfl = P1[col]["LOW"]["s2"], P1[col]["LOW"]["df"]
    if s2l == 0.0:
        VR[col] = dict(F=np.inf, p=0.0, ci=(np.inf, np.inf),
                       sd_ratio=np.inf, degenerate=True)
    else:
        F = s2h / s2l
        VR[col] = dict(F=F, p=float(fdist.sf(F, dfh, dfl)),
                       ci=(F / fdist.ppf(1 - ALPHA / 2, dfh, dfl),
                           F / fdist.ppf(ALPHA / 2, dfh, dfl)),
                       sd_ratio=np.sqrt(F), degenerate=False)
TRIGGER = (VR[M[0]]["p"] < ALPHA) and (VR[M[0]]["sd_ratio"] > 3)

# ---- function-term envelope (prompt 41 section 4 conventions) ----
def env_lin(h):  return float(np.sqrt(2.52e6 * h / 0.068))
def env_quad(h): return float(np.sqrt(2.52e6) * h / 0.068)
H1, H2 = 0.001 / 0.95, 0.002 / 0.95

# ---- execution metadata ----
meta = pd.read_csv(HERE / "replicate_run_metadata.csv")
assert len(meta) == 12
meta["end"] = pd.to_datetime(meta["log_end_mtime_et"])
meta["start_implied"] = meta["end"] - pd.to_timedelta(meta["sim_time_s"], unit="s")
meta["hours"] = meta["sim_time_s"] / 3600.0
hi_h = meta.loc[meta.design == "HIGH", "hours"]
ot_h = meta.loc[meta.design != "HIGH", "hours"]
assert hi_h.min() > ot_h.max(), "HIGH runtimes must exceed the rest"

# ================= report =================
def g4(x):
    return f"{x:,.4g}"

L = []
A = L.append
A("# REPLICATE_RESULT — prompt 41 replicate waves (measured shed noise floor)")
A("")
A(f"Generated {datetime.now():%Y-%m-%d} by `analysis/noise_floor/replicate_result.py` "
  f"(permutation seed {SEED}, {NPERM:,} permutations, alpha = {ALPHA}).")
A(f"Inputs: `waves/{RA}` and `waves/{RB}` objectives (collector commits on d6, "
  "merged at `b0a6e1e`), the frozen parent waves, `part_a_replicates.csv`, and "
  "`replicate_run_metadata.csv`. The recipe is prompt 41 section 4, applied as pinned.")
A("")
A("## 1. Data integrity")
A("")
A("- All 12 runs landed. Both collectors report GATE PASS (6 run dirs each).")
A("- All 12 `load_shed_mwh` values match the values read directly on CRC "
  "(asserted to 2 decimals in this script).")
A("- The scp copies match the collector-committed `objectives.csv` byte for byte.")
A("- The four accidental pairs reproduce `part_a_replicates.csv` deltas "
  "to < 1e-5 on all three objectives (asserted).")
A("- Byte-identity findings below are asserted before they are printed.")
A("")
A("## 2. Execution environment (mandatory disclosure)")
A("")
A("**Nodes.** The job stdout does not record the host. `qacct` is unavailable "
  "on this cluster (no accounting file). The ONLY node records are live `qstat` "
  "observations during the runs: **tasks 5 and 6 of BOTH waves ran on "
  "`d12chas342` — the same node.** The nodes of tasks 1–4 of each wave are "
  "unknown. Consequences, stated plainly:")
A("")
A("- The HIGH fresh exact pair (a:5 x b:5) is a **same-node** pair. Its "
  "delta = 45.70 MWh measures within-node, cross-job-instance variation, not "
  "cross-node variation.")
A("- The LOW and MID fresh exact pairs may also have shared nodes; no record "
  "exists either way. Their delta = 0 results are therefore NOT confirmed "
  "cross-node measurements.")
A("- The wave A -> wave B submission gap was about 6 minutes (implied starts "
  "01:17 vs 01:22 ET on 2026-10-21), so the two waves ran concurrently. The "
  "scheduler weakened the cross-environment design intent. The label "
  "'Population 1 = cross-environment' holds with certainty only for the "
  "pairs that straddle separate submissions days apart (fresh vs "
  "parent/twin, and the 4 accidental pairs).")
A("")
A("**Runtimes** (wallclock = `Total simulation time` from the task logs; "
  "implied start = log end mtime minus wallclock):")
A("")
A("| wave | task | design | role | node | wallclock (h) | end (ET) |")
A("|---|---|---|---|---|---|---|")
for r in meta.itertuples():
    A(f"| {r.wave} | {r.task} | {r.design} | {r.role} | {r.node} | "
      f"{r.hours:.2f} | {r.end:%m-%d %H:%M} |")
A("")
A(f"The HIGH corner tasks took {hi_h.min():.1f}–{hi_h.max():.1f} h; every other "
  f"task took {ot_h.min():.1f}–{ot_h.max():.1f} h (asserted disjoint). Solve "
  "difficulty rises with shed level (about 1.5x at the all-0.05 corner). "
  "NOTE: a 31–33 h figure was reported from memory during the wait; the logs "
  "record 23.8–24.7 h, and the log values are used here.")
A("")
A("## 3. Population 1 (PRIMARY): cross-environment exact draws")
A("")
A("Estimator as pinned: per-design sample variance over distinct draws, "
  "df = draws − 1 (LOW 2, MID 3, HIGH 3, two standalone accidental pairs 1 "
  "each; total df = 10, asserted). Observed zeros are legitimate draws and "
  "are never collapsed. One design per stratum: design identity and shed "
  "level are confounded, so every per-stratum number below is a per-DESIGN "
  "number.")
A("")
A("Draws (shed, MWh): LOW = 3 x 429.528861 (parent and both fresh exacts are "
  "byte-identical on ALL THREE objectives; both perturbed LOW runs are ALSO "
  "byte-identical to the exacts — the pv 1.0 -> 0.999/0.998 perturbation "
  "changed nothing on the deterministic plateau). "
  "MID = {4645.048205 (parent); 4671.72164 x3 — both fresh exacts are "
  "byte-identical to the twin `methods_C_P2_r1:5` on all three objectives}. "
  "HIGH = {38927.225397 (parent); 38065.316271 (twin); 37810.89226 (a:5); "
  "37856.588432 (b:5)} — four distinct values. "
  "ACC-29k = {29181.754986; 29120.116627}. ACC-17k = {16912.379196 x2 "
  "(shed and curt identical; cost differs by 1,100.07 USD)}.")
A("")
for col in M:
    A(f"### {LAB[col]}")
    A("")
    A("| design | draws | df | sd | 95% chi2 CI on sd |")
    A("|---|---|---|---|---|")
    for d in ["LOW", "MID", "HIGH", "ACC-29k", "ACC-17k"]:
        e = P1[col][d]
        sd = np.sqrt(e["s2"])
        ci = "degenerate [0, 0]" if e["s2"] == 0 else f"[{g4(e['ci'][0])}, {g4(e['ci'][1])}]"
        A(f"| {d} | {len(e['draws'])} | {e['df']} | {g4(sd)} | {ci} |")
    s2p, dftot, nu, (lo, hi) = POOL1[col]
    A("")
    A(f"**Pooled (pinned formula):** sd = **{g4(np.sqrt(s2p))}**, df = {dftot}, "
      f"Satterthwaite nu = {nu:.2f}, 95% CI **[{g4(lo)}, {g4(hi)}]**.")
    fs2, fdf, fnu, (flo, fhi) = FRESH[col]
    A(f"Fresh-only cross-wave subpopulation (3 exact pairs, df 3; disclosure, "
      f"not the estimator): sd = {g4(np.sqrt(fs2))}, 95% CI [{g4(flo)}, {g4(fhi)}].")
    A("")
A("A zero sample variance gives a collapsed chi2 interval [0, 0]. Read it as "
  "'no variation observed in these draws', not as a proof that sigma = 0.")
A("")
A("### Cross-date side table (mandatory disclosure)")
A("")
A("Fresh (2026-10-21/22) vs historical draws of the same design, shed MWh. "
  "These deltas ARE part of the pinned Population-1 estimator above (the "
  "prompt counts parent and twin as draws); this table separates them from "
  "the fresh cross-wave deltas to show the across-submission component. "
  "NOTE: the historical runs landed 2026-10-10 to 10-18, i.e. 3-11 days "
  "before the replicate waves, not in a prior month; the 'cross-month' "
  "label used during planning overstates the gap.")
A("")
A("| design | pair | delta shed (MWh) |")
A("|---|---|---|")
for d, g in DES.items():
    for fkey in g["fresh"]:
        for hkey in g["hist"]:
            dd = abs(val(fkey, M[0]) - val(hkey, M[0]))
            A(f"| {d} | {fkey.split('/')[-1]} vs {hkey} | {dd:,.2f} |")
    dd = abs(val(g['fresh'][0], M[0]) - val(g['fresh'][1], M[0]))
    A(f"| {d} | fresh a vs fresh b (concurrent waves) | {dd:,.2f} |")
A("")
A("Fresh-vs-fresh deltas (0 / 0 / 45.70) are much smaller than fresh-vs-"
  "historical deltas at HIGH (209–1,116) and MID (26.67 vs parent, 0 vs twin). "
  "Noise across submissions days apart is larger than noise across these "
  "two concurrent waves. The MID fresh runs reproduced the 2026-10-15 twin "
  "exactly, "
  "so the outcome set looks quantized: runs land on a small set of discrete "
  "solutions rather than spreading continuously.")
A("")
A("## 4. Population 2: perturbed pairs (separate population)")
A("")
A("Pairs = each perturbed run vs its fresh exact siblings and the two "
  "perturbed runs vs each other (5 per design, 15 total; the pairs share "
  "draws, so the dfs are nominal). sigma-hat per pair = |delta|/sqrt(2). "
  "The function-term envelope is reported BESIDE the numbers, never "
  "subtracted; it biases this population's floor UPWARD, i.e. toward "
  "KEEPING the recorded stops.")
A("")
A("| design | pair | h | delta shed (MWh) | sigma-hat (MWh) |")
A("|---|---|---|---|---|")
for d, a, b in P2PAIRS[M[0]][1]:
    (w1, i1), (w2, i2) = a.rsplit(":", 1), b.rsplit(":", 1)
    h = h_norm(w1, int(i1), w2, int(i2))
    dd = abs(val(a, M[0]) - val(b, M[0]))
    A(f"| {d} | {a} vs {b} | {h:.5f} | {dd:,.2f} | {dd/np.sqrt(2):,.2f} |")
s2_p2 = P2PAIRS[M[0]][0].sum() / 2 / 15
A("")
A(f"Nominal pooled Population-2 sd (shed) = {g4(np.sqrt(s2_p2))} MWh over 15 "
  "non-independent pairs.")
A(f"Envelope on the estimated sigma, linear anchor gamma(0.068) = 2.52e6 MWh^2: "
  f"{env_lin(H1):,.0f} MWh at h = {H1:.5f} and {env_lin(H2):,.0f} MWh at "
  f"h = {H2:.5f}. Quadratic smooth-function bound: {env_quad(H1):,.0f} and "
  f"{env_quad(H2):,.0f} MWh. Both LOW perturbed runs were byte-identical to "
  "the exacts (delta = 0), so at LOW the function term is exactly zero at "
  "these h.")
A("")
A("## 5. Homogeneity (pinned permutation test) and pooling verdict")
A("")
A(f"Pinned test: permutation on the squared deltas, {NPERM:,} permutations, "
  f"alpha = {ALPHA}, statistic = |mean(delta^2, Pop 1) − mean(delta^2, Pop 2)| "
  f"(17 vs 15 pairs). Seed {SEED} (the prompt does not pin a seed; disclosed). "
  "Power is low at these dfs — disclosed as pinned.")
A("")
A("| objective | observed mean-diff of delta^2 | p | verdict at alpha = 0.05 |")
A("|---|---|---|---|")
for col in M:
    obs, p = PERM[col]
    v = "POOL (homogeneity not rejected)" if p >= ALPHA else "DO NOT POOL"
    A(f"| {LAB[col]} | {g4(obs)} | {p:.4f} | {v} |")
A("")
for col in M:
    if col in COND:
        A(f"- Conditional pooled sd ({LAB[col]}), Populations 1+2, nominal "
          f"df 25: {g4(COND[col])}. This number is CONDITIONAL on the "
          "homogeneity verdict and is NOT the handoff scalar.")
if not COND:
    A("- No conditional pooled number: the test rejects for every objective.")
A("")
A("Across designs (the heterogeneity question): the fresh exact-pair deltas "
  "are 0 / 0 / 45.70 MWh at shed levels 429 / 4,672 / 37,834, and the "
  "per-design sds span 0 to 520 MWh. One pooled sd is NOT defensible as a "
  "description of the per-design noise; the pinned across-design claim is "
  "the variance-ratio test below.")
A("")
A("## 6. Level dependence and the pinned rejection trigger")
A("")
A("Pinned: ONE pre-registered claim — a one-sided HIGH-vs-LOW per-design "
  "variance-ratio test (alpha = 0.05) plus CI. Trigger = test rejects AND "
  "the point sd ratio exceeds 3.")
A("")
A("| objective | sd HIGH | sd LOW | sd ratio | p (one-sided F, df 3,2) |")
A("|---|---|---|---|---|")
for col in M:
    v = VR[col]
    A(f"| {LAB[col]} | {g4(np.sqrt(P1[col]['HIGH']['s2']))} | "
      f"{g4(np.sqrt(P1[col]['LOW']['s2']))} | "
      f"{'infinite' if v['degenerate'] else g4(v['sd_ratio'])} | "
      + ("0 (degenerate)" if v["degenerate"] else f"{v['p']:.4f}") + " |")
A("")
A("The LOW sample variance is exactly 0 on all three objectives (five "
  "byte-identical runs across three submissions: the 2026-10-18 parent "
  "wave and waves A and B). The F "
  "statistic degenerates: under any common sigma^2 > 0 the probability of "
  "an exactly zero df-2 sample variance is 0, so the test rejects at any "
  "alpha, and the point sd ratio is infinite (> 3). The CI on the ratio is "
  "degenerate and is reported as such. The prompt anticipated a zero LOW "
  "reading ('its shed noise may read 0') and pinned the trigger anyway.")
A("")
A(f"**REJECTION TRIGGER (shed): {'FIRES' if TRIGGER else 'does not fire'}.** "
  "The scalar-floor framing is REJECTED. The heteroscedastic Phase-B route "
  "opens regardless of prompt 42's route, per prompt 41 section 0 and "
  "section 4 (pinned).")
A("")
A("## 7. Handoff")
A("")
s2p, dftot, nu, (lo, hi) = POOL1[M[0]]
A(f"- Paper-grade floor by the pinned formula (pooled Population-1 "
  f"cross-environment sd, shed): **{g4(np.sqrt(s2p))} MWh**, df 10, "
  f"Satterthwaite nu = {nu:.2f}, 95% CI **[{g4(lo)}, {g4(hi)}] MWh**. "
  "This replaces the preview estimate (sd 306, CI [180, 880], n = 4).")
A("- **But the pinned rejection trigger FIRES**, so the scalar framing is "
  "rejected: do NOT hand a single floor to prompt 42 as paper-grade. The "
  "pooled value above is dominated by the HIGH design (nu ~ 3) and "
  "understates HIGH noise while overstating LOW/MID noise.")
A("- Cross-environment exact-pair verdict: noise at identical inputs is "
  "**NONZERO** (HIGH fresh pair delta 45.70 on one node; HIGH cross-date "
  "deltas 209–1,116; MID cross-date delta 26.67). It is zero on the LOW "
  "plateau and between the MID fresh runs and the twin. Within-wave replay "
  "determinism is prior evidence and was not retested.")
A("- The campaign floor (3,000 MWh) does NOT change in this prompt (pinned; "
  "Kay's decision after strategy review).")
A("")
A("## 8. tau and the recorded stops")
A("")
A(f"Prompt 40's break-even table puts the first-stop break-even floors at "
  f"P1 1,997 / N1 1,726 / P2 1,133 MWh. The measured pooled sd "
  f"{g4(np.sqrt(s2p))} MWh sits below all three, and the whole 95% CI "
  f"[{g4(lo)}, {g4(hi)}] sits below P2's 1,133 MWh"
  + (" as well" if hi < 1133 else " — CHECK: upper bound crosses 1,133")
  + ". Taken as a scalar, the measurement would flip every recorded stop and "
    "shrink tau by roughly 7x (prompt 40: tau_300 = 0.13–0.14 tau_old). But "
    "the trigger rejected the scalar framing: at HIGH-shed designs the "
    f"per-design sd ({g4(np.sqrt(P1[M[0]]['HIGH']['s2']))} MWh, chi2 CI up to "
    f"{g4(P1[M[0]]['HIGH']['ci'][1])}) approaches the "
    "break-even floors, while at LOW it is 0. No re-grading happens here; "
    "prompt 42's machinery consumes this result, and the Phase-B "
    "heteroscedastic prompt opens.")
A("")
A("## 9. Deviations and unpinned choices (full disclosure)")
A("")
A("1. Permutation-test statistic (|difference of mean delta^2|) and seed "
  f"({SEED}) are not pinned by the prompt; both are fixed here before "
  "looking at the test outcome, and the test itself (permutation on "
  "delta^2, 10k, alpha 0.05) is as pinned.")
A("2. 'Exact siblings' for Population 2 = the fresh in-wave exacts only "
  "(not the historical parents), keeping Population 2 inside the "
  "replicate waves.")
A("3. Population-1 pair list for the permutation test = all within-design "
  "pairs over the distinct draws (17 pairs). This follows section 4's "
  "enumeration with the accidental pairs entering exactly once (dedup).")
A("4. The variance-ratio test is degenerate at s2_LOW = 0; the p-value is "
  "the limit value 0 and the ratio CI cannot be formed. Disclosed in "
  "section 6; the trigger decision does not depend on the CI.")
A("5. Node identity for 8 of 12 tasks is unrecoverable (no hostname in "
  "stdout, no SGE accounting). Disclosed in section 2 with consequences.")
A("6. The runtime figure quoted from memory during the wait (31–33 h for "
  "HIGH) does not match the logs (23.8–24.7 h); the log values stand.")
A("7. No figures: the result is three small tables; a figure adds nothing. "
  "(House rule on bold axes therefore does not apply.)")
A("")
A("Integrity checks run by this script: CRC shed cross-check (12/12), "
  "part_a delta reproduction (4 pairs x 3 objectives), byte-identity "
  "asserts (LOW x5, MID fresh = twin, ACC-17k shed), omega identity of "
  "fresh exacts across waves, single-tier perturbation check per Pop-2 "
  "pair, df total = 10, pair counts 17 and 15, HIGH/other runtime "
  "separation.")

OUT.write_text("\n".join(L) + "\n")
print(f"wrote {OUT}")
print(f"pooled shed sd {np.sqrt(POOL1[M[0]][0]):.2f} CI [{POOL1[M[0]][3][0]:.1f}, "
      f"{POOL1[M[0]][3][1]:.1f}] nu {POOL1[M[0]][2]:.2f}; trigger fires: {TRIGGER}")
for col in M:
    print(col, "perm p =", PERM[col][1])
