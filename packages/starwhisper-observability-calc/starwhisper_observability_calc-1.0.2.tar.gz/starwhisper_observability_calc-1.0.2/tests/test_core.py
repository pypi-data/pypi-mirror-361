"""
测试核心计算功能
"""

import pytest
from starwhisper_observation_calculator.core import (
    ObservabilityCalculator, 
    calculate_target_observability
)


class TestObservabilityCalculator:
    """测试可观测性计算器"""
    
    def test_initialization(self):
        """测试初始化"""
        calc = ObservabilityCalculator()
        assert calc.latitude == 40.393333
        assert calc.longitude == 117.575278
        assert calc.altitude == 900.0
        
    def test_custom_location(self):
        """测试自定义位置"""
        calc = ObservabilityCalculator(
            latitude=30.0,
            longitude=120.0,
            altitude=100.0
        )
        assert calc.latitude == 30.0
        assert calc.longitude == 120.0
        assert calc.altitude == 100.0
    
    def test_calculate_vega_observability(self):
        """测试计算Vega可观测性"""
        calc = ObservabilityCalculator()
        result = calc.calculate_observability("Vega")
        
        assert result["success"] is True
        assert result["target_name"] == "Vega"
        assert "coordinates" in result
        assert "observability" in result
        assert "observer_location" in result
    
    def test_calculate_moon_observability(self):
        """测试计算月球可观测性"""
        calc = ObservabilityCalculator()
        result = calc.calculate_observability("moon")
        
        assert result["success"] is True
        assert result["target_name"] == "moon"
        assert "coordinates" in result
        assert "observability" in result
    
    def test_invalid_target(self):
        """测试无效目标"""
        calc = ObservabilityCalculator()
        result = calc.calculate_observability("invalid_target_name")
        
        assert result["success"] is False
        assert "error" in result


class TestCalculateTargetObservability:
    """测试目标可观测性计算函数"""
    
    def test_vega_calculation(self):
        """测试Vega计算"""
        result = calculate_target_observability(
            latitude=40.393333,
            longitude=117.575278,
            target_name="Vega",
            altitude=900.0
        )
        
        assert result["success"] is True
        assert result["target_name"] == "Vega"
        assert "coordinates" in result
        assert "observability" in result
        assert "observer_location" in result
        assert "constraints" in result
        
    def test_moon_calculation(self):
        """测试月球计算"""
        result = calculate_target_observability(
            latitude=40.393333,
            longitude=117.575278,
            target_name="moon",
            altitude=900.0
        )
        
        assert result["success"] is True
        assert result["target_name"] == "moon"
        
    def test_custom_constraints(self):
        """测试自定义约束"""
        result = calculate_target_observability(
            latitude=40.393333,
            longitude=117.575278,
            target_name="Vega",
            altitude=900.0,
            min_altitude=20.0,
            min_moon_separation=45.0,
            time_range_hours=48
        )
        
        assert result["success"] is True
        assert result["constraints"]["min_altitude"] == 20.0
        assert result["constraints"]["min_moon_separation"] == 45.0
        assert result["constraints"]["time_range_hours"] == 48
        
    def test_invalid_target(self):
        """测试无效目标"""
        result = calculate_target_observability(
            latitude=40.393333,
            longitude=117.575278,
            target_name="invalid_target",
            altitude=900.0
        )
        
        assert result["success"] is False
        assert "error" in result 