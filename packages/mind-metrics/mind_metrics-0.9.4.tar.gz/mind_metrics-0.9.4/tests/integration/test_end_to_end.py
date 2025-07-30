"""End-to-end integration tests for Mind Metrics."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from click.testing import CliRunner

from src.analysis.burnout import BurnoutAnalyzer
from src.analysis.correlations import CorrelationAnalyzer
from src.analysis.statistics import StatisticsCalculator
from src.cli import main
from src.data.cleaner import DataCleaner
from src.data.loader import DataLoader


class TestCompleteWorkflow:
    """Test complete data analysis workflow."""

    def test_full_csv_workflow(self, sample_csv_file, temp_output_dir):
        """Test complete workflow from CSV input to report generation."""
        runner = CliRunner()

        # Run complete analysis
        result = runner.invoke(
            main,
            [
                "--source",
                sample_csv_file,
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
                "-vv",
            ],
        )

        assert result.exit_code == 0

        # Verify all expected outputs were created
        expected_files = [
            "mental_health_report.json",
            "burnout_distribution.png",
            "correlation_heatmap.png",
        ]

        for filename in expected_files:
            file_path = temp_output_dir / filename
            assert file_path.exists(), f"Expected file {filename} was not created"

            # Verify file is not empty
            assert file_path.stat().st_size > 0, f"File {filename} is empty"

        # Verify JSON report structure
        report_file = temp_output_dir / "mental_health_report.json"
        with open(report_file) as f:
            report_data = json.load(f)

        assert "summary" in report_data
        assert "burnout_analysis" in report_data
        assert "correlations" in report_data
        assert "statistics" in report_data

    def test_full_excel_workflow(self, sample_excel_file, temp_output_dir):
        """Test complete workflow from Excel input to report generation."""
        runner = CliRunner()

        result = runner.invoke(
            main,
            [
                "--source",
                sample_excel_file,
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
                "-v",
            ],
        )

        assert result.exit_code == 0

        # Verify key outputs
        assert (temp_output_dir / "mental_health_report.json").exists()

        # Verify report content
        with open(temp_output_dir / "mental_health_report.json") as f:
            report_data = json.load(f)

        assert isinstance(report_data["summary"]["total_employees"], int)
        assert report_data["summary"]["total_employees"] > 0

    def test_workflow_with_different_data_structures(self, temp_output_dir):
        """Test workflow with different data structures."""
        runner = CliRunner()

        # Create minimal dataset
        minimal_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "BurnoutLevel": [3.0, 7.5, 2.1, 8.9, 4.2],
                "JobSatisfaction": [8.0, 4.2, 9.1, 3.5, 7.8],
                "StressLevel": [4.0, 8.1, 2.5, 9.2, 5.0],
            }
        )

        minimal_file = temp_output_dir / "minimal_dataset.csv"
        minimal_data.to_csv(minimal_file, index=False)

        result = runner.invoke(
            main,
            [
                "--source",
                str(minimal_file),
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
            ],
        )

        assert result.exit_code == 0
        assert (temp_output_dir / "mental_health_report.json").exists()

    def test_workflow_with_extended_dataset(self, temp_output_dir):
        """Test workflow with dataset containing all optional columns."""
        runner = CliRunner()

        # Create comprehensive dataset
        comprehensive_data = pd.DataFrame(
            {
                "EmployeeID": range(1, 51),
                "Age": np.random.randint(22, 65, 50),
                "Gender": np.random.choice(["Male", "Female", "Other"], 50),
                "Country": np.random.choice(["USA", "Canada", "UK"], 50),
                "JobRole": np.random.choice(["Junior", "Senior", "Manager"], 50),
                "Department": np.random.choice(
                    ["IT", "HR", "Finance", "Marketing"], 50
                ),
                "YearsAtCompany": np.random.randint(0, 20, 50),
                "WorkHoursPerWeek": np.random.randint(35, 60, 50),
                "RemoteWork": np.random.choice(["Yes", "No", "Hybrid"], 50),
                "BurnoutLevel": np.random.uniform(0, 10, 50),
                "JobSatisfaction": np.random.uniform(0, 10, 50),
                "StressLevel": np.random.uniform(0, 10, 50),
                "ProductivityScore": np.random.uniform(0, 10, 50),
                "SleepHours": np.random.uniform(4, 10, 50),
                "PhysicalActivityHrs": np.random.uniform(0, 15, 50),
                "CommuteTime": np.random.randint(0, 120, 50),
                "HasMentalHealthSupport": np.random.choice(["Yes", "No"], 50),
                "ManagerSupportScore": np.random.uniform(0, 10, 50),
                "HasTherapyAccess": np.random.choice(["Yes", "No"], 50),
                "MentalHealthDaysOff": np.random.randint(0, 30, 50),
                "SalaryRange": np.random.choice(
                    ["<50k", "50k-75k", "75k-100k", "100k+"], 50
                ),
                "WorkLifeBalanceScore": np.random.uniform(0, 10, 50),
                "TeamSize": np.random.randint(3, 15, 50),
                "CareerGrowthScore": np.random.uniform(0, 10, 50),
                "BurnoutRisk": np.random.randint(0, 2, 50),
            }
        )

        comprehensive_file = temp_output_dir / "comprehensive_dataset.csv"
        comprehensive_data.to_csv(comprehensive_file, index=False)

        result = runner.invoke(
            main,
            [
                "--source",
                str(comprehensive_file),
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
                "-vv",
            ],
        )

        assert result.exit_code == 0

        # Should generate more comprehensive outputs
        expected_plots = [
            "burnout_distribution.png",
            "correlation_heatmap.png",
            "stress_vs_satisfaction.png",
            "work_life_balance_analysis.png",
            "demographic_analysis.png",
        ]

        for _plot_name in expected_plots:
            # At least some plots should be created
            plot_files = list(temp_output_dir.glob("*.png"))
            assert len(plot_files) >= 3  # Should create multiple plots


class TestComponentIntegration:
    """Test integration between different components."""

    def test_data_pipeline_integration(self, sample_mental_health_data):
        """Test integration of data loading and cleaning pipeline."""
        # Test data flows correctly through pipeline
        _ = DataLoader()
        cleaner = DataCleaner()

        # Simulate loading (use sample data directly)
        loaded_data = sample_mental_health_data

        # Clean data
        cleaned_data = cleaner.clean(loaded_data)

        # Verify data integrity
        assert isinstance(cleaned_data, pd.DataFrame)
        assert len(cleaned_data) > 0
        assert "BurnoutLevel" in cleaned_data.columns

        # Verify cleaning stats
        stats = cleaner.get_cleaning_summary()
        assert stats["original_rows"] == len(loaded_data)
        assert stats["final_rows"] == len(cleaned_data)

    def test_analysis_pipeline_integration(self, sample_mental_health_data):
        """Test integration of analysis components."""
        # Clean data first
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean(sample_mental_health_data)

        # Run all analysis components
        burnout_analyzer = BurnoutAnalyzer(cleaned_data)
        correlation_analyzer = CorrelationAnalyzer(cleaned_data)
        stats_calculator = StatisticsCalculator(cleaned_data)

        # Get results from each component
        burnout_results = burnout_analyzer.analyze_burnout_patterns()
        correlation_results = correlation_analyzer.compute_correlations()
        statistical_results = stats_calculator.calculate_basic_statistics()

        # Verify all components produce compatible outputs
        assert isinstance(burnout_results, dict)
        assert isinstance(correlation_results, pd.DataFrame)
        assert isinstance(statistical_results, dict)

        # Verify data consistency across components
        assert burnout_results["total_employees_analyzed"] == len(cleaned_data)

    def test_visualization_integration(
        self, sample_mental_health_data, temp_output_dir
    ):
        """Test integration with visualization components."""
        from src.visualization.plots import PlotGenerator

        # Clean and analyze data
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean(sample_mental_health_data)

        correlation_analyzer = CorrelationAnalyzer(cleaned_data)
        correlations = correlation_analyzer.compute_correlations()

        # Generate visualizations
        plot_gen = PlotGenerator(cleaned_data, temp_output_dir, text_only=True)

        # Create plots
        burnout_plot = plot_gen.create_burnout_distribution_plot()
        correlation_plot = plot_gen.create_correlation_heatmap(correlations)

        # Verify plots were created
        if burnout_plot:
            assert Path(burnout_plot).exists()
        if correlation_plot:
            assert Path(correlation_plot).exists()


class TestErrorHandlingIntegration:
    """Test error handling across the entire pipeline."""

    def test_invalid_data_handling(self, temp_output_dir):
        """Test handling of invalid data throughout pipeline."""
        runner = CliRunner()

        # Create dataset with various issues
        problematic_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 2, 3],  # Duplicate ID
                "BurnoutLevel": [5.0, 15.0, -2.0, 6.0],  # Out of range values
                "JobSatisfaction": [7.0, np.nan, 8.0, 6.0],  # Missing values
                "StressLevel": [4.0, 5.0, "invalid", 3.0],  # Invalid type
                "Age": [25, 150, 30, 15],  # Impossible ages
            }
        )

        problematic_file = temp_output_dir / "problematic_data.csv"
        problematic_data.to_csv(problematic_file, index=False)

        result = runner.invoke(
            main,
            [
                "--source",
                str(problematic_file),
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
                "-v",
            ],
        )

        # Should handle errors gracefully or clean data and continue
        # Exact behavior depends on implementation
        assert result.exit_code in [0, 1]  # Either success or controlled failure

    def test_missing_required_columns(self, temp_output_dir):
        """Test handling when required columns are missing."""
        runner = CliRunner()

        # Create dataset missing required columns
        incomplete_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3],
                "SomeOtherColumn": [4, 5, 6],
                # Missing BurnoutLevel, JobSatisfaction, StressLevel
            }
        )

        incomplete_file = temp_output_dir / "incomplete_data.csv"
        incomplete_data.to_csv(incomplete_file, index=False)

        result = runner.invoke(
            main,
            [
                "--source",
                str(incomplete_file),
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
            ],
        )

        assert result.exit_code == 1  # Should fail gracefully
        assert "Error" in result.output or "Missing" in result.output

    def test_empty_dataset_handling(self, temp_output_dir):
        """Test handling of empty datasets."""
        runner = CliRunner()

        # Create empty CSV file
        empty_file = temp_output_dir / "empty.csv"
        empty_file.write_text("EmployeeID,BurnoutLevel,JobSatisfaction,StressLevel\n")

        result = runner.invoke(
            main,
            [
                "--source",
                str(empty_file),
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
            ],
        )

        assert result.exit_code == 1  # Should fail gracefully
        assert "Error" in result.output


class TestOutputConsistency:
    """Test consistency of outputs across different scenarios."""

    def test_output_format_consistency(
        self, sample_mental_health_data, temp_output_dir
    ):
        """Test that output formats are consistent across runs."""
        runner = CliRunner()

        # Save sample data to file
        data_file = temp_output_dir / "consistency_test.csv"
        sample_mental_health_data.to_csv(data_file, index=False)

        # Run analysis twice
        for run_num in [1, 2]:
            run_output_dir = temp_output_dir / f"run_{run_num}"
            run_output_dir.mkdir()

            result = runner.invoke(
                main,
                [
                    "--source",
                    str(data_file),
                    "--text-only",
                    "--output-dir",
                    str(run_output_dir),
                ],
            )

            assert result.exit_code == 0

        # Compare outputs from both runs
        run1_report = temp_output_dir / "run_1" / "mental_health_report.json"
        run2_report = temp_output_dir / "run_2" / "mental_health_report.json"

        with open(run1_report) as f1, open(run2_report) as f2:
            report1 = json.load(f1)
            report2 = json.load(f2)

        # Key statistics should be identical
        assert (
            report1["summary"]["total_employees"]
            == report2["summary"]["total_employees"]
        )

        # Floating point comparisons should be close
        stats1 = report1["summary"]
        stats2 = report2["summary"]

        for key in ["average_burnout_level", "average_job_satisfaction"]:
            if key in stats1 and key in stats2:
                assert abs(stats1[key] - stats2[key]) < 0.001

    def test_different_output_formats(self, sample_mental_health_data, temp_output_dir):
        """Test consistency between different output formats."""
        runner = CliRunner()

        data_file = temp_output_dir / "format_test.csv"
        sample_mental_health_data.to_csv(data_file, index=False)

        # Test JSON output
        json_output_dir = temp_output_dir / "json_output"
        json_output_dir.mkdir()

        result_json = runner.invoke(
            main,
            [
                "--source",
                str(data_file),
                "--text-only",
                "--output-dir",
                str(json_output_dir),
                "--format",
                "json",
            ],
        )

        # Test CSV output
        csv_output_dir = temp_output_dir / "csv_output"
        csv_output_dir.mkdir()

        result_csv = runner.invoke(
            main,
            [
                "--source",
                str(data_file),
                "--text-only",
                "--output-dir",
                str(csv_output_dir),
                "--format",
                "csv",
            ],
        )

        assert result_json.exit_code == 0
        assert result_csv.exit_code == 0

        # Both should create report files
        assert (json_output_dir / "mental_health_report.json").exists()
        assert (csv_output_dir / "mental_health_report.csv").exists()


class TestPerformanceIntegration:
    """Test performance characteristics of the complete system."""

    @pytest.mark.slow
    def test_large_dataset_end_to_end(self, temp_output_dir):
        """Test end-to-end performance with large dataset."""
        runner = CliRunner()

        # Create large dataset
        large_data = pd.DataFrame(
            {
                "EmployeeID": range(1, 5001),  # 5000 employees
                "Age": np.random.randint(22, 65, 5000),
                "BurnoutLevel": np.random.uniform(0, 10, 5000),
                "JobSatisfaction": np.random.uniform(0, 10, 5000),
                "StressLevel": np.random.uniform(0, 10, 5000),
                "Department": np.random.choice(
                    ["IT", "HR", "Finance", "Marketing"], 5000
                ),
                "WorkHoursPerWeek": np.random.randint(30, 60, 5000),
            }
        )

        large_file = temp_output_dir / "large_dataset.csv"
        large_data.to_csv(large_file, index=False)

        import time

        start_time = time.time()

        result = runner.invoke(
            main,
            [
                "--source",
                str(large_file),
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
                "-v",
            ],
        )

        end_time = time.time()
        execution_time = end_time - start_time

        assert result.exit_code == 0
        assert execution_time < 120  # Should complete within 2 minutes

        # Verify outputs were created
        assert (temp_output_dir / "mental_health_report.json").exists()

    def test_memory_efficiency_integration(self, temp_output_dir):
        """Test memory efficiency of complete pipeline."""
        runner = CliRunner()

        # Create moderately large dataset
        data = pd.DataFrame(
            {
                "EmployeeID": range(1, 1001),
                "BurnoutLevel": np.random.uniform(0, 10, 1000),
                "JobSatisfaction": np.random.uniform(0, 10, 1000),
                "StressLevel": np.random.uniform(0, 10, 1000),
                "Age": np.random.randint(22, 65, 1000),
            }
        )

        data_file = temp_output_dir / "memory_test.csv"
        data.to_csv(data_file, index=False)

        result = runner.invoke(
            main,
            [
                "--source",
                str(data_file),
                "--text-only",
                "--output-dir",
                str(temp_output_dir),
            ],
        )

        assert result.exit_code == 0
        # Basic check that it completes without memory errors
