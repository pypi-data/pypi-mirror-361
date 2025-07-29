"""
命令行接口模块
提供observability-calculator, observability-mcp, observability-web等命令
"""

import argparse
import sys
from typing import Optional

from .core import calculate_target_observability
from .mcp_server import ObservabilityMCPServer


def main_calculator():
    """主计算器命令行入口"""
    parser = argparse.ArgumentParser(
        description="StarWhisper Observatory Calculator - 天文可观测性计算器"
    )
    
    parser.add_argument("target_name", help="目标名称 (如 'Vega', 'moon', 'M31')")
    parser.add_argument("--latitude", type=float, default=40.393333, 
                       help="观测站纬度 (度，默认兴隆观测站)")
    parser.add_argument("--longitude", type=float, default=117.575278,
                       help="观测站经度 (度，默认兴隆观测站)")
    parser.add_argument("--altitude", type=float, default=900.0,
                       help="观测站海拔 (米，默认900)")
    parser.add_argument("--min-altitude", type=float, default=30.0,
                       help="最小地平高度 (度，默认30)")
    parser.add_argument("--min-moon-separation", type=float, default=30.0,
                       help="最小月距 (度，默认30)")
    parser.add_argument("--time-range-hours", type=int, default=24,
                       help="检查时间范围 (小时，默认24)")
    
    args = parser.parse_args()
    
    try:
        result = calculate_target_observability(
            latitude=args.latitude,
            longitude=args.longitude,
            target_name=args.target_name,
            altitude=args.altitude,
            min_altitude=args.min_altitude,
            min_moon_separation=args.min_moon_separation,
            time_range_hours=args.time_range_hours
        )
        
        if result.get("success", False):
            print(_format_result(result))
        else:
            print(f"错误: {result.get('error', '未知错误')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"计算失败: {e}")
        sys.exit(1)


def main_mcp():
    """MCP服务器命令行入口"""
    parser = argparse.ArgumentParser(
        description="StarWhisper MCP Server - 天文可观测性MCP服务器"
    )
    
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志级别
    import logging
    logging.basicConfig(level=getattr(logging, args.log_level))
    
    # 启动MCP服务器
    server = ObservabilityMCPServer()
    
    # 处理标准输入输出
    import json
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        except json.JSONDecodeError as e:
            continue
        except Exception as e:
            continue


def main_web():
    """Web服务器命令行入口"""
    parser = argparse.ArgumentParser(
        description="StarWhisper Web Server - 天文可观测性Web服务器"
    )
    
    parser.add_argument("--host", default="127.0.0.1",
                       help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000,
                       help="服务器端口")
    parser.add_argument("--reload", action="store_true",
                       help="开启自动重载")
    
    args = parser.parse_args()
    
    try:
        import uvicorn
        from .web_server import create_web_app
        app = create_web_app()
        uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
    except ImportError:
        print("错误: 需要安装web依赖。请运行: pip install 'starwhisper-observation-calculator[web]'")
        sys.exit(1)
    except Exception as e:
        print(f"启动Web服务器失败: {e}")
        sys.exit(1)


def main():
    """统一入口点，支持uvx直接运行"""
    parser = argparse.ArgumentParser(
        description="StarWhisper Observatory Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令:
  默认          启动MCP服务器
  --calculator  启动计算器模式
  --web         启动Web服务器
  --mcp         启动MCP服务器（显式）

示例:
  uvx starwhisper-observation-calculator
  uvx starwhisper-observation-calculator --calculator Vega
  uvx starwhisper-observation-calculator --web --port 8080
        """
    )
    
    parser.add_argument("--calculator", metavar="TARGET", 
                       help="计算器模式 - 计算指定目标的可观测性")
    parser.add_argument("--web", action="store_true",
                       help="启动Web服务器")
    parser.add_argument("--mcp", action="store_true",
                       help="启动MCP服务器（默认模式）")
    
    # Web服务器参数
    parser.add_argument("--host", default="127.0.0.1",
                       help="Web服务器主机地址")
    parser.add_argument("--port", type=int, default=8000,
                       help="Web服务器端口")
    parser.add_argument("--reload", action="store_true",
                       help="Web服务器自动重载")
    
    # 计算器参数
    parser.add_argument("--latitude", type=float, default=40.393333,
                       help="观测站纬度")
    parser.add_argument("--longitude", type=float, default=117.575278,
                       help="观测站经度")
    parser.add_argument("--altitude", type=float, default=900.0,
                       help="观测站海拔")
    parser.add_argument("--min-altitude", type=float, default=30.0,
                       help="最小地平高度")
    parser.add_argument("--min-moon-separation", type=float, default=30.0,
                       help="最小月距")
    parser.add_argument("--time-range-hours", type=int, default=24,
                       help="检查时间范围")
    
    # 通用参数
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    import logging
    logging.basicConfig(level=getattr(logging, args.log_level))
    
    # 路由到相应的功能
    if args.calculator:
        # 计算器模式
        try:
            result = calculate_target_observability(
                latitude=args.latitude,
                longitude=args.longitude,
                target_name=args.calculator,
                altitude=args.altitude,
                min_altitude=args.min_altitude,
                min_moon_separation=args.min_moon_separation,
                time_range_hours=args.time_range_hours
            )
            
            if result.get("success", False):
                print(_format_result(result))
            else:
                print(f"错误: {result.get('error', '未知错误')}")
                sys.exit(1)
                
        except Exception as e:
            print(f"计算失败: {e}")
            sys.exit(1)
            
    elif args.web:
        # Web服务器模式
        try:
            import uvicorn
            from .web_server import create_web_app
            app = create_web_app()
            print(f"🌐 启动Web服务器: http://{args.host}:{args.port}")
            uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
        except ImportError:
            print("错误: 需要安装web依赖。请运行: uvx --with 'starwhisper-observation-calculator[web]' starwhisper-observation-calculator --web")
            sys.exit(1)
        except Exception as e:
            print(f"启动Web服务器失败: {e}")
            sys.exit(1)
            
    else:
        # 默认MCP服务器模式
        server = ObservabilityMCPServer()
        
        # 处理标准输入输出
        import json
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = server.handle_request(request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                continue
            except Exception as e:
                continue


def _format_result(result):
    """格式化结果输出"""
    if not result.get("success", False):
        return f"计算失败: {result.get('error', '未知错误')}"

    target_name = result.get("target_name", "未知目标")
    coordinates = result.get("coordinates", {})
    observability = result.get("observability", {})
    observer_location = result.get("observer_location", {})
    
    lines = [
        f"🌟 {target_name} 可观测性分析报告",
        "",
        f"📍 观测站: {observer_location.get('latitude', 0):.6f}°, {observer_location.get('longitude', 0):.6f}°, {observer_location.get('altitude', 0):.1f}m",
        f"🌌 坐标: {coordinates.get('ra_string', 'N/A')}, {coordinates.get('dec_string', 'N/A')}",
        f"📊 当前高度: {observability.get('current_altitude', 0):.2f}°",
        f"🧭 当前方位: {observability.get('current_azimuth', 0):.2f}°",
        f"✅ 可观测性: {'可观测' if observability.get('observable', False) else '不可观测'}",
        "",
        "🎯 约束条件检查:",
    ]
    
    constraints_satisfied = observability.get("constraints_satisfied", {})
    lines.extend([
        f"  高度约束: {'✅ 满足' if constraints_satisfied.get('altitude', False) else '❌ 不满足'}",
        f"  月距约束: {'✅ 满足' if constraints_satisfied.get('moon_separation', False) else '❌ 不满足'}",
    ])
    
    return "\n".join(lines)


if __name__ == "__main__":
    main() 