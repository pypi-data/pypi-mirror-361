"""
Data models for vessel performance calculations.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class VesselData:
    """Class for storing vessel basic data."""
    
    length: float  # Length overall in meters
    beam: float  # Beam (width) in meters
    draft: float  # Draft in meters
    displacement: float  # Displacement in metric tons
    
    # Optional parameters
    design_speed: Optional[float] = None  # Design speed in knots
    installed_power: Optional[float] = None  # Main engine power in kW
    
    def __post_init__(self):
        """Validate the input data."""
        if any(v <= 0 for v in [self.length, self.beam, self.draft, self.displacement]):
            raise ValueError("All dimensions must be positive numbers")
        
        if self.design_speed is not None and self.design_speed <= 0:
            raise ValueError("Design speed must be positive")
            
        if self.installed_power is not None and self.installed_power <= 0:
            raise ValueError("Installed power must be positive") 