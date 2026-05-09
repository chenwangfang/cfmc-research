#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键运行第1-4章全部图表生成脚本
按编号顺序执行，输出到各脚本所在目录
兼容WSL和Windows环境
"""

import os
import sys
import subprocess
import time
import platform

# 设置Windows控制台UTF-8编码
if platform.system() == 'Windows':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except:
        pass

# 检测是否支持Unicode符号（Windows CMD可能不支持）
def get_status_symbols():
    """根据环境返回合适的状态符号"""
    if platform.system() == 'Windows':
        # Windows下使用ASCII兼容符号
        return {'success': '[OK]', 'fail': '[FAIL]'}
    else:
        # Linux/WSL使用Unicode符号
        return {'success': '✓ 成功', 'fail': '✗ 失败'}

SYMBOLS = get_status_symbols()

# 脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 图表脚本列表（按章节顺序）
FIGURE_SCRIPTS = [
    "图1.py",
    "图2.py",
    "图3.py",
    "图4.py",
    "图5.py",
    "图6.py",
    "图7.py",
    "图8.py",
    "图9.py",
    "图10.py",
]

def run_script(script_name):
    """运行单个脚本"""
    script_path = os.path.join(SCRIPT_DIR, script_name)

    if not os.path.exists(script_path):
        return False, f"文件不存在: {script_path}"

    try:
        # 设置环境变量确保子进程使用UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        result = subprocess.run(
            [sys.executable, script_path],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # 替换无法解码的字符
            timeout=120,  # 2分钟超时
            env=env
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr or result.stdout

    except subprocess.TimeoutExpired:
        return False, "执行超时（超过2分钟）"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("第1-4章图表生成脚本批量运行")
    print("=" * 60)
    print(f"运行环境: {platform.system()}")
    print(f"脚本目录: {SCRIPT_DIR}")
    print(f"待运行脚本数: {len(FIGURE_SCRIPTS)}")
    print("=" * 60)

    success_count = 0
    fail_count = 0
    results = []

    start_time = time.time()

    for i, script_name in enumerate(FIGURE_SCRIPTS, 1):
        print(f"\n[{i}/{len(FIGURE_SCRIPTS)}] 运行: {script_name}")
        print("-" * 40)

        success, output = run_script(script_name)

        if success:
            success_count += 1
            status = SYMBOLS['success']
            # 显示保存信息
            for line in output.split('\n'):
                if '已保存' in line or 'saved' in line.lower():
                    print(f"  {line}")
        else:
            fail_count += 1
            status = SYMBOLS['fail']
            print(f"  错误: {output[:200]}")

        results.append((script_name, success))
        print(f"  状态: {status}")

    elapsed = time.time() - start_time

    # 汇总报告
    print("\n" + "=" * 60)
    print("运行汇总")
    print("=" * 60)
    print(f"总计: {len(FIGURE_SCRIPTS)} 个脚本")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"耗时: {elapsed:.1f} 秒")
    print("=" * 60)

    if fail_count > 0:
        print("\n失败的脚本:")
        for name, success in results:
            if not success:
                print(f"  - {name}")

    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
