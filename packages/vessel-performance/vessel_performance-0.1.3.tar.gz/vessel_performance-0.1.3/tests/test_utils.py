"""
Unit tests for utility functions, focusing on coordinate conversion functions.
"""

import pytest
from vessel_performance.utils import (
    convert_mfwam_point,
    convert_ec_point,
    convert_smoc_point,
    convert_era5_wind_point,
    convert_era5_wave_point,
    convert_era5_flow_point
)

def test_convert_mfwam_point():
    # Test normal case
    lat_idx, lon_idx = convert_mfwam_point(0.0, 0.0)
    assert lat_idx == 960  # (0 + 80) / (1/12)
    assert lon_idx == 2160  # (0 + 180) / (1/12)
    
    # Test boundary cases
    lat_idx, lon_idx = convert_mfwam_point(-80.0, -180.0)
    assert lat_idx == 0
    assert lon_idx == 0
    
    lat_idx, lon_idx = convert_mfwam_point(90.0, 180.0)
    assert lat_idx == 2040  # (90 + 80) / (1/12)
    assert lon_idx == 0  # 4320 -> 0 due to wraparound
    
    # Test middle values
    lat_idx, lon_idx = convert_mfwam_point(45.0, 90.0)
    assert lat_idx == 1500  # (45 + 80) / (1/12)
    assert lon_idx == 3240  # (90 + 180) / (1/12)

def test_convert_ec_point():
    # Test normal case
    lat_idx, lon_idx = convert_ec_point(0.0, 0.0)
    assert lat_idx == 360  # (0 + 90) / 0.25
    assert lon_idx == 720  # (0 + 180) / 0.25
    
    # Test boundary cases
    lat_idx, lon_idx = convert_ec_point(-90.0, -180.0)
    assert lat_idx == 0
    assert lon_idx == 0
    
    lat_idx, lon_idx = convert_ec_point(90.0, 180.0)
    assert lat_idx == 720  # (90 + 90) / 0.25
    assert lon_idx == 0  # 1440 -> 0 due to wraparound
    
    # Test middle values
    lat_idx, lon_idx = convert_ec_point(45.0, 90.0)
    assert lat_idx == 540  # (45 + 90) / 0.25
    assert lon_idx == 1080  # (90 + 180) / 0.25

def test_convert_smoc_point():
    # Test normal case
    lat_idx, lon_idx = convert_smoc_point(0.0, 0.0)
    assert lat_idx == 960  # (0 + 80) / (1/12)
    assert lon_idx == 2160  # (0 + 180) / (1/12)
    
    # Test boundary cases
    lat_idx, lon_idx = convert_smoc_point(-80.0, -180.0)
    assert lat_idx == 0
    assert lon_idx == 0
    
    lat_idx, lon_idx = convert_smoc_point(90.0, 180.0)
    assert lat_idx == 2040  # (90 + 80) / (1/12)
    assert lon_idx == 0  # 4320 -> 0 due to wraparound

def test_convert_era5_wind_point():
    # Test normal case
    lat_idx, lon_idx = convert_era5_wind_point(0.0, 0.0)
    assert lat_idx == 360  # (90 - 0) / 0.25
    assert lon_idx == 0  # 0 / 0.25
    
    # Test boundary cases
    lat_idx, lon_idx = convert_era5_wind_point(90.0, 0.0)
    assert lat_idx == 0  # (90 - 90) / 0.25
    assert lon_idx == 0
    
    lat_idx, lon_idx = convert_era5_wind_point(-90.0, 360.0)
    assert lat_idx == 720  # (90 - (-90)) / 0.25
    assert lon_idx == 0  # 1440 -> 0 due to wraparound
    
    # Test negative longitude
    lat_idx, lon_idx = convert_era5_wind_point(0.0, -180.0)
    assert lat_idx == 360  # (90 - 0) / 0.25
    assert lon_idx == 720  # (360 + (-180)) / 0.25

def test_convert_era5_wave_point():
    # Test normal case
    lat_idx, lon_idx = convert_era5_wave_point(0.0, 0.0)
    assert lat_idx == 180  # (90 - 0) / 0.5
    assert lon_idx == 0  # 0 / 0.5
    
    # Test boundary cases
    lat_idx, lon_idx = convert_era5_wave_point(90.0, 0.0)
    assert lat_idx == 0  # (90 - 90) / 0.5
    assert lon_idx == 0
    
    lat_idx, lon_idx = convert_era5_wave_point(-90.0, 360.0)
    assert lat_idx == 360  # (90 - (-90)) / 0.5
    assert lon_idx == 0  # 720 -> 0 due to wraparound
    
    # Test negative longitude
    lat_idx, lon_idx = convert_era5_wave_point(0.0, -180.0)
    assert lat_idx == 180  # (90 - 0) / 0.5
    assert lon_idx == 360  # (360 + (-180)) / 0.5

def test_convert_era5_flow_point():
    # Test normal case
    lat_idx, lon_idx = convert_era5_flow_point(0.0, 0.0)
    assert lat_idx == 960  # (0 + 80) / (1/12)
    assert lon_idx == 2160  # (0 + 180) / (1/12)
    
    # Test boundary cases
    lat_idx, lon_idx = convert_era5_flow_point(-80.0, -180.0)
    assert lat_idx == 0
    assert lon_idx == 0
    
    lat_idx, lon_idx = convert_era5_flow_point(90.0, 180.0)
    assert lat_idx == 2040  # (90 + 80) / (1/12)
    assert lon_idx == 0  # 4320 -> 0 due to wraparound

def test_invalid_inputs():
    # Test out of range values
    with pytest.raises(Exception):
        convert_mfwam_point(-81.0, 0.0)  # Latitude too low
    
    with pytest.raises(Exception):
        convert_mfwam_point(91.0, 0.0)  # Latitude too high
    
    with pytest.raises(Exception):
        convert_ec_point(0.0, -181.0)  # Longitude too low
    
    with pytest.raises(Exception):
        convert_ec_point(0.0, 181.0)  # Longitude too high 