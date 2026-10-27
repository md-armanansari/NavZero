# Research Evaluation Benchmark Report (Validated Methodology)

> **Scientific Disclaimer:**
> Notice: The sample match rate and zero false-positive observation apply strictly to this controlled synthetic 7-pair benchmark. Pixel RMSE is measured on independent 25-point synthetic grid mappings and does NOT claim real-world geodetic localization accuracy.

- **Total Pairs Tested:** 7
- **Sample Match Rate:** 71.4%
- **Timing Repetitions:** 5 steady-state passes (after 1 warmup pass)
- **Median Steady-State Latency:** 8.64 ms
- **95th Percentile Latency (P95):** 11.47 ms
- **Median Independent Pixel RMSE:** 1.736 pixels (across 25 independent test grid points)
- **95th Percentile Pixel RMSE (P95):** 13.214 pixels
- **Median Synthetic Grid Scale Error:** 0.868 meters (at synthetic GSD=0.5m/px)
- **95th Percentile Synthetic Grid Scale Error (P95):** 6.607 meters

## Detailed Trial Results Table

| Pair ID | Category | Status | Inliers | Pixel RMSE (px) | Synthetic Grid Err (m) | Steady-State Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `pair_01_baseline` | Baseline | `SUCCESS` | 101 | 0.88 | 0.44 | 8.53 ± 0.13 |
| `pair_02_brightness_dark` | Illumination | `SUCCESS` | 84 | 0.69 | 0.35 | 8.32 ± 0.13 |
| `pair_03_brightness_bright` | Illumination | `SUCCESS` | 21 | 15.84 | 7.92 | 8.64 ± 0.1 |
| `pair_04_rotation_20deg` | Geometric | `SUCCESS` | 65 | 2.72 | 1.36 | 8.79 ± 0.12 |
| `pair_05_sensor_noise` | Sensor Noise | `SUCCESS` | 70 | 1.74 | 0.87 | 10.62 ± 0.8 |
| `pair_06_uncorrelated_noise` | Hard Negative | `NO_CORRESPONDENCE` | 0 | N/A | N/A | 11.84 ± 0.15 |
| `pair_07_blank_frame` | Hard Negative | `INSUFFICIENT_FEATURES` | 0 | N/A | N/A | 7.89 ± 0.18 |
