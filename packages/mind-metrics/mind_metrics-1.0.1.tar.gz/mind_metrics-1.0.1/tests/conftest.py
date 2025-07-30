"""Pytest configuration and fixtures for Mind Metrics tests."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_mental_health_data() -> pd.DataFrame:
    """Create sample mental health survey data for testing."""
    np.random.seed(42)  # For reproducible tests

    n_records = 100

    data = {
        "EmployeeID": range(1, n_records + 1),
        "Age": np.random.randint(22, 65, n_records),
        "Gender": np.random.choice(
            ["Male", "Female", "Other"], n_records, p=[0.4, 0.5, 0.1]
        ),
        "Department": np.random.choice(
            ["IT", "HR", "Finance", "Marketing", "Operations"],
            n_records,
            p=[0.3, 0.15, 0.2, 0.2, 0.15],
        ),
        "JobRole": np.random.choice(
            ["Junior", "Senior", "Manager", "Director"],
            n_records,
            p=[0.4, 0.3, 0.2, 0.1],
        ),
        "YearsAtCompany": np.random.randint(0, 20, n_records),
        "WorkHoursPerWeek": np.random.normal(40, 8, n_records).clip(20, 70),
        "RemoteWork": np.random.choice(
            ["Yes", "No", "Hybrid"], n_records, p=[0.3, 0.4, 0.3]
        ),
        "BurnoutLevel": np.random.beta(2, 3, n_records)
        * 10,  # Skewed towards lower values
        "JobSatisfaction": np.random.beta(3, 2, n_records)
        * 10,  # Skewed towards higher values
        "StressLevel": np.random.beta(2, 2, n_records) * 10,  # More normal distribution
        "ProductivityScore": np.random.normal(7, 1.5, n_records).clip(0, 10),
        "SleepHours": np.random.normal(7, 1, n_records).clip(4, 10),
        "PhysicalActivityHrs": np.random.exponential(2, n_records).clip(0, 15),
        "CommuteTime": np.random.gamma(2, 15, n_records).clip(0, 120),
        "HasMentalHealthSupport": np.random.choice(
            ["Yes", "No"], n_records, p=[0.6, 0.4]
        ),
        "ManagerSupportScore": np.random.normal(6, 2, n_records).clip(0, 10),
        "HasTherapyAccess": np.random.choice(["Yes", "No"], n_records, p=[0.4, 0.6]),
        "MentalHealthDaysOff": np.random.poisson(3, n_records),
        "SalaryRange": np.random.choice(
            ["<50k", "50k-75k", "75k-100k", "100k+"], n_records, p=[0.2, 0.3, 0.3, 0.2]
        ),
        "WorkLifeBalanceScore": np.random.normal(6, 2, n_records).clip(0, 10),
        "TeamSize": np.random.randint(3, 15, n_records),
        "CareerGrowthScore": np.random.normal(5, 2, n_records).clip(0, 10),
    }

    df = pd.DataFrame(data)

    # Round numeric columns to reasonable precision
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if col != "EmployeeID":
            df[col] = df[col].round(1)

    # Add some missing values for realistic testing
    missing_indices = np.random.choice(df.index, size=10, replace=False)
    df.loc[missing_indices, "PhysicalActivityHrs"] = np.nan

    missing_indices = np.random.choice(df.index, size=5, replace=False)
    df.loc[missing_indices, "ManagerSupportScore"] = np.nan

    return df


@pytest.fixture
def sample_csv_file(
    sample_mental_health_data: pd.DataFrame,
) -> Generator[str, None, None]:
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        sample_mental_health_data.to_csv(f.name, index=False)
        yield f.name

    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def sample_excel_file(
    sample_mental_health_data: pd.DataFrame,
) -> Generator[str, None, None]:
    """Create a temporary Excel file with sample data."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        sample_mental_health_data.to_excel(f.name, index=False)
        yield f.name

    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def invalid_data() -> pd.DataFrame:
    """Create invalid data for testing error handling."""
    return pd.DataFrame(
        {
            "EmployeeID": [1, 2, 3],
            "BurnoutLevel": [15, -5, "invalid"],  # Out of range and invalid type
            "JobSatisfaction": [11, 2, 8],  # Out of range
            "StressLevel": [3, 7, 9],
            "Age": [150, 10, 35],  # Unrealistic ages
        }
    )


@pytest.fixture
def minimal_valid_data() -> pd.DataFrame:
    """Create minimal valid data for testing edge cases."""
    return pd.DataFrame(
        {
            "EmployeeID": [1, 2, 3, 4, 5],
            "BurnoutLevel": [3.0, 7.5, 2.1, 8.9, 4.2],
            "JobSatisfaction": [8.0, 4.2, 9.1, 3.5, 7.8],
            "StressLevel": [4.0, 8.1, 2.5, 9.2, 5.0],
        }
    )


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_correlation_data() -> pd.DataFrame:
    """Create data with known correlations for testing."""
    np.random.seed(123)
    n = 50

    # Create correlated variables
    x1 = np.random.normal(0, 1, n)
    x2 = 0.8 * x1 + 0.6 * np.random.normal(
        0, 1, n
    )  # Strong positive correlation with x1
    x3 = -0.7 * x1 + 0.7 * np.random.normal(
        0, 1, n
    )  # Strong negative correlation with x1
    x4 = np.random.normal(0, 1, n)  # Independent

    return pd.DataFrame(
        {
            "BurnoutLevel": (x1 * 2 + 5).clip(0, 10),
            "StressLevel": (x2 * 2 + 5).clip(0, 10),
            "JobSatisfaction": (x3 * 2 + 5).clip(0, 10),
            "WorkLifeBalanceScore": (x4 * 2 + 5).clip(0, 10),
        }
    )


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Set up logging for tests."""
    import logging

    logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing


# Pytest markers for different test categories
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests that take more time")
    config.addinivalue_line("markers", "cli: CLI interface tests")
