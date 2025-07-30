"""Data validation utilities."""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for data validation errors."""

    pass


class DataValidator:
    """Comprehensive data validation for mental health survey data."""

    def __init__(self):
        """Initialize DataValidator with validation rules."""
        # Define validation rules for different column types
        self.numeric_ranges = {
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

        self.categorical_values = {
            "Gender": ["Male", "Female", "Other", "Non-binary"],
            "RemoteWork": ["Yes", "No", "Hybrid"],
            "HasMentalHealthSupport": ["Yes", "No"],
            "HasTherapyAccess": ["Yes", "No"],
        }

        self.required_columns = [
            "EmployeeID",
            "BurnoutLevel",
            "JobSatisfaction",
            "StressLevel",
        ]

    def validate_dataset(self, data: pd.DataFrame) -> dict:
        """Perform comprehensive dataset validation.

        Args:
            data: DataFrame to validate

        Returns:
            Dictionary containing validation results
        """
        logger.info("Starting comprehensive data validation")

        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "summary": {
                "total_records": len(data),
                "total_columns": len(data.columns),
            },
        }

        # Check basic dataset properties
        basic_checks = self._validate_basic_properties(data)
        validation_results["errors"].extend(basic_checks["errors"])
        validation_results["warnings"].extend(basic_checks["warnings"])

        # Check required columns
        column_checks = self._validate_required_columns(data)
        validation_results["errors"].extend(column_checks["errors"])
        validation_results["warnings"].extend(column_checks["warnings"])

        # Validate data types
        type_checks = self._validate_data_types(data)
        validation_results["errors"].extend(type_checks["errors"])
        validation_results["warnings"].extend(type_checks["warnings"])

        # Validate value ranges
        range_checks = self._validate_value_ranges(data)
        validation_results["errors"].extend(range_checks["errors"])
        validation_results["warnings"].extend(range_checks["warnings"])

        # Check for data quality issues
        quality_checks = self._validate_data_quality(data)
        validation_results["errors"].extend(quality_checks["errors"])
        validation_results["warnings"].extend(quality_checks["warnings"])

        # Check logical consistency
        consistency_checks = self._validate_logical_consistency(data)
        validation_results["errors"].extend(consistency_checks["errors"])
        validation_results["warnings"].extend(consistency_checks["warnings"])

        # Update overall validation status
        validation_results["is_valid"] = len(validation_results["errors"]) == 0

        # Add summary statistics
        validation_results["summary"].update(
            {
                "error_count": len(validation_results["errors"]),
                "warning_count": len(validation_results["warnings"]),
                "missing_data_percentage": (
                    float(
                        data.isnull().sum().sum()
                        / (len(data) * len(data.columns))
                        * 100
                    )
                    if len(data) > 0 and len(data.columns) > 0
                    else 0.0
                ),
                "duplicate_records": int(data.duplicated().sum()),
            }
        )

        logger.info(f"Validation complete: {validation_results['summary']}")

        return validation_results

    def _validate_basic_properties(self, data: pd.DataFrame) -> dict:
        """Validate basic dataset properties."""
        errors = []
        warnings = []

        # Check if dataset is empty
        if data.empty:
            errors.append("Dataset is empty")
            return {"errors": errors, "warnings": warnings}

        # Check minimum size requirements
        if len(data) < 10:
            errors.append(
                f"Dataset too small: {len(data)} records (minimum 10 required)"
            )
        elif len(data) < 50:
            warnings.append(
                f"Small dataset: {len(data)} records (recommended minimum 50)"
            )

        # Check for reasonable number of columns
        if len(data.columns) < 3:
            errors.append(f"Too few columns: {len(data.columns)} (minimum 3 required)")

        return {"errors": errors, "warnings": warnings}

    def _validate_required_columns(self, data: pd.DataFrame) -> dict:
        """Validate presence of required columns."""
        errors = []
        warnings = []

        # Check for required columns
        missing_required = [
            col for col in self.required_columns if col not in data.columns
        ]
        if missing_required:
            errors.append(f"Missing required columns: {missing_required}")

        # Check for recommended columns
        recommended_columns = ["Age", "Gender", "Department", "WorkHoursPerWeek"]
        missing_recommended = [
            col for col in recommended_columns if col not in data.columns
        ]
        if missing_recommended:
            warnings.append(f"Missing recommended columns: {missing_recommended}")

        return {"errors": errors, "warnings": warnings}

    def _validate_data_types(self, data: pd.DataFrame) -> dict:
        """Validate data types of columns."""
        errors = []
        warnings = []

        # Check numeric columns
        numeric_columns = [
            col for col in self.numeric_ranges.keys() if col in data.columns
        ]
        for col in numeric_columns:
            if not pd.api.types.is_numeric_dtype(data[col]):
                try:
                    # Try to convert to numeric
                    pd.to_numeric(data[col], errors="raise")
                except (ValueError, TypeError):
                    errors.append(
                        f"Column '{col}' should be numeric but contains non-numeric values"
                    )

        # Check categorical columns
        for col, valid_values in self.categorical_values.items():
            if col in data.columns:
                invalid_values = set(data[col].dropna().astype(str)) - set(
                    valid_values + ["Unknown"]
                )
                if invalid_values:
                    warnings.append(
                        f"Column '{col}' contains unexpected values: {list(invalid_values)}"
                    )

        return {"errors": errors, "warnings": warnings}

    def _validate_value_ranges(self, data: pd.DataFrame) -> dict:
        """Validate that numeric values fall within expected ranges."""
        errors = []
        warnings = []

        for col, (min_val, max_val) in self.numeric_ranges.items():
            if col in data.columns:
                series = data[col].dropna()
                if len(series) == 0:
                    continue

                # Check for values outside valid range
                out_of_range = series[(series < min_val) | (series > max_val)]
                if len(out_of_range) > 0:
                    percentage = len(out_of_range) / len(series) * 100
                    if percentage > 10:  # More than 10% out of range is an error
                        errors.append(
                            f"Column '{col}': {len(out_of_range)} values ({percentage:.1f}%) "
                            f"outside valid range [{min_val}, {max_val}]"
                        )
                    else:
                        warnings.append(
                            f"Column '{col}': {len(out_of_range)} values ({percentage:.1f}%) "
                            f"outside expected range [{min_val}, {max_val}]"
                        )

        return {"errors": errors, "warnings": warnings}

    def _validate_data_quality(self, data: pd.DataFrame) -> dict:
        """Validate overall data quality."""
        errors = []
        warnings = []

        # Check for excessive missing data
        for col in data.columns:
            missing_pct = data[col].isnull().sum() / len(data) * 100
            if missing_pct > 50:
                errors.append(f"Column '{col}' has {missing_pct:.1f}% missing data")
            elif missing_pct > 20:
                warnings.append(f"Column '{col}' has {missing_pct:.1f}% missing data")

        # Check for duplicate records
        if "EmployeeID" in data.columns:
            duplicate_ids = data["EmployeeID"].duplicated().sum()
            if duplicate_ids > 0:
                errors.append(f"Found {duplicate_ids} duplicate EmployeeIDs")

        # Check for constant columns (no variation)
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if data[col].nunique() <= 1:
                warnings.append(f"Column '{col}' has no variation (constant values)")

        # Check for suspicious patterns
        self._check_suspicious_patterns(data, warnings)

        return {"errors": errors, "warnings": warnings}

    def _validate_logical_consistency(self, data: pd.DataFrame) -> dict:
        """Validate logical consistency between related columns."""
        errors = []
        warnings = []

        # Age vs Years at Company consistency
        if all(col in data.columns for col in ["Age", "YearsAtCompany"]):
            inconsistent = data["YearsAtCompany"] > (data["Age"] - 16)
            if inconsistent.any():
                count = inconsistent.sum()
                errors.append(f"{count} records have YearsAtCompany > (Age - 16)")

        # Work hours vs productivity consistency
        if all(
            col in data.columns for col in ["WorkHoursPerWeek", "ProductivityScore"]
        ):
            # Very high work hours with very low productivity might be suspicious
            suspicious = (data["WorkHoursPerWeek"] > 60) & (
                data["ProductivityScore"] < 3
            )
            if suspicious.any():
                count = suspicious.sum()
                warnings.append(
                    f"{count} records show high work hours (>60) with very low productivity (<3)"
                )

        # Burnout vs job satisfaction consistency
        if all(col in data.columns for col in ["BurnoutLevel", "JobSatisfaction"]):
            # High burnout with high satisfaction is unusual
            unusual = (data["BurnoutLevel"] > 7) & (data["JobSatisfaction"] > 7)
            if unusual.any():
                count = unusual.sum()
                warnings.append(
                    f"{count} records show high burnout (>7) with high satisfaction (>7)"
                )

        return {"errors": errors, "warnings": warnings}

    def _check_suspicious_patterns(
        self, data: pd.DataFrame, warnings: list[str]
    ) -> None:
        """Check for suspicious data patterns."""
        # Check for too many exact values (possible data entry errors)
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if col in data.columns:
                value_counts = data[col].value_counts()
                if len(value_counts) > 0:
                    most_common_count = value_counts.iloc[0]
                    total_count = len(data[col].dropna())

                    if (
                        most_common_count / total_count > 0.5
                    ):  # More than 50% same value
                        most_common_value = value_counts.index[0]
                        warnings.append(
                            f"Column '{col}': {most_common_count}/{total_count} "
                            f"({most_common_count/total_count:.1%}) records have the same value ({most_common_value})"
                        )

        # Check for sequential patterns in IDs
        if "EmployeeID" in data.columns:
            ids = data["EmployeeID"].dropna().sort_values()
            if len(ids) > 1:
                diffs = ids.diff().dropna()
                if (diffs == 1).all():
                    warnings.append(
                        "EmployeeIDs appear to be perfectly sequential (might be synthetic data)"
                    )

    def validate_file_format(self, file_path: str) -> dict:
        """Validate file format and basic readability.

        Args:
            file_path: Path to the file to validate

        Returns:
            Dictionary containing file validation results
        """
        from pathlib import Path

        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "file_info": {},
        }

        try:
            file_path_obj = Path(file_path)

            # Check if file exists
            if not file_path_obj.exists():
                validation_results["errors"].append(f"File does not exist: {file_path}")
                validation_results["is_valid"] = False
                return validation_results

            # Check file size
            file_size = file_path_obj.stat().st_size
            validation_results["file_info"]["size_bytes"] = file_size
            validation_results["file_info"]["size_mb"] = round(
                file_size / (1024 * 1024), 2
            )

            if file_size == 0:
                validation_results["errors"].append("File is empty")
                validation_results["is_valid"] = False
                return validation_results

            if file_size > 100 * 1024 * 1024:  # 100MB
                validation_results["warnings"].append(
                    f"Large file size: {validation_results['file_info']['size_mb']} MB"
                )

            # Check file extension
            file_extension = file_path_obj.suffix.lower()
            validation_results["file_info"]["extension"] = file_extension

            supported_extensions = [".csv", ".xlsx", ".xls"]
            if file_extension not in supported_extensions:
                validation_results["errors"].append(
                    f"Unsupported file extension: {file_extension}. "
                    f"Supported: {supported_extensions}"
                )
                validation_results["is_valid"] = False

            # Try to read first few rows to validate format
            try:
                if file_extension == ".csv":
                    sample_data = pd.read_csv(file_path, nrows=5)
                elif file_extension in [".xlsx", ".xls"]:
                    sample_data = pd.read_excel(file_path, nrows=5)

                validation_results["file_info"]["columns"] = list(sample_data.columns)
                validation_results["file_info"]["sample_rows"] = len(sample_data)

            except Exception as e:
                validation_results["errors"].append(
                    f"Cannot read file format: {str(e)}"
                )
                validation_results["is_valid"] = False

        except Exception as e:
            validation_results["errors"].append(f"File validation failed: {str(e)}")
            validation_results["is_valid"] = False

        return validation_results

    def generate_validation_report(self, validation_results: dict) -> str:
        """Generate a human-readable validation report.

        Args:
            validation_results: Results from validate_dataset()

        Returns:
            Formatted validation report string
        """
        report = []
        report.append("=" * 50)
        report.append("DATA VALIDATION REPORT")
        report.append("=" * 50)

        # Summary
        summary = validation_results["summary"]
        report.append(
            f"Dataset Size: {summary['total_records']} records, {summary['total_columns']} columns"
        )
        report.append(
            f"Validation Status: {'✓ PASSED' if validation_results['is_valid'] else '✗ FAILED'}"
        )
        report.append(f"Errors: {summary['error_count']}")
        report.append(f"Warnings: {summary['warning_count']}")
        report.append(f"Missing Data: {summary['missing_data_percentage']:.1f}%")
        report.append("")

        # Errors
        if validation_results["errors"]:
            report.append("ERRORS:")
            for i, error in enumerate(validation_results["errors"], 1):
                report.append(f"  {i}. {error}")
            report.append("")

        # Warnings
        if validation_results["warnings"]:
            report.append("WARNINGS:")
            for i, warning in enumerate(validation_results["warnings"], 1):
                report.append(f"  {i}. {warning}")
            report.append("")

        # Recommendations
        report.append("RECOMMENDATIONS:")
        if validation_results["is_valid"]:
            report.append("  • Data validation passed. Proceed with analysis.")
        else:
            report.append("  • Fix all errors before proceeding with analysis.")

        if summary["warning_count"] > 0:
            report.append("  • Review warnings and consider data cleaning.")

        if summary["missing_data_percentage"] > 10:
            report.append(
                "  • High missing data percentage. Consider imputation strategies."
            )

        return "\n".join(report)
