# Screening analysis

Effect-share criterion: independent iff OAT curtailment-reduction share >= 5% (noise floor is zero; see docstring).

         site tier_now  pem_mw  curt_reduction_mwh  curt_red_per_mw  shed_reduction_mwh  pem_cf  share_of_oat_total     verdict
   303_WIND_1 wind_303 423.500         671,601.561        1,585.836          11,344.321   0.385               0.295 independent
   317_WIND_1 wind_317 399.550         498,712.005        1,248.184          21,969.910   0.426               0.219 independent
   122_WIND_1 wind_122 356.750         416,555.923        1,167.641          21,432.962   0.429               0.183 independent
121_NUCLEAR_1  nuclear 200.000         371,140.738        1,855.704           3,492.341   0.960               0.163 independent
     319_PV_1   pv_319  75.280          95,539.407        1,269.121            -457.401   0.415               0.042     cluster
   309_WIND_1     tail  74.150          64,300.698          867.171             384.251   0.340               0.028     cluster
     310_PV_2     tail  20.640          35,302.604        1,710.397          -2,475.082   0.411               0.016     cluster
     324_PV_2   pv_324  20.640          32,814.177        1,589.834          -2,192.620   0.412               0.014     cluster
     320_PV_1     tail  20.640          30,529.119        1,479.124          -1,809.498   0.412               0.013     cluster
     324_PV_1   pv_324  19.880          29,024.301        1,459.975          -1,099.974   0.417               0.013     cluster
     324_PV_3   pv_324  20.400          27,968.988        1,371.029           2,292.791   0.415               0.012     cluster

Sum of OAT curtailment reductions: 2,273,490 MWh
All-in joint reduction:            1,470,501 MWh
Interaction gap (sum-OAT vs joint): +54.6%
  > 0: sites are substitutes — OAT overstates marginal sites;
  the larger the gap, the less additive the landscape (GP kernel note).

All-in load-shed reduction: 38,757 MWh

Tier-change candidates (verdict differs from current tier structure — final call is Kay's, edit tiers.py accordingly):
    site tier_now  share_of_oat_total verdict
319_PV_1   pv_319            0.042023 cluster
