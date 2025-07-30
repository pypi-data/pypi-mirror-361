"""
Unit tests for the VesselAnalyzer class.
"""

import pytest
from vessel_performance import VesselAnalyzer
from vessel_performance.models import VesselData

def test_fuel_efficiency_calculation():
    analyzer = VesselAnalyzer()
    
    # Test basic calculation
    efficiency = analyzer.calculate_fuel_efficiency(
        fuel_consumption=100,  # tons per day
        vessel_speed=14,       # knots
        displacement=50000,    # tons
    )
    assert efficiency > 0
    
    # Test with weather factor
    efficiency_with_weather = analyzer.calculate_fuel_efficiency(
        fuel_consumption=100,
        vessel_speed=14,
        displacement=50000,
        weather_factor=1.2
    )
    assert efficiency_with_weather > efficiency  # Should be less efficient in bad weather

def test_speed_power_curve():
    analyzer = VesselAnalyzer()
    
    vessel_data = {
        "length": 200,
        "beam": 32,
        "draft": 12
    }
    
    result = analyzer.get_speed_power_curve(
        speed_range=[10, 12, 14, 16],
        vessel_data=vessel_data
    )
    
    assert "speeds" in result
    assert "powers" in result
    assert len(result["speeds"]) == len(result["powers"])
    assert all(p > 0 for p in result["powers"])
    
    # Test power increases with speed
    powers = result["powers"]
    assert all(powers[i] < powers[i+1] for i in range(len(powers)-1))

def test_vessel_data_validation():
    # Test valid data
    valid_data = VesselData(
        length=200,
        beam=32,
        draft=12,
        displacement=50000
    )
    assert valid_data.length == 200
    
    # Test invalid data
    with pytest.raises(ValueError):
        VesselData(
            length=-200,  # Invalid negative length
            beam=32,
            draft=12,
            displacement=50000
        )
        
    with pytest.raises(ValueError):
        VesselData(
            length=200,
            beam=32,
            draft=12,
            displacement=50000,
            design_speed=-15  # Invalid negative speed
        ) 