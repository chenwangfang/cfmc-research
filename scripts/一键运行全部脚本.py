#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键运行全部脚本
================
汉语系表隐喻构式统计分析脚本批量运行工具

功能：
- 按正确顺序运行Q1、Q2、Q3全部分析脚本及独立图表脚本
- 显示运行进度和状态
- 捕获错误并生成运行日志
- 统计各脚本运行时间

使用方法：
    python3 一键运行全部脚本.py [选项]

选项：
    --q1    仅运行Q1模块
    --q2    仅运行Q2模块
    --q3    仅运行Q3模块
    --dry   仅显示运行计划，不实际执行

创建日期：2025-12-05
"""

import subprocess
import sys
import os
import time
from datetime import datetime
from pathlib import Path


# =============================================================================
# 配置
# =============================================================================

# 脚本运行顺序定义
SCRIPTS = {
    'Q1': [
        ('Q1_01_描述统计.py', '认知通达度与映射类型描述统计'),
        ('Q1_02_H1_1相关分析.py', 'H1-1假设验证：双维度相关分析'),
        ('Q1_03_GMM聚类.py', 'GMM聚类识别12类构式'),
        ('Q1_04_LDA判别.py', 'LDA判别分析验证聚类结果'),
        ('Q1_05_原型梯度.py', '马氏距离计算与原型梯度划分'),
        ('Q1_06_类型特征.py', '12类构式详细特征分析'),
        ('Q1_07_假设汇总.py', 'Q1假设验证结果汇总'),
    ],
    'Q2': [
        ('Q2_01_网络构建.py', '构建两层构式网络'),
        ('Q2_02_小世界检验.py', 'H2假设验证：小世界性质检验'),
        ('Q2_03_链接分析.py', '四类链接关系分布分析'),
        ('Q2_04_中心性分析.py', '三类中心性指标计算'),
        ('Q2_05_模块检测.py', 'Louvain社区检测'),
        ('Q2_06_度分布.py', '网络度分布分析'),
        ('Q2_07_网络可视化.py', '构式网络可视化'),
        ('Q2_08_整合分析.py', 'Q2整合分析与假设汇总'),
    ],
    'Q3': [
        ('Q3_01_描述统计.py', 'SEM变量描述统计'),
        ('Q3_02_SEM基础模型.py', 'SEM模型拟合与模型比较'),
        ('Q3_03_SEM完整模型.py', '路径系数与效度检验'),
        ('Q3_04_多组比较.py', '测量不变性检验'),
        ('Q3_05_中介效应.py', 'Bootstrap中介效应检验'),
        ('Q3_06_调节效应.py', '汉语认知特色调节效应'),
        ('Q3_07_假设汇总.py', 'Q3假设验证结果汇总'),
    ],
    '综合': [
        ('综合分析报告.py', 'Q1-Q3综合分析报告生成'),
    ],
    '图表': [
        ('图31_整合关系示意图.py', 'Q2与Q1/Q3整合关系示意图'),
        ('图35_路径系数比较图.py', 'Q3总体路径系数比较'),
        ('图39_Q1Q2Q3整合框架图.py', 'Q1-Q2-Q3研究发现整合框架'),
        ('图40_本研究与相关理论关系图.py', '本研究与相关理论关系'),
        ('图41_Sullivan理论修补层级图.py', 'Sullivan理论修补层级'),
    ]
}

# 模块描述
MODULE_DESC = {
    'Q1': '类型体系分析（第5章）',
    'Q2': '网络组织分析（第6章）',
    'Q3': '认知机制分析（第7章）',
    '综合': '综合分析报告',
    '图表': '独立图表生成（第6/8/9章）',
}


# =============================================================================
# 工具函数
# =============================================================================

def get_terminal_width():
    """获取终端宽度"""
    try:
        return os.get_terminal_size().columns
    except:
        return 80


def print_header(text, char='='):
    """打印标题"""
    width = get_terminal_width()
    print()
    print(char * width)
    print(f" {text}")
    print(char * width)


def print_subheader(text, char='-'):
    """打印子标题"""
    width = get_terminal_width()
    print()
    print(char * width)
    print(f" {text}")
    print(char * width)


def format_time(seconds):
    """格式化时间"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}分{secs:.1f}秒"


def print_progress(current, total, script_name, status='运行中'):
    """打印进度"""
    bar_width = 30
    progress = current / total
    filled = int(bar_width * progress)
    bar = '█' * filled + '░' * (bar_width - filled)
    print(f"\r[{bar}] {current}/{total} ({progress*100:.0f}%) {status}: {script_name}", end='', flush=True)


def run_script(script_path, script_dir):
    """运行单个脚本"""
    try:
        # 使用UTF-8编码以支持中文输出（解决Windows cp1252编码问题）
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=script_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # 遇到无法解码的字符时替换而非报错
            timeout=600  # 10分钟超时
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': '脚本执行超时（超过10分钟）',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }


# =============================================================================
# 主运行逻辑
# =============================================================================

def run_module(module_name, scripts, script_dir, dry_run=False):
    """运行单个模块的所有脚本"""
    results = []
    total = len(scripts)

    print_subheader(f"模块 {module_name}：{MODULE_DESC[module_name]} ({total}个脚本)")

    for i, (script_name, description) in enumerate(scripts, 1):
        script_path = script_dir / script_name

        # 检查脚本是否存在
        if not script_path.exists():
            print(f"\n  [{i}/{total}] [X] {script_name}")
            print(f"          错误：脚本文件不存在")
            results.append({
                'script': script_name,
                'description': description,
                'success': False,
                'time': 0,
                'error': '脚本文件不存在'
            })
            continue

        if dry_run:
            print(f"  [{i}/{total}] ○ {script_name}")
            print(f"          {description}")
            results.append({
                'script': script_name,
                'description': description,
                'success': True,
                'time': 0,
                'error': None,
                'dry_run': True
            })
            continue

        # 运行脚本
        print(f"\n  [{i}/{total}] ◐ {script_name} ... ", end='', flush=True)

        start_time = time.time()
        result = run_script(script_path, script_dir)
        elapsed = time.time() - start_time

        if result['success']:
            print(f"[OK] 完成 ({format_time(elapsed)})")
        else:
            print(f"[X] 失败 ({format_time(elapsed)})")
            if result['stderr']:
                # 只显示错误的最后几行
                error_lines = result['stderr'].strip().split('\n')
                error_summary = '\n'.join(error_lines[-3:]) if len(error_lines) > 3 else result['stderr'].strip()
                print(f"          错误: {error_summary[:200]}")

        results.append({
            'script': script_name,
            'description': description,
            'success': result['success'],
            'time': elapsed,
            'error': result['stderr'] if not result['success'] else None
        })

    return results


def run_all(modules_to_run, dry_run=False):
    """运行指定的所有模块"""
    # 获取脚本目录
    script_dir = Path(__file__).parent.resolve()

    # 开始时间
    total_start = time.time()

    # 打印欢迎信息
    print_header("汉语系表隐喻构式统计分析 - 批量运行工具")
    print(f"\n  运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  脚本目录: {script_dir}")
    print(f"  运行模块: {', '.join(modules_to_run)}")
    print(f"  运行模式: {'预览模式（不实际执行）' if dry_run else '正式运行'}")

    # 统计总脚本数
    total_scripts = sum(len(SCRIPTS[m]) for m in modules_to_run)
    print(f"  脚本总数: {total_scripts}个")

    # 运行各模块
    all_results = {}
    for module in modules_to_run:
        if module in SCRIPTS:
            all_results[module] = run_module(module, SCRIPTS[module], script_dir, dry_run)

    # 总耗时
    total_elapsed = time.time() - total_start

    # 打印汇总报告
    print_header("运行结果汇总")

    total_success = 0
    total_failed = 0

    for module, results in all_results.items():
        success = sum(1 for r in results if r['success'])
        failed = len(results) - success
        total_success += success
        total_failed += failed

        status = "[OK] 全部成功" if failed == 0 else f"[X] {failed}个失败"
        module_time = sum(r['time'] for r in results)

        print(f"\n  {module} {MODULE_DESC[module]}")
        print(f"      状态: {status}")
        print(f"      耗时: {format_time(module_time)}")

        # 显示失败的脚本
        if failed > 0:
            print("      失败脚本:")
            for r in results:
                if not r['success']:
                    print(f"        - {r['script']}")

    # 总结
    print_subheader("总计")
    print(f"\n  成功: {total_success}个")
    print(f"  失败: {total_failed}个")
    print(f"  总耗时: {format_time(total_elapsed)}")

    if total_failed == 0:
        print("\n  [OK] 全部脚本运行成功！")
    else:
        print(f"\n  [X] 有{total_failed}个脚本运行失败，请检查错误信息。")

    # 生成日志文件
    if not dry_run:
        log_path = script_dir.parent / '结果_输出' / f'运行日志_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"汉语系表隐喻构式统计分析 - 运行日志\n")
                f.write(f"{'='*60}\n\n")
                f.write(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总耗时: {format_time(total_elapsed)}\n")
                f.write(f"成功: {total_success}个, 失败: {total_failed}个\n\n")

                for module, results in all_results.items():
                    f.write(f"\n{module} {MODULE_DESC[module]}\n")
                    f.write(f"{'-'*40}\n")
                    for r in results:
                        status = "[OK]" if r['success'] else "[X]"
                        f.write(f"  {status} {r['script']} ({format_time(r['time'])})\n")
                        if r['error']:
                            f.write(f"      错误: {r['error'][:500]}\n")

            print(f"\n  日志已保存: {log_path}")
        except Exception as e:
            print(f"\n  日志保存失败: {e}")

    print()

    return total_failed == 0


# =============================================================================
# 命令行入口
# =============================================================================

def main():
    """主函数"""
    # 解析命令行参数
    args = sys.argv[1:]

    modules_to_run = []
    dry_run = False

    if '--dry' in args:
        dry_run = True
        args.remove('--dry')

    if '--q1' in args:
        modules_to_run.append('Q1')
    if '--q2' in args:
        modules_to_run.append('Q2')
    if '--q3' in args:
        modules_to_run.append('Q3')
    if '--综合' in args or '--summary' in args:
        modules_to_run.append('综合')
    if '--图表' in args or '--figures' in args:
        modules_to_run.append('图表')

    # 如果没有指定模块，运行全部（包括综合报告）
    if not modules_to_run:
        modules_to_run = ['Q1', 'Q2', 'Q3', '综合', '图表']

    # 显示帮助
    if '--help' in args or '-h' in args:
        print(__doc__)
        print("\n示例:")
        print("  python3 一键运行全部脚本.py          # 运行全部")
        print("  python3 一键运行全部脚本.py --q1     # 仅运行Q1模块")
        print("  python3 一键运行全部脚本.py --q2 --q3  # 运行Q2和Q3模块")
        print("  python3 一键运行全部脚本.py --dry    # 预览模式")
        print("  python3 一键运行全部脚本.py --图表   # 仅运行独立图表")
        return

    # 运行
    success = run_all(modules_to_run, dry_run)

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
