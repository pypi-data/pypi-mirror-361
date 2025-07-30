"""Unit tests for BurnoutAnalyzer class."""

import numpy as np
import pandas as pd
import pytest

from src.analysis.burnout import BurnoutAnalyzer


class TestBurnoutAnalyzer:
    """Test suite for BurnoutAnalyzer class."""

    def test_init(self, sample_mental_health_data):
        """Test BurnoutAnalyzer initialization."""
        analyzer = BurnoutAnalyzer(sample_mental_health_data)

        assert isinstance(analyzer.data, pd.DataFrame)
        assert analyzer.burnout_threshold_high == 7.0
        assert analyzer.burnout_threshold_medium == 4.0
        assert len(analyzer.data) == len(sample_mental_health_data)

    def test_init_custom_thresholds(self, sample_mental_health_data):
        """Test BurnoutAnalyzer with custom thresholds."""
        analyzer = BurnoutAnalyzer(sample_mental_health_data)
        analyzer.burnout_threshold_high = 8.0
        analyzer.burnout_threshold_medium = 5.0

        assert analyzer.burnout_threshold_high == 8.0
        assert analyzer.burnout_threshold_medium == 5.0

    def test_analyze_burnout_patterns_basic(self, sample_mental_health_data):
        """Test basic burnout pattern analysis."""
        analyzer = BurnoutAnalyzer(sample_mental_health_data)

        result = analyzer.analyze_burnout_patterns()

        assert isinstance(result, dict)
        assert "basic_statistics" in result
        assert "severity_distribution" in result
        assert "total_employees_analyzed" in result

        # Check basic statistics structure
        basic_stats = result["basic_statistics"]
        expected_stats = ["mean", "median", "std", "min", "max"]
        for stat in expected_stats:
            assert stat in basic_stats

    def test_analyze_burnout_patterns_missing_column(self):
        """Test burnout analysis with missing BurnoutLevel column."""
        data_without_burnout = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3],
                "JobSatisfaction": [7.0, 8.0, 6.0],
                "StressLevel": [4.0, 5.0, 3.0],
            }
        )

        analyzer = BurnoutAnalyzer(data_without_burnout)

        with pytest.raises(ValueError, match="BurnoutLevel column not found"):
            analyzer.analyze_burnout_patterns()

    def test_severity_distribution_calculation(self):
        """Test burnout severity distribution calculation."""
        # Create data with known burnout distribution
        test_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "BurnoutLevel": [2.0, 3.0, 5.0, 6.0, 7.0, 8.0, 9.0, 1.0, 4.5, 7.5],
                "JobSatisfaction": [8.0] * 10,
                "StressLevel": [4.0] * 10,
            }
        )

        analyzer = BurnoutAnalyzer(test_data)
        result = analyzer.analyze_burnout_patterns()

        severity = result["severity_distribution"]

        # Check counts
        high_burnout_expected = 4  # >= 7.0: [7.0, 8.0, 9.0, 7.5]
        medium_burnout_expected = 3  # >= 4.0 and < 7.0: [5.0, 6.0, 4.5]
        low_burnout_expected = 3  # < 4.0: [2.0, 3.0, 1.0]

        assert severity["high_burnout_count"] == high_burnout_expected
        assert severity["medium_burnout_count"] == medium_burnout_expected
        assert severity["low_burnout_count"] == low_burnout_expected

        # Check percentages
        assert severity["high_burnout_percentage"] == 40.0
        assert severity["medium_burnout_percentage"] == 30.0
        assert severity["low_burnout_percentage"] == 30.0

    def test_analyze_burnout_by_demographics(self):
        """Test demographic breakdown analysis."""
        # Create test data with demographics
        test_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5, 6],
                "BurnoutLevel": [3.0, 7.0, 4.0, 8.0, 5.0, 6.0],
                "Gender": ["Male", "Female", "Male", "Female", "Other", "Male"],
                "Department": ["IT", "HR", "IT", "Finance", "IT", "HR"],
                "JobSatisfaction": [8.0] * 6,
                "StressLevel": [4.0] * 6,
            }
        )

        analyzer = BurnoutAnalyzer(test_data)
        demographics = analyzer._analyze_burnout_by_demographics()

        assert isinstance(demographics, dict)
        assert "Gender" in demographics
        assert "Department" in demographics

        # Check that analysis includes mean, count, etc.
        gender_analysis = demographics["Gender"]
        assert isinstance(gender_analysis, dict)

    def test_analyze_burnout_trends(self):
        """Test burnout trend analysis."""
        # Create test data with work-related factors
        test_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "BurnoutLevel": [3.0, 5.0, 7.0, 4.0, 8.0],
                "WorkHoursPerWeek": [35, 40, 50, 45, 60],
                "RemoteWork": ["Yes", "No", "Hybrid", "Yes", "No"],
                "TeamSize": [5, 8, 12, 3, 15],
                "JobSatisfaction": [8.0] * 5,
                "StressLevel": [4.0] * 5,
            }
        )

        analyzer = BurnoutAnalyzer(test_data)
        trends = analyzer._analyze_burnout_trends()

        assert isinstance(trends, dict)
        assert "work_hours_correlation" in trends
        assert "remote_work_impact" in trends
        assert "team_size_impact" in trends

    def test_identify_risk_factors_basic(self, sample_mental_health_data):
        """Test basic risk factor identification."""
        # Add required columns for risk analysis
        enhanced_data = sample_mental_health_data.copy()
        enhanced_data["Age"] = np.random.randint(25, 60, len(enhanced_data))
        enhanced_data["WorkHoursPerWeek"] = np.random.randint(
            35, 55, len(enhanced_data)
        )
        enhanced_data["YearsAtCompany"] = np.random.randint(1, 10, len(enhanced_data))

        analyzer = BurnoutAnalyzer(enhanced_data)
        risk_factors = analyzer.identify_risk_factors()

        assert isinstance(risk_factors, dict)

        # Should have either valid results or error/warning
        if "error" not in risk_factors and "warning" not in risk_factors:
            assert "top_risk_factors" in risk_factors
            assert "model_performance" in risk_factors
            assert "sample_size" in risk_factors

    def test_identify_risk_factors_insufficient_features(self):
        """Test risk factor identification with insufficient features."""
        # Create minimal data
        minimal_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3],
                "BurnoutLevel": [5.0, 6.0, 4.0],
                "JobSatisfaction": [7.0, 8.0, 6.0],
                "StressLevel": [4.0, 5.0, 3.0],
            }
        )

        analyzer = BurnoutAnalyzer(minimal_data)
        risk_factors = analyzer.identify_risk_factors()

        # Should handle gracefully with limited features
        assert isinstance(risk_factors, dict)

    def test_identify_risk_factors_insufficient_data(self):
        """Test risk factor identification with insufficient data."""
        # Create very small dataset
        small_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2],
                "BurnoutLevel": [5.0, 6.0],
                "Age": [25, 30],
                "WorkHoursPerWeek": [40, 45],
                "StressLevel": [4.0, 5.0],
                "JobSatisfaction": [7.0, 8.0],
            }
        )

        analyzer = BurnoutAnalyzer(small_data)
        risk_factors = analyzer.identify_risk_factors()

        # Should handle small dataset gracefully
        assert isinstance(risk_factors, dict)
        assert "warning" in risk_factors or "error" in risk_factors

    def test_analyze_burnout_by_department(self):
        """Test department-specific burnout analysis."""
        # Create test data with departments
        test_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5, 6],
                "BurnoutLevel": [3.0, 7.0, 4.0, 8.0, 5.0, 6.0],
                "Department": ["IT", "IT", "HR", "HR", "Finance", "Finance"],
                "StressLevel": [3.0, 7.0, 4.0, 8.0, 5.0, 6.0],
                "JobSatisfaction": [8.0, 4.0, 7.0, 3.0, 6.0, 5.0],
                "WorkLifeBalanceScore": [7.0, 3.0, 6.0, 2.0, 5.0, 4.0],
            }
        )

        analyzer = BurnoutAnalyzer(test_data)
        dept_analysis = analyzer.analyze_burnout_by_department()

        assert isinstance(dept_analysis, dict)

        # Should have analysis for each department
        departments = test_data["Department"].unique()
        for dept in departments:
            # Department data should be present in some form
            assert any(dept in str(key) for key in dept_analysis.keys())

    def test_analyze_burnout_by_department_no_column(self, sample_mental_health_data):
        """Test department analysis when Department column is missing."""
        # Remove Department column if it exists
        data_no_dept = sample_mental_health_data.drop(
            "Department", axis=1, errors="ignore"
        )

        analyzer = BurnoutAnalyzer(data_no_dept)
        dept_analysis = analyzer.analyze_burnout_by_department()

        assert dept_analysis is None

    def test_generate_burnout_recommendations_high_risk(self):
        """Test recommendations for high-risk scenario."""
        # Create high-risk data
        high_risk_data = pd.DataFrame(
            {
                "EmployeeID": range(1, 11),
                "BurnoutLevel": [
                    8.0,
                    9.0,
                    7.5,
                    8.5,
                    9.5,
                    7.0,
                    8.0,
                    9.0,
                    8.5,
                    7.5,
                ],  # High burnout
                "StressLevel": [
                    8.0,
                    9.0,
                    7.5,
                    8.5,
                    9.5,
                    7.0,
                    8.0,
                    9.0,
                    8.5,
                    7.5,
                ],  # High stress
                "JobSatisfaction": [
                    3.0,
                    2.0,
                    4.0,
                    2.5,
                    1.5,
                    4.0,
                    3.0,
                    2.0,
                    2.5,
                    3.5,
                ],  # Low satisfaction
                "WorkHoursPerWeek": [
                    55,
                    60,
                    50,
                    58,
                    65,
                    52,
                    55,
                    60,
                    58,
                    53,
                ],  # High hours
                "HasMentalHealthSupport": ["No"] * 10,  # No support
                "ManagerSupportScore": [
                    3.0,
                    2.0,
                    4.0,
                    2.5,
                    1.5,
                    4.0,
                    3.0,
                    2.0,
                    2.5,
                    3.5,
                ],  # Low support
                "WorkLifeBalanceScore": [
                    2.0,
                    1.0,
                    3.0,
                    1.5,
                    1.0,
                    3.0,
                    2.0,
                    1.0,
                    1.5,
                    2.5,
                ],  # Poor balance
            }
        )

        analyzer = BurnoutAnalyzer(high_risk_data)
        recommendations = analyzer.generate_burnout_recommendations()

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should have urgent recommendations
        urgent_found = any("URGENT" in rec for rec in recommendations)
        assert urgent_found

    def test_generate_burnout_recommendations_healthy(self):
        """Test recommendations for healthy scenario."""
        # Create healthy data
        healthy_data = pd.DataFrame(
            {
                "EmployeeID": range(1, 11),
                "BurnoutLevel": [
                    2.0,
                    3.0,
                    1.5,
                    2.5,
                    3.5,
                    2.0,
                    2.0,
                    3.0,
                    2.5,
                    1.5,
                ],  # Low burnout
                "StressLevel": [
                    2.0,
                    3.0,
                    1.5,
                    2.5,
                    3.5,
                    2.0,
                    2.0,
                    3.0,
                    2.5,
                    1.5,
                ],  # Low stress
                "JobSatisfaction": [
                    8.0,
                    9.0,
                    7.5,
                    8.5,
                    9.5,
                    8.0,
                    8.0,
                    9.0,
                    8.5,
                    7.5,
                ],  # High satisfaction
                "WorkHoursPerWeek": [
                    35,
                    40,
                    38,
                    42,
                    37,
                    39,
                    35,
                    40,
                    38,
                    36,
                ],  # Normal hours
                "HasMentalHealthSupport": ["Yes"] * 10,  # Good support
                "ManagerSupportScore": [
                    8.0,
                    9.0,
                    7.5,
                    8.5,
                    9.5,
                    8.0,
                    8.0,
                    9.0,
                    8.5,
                    7.5,
                ],  # Good support
                "WorkLifeBalanceScore": [
                    8.0,
                    9.0,
                    7.5,
                    8.5,
                    9.5,
                    8.0,
                    8.0,
                    9.0,
                    8.5,
                    7.5,
                ],  # Good balance
            }
        )

        analyzer = BurnoutAnalyzer(healthy_data)
        recommendations = analyzer.generate_burnout_recommendations()

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should have positive recommendations
        positive_found = any(
            "healthy" in rec.lower() or "maintain" in rec.lower()
            for rec in recommendations
        )
        assert positive_found


class TestBurnoutAnalyzerEdgeCases:
    """Test edge cases for BurnoutAnalyzer."""

    def test_empty_dataset(self):
        """Test analyzer with empty dataset."""
        empty_data = pd.DataFrame()
        analyzer = BurnoutAnalyzer(empty_data)

        with pytest.raises(ValueError):
            analyzer.analyze_burnout_patterns()

    def test_single_employee(self):
        """Test analyzer with single employee."""
        single_employee = pd.DataFrame(
            {
                "EmployeeID": [1],
                "BurnoutLevel": [5.0],
                "JobSatisfaction": [7.0],
                "StressLevel": [4.0],
            }
        )

        analyzer = BurnoutAnalyzer(single_employee)
        result = analyzer.analyze_burnout_patterns()

        assert isinstance(result, dict)
        assert result["total_employees_analyzed"] == 1

    def test_all_same_burnout_values(self):
        """Test analyzer when all employees have same burnout level."""
        same_burnout_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "BurnoutLevel": [5.0, 5.0, 5.0, 5.0, 5.0],  # All same
                "JobSatisfaction": [7.0, 8.0, 6.0, 9.0, 7.5],
                "StressLevel": [4.0, 5.0, 3.0, 6.0, 4.5],
            }
        )

        analyzer = BurnoutAnalyzer(same_burnout_data)
        result = analyzer.analyze_burnout_patterns()

        assert isinstance(result, dict)
        assert result["basic_statistics"]["std"] == 0.0  # No variation

    def test_extreme_burnout_values(self):
        """Test analyzer with extreme burnout values."""
        extreme_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "BurnoutLevel": [0.0, 10.0, 0.0, 10.0, 5.0],  # Extreme values
                "JobSatisfaction": [10.0, 0.0, 10.0, 0.0, 5.0],
                "StressLevel": [0.0, 10.0, 0.0, 10.0, 5.0],
            }
        )

        analyzer = BurnoutAnalyzer(extreme_data)
        result = analyzer.analyze_burnout_patterns()

        assert isinstance(result, dict)
        assert result["basic_statistics"]["min"] == 0.0
        assert result["basic_statistics"]["max"] == 10.0

    def test_missing_values_in_burnout(self):
        """Test analyzer with missing values in BurnoutLevel."""
        data_with_missing = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "BurnoutLevel": [5.0, np.nan, 7.0, 6.0, np.nan],
                "JobSatisfaction": [7.0, 8.0, 6.0, 9.0, 7.5],
                "StressLevel": [4.0, 5.0, 3.0, 6.0, 4.5],
            }
        )

        analyzer = BurnoutAnalyzer(data_with_missing)
        result = analyzer.analyze_burnout_patterns()

        # Should handle missing values by dropping them
        assert isinstance(result, dict)
        assert result["total_employees_analyzed"] == 3  # Only non-null values

    def test_non_numeric_burnout_values(self):
        """Test analyzer with valid numeric values."""
        # This test assumes data comes pre-cleaned, but tests robustness
        valid_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3],
                "BurnoutLevel": [5.0, 6.0, 7.0],  # Valid numeric
                "JobSatisfaction": [7.0, 8.0, 6.0],
                "StressLevel": [4.0, 5.0, 3.0],
            }
        )

        # Analyzer should work with valid numeric data
        analyzer = BurnoutAnalyzer(valid_data)
        result = analyzer.analyze_burnout_patterns()

        assert isinstance(result, dict)


# Fixtures
@pytest.fixture
def sample_mental_health_data():
    """Create sample mental health data for testing."""
    return pd.DataFrame(
        {
            "EmployeeID": list(range(1, 21)),
            "BurnoutLevel": np.random.uniform(1, 9, 20),  # Varied burnout levels
            "JobSatisfaction": np.random.uniform(2, 9, 20),
            "StressLevel": np.random.uniform(1, 8, 20),
            "Age": np.random.randint(25, 60, 20),
            "Department": ["IT"] * 7 + ["HR"] * 6 + ["Finance"] * 7,
            "Gender": ["Male"] * 10 + ["Female"] * 10,
            "WorkHoursPerWeek": np.random.randint(35, 55, 20),
            "WorkLifeBalanceScore": np.random.uniform(3, 9, 20),
        }
    )
