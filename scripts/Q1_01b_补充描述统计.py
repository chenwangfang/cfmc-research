#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_01b_补充描述统计.py
======================
生成论文正文引用的基础描述统计数据（补充Q1_01未覆盖的统计量）

输出数据表：
- 表S1: 12类构式分组描述统计（含M、SD、占比）
- 表S2: 认知通达度三级分布（低/中/高）
- 表S3: 语体×映射方向交叉分布
- 表S4: 语体×认知通达度等级交叉分布
- 表S5: 12类构式×语体交叉分布
- 表S6: 全样本核心变量描述统计汇总

创建日期：2026-02-07
"""

import sys
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import numpy as np
import pandas as pd
from scipy import stats

from utils_公共函数 import (
    CONSTRUCTION_TYPE_12, MAPPING_DIRECTION_CODES,
    MAPPING_DIRECTION_SHORT,
    get_paths, load_cfmc_data, save_table
)


# =============================================================================
# 辅助函数
# =============================================================================

def get_ca_level(ca: float) -> str:
    """认知通达度→三级标签"""
    if ca <= 2:
        return '低'
    elif ca == 3:
        return '中'
    else:
        return '高'


def get_type_label(ca: float, md: float) -> str:
    """认知通达度+映射方向→12类标签"""
    ca_label = get_ca_level(ca)
    md_short = MAPPING_DIRECTION_SHORT.get(int(md), str(int(md)))
    return f'{ca_label}_{md_short}'


def get_type_code(label: str) -> int:
    """12类标签→T编号（1-12）"""
    type_order = [
        '低_具具', '低_具抽', '低_抽抽', '低_抽具',
        '中_具具', '中_具抽', '中_抽抽', '中_抽具',
        '高_具具', '高_具抽', '高_抽抽', '高_抽具'
    ]
    try:
        return type_order.index(label) + 1
    except ValueError:
        return 0


# =============================================================================
# 表S1: 12类构式分组描述统计
# =============================================================================

def generate_type_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成12类构式的分组描述统计（含M、SD、占比）

    对应正文表格：第5章12类构式特征表（含SD列）
    """
    df = df.copy()
    df['type_label'] = df.apply(
        lambda r: get_type_label(r['cognitive_accessibility'], r['mapping_direction']),
        axis=1
    )

    total = len(df)
    rows = []

    for label in CONSTRUCTION_TYPE_12:
        subset = df[df['type_label'] == label]
        n = len(subset)
        if n == 0:
            continue

        ca = subset['cognitive_accessibility']
        cc = subset['conceptual_complexity']

        rows.append({
            '类型编号': f'T{get_type_code(label)}',
            '类型标签': label,
            '样本量': n,
            '占比(%)': round(n / total * 100, 2),
            '认知通达度M': round(ca.mean(), 2),
            '认知通达度SD': round(ca.std(), 2),
            '概念复杂度M': round(cc.mean(), 2),
            '概念复杂度SD': round(cc.std(), 2),
            '认知通达度等级': label.split('_')[0],
            '映射方向': MAPPING_DIRECTION_CODES.get(
                int(subset['mapping_direction'].mode().iloc[0]), '未知'
            ) if n > 0 else '未知'
        })

    result = pd.DataFrame(rows)

    # 打印
    print("\n表S1: 12类构式分组描述统计")
    print("=" * 80)
    for _, r in result.iterrows():
        print(f"  {r['类型编号']} ({r['类型标签']}): "
              f"n={r['样本量']} ({r['占比(%)']:.2f}%), "
              f"CA: M={r['认知通达度M']:.2f}, SD={r['认知通达度SD']:.2f}, "
              f"CC: M={r['概念复杂度M']:.2f}, SD={r['概念复杂度SD']:.2f}")

    # 汇总行
    print(f"\n  合计: N={total}")
    print(f"  全样本 CA: M={df['cognitive_accessibility'].mean():.2f}, SD={df['cognitive_accessibility'].std():.2f}")
    print(f"  全样本 CC: M={df['conceptual_complexity'].mean():.2f}, SD={df['conceptual_complexity'].std():.2f}")

    return result


# =============================================================================
# 表S2: 认知通达度三级分布
# =============================================================================

def generate_ca_level_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成认知通达度三级分布（低/中/高）

    对应正文引用：高通达68.49%、中通达30.52%、低通达0.99%
    """
    df = df.copy()
    df['ca_level'] = df['cognitive_accessibility'].apply(get_ca_level)

    total = len(df)
    level_order = ['低', '中', '高']
    rows = []
    cum_n = 0

    for level in level_order:
        subset = df[df['ca_level'] == level]
        n = len(subset)
        cum_n += n

        ca = subset['cognitive_accessibility']
        cc = subset['conceptual_complexity']

        rows.append({
            '认知通达度等级': level,
            'CA取值范围': '1-2' if level == '低' else ('3' if level == '中' else '4-5'),
            '样本量': n,
            '占比(%)': round(n / total * 100, 2),
            '累计占比(%)': round(cum_n / total * 100, 2),
            'CA均值': round(ca.mean(), 3) if n > 0 else np.nan,
            'CA标准差': round(ca.std(), 3) if n > 0 else np.nan,
            'CC均值': round(cc.mean(), 3) if n > 0 else np.nan,
            'CC标准差': round(cc.std(), 3) if n > 0 else np.nan
        })

    # 添加合计行
    rows.append({
        '认知通达度等级': '合计',
        'CA取值范围': '1-5',
        '样本量': total,
        '占比(%)': 100.0,
        '累计占比(%)': 100.0,
        'CA均值': round(df['cognitive_accessibility'].mean(), 3),
        'CA标准差': round(df['cognitive_accessibility'].std(), 3),
        'CC均值': round(df['conceptual_complexity'].mean(), 3),
        'CC标准差': round(df['conceptual_complexity'].std(), 3)
    })

    result = pd.DataFrame(rows)

    print("\n表S2: 认知通达度三级分布")
    print("=" * 80)
    for _, r in result.iterrows():
        print(f"  {r['认知通达度等级']}通达 ({r['CA取值范围']}): "
              f"n={r['样本量']} ({r['占比(%)']:.2f}%)")

    return result


# =============================================================================
# 表S3: 语体×映射方向交叉分布
# =============================================================================

def generate_genre_mapping_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成语体×映射方向交叉分布表

    对应正文引用：如"文学语体中抽→抽占38.5%"
    包含频数和行百分比（语体内部占比）
    """
    # 映射方向标签
    md_labels = {1: '具→具', 2: '具→抽', 3: '抽→抽', 4: '抽→具'}
    df = df.copy()
    df['md_label'] = df['mapping_direction'].map(md_labels)

    # 语体排序
    genre_order = ['文学', '新闻', '网络', '学术', '对话']

    rows = []
    for genre in genre_order:
        subset = df[df['genre'] == genre]
        n_genre = len(subset)
        if n_genre == 0:
            continue

        row = {'语体': genre, '语体样本量': n_genre}

        for md_code, md_label in md_labels.items():
            md_subset = subset[subset['mapping_direction'] == md_code]
            n_md = len(md_subset)
            row[f'{md_label}_频数'] = n_md
            row[f'{md_label}_行占比(%)'] = round(n_md / n_genre * 100, 2)

        rows.append(row)

    # 添加合计行
    total_row = {'语体': '合计', '语体样本量': len(df)}
    for md_code, md_label in md_labels.items():
        n_md = len(df[df['mapping_direction'] == md_code])
        total_row[f'{md_label}_频数'] = n_md
        total_row[f'{md_label}_行占比(%)'] = round(n_md / len(df) * 100, 2)
    rows.append(total_row)

    result = pd.DataFrame(rows)

    print("\n表S3: 语体×映射方向交叉分布")
    print("=" * 80)
    for _, r in result.iterrows():
        parts = []
        for md_label in md_labels.values():
            parts.append(f"{md_label}={r[f'{md_label}_频数']}({r[f'{md_label}_行占比(%)']:.1f}%)")
        print(f"  {r['语体']} (n={r['语体样本量']}): {', '.join(parts)}")

    return result


# =============================================================================
# 表S4: 语体×认知通达度等级交叉分布
# =============================================================================

def generate_genre_ca_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成语体×认知通达度等级交叉分布表
    """
    df = df.copy()
    df['ca_level'] = df['cognitive_accessibility'].apply(get_ca_level)

    genre_order = ['文学', '新闻', '网络', '学术', '对话']
    ca_levels = ['低', '中', '高']

    rows = []
    for genre in genre_order:
        subset = df[df['genre'] == genre]
        n_genre = len(subset)
        if n_genre == 0:
            continue

        row = {'语体': genre, '语体样本量': n_genre}

        for level in ca_levels:
            n_level = len(subset[subset['ca_level'] == level])
            row[f'{level}通达_频数'] = n_level
            row[f'{level}通达_行占比(%)'] = round(n_level / n_genre * 100, 2)

        row['CA均值'] = round(subset['cognitive_accessibility'].mean(), 3)
        row['CA标准差'] = round(subset['cognitive_accessibility'].std(), 3)
        rows.append(row)

    # 合计行
    total_row = {'语体': '合计', '语体样本量': len(df)}
    for level in ca_levels:
        n_level = len(df[df['ca_level'] == level])
        total_row[f'{level}通达_频数'] = n_level
        total_row[f'{level}通达_行占比(%)'] = round(n_level / len(df) * 100, 2)
    total_row['CA均值'] = round(df['cognitive_accessibility'].mean(), 3)
    total_row['CA标准差'] = round(df['cognitive_accessibility'].std(), 3)
    rows.append(total_row)

    result = pd.DataFrame(rows)

    print("\n表S4: 语体×认知通达度等级交叉分布")
    print("=" * 80)
    for _, r in result.iterrows():
        parts = [f"{lv}通达={r[f'{lv}通达_频数']}({r[f'{lv}通达_行占比(%)']:.1f}%)" for lv in ca_levels]
        print(f"  {r['语体']} (n={r['语体样本量']}): {', '.join(parts)}")

    return result


# =============================================================================
# 表S5: 12类构式×语体交叉分布
# =============================================================================

def generate_type_genre_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成12类构式×语体交叉分布表
    """
    df = df.copy()
    df['type_label'] = df.apply(
        lambda r: get_type_label(r['cognitive_accessibility'], r['mapping_direction']),
        axis=1
    )

    genre_order = ['文学', '新闻', '网络', '学术', '对话']

    rows = []
    for label in CONSTRUCTION_TYPE_12:
        subset = df[df['type_label'] == label]
        n_type = len(subset)
        if n_type == 0:
            continue

        row = {
            '类型编号': f'T{get_type_code(label)}',
            '类型标签': label,
            '样本量': n_type
        }

        for genre in genre_order:
            n_genre = len(subset[subset['genre'] == genre])
            row[f'{genre}_频数'] = n_genre
            row[f'{genre}_行占比(%)'] = round(n_genre / n_type * 100, 2) if n_type > 0 else 0

        rows.append(row)

    result = pd.DataFrame(rows)

    print("\n表S5: 12类构式×语体交叉分布")
    print("=" * 80)
    for _, r in result.iterrows():
        parts = [f"{g}={r[f'{g}_频数']}" for g in genre_order]
        print(f"  {r['类型编号']} ({r['类型标签']}, n={r['样本量']}): {', '.join(parts)}")

    return result


# =============================================================================
# 表S6: 全样本核心变量描述统计汇总
# =============================================================================

def generate_overall_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成全样本核心变量描述统计汇总

    包含N, M, SD, Min, Max, 偏度, 峰度, 中位数
    """
    variables = {
        'cognitive_accessibility': '认知通达度',
        'conceptual_complexity': '概念复杂度',
        'mapping_direction': '映射方向',
        'conventionality': '常规度',
        'systematicity': '系统性',
        'entailment_richness': '蕴涵丰富度',
        'embodied_experience': '具身体验',
        'prototype_distance': '原型距离'
    }

    rows = []
    for var, label in variables.items():
        if var not in df.columns:
            continue
        data = pd.to_numeric(df[var], errors='coerce').dropna()
        if len(data) == 0:
            continue

        data_float = data.astype(float)
        rows.append({
            '变量英文': var,
            '变量中文': label,
            'N': len(data),
            'M': round(data_float.mean(), 4),
            'SD': round(data_float.std(), 4),
            'Min': round(data_float.min(), 4),
            'Max': round(data_float.max(), 4),
            'Median': round(data_float.median(), 4),
            '偏度': round(float(stats.skew(data_float)), 4),
            '峰度': round(float(stats.kurtosis(data_float)), 4)
        })

    result = pd.DataFrame(rows)

    print("\n表S6: 全样本核心变量描述统计汇总")
    print("=" * 80)
    for _, r in result.iterrows():
        print(f"  {r['变量中文']}: N={r['N']}, M={r['M']:.3f}, SD={r['SD']:.3f}, "
              f"Range=[{r['Min']:.2f}, {r['Max']:.2f}], Skew={r['偏度']:.3f}")

    return result


# =============================================================================
# 主函数
# =============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Q1_01b_补充描述统计.py")
    print("生成论文正文引用的基础描述统计数据")
    print("=" * 60)

    # 加载数据
    df, meta = load_cfmc_data()
    print(f"\n数据量: {len(df)} 条")
    print(f"语体分布: {dict(df['genre'].value_counts())}")

    # =========================================================================
    # 表S1: 12类构式分组描述统计
    # =========================================================================
    print("\n" + "-" * 60)
    s1 = generate_type_descriptive_stats(df)
    save_table(s1, "12类构式分组描述统计", global_num='S1',
               title="12类构式分组描述统计（含M和SD）", formats=['csv', 'json'])
    print("[OK] 表S1 已保存")

    # =========================================================================
    # 表S2: 认知通达度三级分布
    # =========================================================================
    print("\n" + "-" * 60)
    s2 = generate_ca_level_distribution(df)
    save_table(s2, "认知通达度三级分布", global_num='S2',
               title="认知通达度三级分布（低/中/高）", formats=['csv', 'json'])
    print("[OK] 表S2 已保存")

    # =========================================================================
    # 表S3: 语体×映射方向交叉分布
    # =========================================================================
    print("\n" + "-" * 60)
    s3 = generate_genre_mapping_crosstab(df)
    save_table(s3, "语体×映射方向交叉分布", global_num='S3',
               title="语体×映射方向交叉分布", formats=['csv', 'json'])
    print("[OK] 表S3 已保存")

    # =========================================================================
    # 表S4: 语体×认知通达度等级交叉分布
    # =========================================================================
    print("\n" + "-" * 60)
    s4 = generate_genre_ca_crosstab(df)
    save_table(s4, "语体×认知通达度等级交叉分布", global_num='S4',
               title="语体×认知通达度等级交叉分布", formats=['csv', 'json'])
    print("[OK] 表S4 已保存")

    # =========================================================================
    # 表S5: 12类构式×语体交叉分布
    # =========================================================================
    print("\n" + "-" * 60)
    s5 = generate_type_genre_crosstab(df)
    save_table(s5, "12类构式×语体交叉分布", global_num='S5',
               title="12类构式×语体交叉分布", formats=['csv', 'json'])
    print("[OK] 表S5 已保存")

    # =========================================================================
    # 表S6: 全样本核心变量描述统计汇总
    # =========================================================================
    print("\n" + "-" * 60)
    s6 = generate_overall_summary(df)
    save_table(s6, "全样本核心变量描述统计汇总", global_num='S6',
               title="全样本核心变量描述统计汇总", formats=['csv', 'json'])
    print("[OK] 表S6 已保存")

    # =========================================================================
    # 汇总
    # =========================================================================
    print("\n" + "=" * 60)
    print("Q1_01b_补充描述统计 完成")
    print("=" * 60)
    print(f"\n共生成 6 个数据表（CSV + JSON）：")
    print(f"  表S1: 12类构式分组描述统计（含SD）")
    print(f"  表S2: 认知通达度三级分布")
    print(f"  表S3: 语体×映射方向交叉分布")
    print(f"  表S4: 语体×认知通达度等级交叉分布")
    print(f"  表S5: 12类构式×语体交叉分布")
    print(f"  表S6: 全样本核心变量描述统计汇总")

    return s1, s2, s3, s4, s5, s6


if __name__ == "__main__":
    main()
