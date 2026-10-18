"""
Reproducible Benchmark Runner Script.
Executes the evaluation suite, exports CSV results, generates diagnostic plots,
and outputs an experimental Markdown report.
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
    print("=" * 70)
    print("Vision-Based Aerial Localization: Research Benchmark Runner")
    print("=" * 70)

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

    # 4. Execute trials
    print("\n[3/4] Running feature matching and evaluation pipeline...")
    matcher = VisualFeatureMatcher(max_features=1200)
    results = []

    for p in test_pairs:
        trial = evaluate_trial(matcher, p, synthetic_georef)
        results.append(trial)
        err_str = f"{trial.position_error_m:.2f} m" if trial.position_error_m is not None else "N/A"
        print(f"      Trial {trial.pair_id:<28} | Status: {trial.status:<20} | Inliers: {trial.geometric_inliers:<3} | Error: {err_str:<8} | Time: {trial.total_time_ms} ms")

    # 5. Compute summary statistics
    summary = compute_summary_statistics(results)
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Total Trials Tested:           {summary.total_trials}")
    print(f"Successful Matches:            {summary.successful_matches} ({summary.match_success_rate * 100:.1f}%)")
    print(f"Failed Matches:                {summary.failed_matches}")
    print(f"Successful Localizations:      {summary.successful_localizations}")
    print(f"Median Processing Latency:     {summary.median_time_ms:.2f} ms")
    print(f"95th Percentile Latency (P95): {summary.p95_time_ms:.2f} ms")
    if summary.median_position_error_m is not None:
        print(f"Median Position Error:         {summary.median_position_error_m:.3f} meters")
        print(f"95th Percentile Error (P95):   {summary.p95_position_error_m:.3f} meters")

    # 6. Export CSV
    csv_path = exp_dir / "benchmark_results.csv"
    export_results_to_csv(results, csv_path)
    print(f"\n[4/4] Results exported to: {csv_path}")

    # 7. Generate diagnostic plots
    # Plot 1: Inlier Counts & Inlier Ratios across test pairs
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    names = [r.pair_id.replace("pair_", "") for r in results]
    inliers = [r.geometric_inliers for r in results]
    colors = ["#2ecc71" if r.status == "SUCCESS" else "#e74c3c" for r in results]

    ax1.barh(names, inliers, color=colors)
    ax1.set_xlabel("Geometric Inlier Count (RANSAC)")
    ax1.set_title("Inlier Count Across Degradation Scenarios")
    ax1.grid(axis="x", alpha=0.3)

    times = [r.total_time_ms for r in results]
    ax2.barh(names, times, color="#3498db")
    ax2.set_xlabel("Processing Time (milliseconds)")
    ax2.set_title("Latency Per Trial (CPU execution)")
    ax2.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plot_path = plots_dir / "evaluation_metrics_plot.png"
    fig.savefig(str(plot_path), dpi=150)
    plt.close(fig)
    print(f"      Diagnostic plot saved to: {plot_path}")

    # 8. Generate Markdown Report
    md_report_path = exp_dir / "benchmark_report.md"
    with md_report_path.open("w", encoding="utf-8") as f:
        f.write("# Research Evaluation Benchmark Report\n\n")
        f.write(f"- **Total Pairs Tested:** {summary.total_trials}\n")
        f.write(f"- **Match Success Rate:** {summary.match_success_rate * 100:.1f}%\n")
        f.write(f"- **Successful Localizations:** {summary.successful_localizations}\n")
        f.write(f"- **Median Latency:** {summary.median_time_ms:.2f} ms\n")
        f.write(f"- **95th Percentile Latency (P95):** {summary.p95_time_ms:.2f} ms\n")
        if summary.median_position_error_m is not None:
            f.write(f"- **Median Position Error:** {summary.median_position_error_m:.3f} meters\n")
            f.write(f"- **95th Percentile Error (P95):** {summary.p95_position_error_m:.3f} meters\n")
        f.write("\n## Detailed Trial Results Table\n\n")
        f.write("| Pair ID | Category | Status | Inliers | Error (m) | Time (ms) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            err = f"{r.position_error_m:.2f}" if r.position_error_m is not None else "N/A"
            f.write(f"| `{r.pair_id}` | {r.category} | `{r.status}` | {r.geometric_inliers} | {err} | {r.total_time_ms} |\n")
    print(f"      Markdown report saved to: {md_report_path}")


if __name__ == "__main__":
    main()
