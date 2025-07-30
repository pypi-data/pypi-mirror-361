"""
Vessel Performance Analysis Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A comprehensive library for analyzing vessel performance metrics.
"""

from vessel_performance.analyzer import VesselAnalyzer
from vessel_performance.models import VesselData
from vessel_performance.utils import calculate_weather_factor

__version__ = "0.1.0"
__author__ = "Jiufang Technology"

__all__ = ["VesselAnalyzer", "VesselData", "calculate_weather_factor"] 