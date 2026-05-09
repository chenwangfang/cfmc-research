#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_05_原型梯度.py
================
计算马氏距离并划分原型梯度结构

输出：
- 图16: 原型梯度三组核心变量差异比较箱线图
- 表63: 原型梯度分布
- 表64: 原型梯度间差异检验

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
from scipy.spatial.distance import mahalanobis
from sklearn.covariance import EmpiricalCovariance
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, format_stats,
    PROTOTYPE_DISTANCE_LABELS, cohens_d, eta_squared
)


def load_clustered_data(paths: dict) -> pd.DataFrame:
    """加载带聚类标签的数据"""
    cluster_file = paths['output_data'] / 'CFMC_with_clusters.csv'

    if cluster_file.exists():
        df = pd.read_csv(cluster_file, index_col=0)
        print(f"[OK] 已加载聚类结果: {cluster_file}")
    else:
        raise FileNotFoundError("请先运行Q1_03_GMM聚类.py生成聚类结果")

    return df


def calculate_mahalanobis_distance(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算马氏距离并划分原型梯度

    Parameters
    ----------
    df : pd.DataFrame
        带聚类标签的数据

    Returns
    -------
    pd.DataFrame
        添加了马氏距离和原型梯度的数据框
    """
    # 特征与Q1_03分类维度一致：认知通达度x映射方向
    features = ['cognitive_accessibility', 'mapping_direction']
    df_result = df.copy()

    # 对每个聚类计算马氏距离
    all_distances = []
    all_grades = []

    for cluster in df['cluster_label'].unique():
        mask = df['cluster_label'] == cluster
        X_cluster = df.loc[mask, features].values

        # 计算协方差矩阵
        cov = EmpiricalCovariance().fit(X_cluster)
        center = X_cluster.mean(axis=0)

        # 计算每个点到中心的马氏距离
        distances = []
        for x in X_cluster:
            try:
                d = mahalanobis(x, center, cov.precision_)
            except:
                # 如果协方差矩阵奇异，使用欧氏距离
                d = np.linalg.norm(x - center)
            distances.append(d)

        distances = np.array(distances)

        # 基于百分位数划分原型梯度
        p33 = np.percentile(distances, 33.33)
        p67 = np.percentile(distances, 66.67)

        grades = np.where(distances <= p33, 1,  # 中心成员
                         np.where(distances <= p67, 2,  # 次中心成员
                                 3))  # 边缘成员

        # 存储结果
        idx = df.index[mask]
        for i, (idx_val, dist, grade) in enumerate(zip(idx, distances, grades)):
            all_distances.append((idx_val, dist, grade))

    # 添加到数据框
    dist_df = pd.DataFrame(all_distances, columns=['index', 'mahalanobis_distance', 'prototype_grade'])
    dist_df.set_index('index', inplace=True)

    df_result['mahalanobis_distance'] = dist_df['mahalanobis_distance']
    df_result['prototype_grade'] = dist_df['prototype_grade']

    print(f"\n马氏距离计算完成:")
    print(f"  均值: {df_result['mahalanobis_distance'].mean():.3f}")
    print(f"  标准差: {df_result['mahalanobis_distance'].std():.3f}")
    print(f"  范围: [{df_result['mahalanobis_distance'].min():.3f}, {df_result['mahalanobis_distance'].max():.3f}]")

    return df_result


def create_prototype_distribution_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    创建原型梯度分布表（表63）

    Parameters
    ----------
    df : pd.DataFrame
        带原型梯度的数据

    Returns
    -------
    pd.DataFrame
        分布表
    """
    table_data = []
    total = len(df)

    for grade in [1, 2, 3]:
        mask = df['prototype_grade'] == grade
        subset = df[mask]
        n = len(subset)

        table_data.append({
            '原型梯度': PROTOTYPE_DISTANCE_LABELS[grade],
            '梯度编码': grade,
            '样本量': n,
            '占比(%)': round(n / total * 100, 2),
            '马氏距离M': round(subset['mahalanobis_distance'].mean(), 3),
            '马氏距离SD': round(subset['mahalanobis_distance'].std(), 3),
            '认知通达度M': round(subset['cognitive_accessibility'].mean(), 3),
            '映射方向M': round(subset['mapping_direction'].mean(), 3)
        })

    return pd.DataFrame(table_data)


def perform_grade_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    进行原型梯度间差异检验（表64）

    Parameters
    ----------
    df : pd.DataFrame
        带原型梯度的数据

    Returns
    -------
    pd.DataFrame
        差异检验结果表
    """
    variables = ['cognitive_accessibility', 'mapping_direction', 'mahalanobis_distance']
    var_names = ['认知通达度', '映射方向', '马氏距离']

    results = []

    for var, var_name in zip(variables, var_names):
        # 三组数据
        group1 = df[df['prototype_grade'] == 1][var].dropna()
        group2 = df[df['prototype_grade'] == 2][var].dropna()
        group3 = df[df['prototype_grade'] == 3][var].dropna()

        # 单因素ANOVA
        f_stat, p_anova = stats.f_oneway(group1, group2, group3)
        df_between = 2
        df_within = len(group1) + len(group2) + len(group3) - 3
        eta2 = eta_squared(f_stat, df_between, df_within)

        # Tukey HSD事后检验
        from scipy.stats import tukey_hsd
        try:
            tukey = tukey_hsd(group1, group2, group3)
            # 获取各组间比较
            p_12 = tukey.pvalue[0, 1]
            p_13 = tukey.pvalue[0, 2]
            p_23 = tukey.pvalue[1, 2]
        except:
            # 如果tukey_hsd不可用，用独立t检验近似
            _, p_12 = stats.ttest_ind(group1, group2)
            _, p_13 = stats.ttest_ind(group1, group3)
            _, p_23 = stats.ttest_ind(group2, group3)

        # Cohen's d效果量
        d_12 = cohens_d(group1.values, group2.values)
        d_13 = cohens_d(group1.values, group3.values)
        d_23 = cohens_d(group2.values, group3.values)

        results.append({
            '变量': var_name,
            '中心M(SD)': f"{group1.mean():.3f}({group1.std():.3f})",
            '次中心M(SD)': f"{group2.mean():.3f}({group2.std():.3f})",
            '边缘M(SD)': f"{group3.mean():.3f}({group3.std():.3f})",
            'F值': round(f_stat, 2),
            'p值': '<0.001' if p_anova < 0.001 else f'{p_anova:.3f}',
            'eta^2': round(eta2, 3),
            '中心vs次中心p': '<0.001' if p_12 < 0.001 else f'{p_12:.3f}',
            '中心vs边缘p': '<0.001' if p_13 < 0.001 else f'{p_13:.3f}',
            '次中心vs边缘p': '<0.001' if p_23 < 0.001 else f'{p_23:.3f}',
            "中心vs边缘d": round(d_13, 3)
        })

    return pd.DataFrame(results)


def plot_prototype_boxplot(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制原型梯度三组核心变量差异比较箱线图（图16）

    Parameters
    ----------
    df : pd.DataFrame
        带原型梯度的数据
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
    font_en = fm.FontProperties(fname=font_paths['english'], size=10)

    # 调整图表尺寸，减少垂直空白
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    variables = ['cognitive_accessibility', 'mapping_direction', 'mahalanobis_distance']
    var_names = ['认知通达度', '映射方向', '马氏距离']

    # 为每个子图设置优化的Y轴范围，减少空白
    ylim_settings = {
        'cognitive_accessibility': (0.5, 5.3),
        'mapping_direction': (0.5, 4.3),
        'mahalanobis_distance': (-0.3, 5.5)
    }

    # 三组原型梯度使用不同颜色（与图16/5-6配色一致）
    # 中心成员：蓝色，次中心成员：绿色，边缘成员：红色
    grade_colors = ['#3498db', '#27ae60', '#e74c3c']
    grade_labels = ['中心成员', '次中心成员', '边缘成员']

    # 固定随机种子保证可重复性
    np.random.seed(42)

    for ax, var, var_name in zip(axes, variables, var_names):
        # 准备数据
        data = [df[df['prototype_grade'] == g][var].dropna() for g in [1, 2, 3]]

        # 箱线图 - 统一宽度，每组不同颜色
        bp = ax.boxplot(data, labels=grade_labels, patch_artist=True,
                       widths=0.55,  # 稍宽的箱体，更饱满
                       flierprops=dict(marker='o', markersize=4, alpha=0.6))

        # 为每个箱体设置不同颜色
        for patch, color in zip(bp['boxes'], grade_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
            patch.set_edgecolor('black')
            patch.set_linewidth(1.2)

        # 设置中位线颜色
        for median in bp['medians']:
            median.set_color('black')
            median.set_linewidth(1.5)

        # 设置须线颜色
        for whisker in bp['whiskers']:
            whisker.set_color('gray')
            whisker.set_linewidth(1.0)

        for cap in bp['caps']:
            cap.set_color('gray')
            cap.set_linewidth(1.0)

        # 添加散点（抖动）- 减小大小，增加透明度，使用对应颜色
        for i, (d, color) in enumerate(zip(data, grade_colors)):
            # 根据数据量调整抖动范围
            jitter_width = 0.12 if len(d) < 500 else 0.15
            x = np.random.normal(i + 1, jitter_width, size=len(d))
            ax.scatter(x, d, alpha=0.15, s=6, c=color, edgecolors='none')

        # 添加均值标记（红色菱形）
        means = [d.mean() for d in data]
        ax.scatter([1, 2, 3], means, marker='D', s=70, c='darkred',
                  edgecolors='white', linewidths=1, zorder=5, label='均值')

        ax.set_ylabel(var_name, fontproperties=font_cn, fontsize=12)
        ax.set_xticklabels(grade_labels, fontproperties=font_cn, fontsize=11)
        ax.tick_params(axis='y', labelsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # 设置优化的Y轴范围，减少空白
        ax.set_ylim(ylim_settings[var])

        # 添加显著性标记 - ANOVA
        f_stat, p_val = stats.f_oneway(*data)
        sig_text = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else 'ns'))

        # 调整ANOVA标注位置，避免与数据重叠
        ax.text(0.98, 0.98, f'ANOVA: F={f_stat:.1f}, {sig_text}',
               transform=ax.transAxes, ha='right', va='top',
               fontsize=10, fontproperties=font_en,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                        edgecolor='gray', alpha=0.9))

    # plt.suptitle('图15 原型梯度三组核心变量差异比较箱线图',
                # fontproperties=font_cn_title, fontsize=14, y=0.98)

    # 调整边距，减少空白
    plt.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.12, wspace=0.25)

    return fig


def main():
    """主函数"""
    print("=" * 60)
    print("Q1_05_原型梯度.py")
    print("计算马氏距离并划分原型梯度结构")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载聚类数据
    print("\n" + "-" * 40)
    print("1. 加载聚类数据")
    print("-" * 40)
    df = load_clustered_data(paths)
    print(f"样本量: {len(df)}")

    # 2. 计算马氏距离并划分原型梯度
    print("\n" + "-" * 40)
    print("2. 计算马氏距离并划分原型梯度")
    print("-" * 40)
    df_with_grades = calculate_mahalanobis_distance(df)

    # 原型梯度分布
    print("\n原型梯度分布:")
    for grade in [1, 2, 3]:
        n = (df_with_grades['prototype_grade'] == grade).sum()
        pct = n / len(df_with_grades) * 100
        print(f"  {PROTOTYPE_DISTANCE_LABELS[grade]}: n={n} ({pct:.1f}%)")

    # 3. 创建表61
    print("\n" + "-" * 40)
    print("3. 保存表63: 原型梯度分布")
    print("-" * 40)
    dist_table = create_prototype_distribution_table(df_with_grades)
    print(dist_table.to_string(index=False))
    save_table(dist_table, "原型梯度分布", global_num=63,
               title="原型梯度分布", formats=['csv', 'json'])

    # 4. 创建表62
    print("\n" + "-" * 40)
    print("4. 保存表64: 原型梯度间差异检验")
    print("-" * 40)
    comparison_table = perform_grade_comparison(df_with_grades)
    print(comparison_table.to_string(index=False))
    save_table(comparison_table, "原型梯度间差异检验", global_num=64,
               title="原型梯度间差异检验", formats=['csv', 'json'])

    # 5. 绘制图15
    print("\n" + "-" * 40)
    print("5. 绘制图16: 原型梯度三组核心变量差异比较箱线图")
    print("-" * 40)
    fig = plot_prototype_boxplot(df_with_grades, paths)
    save_figure(fig, "原型梯度核心变量差异箱线图", global_num=16,
                title="原型梯度三组核心变量差异比较箱线图")

    # 6. 保存带原型梯度的数据
    output_path = paths['output_data'] / 'CFMC_with_prototype_grades.csv'
    df_with_grades.to_csv(output_path, index=True, encoding='utf-8-sig')
    print(f"\n[OK] 已保存带原型梯度的数据: {output_path}")

    print("\n" + "=" * 60)
    print("Q1_05_原型梯度 完成")
    print("=" * 60)

    return df_with_grades, dist_table, comparison_table


if __name__ == "__main__":
    df_with_grades, dist_table, comparison_table = main()
