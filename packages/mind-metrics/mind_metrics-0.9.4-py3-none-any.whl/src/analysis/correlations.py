"""Correlation analysis for mental health metrics."""

import logging

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """Analyze correlations between mental health metrics and other factors."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with mental health data.

        Args:
            data: Cleaned mental health survey data
        """
        self.data = data.copy()

        # Define key metrics for analysis
        self.key_metrics = [
            "BurnoutLevel",
            "JobSatisfaction",
            "StressLevel",
            "ProductivityScore",
            "WorkLifeBalanceScore",
            "ManagerSupportScore",
            "CareerGrowthScore",
        ]

        # Define potential factor columns
        self.factor_columns = [
            "Age",
            "YearsAtCompany",
            "WorkHoursPerWeek",
            "SleepHours",
            "PhysicalActivityHrs",
            "CommuteTime",
            "TeamSize",
            "MentalHealthDaysOff",
        ]

    def compute_correlations(self, method: str = "pearson") -> pd.DataFrame:
        """Compute correlation matrix for numeric variables.

        Args:
            method: Correlation method ("pearson" or "spearman")

        Returns:
            Correlation matrix DataFrame
        """
        logger.info(f"Computing {method} correlations")

        # Select numeric columns for correlation analysis
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns

        # Filter to available columns
        analysis_columns = [
            col
            for col in self.key_metrics + self.factor_columns
            if col in numeric_columns
        ]

        if len(analysis_columns) < 2:
            raise ValueError("Insufficient numeric columns for correlation analysis")

        # Compute correlation matrix
        correlation_data = self.data[analysis_columns]

        if method == "pearson":
            corr_matrix = correlation_data.corr(method="pearson")
        elif method == "spearman":
            corr_matrix = correlation_data.corr(method="spearman")
        else:
            raise ValueError("Method must be 'pearson' or 'spearman'")

        return corr_matrix

    def find_significant_correlations(
        self, significance_level: float = 0.05, min_correlation: float = 0.3
    ) -> list[dict]:
        """Find statistically significant correlations.

        Args:
            significance_level: P-value threshold for significance
            min_correlation: Minimum absolute correlation coefficient

        Returns:
            List of significant correlation dictionaries
        """
        logger.info("Finding significant correlations")

        significant_correlations = []

        # Get numeric columns
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        analysis_columns = [
            col
            for col in self.key_metrics + self.factor_columns
            if col in numeric_columns
        ]

        # Test all pairs
        for i, col1 in enumerate(analysis_columns):
            for col2 in analysis_columns[i + 1 :]:
                # Get valid data pairs
                data_pairs = self.data[[col1, col2]].dropna()

                if len(data_pairs) < 10:  # Need minimum sample size
                    continue

                # Compute correlation and p-value
                corr_coef, p_value = pearsonr(data_pairs[col1], data_pairs[col2])

                # Check significance and strength
                if abs(corr_coef) >= min_correlation and p_value < significance_level:
                    correlation_strength = self._interpret_correlation_strength(
                        abs(corr_coef)
                    )

                    significant_correlations.append(
                        {
                            "variable1": col1,
                            "variable2": col2,
                            "correlation_coefficient": round(corr_coef, 3),
                            "p_value": round(p_value, 4),
                            "sample_size": len(data_pairs),
                            "strength": correlation_strength,
                            "direction": "positive" if corr_coef > 0 else "negative",
                            "interpretation": self._interpret_correlation(
                                col1, col2, corr_coef
                            ),
                        }
                    )

        # Sort by absolute correlation strength
        significant_correlations.sort(
            key=lambda x: abs(x["correlation_coefficient"]), reverse=True
        )

        return significant_correlations

    def _interpret_correlation_strength(self, abs_corr: float) -> str:
        """Interpret correlation strength based on coefficient magnitude."""
        if abs_corr >= 0.8:
            return "very strong"
        elif abs_corr >= 0.6:
            return "strong"
        elif abs_corr >= 0.4:
            return "moderate"
        elif abs_corr >= 0.2:
            return "weak"
        else:
            return "very weak"

    def _interpret_correlation(self, var1: str, var2: str, corr_coef: float) -> str:
        """Generate human-readable interpretation of correlation."""
        direction = "increases" if corr_coef > 0 else "decreases"
        strength = self._interpret_correlation_strength(abs(corr_coef))

        # Create meaningful interpretations
        interpretations = {
            (
                "BurnoutLevel",
                "StressLevel",
            ): f"Higher burnout levels are {strength}ly associated with higher stress levels",
            (
                "BurnoutLevel",
                "JobSatisfaction",
            ): f"Higher burnout levels are {strength}ly associated with lower job satisfaction",
            (
                "BurnoutLevel",
                "WorkLifeBalanceScore",
            ): f"Higher burnout levels are {strength}ly associated with poorer work-life balance",
            (
                "JobSatisfaction",
                "WorkLifeBalanceScore",
            ): f"Higher job satisfaction is {strength}ly associated with better work-life balance",
            (
                "StressLevel",
                "SleepHours",
            ): f"Higher stress levels are {strength}ly associated with {'more' if corr_coef > 0 else 'fewer'} sleep hours",
            (
                "WorkHoursPerWeek",
                "StressLevel",
            ): f"Longer work hours are {strength}ly associated with higher stress levels",
            (
                "ManagerSupportScore",
                "JobSatisfaction",
            ): f"Better manager support is {strength}ly associated with higher job satisfaction",
            (
                "PhysicalActivityHrs",
                "StressLevel",
            ): f"More physical activity is {strength}ly associated with {'higher' if corr_coef > 0 else 'lower'} stress levels",
        }

        # Check for specific interpretations
        for (v1, v2), interpretation in interpretations.items():
            if (var1 == v1 and var2 == v2) or (var1 == v2 and var2 == v1):
                return interpretation

        # Generic interpretation
        return f"As {var1} {direction}, {var2} tends to {'increase' if corr_coef > 0 else 'decrease'} ({strength} correlation)"

    def analyze_burnout_correlations(self) -> dict:
        """Analyze correlations specifically with burnout levels.

        Returns:
            Dictionary containing burnout correlation analysis
        """
        if "BurnoutLevel" not in self.data.columns:
            raise ValueError("BurnoutLevel column not found in data")

        logger.info("Analyzing burnout correlations")

        # Get all numeric columns except BurnoutLevel
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        other_columns = [col for col in numeric_columns if col != "BurnoutLevel"]

        burnout_correlations = []

        for column in other_columns:
            # Get valid data pairs
            data_pairs = self.data[["BurnoutLevel", column]].dropna()

            if len(data_pairs) < 10:
                continue

            # Compute correlation
            corr_coef, p_value = pearsonr(
                data_pairs["BurnoutLevel"], data_pairs[column]
            )

            if not np.isnan(corr_coef):
                burnout_correlations.append(
                    {
                        "factor": column,
                        "correlation": round(corr_coef, 3),
                        "p_value": round(p_value, 4),
                        "sample_size": len(data_pairs),
                        "strength": self._interpret_correlation_strength(
                            abs(corr_coef)
                        ),
                        "significant": p_value < 0.05,
                    }
                )

        # Sort by absolute correlation
        burnout_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "correlations": burnout_correlations,
            "top_positive_factors": [
                c for c in burnout_correlations if c["correlation"] > 0
            ][:5],
            "top_negative_factors": [
                c for c in burnout_correlations if c["correlation"] < 0
            ][:5],
            "significant_factors": [
                c for c in burnout_correlations if c["significant"]
            ],
        }

    def analyze_satisfaction_correlations(self) -> dict:
        """Analyze correlations specifically with job satisfaction.

        Returns:
            Dictionary containing job satisfaction correlation analysis
        """
        if "JobSatisfaction" not in self.data.columns:
            raise ValueError("JobSatisfaction column not found in data")

        logger.info("Analyzing job satisfaction correlations")

        # Get all numeric columns except JobSatisfaction
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        other_columns = [col for col in numeric_columns if col != "JobSatisfaction"]

        satisfaction_correlations = []

        for column in other_columns:
            # Get valid data pairs
            data_pairs = self.data[["JobSatisfaction", column]].dropna()

            if len(data_pairs) < 10:
                continue

            # Compute correlation
            corr_coef, p_value = pearsonr(
                data_pairs["JobSatisfaction"], data_pairs[column]
            )

            if not np.isnan(corr_coef):
                satisfaction_correlations.append(
                    {
                        "factor": column,
                        "correlation": round(corr_coef, 3),
                        "p_value": round(p_value, 4),
                        "sample_size": len(data_pairs),
                        "strength": self._interpret_correlation_strength(
                            abs(corr_coef)
                        ),
                        "significant": p_value < 0.05,
                    }
                )

        # Sort by correlation (positive first)
        satisfaction_correlations.sort(key=lambda x: x["correlation"], reverse=True)

        return {
            "correlations": satisfaction_correlations,
            "top_positive_factors": [
                c for c in satisfaction_correlations if c["correlation"] > 0
            ][:5],
            "top_negative_factors": [
                c for c in satisfaction_correlations if c["correlation"] < 0
            ][:5],
            "significant_factors": [
                c for c in satisfaction_correlations if c["significant"]
            ],
        }

    def compute_partial_correlations(
        self, target_var: str, control_vars: list[str]
    ) -> dict:
        """Compute partial correlations controlling for specified variables.

        Args:
            target_var: Target variable for correlation analysis
            control_vars: Variables to control for

        Returns:
            Dictionary containing partial correlation results
        """
        logger.info(f"Computing partial correlations for {target_var}")

        if target_var not in self.data.columns:
            raise ValueError(f"{target_var} not found in data")

        # Check control variables
        available_controls = [var for var in control_vars if var in self.data.columns]

        if len(available_controls) == 0:
            logger.warning("No control variables available")
            return {"error": "No control variables available"}

        # Get numeric columns for analysis
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        analysis_vars = [
            col
            for col in numeric_columns
            if col != target_var and col not in available_controls
        ]

        partial_correlations = []

        for var in analysis_vars:
            try:
                # Prepare data
                all_vars = [target_var, var] + available_controls
                analysis_data = self.data[all_vars].dropna()

                if len(analysis_data) < 20:  # Need sufficient sample size
                    continue

                # Compute partial correlation using linear regression residuals
                from sklearn.linear_model import LinearRegression

                # Regress target_var on control variables
                X_control = analysis_data[available_controls]
                y_target = analysis_data[target_var]
                y_var = analysis_data[var]

                model_target = LinearRegression().fit(X_control, y_target)
                model_var = LinearRegression().fit(X_control, y_var)

                # Get residuals
                residuals_target = y_target - model_target.predict(X_control)
                residuals_var = y_var - model_var.predict(X_control)

                # Compute correlation of residuals
                partial_corr, p_value = pearsonr(residuals_target, residuals_var)

                partial_correlations.append(
                    {
                        "variable": var,
                        "partial_correlation": round(partial_corr, 3),
                        "p_value": round(p_value, 4),
                        "sample_size": len(analysis_data),
                        "controlled_for": available_controls,
                        "significant": p_value < 0.05,
                    }
                )

            except Exception as e:
                logger.warning(f"Could not compute partial correlation for {var}: {e}")
                continue

        # Sort by absolute correlation
        partial_correlations.sort(
            key=lambda x: abs(x["partial_correlation"]), reverse=True
        )

        return {
            "target_variable": target_var,
            "control_variables": available_controls,
            "partial_correlations": partial_correlations,
            "significant_correlations": [
                c for c in partial_correlations if c["significant"]
            ],
        }

    def analyze_correlation_networks(self) -> dict:
        """Analyze correlation networks to identify clusters of related variables.

        Returns:
            Dictionary containing network analysis results
        """
        logger.info("Analyzing correlation networks")

        # Compute correlation matrix
        corr_matrix = self.compute_correlations()

        # Find strong correlations (>0.5)
        strong_correlations = []

        for i, var1 in enumerate(corr_matrix.columns):
            for j, var2 in enumerate(corr_matrix.columns):
                if i < j:  # Avoid duplicates
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.5 and not np.isnan(corr_val):
                        strong_correlations.append(
                            {
                                "var1": var1,
                                "var2": var2,
                                "correlation": round(corr_val, 3),
                            }
                        )

        # Identify variable clusters based on correlations
        clusters = self._identify_correlation_clusters(corr_matrix)

        return {
            "strong_correlations": strong_correlations,
            "correlation_clusters": clusters,
            "network_density": len(strong_correlations)
            / (len(corr_matrix.columns) * (len(corr_matrix.columns) - 1) / 2),
        }

    def _identify_correlation_clusters(self, corr_matrix: pd.DataFrame) -> list[dict]:
        """Identify clusters of highly correlated variables."""
        try:
            from scipy.cluster.hierarchy import fcluster, linkage

            # Use absolute correlations for clustering
            abs_corr = corr_matrix.abs()

            # Convert correlation to distance
            distance_matrix = 1 - abs_corr

            # Perform hierarchical clustering
            linkage_matrix = linkage(distance_matrix, method="ward")
            cluster_labels = fcluster(linkage_matrix, t=0.5, criterion="distance")

            # Organize clusters
            clusters = []
            for cluster_id in np.unique(cluster_labels):
                cluster_vars = [
                    var
                    for i, var in enumerate(corr_matrix.columns)
                    if cluster_labels[i] == cluster_id
                ]

                if (
                    len(cluster_vars) > 1
                ):  # Only include clusters with multiple variables
                    # Calculate average within-cluster correlation
                    cluster_corrs = []
                    for i, var1 in enumerate(cluster_vars):
                        for var2 in cluster_vars[i + 1 :]:
                            cluster_corrs.append(abs(corr_matrix.loc[var1, var2]))

                    avg_correlation = np.mean(cluster_corrs) if cluster_corrs else 0

                    clusters.append(
                        {
                            "cluster_id": int(cluster_id),
                            "variables": cluster_vars,
                            "size": len(cluster_vars),
                            "avg_internal_correlation": round(avg_correlation, 3),
                        }
                    )

            return clusters

        except ImportError:
            logger.warning("Scikit-learn not available for clustering analysis")
            return []
        except Exception as e:
            logger.warning(f"Clustering analysis failed: {e}")
            return []

    def generate_correlation_insights(self) -> list[str]:
        """Generate actionable insights from correlation analysis.

        Returns:
            List of insight strings
        """
        insights = []

        try:
            # Analyze key correlations
            significant_corrs = self.find_significant_correlations(min_correlation=0.3)

            if not significant_corrs:
                insights.append(
                    "No strong correlations detected in the current dataset."
                )
                return insights

            # Insights about burnout
            burnout_analysis = self.analyze_burnout_correlations()
            top_burnout_factors = burnout_analysis.get("top_positive_factors", [])[:3]

            if top_burnout_factors:
                factors = [f["factor"] for f in top_burnout_factors]
                insights.append(
                    f"Key factors positively correlated with burnout: {', '.join(factors)}. "
                    "Focus on managing these areas to reduce burnout risk."
                )

            # Insights about job satisfaction
            satisfaction_analysis = self.analyze_satisfaction_correlations()
            top_satisfaction_factors = satisfaction_analysis.get(
                "top_positive_factors", []
            )[:3]

            if top_satisfaction_factors:
                factors = [f["factor"] for f in top_satisfaction_factors]
                insights.append(
                    f"Key factors positively correlated with job satisfaction: {', '.join(factors)}. "
                    "Improving these areas may boost overall satisfaction."
                )

            # Work-life balance insights
            wlb_correlations = [
                c
                for c in significant_corrs
                if "WorkLifeBalanceScore" in [c["variable1"], c["variable2"]]
            ]

            if wlb_correlations:
                strongest_wlb = max(
                    wlb_correlations, key=lambda x: abs(x["correlation_coefficient"])
                )
                other_var = (
                    strongest_wlb["variable1"]
                    if strongest_wlb["variable2"] == "WorkLifeBalanceScore"
                    else strongest_wlb["variable2"]
                )

                insights.append(
                    f"Work-life balance shows strongest correlation with {other_var}. "
                    f"This relationship suggests focusing on {other_var.lower()} to improve work-life balance."
                )

            # Stress level insights
            stress_correlations = [
                c
                for c in significant_corrs
                if "StressLevel" in [c["variable1"], c["variable2"]]
            ]

            high_stress_corrs = [
                c
                for c in stress_correlations
                if abs(c["correlation_coefficient"]) > 0.5
            ]

            if high_stress_corrs:
                insights.append(
                    f"Stress levels show strong correlations with {len(high_stress_corrs)} factors. "
                    "A multi-faceted approach to stress management may be most effective."
                )

        except Exception as e:
            logger.error(f"Error generating correlation insights: {e}")
            insights.append(
                "Unable to generate correlation insights due to data limitations."
            )

        return insights
