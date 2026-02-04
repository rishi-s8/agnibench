# agnibench

A comprehensive benchmarking framework for evaluating AI agents on multi-step tool-calling tasks.

> ⚠️ **Warning**: This project is under active development with regular breaking changes in the API.

## Overview

agnibench provides a structured framework for testing and comparing AI agent performance across various domains including customer service, data analysis, mathematical reasoning, research synthesis, and workspace management.

## Features

- **Multiple Benchmark Suites**: Pre-configured test suites for different domains
- **Task Characteristics**: Detailed metrics for task difficulty, information flow, and complexity
- **Verification System**: Flexible verifiers for exact match, environment state, and tool call sequences
- **Comprehensive Reporting**: Detailed benchmark reports and model comparison analytics
- **Simulated Environments**: Isolated testing environments for reproducible results

## Installation

```bash
pip install -e .
```

For development with additional tools:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from agnibench import BenchmarkRunner, BenchmarkSuite
from agnibench.suites import customer_service, data_analysis

# Create a benchmark runner
runner = BenchmarkRunner()

# Run benchmarks
results = runner.run_suite(customer_service.suite)

# Generate reports
report = runner.generate_report(results)
print(report)
```

## Benchmark Suites

- **Customer Service**: Multi-turn customer interaction scenarios
- **Data Analysis**: Data processing and analytical tasks
- **Math Reasoning**: Mathematical problem-solving challenges
- **Research Synthesis**: Information gathering and synthesis
- **Workspace**: File and project management operations

## License

CC BY-SA 4.0 (See LICENSE file for details.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
