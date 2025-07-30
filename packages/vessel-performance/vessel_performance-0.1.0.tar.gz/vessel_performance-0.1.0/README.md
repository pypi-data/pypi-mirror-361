# Vessel Performance

A Python library for calculating and analyzing vessel performance metrics.

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

For detailed documentation, please visit our [documentation site](https://vessel-performance.readthedocs.io/).

## Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 