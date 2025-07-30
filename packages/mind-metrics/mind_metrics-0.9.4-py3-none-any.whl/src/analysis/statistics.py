"""Statistical analysis and calculations for mental health data."""

import logging
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import normaltest, ttest_ind

logger = logging.getLogger(__name__)


class StatisticsCalculator:
    """Calculate comprehensive statistics for mental health survey data."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with mental health data.

        Args:
            data: Cleaned mental health survey data
        """
        self.data = data.copy()

        # Define key metrics for statistical analysis
        self.key_metrics = [
            "BurnoutLevel",
            "JobSatisfaction",
            "StressLevel",
            "ProductivityScore",
            "WorkLifeBalanceScore",
            "ManagerSupportScore",
            "CareerGrowthScore",
        ]

        # Define demographic columns
        self.demographic_columns = [
            "Age",
            "Gender",
            "Department",
            "JobRole",
            "YearsAtCompany",
            "RemoteWork",
        ]

    def calculate_basic_statistics(self) -> dict:
        """Calculate basic descriptive statistics for all numeric columns.

        Returns:
            Dictionary containing statistics for each numeric column
        """
        logger.info("Calculating basic statistics")

        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        statistics = {}

        for column in numeric_columns:
            series = self.data[column].dropna()

            if len(series) == 0:
                statistics[column] = {"error": "No valid data"}
                continue

            # Basic descriptive statistics
            stats_dict = {
                "count": int(len(series)),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
                "q25": float(series.quantile(0.25)),
                "q75": float(series.quantile(0.75)),
                "iqr": float(series.quantile(0.75) - series.quantile(0.25)),
                "skewness": float(series.skew()),
                "kurtosis": float(series.kurtosis()),
                "missing_count": int(self.data[column].isnull().sum()),
                "missing_percentage": float(
                    self.data[column].isnull().sum() / len(self.data) * 100
                ),
            }

            # Add confidence intervals for mean
            confidence_interval = self._calculate_confidence_interval(series)
            stats_dict.update(confidence_interval)

            # Add normality test
            normality_test = self._test_normality(series)
            stats_dict.update(normality_test)

            statistics[column] = stats_dict

        return statistics

    def _calculate_confidence_interval(
        self, series: pd.Series, confidence: float = 0.95
    ) -> dict:
        """Calculate confidence interval for the mean."""
        try:
            n = len(series)
            mean = series.mean()
            std_err = series.std() / np.sqrt(n)

            # Calculate t-critical value
            alpha = 1 - confidence
            t_critical = stats.t.ppf(1 - alpha / 2, df=n - 1)

            margin_error = t_critical * std_err

            return {
                "ci_lower": float(mean - margin_error),
                "ci_upper": float(mean + margin_error),
                "ci_confidence": confidence,
                "standard_error": float(std_err),
            }
        except Exception as e:
            logger.warning(f"Could not calculate confidence interval: {e}")
            return {"ci_error": str(e)}

    def _test_normality(self, series: pd.Series) -> dict:
        """Test for normality using D'Agostino-Pearson test."""
        try:
            if len(series) < 8:  # Minimum sample size for test
                return {"normality_test": "insufficient_data"}

            statistic, p_value = normaltest(series)
            is_normal = p_value > 0.05

            return {
                "normality_statistic": float(statistic),
                "normality_p_value": float(p_value),
                "is_normal": bool(is_normal),
                "normality_interpretation": "normal" if is_normal else "non-normal",
            }
        except Exception as e:
            logger.warning(f"Could not perform normality test: {e}")
            return {"normality_test": "failed"}

    def analyze_group_differences(
        self, metric: str, grouping_var: str
    ) -> Optional[dict]:
        """Analyze differences in a metric across groups.

        Args:
            metric: Numeric variable to analyze
            grouping_var: Categorical variable for grouping

        Returns:
            Dictionary containing group comparison results or None if not possible
        """
        if metric not in self.data.columns or grouping_var not in self.data.columns:
            return None

        logger.info(f"Analyzing group differences in {metric} by {grouping_var}")

        # Remove missing values
        analysis_data = self.data[[metric, grouping_var]].dropna()

        if len(analysis_data) < 10:
            return {"error": "Insufficient data for group analysis"}

        # Group statistics
        group_stats = (
            analysis_data.groupby(grouping_var)[metric]
            .agg(["count", "mean", "median", "std", "min", "max"])
            .round(3)
        )

        # Get unique groups
        groups = analysis_data[grouping_var].unique()

        # Perform statistical tests
        test_results = {}

        if len(groups) == 2:
            # Two-sample t-test
            group1_data = analysis_data[analysis_data[grouping_var] == groups[0]][
                metric
            ]
            group2_data = analysis_data[analysis_data[grouping_var] == groups[1]][
                metric
            ]

            # Check for equal variances
            levene_stat, levene_p = stats.levene(group1_data, group2_data)
            equal_var = levene_p > 0.05

            # Perform t-test
            t_stat, t_p = ttest_ind(group1_data, group2_data, equal_var=equal_var)

            test_results = {
                "test_type": "two_sample_t_test",
                "t_statistic": float(t_stat),
                "p_value": float(t_p),
                "equal_variances": bool(equal_var),
                "significant": bool(t_p < 0.05),
                "effect_size": self._calculate_cohens_d(group1_data, group2_data),
            }

        elif len(groups) > 2:
            # One-way ANOVA
            group_data = [
                analysis_data[analysis_data[grouping_var] == group][metric]
                for group in groups
            ]

            f_stat, f_p = stats.f_oneway(*group_data)

            test_results = {
                "test_type": "one_way_anova",
                "f_statistic": float(f_stat),
                "p_value": float(f_p),
                "significant": bool(f_p < 0.05),
                "eta_squared": self._calculate_eta_squared(
                    analysis_data, metric, grouping_var
                ),
            }

        return {
            "metric": metric,
            "grouping_variable": grouping_var,
            "group_statistics": group_stats.to_dict(),
            "statistical_test": test_results,
            "sample_size": len(analysis_data),
            "groups": groups.tolist(),
        }

    def _calculate_cohens_d(self, group1: pd.Series, group2: pd.Series) -> float:
        """Calculate Cohen's d effect size for two groups."""
        try:
            mean1, mean2 = group1.mean(), group2.mean()
            std1, std2 = group1.std(), group2.std()
            n1, n2 = len(group1), len(group2)

            # Pooled standard deviation
            pooled_std = np.sqrt(
                ((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)
            )

            cohens_d = (mean1 - mean2) / pooled_std
            return float(cohens_d)
        except Exception:
            return 0.0

    def _calculate_eta_squared(
        self, data: pd.DataFrame, metric: str, grouping_var: str
    ) -> float:
        """Calculate eta-squared effect size for ANOVA."""
        try:
            # Total sum of squares
            grand_mean = data[metric].mean()
            total_ss = ((data[metric] - grand_mean) ** 2).sum()

            # Between groups sum of squares
            group_means = data.groupby(grouping_var)[metric].mean()
            group_counts = data.groupby(grouping_var)[metric].count()

            between_ss = sum(group_counts * (group_means - grand_mean) ** 2)

            # Eta-squared
            eta_squared = between_ss / total_ss
            return float(eta_squared)
        except Exception:
            return 0.0

    def calculate_wellbeing_index(self) -> Optional[pd.Series]:
        """Calculate a composite wellbeing index from multiple metrics.

        Returns:
            Series containing wellbeing index values or None if insufficient data
        """
        logger.info("Calculating wellbeing index")

        # Required columns for wellbeing index
        wellbeing_components = [
            "JobSatisfaction",
            "WorkLifeBalanceScore",
        ]

        # Optional components (reverse scored)
        reverse_components = ["BurnoutLevel", "StressLevel"]

        # Check available components
        available_positive = [
            col for col in wellbeing_components if col in self.data.columns
        ]
        available_negative = [
            col for col in reverse_components if col in self.data.columns
        ]

        if len(available_positive) < 1:
            logger.warning("Insufficient components for wellbeing index")
            return None

        # Calculate index
        wellbeing_data = self.data[available_positive + available_negative].copy()

        # Normalize all components to 0-1 scale
        for col in available_positive:
            wellbeing_data[f"{col}_norm"] = wellbeing_data[col] / 10.0

        for col in available_negative:
            wellbeing_data[f"{col}_norm"] = 1.0 - (
                wellbeing_data[col] / 10.0
            )  # Reverse score

        # Calculate weighted average
        norm_columns = [
            f"{col}_norm" for col in available_positive + available_negative
        ]
        wellbeing_index = (
            wellbeing_data[norm_columns].mean(axis=1) * 10
        )  # Scale back to 0-10

        return wellbeing_index

    def analyze_trends_by_demographics(self) -> dict:
        """Analyze mental health trends across demographic groups.

        Returns:
            Dictionary containing demographic trend analysis
        """
        logger.info("Analyzing demographic trends")

        demographic_analysis = {}

        for demographic in self.demographic_columns:
            if demographic not in self.data.columns:
                continue

            demographic_trends = {}

            # Analyze each key metric by demographic
            for metric in self.key_metrics:
                if metric in self.data.columns:
                    group_analysis = self.analyze_group_differences(metric, demographic)
                    if group_analysis and "error" not in group_analysis:
                        demographic_trends[metric] = group_analysis

            if demographic_trends:
                demographic_analysis[demographic] = demographic_trends

        return demographic_analysis

    def calculate_risk_scores(self) -> Optional[pd.DataFrame]:
        """Calculate risk scores for mental health issues.

        Returns:
            DataFrame with risk scores or None if insufficient data
        """
        logger.info("Calculating mental health risk scores")

        required_columns = ["BurnoutLevel", "StressLevel"]
        if not all(col in self.data.columns for col in required_columns):
            return None

        risk_data = self.data.copy()

        # Burnout risk (0-10 scale)
        risk_data["BurnoutRisk"] = risk_data["BurnoutLevel"]

        # Stress risk (0-10 scale)
        risk_data["StressRisk"] = risk_data["StressLevel"]

        # Combined mental health risk
        risk_factors = ["BurnoutLevel", "StressLevel"]

        # Add job satisfaction (reverse scored) if available
        if "JobSatisfaction" in self.data.columns:
            risk_data["JobSatisfactionRisk"] = 10 - risk_data["JobSatisfaction"]
            risk_factors.append("JobSatisfactionRisk")

        # Add work-life balance (reverse scored) if available
        if "WorkLifeBalanceScore" in self.data.columns:
            risk_data["WorkLifeBalanceRisk"] = 10 - risk_data["WorkLifeBalanceScore"]
            risk_factors.append("WorkLifeBalanceRisk")

        # Calculate composite risk score
        risk_data["CompositeRisk"] = risk_data[risk_factors].mean(axis=1)

        # Categorize risk levels
        risk_data["RiskCategory"] = pd.cut(
            risk_data["CompositeRisk"],
            bins=[0, 3, 6, 8, 10],
            labels=["Low", "Moderate", "High", "Severe"],
            include_lowest=True,
        )

        return risk_data[
            ["BurnoutRisk", "StressRisk"]
            + [
                col
                for col in ["JobSatisfactionRisk", "WorkLifeBalanceRisk"]
                if col in risk_data.columns
            ]
            + ["CompositeRisk", "RiskCategory"]
        ]

    def generate_statistical_summary(self) -> dict:
        """Generate a comprehensive statistical summary.

        Returns:
            Dictionary containing complete statistical summary
        """
        logger.info("Generating comprehensive statistical summary")

        summary = {
            "dataset_overview": {
                "total_records": len(self.data),
                "total_variables": len(self.data.columns),
                "numeric_variables": len(
                    self.data.select_dtypes(include=[np.number]).columns
                ),
                "categorical_variables": len(
                    self.data.select_dtypes(include=["object"]).columns
                ),
            },
            "basic_statistics": self.calculate_basic_statistics(),
        }

        # Add demographic analysis
        demographic_trends = self.analyze_trends_by_demographics()
        if demographic_trends:
            summary["demographic_analysis"] = demographic_trends

        # Add wellbeing index
        wellbeing_index = self.calculate_wellbeing_index()
        if wellbeing_index is not None:
            wellbeing_stats = {
                "mean": float(wellbeing_index.mean()),
                "median": float(wellbeing_index.median()),
                "std": float(wellbeing_index.std()),
                "min": float(wellbeing_index.min()),
                "max": float(wellbeing_index.max()),
            }
            summary["wellbeing_index"] = wellbeing_stats

        # Add risk score analysis
        risk_scores = self.calculate_risk_scores()
        if risk_scores is not None:
            risk_summary = {
                "composite_risk_mean": float(risk_scores["CompositeRisk"].mean()),
                "risk_distribution": risk_scores["RiskCategory"]
                .value_counts()
                .to_dict(),
                "high_risk_percentage": float(
                    (risk_scores["RiskCategory"].isin(["High", "Severe"])).mean() * 100
                ),
            }
            summary["risk_analysis"] = risk_summary

        return summary
