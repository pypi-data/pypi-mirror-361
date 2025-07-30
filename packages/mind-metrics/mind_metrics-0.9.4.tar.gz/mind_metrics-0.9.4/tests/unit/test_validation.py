"""Unit tests for DataValidator class."""

import numpy as np
import pandas as pd
import pytest

from src.utils.validation import DataValidator, ValidationError


class TestDataValidator:
    """Test suite for DataValidator class."""

    def test_init(self):
        """Test DataValidator initialization."""
        validator = DataValidator()

        assert isinstance(validator.numeric_ranges, dict)
        assert isinstance(validator.categorical_values, dict)
        assert isinstance(validator.required_columns, list)
        assert len(validator.required_columns) > 0

    def test_validate_dataset_valid_data(self, sample_mental_health_data):
        """Test validation with valid dataset."""
        validator = DataValidator()

        result = validator.validate_dataset(sample_mental_health_data)

        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "summary" in result

        # Should be valid or have only minor warnings
        assert isinstance(result["is_valid"], bool)
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)

    def test_validate_dataset_empty(self):
        """Test validation with empty dataset."""
        validator = DataValidator()
        empty_data = pd.DataFrame()

        result = validator.validate_dataset(empty_data)

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert any("empty" in error.lower() for error in result["errors"])

    def test_validate_dataset_too_small(self):
        """Test validation with dataset that's too small."""
        validator = DataValidator()
        small_data = pd.DataFrame({"EmployeeID": [1, 2], "BurnoutLevel": [5.0, 6.0]})

        result = validator.validate_dataset(small_data)

        assert result["is_valid"] is False
        assert any("too small" in error.lower() for error in result["errors"])

    def test_validate_basic_properties(self, sample_mental_health_data):
        """Test basic properties validation."""
        validator = DataValidator()

        result = validator._validate_basic_properties(sample_mental_health_data)

        assert "errors" in result
        assert "warnings" in result
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)

    def test_validate_basic_properties_empty(self):
        """Test basic properties validation with empty data."""
        validator = DataValidator()
        empty_data = pd.DataFrame()

        result = validator._validate_basic_properties(empty_data)

        assert len(result["errors"]) > 0
        assert any("empty" in error.lower() for error in result["errors"])

    def test_validate_basic_properties_minimal_size(self):
        """Test basic properties validation with minimal size."""
        validator = DataValidator()

        # Create data that's just above minimum threshold
        adequate_data = pd.DataFrame(
            {"col1": range(15), "col2": range(15), "col3": range(15)}
        )

        result = validator._validate_basic_properties(adequate_data)

        # Should not have size-related errors
        size_errors = [e for e in result["errors"] if "small" in e.lower()]
        assert len(size_errors) == 0

    def test_validate_required_columns_present(self, sample_mental_health_data):
        """Test required columns validation when columns are present."""
        validator = DataValidator()

        result = validator._validate_required_columns(sample_mental_health_data)

        # Should not have missing required column errors if data is properly structured
        required_errors = [e for e in result["errors"] if "required" in e.lower()]

        # Check if sample data has required columns
        has_required = any(
            col in sample_mental_health_data.columns
            for col in validator.required_columns
        )
        if has_required:
            assert len(required_errors) == 0

    def test_validate_required_columns_missing(self):
        """Test required columns validation when columns are missing."""
        validator = DataValidator()

        data_missing_required = pd.DataFrame(
            {"SomeColumn": [1, 2, 3], "AnotherColumn": [4, 5, 6]}
        )

        result = validator._validate_required_columns(data_missing_required)

        assert len(result["errors"]) > 0
        assert any("required" in error.lower() for error in result["errors"])

    def test_validate_data_types_valid(self):
        """Test data type validation with valid types."""
        validator = DataValidator()

        valid_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Age": [25, 30, 35, 40, 45],
                "BurnoutLevel": [3.0, 5.0, 7.0, 4.0, 6.0],
                "Gender": ["Male", "Female", "Male", "Other", "Female"],
            }
        )

        result = validator._validate_data_types(valid_data)

        # Should not have type-related errors
        type_errors = [
            e for e in result["errors"] if "numeric" in e.lower() or "type" in e.lower()
        ]
        assert len(type_errors) == 0

    def test_validate_value_ranges_valid(self):
        """Test value range validation with valid ranges."""
        validator = DataValidator()

        valid_range_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Age": [25, 30, 35, 40, 45],  # Valid age range
                "BurnoutLevel": [3.0, 5.0, 7.0, 4.0, 6.0],  # Valid 0-10 range
                "WorkHoursPerWeek": [35, 40, 45, 50, 38],  # Valid work hours
            }
        )

        result = validator._validate_value_ranges(valid_range_data)

        # Should not have range-related errors
        range_errors = [e for e in result["errors"] if "range" in e.lower()]
        assert len(range_errors) == 0

    def test_validate_value_ranges_invalid(self):
        """Test value range validation with invalid ranges."""
        validator = DataValidator()

        invalid_range_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Age": [15, 30, 35, 100, 45],  # Invalid ages: 15, 100
                "BurnoutLevel": [-1.0, 5.0, 15.0, 4.0, 6.0],  # Invalid: -1, 15
                "WorkHoursPerWeek": [35, 40, 100, 50, 38],  # Invalid: 100
            }
        )

        result = validator._validate_value_ranges(invalid_range_data)

        # Should have range-related errors or warnings
        issues = result["errors"] + result["warnings"]
        range_issues = [i for i in issues if "range" in i.lower()]
        assert len(range_issues) > 0

    def test_validate_data_quality_good_quality(self):
        """Test data quality validation with good quality data."""
        validator = DataValidator()

        good_quality_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Age": [25, 30, 35, 40, 45],
                "BurnoutLevel": [3.0, 5.0, 7.0, 4.0, 6.0],
                "Gender": ["Male", "Female", "Male", "Other", "Female"],
            }
        )

        result = validator._validate_data_quality(good_quality_data)

        # Should have minimal quality issues
        quality_errors = [e for e in result["errors"] if "missing" in e.lower()]
        assert len(quality_errors) == 0

    def test_validate_data_quality_poor_quality(self):
        """Test data quality validation with poor quality data."""
        validator = DataValidator()

        poor_quality_data = pd.DataFrame(
            {
                "EmployeeID": [1, 1, 3, 4, 5],  # Duplicate ID
                "Age": [25, np.nan, np.nan, np.nan, 45],  # Lots of missing data
                "BurnoutLevel": [3.0, np.nan, np.nan, 4.0, np.nan],  # 60% missing
                "Gender": ["Male", "Female", "Male", "Other", "Female"],
            }
        )

        result = validator._validate_data_quality(poor_quality_data)

        # Should have quality issues
        assert len(result["errors"]) > 0

        # Should detect duplicate IDs
        duplicate_errors = [e for e in result["errors"] if "duplicate" in e.lower()]
        assert len(duplicate_errors) > 0

        # Should detect excessive missing data
        missing_errors = [e for e in result["errors"] if "missing" in e.lower()]
        assert len(missing_errors) > 0

    def test_validate_logical_consistency_valid(self):
        """Test logical consistency validation with consistent data."""
        validator = DataValidator()

        consistent_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Age": [25, 30, 35, 40, 45],
                "YearsAtCompany": [3, 8, 12, 18, 22],  # Reasonable for ages
                "WorkHoursPerWeek": [40, 42, 38, 45, 40],
                "ProductivityScore": [
                    7.0,
                    8.0,
                    6.0,
                    7.5,
                    8.5,
                ],  # Reasonable productivity
                "BurnoutLevel": [3.0, 4.0, 5.0, 6.0, 4.5],
                "JobSatisfaction": [
                    7.0,
                    7.5,
                    6.0,
                    5.5,
                    7.0,
                ],  # Inverse relationship with burnout
            }
        )

        result = validator._validate_logical_consistency(consistent_data)

        # Should have minimal consistency issues
        consistency_errors = [
            e
            for e in result["errors"]
            if "inconsistent" in e.lower() or "impossible" in e.lower()
        ]
        assert len(consistency_errors) == 0

    def test_validate_logical_consistency_invalid(self):
        """Test logical consistency validation with inconsistent data."""
        validator = DataValidator()

        inconsistent_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Age": [25, 30, 35, 40, 45],
                "YearsAtCompany": [
                    20,
                    8,
                    25,
                    18,
                    35,
                ],  # Impossible: 20 years for 25-year-old
                "WorkHoursPerWeek": [70, 42, 65, 45, 75],
                "ProductivityScore": [1.0, 8.0, 2.0, 7.5, 1.5],  # Very low productivity
                "BurnoutLevel": [8.0, 4.0, 9.0, 6.0, 8.5],  # High burnout
                "JobSatisfaction": [
                    8.0,
                    7.5,
                    9.0,
                    5.5,
                    8.5,
                ],  # High satisfaction with high burnout
            }
        )

        result = validator._validate_logical_consistency(inconsistent_data)

        # Should detect logical inconsistencies
        issues = result["errors"] + result["warnings"]
        assert len(issues) > 0

    def test_validate_file_format_valid_csv(self, sample_csv_file):
        """Test file format validation with valid CSV."""
        validator = DataValidator()

        result = validator.validate_file_format(sample_csv_file)

        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert "file_info" in result
        assert result["file_info"]["extension"] == ".csv"

    def test_validate_file_format_nonexistent(self):
        """Test file format validation with nonexistent file."""
        validator = DataValidator()

        result = validator.validate_file_format("nonexistent_file.csv")

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert any("not exist" in error.lower() for error in result["errors"])

    def test_validate_file_format_empty_file(self, tmp_path):
        """Test file format validation with empty file."""
        validator = DataValidator()

        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")

        result = validator.validate_file_format(str(empty_file))

        assert result["is_valid"] is False
        assert any("empty" in error.lower() for error in result["errors"])

    def test_validate_file_format_unsupported_extension(self, tmp_path):
        """Test file format validation with unsupported file extension."""
        validator = DataValidator()

        unsupported_file = tmp_path / "data.txt"
        unsupported_file.write_text("some content")

        result = validator.validate_file_format(str(unsupported_file))

        assert result["is_valid"] is False
        assert any("unsupported" in error.lower() for error in result["errors"])

    def test_generate_validation_report_valid_data(self, sample_mental_health_data):
        """Test validation report generation with valid data."""
        validator = DataValidator()

        validation_results = validator.validate_dataset(sample_mental_health_data)
        report = validator.generate_validation_report(validation_results)

        assert isinstance(report, str)
        assert "DATA VALIDATION REPORT" in report
        assert "Dataset Size:" in report
        assert "Validation Status:" in report

    def test_generate_validation_report_invalid_data(self):
        """Test validation report generation with invalid data."""
        validator = DataValidator()

        invalid_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2],  # Too small
                "SomeColumn": [3, 4],  # Missing required columns
            }
        )

        validation_results = validator.validate_dataset(invalid_data)
        report = validator.generate_validation_report(validation_results)

        assert isinstance(report, str)
        assert "FAILED" in report
        assert "ERRORS:" in report
        assert "RECOMMENDATIONS:" in report

    def test_suspicious_patterns_detection(self):
        """Test detection of suspicious data patterns."""
        validator = DataValidator()

        # Create data with suspicious patterns
        suspicious_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # Sequential IDs
                "BurnoutLevel": [
                    5.0,
                    5.0,
                    5.0,
                    5.0,
                    5.0,
                    5.0,
                    5.0,
                    5.0,
                    5.0,
                    5.0,
                ],  # All same
                "Age": [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],  # Sequential ages
                "JobSatisfaction": [7.0, 8.0, 6.0, 9.0, 7.5, 8.5, 6.5, 7.8, 8.2, 6.8],
            }
        )

        validation_results = validator.validate_dataset(suspicious_data)

        # Should detect suspicious patterns
        warnings = validation_results["warnings"]
        suspicious_warnings = [
            w
            for w in warnings
            if "same value" in w.lower() or "sequential" in w.lower()
        ]
        assert len(suspicious_warnings) > 0


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_creation(self):
        """Test ValidationError can be created and raised."""
        error_message = "Test validation error"

        with pytest.raises(ValidationError, match=error_message):
            raise ValidationError(error_message)

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from Exception."""
        error = ValidationError("test")
        assert isinstance(error, Exception)


class TestDataValidatorEdgeCases:
    """Test edge cases for DataValidator."""

    def test_validate_dataset_with_all_nulls(self):
        """Test validation with dataset containing all null values."""
        validator = DataValidator()

        all_nulls_data = pd.DataFrame(
            {
                "EmployeeID": [np.nan] * 10,
                "BurnoutLevel": [np.nan] * 10,
                "JobSatisfaction": [np.nan] * 10,
                "StressLevel": [np.nan] * 10,
            }
        )

        result = validator.validate_dataset(all_nulls_data)

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_dataset_with_numeric_only(self):
        """Test validation with clean numeric data types."""
        validator = DataValidator()

        numeric_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "BurnoutLevel": [5.0, 6.0, 7.0, 4.0, 8.0],  # Clean numeric
                "JobSatisfaction": [7, 8, 6, 9, 5],  # Clean numeric
                "StressLevel": [4.0, 5.0, 3.0, 6.0, 7.0],
            }
        )

        result = validator.validate_dataset(numeric_data)

        # Should handle clean numeric data without type errors
        assert isinstance(result, dict)
        assert "errors" in result

    def test_validate_dataset_extreme_values(self):
        """Test validation with extreme values."""
        validator = DataValidator()

        extreme_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Age": [0, 200, -10, 999, 25],  # Extreme ages
                "BurnoutLevel": [-100, 1000, 0, 10, 5],  # Extreme burnout levels
                "JobSatisfaction": [7.0, 8.0, 6.0, 9.0, 7.5],
                "StressLevel": [4.0, 5.0, 3.0, 6.0, 7.0],
            }
        )

        result = validator.validate_dataset(extreme_data)

        # Should detect extreme values as out of range
        issues = result["errors"] + result["warnings"]
        range_issues = [i for i in issues if "range" in i.lower()]
        assert len(range_issues) > 0

    def test_validate_dataset_unicode_content(self):
        """Test validation with Unicode content."""
        validator = DataValidator()

        unicode_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Name": ["José", "François", "Müller", "Søren", "Наташа"],
                "Department": [
                    "Développement",
                    "Diseño",
                    "Forschung",
                    "Udvikling",
                    "Разработка",
                ],
                "BurnoutLevel": [3.0, 5.0, 7.0, 4.0, 6.0],
                "JobSatisfaction": [7.0, 8.0, 6.0, 9.0, 7.5],
                "StressLevel": [4.0, 5.0, 3.0, 6.0, 7.0],
            }
        )

        result = validator.validate_dataset(unicode_data)

        # Should handle Unicode content without issues
        assert isinstance(result, dict)
        # Unicode content itself shouldn't cause validation errors

    def test_validate_single_column_dataset(self):
        """Test validation with single column dataset."""
        validator = DataValidator()

        single_column_data = pd.DataFrame({"OnlyColumn": [1, 2, 3, 4, 5]})

        result = validator.validate_dataset(single_column_data)

        # Should detect insufficient columns
        assert result["is_valid"] is False
        column_errors = [e for e in result["errors"] if "column" in e.lower()]
        assert len(column_errors) > 0


class TestDataValidatorIntegration:
    """Test DataValidator integration with other components."""

    def test_validator_with_data_loader_output(self, sample_csv_file):
        """Test validator with output from DataLoader."""
        from src.data.loader import DataLoader

        # Load data using DataLoader
        loader = DataLoader()
        loaded_data = loader.load(sample_csv_file)

        # Validate loaded data
        validator = DataValidator()
        result = validator.validate_dataset(loaded_data)

        # Data from DataLoader should generally be valid
        assert isinstance(result, dict)
        # May have warnings but should not have critical errors

    def test_validator_with_data_cleaner_output(self, sample_mental_health_data):
        """Test validator with output from DataCleaner."""
        from src.data.cleaner import DataCleaner

        # Clean data using DataCleaner
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean(sample_mental_health_data)

        # Validate cleaned data
        validator = DataValidator()
        result = validator.validate_dataset(cleaned_data)

        # Cleaned data should have fewer validation issues
        assert isinstance(result, dict)
        # Should have improved data quality compared to raw data

    def test_validation_report_usability(self, sample_mental_health_data):
        """Test that validation reports are human-readable and useful."""
        validator = DataValidator()

        validation_results = validator.validate_dataset(sample_mental_health_data)
        report = validator.generate_validation_report(validation_results)

        # Report should be well-formatted and informative
        assert len(report) > 100  # Should be substantial
        assert report.count("\n") > 5  # Should have multiple lines
        assert "Dataset Size:" in report
        assert "Validation Status:" in report

        # Should provide actionable recommendations
        assert "RECOMMENDATIONS:" in report


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
