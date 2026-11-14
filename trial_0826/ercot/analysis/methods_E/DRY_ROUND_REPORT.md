# methods_E Part A dry round — 2026-11-14 17:46 UTC

scratch = `/private/tmp/claude-501/-Users-yilu-Documents-GitHub-RTS-GMLC/b07c1295-f5b8-4bfe-a09b-68be92e92897/scratchpad/dry55`; fast mode = False; python = 3.10.20

botorch 0.16.1, torch 2.12.0, bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15

## Scratch A (Sigma placeholder = diag (0.02 x sd)^2)

- loader = stub, configs = stub, n0 = 32, R source = PLACEHOLDER (Part A): nadir + 0.1 (nadir - ideal) over the 48 loaded n0_E rows
- R = [359460.1614, 2086136873.0495, 12688.539, 3052.8573]
- tau_joint = 1.10334e+17, tau_marginal = 1.07928e+17, joint/marginal = 1.0223 (PLACEHOLDER (Part A): diag (0.02 x start-set sd)^2)
- hv0 = 2.79692e+19; recompute-tau reproduced the ledger (equality)
- r1 proposals pairwise disjoint across seed_ids 0-4 (acq seeds [20261007, 20261107, 20261207, 20261307, 20261407]); settings {'mc_samples': 128, 'num_restarts': 20, 'raw_samples': 512, 'alpha': 0.0, 'prune_baseline': True, 'sequential': True, 'fast_mode': False, 'constraint': 'none', 'guardrail_mode': 'monitor', 'seed': 20261007, 'dtype': 'float64'}
- r1 qNEHVI seconds per lane: [172.1, 408.6, 405.0, 375.5, 142.3]

### s0 — two clean rounds

- r1: n=40 n_hv=40 hv=3.31509e+19 gain=5.18166e+18 gain/tau_joint=46.963 would_stop joint/marginal=False/False C2=False C3=False decision=graded (record_only)
- r2: n=48 n_hv=48 hv=3.56028e+19 gain=2.45189e+18 gain/tau_joint=22.222 would_stop joint/marginal=False/False C2=False C3=False decision=graded (record_only)
- r1 calibration: {"V1": {"mean_z": 0.791, "rms_z": 1.455, "cov95": 6, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.379, "rms_z": 1.097, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "R4": {"mean_z": 0.251, "rms_z": 0.448, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "N1": {"mean_z": -0.895, "rms_z": 1.316, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- first_fire_round: {'tau_joint': None, 'tau_marginal': None}
- wave r3 proposed: True

### s1 — one shed violation in r1

- guardrail_mode after grading r1: constrain (flipped at round 1); violations ['methods_E_qnehvi_s1_r1:3']
- r2 proposed under constraint: `shed <= 1.0 MWh (GP on the accumulated R1 column)`; n_hv at r1 = 39 (violating row excluded), n_train = 40 (kept in training)

### s2 — two shed violations in r1

- `analysis/methods_E/qnehvi/s2/HALT_FOR_DECISION.md` written; r2 NOT proposed; `propose --round 2` refused
- - 2 R1 shed violations (> 1.0 MWh) in round 1: ['methods_E_qnehvi_s2_r1:2', 'methods_E_qnehvi_s2_r1:6']

### s3 — two SUSPECT runs in r1

- HALT: ["2 SUSPECT runs in round 1: ['methods_E_qnehvi_s3_r1:1', 'methods_E_qnehvi_s3_r1:8']"]; n_hv = 38 (both excluded)

### s4 — one SUSPECT + one R2 flag in r1

- suspects ['methods_E_qnehvi_s4_r1:5']; n_hv = 39, n_train for r2 = 39 (SUSPECT out of both); R2 flag rounds [1]; no halt; r2 proposed

### Plumbing

- qsub never called (shim would have logged)
- origin git log (bot commits pushed):

```
8775253 ercot-bot: methods_E qnehvi s4 r1 graded + r2 proposed (methods_E_qnehvi_s4_r2)
f25581f ercot-bot: methods_E qnehvi s3 r1 graded (43.34 tau_joint) — HALT FOR DECISION
723c1d6 ercot-bot: methods_E qnehvi s2 r1 graded (39.77 tau_joint) — HALT FOR DECISION
3c1a347 ercot-bot: methods_E qnehvi s1 r1 graded + r2 proposed (methods_E_qnehvi_s1_r2)
44136cb ercot-bot: methods_E qnehvi s0 r2 graded + r3 proposed (methods_E_qnehvi_s0_r3)
c656e84 ercot-bot: methods_E qnehvi s0 r1 graded + r2 proposed (methods_E_qnehvi_s0_r2)
d3b394e seed
```

## Scratch B (Sigma = 0 -> tau = 0)

- tau_joint = tau_marginal = 0; README carries the plan-3 statement; r1 graded: gain = 5.18166e+18, gain_tau = None, would_stop = False (budget-cap-only)

## Timings (s)

| step | seconds |
|---|---|
| init-all (5 lanes: init + r1) | 2658 |
| recompute-tau s0 | 23 |
| s0 run r1 (grade + propose r2) | 182 |
| s0 run r2 | 219 |
| s1 run r1 (one violation) | 182 |
| s2 run r1 (two violations -> HALT) | 1 |
| s3 run r1 (two SUSPECT -> HALT) | 1 |
| s4 run r1 (one SUSPECT + R2 flag) | 136 |
| B init s0 (Sigma = 0) | 0 |
| B run r0 + r1 | 238 |
