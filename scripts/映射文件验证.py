#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
映射文件验证脚本
用途：验证论文正文、映射文件、实际文件三者的一致性
兼容：Windows / Linux / WSL
更新：2025-12-18
"""

import re
import os
import platform
from pathlib import Path

# =============================================================================
# 跨平台路径配置
# =============================================================================
def get_base_path():
    """获取项目根目录，自动适配Windows/Linux/WSL"""
    # 方法1：基于脚本位置推断（推荐）
    script_dir = Path(__file__).resolve().parent
    # 脚本位于：博士毕业论文/大论文/论文撰写/统计分析/脚本/
    # 需要向上4级到达：博士毕业论文/
    base_path = script_dir.parent.parent.parent.parent

    # 验证路径是否正确（检查是否存在特征文件/目录）
    if (base_path / "大论文").exists():
        return base_path

    # 方法2：尝试平台特定的硬编码路径（备选）
    system = platform.system()
    if system == 'Windows':
        candidates = [
            Path(r"E:\博士毕业论文"),
            Path(r"D:\博士毕业论文"),
        ]
    else:
        # Linux / WSL
        candidates = [
            Path("/mnt/e/博士毕业论文"),
            Path("/mnt/d/博士毕业论文"),
        ]

    for path in candidates:
        if path.exists() and (path / "大论文").exists():
            return path

    # 未找到，返回基于脚本位置的推断（可能不正确但避免崩溃）
    print(f"⚠️ 警告：无法确定项目根目录，使用脚本位置推断：{base_path}")
    return base_path

# 初始化路径
BASE_PATH = get_base_path()
THESIS_PATH = BASE_PATH / "大论文/论文撰写/正文/基于语料库的汉语系表隐喻构式网络认知机制研究.md"
MAPPING_PATH = BASE_PATH / "大论文/论文撰写/统计分析/图-表-语例编号对应关系.md"
FIGURES_CH1_4 = BASE_PATH / "大论文/论文撰写/正文/第1-4章图"
FIGURES_CH5_7 = BASE_PATH / "大论文/论文撰写/统计分析/结果_输出/Figures"
DATA_PATH = BASE_PATH / "大论文/论文撰写/统计分析/结果_输出/Data"

# =============================================================================
# 提取函数
# =============================================================================

def extract_from_thesis(content):
    """从论文正文提取图表引用"""
    figures = set(re.findall(r'图(\d+-\d+[a-z]?)', content))
    tables = set(re.findall(r'表(\d+-\d+[a-z]?)', content))
    return figures, tables

def extract_from_mapping(content):
    """从映射文件提取图表记录"""
    # 匹配格式：| 图N | 图X-Y | 或 | 图N† | 图X-Y |（†表示待定稿时重排）
    figures = set(re.findall(r'\| 图\d+†? \| 图(\d+-\d+[a-z]?) \|', content))
    tables = set(re.findall(r'\| 表\d+†? \| 表(\d+-\d+[a-z]?) \|', content))
    return figures, tables

def scan_figure_files():
    """扫描实际图片文件"""
    files = set()

    # 第1-4章图片（空格分隔）
    if FIGURES_CH1_4.exists():
        for f in FIGURES_CH1_4.glob("图*.png"):
            match = re.match(r'图(\d+-\d+[a-z]?)', f.stem)
            if match:
                files.add(match.group(1))

    # 第5-7章图片（下划线分隔）
    if FIGURES_CH5_7.exists():
        for f in FIGURES_CH5_7.glob("图*.png"):
            match = re.match(r'图(\d+-\d+[a-z]?)', f.stem)
            if match:
                files.add(match.group(1))

    return files

def scan_data_files():
    """扫描实际数据文件"""
    files = set()
    if DATA_PATH.exists():
        for f in DATA_PATH.glob("表*.csv"):
            match = re.match(r'表(\d+-\d+[a-z]?)', f.stem)
            if match:
                files.add(match.group(1))
    return files

# =============================================================================
# 验证函数
# =============================================================================

def verify_alignment():
    """执行三方对齐验证"""
    print("=" * 60)
    print("映射文件验证报告")
    print("=" * 60)
    print(f"平台: {platform.system()}")
    print(f"根目录: {BASE_PATH}")

    # 检查关键文件是否存在
    if not THESIS_PATH.exists():
        print(f"\n❌ 错误：论文正文不存在：{THESIS_PATH}")
        return -1
    if not MAPPING_PATH.exists():
        print(f"\n❌ 错误：映射文件不存在：{MAPPING_PATH}")
        return -1

    # 读取文件
    thesis_content = THESIS_PATH.read_text(encoding='utf-8')
    mapping_content = MAPPING_PATH.read_text(encoding='utf-8')

    # 提取引用
    thesis_figs, thesis_tbls = extract_from_thesis(thesis_content)
    mapping_figs, mapping_tbls = extract_from_mapping(mapping_content)
    actual_figs = scan_figure_files()
    actual_tbls = scan_data_files()

    # 统计
    print(f"\n【统计数据】")
    print(f"  论文正文：{len(thesis_figs)} 个图，{len(thesis_tbls)} 个表")
    print(f"  映射文件：{len(mapping_figs)} 个图，{len(mapping_tbls)} 个表")
    print(f"  实际文件：{len(actual_figs)} 个图，{len(actual_tbls)} 个表")

    # 图片验证
    print(f"\n【图片验证】")
    fig_only_thesis = thesis_figs - mapping_figs
    fig_only_mapping = mapping_figs - thesis_figs
    fig_no_file = mapping_figs - actual_figs

    if fig_only_thesis:
        print(f"  ⚠️ 正文有但映射无：{sorted(fig_only_thesis)}")
    if fig_only_mapping:
        print(f"  ⚠️ 映射有但正文无：{sorted(fig_only_mapping)}")
    if fig_no_file:
        # 排除第1-4章（可能是理论框架图）
        ch5_7_no_file = {f for f in fig_no_file if f.startswith(('5-', '6-', '7-'))}
        if ch5_7_no_file:
            print(f"  ⚠️ 第5-7章映射有但文件无：{sorted(ch5_7_no_file)}")
    if not (fig_only_thesis or fig_only_mapping or fig_no_file):
        print(f"  ✅ 图片三方对齐一致")

    # 表格验证
    print(f"\n【表格验证】")
    tbl_only_thesis = thesis_tbls - mapping_tbls
    tbl_only_mapping = mapping_tbls - thesis_tbls

    if tbl_only_thesis:
        print(f"  ⚠️ 正文有但映射无：{sorted(tbl_only_thesis)}")
    if tbl_only_mapping:
        print(f"  ⚠️ 映射有但正文无：{sorted(tbl_only_mapping)}")
    if not (tbl_only_thesis or tbl_only_mapping):
        print(f"  ✅ 表格正文-映射对齐一致")

    # 注意：表格编号偏移是正常的
    print(f"\n【注意】")
    print(f"  - 第5-7章CSV文件编号与正文表格编号存在偏移（正文含理论说明表）")
    print(f"  - 第1-4章图片无对应CSV文件（理论框架图）")

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)

    # 返回差异数量（用于判断是否需要更新）
    return len(fig_only_thesis) + len(fig_only_mapping) + len(tbl_only_thesis) + len(tbl_only_mapping)

# =============================================================================
# 主程序
# =============================================================================

if __name__ == "__main__":
    diff_count = verify_alignment()

    if diff_count < 0:
        print(f"\n验证失败，请检查文件路径。")
    elif diff_count > 0:
        print(f"\n发现 {diff_count} 处差异，建议更新映射文件。")
    else:
        print(f"\n无差异，映射文件与正文一致。")
