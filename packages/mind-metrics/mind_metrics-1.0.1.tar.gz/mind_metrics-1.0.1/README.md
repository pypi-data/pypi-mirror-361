# Mind Metrics

**Mind Metrics** is a comprehensive data analysis application for workplace mental health survey data. It provides insights into burnout patterns, stress factors, and workplace well-being metrics through interactive visualizations and statistical analysis.

## Features

- 📊 **Comprehensive Analytics**: Analyze burnout levels, job satisfaction, stress patterns, and productivity metrics
- 📈 **Interactive Visualizations**: Generate insightful plots and charts for mental health data
- 🔧 **Flexible Data Input**: Support for CSV and Excel files with automatic data validation
- 🖥️ **Command Line Interface**: Easy-to-use CLI built with Click framework
- 📋 **Detailed Reporting**: Generate comprehensive reports on workplace mental health trends
- 🧪 **Robust Testing**: Comprehensive test suite ensuring data integrity and reliability

## Installation

### From PyPI (Recommended)

```bash
pip install mind-metrics
```

### From Source

```bash
git clone https://codebase.helmholtz.cloud/tud-rse-pojects-2025/group-7.git
cd group-7
pip install uv
uv sync
uv pip install -e . 
```

## Quick Start

### Basic Usage

```bash
# Analyze a mental health dataset
mind-metrics --source dataset/mental_health_workplace_survey.csv

# Run in text-only mode (no GUI plots)
mind-metrics --source dataset/mental_health_workplace_survey.csv --text-only

# Enable verbose logging
mind-metrics --source dataset/mental_health_workplace_survey.csv -vv

# Get help
mind-metrics --help
```

### Example Analysis

```bash
# Comprehensive analysis with debug output
mind-metrics --source https://example.com/survey.csv -vvv --text-only
```

## Data Format

Mind Metrics expects datasets with the following key columns:

- **EmployeeID**: Unique identifier for employees
- **Age**: Employee age
- **Gender**: Employee gender
- **BurnoutLevel**: Burnout score (0-10 scale)
- **JobSatisfaction**: Job satisfaction score (0-10 scale)
- **StressLevel**: Stress level (0-10 scale)
- **WorkLifeBalanceScore**: Work-life balance rating
- **HasMentalHealthSupport**: Whether employee has mental health support

For a complete list of supported columns, see our [data schema documentation](docs/data-schema.md).

## Example Dataset

Mind Metrics includes an example dataset (`mental_health_workplace_survey.csv`) for testing and demonstration purposes. This dataset is based on the "Mental Health and Burnout in the Workplace" dataset by Khushi Yadav, available on [Kaggle](https://www.kaggle.com/datasets/khushikyad001/mental-health-and-burnout-in-the-workplace).

### Dataset Attribution

The example dataset used in this project is derived from:
- **Title**: Mental Health and Burnout in the Workplace
- **Author**: Khushi Yadav
- **Source**: Kaggle
- **URL**: https://www.kaggle.com/datasets/khushikyad001/mental-health-and-burnout-in-the-workplace
- **License**: [MIT License](https://www.mit.edu/~amini/LICENSE.md)

We thank the original dataset creator for making this valuable data available for research and development purposes.

## Command Line Options

```
Options:
  --source TEXT           URL or path to dataset (CSV/Excel)  [required]
  -v, -vv, -vvv          Verbose output (WARNING/INFO/DEBUG levels)
  --text-only            Suppress graphical output
  --output-dir TEXT      Directory for output files [default: ./output]
  --format [json|csv]    Output format for reports [default: json]
  --help                 Show this message and exit.
```

## Output

Mind Metrics generates several types of output:

1. **Summary Statistics**: Key metrics and trends in your data
2. **Visualizations**: Charts showing burnout patterns, correlations, and distributions
3. **Reports**: Detailed analysis reports in JSON or CSV format
4. **Recommendations**: Data-driven insights for improving workplace mental health

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://codebase.helmholtz.cloud/tud-rse-pojects-2025/group-7.git
cd group-7

# Install dependencies
uv sync

# Install pre-commit hooks
pre-commit install

# Run tests
uv run pytest

# Run linting
uv run ruff check mind_metrics/ tests/
uv run mypy mind_metrics/
```

### Project Structure

```
group-7/
├── CITATION.cff
├── CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE.md
├── dataset/
│   ├── mental_health_workplace_survey.csv
├── pyproject.toml
├── README.md
├── mind_metrics/
│   ├── __init__.py
│   ├── __main__.py         # Main entry point
│   ├── cli.py              # Command line interface
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py       # Data loading and validation
│   │   └── cleaner.py      # Data cleaning utilities
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── burnout.py      # Burnout analysis
│   │   ├── correlations.py # Correlation analysis
│   │   └── statistics.py   # Statistical computations
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plots.py        # Plotting functions
│   │   └── dashboard.py    # Dashboard generation
│   └── utils/
│       ├── __init__.py
│       ├── logger.py       # Logging configuration
│       └── validation.py   # Data validation utilities
├── tests/
│   ├── conftest.py
│   ├── integration/
│   │   ├── test_cli.py
│   │   └── test_end_to_end.py
│   └── unit/
│       ├── test_burnout_analyzer.py
│       ├── test_data_cleaner.py
│       ├── test_data_loader.py
│       └── test_validation.py
└── uv.lock
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mind_metrics

# Run specific test file
uv run pytest tests/test_data_loader.py
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Merge Request

## Documentation

- [User Guide](https://group-7-589e0e.pages.hzdr.de/)
- [Developer Guide](https://group-7-589e0e.pages.hzdr.de/)

## Citation

If you use Mind Metrics in your research, please cite it:

```bibtex
@software{mind_metrics,
  title = {Mind Metrics: Workplace Mental Health Analytics},
  author = {Group 7},
  year = {2025},
  url = {https://codebase.helmholtz.cloud/tud-rse-pojects-2025/group-7},
  version = {1.0.0}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Mental health research community for inspiration
- Khushi Yadav for the "Mental Health and Burnout in the Workplace" dataset from Kaggle
- Open source contributors and maintainers
- Survey participants who make this research possible

## Support

- 📧 Email: support@mindmetrics.dev
- 🐛 Issues: [GitLab Issues](https://codebase.helmholtz.cloud/tud-rse-pojects-2025/group-7/-/issues)
- 📖 Documentation: [Project Documentation](https://group-7-589e0e.pages.hzdr.de/)

---

**Made with ❤️ for better workplace mental health**