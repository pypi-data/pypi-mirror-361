"""
测试MCP服务器功能
"""

import pytest
import json
from starwhisper_observation_calculator.mcp_server import ObservabilityMCPServer


class TestObservabilityMCPServer:
    """测试MCP服务器"""
    
    def test_initialization(self):
        """测试初始化"""
        server = ObservabilityMCPServer()
        assert server.server_info["name"] == "starwhisper-observation-calculator"
        assert server.server_info["version"] == "1.0.0"
        assert len(server.tools) == 1
        assert server.tools[0]["name"] == "calculate_observability"
    
    def test_initialize_request(self):
        """测试初始化请求"""
        server = ObservabilityMCPServer()
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert "capabilities" in response["result"]
        assert "serverInfo" in response["result"]
    
    def test_tools_list_request(self):
        """测试工具列表请求"""
        server = ObservabilityMCPServer()
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 1
        assert response["result"]["tools"][0]["name"] == "calculate_observability"
    
    def test_tools_call_request(self):
        """测试工具调用请求"""
        server = ObservabilityMCPServer()
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "calculate_observability",
                "arguments": {
                    "latitude": 40.393333,
                    "longitude": 117.575278,
                    "target_name": "Vega"
                }
            }
        }
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        assert "result" in response
        assert "content" in response["result"]
        assert len(response["result"]["content"]) == 1
        assert response["result"]["content"][0]["type"] == "text"
        assert "Vega" in response["result"]["content"][0]["text"]
    
    def test_tools_call_missing_params(self):
        """测试工具调用缺少参数"""
        server = ObservabilityMCPServer()
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "calculate_observability",
                "arguments": {
                    "latitude": 40.393333
                    # 缺少longitude和target_name
                }
            }
        }
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 4
        assert "error" in response
        assert response["error"]["code"] == -32602
    
    def test_unknown_method(self):
        """测试未知方法"""
        server = ObservabilityMCPServer()
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "unknown_method",
            "params": {}
        }
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 5
        assert "error" in response
        assert response["error"]["code"] == -32601
    
    def test_format_result_success(self):
        """测试格式化成功结果"""
        server = ObservabilityMCPServer()
        result = {
            "success": True,
            "target_name": "Vega",
            "coordinates": {
                "ra_string": "18:36:56.34",
                "dec_string": "+38:47:01.3",
                "ra_degrees": 279.234,
                "dec_degrees": 38.784
            },
            "observability": {
                "current_altitude": 45.0,
                "current_azimuth": 180.0,
                "observable": True,
                "constraints_satisfied": {
                    "altitude": True,
                    "moon_separation": True
                },
                "altitude_curve": [
                    {"time": "2024-01-01T00:00:00", "altitude": 45.0, "observable": True}
                ]
            },
            "observer_location": {
                "latitude": 40.393333,
                "longitude": 117.575278,
                "altitude": 900.0,
                "timezone": "UTC"
            },
            "constraints": {
                "min_altitude": 30.0,
                "min_moon_separation": 30.0,
                "time_range_hours": 24
            }
        }
        
        formatted = server._format_result(result)
        
        assert "Vega" in formatted
        assert "18:36:56.34" in formatted
        assert "+38:47:01.3" in formatted
        assert "45.00°" in formatted
        assert "✅ Yes" in formatted
    
    def test_format_result_failure(self):
        """测试格式化失败结果"""
        server = ObservabilityMCPServer()
        result = {
            "success": False,
            "error": "Target not found"
        }
        
        formatted = server._format_result(result)
        
        assert "Calculation failed" in formatted
        assert "Target not found" in formatted 