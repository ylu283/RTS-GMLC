# Generated-metadata provenance (make_metadata.py)

Vendored state = commit-pinned MD5SUMS.vendored. This run's input -> output MD5s (32-char):

| file | input md5 | output md5 |
|---|---|---|
| branch.csv | df72b63b4f21a4042732531070c6664f | 3fe279ff4a2dfe9e9dba2cc256a2961d |
| DAY_AHEAD_load.csv | 96b78d9d755ed4156e42afca8e1dd298 | 6053fc8869561d2c3b570bdb3c6a2200 |
| REAL_TIME_load.csv | 96b78d9d755ed4156e42afca8e1dd298 | 6053fc8869561d2c3b570bdb3c6a2200 |
| DAY_AHEAD_solar.csv | 20d799754349519c61699c46448a7adc | 435ddf1ebbce54ce9f593fa3e000b9f5 |
| REAL_TIME_solar.csv | 20d799754349519c61699c46448a7adc | 435ddf1ebbce54ce9f593fa3e000b9f5 |
| DAY_AHEAD_wind.csv | b0eb20289f9b5073ff258eb6f50e2908 | eaac5aaf43a98ba668c118dff77f34f8 |
| REAL_TIME_wind.csv | b0eb20289f9b5073ff258eb6f50e2908 | eaac5aaf43a98ba668c118dff77f34f8 |
| timeseries_pointers.csv | (generated) | 9e2ac0da1c771f9b94d9840a4586524b |
| simulation_objects.csv | (generated) | 8a67288cfa1569eeac3f5c67c8138267 |

timeseries_pointers rows: 554 (2 sims x (123 Area MW Load + 82 wind PMax + 72 solar PMax)); HYDRO deliberately unpointed (scalar PMax — see CONFIG_ERCOT.md).

Processing-notebook identity (upstream Data_public_5year -> these CSVs):

- `33c5205947fb5dc67884320f3c57e63f`  2_demo_processing_kay copy.ipynb (gtep/123_bus_coal/ERCOT_BUS123_base_XC_editeddata/original_data/)
- `1a143831cbc3638800d41e38729d26eb`  demo_processing_XC.ipynb (gtep/123_bus_coal/ERCOT_BUS123_base_XC_editeddata/ — the DIFFERENT notebook named by MANIFEST.md SS2/SS6; recorded so the TODO closes against the right file)
