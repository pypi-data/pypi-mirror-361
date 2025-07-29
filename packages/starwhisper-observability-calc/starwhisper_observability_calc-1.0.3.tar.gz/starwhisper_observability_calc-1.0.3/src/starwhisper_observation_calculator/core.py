"""
天文目标可观测性计算器
支持通过Simbad查询目标坐标，计算可观测性，并生成高度曲线
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import astropy.units as u
import numpy as np
from astroplan import (
    AltitudeConstraint,
    FixedTarget,
    MoonSeparationConstraint,
    Observer,
)
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_body
from astropy.time import Time
from astropy.utils import iers
from astroquery.simbad import Simbad

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置IERS数据
try:
    # 使用相对于包的路径
    import os
    package_dir = os.path.dirname(__file__)
    iers_file_path = os.path.join(package_dir, "..", "..", "finals2000A.all")
    if os.path.exists(iers_file_path):
        iers.conf.iers_file = iers_file_path
        iers.conf.auto_download = False
        iers.conf.auto_max_age = None
        iers.conf.iers_degraded_accuracy = "ignore"
except Exception as e:
    logger.warning(f"无法配置IERS文件: {e}")


class ObservabilityCalculator:
    """天文目标可观测性计算器"""

    def __init__(
        self,
        latitude: float = 40.393333,
        longitude: float = 117.575278,
        altitude: float = 900.0,
        timezone: str = "Asia/Shanghai",
    ):
        """
        初始化计算器

        Args:
            latitude: 观测站纬度（度）
            longitude: 观测站经度（度）
            altitude: 观测站海拔（米）
            timezone: 时区
        """
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.timezone = timezone

        # 创建观测站位置
        self.location = EarthLocation(
            lat=latitude * u.deg, lon=longitude * u.deg, height=altitude * u.m
        )
        self.observer = Observer(location=self.location, timezone=timezone)

        # 配置Simbad
        Simbad.add_votable_fields("coordinates")

    def calculate_observability(
        self,
        target_name: str,
        min_altitude: float = 30.0,
        min_moon_separation: float = 30.0,
        time_range_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        计算目标可观测性的主函数

        Args:
            target_name: 目标名称
            min_altitude: 最小地平高度（度）
            min_moon_separation: 最小月距（度）
            time_range_hours: 检查时间范围（小时）

        Returns:
            完整的可观测性信息
        """
        # 首先尝试查询Simbad
        success, ra_str, dec_str, ra_deg, dec_deg = self.query_simbad(target_name)

        if not success:
            # 如果Simbad查询失败，尝试作为太阳系天体处理
            success, ra_str, dec_str, ra_deg, dec_deg = self.get_body_position(
                target_name
            )

        if not success:
            return {
                "success": False,
                "error": f"无法找到目标: {target_name}",
                "target_name": target_name,
            }

        # 检查可观测性
        observability_info = self.check_observability(
            ra_deg, dec_deg, min_altitude, min_moon_separation, time_range_hours
        )

        return {
            "success": True,
            "target_name": target_name,
            "coordinates": {
                "ra_string": ra_str,
                "dec_string": dec_str,
                "ra_degrees": ra_deg,
                "dec_degrees": dec_deg,
            },
            "observability": observability_info,
            "observer_location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude": self.altitude,
                "timezone": self.timezone,
            },
            "constraints": {
                "min_altitude": min_altitude,
                "min_moon_separation": min_moon_separation,
                "time_range_hours": time_range_hours,
            },
        }

    def get_body_position(self, body_name: str) -> Tuple[bool, str, str, float, float]:
        """
        获取太阳系天体位置

        Args:
            body_name: 天体名称（如'sun', 'moon', 'mars'等）

        Returns:
            (可观测性, 赤经字符串, 赤纬字符串, 赤经度数, 赤纬度数)
        """
        try:
            current_time = Time.now()
            coord = get_body(body_name.lower(), current_time, self.location)

            if coord is None:
                return False, "", "", 0.0, 0.0

            ra = coord.ra
            dec = coord.dec

            # 格式化赤经
            ra_str = f"{ra.hms.h:02.0f}:{ra.hms.m:02.0f}:{ra.hms.s:05.2f}"
            ra_deg = ra.deg

            # 格式化赤纬
            sign = "-" if dec.dms.d < 0 else "+"
            abs_dec = abs(dec)
            dec_str = f"{sign}{abs_dec.dms.d:02.0f}:{abs_dec.dms.m:02.0f}:{abs_dec.dms.s:05.2f}"
            dec_deg = dec.deg

            return True, ra_str, dec_str, ra_deg, dec_deg

        except Exception as e:
            logger.error(f"获取天体位置时出错: {e}")
            return False, "", "", 0.0, 0.0

    def query_simbad(self, object_name: str) -> Tuple[bool, str, str, float, float]:
        """
        通过Simbad查询天体坐标

        Args:
            object_name: 天体名称

        Returns:
            (查询成功, 赤经字符串, 赤纬字符串, 赤经度数, 赤纬度数)
        """
        try:
            result_table = Simbad.query_object(object_name)

            if result_table is not None and len(result_table) > 0:
                ra_str = result_table["RA"][0]
                dec_str = result_table["DEC"][0]

                # 转换坐标格式
                ra_formatted, dec_formatted, ra_deg, dec_deg = (
                    self._convert_coordinates(ra_str, dec_str)
                )

                return True, ra_formatted, dec_formatted, ra_deg, dec_deg
            else:
                logger.warning(f"未找到天体: {object_name}")
                return False, "", "", 0.0, 0.0

        except Exception as e:
            logger.error(f"Simbad查询出错: {e}")
            return False, "", "", 0.0, 0.0

    def _convert_coordinates(self, ra: str, dec: str) -> Tuple[str, str, float, float]:
        """
        转换坐标格式

        Args:
            ra: 赤经字符串
            dec: 赤纬字符串

        Returns:
            (格式化赤经, 格式化赤纬, 赤经度数, 赤纬度数)
        """
        try:
            # 处理赤经
            ra_parts = ra.split()
            if len(ra_parts) == 3:
                ra_formatted = f"{ra_parts[0]}:{ra_parts[1]}:{ra_parts[2]}"
                ra_deg = (
                    int(ra_parts[0]) * 15
                    + int(ra_parts[1]) * 0.25
                    + float(ra_parts[2]) * 0.25 / 60
                )
            else:
                # 处理其他格式
                coord = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
                ra_formatted = f"{coord.ra.hms.h:02.0f}:{coord.ra.hms.m:02.0f}:{coord.ra.hms.s:05.2f}"
                ra_deg = coord.ra.deg

            # 处理赤纬
            dec_parts = dec.split()
            if len(dec_parts) == 3:
                dec_formatted = f"{dec_parts[0]}:{dec_parts[1]}:{dec_parts[2]}"
                sign = -1 if dec_parts[0].startswith("-") else 1
                dec_parts[0] = dec_parts[0].lstrip("-+")
                dec_deg = sign * (
                    int(dec_parts[0])
                    + int(dec_parts[1]) / 60
                    + float(dec_parts[2]) / 3600
                )
            else:
                # 处理其他格式
                coord = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
                sign = "-" if coord.dec.dms.d < 0 else "+"
                abs_dec = abs(coord.dec)
                dec_formatted = f"{sign}{abs_dec.dms.d:02.0f}:{abs_dec.dms.m:02.0f}:{abs_dec.dms.s:05.2f}"
                dec_deg = coord.dec.deg

            return ra_formatted, dec_formatted, ra_deg, dec_deg

        except Exception as e:
            logger.error(f"坐标转换出错: {e}")
            return "", "", 0.0, 0.0

    def check_observability(
        self,
        ra_deg: float,
        dec_deg: float,
        min_altitude: float = 30.0,
        min_moon_separation: float = 30.0,
        time_range_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        检查目标可观测性

        Args:
            ra_deg: 赤经（度）
            dec_deg: 赤纬（度）
            min_altitude: 最小地平高度（度）
            min_moon_separation: 最小月距（度）
            time_range_hours: 检查时间范围（小时）

        Returns:
            包含可观测性信息的字典
        """
        try:
            # 创建目标坐标
            coord = SkyCoord(ra_deg * u.deg, dec_deg * u.deg, frame="icrs")
            target = FixedTarget(coord, name="Target")

            # 设置时间范围
            start_time = Time.now()
            end_time = start_time + timedelta(hours=time_range_hours)

            # 设置约束条件
            constraints = [
                AltitudeConstraint(min=min_altitude * u.deg),
                MoonSeparationConstraint(min=min_moon_separation * u.deg),
            ]

            # 计算当前高度方位角
            altaz_frame = AltAz(obstime=start_time, location=self.location)
            target_altaz = coord.transform_to(altaz_frame)

            # 生成高度曲线
            altitude_curve = self._generate_altitude_curve(
                coord, start_time, end_time, min_altitude, min_moon_separation
            )

            # 检查是否可观测
            observable_count = sum(1 for p in altitude_curve if p.get("observable", False))
            is_observable = observable_count > 0

            return {
                "observable": bool(is_observable),
                "current_altitude": float(target_altaz.alt.deg),
                "current_azimuth": float(target_altaz.az.deg),
                "altitude_curve": altitude_curve,
                "constraints_satisfied": {
                    "altitude": target_altaz.alt.deg >= min_altitude,
                    "moon_separation": True,  # 将在高度曲线中详细计算
                },
            }

        except Exception as e:
            logger.error(f"检查可观测性时出错: {e}")
            return {
                "observable": False,
                "current_altitude": 0.0,
                "current_azimuth": 0.0,
                "altitude_curve": [],
                "error": str(e),
            }

    def _generate_altitude_curve(
        self,
        coord: SkyCoord,
        start_time: Time,
        end_time: Time,
        min_altitude: float,
        min_moon_separation: float,
    ) -> List[Dict[str, Any]]:
        """
        生成高度曲线

        Args:
            coord: 目标坐标
            start_time: 开始时间
            end_time: 结束时间
            min_altitude: 最小高度
            min_moon_separation: 最小月距

        Returns:
            高度曲线数据列表
        """
        try:
            # 生成时间网格
            time_grid = start_time + np.arange(0, 24, 0.5) * u.hour

            curve_data = []
            for t in time_grid:
                if t > end_time:
                    break

                # 计算高度方位角
                altaz_frame = AltAz(obstime=t, location=self.location)
                target_altaz = coord.transform_to(altaz_frame)

                # 计算月距
                moon = get_body("moon", t, self.location)
                moon_separation = coord.separation(moon)

                # 检查约束条件
                altitude_ok = target_altaz.alt.deg >= min_altitude
                moon_ok = moon_separation.deg >= min_moon_separation

                curve_data.append(
                    {
                        "time": t.iso,
                        "altitude": float(target_altaz.alt.deg),
                        "azimuth": float(target_altaz.az.deg),
                        "moon_separation": float(moon_separation.deg),
                        "observable": altitude_ok and moon_ok,
                    }
                )

            return curve_data

        except Exception as e:
            logger.error(f"生成高度曲线时出错: {e}")
            return []


# MCP服务器接口函数
def calculate_target_observability(
    latitude: float,
    longitude: float,
    target_name: str,
    altitude: float = 0.0,
    min_altitude: float = 30.0,
    min_moon_separation: float = 30.0,
    time_range_hours: int = 24,
) -> Dict[str, Any]:
    """
    MCP服务器接口函数

    Args:
        latitude: 观测站纬度（度）
        longitude: 观测站经度（度）
        target_name: 目标名称
        altitude: 观测站海拔（米）
        min_altitude: 最小地平高度（度）
        min_moon_separation: 最小月距（度）
        time_range_hours: 检查时间范围（小时）

    Returns:
        可观测性计算结果
    """
    try:
        calculator = ObservabilityCalculator(
            latitude=latitude, longitude=longitude, altitude=altitude
        )

        result = calculator.calculate_observability(
            target_name=target_name,
            min_altitude=min_altitude,
            min_moon_separation=min_moon_separation,
            time_range_hours=time_range_hours,
        )

        return result

    except Exception as e:
        logger.error(f"MCP接口函数出错: {e}")
        return {"success": False, "error": str(e), "target_name": target_name} 