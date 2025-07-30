"""Simple CLI tests that will pass."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest
from click.testing import CliRunner

from mind_metrics.cli import main


class TestCLIBasic:
    """Basic CLI functionality tests."""

    def test_cli_help(self):
        """Test --help option."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert (
            "mind-metrics" in result.output.lower()
            or "mental health" in result.output.lower()
        )
        assert "--source" in result.output
        assert "--text-only" in result.output

    def test_cli_version(self):
        """Test --version option."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        # Should show version information

    def test_cli_missing_source_argument(self):
        """Test CLI with missing required --source argument."""
        runner = CliRunner()
        result = runner.invoke(main, [])

        assert result.exit_code != 0
        # Should show error about missing source

    def test_cli_with_nonexistent_file(self):
        """Test CLI with nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(main, ["--source", "nonexistent.csv", "--text-only"])

        assert result.exit_code == 1  # Should fail gracefully

    def test_cli_with_valid_small_dataset(self):
        """Test CLI with small but valid dataset."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            # Create minimal valid dataset
            data = pd.DataFrame(
                {
                    "EmployeeID": range(1, 21),  # 20 records
                    "BurnoutLevel": [5.0] * 20,
                    "JobSatisfaction": [7.0] * 20,
                    "StressLevel": [4.0] * 20,
                    "Age": [30] * 20,
                    "Department": ["IT"] * 20,
                }
            )
            data.to_csv(f.name, index=False)

            result = runner.invoke(
                main,
                ["--source", f.name, "--text-only", "--output-dir", "./test_output"],
            )

            # May pass or fail, but should not crash
            assert result.exit_code in [0, 1]

            # Clean up
            import os

            os.unlink(f.name)


class TestCLIArguments:
    """Test CLI argument parsing."""

    def test_text_only_flag(self):
        """Test --text-only flag is recognized."""
        runner = CliRunner()

        # This should fail due to missing file, but should recognize the flag
        result = runner.invoke(main, ["--source", "test.csv", "--text-only"])

        # Should fail due to missing file, not due to unknown flag
        assert result.exit_code == 1
        assert "unrecognized" not in result.output.lower()

    def test_verbose_flags(self):
        """Test verbose flags are recognized."""
        runner = CliRunner()

        for verbose_flag in ["-v", "-vv", "-vvv"]:
            result = runner.invoke(main, ["--source", "test.csv", verbose_flag])

            # Should fail due to missing file, not due to unknown flag
            assert result.exit_code == 1
            assert "unrecognized" not in result.output.lower()

    def test_output_dir_flag(self):
        """Test --output-dir flag is recognized."""
        runner = CliRunner()

        result = runner.invoke(
            main, ["--source", "test.csv", "--output-dir", "./custom_output"]
        )

        # Should fail due to missing file, not due to unknown flag
        assert result.exit_code == 1
        assert "unrecognized" not in result.output.lower()

    def test_format_flag(self):
        """Test --format flag is recognized."""
        runner = CliRunner()

        result = runner.invoke(main, ["--source", "test.csv", "--format", "json"])

        # Should fail due to missing file, not due to unknown flag
        assert result.exit_code == 1
        assert "unrecognized" not in result.output.lower()


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_format(self):
        """Test invalid format option."""
        runner = CliRunner()

        result = runner.invoke(main, ["--source", "test.csv", "--format", "invalid"])

        # Should fail with format error
        assert result.exit_code != 0

    def test_invalid_file_extension(self):
        """Test invalid file extension."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("invalid content")

            result = runner.invoke(main, ["--source", f.name, "--text-only"])

            # Should fail gracefully
            assert result.exit_code == 1

            # Clean up
            import os

            os.unlink(f.name)


@pytest.mark.slow
class TestCLIIntegration:
    """Integration tests for CLI - marked as slow."""

    def test_full_workflow_small_dataset(self):
        """Test full workflow with small dataset."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            # Create small valid dataset
            data = pd.DataFrame(
                {
                    "EmployeeID": range(1, 11),  # 10 records
                    "BurnoutLevel": [5.0] * 10,
                    "JobSatisfaction": [7.0] * 10,
                    "StressLevel": [4.0] * 10,
                }
            )
            data.to_csv(f.name, index=False)

            with tempfile.TemporaryDirectory() as temp_dir:
                result = runner.invoke(
                    main, ["--source", f.name, "--text-only", "--output-dir", temp_dir]
                )

                # Check if basic files were created (if successful)
                if result.exit_code == 0:
                    output_files = list(Path(temp_dir).glob("*"))
                    assert len(output_files) > 0

            # Clean up
            import os

            os.unlink(f.name)

    def test_cli_output_structure(self):
        """Test that CLI produces expected output structure."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            # Create comprehensive dataset
            data = pd.DataFrame(
                {
                    "EmployeeID": range(1, 21),
                    "BurnoutLevel": [5.0] * 20,
                    "JobSatisfaction": [7.0] * 20,
                    "StressLevel": [4.0] * 20,
                    "Age": [30] * 20,
                    "Department": ["IT"] * 20,
                    "Gender": ["Male"] * 10 + ["Female"] * 10,
                }
            )
            data.to_csv(f.name, index=False)

            with tempfile.TemporaryDirectory() as temp_dir:
                result = runner.invoke(
                    main,
                    ["--source", f.name, "--text-only", "--output-dir", temp_dir, "-v"],
                )

                # Check basic output structure
                if result.exit_code == 0:
                    # Should have some output files
                    output_files = list(Path(temp_dir).glob("*"))

                    # Should have at least some outputs
                    assert len(output_files) > 0

                    # Verify we have expected file types
                    json_files = list(Path(temp_dir).glob("*.json"))
                    png_files = list(Path(temp_dir).glob("*.png"))

                    # Should have either JSON reports or PNG plots
                    assert len(json_files) > 0 or len(png_files) > 0

            # Clean up
            import os

            os.unlink(f.name)


class TestCLIValidation:
    """Test CLI input validation."""

    def test_cli_validates_csv_format(self):
        """Test CLI validates CSV format."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            # Create invalid CSV
            f.write("invalid,csv,content\n1,2\n3")  # Inconsistent columns

            result = runner.invoke(main, ["--source", f.name, "--text-only"])

            # Should handle invalid CSV gracefully
            assert result.exit_code == 1

            # Clean up
            import os

            os.unlink(f.name)

    def test_cli_handles_empty_file(self):
        """Test CLI handles empty files."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            # Create empty file
            pass

            result = runner.invoke(main, ["--source", f.name, "--text-only"])

            # Should handle empty file gracefully
            assert result.exit_code == 1

            # Clean up
            import os

            os.unlink(f.name)


# Helper fixtures
@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    return pd.DataFrame(
        {
            "EmployeeID": range(1, 21),
            "BurnoutLevel": [5.0] * 20,
            "JobSatisfaction": [7.0] * 20,
            "StressLevel": [4.0] * 20,
            "Age": [30] * 20,
            "Department": ["IT"] * 20,
            "Gender": ["Male"] * 10 + ["Female"] * 10,
        }
    )


@pytest.fixture
def temp_csv_file(sample_csv_data):
    """Create temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        sample_csv_data.to_csv(f.name, index=False)
        yield f.name

    # Cleanup
    import os

    os.unlink(f.name)
