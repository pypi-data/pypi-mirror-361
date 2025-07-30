"""Data cleaning and preprocessing utilities."""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and preprocess mental health survey data."""

    def __init__(self, remove_outliers: bool = True, fill_missing: bool = True):
        """Initialize DataCleaner with configuration options.

        Args:
            remove_outliers: Whether to remove statistical outliers
            fill_missing: Whether to fill missing values
        """
        self.remove_outliers = remove_outliers
        self.fill_missing = fill_missing

        # Define expected data types for key columns
        self.column_types = {
            "EmployeeID": "int64",
            "Age": "float64",
            "YearsAtCompany": "float64",
            "WorkHoursPerWeek": "float64",
            "BurnoutLevel": "float64",
            "JobSatisfaction": "float64",
            "StressLevel": "float64",
            "ProductivityScore": "float64",
            "SleepHours": "float64",
            "PhysicalActivityHrs": "float64",
            "CommuteTime": "float64",
            "ManagerSupportScore": "float64",
            "MentalHealthDaysOff": "float64",
            "WorkLifeBalanceScore": "float64",
            "TeamSize": "float64",
            "CareerGrowthScore": "float64",
            "BurnoutRisk": "float64",
        }

        # Define valid ranges for numeric columns
        self.valid_ranges = {
            "Age": (16, 80),
            "YearsAtCompany": (0, 50),
            "WorkHoursPerWeek": (1, 80),
            "BurnoutLevel": (0, 10),
            "JobSatisfaction": (0, 10),
            "StressLevel": (0, 10),
            "ProductivityScore": (0, 10),
            "SleepHours": (3, 12),
            "PhysicalActivityHrs": (0, 20),
            "CommuteTime": (0, 180),
            "ManagerSupportScore": (0, 10),
            "MentalHealthDaysOff": (0, 365),
            "WorkLifeBalanceScore": (0, 10),
            "TeamSize": (1, 100),
            "CareerGrowthScore": (0, 10),
            "BurnoutRisk": (0, 1),
        }

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """Perform comprehensive data cleaning.

        Args:
            data: Raw DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        logger.info("Starting data cleaning process")

        # Create a copy to avoid modifying original data
        cleaned_data = data.copy()

        # Store cleaning statistics
        self.cleaning_stats = {
            "original_rows": len(cleaned_data),
            "original_columns": len(cleaned_data.columns),
        }

        # Step 1: Handle data types
        cleaned_data = self._fix_data_types(cleaned_data)

        # Step 2: Remove duplicate records
        cleaned_data = self._remove_duplicates(cleaned_data)

        # Step 3: Handle missing values
        if self.fill_missing:
            cleaned_data = self._handle_missing_values(cleaned_data)

        # Step 4: Remove invalid values
        cleaned_data = self._remove_invalid_values(cleaned_data)

        # Step 5: Remove outliers
        if self.remove_outliers:
            cleaned_data = self._remove_outliers(cleaned_data)

        # Step 6: Standardize categorical values
        cleaned_data = self._standardize_categorical_values(cleaned_data)

        # Step 7: Create derived features
        cleaned_data = self._create_derived_features(cleaned_data)

        # Update cleaning statistics
        self.cleaning_stats.update(
            {
                "final_rows": len(cleaned_data),
                "final_columns": len(cleaned_data.columns),
                "rows_removed": self.cleaning_stats["original_rows"]
                - len(cleaned_data),
                "data_retention_rate": (
                    len(cleaned_data) / self.cleaning_stats["original_rows"]
                    if self.cleaning_stats["original_rows"] > 0
                    else 0.0
                ),
            }
        )

        logger.info(
            f"Data cleaning complete. Retained {len(cleaned_data)}/{self.cleaning_stats['original_rows']} rows "
            f"({self.cleaning_stats['data_retention_rate']:.1%})"
        )

        return cleaned_data

    def _fix_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fix and standardize data types."""
        logger.info("Fixing data types")

        for column, expected_type in self.column_types.items():
            if column in data.columns:
                try:
                    if expected_type.startswith("float"):
                        data[column] = pd.to_numeric(data[column], errors="coerce")
                    elif expected_type.startswith("int"):
                        data[column] = pd.to_numeric(
                            data[column], errors="coerce"
                        ).astype("Int64")

                except Exception:
                    logger.warning(f"Could not convert {column} to {expected_type}")

        return data

    def _remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records."""
        logger.info("Removing duplicate records")

        initial_count = len(data)

        if "EmployeeID" in data.columns:
            # Remove duplicates based on EmployeeID, keep first occurrence
            data = data.drop_duplicates(subset=["EmployeeID"], keep="first")
        else:
            # Remove exact duplicate rows
            data = data.drop_duplicates(keep="first")

        removed_count = initial_count - len(data)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate records")

        return data

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values through imputation."""
        logger.info("Handling missing values")

        for column in data.columns:
            if data[column].isnull().any():
                if data[column].dtype in ["float64", "int64", "Int64"]:
                    # Fill numeric columns with median
                    if not data[column].dropna().empty:
                        data[column] = data[column].fillna(data[column].median())
                    else:
                        data[column] = data[column].fillna(0)
                else:
                    # Fill categorical columns with mode or 'Unknown'
                    mode_value = data[column].mode()
                    if len(mode_value) > 0:
                        data[column] = data[column].fillna(mode_value[0])
                    else:
                        data[column] = data[column].fillna("Unknown")

        return data

    def _remove_invalid_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove rows with invalid values based on defined ranges."""
        logger.info("Removing invalid values")

        initial_count = len(data)

        for column, (min_val, max_val) in self.valid_ranges.items():
            if column in data.columns:
                # Remove rows where values are outside valid range
                data = data[
                    (data[column] >= min_val) & (data[column] <= max_val)
                    | data[column].isnull()  # Keep null values for now
                ]

        removed_count = initial_count - len(data)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} rows with invalid values")

        return data

    def _remove_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove statistical outliers using IQR method."""
        logger.info("Removing statistical outliers")

        initial_count = len(data)
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for column in numeric_columns:
            if column in self.valid_ranges:  # Only apply to defined columns
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1

                # Define outlier bounds
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                # Remove outliers
                data = data[
                    (data[column] >= lower_bound) & (data[column] <= upper_bound)
                    | data[column].isnull()
                ]

        removed_count = initial_count - len(data)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} outlier records")

        return data

    def _standardize_categorical_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Standardize categorical values to consistent formats."""
        logger.info("Standardizing categorical values")

        # Gender standardization
        if "Gender" in data.columns:
            gender_mapping = {
                "m": "Male",
                "male": "Male",
                "M": "Male",
                "MALE": "Male",
                "f": "Female",
                "female": "Female",
                "F": "Female",
                "FEMALE": "Female",
                "other": "Other",
                "OTHER": "Other",
                "non-binary": "Non-binary",
                "nonbinary": "Non-binary",
                "nb": "Non-binary",
            }
            data["Gender"] = (
                data["Gender"].astype(str).map(gender_mapping).fillna(data["Gender"])
            )

        # Remote work standardization
        if "RemoteWork" in data.columns:
            remote_mapping = {
                "yes": "Yes",
                "YES": "Yes",
                "y": "Yes",
                "true": "Yes",
                "1": "Yes",
                "no": "No",
                "NO": "No",
                "n": "No",
                "false": "No",
                "0": "No",
                "hybrid": "Hybrid",
                "HYBRID": "Hybrid",
                "mixed": "Hybrid",
                "partial": "Hybrid",
            }
            data["RemoteWork"] = (
                data["RemoteWork"]
                .astype(str)
                .map(remote_mapping)
                .fillna(data["RemoteWork"])
            )

        # Mental health support standardization
        if "HasMentalHealthSupport" in data.columns:
            support_mapping = {
                "yes": "Yes",
                "YES": "Yes",
                "y": "Yes",
                "true": "Yes",
                "1": "Yes",
                "no": "No",
                "NO": "No",
                "n": "No",
                "false": "No",
                "0": "No",
            }
            data["HasMentalHealthSupport"] = (
                data["HasMentalHealthSupport"]
                .astype(str)
                .map(support_mapping)
                .fillna(data["HasMentalHealthSupport"])
            )

        return data

    def _create_derived_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create derived features from existing data."""
        logger.info("Creating derived features")

        # Age groups
        if "Age" in data.columns:
            data["AgeGroup"] = pd.cut(
                data["Age"],
                bins=[0, 30, 40, 50, 100],
                labels=["<30", "30-40", "40-50", "50+"],
                include_lowest=True,
            )

        # Experience levels
        if "YearsAtCompany" in data.columns:
            data["ExperienceLevel"] = pd.cut(
                data["YearsAtCompany"],
                bins=[0, 2, 5, 10, 100],
                labels=["Junior", "Mid-level", "Senior", "Veteran"],
                include_lowest=True,
            )

        # Work intensity
        if "WorkHoursPerWeek" in data.columns:
            data["WorkIntensity"] = pd.cut(
                data["WorkHoursPerWeek"],
                bins=[0, 35, 45, 55, 100],
                labels=["Part-time", "Standard", "High", "Extreme"],
                include_lowest=True,
            )

        # Wellbeing score (composite)
        wellbeing_columns = ["JobSatisfaction", "WorkLifeBalanceScore"]
        stress_columns = ["BurnoutLevel", "StressLevel"]

        available_positive = [col for col in wellbeing_columns if col in data.columns]
        available_negative = [col for col in stress_columns if col in data.columns]

        if available_positive or available_negative:
            wellbeing_sum = 0
            stress_sum = 0
            count = 0

            for col in available_positive:
                wellbeing_sum += data[col].fillna(5)  # Use neutral value for missing
                count += 1

            for col in available_negative:
                stress_sum += 10 - data[col].fillna(5)  # Reverse and use neutral value
                count += 1

            if count > 0:
                data["WellbeingScore"] = (wellbeing_sum + stress_sum) / count

        # Risk level categorization
        if "BurnoutLevel" in data.columns:
            data["RiskLevel"] = pd.cut(
                data["BurnoutLevel"],
                bins=[0, 4, 7, 10],
                labels=["Low", "Medium", "High"],
                include_lowest=True,
            )

        return data

    def get_cleaning_summary(self) -> dict:
        """Get summary of cleaning operations performed."""
        if not hasattr(self, "cleaning_stats"):
            return {"error": "No cleaning operations performed yet"}

        return self.cleaning_stats.copy()

    def validate_cleaned_data(self, data: pd.DataFrame) -> tuple[bool, list[str]]:
        """Validate that cleaned data meets quality standards.

        Args:
            data: Cleaned DataFrame to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check minimum size
        if len(data) < 5:
            issues.append("Dataset too small after cleaning")

        # Check for required columns
        required_cols = ["EmployeeID", "BurnoutLevel", "JobSatisfaction", "StressLevel"]
        missing_required = [col for col in required_cols if col not in data.columns]
        if missing_required:
            issues.append(f"Missing required columns: {missing_required}")

        # Check data quality
        for col in data.columns:
            if data[col].dtype in ["float64", "int64", "Int64"]:
                if data[col].isnull().sum() / len(data) > 0.5:
                    issues.append(f"Column {col} has >50% missing values")

                if data[col].nunique() <= 1:
                    issues.append(f"Column {col} has no variation")

        # Check logical consistency
        if all(col in data.columns for col in ["Age", "YearsAtCompany"]):
            impossible = (data["YearsAtCompany"] > (data["Age"] - 16)).sum()
            if impossible > 0:
                issues.append(
                    f"{impossible} records have impossible age/experience combinations"
                )

        is_valid = len(issues) == 0
        return is_valid, issues
