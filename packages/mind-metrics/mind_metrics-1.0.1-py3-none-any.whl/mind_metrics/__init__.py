"""Mind Metrics: Workplace Mental Health Analytics.

A comprehensive data analysis application for workplace mental health survey data,
providing insights into burnout patterns, stress factors, and workplace well-being metrics.
"""

__version__ = "1.0.1"
__author__ = "Mind Metrics Team"
__email__ = "team@mindmetrics.dev"
__license__ = "MIT"

from .analysis import BurnoutAnalyzer, CorrelationAnalyzer, StatisticsCalculator
from .data import DataCleaner, DataLoader
from .visualization import DashboardCreator, PlotGenerator

__all__ = [
    "BurnoutAnalyzer",
    "CorrelationAnalyzer",
    "StatisticsCalculator",
    "DataLoader",
    "DataCleaner",
    "PlotGenerator",
    "DashboardCreator",
]
