# Backfill sensitivity (prompt 30, round-1-only, REPORT-ONLY)

LOO RMSE (closed form) on the 32 in-box points, prediction
GPs trained on (a) the 32 alone vs (b) 32 + 10 backfill rows
(absent tiers encoded 0). Never switch training sets without
Kay.

- load_shed_mwh: LOO RMSE 32-only = 1,879.9; with backfill = 1,699.8 (delta -180.1; floor 3,000)
- true_curtailment_mwh: LOO RMSE 32-only = 40,604.5; with backfill = 35,029.4 (delta -5,575.1; floor 5,000)
- total_cost_less_synthetic_usd: LOO RMSE 32-only = 4,196,390.0; with backfill = 4,123,953.3 (delta -72,436.7; floor 500,000)
