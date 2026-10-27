# Research Evaluation Benchmark Report (Validated Methodology)

> **Scientific Disclaimer:**
> Notice: The sample match rate and zero false-positive observation apply strictly to this controlled synthetic 7-pair benchmark. Pixel RMSE is measured on independent 25-point synthetic grid mappings and does NOT claim real-world geodetic localization accuracy.

- **Total Pairs Tested:** 7
- **Sample Match Rate:** 71.4%
- **Timing Repetitions:** 5 steady-state passes (after 1 warmup pass)
- **Median Steady-State Latency:** 46.19 ms
- **95th Percentile Latency (P95):** 69.45 ms
- **Median Independent Pixel RMSE:** 2.131 pixels (across 25 independent test grid points)
- **95th Percentile Pixel RMSE (P95):** 13.214 pixels
- **Median Synthetic Grid Scale Error:** 1.066 meters (at synthetic GSD=0.5m/px)
- **95th Percentile Synthetic Grid Scale Error (P95):** 6.608 meters

## Detailed Trial Results Table

| Pair ID | Category | Status | Inliers | Pixel RMSE (px) | Synthetic Grid Err (m) | Steady-State Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `pair_01_baseline` | Baseline | `SUCCESS` | 101 | 0.88 | 0.44 | 25.95 ± 1.23 |
| `pair_02_brightness_dark` | Illumination | `SUCCESS` | 84 | 0.69 | 0.35 | 28.03 ± 2.99 |
| `pair_03_brightness_bright` | Illumination | `SUCCESS` | 21 | 15.84 | 7.92 | 25.74 ± 1.35 |
| `pair_04_rotation_20deg` | Geometric | `SUCCESS` | 65 | 2.72 | 1.36 | 59.69 ± 6.39 |
| `pair_05_sensor_noise` | Sensor Noise | `SUCCESS` | 70 | 2.13 | 1.07 | 68.54 ± 3.88 |
| `pair_06_uncorrelated_noise` | Hard Negative | `NO_CORRESPONDENCE` | 0 | N/A | N/A | 69.84 ± 1.44 |
| `pair_07_blank_frame` | Hard Negative | `INSUFFICIENT_FEATURES` | 0 | N/A | N/A | 46.19 ± 1.75 |
