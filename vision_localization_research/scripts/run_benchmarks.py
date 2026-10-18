"""
Reproducible Benchmark Runner Script.
Executes the evaluation suite with unrecorded warmup and multi-run steady-state timing,
exports CSV results, generates diagnostic plots, and outputs an experimental Markdown report.
"""
from pathlib import Path
import sys

# Ensure src is in python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

import matplotlib.pyplot as plt
import numpy as np

from vision_loc.evaluation import (
    compute_summary_statistics,
    create_base_synthetic_landscape,
    evaluate_trial,
    export_results_to_csv,
    generate_benchmark_pairs,
)
from vision_loc.feature_matcher import VisualFeatureMatcher
from vision_loc.georeference import AffineTransform


def main():
    print("=" * 78)
    print("Vision-Based Aerial Localization: Research Benchmark Runner (Validated)")
    print("=" * 78)

    exp_dir = project_root / "experiments"
    plots_dir = exp_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 1. Authoritative synthetic reference coordinate system (UTM meters, 0.5m GSD)
    synthetic_georef = AffineTransform(
        origin_x=500000.0,
        origin_y=4000000.0,
        a=0.5,
        b=0.0,
        d=0.0,
        e=-0.5,
    )

    # 2. Generate deterministic landscape
    print("[1/4] Generating deterministic synthetic landscape (seed=42)...")
    base_landscape = create_base_synthetic_landscape(width=1200, height=1200, seed=42)

    # 3. Generate benchmark test pairs across degradation categories
    print("[2/4] Generating degradation test pairs...")
    test_pairs = generate_benchmark_pairs(base_landscape, synthetic_georef, crop_size=350)
    print(f"      Generated {len(test_pairs)} test pairs across categories:")
    for p in test_pairs:
        print(f"        - [{p['category']}] {p['pair_id']}: {p['description']}")

    # 4. Execute trials with 1 unrecorded warmup run and 5 steady-state timed repetitions
    timing_repeats = 5
    print(f"\n[3/4] Running feature matching pipeline (1 warmup + {timing_repeats} steady-state repetitions per trial)...")
    matcher = VisualFeatureMatcher(max_features=1200)
    results = []

    for p in test_pairs:
        trial = evaluate_trial(matcher, p, synthetic_georef, timing_repeats=timing_repeats)
        results.append(trial)
        rmse_str = f"{trial.pixel_reprojection_rmse:.2f} px" if trial.pixel_reprojection_rmse is not None else "N/A"
        time_str = f"{trial.steady_state_latency_median_ms:.1f} ± {trial.steady_state_latency_std_ms:.1f} ms"
        print(f"      Trial {trial.pair_id:<28} | Status: {trial.status:<20} | Inliers: {trial.geometric_inliers:<3} | RMSE: {rmse_str:<9} | Time: {time_str}")

    # 5. Compute summary statistics
    summary = compute_summary_statistics(results)
    print("\n" + "=" * 78)
    print("BENCHMARK SUMMARY STATISTICS (STEADY-STATE)")
    print("=" * 78)
    print(f"Total Trials Tested:                {summary.total_trials}")
    print(f"Sample Match Success Rate:          {summary.sample_match_success_rate * 100:.1f}% ({summary.successful_matches}/{summary.total_trials})")
    print(f"Failed Matches:                     {summary.failed_matches}")
    print(f"Timing Repetitions Per Trial:       {summary.timing_repetitions_per_trial}")
    print(f"Median Steady-State Latency:        {summary.median_steady_state_time_ms:.2f} ms")
    print(f"95th Percentile Latency (P95):      {summary.p95_steady_state_time_ms:.2f} ms")
    if summary.median_pixel_rmse is not None:
        print(f"Median Reprojection RMSE:           {summary.median_pixel_rmse:.3f} pixels (on 25 independent checkpoints)")
        print(f"95th Percentile RMSE (P95):         {summary.p95_pixel_rmse:.3f} pixels")
    if summary.median_synthetic_grid_error_m is not None:
        print(f"Median Synthetic Grid Error:        {summary.median_synthetic_grid_error_m:.3f} m (scaled at GSD=0.5m/px)")
        print(f"95th Percentile Grid Error (P95):   {summary.p95_synthetic_grid_error_m:.3f} m")

    print(f"\n[NOTE] {summary.disclaimer}")

    # 6. Export CSV
    csv_path = exp_dir / "benchmark_results.csv"
    export_results_to_csv(results, csv_path)
    print(f"\n[4/4] Results exported to: {csv_path}")

    # 7. Generate diagnostic plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    names = [r.pair_id.replace("pair_", "") for r in results]
    inliers = [r.geometric_inliers for r in results]
    colors = ["#2ecc71" if r.status == "SUCCESS" else "#e74c3c" for r in results]

    ax1.barh(names, inliers, color=colors)
    ax1.set_xlabel("Geometric Inlier Count (RANSAC)")
    ax1.set_title("Inlier Count Across Degradation Scenarios")
    ax1.grid(axis="x", alpha=0.3)

    latencies = [r.steady_state_latency_median_ms for r in results]
    errors = [r.steady_state_latency_std_ms for r in results]
    ax2.barh(names, latencies, xerr=errors, color="#3498db", capsize=3)
    ax2.set_xlabel("Steady-State Latency (ms, Median ± Std)")
    ax2.set_title(f"Steady-State Processing Time ({timing_repeats} Repetitions)")
    ax2.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plot_path = plots_dir / "evaluation_metrics_plot.png"
    fig.savefig(str(plot_path), dpi=150)
    plt.close(fig)
    print(f"      Diagnostic plot saved to: {plot_path}")

    # 8. Generate Markdown Report
    md_report_path = exp_dir / "benchmark_report.md"
    with md_report_path.open("w", encoding="utf-8") as f:
        f.write("# Research Evaluation Benchmark Report (Validated Methodology)\n\n")
        f.write("> **Scientific Disclaimer:**\n")
        f.write(f"> {summary.disclaimer}\n\n")
        f.write(f"- **Total Pairs Tested:** {summary.total_trials}\n")
        f.write(f"- **Sample Match Rate:** {summary.sample_match_success_rate * 100:.1f}%\n")
        f.write(f"- **Timing Repetitions:** {summary.timing_repetitions_per_trial} steady-state passes (after 1 warmup pass)\n")
        f.write(f"- **Median Steady-State Latency:** {summary.median_steady_state_time_ms:.2f} ms\n")
        f.write(f"- **95th Percentile Latency (P95):** {summary.p95_steady_state_time_ms:.2f} ms\n")
        if summary.median_pixel_rmse is not None:
            f.write(f"- **Median Independent Pixel RMSE:** {summary.median_pixel_rmse:.3f} pixels (across 25 independent test grid points)\n")
            f.write(f"- **95th Percentile Pixel RMSE (P95):** {summary.p95_pixel_rmse:.3f} pixels\n")
        if summary.median_synthetic_grid_error_m is not None:
            f.write(f"- **Median Synthetic Grid Scale Error:** {summary.median_synthetic_grid_error_m:.3f} meters (at synthetic GSD=0.5m/px)\n")
            f.write(f"- **95th Percentile Synthetic Grid Scale Error (P95):** {summary.p95_synthetic_grid_error_m:.3f} meters\n")
        f.write("\n## Detailed Trial Results Table\n\n")
        f.write("| Pair ID | Category | Status | Inliers | Pixel RMSE (px) | Synthetic Grid Err (m) | Steady-State Latency (ms) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            rmse_s = f"{r.pixel_reprojection_rmse:.2f}" if r.pixel_reprojection_rmse is not None else "N/A"
            grid_s = f"{r.synthetic_grid_error_m:.2f}" if r.synthetic_grid_error_m is not None else "N/A"
            f.write(f"| `{r.pair_id}` | {r.category} | `{r.status}` | {r.geometric_inliers} | {rmse_s} | {grid_s} | {r.steady_state_latency_median_ms} ± {r.steady_state_latency_std_ms} |\n")
    print(f"      Markdown report saved to: {md_report_path}")


if __name__ == "__main__":
    main()
