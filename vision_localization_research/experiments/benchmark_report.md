# Research Evaluation Benchmark Report

- **Total Pairs Tested:** 7
- **Match Success Rate:** 71.4%
- **Successful Localizations:** 5
- **Median Latency:** 64.70 ms
- **95th Percentile Latency (P95):** 741.90 ms
- **Median Position Error:** 0.288 meters
- **95th Percentile Error (P95):** 3.451 meters

## Detailed Trial Results Table

| Pair ID | Category | Status | Inliers | Error (m) | Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `pair_01_baseline` | Baseline | `SUCCESS` | 101 | 0.22 | 1017.29 |
| `pair_02_brightness_dark` | Illumination | `SUCCESS` | 84 | 0.29 | 57.49 |
| `pair_03_brightness_bright` | Illumination | `SUCCESS` | 21 | 4.21 | 64.7 |
| `pair_04_rotation_20deg` | Geometric | `SUCCESS` | 65 | 0.16 | 62.78 |
| `pair_05_sensor_noise` | Sensor Noise | `SUCCESS` | 70 | 0.43 | 77.74 |
| `pair_06_uncorrelated_noise` | Hard Negative | `NO_CORRESPONDENCE` | 0 | N/A | 99.34 |
| `pair_07_blank_frame` | Hard Negative | `INSUFFICIENT_FEATURES` | 0 | N/A | 63.68 |
