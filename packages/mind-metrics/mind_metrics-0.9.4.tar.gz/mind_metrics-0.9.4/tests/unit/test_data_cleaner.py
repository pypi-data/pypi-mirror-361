"""Unit tests for DataCleaner class."""

import numpy as np
import pandas as pd
import pytest

from src.data.cleaner import DataCleaner


class TestDataCleaner:
    """Test suite for DataCleaner class."""

    def test_init_default_settings(self):
        """Test DataCleaner initialization with default settings."""
        cleaner = DataCleaner()
        assert cleaner.remove_outliers is True
        assert cleaner.fill_missing is True
        assert isinstance(cleaner.column_types, dict)
        assert isinstance(cleaner.valid_ranges, dict)

    def test_init_custom_settings(self):
        """Test DataCleaner initialization with custom settings."""
        cleaner = DataCleaner(remove_outliers=False, fill_missing=False)
        assert cleaner.remove_outliers is False
        assert cleaner.fill_missing is False

    def test_clean_basic_functionality(self, sample_mental_health_data):
        """Test basic cleaning functionality."""
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean(sample_mental_health_data)

        assert isinstance(cleaned_data, pd.DataFrame)
        assert len(cleaned_data) > 0
        assert hasattr(cleaner, "cleaning_stats")
        assert "original_rows" in cleaner.cleaning_stats

    def test_fix_data_types(self, sample_mental_health_data):
        """Test data type fixing."""
        cleaner = DataCleaner()

        # Create data with wrong types
        data_with_wrong_types = sample_mental_health_data.copy()
        data_with_wrong_types["Age"] = data_with_wrong_types["Age"].astype(str)

        fixed_data = cleaner._fix_data_types(data_with_wrong_types)

        # Age should be converted back to numeric
        assert pd.api.types.is_numeric_dtype(fixed_data["Age"])

    def test_remove_duplicates_with_employee_id(self):
        """Test duplicate removal based on EmployeeID."""
        cleaner = DataCleaner()

        # Create data with duplicates
        data_with_dupes = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 2, 3],  # Duplicate ID
                "BurnoutLevel": [5.0, 6.0, 6.5, 4.0],
                "JobSatisfaction": [7.0, 8.0, 8.5, 9.0],
                "StressLevel": [4.0, 5.0, 5.5, 3.0],
            }
        )

        cleaned_data = cleaner._remove_duplicates(data_with_dupes)

        assert len(cleaned_data) == 3  # Should remove 1 duplicate
        assert cleaned_data["EmployeeID"].is_unique

    def test_remove_duplicates_without_employee_id(self):
        """Test duplicate removal without EmployeeID column."""
        cleaner = DataCleaner()

        # Create data without EmployeeID
        data_without_id = pd.DataFrame(
            {
                "BurnoutLevel": [5.0, 6.0, 5.0, 4.0],  # Exact duplicate
                "JobSatisfaction": [7.0, 8.0, 7.0, 9.0],
                "StressLevel": [4.0, 5.0, 4.0, 3.0],
            }
        )

        cleaned_data = cleaner._remove_duplicates(data_without_id)

        assert len(cleaned_data) == 3  # Should remove 1 exact duplicate

    def test_handle_missing_values_numeric(self):
        """Test missing value handling for numeric columns."""
        cleaner = DataCleaner()

        # Create data with missing values
        data_with_missing = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4],
                "BurnoutLevel": [5.0, np.nan, 7.0, 6.0],
                "Age": [25, 30, np.nan, 35],
            }
        )

        cleaned_data = cleaner._handle_missing_values(data_with_missing)

        # Missing values should be filled
        assert not cleaned_data["BurnoutLevel"].isnull().any()
        assert not cleaned_data["Age"].isnull().any()

    def test_handle_missing_values_categorical(self):
        """Test missing value handling for categorical columns."""
        cleaner = DataCleaner()

        # Create data with missing categorical values
        data_with_missing = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4],
                "Gender": ["Male", np.nan, "Female", "Male"],
                "Department": ["IT", "HR", np.nan, "IT"],
            }
        )

        cleaned_data = cleaner._handle_missing_values(data_with_missing)

        # Missing values should be filled
        assert not cleaned_data["Gender"].isnull().any()
        assert not cleaned_data["Department"].isnull().any()

    def test_remove_invalid_values(self):
        """Test removal of invalid values based on ranges."""
        cleaner = DataCleaner()

        # Create data with invalid values
        data_with_invalid = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "BurnoutLevel": [
                    5.0,
                    15.0,
                    7.0,
                    -2.0,
                    6.0,
                ],  # 15.0 and -2.0 are invalid
                "Age": [25, 30, 150, 35, 40],  # 150 is invalid
                "JobSatisfaction": [7.0, 8.0, 6.0, 5.0, 4.0],
                "StressLevel": [4.0, 5.0, 3.0, 6.0, 7.0],
            }
        )

        cleaned_data = cleaner._remove_invalid_values(data_with_invalid)

        # Should remove rows with invalid values
        assert len(cleaned_data) < len(data_with_invalid)
        assert all(cleaned_data["BurnoutLevel"] <= 10)
        assert all(cleaned_data["BurnoutLevel"] >= 0)
        assert all(cleaned_data["Age"] <= 80)

    def test_remove_outliers(self):
        """Test outlier removal using IQR method."""
        cleaner = DataCleaner()

        # Create data with clear outliers
        normal_ages = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
        outlier_ages = [100, 15]  # Clear outliers
        all_ages = normal_ages + outlier_ages

        data_with_outliers = pd.DataFrame(
            {
                "EmployeeID": range(1, len(all_ages) + 1),
                "Age": all_ages,
                "BurnoutLevel": [5.0] * len(all_ages),
                "JobSatisfaction": [7.0] * len(all_ages),
                "StressLevel": [4.0] * len(all_ages),
            }
        )

        cleaned_data = cleaner._remove_outliers(data_with_outliers)

        # Should remove outliers
        assert len(cleaned_data) < len(data_with_outliers)
        assert cleaned_data["Age"].max() < 100
        assert cleaned_data["Age"].min() > 15

    def test_standardize_categorical_values(self):
        """Test standardization of categorical values."""
        cleaner = DataCleaner()

        # Create data with inconsistent categorical values
        data_with_inconsistent = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4],
                "Gender": ["m", "Female", "MALE", "f"],
                "RemoteWork": ["yes", "No", "TRUE", "hybrid"],
                "HasMentalHealthSupport": ["y", "No", "1", "false"],
            }
        )

        cleaned_data = cleaner._standardize_categorical_values(data_with_inconsistent)

        # Values should be standardized
        assert "Male" in cleaned_data["Gender"].values
        assert "Female" in cleaned_data["Gender"].values
        assert "Yes" in cleaned_data["RemoteWork"].values
        assert "Hybrid" in cleaned_data["RemoteWork"].values

    def test_create_derived_features(self):
        """Test creation of derived features."""
        cleaner = DataCleaner()

        # Create data for feature derivation
        base_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4],
                "Age": [25, 35, 45, 55],
                "YearsAtCompany": [1, 5, 10, 20],
                "WorkHoursPerWeek": [30, 40, 50, 65],
                "BurnoutLevel": [3.0, 5.0, 7.0, 8.0],
                "StressLevel": [2.0, 4.0, 6.0, 8.0],
                "JobSatisfaction": [8.0, 7.0, 5.0, 3.0],
                "WorkLifeBalanceScore": [8.0, 6.0, 4.0, 2.0],
            }
        )

        enriched_data = cleaner._create_derived_features(base_data)

        # New features should be created
        assert "AgeGroup" in enriched_data.columns
        assert "ExperienceLevel" in enriched_data.columns
        assert "WorkIntensity" in enriched_data.columns
        assert "WellbeingScore" in enriched_data.columns
        assert "RiskLevel" in enriched_data.columns

    def test_get_cleaning_summary(self, sample_mental_health_data):
        """Test cleaning summary generation."""
        cleaner = DataCleaner()

        # Clean data first
        cleaner.clean(sample_mental_health_data)

        # Get summary
        summary = cleaner.get_cleaning_summary()

        assert isinstance(summary, dict)
        assert "original_rows" in summary
        assert "final_rows" in summary
        assert "data_retention_rate" in summary

    def test_validate_cleaned_data_valid(self, sample_mental_health_data):
        """Test validation of valid cleaned data."""
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean(sample_mental_health_data)

        is_valid, issues = cleaner.validate_cleaned_data(cleaned_data)

        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

    def test_validate_cleaned_data_invalid(self):
        """Test validation of invalid cleaned data."""
        cleaner = DataCleaner()

        # Create invalid data (too small)
        invalid_data = pd.DataFrame({"EmployeeID": [1, 2], "BurnoutLevel": [5.0, 6.0]})

        is_valid, issues = cleaner.validate_cleaned_data(invalid_data)

        assert is_valid is False
        assert len(issues) > 0
        assert any("too small" in issue for issue in issues)

    def test_clean_with_disabled_options(self, sample_mental_health_data):
        """Test cleaning with disabled options."""
        cleaner = DataCleaner(remove_outliers=False, fill_missing=False)

        # Add some missing values
        data_with_missing = sample_mental_health_data.copy()
        data_with_missing.loc[0, "Age"] = np.nan

        cleaned_data = cleaner.clean(data_with_missing)

        # Should still work but may retain missing values
        assert isinstance(cleaned_data, pd.DataFrame)

    def test_logical_consistency_validation(self):
        """Test logical consistency checks."""
        cleaner = DataCleaner()

        # Create data with logical inconsistencies
        inconsistent_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3],
                "Age": [25, 30, 35],
                "YearsAtCompany": [
                    20,
                    5,
                    3,
                ],  # 20 years at company for 25-year-old is impossible
                "BurnoutLevel": [8.0, 5.0, 3.0],
                "JobSatisfaction": [
                    8.0,
                    7.0,
                    9.0,
                ],  # High satisfaction with high burnout
                "StressLevel": [2.0, 4.0, 6.0],
                "WorkHoursPerWeek": [70, 40, 35],
                "ProductivityScore": [
                    2.0,
                    8.0,
                    9.0,
                ],  # Very low productivity with very high hours
            }
        )

        # Should detect and handle inconsistencies
        is_valid, issues = cleaner.validate_cleaned_data(inconsistent_data)

        # Note: This tests the validation method, actual cleaning may remove inconsistent records
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

    def test_cleaning_stats_tracking(self, sample_mental_health_data):
        """Test that cleaning statistics are properly tracked."""
        cleaner = DataCleaner()

        original_count = len(sample_mental_health_data)
        cleaned_data = cleaner.clean(sample_mental_health_data)

        stats = cleaner.cleaning_stats

        assert stats["original_rows"] == original_count
        assert stats["final_rows"] == len(cleaned_data)
        assert "data_retention_rate" in stats
        assert 0 <= stats["data_retention_rate"] <= 1

    def test_empty_data_handling(self):
        """Test handling of empty datasets."""
        cleaner = DataCleaner()
        empty_data = pd.DataFrame()

        # Should handle empty data gracefully
        cleaned_data = cleaner.clean(empty_data)
        assert isinstance(cleaned_data, pd.DataFrame)
        assert len(cleaned_data) == 0


class TestDataCleanerEdgeCases:
    """Test edge cases for DataCleaner."""

    def test_all_missing_column(self):
        """Test handling of columns with all missing values."""
        cleaner = DataCleaner()

        data_all_missing = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3],
                "BurnoutLevel": [5.0, 6.0, 7.0],
                "JobSatisfaction": [np.nan, np.nan, np.nan],  # All missing
                "StressLevel": [4.0, 5.0, 6.0],
            }
        )

        cleaned_data = cleaner.clean(data_all_missing)

        # Should handle gracefully
        assert isinstance(cleaned_data, pd.DataFrame)

    def test_single_row_data(self):
        """Test handling of single-row datasets."""
        cleaner = DataCleaner()

        single_row = pd.DataFrame(
            {
                "EmployeeID": [1],
                "BurnoutLevel": [5.0],
                "JobSatisfaction": [7.0],
                "StressLevel": [4.0],
            }
        )

        cleaned_data = cleaner.clean(single_row)

        # Should handle gracefully
        assert isinstance(cleaned_data, pd.DataFrame)

    def test_constant_values_detection(self):
        """Test detection of constant value columns."""
        cleaner = DataCleaner()

        constant_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "BurnoutLevel": [5.0, 5.0, 5.0, 5.0, 5.0],  # Constant
                "JobSatisfaction": [7.0, 8.0, 6.0, 9.0, 7.5],
                "StressLevel": [4.0, 4.0, 4.0, 4.0, 4.0],  # Constant
            }
        )

        # Should detect constant columns during validation
        is_valid, issues = cleaner.validate_cleaned_data(constant_data)

        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

    @pytest.mark.slow
    def test_large_dataset_performance(self):
        """Test performance with larger datasets."""
        cleaner = DataCleaner()

        # Create larger synthetic dataset
        large_data = pd.DataFrame(
            {
                "EmployeeID": range(1, 1001),
                "Age": np.random.randint(22, 65, 1000),
                "BurnoutLevel": np.random.uniform(0, 10, 1000),
                "JobSatisfaction": np.random.uniform(0, 10, 1000),
                "StressLevel": np.random.uniform(0, 10, 1000),
            }
        )

        # Should handle larger datasets efficiently
        cleaned_data = cleaner.clean(large_data)

        assert isinstance(cleaned_data, pd.DataFrame)
        assert len(cleaned_data) > 0
