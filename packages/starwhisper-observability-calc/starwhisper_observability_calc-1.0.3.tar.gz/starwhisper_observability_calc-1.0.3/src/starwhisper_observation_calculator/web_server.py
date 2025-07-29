"""
Web服务器模块
提供RESTful API和Web界面
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    BaseModel = None
    Field = None

from .core import calculate_target_observability, ObservabilityCalculator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 只在FastAPI可用时定义这些类
if FASTAPI_AVAILABLE:
    class ObservabilityRequest(BaseModel):
        """可观测性请求模型"""
        latitude: float = Field(..., description="观测站纬度（度）", ge=-90, le=90)
        longitude: float = Field(..., description="观测站经度（度）", ge=-180, le=180)
        target_name: str = Field(..., description="目标名称")
        altitude: float = Field(900.0, description="观测站海拔（米）")
        min_altitude: float = Field(30.0, description="最小地平高度（度）", ge=0, le=90)
        min_moon_separation: float = Field(30.0, description="最小月距（度）", ge=0, le=180)
        time_range_hours: int = Field(24, description="检查时间范围（小时）", ge=1, le=168)


    class BatchObservabilityRequest(BaseModel):
        """批量可观测性请求模型"""
        requests: List[ObservabilityRequest] = Field(..., description="请求列表")


def create_web_app() -> FastAPI:
    """创建FastAPI应用"""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not available. Please install with: pip install 'starwhisper-observation-calculator[web]'")
    
    app = FastAPI(
        title="StarWhisper Observatory Calculator",
        description="天文可观测性计算器 Web API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        """主页"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StarWhisper Observatory Calculator</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .container { max-width: 800px; margin: 0 auto; }
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; }
                input, select { width: 100%; padding: 8px; margin-bottom: 10px; }
                button { background-color: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
                button:hover { background-color: #0056b3; }
                .result { margin-top: 20px; padding: 20px; border: 1px solid #ddd; background-color: #f9f9f9; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌟 StarWhisper Observatory Calculator</h1>
                <p>天文可观测性计算器 - 计算天文目标的可观测性</p>
                
                <form id="calcForm">
                    <div class="form-group">
                        <label for="target_name">目标名称：</label>
                        <input type="text" id="target_name" name="target_name" value="Vega" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="latitude">纬度（度）：</label>
                        <input type="number" id="latitude" name="latitude" value="40.393333" step="0.000001" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="longitude">经度（度）：</label>
                        <input type="number" id="longitude" name="longitude" value="117.575278" step="0.000001" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="altitude">海拔（米）：</label>
                        <input type="number" id="altitude" name="altitude" value="900" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="min_altitude">最小地平高度（度）：</label>
                        <input type="number" id="min_altitude" name="min_altitude" value="30" min="0" max="90" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="min_moon_separation">最小月距（度）：</label>
                        <input type="number" id="min_moon_separation" name="min_moon_separation" value="30" min="0" max="180" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="time_range_hours">检查时间范围（小时）：</label>
                        <input type="number" id="time_range_hours" name="time_range_hours" value="24" min="1" max="168" required>
                    </div>
                    
                    <button type="submit">计算可观测性</button>
                </form>
                
                <div id="result" class="result" style="display: none;"></div>
                
                <div style="margin-top: 40px;">
                    <h3>API 文档</h3>
                    <p><a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a></p>
                </div>
            </div>
            
            <script>
                document.getElementById('calcForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    
                    // 转换数值类型
                    data.latitude = parseFloat(data.latitude);
                    data.longitude = parseFloat(data.longitude);
                    data.altitude = parseFloat(data.altitude);
                    data.min_altitude = parseFloat(data.min_altitude);
                    data.min_moon_separation = parseFloat(data.min_moon_separation);
                    data.time_range_hours = parseInt(data.time_range_hours);
                    
                    try {
                        const response = await fetch('/observability', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data),
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                        } else {
                            document.getElementById('result').innerHTML = '<div class="error">错误: ' + result.detail + '</div>';
                        }
                        
                        document.getElementById('result').style.display = 'block';
                    } catch (error) {
                        document.getElementById('result').innerHTML = '<div class="error">网络错误: ' + error.message + '</div>';
                        document.getElementById('result').style.display = 'block';
                    }
                });
            </script>
        </body>
        </html>
        """

    @app.post("/observability", response_model=Dict[str, Any])
    async def calculate_observability(request: ObservabilityRequest):
        """计算单个目标的可观测性"""
        try:
            result = calculate_target_observability(
                latitude=request.latitude,
                longitude=request.longitude,
                target_name=request.target_name,
                altitude=request.altitude,
                min_altitude=request.min_altitude,
                min_moon_separation=request.min_moon_separation,
                time_range_hours=request.time_range_hours,
            )
            return result
        except Exception as e:
            logger.error(f"计算可观测性时出错: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/observability/batch", response_model=List[Dict[str, Any]])
    async def calculate_observability_batch(request: BatchObservabilityRequest):
        """批量计算可观测性"""
        results = []
        for req in request.requests:
            try:
                result = calculate_target_observability(
                    latitude=req.latitude,
                    longitude=req.longitude,
                    target_name=req.target_name,
                    altitude=req.altitude,
                    min_altitude=req.min_altitude,
                    min_moon_separation=req.min_moon_separation,
                    time_range_hours=req.time_range_hours,
                )
                results.append(result)
            except Exception as e:
                logger.error(f"批量计算出错: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "target_name": req.target_name
                })
        return results

    @app.get("/targets/supported", response_model=Dict[str, List[str]])
    async def get_supported_targets():
        """获取支持的目标列表"""
        return {
            "solar_system": [
                "sun", "moon", "mercury", "venus", "mars", 
                "jupiter", "saturn", "uranus", "neptune", "pluto"
            ],
            "stars": [
                "vega", "sirius", "polaris", "rigel", "betelgeuse", 
                "altair", "deneb", "arcturus", "spica", "antares"
            ],
            "deep_sky": [
                "m31", "m42", "m13", "m57", "m27", "m51", "m104", "m87"
            ]
        }

    @app.get("/observatories", response_model=Dict[str, Dict[str, float]])
    async def get_observatories():
        """获取预设观测站"""
        return {
            "兴隆观测站": {
                "latitude": 40.393333,
                "longitude": 117.575278,
                "altitude": 900.0
            },
            "新昌观测站": {
                "latitude": 29.501784,
                "longitude": 120.905740,
                "altitude": 0.0
            },
            "帕洛马天文台": {
                "latitude": 33.3563,
                "longitude": -116.8650,
                "altitude": 1712.0
            }
        }

    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    return app


def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """运行Web服务器"""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not available. Please install with: pip install 'starwhisper-observation-calculator[web]'")
    
    app = create_web_app()
    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_server() 