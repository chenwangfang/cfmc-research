#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_01_描述统计.py
==================
认知通达度与映射类型的描述性统计

输出：
- 图12: 认知通达度分布直方图
- 图13: 映射类型分布条形图
- 表58: 认知通达度分布
- 表59: 映射类型分布与概念复杂度对应

创建日期：2025-12-05
"""

import sys
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import stats

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, format_stats,
    MAPPING_DIRECTION_CODES, setup_matplotlib_chinese
)


def analyze_cognitive_accessibility(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析认知通达度分布

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        认知通达度分布统计表
    """
    # 基本统计（确保数值类型）
    ca = pd.to_numeric(df['cognitive_accessibility'], errors='coerce').dropna()

    # 频率分布
    value_counts = ca.value_counts().sort_index()
    total = len(ca)

    # 构建分布表
    dist_data = []
    for level in sorted(ca.unique()):
        count = value_counts.get(level, 0)
        pct = count / total * 100
        cum_pct = value_counts[value_counts.index <= level].sum() / total * 100

        # 认知通达度等级标签
        if level <= 2:
            label = "低通达"
        elif level == 3:
            label = "中通达"
        else:
            label = "高通达"

        dist_data.append({
            '认知通达度': int(level),
            '等级': label,
            '频数': count,
            '百分比(%)': round(pct, 2),
            '累计百分比(%)': round(cum_pct, 2)
        })

    # 添加汇总统计
    dist_df = pd.DataFrame(dist_data)

    # 打印描述统计
    print("\n认知通达度描述统计:")
    print(f"  N = {len(ca)}")
    print(f"  M = {ca.mean():.3f}")
    print(f"  SD = {ca.std():.3f}")
    print(f"  Median = {ca.median():.1f}")
    print(f"  Range = {ca.min():.0f} - {ca.max():.0f}")
    print(f"  Skewness = {stats.skew(ca.astype(float)):.3f}")
    print(f"  Kurtosis = {stats.kurtosis(ca.astype(float)):.3f}")

    return dist_df


def analyze_mapping_direction(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析映射类型分布及其与概念复杂度的对应关系

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        映射类型分布统计表
    """
    # 映射方向频率
    md = df['mapping_direction'].dropna()
    cc = df['conceptual_complexity'].dropna()

    # 计算各类型的统计
    dist_data = []
    for code in sorted(md.unique()):
        mask = df['mapping_direction'] == code
        count = mask.sum()
        pct = count / len(md) * 100

        # 该类型的概念复杂度统计
        cc_subset = df.loc[mask, 'conceptual_complexity'].dropna()
        cc_mean = cc_subset.mean() if len(cc_subset) > 0 else np.nan
        cc_sd = cc_subset.std() if len(cc_subset) > 0 else np.nan

        label = MAPPING_DIRECTION_CODES.get(int(code), f'类型{int(code)}')

        dist_data.append({
            '映射类型': label,
            '代码': int(code),
            '频数': count,
            '百分比(%)': round(pct, 2),
            '概念复杂度M': round(cc_mean, 3) if not np.isnan(cc_mean) else '—',
            '概念复杂度SD': round(cc_sd, 3) if not np.isnan(cc_sd) else '—'
        })

    dist_df = pd.DataFrame(dist_data)

    # 打印映射类型分布
    print("\n映射类型分布:")
    for _, row in dist_df.iterrows():
        print(f"  {row['映射类型']}: n={row['频数']} ({row['百分比(%)']:.1f}%)")

    return dist_df


def plot_cognitive_accessibility_histogram(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制认知通达度分布直方图（图12）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据
    paths : dict
        路径字典

    Returns
    -------
    Figure
        matplotlib图表对象
    """
    # 设置字体
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=12)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_en = fm.FontProperties(fname=font_paths['english'], size=10)

    ca = df['cognitive_accessibility'].dropna()

    fig, ax = plt.subplots(figsize=(10, 6))

    # 直方图
    counts, bins, patches = ax.hist(ca, bins=5, range=(0.5, 5.5),
                                    color='#3498db', edgecolor='white',
                                    alpha=0.8, rwidth=0.85)

    # 添加频数标签
    for count, patch in zip(counts, patches):
        height = patch.get_height()
        ax.annotate(f'{int(count)}',
                   xy=(patch.get_x() + patch.get_width() / 2, height),
                   ha='center', va='bottom', fontsize=11,
                   fontproperties=font_en)

    # 添加均值线
    mean_val = ca.mean()
    ax.axvline(x=mean_val, color='#e74c3c', linestyle='--', linewidth=2,
               label=f'均值 = {mean_val:.2f}')

    # 设置坐标轴
    ax.set_xlabel('认知通达度', fontproperties=font_cn, fontsize=12)
    ax.set_ylabel('频数', fontproperties=font_cn, fontsize=12)
    # ax.set_title('图12 认知通达度分布直方图', fontproperties=font_cn_title, fontsize=14, pad=15)

    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(['1\n（极低）', '2\n（低）', '3\n（中）', '4\n（高）', '5\n（极高）'],
                       fontproperties=font_cn, fontsize=10)

    # 添加统计信息文本框（位置左移避免覆盖柱子）
    stats_text = f'N = {len(ca)}\nM = {ca.mean():.2f}\nSD = {ca.std():.2f}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.68, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=props, fontproperties=font_en)

    ax.legend(loc='upper left', prop=font_cn)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    return fig


def plot_mapping_direction_bar(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制映射类型分布条形图（图13）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据
    paths : dict
        路径字典

    Returns
    -------
    Figure
        matplotlib图表对象
    """
    # 设置字体
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=12)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_en = fm.FontProperties(fname=font_paths['english'], size=10)

    md = df['mapping_direction'].dropna()
    cc = df['conceptual_complexity']

    # 准备数据
    labels = []
    counts = []
    cc_means = []
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']

    for code in [1, 2, 3, 4]:
        mask = md == code
        label = MAPPING_DIRECTION_CODES.get(code, f'类型{code}')
        labels.append(label)
        counts.append(mask.sum())
        cc_means.append(df.loc[mask, 'conceptual_complexity'].mean())

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 条形图（频数）
    x = np.arange(len(labels))
    width = 0.6
    bars = ax1.bar(x, counts, width, color=colors, edgecolor='white', alpha=0.8)

    # 添加频数标签
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        pct = count / sum(counts) * 100
        ax1.annotate(f'{count}\n（{pct:.1f}%）',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    ha='center', va='bottom', fontsize=10,
                    fontproperties=font_cn)

    # 设置主坐标轴
    ax1.set_xlabel('映射类型', fontproperties=font_cn, fontsize=12)
    ax1.set_ylabel('频数', fontproperties=font_cn, fontsize=12)
    # ax1.set_title('图13 映射类型分布条形图', fontproperties=font_cn_title, fontsize=14, pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontproperties=font_cn, fontsize=11)
    ax1.set_ylim(0, 3000)  # 设置Y轴范围，使柱子比例更合适

    # 次坐标轴（概念复杂度均值）- 使用红色区分
    ax2 = ax1.twinx()
    ax2.plot(x, cc_means, 'ro-', markersize=8, linewidth=2, label='概念复杂度均值')
    ax2.set_ylabel('概念复杂度均值', fontproperties=font_cn, fontsize=12, color='#e74c3c')
    ax2.set_ylim(1, 5)
    ax2.tick_params(axis='y', colors='#e74c3c')  # 右侧刻度也用红色

    # 添加概念复杂度标签
    for i, (xi, yi) in enumerate(zip(x, cc_means)):
        ax2.annotate(f'{yi:.2f}', xy=(xi, yi), xytext=(5, 5),
                    textcoords='offset points', fontsize=9,
                    fontproperties=font_en, color='#e74c3c')

    # 图例
    ax2.legend(loc='upper right', prop=font_cn, labelcolor='#e74c3c')

    ax1.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    return fig


def main():
    """主函数"""
    print("=" * 60)
    print("Q1_01_描述统计.py")
    print("认知通达度与映射类型的描述性统计")
    print("=" * 60)

    # 获取路径
    paths = get_paths()
    print(f"\n数据文件: {paths['data_file']}")

    # 加载数据
    df, meta = load_cfmc_data()
    print(f"数据量: {len(df)} 条")

    # 1. 认知通达度分布分析
    print("\n" + "-" * 40)
    print("1. 认知通达度分布分析")
    print("-" * 40)
    ca_dist = analyze_cognitive_accessibility(df)

    # 保存表58
    save_table(ca_dist, "认知通达度分布", global_num=58,
               title="认知通达度分布", formats=['csv', 'json'])

    # 2. 映射类型分布分析
    print("\n" + "-" * 40)
    print("2. 映射类型分布分析")
    print("-" * 40)
    md_dist = analyze_mapping_direction(df)

    # 保存表59
    save_table(md_dist, "映射类型分布与概念复杂度对应", global_num=59,
               title="映射类型分布与概念复杂度对应", formats=['csv', 'json'])

    # 3. 绘制图12
    print("\n" + "-" * 40)
    print("3. 绘制图12: 认知通达度分布直方图")
    print("-" * 40)
    fig1 = plot_cognitive_accessibility_histogram(df, paths)
    save_figure(fig1, "认知通达度分布直方图", global_num=12,
                title="认知通达度分布直方图")

    # 4. 绘制图13
    print("\n" + "-" * 40)
    print("4. 绘制图13: 映射类型分布条形图")
    print("-" * 40)
    fig2 = plot_mapping_direction_bar(df, paths)
    save_figure(fig2, "映射类型分布条形图", global_num=13,
                title="映射类型分布条形图")

    # 5. 汇总描述统计
    print("\n" + "-" * 40)
    print("5. 核心变量汇总描述统计")
    print("-" * 40)

    # 创建汇总统计表
    summary_vars = ['cognitive_accessibility', 'conceptual_complexity',
                    'mapping_direction', 'prototype_distance']
    summary_data = []

    for var in summary_vars:
        if var in df.columns:
            data = pd.to_numeric(df[var], errors='coerce').dropna().astype(float)
            summary_data.append({
                '变量': var,
                'N': len(data),
                '均值': round(data.mean(), 3),
                '标准差': round(data.std(), 3),
                '最小值': round(data.min(), 3),
                '最大值': round(data.max(), 3),
                '偏度': round(stats.skew(data), 3),
                '峰度': round(stats.kurtosis(data), 3)
            })

    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))

    print("\n" + "=" * 60)
    print("Q1_01_描述统计 完成")
    print("=" * 60)

    return ca_dist, md_dist


if __name__ == "__main__":
    ca_dist, md_dist = main()
