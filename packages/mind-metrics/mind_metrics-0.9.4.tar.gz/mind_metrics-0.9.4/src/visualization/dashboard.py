"""Interactive dashboard creation for mental health data."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class DashboardCreator:
    """Create interactive HTML dashboards for mental health data."""

    def __init__(self, data: pd.DataFrame):
        """Initialize DashboardCreator.

        Args:
            data: Mental health survey data
        """
        self.data = data.copy()

        # Color scheme for consistency
        self.colors = {
            "primary": "#2E86AB",
            "secondary": "#A23B72",
            "accent": "#F18F01",
            "success": "#2ECC71",
            "warning": "#F39C12",
            "danger": "#E74C3C",
            "background": "#F8F9FA",
        }

    def create_comprehensive_dashboard(self, output_path: Path) -> Optional[str]:
        """Create a comprehensive interactive dashboard.

        Args:
            output_path: Path to save the HTML dashboard

        Returns:
            Path to saved dashboard or None if creation failed
        """
        logger.info("Creating comprehensive interactive dashboard")

        try:
            # Create subplots
            fig = make_subplots(
                rows=4,
                cols=3,
                subplot_titles=[
                    "Burnout Level Distribution",
                    "Job Satisfaction vs Stress",
                    "Work-Life Balance by Department",
                    "Age Distribution",
                    "Burnout by Gender",
                    "Correlation Heatmap",
                    "Work Hours vs Burnout",
                    "Mental Health Support Impact",
                    "Manager Support vs Satisfaction",
                    "Risk Level Distribution",
                    "Trends by Experience",
                    "Key Metrics Summary",
                ],
                specs=[
                    [{"type": "histogram"}, {"type": "scatter"}, {"type": "box"}],
                    [{"type": "histogram"}, {"type": "box"}, {"type": "heatmap"}],
                    [{"type": "scatter"}, {"type": "box"}, {"type": "scatter"}],
                    [{"type": "pie"}, {"type": "scatter"}, {"type": "bar"}],
                ],
                vertical_spacing=0.08,
                horizontal_spacing=0.08,
            )

            # 1. Burnout Level Distribution
            if "BurnoutLevel" in self.data.columns:
                fig.add_trace(
                    go.Histogram(
                        x=self.data["BurnoutLevel"],
                        nbinsx=20,
                        name="Burnout Distribution",
                        marker_color=self.colors["danger"],
                        opacity=0.7,
                    ),
                    row=1,
                    col=1,
                )

            # 2. Job Satisfaction vs Stress
            if all(
                col in self.data.columns for col in ["StressLevel", "JobSatisfaction"]
            ):
                fig.add_trace(
                    go.Scatter(
                        x=self.data["StressLevel"],
                        y=self.data["JobSatisfaction"],
                        mode="markers",
                        name="Stress vs Satisfaction",
                        marker={
                            "color": self.data.get(
                                "BurnoutLevel", [5] * len(self.data)
                            ),
                            "colorscale": "Reds",
                            "size": 8,
                            "opacity": 0.6,
                        },
                        text=self.data.get("Department", [""] * len(self.data)),
                        hovertemplate="Stress: %{x}<br>Satisfaction: %{y}<br>Department: %{text}<extra></extra>",
                    ),
                    row=1,
                    col=2,
                )

            # 3. Work-Life Balance by Department
            if all(
                col in self.data.columns
                for col in ["Department", "WorkLifeBalanceScore"]
            ):
                for i, dept in enumerate(self.data["Department"].unique()):
                    dept_data = self.data[self.data["Department"] == dept][
                        "WorkLifeBalanceScore"
                    ]
                    fig.add_trace(
                        go.Box(
                            y=dept_data,
                            name=dept,
                            marker_color=px.colors.qualitative.Set3[
                                i % len(px.colors.qualitative.Set3)
                            ],
                        ),
                        row=1,
                        col=3,
                    )

            # 4. Age Distribution
            if "Age" in self.data.columns:
                fig.add_trace(
                    go.Histogram(
                        x=self.data["Age"],
                        nbinsx=15,
                        name="Age Distribution",
                        marker_color=self.colors["primary"],
                        opacity=0.7,
                    ),
                    row=2,
                    col=1,
                )

            # 5. Burnout by Gender
            if all(col in self.data.columns for col in ["Gender", "BurnoutLevel"]):
                for i, gender in enumerate(self.data["Gender"].unique()):
                    gender_data = self.data[self.data["Gender"] == gender][
                        "BurnoutLevel"
                    ]
                    fig.add_trace(
                        go.Box(
                            y=gender_data,
                            name=gender,
                            marker_color=px.colors.qualitative.Pastel[
                                i % len(px.colors.qualitative.Pastel)
                            ],
                        ),
                        row=2,
                        col=2,
                    )

            # 6. Correlation Heatmap
            numeric_cols = [
                "BurnoutLevel",
                "JobSatisfaction",
                "StressLevel",
                "WorkLifeBalanceScore",
            ]
            available_cols = [col for col in numeric_cols if col in self.data.columns]

            if len(available_cols) >= 2:
                corr_matrix = self.data[available_cols].corr()
                fig.add_trace(
                    go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale="RdBu",
                        zmid=0,
                        text=corr_matrix.round(2).values,
                        texttemplate="%{text}",
                        textfont={"size": 10},
                        hovertemplate="Correlation: %{z:.2f}<extra></extra>",
                    ),
                    row=2,
                    col=3,
                )

            # 7. Work Hours vs Burnout
            if all(
                col in self.data.columns for col in ["WorkHoursPerWeek", "BurnoutLevel"]
            ):
                fig.add_trace(
                    go.Scatter(
                        x=self.data["WorkHoursPerWeek"],
                        y=self.data["BurnoutLevel"],
                        mode="markers",
                        name="Hours vs Burnout",
                        marker={
                            "color": self.colors["warning"],
                            "size": 6,
                            "opacity": 0.6,
                        },
                        hovertemplate="Work Hours: %{x}<br>Burnout: %{y}<extra></extra>",
                    ),
                    row=3,
                    col=1,
                )

            # 8. Mental Health Support Impact
            if all(
                col in self.data.columns
                for col in ["HasMentalHealthSupport", "BurnoutLevel"]
            ):
                for support in self.data["HasMentalHealthSupport"].unique():
                    support_data = self.data[
                        self.data["HasMentalHealthSupport"] == support
                    ]["BurnoutLevel"]
                    fig.add_trace(
                        go.Box(
                            y=support_data,
                            name=f"Support: {support}",
                            marker_color=(
                                self.colors["success"]
                                if support == "Yes"
                                else self.colors["danger"]
                            ),
                        ),
                        row=3,
                        col=2,
                    )

            # 9. Manager Support vs Satisfaction
            if all(
                col in self.data.columns
                for col in ["ManagerSupportScore", "JobSatisfaction"]
            ):
                fig.add_trace(
                    go.Scatter(
                        x=self.data["ManagerSupportScore"],
                        y=self.data["JobSatisfaction"],
                        mode="markers",
                        name="Manager Support vs Satisfaction",
                        marker={
                            "color": self.colors["success"],
                            "size": 6,
                            "opacity": 0.6,
                        },
                        hovertemplate="Manager Support: %{x}<br>Job Satisfaction: %{y}<extra></extra>",
                    ),
                    row=3,
                    col=3,
                )

            # 10. Risk Level Distribution
            if "BurnoutLevel" in self.data.columns:
                # Create risk categories
                risk_labels = []
                for burnout in self.data["BurnoutLevel"]:
                    if burnout >= 7:
                        risk_labels.append("High Risk")
                    elif burnout >= 4:
                        risk_labels.append("Medium Risk")
                    else:
                        risk_labels.append("Low Risk")

                risk_counts = pd.Series(risk_labels).value_counts()
                fig.add_trace(
                    go.Pie(
                        labels=risk_counts.index,
                        values=risk_counts.values,
                        marker_colors=[
                            self.colors["success"],
                            self.colors["warning"],
                            self.colors["danger"],
                        ],
                        hovertemplate="Risk Level: %{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
                    ),
                    row=4,
                    col=1,
                )

            # 11. Trends by Experience
            if all(
                col in self.data.columns for col in ["YearsAtCompany", "BurnoutLevel"]
            ):
                fig.add_trace(
                    go.Scatter(
                        x=self.data["YearsAtCompany"],
                        y=self.data["BurnoutLevel"],
                        mode="markers",
                        name="Experience vs Burnout",
                        marker={
                            "color": self.colors["secondary"],
                            "size": 6,
                            "opacity": 0.6,
                        },
                        hovertemplate="Years at Company: %{x}<br>Burnout: %{y}<extra></extra>",
                    ),
                    row=4,
                    col=2,
                )

            # 12. Key Metrics Summary
            key_metrics = [
                "BurnoutLevel",
                "JobSatisfaction",
                "StressLevel",
                "WorkLifeBalanceScore",
            ]
            available_metrics = [col for col in key_metrics if col in self.data.columns]

            if available_metrics:
                metric_means = [self.data[col].mean() for col in available_metrics]
                fig.add_trace(
                    go.Bar(
                        x=available_metrics,
                        y=metric_means,
                        marker_color=[
                            self.colors["danger"],
                            self.colors["success"],
                            self.colors["warning"],
                            self.colors["primary"],
                        ][: len(available_metrics)],
                        text=[f"{mean:.1f}" for mean in metric_means],
                        textposition="auto",
                        hovertemplate="Metric: %{x}<br>Average: %{y:.2f}<extra></extra>",
                    ),
                    row=4,
                    col=3,
                )

            # Update layout
            fig.update_layout(
                title={
                    "text": "Mind Metrics: Comprehensive Mental Health Dashboard",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 24, "color": self.colors["primary"]},
                },
                height=1600,
                showlegend=False,
                template="plotly_white",
                font={"family": "Arial, sans-serif", "size": 12},
                plot_bgcolor=self.colors["background"],
            )

            # Update subplot titles
            fig.update_annotations(font_size=14, font_color=self.colors["primary"])

            # Save dashboard
            fig.write_html(
                str(output_path),
                include_plotlyjs=True,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
                },
            )

            logger.info(f"Dashboard saved to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return None

    def create_executive_summary_dashboard(self, output_path: Path) -> Optional[str]:
        """Create a high-level executive summary dashboard.

        Args:
            output_path: Path to save the HTML dashboard

        Returns:
            Path to saved dashboard or None if creation failed
        """
        logger.info("Creating executive summary dashboard")

        try:
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=[
                    "Overall Mental Health Status",
                    "Risk Distribution",
                    "Department Comparison",
                    "Key Performance Indicators",
                ],
                specs=[
                    [{"type": "indicator"}, {"type": "pie"}],
                    [{"type": "bar"}, {"type": "table"}],
                ],
            )

            # 1. Overall Mental Health Score (Gauge)
            if "BurnoutLevel" in self.data.columns:
                avg_burnout = self.data["BurnoutLevel"].mean()
                health_score = 10 - avg_burnout  # Invert burnout to health score

                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number+delta",
                        value=health_score,
                        domain={"x": [0, 1], "y": [0, 1]},
                        title={"text": "Overall Health Score"},
                        delta={"reference": 7},
                        gauge={
                            "axis": {"range": [None, 10]},
                            "bar": {"color": self.colors["primary"]},
                            "steps": [
                                {"range": [0, 4], "color": self.colors["danger"]},
                                {"range": [4, 7], "color": self.colors["warning"]},
                                {"range": [7, 10], "color": self.colors["success"]},
                            ],
                            "threshold": {
                                "line": {"color": "red", "width": 4},
                                "thickness": 0.75,
                                "value": 8,
                            },
                        },
                    ),
                    row=1,
                    col=1,
                )

            # 2. Risk Distribution
            if "BurnoutLevel" in self.data.columns:
                high_risk = (self.data["BurnoutLevel"] >= 7).sum()
                medium_risk = (
                    (self.data["BurnoutLevel"] >= 4) & (self.data["BurnoutLevel"] < 7)
                ).sum()
                low_risk = (self.data["BurnoutLevel"] < 4).sum()

                fig.add_trace(
                    go.Pie(
                        labels=["Low Risk", "Medium Risk", "High Risk"],
                        values=[low_risk, medium_risk, high_risk],
                        marker_colors=[
                            self.colors["success"],
                            self.colors["warning"],
                            self.colors["danger"],
                        ],
                        hole=0.4,
                    ),
                    row=1,
                    col=2,
                )

            # 3. Department Comparison
            if all(col in self.data.columns for col in ["Department", "BurnoutLevel"]):
                dept_burnout = (
                    self.data.groupby("Department")["BurnoutLevel"]
                    .mean()
                    .sort_values(ascending=True)
                )

                fig.add_trace(
                    go.Bar(
                        x=dept_burnout.values,
                        y=dept_burnout.index,
                        orientation="h",
                        marker_color=self.colors["primary"],
                        text=[f"{val:.1f}" for val in dept_burnout.values],
                        textposition="auto",
                    ),
                    row=2,
                    col=1,
                )

            # 4. KPI Table
            kpis = []
            if "BurnoutLevel" in self.data.columns:
                kpis.append(
                    [
                        "Average Burnout Level",
                        f"{self.data['BurnoutLevel'].mean():.1f}/10",
                    ]
                )
                kpis.append(
                    [
                        "High Risk Employees",
                        f"{(self.data['BurnoutLevel'] >= 7).sum()} ({(self.data['BurnoutLevel'] >= 7).mean()*100:.1f}%)",
                    ]
                )

            if "JobSatisfaction" in self.data.columns:
                kpis.append(
                    [
                        "Average Job Satisfaction",
                        f"{self.data['JobSatisfaction'].mean():.1f}/10",
                    ]
                )
                kpis.append(
                    [
                        "Low Satisfaction Employees",
                        f"{(self.data['JobSatisfaction'] <= 4).sum()} ({(self.data['JobSatisfaction'] <= 4).mean()*100:.1f}%)",
                    ]
                )

            if "HasMentalHealthSupport" in self.data.columns:
                support_pct = (
                    self.data["HasMentalHealthSupport"] == "Yes"
                ).mean() * 100
                kpis.append(["Mental Health Support Coverage", f"{support_pct:.1f}%"])

            if kpis:
                fig.add_trace(
                    go.Table(
                        header={
                            "values": ["Key Performance Indicator", "Value"],
                            "fill_color": self.colors["primary"],
                            "font": {"color": "white", "size": 14},
                        },
                        cells={
                            "values": [
                                [kpi[0] for kpi in kpis],
                                [kpi[1] for kpi in kpis],
                            ],
                            "fill_color": "white",
                            "font": {"size": 12},
                        },
                    ),
                    row=2,
                    col=2,
                )

            # Update layout
            fig.update_layout(
                title={
                    "text": "Executive Summary: Mental Health Metrics",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 20, "color": self.colors["primary"]},
                },
                height=800,
                showlegend=True,
                template="plotly_white",
            )

            # Save dashboard
            fig.write_html(str(output_path), include_plotlyjs=True)
            logger.info(f"Executive dashboard saved to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating executive dashboard: {e}")
            return None
