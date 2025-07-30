"""Plot generation for mental health data visualization."""

import logging
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

# Set style for consistent, professional plots
plt.style.use("default")
sns.set_palette("husl")

logger = logging.getLogger(__name__)


class PlotGenerator:
    """Generate various plots for mental health data analysis."""

    def __init__(self, data: pd.DataFrame, output_dir: Path, text_only: bool = False):
        """Initialize PlotGenerator.

        Args:
            data: Mental health survey data
            output_dir: Directory to save plots
            text_only: If True, save plots to files instead of displaying
        """
        self.data = data.copy()
        self.output_dir = Path(output_dir)
        self.text_only = text_only

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up matplotlib backend for text-only mode
        if text_only:
            plt.switch_backend("Agg")

        # Color scheme
        self.colors = {
            "primary": "#2E86AB",
            "secondary": "#A23B72",
            "accent": "#F18F01",
            "success": "#C73E1D",
            "warning": "#FFB30F",
            "danger": "#FF6B6B",
        }

    def create_burnout_distribution_plot(self) -> Optional[str]:
        """Create burnout level distribution plot.

        Returns:
            Path to saved plot file or None if creation failed
        """
        if "BurnoutLevel" not in self.data.columns:
            logger.warning("BurnoutLevel column not found")
            return None

        logger.info("Creating burnout distribution plot")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Histogram
        burnout_data = self.data["BurnoutLevel"].dropna()
        ax1.hist(
            burnout_data,
            bins=20,
            alpha=0.7,
            color=self.colors["primary"],
            edgecolor="black",
        )
        ax1.axvline(
            burnout_data.mean(),
            color=self.colors["accent"],
            linestyle="--",
            label=f"Mean: {burnout_data.mean():.2f}",
        )
        ax1.axvline(
            burnout_data.median(),
            color=self.colors["secondary"],
            linestyle="--",
            label=f"Median: {burnout_data.median():.2f}",
        )
        ax1.set_xlabel("Burnout Level (0-10)")
        ax1.set_ylabel("Frequency")
        ax1.set_title("Distribution of Burnout Levels")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Box plot by demographic if available
        if "Gender" in self.data.columns:
            sns.boxplot(data=self.data, x="Gender", y="BurnoutLevel", ax=ax2)
            ax2.set_title("Burnout Levels by Gender")
        elif "Department" in self.data.columns:
            # Rotate labels if many departments
            dept_counts = self.data["Department"].nunique()
            sns.boxplot(data=self.data, x="Department", y="BurnoutLevel", ax=ax2)
            if dept_counts > 5:
                ax2.tick_params(axis="x", rotation=45)
            ax2.set_title("Burnout Levels by Department")
        else:
            # Create age group boxplot if age is available
            if "Age" in self.data.columns:
                age_groups = pd.cut(
                    self.data["Age"],
                    bins=[0, 30, 40, 50, 100],
                    labels=["<30", "30-40", "40-50", "50+"],
                )
                plot_data = pd.DataFrame(
                    {"Age Group": age_groups, "BurnoutLevel": self.data["BurnoutLevel"]}
                )
                sns.boxplot(data=plot_data, x="Age Group", y="BurnoutLevel", ax=ax2)
                ax2.set_title("Burnout Levels by Age Group")

        plt.tight_layout()

        return self._save_or_show_plot(fig, "burnout_distribution.png")

    def create_correlation_heatmap(
        self, correlation_matrix: pd.DataFrame
    ) -> Optional[str]:
        """Create correlation heatmap.

        Args:
            correlation_matrix: Correlation matrix to visualize

        Returns:
            Path to saved plot file or None if creation failed
        """
        logger.info("Creating correlation heatmap")

        fig, ax = plt.subplots(figsize=(12, 10))

        # Create mask for upper triangle
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

        # Generate heatmap
        sns.heatmap(
            correlation_matrix,
            mask=mask,
            annot=True,
            cmap="RdBu_r",
            center=0,
            square=True,
            fmt=".2f",
            cbar_kws={"shrink": 0.8},
            ax=ax,
        )

        ax.set_title("Correlation Matrix of Mental Health Metrics", fontsize=16, pad=20)
        plt.tight_layout()

        return self._save_or_show_plot(fig, "correlation_heatmap.png")

    def create_stress_vs_satisfaction_plot(self) -> Optional[str]:
        """Create scatter plot of stress vs job satisfaction.

        Returns:
            Path to saved plot file or None if creation failed
        """
        required_columns = ["StressLevel", "JobSatisfaction"]
        if not all(col in self.data.columns for col in required_columns):
            logger.warning("Required columns not found for stress vs satisfaction plot")
            return None

        logger.info("Creating stress vs satisfaction plot")

        fig, ax = plt.subplots(figsize=(10, 8))

        # Create scatter plot with color coding by burnout level if available
        if "BurnoutLevel" in self.data.columns:
            scatter = ax.scatter(
                self.data["StressLevel"],
                self.data["JobSatisfaction"],
                c=self.data["BurnoutLevel"],
                cmap="Reds",
                alpha=0.6,
                s=50,
            )
            plt.colorbar(scatter, label="Burnout Level")
        else:
            ax.scatter(
                self.data["StressLevel"],
                self.data["JobSatisfaction"],
                alpha=0.6,
                color=self.colors["primary"],
            )

        # Add trend line
        z = np.polyfit(
            self.data["StressLevel"].dropna(), self.data["JobSatisfaction"].dropna(), 1
        )
        p = np.poly1d(z)
        ax.plot(
            self.data["StressLevel"],
            p(self.data["StressLevel"]),
            "--",
            alpha=0.8,
            color=self.colors["accent"],
        )

        ax.set_xlabel("Stress Level (0-10)")
        ax.set_ylabel("Job Satisfaction (0-10)")
        ax.set_title("Relationship between Stress Level and Job Satisfaction")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        return self._save_or_show_plot(fig, "stress_vs_satisfaction.png")

    def create_work_life_balance_analysis(self) -> Optional[str]:
        """Create work-life balance analysis visualization.

        Returns:
            Path to saved plot file or None if creation failed
        """
        logger.info("Creating work-life balance analysis")

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Work-life balance distribution
        if "WorkLifeBalanceScore" in self.data.columns:
            wlb_data = self.data["WorkLifeBalanceScore"].dropna()
            axes[0, 0].hist(wlb_data, bins=15, alpha=0.7, color=self.colors["primary"])
            axes[0, 0].axvline(
                wlb_data.mean(),
                color=self.colors["accent"],
                linestyle="--",
                label=f"Mean: {wlb_data.mean():.2f}",
            )
            axes[0, 0].set_title("Work-Life Balance Score Distribution")
            axes[0, 0].set_xlabel("Work-Life Balance Score (0-10)")
            axes[0, 0].set_ylabel("Frequency")
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Work hours vs work-life balance
        if all(
            col in self.data.columns
            for col in ["WorkHoursPerWeek", "WorkLifeBalanceScore"]
        ):
            axes[0, 1].scatter(
                self.data["WorkHoursPerWeek"],
                self.data["WorkLifeBalanceScore"],
                alpha=0.6,
                color=self.colors["secondary"],
            )
            axes[0, 1].set_title("Work Hours vs Work-Life Balance")
            axes[0, 1].set_xlabel("Work Hours per Week")
            axes[0, 1].set_ylabel("Work-Life Balance Score")
            axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Remote work impact on work-life balance
        if all(
            col in self.data.columns for col in ["RemoteWork", "WorkLifeBalanceScore"]
        ):
            sns.boxplot(
                data=self.data, x="RemoteWork", y="WorkLifeBalanceScore", ax=axes[1, 0]
            )
            axes[1, 0].set_title("Work-Life Balance by Remote Work Status")

        # Plot 4: Work-life balance by department (if available)
        if all(
            col in self.data.columns for col in ["Department", "WorkLifeBalanceScore"]
        ):
            dept_wlb = (
                self.data.groupby("Department")["WorkLifeBalanceScore"]
                .mean()
                .sort_values()
            )
            axes[1, 1].barh(
                range(len(dept_wlb)), dept_wlb.values, color=self.colors["primary"]
            )
            axes[1, 1].set_yticks(range(len(dept_wlb)))
            axes[1, 1].set_yticklabels(dept_wlb.index)
            axes[1, 1].set_title("Average Work-Life Balance by Department")
            axes[1, 1].set_xlabel("Average Work-Life Balance Score")

        plt.tight_layout()

        return self._save_or_show_plot(fig, "work_life_balance_analysis.png")

    def create_demographic_analysis(self) -> Optional[str]:
        """Create demographic breakdown analysis.

        Returns:
            Path to saved plot file or None if creation failed
        """
        logger.info("Creating demographic analysis")

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Age distribution
        if "Age" in self.data.columns:
            age_data = self.data["Age"].dropna()
            axes[0, 0].hist(age_data, bins=15, alpha=0.7, color=self.colors["primary"])
            axes[0, 0].set_title("Age Distribution")
            axes[0, 0].set_xlabel("Age")
            axes[0, 0].set_ylabel("Frequency")
            axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Gender distribution
        if "Gender" in self.data.columns:
            gender_counts = self.data["Gender"].value_counts()
            axes[0, 1].pie(
                gender_counts.values,
                labels=gender_counts.index,
                autopct="%1.1f%%",
                colors=[
                    self.colors["primary"],
                    self.colors["secondary"],
                    self.colors["accent"],
                ],
            )
            axes[0, 1].set_title("Gender Distribution")

        # Plot 3: Years at company distribution
        if "YearsAtCompany" in self.data.columns:
            years_data = self.data["YearsAtCompany"].dropna()
            axes[1, 0].hist(
                years_data, bins=15, alpha=0.7, color=self.colors["secondary"]
            )
            axes[1, 0].set_title("Years at Company Distribution")
            axes[1, 0].set_xlabel("Years at Company")
            axes[1, 0].set_ylabel("Frequency")
            axes[1, 0].grid(True, alpha=0.3)

        # Plot 4: Department distribution
        if "Department" in self.data.columns:
            dept_counts = (
                self.data["Department"].value_counts().head(10)
            )  # Top 10 departments
            axes[1, 1].barh(
                range(len(dept_counts)), dept_counts.values, color=self.colors["accent"]
            )
            axes[1, 1].set_yticks(range(len(dept_counts)))
            axes[1, 1].set_yticklabels(dept_counts.index)
            axes[1, 1].set_title("Employee Distribution by Department (Top 10)")
            axes[1, 1].set_xlabel("Number of Employees")

        plt.tight_layout()

        return self._save_or_show_plot(fig, "demographic_analysis.png")

    def create_mental_health_dashboard(self) -> Optional[str]:
        """Create comprehensive mental health dashboard.

        Returns:
            Path to saved plot file or None if creation failed
        """
        logger.info("Creating mental health dashboard")

        fig = plt.figure(figsize=(20, 16))

        # Create a grid layout
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)

        # Key metrics overview (top row)
        if "BurnoutLevel" in self.data.columns:
            ax1 = fig.add_subplot(gs[0, 0])
            self._create_metric_gauge(
                ax1,
                self.data["BurnoutLevel"].mean(),
                "Avg Burnout Level",
                0,
                10,
                self.colors["danger"],
            )

        if "JobSatisfaction" in self.data.columns:
            ax2 = fig.add_subplot(gs[0, 1])
            self._create_metric_gauge(
                ax2,
                self.data["JobSatisfaction"].mean(),
                "Avg Job Satisfaction",
                0,
                10,
                self.colors["success"],
            )

        if "StressLevel" in self.data.columns:
            ax3 = fig.add_subplot(gs[0, 2])
            self._create_metric_gauge(
                ax3,
                self.data["StressLevel"].mean(),
                "Avg Stress Level",
                0,
                10,
                self.colors["warning"],
            )

        if "WorkLifeBalanceScore" in self.data.columns:
            ax4 = fig.add_subplot(gs[0, 3])
            self._create_metric_gauge(
                ax4,
                self.data["WorkLifeBalanceScore"].mean(),
                "Avg Work-Life Balance",
                0,
                10,
                self.colors["primary"],
            )

        # Detailed plots (remaining rows)
        # Burnout distribution
        if "BurnoutLevel" in self.data.columns:
            ax5 = fig.add_subplot(gs[1, :2])
            burnout_data = self.data["BurnoutLevel"].dropna()
            ax5.hist(burnout_data, bins=20, alpha=0.7, color=self.colors["primary"])
            ax5.set_title("Burnout Level Distribution")
            ax5.set_xlabel("Burnout Level")
            ax5.set_ylabel("Frequency")

        # Correlation heatmap (subset)
        key_columns = [
            "BurnoutLevel",
            "JobSatisfaction",
            "StressLevel",
            "WorkLifeBalanceScore",
        ]
        available_columns = [col for col in key_columns if col in self.data.columns]

        if len(available_columns) >= 2:
            ax6 = fig.add_subplot(gs[1, 2:])
            corr_subset = self.data[available_columns].corr()
            sns.heatmap(corr_subset, annot=True, cmap="RdBu_r", center=0, ax=ax6)
            ax6.set_title("Key Metrics Correlation")

        # Department analysis (if available)
        if "Department" in self.data.columns and "BurnoutLevel" in self.data.columns:
            ax7 = fig.add_subplot(gs[2, :])
            dept_burnout = (
                self.data.groupby("Department")["BurnoutLevel"]
                .mean()
                .sort_values(ascending=False)
            )
            dept_burnout.plot(kind="bar", ax=ax7, color=self.colors["secondary"])
            ax7.set_title("Average Burnout Level by Department")
            ax7.set_xlabel("Department")
            ax7.set_ylabel("Average Burnout Level")
            ax7.tick_params(axis="x", rotation=45)

        # Risk distribution pie chart
        if "BurnoutLevel" in self.data.columns:
            ax8 = fig.add_subplot(gs[3, :2])
            high_risk = (self.data["BurnoutLevel"] >= 7).sum()
            medium_risk = (
                (self.data["BurnoutLevel"] >= 4) & (self.data["BurnoutLevel"] < 7)
            ).sum()
            low_risk = (self.data["BurnoutLevel"] < 4).sum()

            risk_data = [low_risk, medium_risk, high_risk]
            labels = ["Low Risk", "Medium Risk", "High Risk"]
            colors = [
                self.colors["success"],
                self.colors["warning"],
                self.colors["danger"],
            ]

            ax8.pie(risk_data, labels=labels, autopct="%1.1f%%", colors=colors)
            ax8.set_title("Burnout Risk Distribution")

        # Summary statistics table
        ax9 = fig.add_subplot(gs[3, 2:])
        ax9.axis("off")

        summary_data = []
        metrics = [
            "BurnoutLevel",
            "JobSatisfaction",
            "StressLevel",
            "WorkLifeBalanceScore",
        ]

        for metric in metrics:
            if metric in self.data.columns:
                mean_val = self.data[metric].mean()
                std_val = self.data[metric].std()
                summary_data.append([metric, f"{mean_val:.2f}", f"{std_val:.2f}"])

        if summary_data:
            table = ax9.table(
                cellText=summary_data,
                colLabels=["Metric", "Mean", "Std Dev"],
                cellLoc="center",
                loc="center",
            )
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            ax9.set_title("Summary Statistics", pad=20)

        return self._save_or_show_plot(fig, "mental_health_dashboard.png")

    def _create_metric_gauge(
        self, ax, value: float, title: str, min_val: float, max_val: float, color: str
    ):
        """Create a gauge-style visualization for a single metric."""
        # Simple gauge using a bar chart
        ax.barh([0], [value], color=color, alpha=0.7)
        ax.set_xlim(min_val, max_val)
        ax.set_ylim(-0.5, 0.5)
        ax.set_title(f"{title}\n{value:.1f}")
        ax.set_yticks([])
        ax.set_xlabel(f"{min_val}-{max_val}")

        # Add value text
        ax.text(
            value / 2,
            0,
            f"{value:.1f}",
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=12,
        )

    def _save_or_show_plot(self, fig: Figure, filename: str) -> Optional[str]:
        """Save plot to file or display based on text_only setting.

        Args:
            fig: Matplotlib figure to save or show
            filename: Name of file to save

        Returns:
            Path to saved file or None
        """
        try:
            if self.text_only:
                filepath = self.output_dir / filename
                fig.savefig(filepath, dpi=300, bbox_inches="tight")
                plt.close(fig)
                logger.info(f"Plot saved to {filepath}")
                return str(filepath)
            else:
                plt.show()
                return None
        except Exception as e:
            logger.error(f"Error saving/showing plot {filename}: {e}")
            plt.close(fig)
            return None
