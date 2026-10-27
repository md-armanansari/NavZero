"""
Automated unit tests for DefenseBenchmarkRunner, metrics aggregation, and report generation.
"""

import pytest
from navzero.core.defense_benchmark import (
    ScenarioMetrics,
    BenchmarkReport,
    DefenseBenchmarkRunner
)


@pytest.fixture
def benchmark_runner():
    return DefenseBenchmarkRunner()


def test_run_single_scenario(benchmark_runner):
    metrics = benchmark_runner.run_scenario("ALPHA_FORWARD_INGRESS", num_steps=10)

    assert isinstance(metrics, ScenarioMetrics)
    assert metrics.scenario_id == "ALPHA_FORWARD_INGRESS"
    assert metrics.frames_evaluated == 10
    assert metrics.mean_error_m >= 0.0
    assert metrics.cep50_m <= metrics.cep95_m
    assert metrics.max_error_m >= metrics.cep95_m or abs(metrics.max_error_m - metrics.cep95_m) < 1e-4
    assert metrics.avg_latency_ms > 0.0
    assert metrics.success_rate_pct > 80.0
    assert len(metrics.mission_verdict) > 0


def test_run_full_benchmark(benchmark_runner):
    report = benchmark_runner.run_full_benchmark(num_steps_per_scenario=5)

    assert isinstance(report, BenchmarkReport)
    assert report.total_scenarios == 3
    assert len(report.results) == 3
    assert report.overall_mean_error_m >= 0.0
    assert report.overall_cep95_m >= 0.0
    assert report.overall_avg_latency_ms > 0.0
    assert report.overall_success_rate > 0.0

    # Test CSV serialization
    csv_text = report.to_csv()
    assert "Scenario_ID,Scenario_Name" in csv_text
    assert "ALPHA_FORWARD_INGRESS" in csv_text
    assert "BRAVO_RIVER_VALLEY_NIGHT" in csv_text
    assert "CHARLIE_DEEP_JAMMING_WHITEOUT" in csv_text

    # Test markdown report generation
    md_text = report.to_summary_markdown()
    assert "NAVZERO DEFENSE EVALUATION BENCHMARK REPORT" in md_text
    assert "CEP95" in md_text
    assert "Operation Desert Falcon" in md_text


def test_invalid_scenario_id_raises(benchmark_runner):
    with pytest.raises(ValueError):
        benchmark_runner.run_scenario("INVALID_MISSION_XYZ", num_steps=5)
