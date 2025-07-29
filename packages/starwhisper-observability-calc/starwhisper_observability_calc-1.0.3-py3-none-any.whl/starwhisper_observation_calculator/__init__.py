"""
StarWhisper Observatory Calculator

一个用于计算天文目标可观测性的Python包，支持恒星、深空天体和太阳系天体。
提供MCP（Model Context Protocol）服务接口，可与支持MCP的AI助手集成。

作者: Cunshi Wang
邮箱: wangcunshi@nao.cas.cn
许可证: MIT
"""

from .core import ObservabilityCalculator, calculate_target_observability
from .mcp_server import ObservabilityMCPServer

__version__ = "1.0.3"
__author__ = "Cunshi Wang"
__email__ = "wangcunshi@nao.cas.cn"
__license__ = "MIT"

# 只在FastAPI可用时导入web_server
def get_web_app():
    """获取web应用，需要安装web依赖"""
    from .web_server import create_web_app
    return create_web_app()

__all__ = [
    "ObservabilityCalculator",
    "calculate_target_observability", 
    "ObservabilityMCPServer",
    "get_web_app",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
] 