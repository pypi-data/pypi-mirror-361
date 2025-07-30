"""Burnout analysis and risk assessment."""

import logging
from typing import Optional

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


class BurnoutAnalyzer:
    """Analyze burnout patterns and identify risk factors."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with mental health data.

        Args:
            data: Cleaned mental health survey data
        """
        self.data = data.copy()
        self.burnout_threshold_high = 7.0
        self.burnout_threshold_medium = 4.0

    def analyze_burnout_patterns(self) -> dict:
        """Analyze overall burnout patterns in the dataset.

        Returns:
            Dictionary containing burnout analysis results
        """
        logger.info("Analyzing burnout patterns")

        if "BurnoutLevel" not in self.data.columns:
            raise ValueError("BurnoutLevel column not found in data")

        burnout_data = self.data["BurnoutLevel"].dropna()

        # Basic statistics
        basic_stats = {
            "mean": float(burnout_data.mean()),
            "median": float(burnout_data.median()),
            "std": float(burnout_data.std()),
            "min": float(burnout_data.min()),
            "max": float(burnout_data.max()),
        }

        # Burnout severity distribution
        high_burnout = (burnout_data >= self.burnout_threshold_high).sum()
        medium_burnout = (
            (burnout_data >= self.burnout_threshold_medium)
            & (burnout_data < self.burnout_threshold_high)
        ).sum()
        low_burnout = (burnout_data < self.burnout_threshold_medium).sum()

        total_employees = len(burnout_data)

        severity_distribution = {
            "high_burnout_count": int(high_burnout),
            "medium_burnout_count": int(medium_burnout),
            "low_burnout_count": int(low_burnout),
            "high_burnout_percentage": float(high_burnout / total_employees * 100),
            "medium_burnout_percentage": float(medium_burnout / total_employees * 100),
            "low_burnout_percentage": float(low_burnout / total_employees * 100),
        }

        # Demographic breakdowns
        demographic_analysis = self._analyze_burnout_by_demographics()

        # Trend analysis
        trend_analysis = self._analyze_burnout_trends()

        return {
            "basic_statistics": basic_stats,
            "severity_distribution": severity_distribution,
            "demographic_breakdown": demographic_analysis,
            "trend_analysis": trend_analysis,
            "total_employees_analyzed": int(total_employees),
        }

    def _analyze_burnout_by_demographics(self) -> dict:
        """Analyze burnout levels by demographic categories."""
        demographic_analysis = {}

        demographic_columns = [
            "Gender",
            "AgeGroup",
            "Department",
            "JobRole",
            "ExperienceLevel",
        ]

        for column in demographic_columns:
            if column in self.data.columns:
                try:
                    # Simple group statistics
                    group_stats = (
                        self.data.groupby(column)["BurnoutLevel"]
                        .agg(["mean", "median", "count", "std"])
                        .round(2)
                    )

                    # Calculate high burnout percentage for each group
                    for group in self.data[column].unique():
                        if pd.notna(group):
                            group_data = self.data[self.data[column] == group]
                            high_burnout_count = (
                                group_data["BurnoutLevel"]
                                >= self.burnout_threshold_high
                            ).sum()
                            total_count = len(group_data)
                            if total_count > 0:
                                pct = (high_burnout_count / total_count) * 100
                                group_stats.loc[group, "high_burnout_percentage"] = (
                                    round(pct, 1)
                                )

                    demographic_analysis[column] = group_stats.to_dict()
                except Exception:
                    # Skip problematic columns
                    continue

        return demographic_analysis

    def _analyze_burnout_trends(self) -> dict:
        """Analyze burnout trends and patterns."""
        trends = {}

        # Work hours vs burnout
        if "WorkHoursPerWeek" in self.data.columns:
            try:
                work_hours_corr = self.data["WorkHoursPerWeek"].corr(
                    self.data["BurnoutLevel"]
                )
                trends["work_hours_correlation"] = float(work_hours_corr)
            except Exception:
                pass

        # Remote work impact
        if "RemoteWork" in self.data.columns:
            try:
                remote_burnout = {}
                for work_type in self.data["RemoteWork"].unique():
                    if pd.notna(work_type):
                        avg_burnout = self.data[self.data["RemoteWork"] == work_type][
                            "BurnoutLevel"
                        ].mean()
                        remote_burnout[work_type] = float(avg_burnout)
                trends["remote_work_impact"] = remote_burnout
            except Exception:
                pass

        # Team size impact (simplified)
        if "TeamSize" in self.data.columns:
            try:
                # Simple correlation instead of categories
                team_corr = self.data["TeamSize"].corr(self.data["BurnoutLevel"])
                trends["team_size_impact"] = float(team_corr)  # Changed key name
            except Exception:
                pass

        return trends

    def identify_risk_factors(self) -> dict:
        """Identify key risk factors for burnout using machine learning.

        Returns:
            Dictionary containing risk factors and their importance
        """
        logger.info("Identifying burnout risk factors")

        # Prepare features for analysis
        feature_columns = [
            "Age",
            "YearsAtCompany",
            "WorkHoursPerWeek",
            "StressLevel",
            "JobSatisfaction",
            "WorkLifeBalanceScore",
            "ManagerSupportScore",
            "SleepHours",
            "PhysicalActivityHrs",
            "CommuteTime",
            "TeamSize",
        ]

        # Include categorical features
        categorical_features = [
            "Gender",
            "Department",
            "RemoteWork",
            "HasMentalHealthSupport",
        ]

        # Filter available columns
        available_numeric = [col for col in feature_columns if col in self.data.columns]
        available_categorical = [
            col for col in categorical_features if col in self.data.columns
        ]

        if len(available_numeric) < 3:
            logger.warning("Insufficient features for risk factor analysis")
            return {"error": "Insufficient features available"}

        # Prepare dataset
        analysis_data = self.data[
            available_numeric + available_categorical + ["BurnoutLevel"]
        ].copy()
        analysis_data = analysis_data.dropna()

        if len(analysis_data) < 50:
            logger.warning("Insufficient data for reliable risk factor analysis")
            return {"warning": "Insufficient data for reliable analysis"}

        # Create burnout risk categories
        analysis_data["HighBurnoutRisk"] = (
            analysis_data["BurnoutLevel"] >= self.burnout_threshold_high
        ).astype(int)

        # Encode categorical variables
        le_dict = {}
        for col in available_categorical:
            le = LabelEncoder()
            analysis_data[f"{col}_encoded"] = le.fit_transform(
                analysis_data[col].astype(str)
            )
            le_dict[col] = le

        # Prepare features and target
        feature_cols = available_numeric + [
            f"{col}_encoded" for col in available_categorical
        ]
        X = analysis_data[feature_cols]
        y = analysis_data["HighBurnoutRisk"]

        # Train random forest model
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )

            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X_train, y_train)

            # Get feature importances
            feature_importance = pd.DataFrame(
                {"feature": feature_cols, "importance": rf_model.feature_importances_}
            ).sort_values("importance", ascending=False)

            # Model performance
            train_score = rf_model.score(X_train, y_train)
            test_score = rf_model.score(X_test, y_test)

            # Decode categorical feature names
            feature_importance["feature_display"] = feature_importance["feature"].apply(
                lambda x: x.replace("_encoded", "") if x.endswith("_encoded") else x
            )

            return {
                "top_risk_factors": feature_importance.head(10).to_dict("records"),
                "model_performance": {
                    "train_accuracy": float(train_score),
                    "test_accuracy": float(test_score),
                },
                "sample_size": len(analysis_data),
                "high_risk_percentage": float(y.mean() * 100),
            }

        except Exception as e:
            logger.error(f"Error in risk factor analysis: {e}")
            return {"error": f"Risk factor analysis failed: {str(e)}"}

    def analyze_burnout_by_department(self) -> Optional[dict]:
        """Analyze burnout patterns by department.

        Returns:
            Department-wise burnout analysis or None if no department data
        """
        if "Department" not in self.data.columns:
            return None

        try:
            # Simple department analysis
            dept_analysis = {}

            for dept in self.data["Department"].unique():
                if pd.notna(dept):
                    dept_data = self.data[self.data["Department"] == dept]
                    burnout_values = dept_data["BurnoutLevel"].dropna()

                    if len(burnout_values) > 0:
                        dept_stats = {
                            "BurnoutLevel_mean": float(burnout_values.mean()),
                            "BurnoutLevel_median": float(burnout_values.median()),
                            "BurnoutLevel_std": float(burnout_values.std()),
                            "BurnoutLevel_count": int(len(burnout_values)),
                        }

                        # Add other metrics if available
                        for col in [
                            "StressLevel",
                            "JobSatisfaction",
                            "WorkLifeBalanceScore",
                        ]:
                            if col in dept_data.columns:
                                values = dept_data[col].dropna()
                                if len(values) > 0:
                                    dept_stats[f"{col}_mean"] = float(values.mean())

                        # Calculate high burnout percentage
                        high_burnout_count = (
                            burnout_values >= self.burnout_threshold_high
                        ).sum()
                        dept_stats["high_burnout_percentage"] = float(
                            (high_burnout_count / len(burnout_values)) * 100
                        )

                        dept_analysis[dept] = dept_stats

            return dept_analysis if dept_analysis else None

        except Exception:
            return None

    def generate_burnout_recommendations(self) -> list[str]:
        """Generate actionable recommendations based on burnout analysis.

        Returns:
            List of recommendations
        """
        recommendations = []

        # Analyze current state
        burnout_stats = self.analyze_burnout_patterns()
        high_burnout_pct = burnout_stats["severity_distribution"][
            "high_burnout_percentage"
        ]
        avg_burnout = burnout_stats["basic_statistics"]["mean"]

        # General recommendations based on burnout levels
        if high_burnout_pct > 20:
            recommendations.append(
                "URGENT: Over 20% of employees show high burnout levels. "
                "Implement immediate intervention programs."
            )
        elif high_burnout_pct > 10:
            recommendations.append(
                "WARNING: Elevated burnout levels detected. "
                "Consider proactive wellness initiatives."
            )

        if avg_burnout > 6:
            recommendations.append(
                "Average burnout level is concerning. "
                "Review workload distribution and support systems."
            )

        # Work hours recommendations
        if "WorkHoursPerWeek" in self.data.columns:
            avg_hours = self.data["WorkHoursPerWeek"].mean()
            if avg_hours > 45:
                recommendations.append(
                    f"Average work hours ({avg_hours:.1f}) exceed healthy levels. "
                    "Consider workload redistribution and flexible scheduling."
                )

        # Stress level recommendations
        if "StressLevel" in self.data.columns:
            avg_stress = self.data["StressLevel"].mean()
            if avg_stress > 6:
                recommendations.append(
                    "High stress levels detected. "
                    "Implement stress management programs and mindfulness training."
                )

        # Support system recommendations
        if "HasMentalHealthSupport" in self.data.columns:
            support_coverage = (self.data["HasMentalHealthSupport"] == "Yes").mean()
            if support_coverage < 0.7:
                recommendations.append(
                    f"Only {support_coverage:.1%} of employees have mental health support. "
                    "Expand mental health benefit programs."
                )

        # Manager support recommendations
        if "ManagerSupportScore" in self.data.columns:
            avg_manager_support = self.data["ManagerSupportScore"].mean()
            if avg_manager_support < 6:
                recommendations.append(
                    "Low manager support scores detected. "
                    "Invest in management training and communication skills."
                )

        # Work-life balance recommendations
        if "WorkLifeBalanceScore" in self.data.columns:
            avg_wlb = self.data["WorkLifeBalanceScore"].mean()
            if avg_wlb < 6:
                recommendations.append(
                    "Poor work-life balance reported. "
                    "Implement flexible work arrangements and respect boundaries."
                )

        if not recommendations:
            recommendations.append(
                "Mental health metrics appear healthy. "
                "Continue monitoring and maintain current support systems."
            )

        return recommendations
