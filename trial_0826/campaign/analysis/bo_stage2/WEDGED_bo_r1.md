# WEDGED — acquisition job for round 1 crashed (rc=1)

at: 2026-10-08T19:30:24Z   JOB_ID: 1516259

## last step reached
2026-10-08T19:30:21+00:00 round=1: run r1: submitting r2 triple

## any JIDs already issued
`SUBMITTED r<k>:` line below. **Silent-death watch: no email of ANY kind
SUBMITTED r1: array=1516257 collector=1516258 acq=1516259

## stderr tail
Loading CRC_default/1.1
Loading CRC_default/1.1
/users/ylu28/.conda/envs/BOGP_CRC/lib/python3.11/site-packages/torch/jit/_script.py:1491: FutureWarning: `torch.jit.script` is deprecated. Please switch to `torch.compile` or `torch.export`.
  warnings.warn(
STEP: run r1: git pull
STEP: run r1: ingest gate
STEP: run r1: idempotency guards
STEP: run r1: grading
STEP: run r1: stop checks
STEP: run r1: proposing round 2
STEP: propose r2: loading training data
STEP: propose r2: fitting prediction GPs on n=40
STEP: propose r2: acquisition (q-ParEGO, candidates mode)
STEP: propose r2: building wave + predictions
STEP: run r1: committing full round record BEFORE submitting
STEP: run r1: submitting r2 triple
From github.com:ylu283/RTS-GMLC
 * branch            d6         -> FETCH_HEAD
Already up to date.
Unable to run job: denied: host "d12chas350.crc.nd.edu" is no submit host.
Exiting.
Traceback (most recent call last):
  File "/groups/adowling/ylu28/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/acquire_next.py", line 633, in <module>
    sys.exit(main())
             ^^^^^^
  File "/groups/adowling/ylu28/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/acquire_next.py", line 626, in main
    return run_round(root, args.round)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/groups/adowling/ylu28/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/acquire_next.py", line 570, in run_round
    subprocess.run(["bash", os.path.join(next_wave, "submit_this.sh")],
  File "/users/ylu28/.conda/envs/BOGP_CRC/lib/python3.11/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['bash', '/groups/adowling/ylu28/RTS-GMLC/trial_0826/campaign/waves/bo_C_r2/submit_this.sh']' returned non-zero exit status 1.

Recovery (ROUND_LOG header): never qdel the running array from
here, never resubmit automatically. Manual: push by hand + qsub
the recorded triple — never re-run acquire_next for a round
that already proposed.
