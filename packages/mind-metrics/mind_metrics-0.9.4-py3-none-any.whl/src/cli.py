"""Command Line Interface for Mind Metrics."""

import logging
import sys
from pathlib import Path

import click
from rich.console import Console

from src.analysis import BurnoutAnalyzer, CorrelationAnalyzer, StatisticsCalculator
from src.data import DataCleaner, DataLoader
from src.utils.logger import setup_logging
from src.visualization import DashboardCreator, PlotGenerator

console = Console()


def safe_get_stat(stats_dict, column_name, stat_name, default=0.0):
    """Safely get a statistic value, handling different key formats."""
    # Try exact column name first
    if column_name in stats_dict:
        return stats_dict[column_name].get(stat_name, default)

    # Try lowercase version
    lowercase_name = column_name.lower()
    if lowercase_name in stats_dict:
        return stats_dict[lowercase_name].get(stat_name, default)

    # Try with underscores
    underscore_name = column_name.replace(" ", "_").lower()
    if underscore_name in stats_dict:
        return stats_dict[underscore_name].get(stat_name, default)

    # Try camelCase to snake_case conversion
    import re

    snake_case = re.sub("([A-Z])", r"_\1", column_name).lower().lstrip("_")
    if snake_case in stats_dict:
        return stats_dict[snake_case].get(stat_name, default)

    return default


@click.command()
@click.option(
    "--source",
    required=True,
    type=str,
    help="URL or path to dataset (CSV/Excel format)",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Verbose output: -v (WARNING), -vv (INFO), -vvv (DEBUG)",
)
@click.option(
    "--text-only",
    is_flag=True,
    help="Suppress graphical output (save plots to files instead)",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("./output"),
    help="Directory for output files",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Output format for reports",
)
@click.version_option(package_name="mind-metrics")
def main(
    source: str,
    verbose: int,
    text_only: bool,
    output_dir: Path,
    output_format: str,
) -> None:
    """Mind Metrics: Workplace Mental Health Analytics.

    Analyze workplace mental health survey data to identify burnout patterns,
    stress factors, and well-being metrics. Generate comprehensive reports
    and visualizations for data-driven insights.

    Examples:

        # Basic analysis
        mind-metrics --source data/survey.csv

        # Analysis with verbose output, no GUI
        mind-metrics --source data/survey.xlsx -vv --text-only

        # Save outputs to custom directory
        mind-metrics --source https://example.com/data.csv --output-dir ./results
    """
    # Setup logging based on verbosity level
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    console.print(
        f"[bold blue]Mind Metrics v{click.get_current_context().find_root().info_name}[/bold blue]"
    )
    console.print("🧠 Workplace Mental Health Analytics\n")

    try:
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Load and validate data
        console.print("📊 [bold]Loading data...[/bold]")
        loader = DataLoader()
        raw_data = loader.load(source)
        logger.info(f"Loaded {len(raw_data)} records from {source}")

        # Clean and validate data
        console.print("🧹 [bold]Cleaning data...[/bold]")
        cleaner = DataCleaner()
        clean_data = cleaner.clean(raw_data)
        logger.info(f"Cleaned data: {len(clean_data)} valid records")

        # Perform statistical analysis
        console.print("📈 [bold]Performing statistical analysis...[/bold]")
        stats_calc = StatisticsCalculator(clean_data)
        basic_stats = stats_calc.calculate_basic_statistics()

        # Burnout analysis
        console.print("🔥 [bold]Analyzing burnout patterns...[/bold]")
        burnout_analyzer = BurnoutAnalyzer(clean_data)
        burnout_insights = burnout_analyzer.analyze_burnout_patterns()
        risk_factors = burnout_analyzer.identify_risk_factors()

        # Correlation analysis
        console.print("🔗 [bold]Computing correlations...[/bold]")
        corr_analyzer = CorrelationAnalyzer(clean_data)
        correlations = corr_analyzer.compute_correlations()
        significant_correlations = corr_analyzer.find_significant_correlations()

        # Generate visualizations
        console.print("📊 [bold]Creating visualizations...[/bold]")
        plot_gen = PlotGenerator(clean_data, output_dir, text_only)

        # Generate individual plots
        plot_gen.create_burnout_distribution_plot()
        plot_gen.create_correlation_heatmap(correlations)
        plot_gen.create_stress_vs_satisfaction_plot()
        plot_gen.create_work_life_balance_analysis()
        plot_gen.create_demographic_analysis()

        if not text_only:
            console.print("🎨 [bold]Creating interactive dashboard...[/bold]")
            dashboard = DashboardCreator(clean_data)
            dashboard.create_comprehensive_dashboard(output_dir / "dashboard.html")

        # Generate comprehensive report
        console.print("📄 [bold]Generating report...[/bold]")

        # Safely extract statistics with proper error handling
        try:
            # Get severity distribution data safely
            severity_dist = burnout_insights.get("severity_distribution", {})
            high_burnout_pct = severity_dist.get("high_burnout_percentage", 0.0)

            report_data = {
                "summary": {
                    "total_employees": len(clean_data),
                    "average_burnout_level": safe_get_stat(
                        basic_stats, "BurnoutLevel", "mean"
                    ),
                    "high_burnout_percentage": high_burnout_pct,
                    "average_job_satisfaction": safe_get_stat(
                        basic_stats, "JobSatisfaction", "mean"
                    ),
                    "stress_level_average": safe_get_stat(
                        basic_stats, "StressLevel", "mean"
                    ),
                    "work_life_balance_average": safe_get_stat(
                        basic_stats, "WorkLifeBalanceScore", "mean"
                    ),
                    "data_retention_rate": cleaner.get_cleaning_summary().get(
                        "data_retention_rate", 1.0
                    ),
                },
                "burnout_analysis": burnout_insights,
                "risk_factors": risk_factors,
                "correlations": {
                    "significant_correlations": significant_correlations,
                    "correlation_matrix": (
                        correlations.to_dict()
                        if hasattr(correlations, "to_dict")
                        else correlations
                    ),
                },
                "statistics": basic_stats,
                "recommendations": burnout_analyzer.generate_burnout_recommendations(),
                "metadata": {
                    "source_file": source,
                    "total_records_processed": len(clean_data),
                    "data_cleaning_summary": cleaner.get_cleaning_summary(),
                },
            }

            # Save report
            report_file = output_dir / f"mental_health_report.{output_format}"
            if output_format == "json":
                import json

                with open(report_file, "w") as f:
                    json.dump(report_data, f, indent=2, default=str)
            else:  # CSV format
                import pandas as pd

                # Flatten report for CSV
                summary_df = pd.DataFrame([report_data["summary"]])
                summary_df.to_csv(report_file, index=False)

            logger.info(f"Report saved to {report_file}")

            # Display summary with safe value extraction
            console.print("\n[bold green]✅ Analysis Complete![/bold green]")
            console.print(f"📊 Total Employees Analyzed: {len(clean_data)}")

            avg_burnout = safe_get_stat(basic_stats, "BurnoutLevel", "mean")
            if avg_burnout > 0:
                console.print(f"🔥 Average Burnout Level: {avg_burnout:.2f}/10")

            avg_satisfaction = safe_get_stat(basic_stats, "JobSatisfaction", "mean")
            if avg_satisfaction > 0:
                console.print(f"😊 Average Job Satisfaction: {avg_satisfaction:.2f}/10")

            avg_stress = safe_get_stat(basic_stats, "StressLevel", "mean")
            if avg_stress > 0:
                console.print(f"😰 Average Stress Level: {avg_stress:.2f}/10")

            avg_wlb = safe_get_stat(basic_stats, "WorkLifeBalanceScore", "mean")
            if avg_wlb > 0:
                console.print(f"⚖️ Average Work-Life Balance: {avg_wlb:.2f}/10")

            console.print(f"📈 High Burnout Risk: {high_burnout_pct:.1f}% of employees")
            console.print(f"\n📁 All outputs saved to: {output_dir}")

            if not text_only:
                console.print(
                    "🌐 Open dashboard.html to view interactive visualizations"
                )

            # Show key recommendations if available
            recommendations = report_data.get("recommendations", [])
            if recommendations:
                console.print("\n🎯 [bold]Key Recommendations:[/bold]")
                for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                    console.print(f"  {i}. {rec}")

        except Exception as report_error:
            logger.error(f"Error generating report: {report_error}")
            console.print(
                f"[yellow]⚠️ Warning: Report generation had issues: {report_error}[/yellow]"
            )
            # Still show basic completion message
            console.print("\n[bold green]✅ Analysis Complete![/bold green]")
            console.print(f"📊 Total Employees Analyzed: {len(clean_data)}")
            console.print(f"📁 Outputs saved to: {output_dir}")

    except FileNotFoundError:
        console.print(f"[bold red]❌ Error: File not found: {source}[/bold red]")
        logger.error(f"File not found: {source}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
