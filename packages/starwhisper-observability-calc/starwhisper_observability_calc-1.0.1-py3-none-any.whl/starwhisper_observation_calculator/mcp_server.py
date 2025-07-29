"""
MCP天文可观测性计算服务器
提供标准MCP接口，用于计算天文目标的可观测性
"""

import json
import logging
import sys
from typing import Any, Dict

from .core import calculate_target_observability

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置标准输入输出编码
if sys.platform.startswith("win"):
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stdin = codecs.getreader("utf-8")(sys.stdin.detach())


class ObservabilityMCPServer:
    """MCP天文可观测性计算服务器"""

    def __init__(self):
        """初始化MCP服务器"""
        self.server_info = {
            "name": "starwhisper-observation-calculator",
            "version": "1.0.0",
            "description": "Calculate astronomical target observability",
        }

        self.tools = [
            {
                "name": "calculate_observability",
                "description": "Calculate observability for astronomical targets",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Observer latitude (degrees)",
                            "minimum": -90,
                            "maximum": 90,
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Observer longitude (degrees)",
                            "minimum": -180,
                            "maximum": 180,
                        },
                        "target_name": {
                            "type": "string",
                            "description": "Target name (e.g., 'Vega', 'moon', 'mars')",
                        },
                        "altitude": {
                            "type": "number",
                            "description": "Observer altitude (meters)",
                            "default": 900.0,
                        },
                        "min_altitude": {
                            "type": "number",
                            "description": "Minimum horizon altitude (degrees)",
                            "default": 30.0,
                            "minimum": 0,
                            "maximum": 90,
                        },
                        "min_moon_separation": {
                            "type": "number",
                            "description": "Minimum moon separation (degrees)",
                            "default": 30.0,
                            "minimum": 0,
                            "maximum": 180,
                        },
                        "time_range_hours": {
                            "type": "integer",
                            "description": "Time range to check (hours)",
                            "default": 24,
                            "minimum": 1,
                            "maximum": 168,
                        },
                    },
                    "required": ["latitude", "longitude", "target_name"],
                },
            }
        ]

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理MCP请求

        Args:
            request: MCP请求字典

        Returns:
            MCP响应字典
        """
        try:
            method = request.get("method")

            if method == "initialize":
                return self._handle_initialize(request)
            elif method == "tools/list":
                return self._handle_tools_list(request)
            elif method == "tools/call":
                return self._handle_tools_call(request)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }

        except Exception as e:
            logger.error(f"处理请求时出错: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }

    def _handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": self.server_info,
            },
        }

    def _handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具列表请求"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"tools": self.tools},
        }

    def _handle_tools_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用请求"""
        params = request.get("params", {})
        arguments = params.get("arguments", {})

        # 提取参数
        latitude = arguments.get("latitude")
        longitude = arguments.get("longitude")
        target_name = arguments.get("target_name")
        altitude = arguments.get("altitude", 900.0)
        min_altitude = arguments.get("min_altitude", 30.0)
        min_moon_separation = arguments.get("min_moon_separation", 30.0)
        time_range_hours = arguments.get("time_range_hours", 24)

        # 验证必需参数
        if latitude is None or longitude is None or target_name is None:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32602,
                    "message": "Missing required parameters: latitude, longitude, target_name",
                },
            }

        # 调用计算函数
        try:
            result = calculate_target_observability(
                latitude=latitude,
                longitude=longitude,
                target_name=target_name,
                altitude=altitude,
                min_altitude=min_altitude,
                min_moon_separation=min_moon_separation,
                time_range_hours=time_range_hours,
            )

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{"type": "text", "text": self._format_result(result)}]
                },
            }

        except Exception as e:
            logger.error(f"计算可观测性时出错: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": f"Calculation error: {str(e)}"},
            }

    def _format_result(self, result: Dict[str, Any]) -> str:
        """
        格式化计算结果为可读文本

        Args:
            result: 计算结果字典

        Returns:
            格式化的结果文本
        """
        if not result.get("success", False):
            return f"Calculation failed: {result.get('error', 'Unknown error')}"

        target_name = result.get("target_name", "Unknown target")
        coordinates = result.get("coordinates", {})
        observability = result.get("observability", {})
        observer_location = result.get("observer_location", {})
        constraints = result.get("constraints", {})

        # 构建结果文本
        text_parts = [
            f"**{target_name}** Observability Analysis Report",
            "",
            "**Observer Location**",
            f"  Latitude: {observer_location.get('latitude', 0):.6f}°",
            f"  Longitude: {observer_location.get('longitude', 0):.6f}°",
            f"  Altitude: {observer_location.get('altitude', 0):.1f}m",
            f"  Timezone: {observer_location.get('timezone', 'UTC')}",
            "",
            "**Target Coordinates**",
            f"  RA: {coordinates.get('ra_string', 'N/A')} ({coordinates.get('ra_degrees', 0):.6f}°)",
            f"  Dec: {coordinates.get('dec_string', 'N/A')} ({coordinates.get('dec_degrees', 0):.6f}°)",
            "",
            "**Current Status**",
            f"  Current Altitude: {observability.get('current_altitude', 0):.2f}°",
            f"  Current Azimuth: {observability.get('current_azimuth', 0):.2f}°",
            f"  Observable: {'✅ Yes' if observability.get('observable', False) else '❌ No'}",
            "",
            "**Constraints**",
            f"  Min Altitude: {constraints.get('min_altitude', 30):.1f}°",
            f"  Min Moon Separation: {constraints.get('min_moon_separation', 30):.1f}°",
            f"  Time Range: {constraints.get('time_range_hours', 24)} hours",
            "",
            "**Constraint Status**",
        ]

        constraints_satisfied = observability.get("constraints_satisfied", {})
        text_parts.extend(
            [
                f"  Altitude Constraint: {'✅' if constraints_satisfied.get('altitude', False) else '❌'}",
                f"  Moon Separation Constraint: {'✅' if constraints_satisfied.get('moon_separation', False) else '❌'}",
            ]
        )

        # 添加高度曲线信息
        altitude_curve = observability.get("altitude_curve", [])
        if altitude_curve:
            text_parts.extend(
                [
                    "",
                    "**Altitude Curve Summary**",
                    f"  Data Points: {len(altitude_curve)}",
                ]
            )

            # 找到最高点和最低点
            altitudes = [point.get("altitude", 0) for point in altitude_curve]
            if altitudes:
                max_alt = max(altitudes)
                min_alt = min(altitudes)
                text_parts.extend(
                    [
                        f"  Max Altitude: {max_alt:.2f}°",
                        f"  Min Altitude: {min_alt:.2f}°",
                    ]
                )

            # 统计可观测时间
            observable_points = sum(
                1 for point in altitude_curve if point.get("observable", False)
            )
            total_points = len(altitude_curve)
            if total_points > 0:
                observable_percentage = (observable_points / total_points) * 100
                text_parts.extend(
                    [
                        f"  Observable Time: {observable_percentage:.1f}% ({observable_points}/{total_points} time points)",
                    ]
                )

        return "\n".join(text_parts)


def main():
    """主函数，处理标准输入输出"""
    server = ObservabilityMCPServer()

    # 读取标准输入
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            continue
        except Exception as e:
            logger.error(f"处理请求时出错: {e}")
            continue


if __name__ == "__main__":
    main() 