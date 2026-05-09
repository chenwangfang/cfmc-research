#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q3_07_假设汇总.py

兼容入口。当前Q3假设汇总已经切换到PLS-SEM/PLS-MGA口径，
权威脚本为同目录下的 Q3_07_PLS_假设汇总.py。

保留本文件只是为了兼容旧命令，避免继续生成旧协方差SEM和
测量不变性口径的报告。
"""

from pathlib import Path
import runpy
import sys


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    """转发到当前权威的PLS假设汇总脚本。"""
    target = Path(__file__).with_name("Q3_07_PLS_假设汇总.py")
    if not target.exists():
        raise FileNotFoundError(f"未找到当前权威脚本: {target}")

    print("Q3_07_假设汇总.py 为兼容入口，正在调用 Q3_07_PLS_假设汇总.py")
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
