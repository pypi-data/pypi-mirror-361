# Vessel Performance

A Python library for calculating and analyzing vessel performance metrics.

[![PyPI version](https://badge.fury.io/py/vessel-performance.svg)](https://badge.fury.io/py/vessel-performance)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Calculate vessel fuel efficiency
- Analyze vessel speed and power relationships
- Estimate vessel performance under different weather conditions
- Generate performance reports and visualizations

## Installation

You can install the package via pip:

```bash
pip install vessel-performance
```

## Quick Start

```python
from vessel_performance import VesselAnalyzer
∏
# Create a vessel analyzer instance
analyzer = VesselAnalyzer()

# Calculate fuel efficiency
efficiency = analyzer.calculate_fuel_efficiency(
    fuel_consumption=100,  # tons per day
    vessel_speed=14,       # knots
    displacement=50000     # tons
)

# Analyze speed-power relationship
power_curve = analyzer.get_speed_power_curve(
    speed_range=[10, 15, 20],  # knots
    vessel_data={
        "length": 200,         # meters
        "beam": 32,           # meters
        "draft": 12           # meters
    }
)
```

## Documentation

- [API Documentation](docs/api.md) - Detailed documentation of all classes and functions
- [Usage Examples](docs/examples.md) - Various examples and use cases
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project

## Advanced Usage

For more complex examples and real-world scenarios, check out our [examples documentation](docs/examples.md). Here are some highlights:

- Weather impact analysis
- Route planning and optimization
- Performance monitoring
- Fuel consumption estimation

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/vessel-performance.git
cd vessel-performance

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details on how to:

- Report bugs
- Suggest new features
- Submit pull requests
- Update documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have questions:

1. Check the [documentation](docs/)
2. Look for similar issues in the [issue tracker](https://github.com/yourusername/vessel-performance/issues)
3. Open a new issue if needed

## Authors

- Shane Lee (liqiyuworks@163.com)

## Acknowledgments

- Thanks to all contributors
- Special thanks to the naval architecture community for formulas and methodologies 