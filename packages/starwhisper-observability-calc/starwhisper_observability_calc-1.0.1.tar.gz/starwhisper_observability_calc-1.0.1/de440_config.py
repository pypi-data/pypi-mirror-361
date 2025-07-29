"""
DE440星表配置文件
提供更高精度的太阳系天体位置计算
"""

import os

from astropy.coordinates import solar_system_ephemeris


def setup_de440_ephemeris(ephemeris_file: str = None):
    """
    设置DE440星表

    Args:
        ephemeris_file: DE440.bsp文件路径，如果为None则使用默认路径
    """
    try:
        if ephemeris_file is None:
            # 查找DE440.bsp文件
            possible_paths = [
                "de440.bsp",
                "DE440.bsp",
                "data/de440.bsp",
                "ephemerides/de440.bsp",
                os.path.expanduser("~/de440.bsp"),
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    ephemeris_file = path
                    break

        if ephemeris_file and os.path.exists(ephemeris_file):
            # 设置DE440星表
            solar_system_ephemeris.set("de440")
            print(f"✅ 已设置DE440星表: {ephemeris_file}")
            return True
        else:
            print("⚠️  未找到DE440.bsp文件，使用默认星表")
            print("   请下载DE440.bsp文件并放置在以下位置之一:")
            for path in ["de440.bsp", "data/de440.bsp", "ephemerides/de440.bsp"]:
                print(f"   - {path}")
            return False

    except Exception as e:
        print(f"❌ 设置DE440星表时出错: {e}")
        return False


def get_available_ephemerides():
    """
    获取可用的星表列表

    Returns:
        可用星表列表
    """
    try:
        # 获取当前星表
        current = solar_system_ephemeris.get()

        # 获取所有可用星表
        available = solar_system_ephemeris.available_ephemerides()

        return {"current": current, "available": available}
    except Exception as e:
        print(f"❌ 获取星表信息时出错: {e}")
        return {"current": "unknown", "available": []}


def download_de440_ephemeris(download_dir: str = "."):
    """
    下载DE440星表（需要网络连接）

    Args:
        download_dir: 下载目录

    Returns:
        是否下载成功
    """
    try:
        import urllib.error
        import urllib.request

        # DE440.bsp下载URL（示例）
        url = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp"

        output_path = os.path.join(download_dir, "de440.bsp")

        print(f"📥 正在下载DE440星表...")
        print(f"   从: {url}")
        print(f"   到: {output_path}")

        # 创建目录
        os.makedirs(download_dir, exist_ok=True)

        # 下载文件
        urllib.request.urlretrieve(url, output_path)

        print("✅ DE440星表下载完成")
        return True

    except urllib.error.URLError as e:
        print(f"❌ 下载失败: {e}")
        print("   请手动下载DE440.bsp文件")
        return False
    except Exception as e:
        print(f"❌ 下载过程中出错: {e}")
        return False


def compare_ephemeris_accuracy():
    """
    比较不同星表的精度

    Returns:
        精度比较结果
    """
    try:
        from astropy.coordinates import get_body
        from astropy.time import Time

        # 测试时间
        test_time = Time("2024-01-01T00:00:00")

        # 测试天体
        test_bodies = ["sun", "moon", "mars", "jupiter"]

        results = {}

        # 测试默认星表
        print("🔍 测试默认星表精度...")
        default_results = {}
        for body in test_bodies:
            try:
                coord = get_body(body, test_time)
                default_results[body] = {"ra": coord.ra.deg, "dec": coord.dec.deg}
            except Exception as e:
                default_results[body] = {"error": str(e)}

        results["default"] = default_results

        # 尝试测试DE440星表
        if setup_de440_ephemeris():
            print("🔍 测试DE440星表精度...")
            de440_results = {}
            for body in test_bodies:
                try:
                    coord = get_body(body, test_time)
                    de440_results[body] = {"ra": coord.ra.deg, "dec": coord.dec.deg}
                except Exception as e:
                    de440_results[body] = {"error": str(e)}

            results["de440"] = de440_results

            # 比较精度
            print("\n📊 精度比较:")
            for body in test_bodies:
                if body in default_results and body in de440_results:
                    if (
                        "error" not in default_results[body]
                        and "error" not in de440_results[body]
                    ):
                        ra_diff = abs(
                            default_results[body]["ra"] - de440_results[body]["ra"]
                        )
                        dec_diff = abs(
                            default_results[body]["dec"] - de440_results[body]["dec"]
                        )
                        print(
                            f"   {body}: RA差异={ra_diff:.6f}°, Dec差异={dec_diff:.6f}°"
                        )

        return results

    except Exception as e:
        print(f"❌ 比较星表精度时出错: {e}")
        return {}


if __name__ == "__main__":
    print("🚀 DE440星表配置工具")
    print("=" * 40)

    # 显示当前星表信息
    print("\n1. 当前星表信息:")
    info = get_available_ephemerides()
    print(f"   当前星表: {info['current']}")
    print(f"   可用星表: {', '.join(info['available'])}")

    # 尝试设置DE440星表
    print("\n2. 设置DE440星表:")
    success = setup_de440_ephemeris()

    # 比较精度
    print("\n3. 精度比较:")
    compare_ephemeris_accuracy()

    print("\n" + "=" * 40)
    print("✅ 配置完成！")
