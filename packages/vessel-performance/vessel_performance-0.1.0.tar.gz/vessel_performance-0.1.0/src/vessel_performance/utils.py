"""
Utility functions for vessel performance calculations.
"""

import math
from typing import Dict, Optional

def calculate_weather_factor(
    wind_speed: float,
    wave_height: float,
    wind_direction: Optional[float] = None,
    wave_direction: Optional[float] = None
) -> float:
    """
    Calculate weather correction factor for vessel performance.
    
    Args:
        wind_speed: Wind speed in knots
        wave_height: Significant wave height in meters
        wind_direction: Relative wind direction in degrees (0-360, optional)
        wave_direction: Relative wave direction in degrees (0-360, optional)
        
    Returns:
        float: Weather correction factor (1.0 means no correction)
    """
    # Basic weather factor calculation
    # This is a simplified version and should be enhanced with proper
    # naval architecture formulas for production use
    
    # Base impact from wind speed
    wind_factor = 1.0 + (wind_speed / 50.0) ** 2
    
    # Base impact from wave height
    wave_factor = 1.0 + (wave_height / 3.0) ** 2
    
    # Direction adjustment if provided
    direction_factor = 1.0
    if wind_direction is not None and wave_direction is not None:
        # Calculate average heading impact
        avg_direction = (wind_direction + wave_direction) / 2
        # Normalize to 0-180 degrees (assuming symmetrical impact)
        heading_angle = abs((avg_direction % 360) - 180)
        # Maximum impact at head seas (180 degrees)
        direction_factor = 1.0 + (heading_angle / 180.0) * 0.5
    
    # Combine all factors
    weather_factor = wind_factor * wave_factor * direction_factor
    
    # Limit the maximum correction factor
    return min(weather_factor, 2.0)

def calculate_admiralty_coefficient(
    displacement: float,
    speed: float,
    power: float
) -> float:
    """
    Calculate the Admiralty Coefficient.
    
    Args:
        displacement: Vessel displacement in metric tons
        speed: Vessel speed in knots
        power: Engine power in kW
        
    Returns:
        float: Admiralty Coefficient
    """
    if any(v <= 0 for v in [displacement, speed, power]):
        raise ValueError("All input values must be positive")
        
    return (displacement ** (2/3) * speed ** 3) / power

def estimate_fuel_consumption(
    power: float,
    sfoc: float = 190.0  # Specific Fuel Oil Consumption in g/kWh
) -> float:
    """
    Estimate daily fuel consumption based on power and SFOC.
    
    Args:
        power: Engine power in kW
        sfoc: Specific Fuel Oil Consumption in g/kWh (default 190)
        
    Returns:
        float: Daily fuel consumption in metric tons
    """
    if power < 0:
        raise ValueError("Power must be positive")
    if sfoc <= 0:
        raise ValueError("SFOC must be positive")
        
    # Calculate daily consumption
    daily_consumption = power * sfoc * 24 / 1000000  # Convert to metric tons
    return round(daily_consumption, 3) 