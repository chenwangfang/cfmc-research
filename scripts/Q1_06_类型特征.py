#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_06_类型特征.py
================
12类构式的详细特征分析

输出：
- 图17: 12类构式在认知通达度x映射类型空间的分布热力图
- 表66: 12类构式频率分布与核心特征
- 表67: 代表性构式类型语例分析

创建日期：2025-12-05
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, MAPPING_DIRECTION_CODES, MAPPING_DIRECTION_SHORT,
    PROTOTYPE_DISTANCE_LABELS, CONSTRUCTION_COLORS
)


def load_prototype_data(paths: dict) -> pd.DataFrame:
    """加载带原型梯度的数据"""
    # 优先加载带原型梯度的数据
    proto_file = paths['output_data'] / 'CFMC_with_prototype_grades.csv'
    cluster_file = paths['output_data'] / 'CFMC_with_clusters.csv'

    if proto_file.exists():
        df = pd.read_csv(proto_file, index_col=0)
        print(f"[OK] 已加载原型梯度数据: {proto_file}")
    elif cluster_file.exists():
        df = pd.read_csv(cluster_file, index_col=0)
        print(f"[OK] 已加载聚类数据: {cluster_file}")
    else:
        raise FileNotFoundError("请先运行Q1_03_GMM聚类.py和Q1_05_原型梯度.py")

    return df


def create_type_frequency_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    创建12类构式频率分布与核心特征表（表66）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        频率分布与特征表
    """
    table_data = []
    total = len(df)

    for cluster in sorted(df['cluster_label'].unique()):
        mask = df['cluster_label'] == cluster
        subset = df[mask]
        n = len(subset)

        # 认知通达度等级
        ca_mean = subset['cognitive_accessibility'].mean()
        if ca_mean <= 2:
            ca_level = "低"
        elif ca_mean <= 3.5:
            ca_level = "中"
        else:
            ca_level = "高"

        # 概念复杂度等级
        cc_mean = subset['conceptual_complexity'].mean()
        if cc_mean <= 2:
            cc_level = "低"
        elif cc_mean <= 3.5:
            cc_level = "中"
        else:
            cc_level = "高"

        # 主要映射类型
        if 'mapping_direction' in subset.columns:
            md_mode = subset['mapping_direction'].mode()
            main_md = MAPPING_DIRECTION_CODES.get(int(md_mode.iloc[0]) if len(md_mode) > 0 else 0, "未知")
        else:
            main_md = "未知"

        # 原型梯度分布
        if 'prototype_grade' in subset.columns:
            proto_dist = subset['prototype_grade'].value_counts(normalize=True)
            center_pct = proto_dist.get(1, 0) * 100
        else:
            center_pct = 0

        table_data.append({
            '类型编号': f'T{cluster + 1}',
            '样本量': n,
            '占比(%)': round(n / total * 100, 2),
            '认知通达度M': round(ca_mean, 2),
            '通达等级': ca_level,
            '概念复杂度M': round(cc_mean, 2),
            '复杂等级': cc_level,
            '主要映射类型': main_md,
            '中心成员占比(%)': round(center_pct, 1)
        })

    result = pd.DataFrame(table_data)
    result = result.sort_values('样本量', ascending=False).reset_index(drop=True)

    return result



# 表36代表性语例定义（论文正文权威来源）
# 自动选择(prototype_distance最小)的语例仅3/12与表36一致，
# 因此直接指定表36中人工筛选的12个代表性语例。
# key = cluster_label (0-11), 对应 T1-T12
TABLE_36_EXAMPLES = {
    0:  {'construction': '山是地的乳头',                     'source_domain': 'BD', 'target_domain': 'NT', 'ca': 2, 'cc': 3},
    1:  {'construction': '人民是建设共产主义的决定性力量',     'source_domain': 'FC', 'target_domain': 'SC', 'ca': 2, 'cc': 2},
    2:  {'construction': '媒介是讯息',                       'source_domain': 'TH', 'target_domain': 'AB', 'ca': 2, 'cc': 3},
    3:  {'construction': '虱子是革命虫',                     'source_domain': 'SC', 'target_domain': 'LV', 'ca': 2, 'cc': 2},
    4:  {'construction': '地铁是文明的延伸线',               'source_domain': 'SP', 'target_domain': 'OB', 'ca': 3, 'cc': 2},
    5:  {'construction': '工人阶级是革命队伍的先锋',         'source_domain': 'WR', 'target_domain': 'SC', 'ca': 3, 'cc': 2},
    6:  {'construction': '服务行业是革命行业',               'source_domain': 'TR', 'target_domain': 'AB', 'ca': 3, 'cc': 3},
    7:  {'construction': '枪是革命战士的第二条生命',         'source_domain': 'LV', 'target_domain': 'OB', 'ca': 3, 'cc': 4},
    8:  {'construction': '主力军是T淋巴细胞和B淋巴细胞',     'source_domain': 'WR', 'target_domain': 'BD', 'ca': 4, 'cc': 2},
    9:  {'construction': '公社就是我的家',                   'source_domain': 'OB', 'target_domain': 'SC', 'ca': 5, 'cc': 2},
    10: {'construction': '毛主席的话是劳动人民的心里话',     'source_domain': 'SP', 'target_domain': 'CM', 'ca': 4, 'cc': 3},
    11: {'construction': '产品是人品',                       'source_domain': 'MR', 'target_domain': 'OB', 'ca': 4, 'cc': 4},
}


def create_representative_examples_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    创建代表性构式类型语例分析表（表67）

    使用论文表36中指定的12个代表性语例（TABLE_36_EXAMPLES），
    域标签和属性值以表36为权威来源。全句从数据中获取，截断到80字符。

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        语例分析表
    """
    table_data = []

    for cluster in sorted(df['cluster_label'].unique()):
        mask = df['cluster_label'] == cluster
        subset = df[mask]

        t36 = TABLE_36_EXAMPLES.get(cluster)

        if t36 is not None:
            # 使用表36指定的构式：在该聚类中查找匹配条目
            pattern = t36['construction']
            match_mask = subset['construction'] == pattern
            if not match_mask.any():
                # 模糊匹配（前6字符）
                match_mask = subset['construction'].str.contains(
                    pattern[:6], na=False, regex=False)

            if match_mask.any():
                example = subset[match_mask].iloc[0]
                full_sent = str(example.get('full_sentence', ''))
            else:
                full_sent = ''

            # 截断到80字符（CSV可读性）
            if len(full_sent) > 80:
                full_sent = full_sent[:80]

            table_data.append({
                '类型编号': f'T{cluster + 1}',
                '代表语例': full_sent,
                '构式结构': pattern,
                '源域': t36['source_domain'],
                '目标域': t36['target_domain'],
                '认知通达度': t36['ca'],
                '概念复杂度': t36['cc']
            })
        else:
            # 回退：未在表36中定义的类型，自动选择最接近聚类中心的
            if 'prototype_distance' in subset.columns:
                best_idx = subset['prototype_distance'].idxmin()
            else:
                best_idx = subset.index[0]

            example = subset.loc[best_idx]
            full_sent = str(example.get('full_sentence',
                                        example.get('construction', '无')))
            if len(full_sent) > 80:
                full_sent = full_sent[:80]

            table_data.append({
                '类型编号': f'T{cluster + 1}',
                '代表语例': full_sent,
                '构式结构': str(example.get('construction', '无')),
                '源域': example.get('source_domain', '未知'),
                '目标域': example.get('target_domain', '未知'),
                '认知通达度': example.get('cognitive_accessibility', np.nan),
                '概念复杂度': example.get('conceptual_complexity', np.nan)
            })

    return pd.DataFrame(table_data)


def plot_type_heatmap(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制12类构式在认知通达度x映射类型空间的分布热力图（图17）

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
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=12)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_cn_small = fm.FontProperties(fname=font_paths['chinese'], size=9)
    font_en = fm.FontProperties(fname=font_paths['english'], size=11)

    fig, ax = plt.subplots(figsize=(11, 8))

    # 计算频数矩阵
    ca = df['cognitive_accessibility'].values
    md = df['mapping_direction'].values

    # 创建热力图数据：4个映射类型 x 5个通达度等级
    heatmap_data = np.zeros((4, 5))

    for i in range(1, 5):  # 映射类型 1-4
        for j in range(1, 6):  # 通达度 1-5
            count = ((md == i) & (ca == j)).sum()
            heatmap_data[i-1, j-1] = count

    # 语义化类型名称映射（认知通达度等级 x 映射类型）
    # 通达度：1=极低→低, 2=低, 3=中, 4=高, 5=极高→高
    ca_level_names = {1: '低', 2: '低', 3: '中', 4: '高', 5: '高'}
    # 映射类型简称
    md_short_names = MAPPING_DIRECTION_SHORT  # 使用utils常量

    # 绘制热力图（添加网格线）
    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')

    # 添加白色网格线
    ax.set_xticks(np.arange(-.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 4, 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
    ax.tick_params(which='minor', size=0)

    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label('频数', fontproperties=font_cn, fontsize=11)

    # 设置标签
    md_labels = [MAPPING_DIRECTION_CODES[i] for i in range(1, 5)]
    ca_labels = ['1（极低）', '2（低）', '3（中）', '4（高）', '5（极高）']

    ax.set_xticks(np.arange(5))
    ax.set_yticks(np.arange(4))
    ax.set_xticklabels(ca_labels, fontproperties=font_cn, fontsize=10)
    ax.set_yticklabels(md_labels, fontproperties=font_cn, fontsize=10)

    # 计算颜色阈值（用于智能文字颜色）
    max_val = heatmap_data.max()
    threshold = max_val * 0.45  # 阈值调整为45%

    # 添加数值和类型名标注
    for i in range(4):  # 映射类型行
        for j in range(5):  # 通达度列
            value = int(heatmap_data[i, j])

            # 根据背景亮度选择文字颜色
            text_color = 'white' if value > threshold else 'black'

            # 生成语义化类型名
            ca_level = ca_level_names[j + 1]
            md_short = md_short_names[i + 1]
            type_name = f'{ca_level}_{md_short}'

            if value > 0:
                # 显示频数和类型名
                ax.text(j, i - 0.15, str(value), ha='center', va='center',
                       color=text_color, fontsize=12, fontweight='bold',
                       fontproperties=font_en)
                ax.text(j, i + 0.2, type_name, ha='center', va='center',
                       color=text_color, fontsize=9,
                       fontproperties=font_cn_small)
            else:
                # 零值格子显示"0"
                ax.text(j, i, '0', ha='center', va='center',
                       color='gray', fontsize=11, fontproperties=font_en)

    ax.set_xlabel('认知通达度', fontproperties=font_cn, fontsize=12)
    ax.set_ylabel('映射类型', fontproperties=font_cn, fontsize=12)
    # ax.set_title('图17 12类构式空间分布热力图',
                # fontproperties=font_cn_title, fontsize=14, pad=15)

    plt.tight_layout()

    return fig


def analyze_type_characteristics(df: pd.DataFrame) -> None:
    """
    打印各类型的详细特征分析

    Parameters
    ----------
    df : pd.DataFrame
        构式数据
    """
    print("\n各类型详细特征:")
    print("-" * 60)

    for cluster in sorted(df['cluster_label'].unique()):
        mask = df['cluster_label'] == cluster
        subset = df[mask]

        print(f"\n【T{cluster + 1}】(n={len(subset)})")
        print(f"  认知通达度: M={subset['cognitive_accessibility'].mean():.2f}, "
              f"SD={subset['cognitive_accessibility'].std():.2f}")
        print(f"  概念复杂度: M={subset['conceptual_complexity'].mean():.2f}, "
              f"SD={subset['conceptual_complexity'].std():.2f}")

        if 'mapping_direction' in subset.columns:
            md_dist = subset['mapping_direction'].value_counts(normalize=True)
            print(f"  映射类型分布:")
            for md, pct in md_dist.items():
                md_name = MAPPING_DIRECTION_CODES.get(int(md), f'类型{int(md)}')
                print(f"    {md_name}: {pct*100:.1f}%")

        if 'source_domain' in subset.columns:
            top_source = subset['source_domain'].value_counts().head(3)
            print(f"  前3源域: {', '.join([f'{k}({v})' for k, v in top_source.items()])}")

        if 'target_domain' in subset.columns:
            top_target = subset['target_domain'].value_counts().head(3)
            print(f"  前3目标域: {', '.join([f'{k}({v})' for k, v in top_target.items()])}")


def main():
    """主函数"""
    print("=" * 60)
    print("Q1_06_类型特征.py")
    print("12类构式的详细特征分析")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载数据
    print("\n" + "-" * 40)
    print("1. 加载数据")
    print("-" * 40)
    df = load_prototype_data(paths)
    print(f"样本量: {len(df)}")
    print(f"类型数: {df['cluster_label'].nunique()}")

    # 2. 创建表63
    print("\n" + "-" * 40)
    print("2. 保存表66: 12类构式频率分布与核心特征")
    print("-" * 40)
    freq_table = create_type_frequency_table(df)
    print(freq_table.to_string(index=False))
    save_table(freq_table, "12类构式频率分布与核心特征", global_num=66,
               title="12类构式频率分布与核心特征", formats=['csv', 'json'])

    # 3. 创建表64
    print("\n" + "-" * 40)
    print("3. 保存表67: 代表性构式类型语例分析")
    print("-" * 40)
    examples_table = create_representative_examples_table(df)
    print(examples_table.to_string(index=False))
    save_table(examples_table, "代表性构式类型语例分析", global_num=67,
               title="代表性构式类型语例分析", formats=['csv', 'json'])

    # 4. 绘制图17
    print("\n" + "-" * 40)
    print("4. 绘制图17: 认知通达度x映射类型空间分布热力图")
    print("-" * 40)
    fig = plot_type_heatmap(df, paths)
    save_figure(fig, "类型空间分布热力图", global_num=16,
                title="12类构式在认知通达度x映射类型空间的分布热力图")

    # 5. 详细特征分析
    print("\n" + "-" * 40)
    print("5. 各类型详细特征分析")
    print("-" * 40)
    analyze_type_characteristics(df)

    print("\n" + "=" * 60)
    print("Q1_06_类型特征 完成")
    print("=" * 60)

    return freq_table, examples_table


if __name__ == "__main__":
    freq_table, examples_table = main()
