"""
Main analyzer module for vessel performance calculations.
"""

import numpy as np
from typing import Dict, List, Optional, Union

from .models import VesselData
from .utils import calculate_weather_factor

class VesselAnalyzer:
    """Main class for analyzing vessel performance metrics."""
    
    def __init__(self):
        """Initialize the VesselAnalyzer."""
        pass
    
    def calculate_fuel_efficiency(
        self,
        fuel_consumption: float,
        vessel_speed: float,
        displacement: float,
        weather_factor: Optional[float] = None
    ) -> float:
        """
        Calculate the fuel efficiency of the vessel.
        
        Args:
            fuel_consumption: Daily fuel consumption in tons
            vessel_speed: Speed in knots
            displacement: Vessel displacement in tons
            weather_factor: Optional weather correction factor
            
        Returns:
            float: Fuel efficiency in grams per ton-nautical mile
        """
        if weather_factor is None:
            weather_factor = 1.0
            
        # Basic fuel efficiency calculation
        efficiency = (fuel_consumption * 1000000) / (displacement * vessel_speed * 24 * weather_factor)
        return round(efficiency, 2)
    
    def get_speed_power_curve(
        self,
        speed_range: List[float],
        vessel_data: Dict[str, float]
    ) -> Dict[str, List[float]]:
        """
        Calculate the speed-power relationship curve.
        
        Args:
            speed_range: List of speeds to calculate power for
            vessel_data: Dictionary containing vessel dimensions
            
        Returns:
            Dict containing speeds and corresponding power requirements
        """
        # Simplified power calculation using admiralty coefficient
        powers = []
        for speed in speed_range:
            # Basic cubic relationship between speed and power
            power = self._calculate_power(speed, vessel_data)
            powers.append(round(power, 2))
            
        return {
            "speeds": speed_range,
            "powers": powers
        }
    
    def _calculate_power(self, speed: float, vessel_data: Dict[str, float]) -> float:
        """
        Calculate required power for a given speed.
        
        This is a simplified calculation and should be enhanced with proper
        naval architecture formulas for production use.
        """
        # Simplified calculation using admiralty coefficient
        length = vessel_data.get("length", 0)
        beam = vessel_data.get("beam", 0)
        draft = vessel_data.get("draft", 0)
        
        # Basic power calculation
        displacement = length * beam * draft * 0.5  # Simplified displacement calculation
        power = (displacement ** (2/3) * speed ** 3) / 50  # Simplified admiralty formula
        
        return power 