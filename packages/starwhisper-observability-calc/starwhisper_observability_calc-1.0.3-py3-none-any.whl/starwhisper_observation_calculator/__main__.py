"""
StarWhisper Observatory Calculator 主入口点
支持通过 python -m starwhisper_observation_calculator 运行
"""

import sys
from .cli import main_calculator


if __name__ == "__main__":
    main_calculator() 