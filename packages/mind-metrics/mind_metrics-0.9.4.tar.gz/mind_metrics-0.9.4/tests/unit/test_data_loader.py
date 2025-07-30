"""Unit tests for DataLoader class."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from src.data.loader import (
    DataLoader,
    DataValidationError,
    MentalHealthDataSchema,
)


class TestDataLoader:
    """Test suite for DataLoader class."""

    def test_init_default_schema(self):
        """Test DataLoader initialization with default schema."""
        loader = DataLoader()
        assert loader.schema is not None
        assert isinstance(loader.schema, MentalHealthDataSchema)

    def test_init_custom_schema(self):
        """Test DataLoader initialization with custom schema."""
        custom_schema = MentalHealthDataSchema()
        loader = DataLoader(schema=custom_schema)
        assert loader.schema == custom_schema

    def test_load_csv_file_success(self, sample_csv_file):
        """Test successful CSV file loading."""
        loader = DataLoader()
        data = loader.load(sample_csv_file)

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "EmployeeID" in data.columns
        assert "BurnoutLevel" in data.columns

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading nonexistent file raises FileNotFoundError."""
        loader = DataLoader()

        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent_file.csv")

    def test_load_unsupported_format_raises_error(self, tmp_path):
        """Test that unsupported file format raises ValueError."""
        # Create a file with unsupported extension
        unsupported_file = tmp_path / "test.txt"
        unsupported_file.write_text("some content")

        loader = DataLoader()

        with pytest.raises(ValueError, match="Unsupported file format"):
            loader.load(str(unsupported_file))

    def test_is_url_detection(self):
        """Test URL detection functionality."""
        loader = DataLoader()

        assert loader._is_url("https://example.com/data.csv")
        assert loader._is_url("http://example.com/data.xlsx")
        assert not loader._is_url("/local/path/data.csv")
        assert not loader._is_url("data.csv")
        assert not loader._is_url("")

    @patch("requests.get")
    def test_load_from_url_success(self, mock_get):
        """Test successful URL loading."""
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"content-type": "text/csv"}
        mock_get.return_value = mock_response

        # Create larger dataset for validation
        large_data = pd.DataFrame(
            {
                "EmployeeID": list(range(1, 21)),  # 20 records
                "BurnoutLevel": [5.0] * 20,
                "JobSatisfaction": [7.0] * 20,
                "StressLevel": [4.0] * 20,
            }
        )

        # Mock pandas read_csv
        with patch("pandas.read_csv") as mock_read_csv:
            mock_read_csv.return_value = large_data

            loader = DataLoader()
            data = loader.load("https://example.com/data.csv")

            assert isinstance(data, pd.DataFrame)
            assert len(data) == 20
            mock_get.assert_called_once()

    @patch("requests.get")
    def test_load_from_url_failure(self, mock_get):
        """Test URL loading failure handling."""
        # Mock failed HTTP response
        mock_get.side_effect = requests.RequestException("Network error")

        loader = DataLoader()

        with pytest.raises(requests.RequestException):
            loader.load("https://example.com/data.csv")

    def test_validate_data_success(self, sample_mental_health_data):
        """Test successful data validation."""
        loader = DataLoader()

        # Should not raise any exception
        loader._validate_data(sample_mental_health_data)

    def test_validate_data_empty_dataset(self):
        """Test validation of empty dataset."""
        loader = DataLoader()
        empty_data = pd.DataFrame()

        with pytest.raises(DataValidationError, match="Dataset is empty"):
            loader._validate_data(empty_data)

    def test_validate_data_missing_required_columns(self):
        """Test validation with missing required columns."""
        loader = DataLoader()
        invalid_data = pd.DataFrame(
            {"SomeColumn": [1, 2, 3], "AnotherColumn": [4, 5, 6]}
        )

        with pytest.raises(DataValidationError, match="Missing required columns"):
            loader._validate_data(invalid_data)

    def test_validate_data_too_small_dataset(self):
        """Test validation of dataset that's too small."""
        loader = DataLoader()
        small_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2],
                "BurnoutLevel": [5.0, 6.0],
                "JobSatisfaction": [7.0, 8.0],
                "StressLevel": [4.0, 5.0],
            }
        )

        with pytest.raises(DataValidationError, match="Dataset too small"):
            loader._validate_data(small_data)

    def test_validate_score_ranges_within_bounds(self):
        """Test that valid score ranges pass validation."""
        loader = DataLoader()
        data_with_valid_ranges = pd.DataFrame(
            {
                "EmployeeID": list(range(1, 21)),  # 20 records
                "BurnoutLevel": [5] * 20,  # Valid range
                "JobSatisfaction": [7] * 20,
                "StressLevel": [4] * 20,
            }
        )

        # Should not raise exception
        loader._validate_data(data_with_valid_ranges)

    @pytest.mark.parametrize(
        "file_extension,expected_method",
        [
            (".csv", "read_csv"),
            (".xlsx", "read_excel"),
            (".xls", "read_excel"),
        ],
    )
    def test_file_extension_handling(self, file_extension, expected_method, tmp_path):
        """Test that different file extensions use correct pandas methods."""
        # Create a temporary file with the specified extension
        test_file = tmp_path / f"test{file_extension}"

        # Create sample data with enough records
        sample_data = pd.DataFrame(
            {
                "EmployeeID": list(range(1, 21)),  # 20 records
                "BurnoutLevel": [5.0] * 20,
                "JobSatisfaction": [7.0] * 20,
                "StressLevel": [4.0] * 20,
            }
        )

        # Save in appropriate format
        if file_extension == ".csv":
            sample_data.to_csv(test_file, index=False)
        else:
            sample_data.to_excel(test_file, index=False)

        loader = DataLoader()
        data = loader.load(str(test_file))

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 20

    def test_load_corrupted_csv_graceful(self, tmp_path):
        """Test handling of corrupted CSV files."""
        corrupted_file = tmp_path / "corrupted.csv"
        # Create corrupted but complete CSV
        corrupted_content = "EmployeeID,BurnoutLevel,JobSatisfaction,StressLevel\n"
        for i in range(1, 21):  # 20 records
            corrupted_content += f"{i},5.0,7.0,4.0\n"
        corrupted_file.write_text(corrupted_content)

        loader = DataLoader()
        data = loader.load(str(corrupted_file))
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 20

    def test_get_data_info(self, sample_mental_health_data):
        """Test data info generation."""
        loader = DataLoader()
        info = loader.get_data_info(sample_mental_health_data)

        assert "total_records" in info
        assert "total_columns" in info
        assert "columns" in info
        assert "missing_data" in info
        assert "data_types" in info
        assert "memory_usage" in info

        assert info["total_records"] == len(sample_mental_health_data)
        assert info["total_columns"] == len(sample_mental_health_data.columns)
        assert isinstance(info["columns"], list)

    def test_load_path_object(self, sample_csv_file):
        """Test loading with Path object instead of string."""
        loader = DataLoader()
        path_obj = Path(sample_csv_file)
        data = loader.load(path_obj)

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0

    def test_numeric_conversion_handling(self):
        """Test handling of numeric conversion in validation."""
        loader = DataLoader()
        data_with_string_numbers = pd.DataFrame(
            {
                "EmployeeID": list(range(1, 21)),
                "BurnoutLevel": ["5.0"] * 20,  # String numbers
                "JobSatisfaction": [7] * 20,
                "StressLevel": [4] * 20,
            }
        )

        # Should handle string-to-numeric conversion
        loader._validate_data(data_with_string_numbers)

    def test_load_with_unicode_content(self, tmp_path):
        """Test loading files with Unicode content."""
        loader = DataLoader()

        # Create CSV with UTF-8 encoding
        utf8_data = pd.DataFrame(
            {
                "EmployeeID": list(range(1, 21)),
                "Name": ["José"] * 20,
                "BurnoutLevel": [5.0] * 20,
                "JobSatisfaction": [7.0] * 20,
                "StressLevel": [4.0] * 20,
            }
        )

        utf8_file = tmp_path / "utf8_data.csv"
        utf8_data.to_csv(utf8_file, index=False, encoding="utf-8")

        data = loader.load(str(utf8_file))
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 20


class TestMentalHealthDataSchema:
    """Test suite for MentalHealthDataSchema class."""

    def test_schema_initialization(self):
        """Test schema initialization with default values."""
        schema = MentalHealthDataSchema()

        assert len(schema.required_columns) > 0
        assert "EmployeeID" in schema.required_columns
        assert "BurnoutLevel" in schema.required_columns
        assert len(schema.optional_columns) > 0

    def test_schema_validation_empty_required_columns(self):
        """Test schema validation with empty required columns."""
        with pytest.raises(ValueError, match="Required columns cannot be empty"):
            MentalHealthDataSchema(required_columns=[])

    def test_schema_custom_required_columns(self):
        """Test schema with custom required columns."""
        custom_columns = ["ID", "Score"]
        schema = MentalHealthDataSchema(required_columns=custom_columns)
        assert schema.required_columns == custom_columns

    def test_schema_optional_columns_structure(self):
        """Test that optional columns are properly structured."""
        schema = MentalHealthDataSchema()

        assert isinstance(schema.optional_columns, list)
        assert len(schema.optional_columns) > 0

        # Check some expected optional columns
        expected_optional = ["Age", "Gender", "Department", "WorkHoursPerWeek"]
        for col in expected_optional:
            assert col in schema.optional_columns


class TestDataValidationError:
    """Test suite for DataValidationError exception."""

    def test_data_validation_error_creation(self):
        """Test DataValidationError can be created and raised."""
        error_message = "Test validation error"

        with pytest.raises(DataValidationError, match=error_message):
            raise DataValidationError(error_message)

    def test_data_validation_error_inheritance(self):
        """Test that DataValidationError inherits from Exception."""
        error = DataValidationError("test")
        assert isinstance(error, Exception)


class TestDataLoaderIntegration:
    """Integration tests for DataLoader with real scenarios."""

    def test_complete_workflow_csv(self, sample_csv_file):
        """Test complete workflow from CSV loading to info generation."""
        loader = DataLoader()

        # Load data
        data = loader.load(sample_csv_file)

        # Validate data was loaded correctly
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0

        # Get data info
        info = loader.get_data_info(data)
        assert info["total_records"] == len(data)

        # Ensure required columns are present
        required_present = any(
            col in data.columns for col in ["EmployeeID", "BurnoutLevel"]
        )
        assert required_present

    def test_error_handling_workflow(self):
        """Test error handling in complete workflow."""
        loader = DataLoader()

        # Test with nonexistent file
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent_file.csv")

        # Test with unsupported format - create a file first
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"invalid content")
            tmp_path = tmp.name

        try:
            with pytest.raises(ValueError):
                loader.load(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_data_consistency_across_formats(self, tmp_path):
        """Test data consistency when loading from different formats."""
        loader = DataLoader()

        # Create test data
        test_data = pd.DataFrame(
            {
                "EmployeeID": list(range(1, 21)),
                "BurnoutLevel": [5.0] * 20,
                "JobSatisfaction": [7.0] * 20,
                "StressLevel": [4.0] * 20,
            }
        )

        # Save same data in different formats
        csv_file = tmp_path / "test_data.csv"
        excel_file = tmp_path / "test_data.xlsx"

        test_data.to_csv(csv_file, index=False)
        test_data.to_excel(excel_file, index=False)

        # Load from both formats
        csv_data = loader.load(str(csv_file))
        excel_data = loader.load(str(excel_file))

        # Data should be equivalent
        assert len(csv_data) == len(excel_data)
        assert list(csv_data.columns) == list(excel_data.columns)


# Fixtures
@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    data = pd.DataFrame(
        {
            "EmployeeID": list(range(1, 21)),
            "BurnoutLevel": [5.0] * 20,
            "JobSatisfaction": [7.0] * 20,
            "StressLevel": [4.0] * 20,
            "Age": [30] * 20,
            "Department": ["IT"] * 20,
        }
    )

    csv_file = tmp_path / "sample_data.csv"
    data.to_csv(csv_file, index=False)
    return str(csv_file)


@pytest.fixture
def sample_mental_health_data():
    """Create sample mental health data for testing."""
    return pd.DataFrame(
        {
            "EmployeeID": list(range(1, 21)),
            "BurnoutLevel": [5.0] * 20,
            "JobSatisfaction": [7.0] * 20,
            "StressLevel": [4.0] * 20,
            "Age": [30] * 20,
            "Department": ["IT"] * 20,
            "Gender": ["Male"] * 10 + ["Female"] * 10,
        }
    )
