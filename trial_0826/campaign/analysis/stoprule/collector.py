"""Prompt 37 collector: results/<cell>/<method>/seed<s>.npz -> per-run
trajectory summaries (summary/trajectories.json) and per-(run, rule) stop
metrics (summary/stops.csv.gz). Runs on CRC after the array (merges + commits
the summaries, never the raw npz) and locally for the 2-D replay.

Per run, at R_j (run's frozen box) and at R_union (problem box):
H_obs[k] (noisy observations), H_true[k] (noise-free truth at the queried
points), H* (true lattice front), tau_j; plus front density (observed) per
round, the PredGP audit, the H_k prediction (PredGP mean, fit < k) and
M3's E[HVI].
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sr_common import hv, mc_threshold, nd_mask  # noqa: E402
from problems import Problem  # noqa: E402
import rules  # noqa: E402

RESULTS = HERE / "results"
SUMMARY = HERE / "summary"


def summarize(path: Path, prob_cache: dict) -> dict:
    z = np.load(path, allow_pickle=True)
    rec = json.loads(str(z["rec"]))
    key = (rec["problem"], rec["noise"])
    if key not in prob_cache:
        prob_cache[key] = Problem(rec["problem"], noise_mult=rec["noise"])
    prob = prob_cache[key]
    idx, Yo = z["idx"].astype(int), z["Yobs"]
    Yt = prob.T[idx]
    n0, q, R = rec["n0"], rec["q"], rec["rounds"]
    ns = [n0 + k * q for k in range(R + 1)]
    out = {k: rec[k] for k in ("problem", "method", "seed", "noise", "q", "rounds",
                               "cand_rule", "n0", "tau")}
    out["cell"] = path.parent.parent.name
    for box, ref in (("frozen", np.asarray(rec["ref_frozen"], float)), ("union", prob.ref_union)):
        Ho = np.array([hv(Yo[:n], ref) for n in ns])
        Ht = np.array([hv(Yt[:n], ref) for n in ns])
        Hs = prob.hv_star(ref)
        tau = rec["tau"] if box == "frozen" else mc_threshold(Yo[:n0], ref, prob.floors)
        out[box] = {"ref": ref.tolist(), "H_obs": Ho.tolist(), "H_true": Ht.tolist(),
                    "H_star": Hs, "tau": tau}
    out["density"] = [float(nd_mask(Yo[:n]).mean()) for n in ns]
    pr = rec["per_round"]
    out["t_acq"] = [r["t_acq"] for r in pr]
    out["n_cand"] = [r["n_cand"] for r in pr]
    if rec["method"] == "M3":
        out["ehvi"] = [r["ehvi256"] for r in pr]
    if pr and "audit" in pr[0]:
        out["audit_rms"] = [[a["rms_z"] for a in r["audit"]] for r in pr]
        out["audit_cov"] = [[a["cov95"] for a in r["audit"]] for r in pr]
        out["audit_ok"] = [[a["calibrated"] for a in r["audit"]] for r in pr]
        ref = np.asarray(rec["ref_frozen"], float)
        # H_k predicted by PredGP fit on rounds < k, at X_{1:k} (plug-in mean)
        out["H_pred"] = [hv(np.asarray(r["pred_mean_all"]), ref) for r in pr]
    # needle discovery (Z-needle): first round that queried a basin cell
    if rec["problem"] == "Z-needle":
        basin = set(prob.meta["needle"]["basin_idx"])
        hit = [k for k in range(R + 1) if any(int(i) in basin for i in idx[:ns[k]])]
        out["needle_round"] = hit[0] if hit else None
    return out


def stops_for(s: dict) -> list[dict]:
    rows = []
    for box in ("frozen", "union"):
        b = s[box]
        traj = {"H_obs": b["H_obs"], "H_true": b["H_true"], "H_star": b["H_star"],
                "tau": b["tau"], "q": s["q"], "ehvi": s.get("ehvi") if box == "frozen" else None}
        extra = rules.apply_q4(traj) if s["q"] == 4 else []
        for r in rules.apply_all(traj) + extra:
            rows.append({"cell": s["cell"], "problem": s["problem"], "method": s["method"],
                         "seed": s["seed"], "noise": s["noise"], "q": s["q"], "box": box,
                         "density_at_stop": s["density"][r["stop"]], **r})
    return rows


def collect(pattern: str = "*") -> tuple[list[dict], pd.DataFrame]:
    SUMMARY.mkdir(exist_ok=True)
    cache: dict = {}
    summ, rows = [], []
    for p in sorted(RESULTS.glob(f"{pattern}/*/seed*.npz")):
        if p.name.endswith(".ckpt.npz"):
            continue
        s = summarize(p, cache)
        summ.append(s)
        rows += stops_for(s)
    df = pd.DataFrame(rows)
    tag = "" if pattern == "*" else "_" + pattern.replace("*", "").replace(":", "_").strip("_")
    (SUMMARY / f"trajectories{tag}.json").write_text(json.dumps(summ, default=float) + "\n")
    df.to_csv(SUMMARY / f"stops{tag}.csv.gz", index=False)
    return summ, df


if __name__ == "__main__":
    s, df = collect(sys.argv[1] if len(sys.argv) > 1 else "*")
    print(f"{len(s)} runs, {len(df)} stop rows")
