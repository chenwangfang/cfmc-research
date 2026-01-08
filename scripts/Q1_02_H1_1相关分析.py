#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_02_H1-1相关分析.py
=====================
验证认知通达度与概念复杂度的相关关系（H1-1）

假设H1-1: 认知通达度与概念复杂度呈显著负相关（r ~= -0.40至-0.60）

输出：
- 图14: 认知通达度x概念复杂度散点图（含95%置信区间）
- 表60: 双维度相关分析

验证标准：r ~= -0.40至-0.60，p < 0.001

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
from scipy.stats import pearsonr, spearmanr
import seaborn as sns

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, format_stats, format_correlation_matrix,
    fix_axis_labels, fix_colorbar_label
)


def calculate_correlations(df: pd.DataFrame) -> dict:
    """
    计算双维度（认知通达度x概念复杂度）相关分析

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    dict
        包含各类相关系数的字典
    """
    ca = df['cognitive_accessibility'].dropna()
    cc = df['conceptual_complexity'].dropna()

    # 对齐数据
    valid_idx = ca.index.intersection(cc.index)
    ca_aligned = ca.loc[valid_idx]
    cc_aligned = cc.loc[valid_idx]

    results = {
        'n': len(valid_idx),
        'ca_mean': ca_aligned.mean(),
        'ca_sd': ca_aligned.std(),
        'cc_mean': cc_aligned.mean(),
        'cc_sd': cc_aligned.std()
    }

    # Pearson相关
    r_pearson, p_pearson = pearsonr(ca_aligned, cc_aligned)
    results['pearson_r'] = r_pearson
    results['pearson_p'] = p_pearson

    # Spearman相关（有序变量更适合）
    r_spearman, p_spearman = spearmanr(ca_aligned, cc_aligned)
    results['spearman_r'] = r_spearman
    results['spearman_p'] = p_spearman

    # Kendall's tau
    tau, p_tau = stats.kendalltau(ca_aligned, cc_aligned)
    results['kendall_tau'] = tau
    results['kendall_p'] = p_tau

    # 95%置信区间（Fisher z变换）
    n = len(valid_idx)
    z = np.arctanh(r_pearson)
    se = 1 / np.sqrt(n - 3)
    z_lower = z - 1.96 * se
    z_upper = z + 1.96 * se
    results['ci_lower'] = np.tanh(z_lower)
    results['ci_upper'] = np.tanh(z_upper)

    # 决定系数
    results['r_squared'] = r_pearson ** 2

    return results


def verify_h1_1(results: dict) -> dict:
    """
    验证假设H1-1

    Parameters
    ----------
    results : dict
        相关分析结果

    Returns
    -------
    dict
        假设验证结果
    """
    r = results['pearson_r']
    p = results['pearson_p']

    # H1-1验证标准：r ~= -0.40至-0.60，p < 0.001
    verification = {
        '假设': 'H1-1',
        '预期范围': '-0.40 至 -0.60',
        '实际r值': round(r, 4),
        'p值': f"< 0.001" if p < 0.001 else f"{p:.4f}",
        '95% CI': f"[{results['ci_lower']:.3f}, {results['ci_upper']:.3f}]",
        '显著性': '是' if p < 0.001 else '否',
        '方向正确': '是' if r < 0 else '否',
        '强度符合': '是' if -0.60 <= r <= -0.40 else ('接近' if -0.70 <= r <= -0.30 else '否')
    }

    # 综合判断
    if p < 0.001 and r < 0 and -0.70 <= r <= -0.30:
        verification['验证结论'] = '支持'
        verification['支持程度'] = '强' if -0.60 <= r <= -0.40 else '中等'
    elif p < 0.05 and r < 0:
        verification['验证结论'] = '部分支持'
        verification['支持程度'] = '弱'
    else:
        verification['验证结论'] = '不支持'
        verification['支持程度'] = '无'

    return verification


def create_correlation_table(df: pd.DataFrame, results: dict) -> pd.DataFrame:
    """
    创建双维度相关分析表（表60）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据
    results : dict
        相关分析结果

    Returns
    -------
    pd.DataFrame
        相关分析表
    """
    # 构建表格
    table_data = [
        {
            '分析项目': '样本量',
            '值': results['n']
        },
        {
            '分析项目': '认知通达度 M (SD)',
            '值': f"{results['ca_mean']:.3f} ({results['ca_sd']:.3f})"
        },
        {
            '分析项目': '概念复杂度 M (SD)',
            '值': f"{results['cc_mean']:.3f} ({results['cc_sd']:.3f})"
        },
        {
            '分析项目': 'Pearson r',
            '值': f"{results['pearson_r']:.4f}"
        },
        {
            '分析项目': 'Pearson p',
            '值': f"< 0.001" if results['pearson_p'] < 0.001 else f"{results['pearson_p']:.4f}"
        },
        {
            '分析项目': '95% CI',
            '值': f"[{results['ci_lower']:.3f}, {results['ci_upper']:.3f}]"
        },
        {
            '分析项目': 'Spearman rho',
            '值': f"{results['spearman_r']:.4f}"
        },
        {
            '分析项目': 'Spearman p',
            '值': f"< 0.001" if results['spearman_p'] < 0.001 else f"{results['spearman_p']:.4f}"
        },
        {
            '分析项目': "Kendall's tau",
            '值': f"{results['kendall_tau']:.4f}"
        },
        {
            '分析项目': "Kendall's p",
            '值': f"< 0.001" if results['kendall_p'] < 0.001 else f"{results['kendall_p']:.4f}"
        },
        {
            '分析项目': 'R² (决定系数)',
            '值': f"{results['r_squared']:.4f}"
        },
        {
            '分析项目': '效果量解释',
            '值': '大' if abs(results['pearson_r']) >= 0.5 else ('中等' if abs(results['pearson_r']) >= 0.3 else '小')
        }
    ]

    return pd.DataFrame(table_data)


def plot_scatter_with_ci(df: pd.DataFrame, results: dict, paths: dict) -> plt.Figure:
    """
    绘制认知通达度x概念复杂度散点图（含95%置信区间）（图14）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据
    results : dict
        相关分析结果
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
    cc = df['conceptual_complexity'].dropna()
    valid_idx = ca.index.intersection(cc.index)

    # 转换为numpy数组以确保与scipy/numpy兼容（强制转为float64）
    ca_arr = np.asarray(ca.loc[valid_idx], dtype=np.float64).flatten()
    cc_arr = np.asarray(cc.loc[valid_idx], dtype=np.float64).flatten()

    fig, ax = plt.subplots(figsize=(10, 8))

    # 散点图（带抖动避免重叠）
    jitter_ca = ca_arr + np.random.uniform(-0.1, 0.1, len(ca_arr))
    jitter_cc = cc_arr + np.random.uniform(-0.1, 0.1, len(cc_arr))

    # 使用密度着色
    from scipy.stats import gaussian_kde
    xy = np.vstack([jitter_ca, jitter_cc])
    try:
        z = gaussian_kde(xy)(xy)
        idx = z.argsort()
        x_sorted, y_sorted, z_sorted = jitter_ca[idx], jitter_cc[idx], z[idx]
        scatter = ax.scatter(x_sorted, y_sorted, c=z_sorted, s=20, alpha=0.6,
                            cmap='viridis', edgecolors='none')
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
        cbar.set_label('密度', fontproperties=font_cn, fontsize=11)
        fix_colorbar_label(cbar, rotation=0)
    except Exception as e:
        # 如果密度估计失败，使用简单散点但仍添加颜色信息
        print(f"  [WARN] 密度估计失败: {e}，使用频次着色")
        # 按位置频次着色
        from collections import Counter
        pos_counts = Counter(zip(ca_arr.astype(int), cc_arr.astype(int)))
        colors = [pos_counts[(int(ca_arr[i]), int(cc_arr[i]))] for i in range(len(ca_arr))]
        scatter = ax.scatter(jitter_ca, jitter_cc, c=colors, s=20, alpha=0.6,
                            cmap='viridis', edgecolors='none')
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
        cbar.set_label('频次', fontproperties=font_cn, fontsize=11)
        fix_colorbar_label(cbar, rotation=0)

    # 回归线 - 使用numpy手动计算以避免scipy版本兼容问题
    n = len(ca_arr)
    x_mean = np.mean(ca_arr)
    y_mean = np.mean(cc_arr)
    ss_xy = np.sum((ca_arr - x_mean) * (cc_arr - y_mean))
    ss_xx = np.sum((ca_arr - x_mean) ** 2)
    ss_yy = np.sum((cc_arr - y_mean) ** 2)
    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    r_value = ss_xy / np.sqrt(ss_xx * ss_yy)
    # 计算标准误差
    y_pred = slope * ca_arr + intercept
    residuals = cc_arr - y_pred
    mse = np.sum(residuals**2) / (n - 2)
    std_err = np.sqrt(mse / ss_xx)
    x_line = np.linspace(ca_arr.min(), ca_arr.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'r-', linewidth=2, label='回归线')

    # 95%置信区间带 (n, x_mean, ss_xx已在上方计算)
    se_fit = std_err * np.sqrt(1/n + (x_line - x_mean)**2 / ss_xx)
    t_crit = stats.t.ppf(0.975, n - 2)
    ci_upper = y_line + t_crit * se_fit
    ci_lower = y_line - t_crit * se_fit

    ax.fill_between(x_line, ci_lower, ci_upper, color='red', alpha=0.2,
                   label='95% 置信区间')

    # 设置坐标轴
    ax.set_xlabel('认知通达度', fontproperties=font_cn, fontsize=12)
    ax.set_ylabel('概念复杂度', fontproperties=font_cn, fontsize=12)
    # ax.set_title('图14 认知通达度x概念复杂度散点图（含95%置信区间）',
                # fontproperties=font_cn_title, fontsize=14, pad=15)

    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])

    # 统计信息文本框
    r = results['pearson_r']
    p = results['pearson_p']
    p_str = "< 0.001" if p < 0.001 else f"= {p:.3f}"
    stats_text = f"r = {r:.3f}, p {p_str}\n95% CI [{results['ci_lower']:.3f}, {results['ci_upper']:.3f}]\nN = {results['n']}"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props, fontproperties=font_en)

    # H1-1验证结果
    h1_supported = -0.70 <= r <= -0.30 and p < 0.001
    h1_result = "H1-1验证：获得支持" if h1_supported else "H1-1验证：未获支持"
    ax.text(0.95, 0.02, h1_result, transform=ax.transAxes, fontsize=12,
            verticalalignment='bottom', horizontalalignment='right',
            fontproperties=font_cn,
            bbox=dict(boxstyle='round', facecolor='lightgreen' if h1_supported else 'lightyellow', alpha=0.9))

    ax.legend(loc='upper right', prop=font_cn)
    ax.grid(alpha=0.3)

    plt.tight_layout()

    return fig


def main():
    """主函数"""
    print("=" * 60)
    print("Q1_02_H1-1相关分析.py")
    print("验证认知通达度与概念复杂度的相关关系")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 加载数据
    df, meta = load_cfmc_data()
    print(f"数据量: {len(df)} 条")

    # 1. 计算相关系数
    print("\n" + "-" * 40)
    print("1. 双维度相关分析")
    print("-" * 40)
    results = calculate_correlations(df)

    print(f"\n样本量: N = {results['n']}")
    print(f"认知通达度: M = {results['ca_mean']:.3f}, SD = {results['ca_sd']:.3f}")
    print(f"概念复杂度: M = {results['cc_mean']:.3f}, SD = {results['cc_sd']:.3f}")
    p_str = '< 0.001' if results['pearson_p'] < 0.001 else f"= {results['pearson_p']:.4f}"
    print(f"\nPearson r = {results['pearson_r']:.4f}, p {p_str}")
    print(f"95% CI: [{results['ci_lower']:.3f}, {results['ci_upper']:.3f}]")
    print(f"Spearman rho = {results['spearman_r']:.4f}")
    print(f"Kendall tau = {results['kendall_tau']:.4f}")
    print(f"R² = {results['r_squared']:.4f}")

    # 2. 验证H1-1
    print("\n" + "-" * 40)
    print("2. H1-1假设验证")
    print("-" * 40)
    verification = verify_h1_1(results)

    print(f"\n假设H1-1: 认知通达度与概念复杂度呈显著负相关（r ~= -0.40至-0.60）")
    print(f"预期范围: {verification['预期范围']}")
    print(f"实际r值: {verification['实际r值']}")
    print(f"p值: {verification['p值']}")
    print(f"95% CI: {verification['95% CI']}")
    print(f"显著性: {verification['显著性']}")
    print(f"方向正确: {verification['方向正确']}")
    print(f"强度符合: {verification['强度符合']}")
    print(f"\n验证结论: {verification['验证结论']}")
    print(f"支持程度: {verification['支持程度']}")

    # 3. 创建并保存表60
    print("\n" + "-" * 40)
    print("3. 保存表60: 双维度相关分析")
    print("-" * 40)
    corr_table = create_correlation_table(df, results)
    save_table(corr_table, "双维度相关分析", global_num=60,
               title="双维度相关分析", formats=['csv', 'json'])

    # 4. 绘制并保存图14
    print("\n" + "-" * 40)
    print("4. 保存图14: 认知通达度x概念复杂度散点图")
    print("-" * 40)
    fig = plot_scatter_with_ci(df, results, paths)
    save_figure(fig, "认知通达度概念复杂度散点图", global_num=14,
                title="认知通达度x概念复杂度散点图（含95%置信区间）")

    # 5. 保存验证结果
    verification_df = pd.DataFrame([verification])
    save_table(verification_df, "H1_1验证结果", global_num="60a",
               title="H1-1假设验证结果", formats=['csv', 'json'])

    print("\n" + "=" * 60)
    print("Q1_02_H1-1相关分析 完成")
    print("=" * 60)

    return results, verification


if __name__ == "__main__":
    results, verification = main()
