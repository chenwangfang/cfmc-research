#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q2_06_度分布.py
==============
网络度分布分析

输出：
- 图27: 度分布直方图
- 图29: 度分布对数-对数图（幂律检验）
- 表83: 度分布拟合结果

创建日期：2025-12-05
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import stats
from scipy.optimize import curve_fit
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, get_font_paths, save_figure, save_table
)


def load_network(paths: dict) -> nx.Graph:
    """加载类型层网络"""
    network_file = paths['output_data'] / 'network_type_layer.graphml'

    if network_file.exists():
        G = nx.read_graphml(network_file)
        print(f"[OK] 已加载网络: {network_file}")
    else:
        print("[WARN] 未找到网络文件，重新构建...")
        from Q2_01_网络构建 import main as build_network
        G, _, _ = build_network()

    return G


def analyze_degree_distribution(G: nx.Graph) -> dict:
    """
    分析度分布

    Parameters
    ----------
    G : nx.Graph
        网络图

    Returns
    -------
    dict
        度分布分析结果
    """
    degrees = [d for n, d in G.degree()]
    degree_sequence = sorted(degrees, reverse=True)

    results = {
        '节点数': len(degrees),
        '边数': G.number_of_edges(),
        '平均度': np.mean(degrees),
        '度标准差': np.std(degrees),
        '最小度': min(degrees),
        '最大度': max(degrees),
        '度中位数': np.median(degrees),
        '度众数': Counter(degrees).most_common(1)[0][0] if degrees else 0,
        '度序列': degree_sequence,
        '度频数': Counter(degrees)
    }

    # 计算度分布的偏度和峰度
    if len(degrees) > 2:
        results['偏度'] = stats.skew(degrees)
        results['峰度'] = stats.kurtosis(degrees)

    # 幂律拟合
    try:
        # 排除度为0的节点
        non_zero_degrees = [d for d in degrees if d > 0]
        if non_zero_degrees:
            # 使用最大似然估计幂律指数
            xmin = min(non_zero_degrees)
            alpha = 1 + len(non_zero_degrees) / sum(np.log(np.array(non_zero_degrees) / xmin))
            results['幂律指数α'] = alpha
            results['xmin'] = xmin
    except:
        results['幂律指数α'] = None

    return results


def fit_power_law(degrees: list) -> tuple:
    """
    拟合幂律分布

    Parameters
    ----------
    degrees : list
        度序列

    Returns
    -------
    tuple
        (幂律指数, R²)
    """
    # 计算度频数
    degree_count = Counter(degrees)

    # 排除度为0
    k_values = sorted([k for k in degree_count.keys() if k > 0])
    p_values = [degree_count[k] / len(degrees) for k in k_values]

    if len(k_values) < 3:
        return None, 0

    # 对数变换
    log_k = np.log10(k_values)
    log_p = np.log10(p_values)

    # 线性拟合
    try:
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_k, log_p)
        return -slope, r_value**2
    except:
        return None, 0


def create_degree_stats_table(results: dict, G: nx.Graph) -> pd.DataFrame:
    """
    创建度分布拟合结果表（表83）

    Parameters
    ----------
    results : dict
        度分布分析结果
    G : nx.Graph
        网络图

    Returns
    -------
    pd.DataFrame
        统计表
    """
    table_data = [
        {'统计指标': '节点数', '数值': results['节点数']},
        {'统计指标': '边数', '数值': results['边数']},
        {'统计指标': '平均度', '数值': round(results['平均度'], 2)},
        {'统计指标': '度标准差', '数值': round(results['度标准差'], 2)},
        {'统计指标': '最小度', '数值': results['最小度']},
        {'统计指标': '最大度', '数值': results['最大度']},
        {'统计指标': '度中位数', '数值': results['度中位数']},
        {'统计指标': '度众数', '数值': results['度众数']},
        {'统计指标': '偏度', '数值': round(results.get('偏度', 0), 4)},
        {'统计指标': '峰度', '数值': round(results.get('峰度', 0), 4)}
    ]

    if results.get('幂律指数α'):
        table_data.append({'统计指标': '幂律指数α', '数值': round(results['幂律指数α'], 4)})

    # 添加各节点度数
    for node in sorted(G.nodes()):
        table_data.append({
            '统计指标': f'{node}的度',
            '数值': G.degree(node)
        })

    return pd.DataFrame(table_data)


def plot_degree_histogram(results: dict, paths: dict) -> plt.Figure:
    """
    绘制度分布直方图（图27）

    修复问题：
    1. 子图(a)改用离散条形图，显示所有度值（包括频数为0的）
    2. 子图(b)修正累积分布计算：每个度值对应一个P(X>=k)
    3. 统一配色方案为蓝色系
    4. 简化统计信息显示

    Parameters
    ----------
    results : dict
        度分布分析结果
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

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    degree_sequence = results['度序列']
    degree_count = results['度频数']
    n_nodes = results['节点数']

    # 左图：度分布条形图（离散）
    ax1 = axes[0]

    # 创建完整的度值范围（包括频数为0的度值）
    k_min = results['最小度']
    k_max = results['最大度']
    k_all = list(range(k_min, k_max + 1))
    counts_all = [degree_count.get(k, 0) for k in k_all]

    # 使用统一的蓝色系
    bars = ax1.bar(k_all, counts_all, color='#3498db', alpha=0.85,
                   edgecolor='#2980b9', linewidth=1.2, width=0.6)

    # 在柱子上方添加频数标签
    for bar, count in zip(bars, counts_all):
        if count > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax1.set_xlabel('度 (k)', fontproperties=font_cn, fontsize=11)
    ax1.set_ylabel('频数', fontproperties=font_cn, fontsize=11)
    ax1.set_title('（a）度分布直方图', fontproperties=font_cn, fontsize=12)
    ax1.set_xticks(k_all)
    ax1.set_ylim(0, max(counts_all) + 1)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # 简化统计信息：放在图内左上角，明确标注类型层网络
    stats_text = f'类型层网络（n={results["节点数"]}）\n$\\bar{{k}}$={results["平均度"]:.2f}, 范围=[{k_min}, {k_max}]'
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
            ha='left', va='top', fontproperties=font_cn, fontsize=10,
            color='#2c3e50', linespacing=1.5)

    # 右图：累积度分布 CCDF（修正计算方法）
    ax2 = axes[1]

    # 正确计算累积分布 P(X >= k)
    # 对于每个唯一的度值k，计算有多少节点的度 >= k
    k_unique = sorted(set(degree_sequence))
    ccdf_values = []
    for k in k_unique:
        count_ge_k = sum(1 for d in degree_sequence if d >= k)
        ccdf_values.append(count_ge_k / n_nodes)

    # 绘制散点和阶梯线
    ax2.scatter(k_unique, ccdf_values, s=80, c='#3498db', edgecolors='#2980b9',
                linewidth=1.5, zorder=3, alpha=0.9)

    # 添加阶梯线连接散点，更清晰展示累积分布
    ax2.step(k_unique, ccdf_values, where='post', color='#3498db',
             alpha=0.5, linewidth=2, linestyle='-')

    # 在散点旁标注概率值
    for k, p in zip(k_unique, ccdf_values):
        ax2.annotate(f'{p:.2f}', (k, p), textcoords='offset points',
                    xytext=(8, 0), fontsize=9, color='#2c3e50')

    ax2.set_xlabel('度 (k)', fontproperties=font_cn, fontsize=11)
    ax2.set_ylabel('累积概率 P(X ≥ k)', fontproperties=font_cn, fontsize=11)
    ax2.set_title('（b）累积度分布', fontproperties=font_cn, fontsize=12)
    ax2.set_xticks(k_all)  # 与左图X轴刻度统一
    ax2.set_ylim(0, 1.1)
    ax2.set_xlim(k_min - 0.5, k_max + 0.5)
    ax2.grid(alpha=0.3, linestyle='--')

    # plt.suptitle('图27 度分布分析（类型层网络）', fontproperties=font_cn_title, fontsize=14, y=1.02)
    plt.tight_layout()

    return fig


def plot_degree_log_log(results: dict, paths: dict) -> plt.Figure:
    """
    绘制度分布对数-对数图（图29）

    Parameters
    ----------
    results : dict
        度分布分析结果
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

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    degree_count = results['度频数']
    total = results['节点数']

    # 准备数据
    k_values = sorted([k for k in degree_count.keys() if k > 0])
    p_values = [degree_count[k] / total for k in k_values]

    # 左图：对数-对数散点图
    ax1 = axes[0]

    ax1.scatter(k_values, p_values, alpha=0.8, s=100, c='#3498db', edgecolors='black')

    # 幂律拟合
    alpha, r2 = fit_power_law(results['度序列'])
    if alpha and len(k_values) >= 2:
        # 绘制拟合线
        k_fit = np.linspace(min(k_values), max(k_values), 100)
        # P(k) = C * k^(-alpha)
        C = p_values[0] * (k_values[0] ** alpha)
        p_fit = C * (k_fit ** (-alpha))
        ax1.plot(k_fit, p_fit, 'r--', linewidth=2,
                label=f'幂律拟合: $\\alpha$={alpha:.2f}, $R^2$={r2:.3f}')
        ax1.legend(prop=font_cn)

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('度 k (对数尺度)', fontproperties=font_cn, fontsize=11)
    ax1.set_ylabel('P(k) (对数尺度)', fontproperties=font_cn, fontsize=11)
    ax1.set_title('（a）度分布对数-对数图', fontproperties=font_cn, fontsize=12)
    ax1.grid(alpha=0.3)

    # 右图：与理论分布比较
    ax2 = axes[1]

    # 泊松分布（随机网络）
    mean_degree = results['平均度']
    k_range = np.arange(0, max(k_values) + 1)
    poisson_p = stats.poisson.pmf(k_range, mean_degree)

    ax2.bar(k_values, p_values, alpha=0.6, color='#3498db', label='实际分布', width=0.4)
    ax2.plot(k_range, poisson_p, 'ro-', alpha=0.8, label=f'泊松分布(λ={mean_degree:.2f})')

    ax2.set_xlabel('度 k', fontproperties=font_cn, fontsize=11)
    ax2.set_ylabel('P(k)', fontproperties=font_cn, fontsize=11)
    ax2.set_title('（b）与泊松分布比较', fontproperties=font_cn, fontsize=12)
    ax2.legend(prop=font_cn)
    ax2.grid(axis='y', alpha=0.3)

    # plt.suptitle('图28 度分布对数-对数图（幂律检验）',
                # fontproperties=font_cn_title, fontsize=14, y=1.02)
    plt.tight_layout()

    return fig


def test_degree_distribution_type(results: dict) -> str:
    """
    检验度分布类型

    Parameters
    ----------
    results : dict
        度分布分析结果

    Returns
    -------
    str
        分布类型判断
    """
    degrees = results['度序列']

    # KS检验：与泊松分布比较
    mean_degree = results['平均度']
    ks_stat, ks_p = stats.kstest(degrees, 'poisson', args=(mean_degree,))

    # 偏度检验
    skewness = results.get('偏度', 0)

    # 判断分布类型
    if ks_p > 0.05:
        dist_type = "接近泊松分布（随机网络特征）"
    elif skewness > 1:
        dist_type = "右偏分布（可能存在枢纽节点）"
    else:
        dist_type = "其他分布类型"

    return dist_type


def main():
    """主函数"""
    print("=" * 60)
    print("Q2_06_度分布.py")
    print("网络度分布分析")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载网络
    print("\n" + "-" * 40)
    print("1. 加载网络")
    print("-" * 40)
    G = load_network(paths)
    print(f"节点数: {G.number_of_nodes()}")
    print(f"边数: {G.number_of_edges()}")

    # 2. 分析度分布
    print("\n" + "-" * 40)
    print("2. 分析度分布")
    print("-" * 40)
    results = analyze_degree_distribution(G)

    print(f"\n度分布统计:")
    print(f"  平均度: {results['平均度']:.2f}")
    print(f"  度标准差: {results['度标准差']:.2f}")
    print(f"  度范围: [{results['最小度']}, {results['最大度']}]")
    print(f"  偏度: {results.get('偏度', 0):.4f}")
    print(f"  峰度: {results.get('峰度', 0):.4f}")

    if results.get('幂律指数α'):
        print(f"  幂律指数α: {results['幂律指数α']:.4f}")

    # 分布类型判断
    dist_type = test_degree_distribution_type(results)
    print(f"\n分布类型判断: {dist_type}")

    # 3. 创建表83
    print("\n" + "-" * 40)
    print("3. 保存表83: 度分布拟合结果")
    print("-" * 40)
    stats_table = create_degree_stats_table(results, G)
    print(stats_table.to_string(index=False))
    save_table(stats_table, "度分布拟合结果", global_num=84,
               title="度分布拟合结果", formats=['csv', 'json'])

    # 4. 绘制图27
    print("\n" + "-" * 40)
    print("4. 绘制图27: 度分布直方图")
    print("-" * 40)
    fig6 = plot_degree_histogram(results, paths)
    save_figure(fig6, "度分布直方图", global_num=27,
                title="度分布直方图")

    # 5. 绘制图28
    print("\n" + "-" * 40)
    print("5. 绘制图28: 度分布对数-对数图")
    print("-" * 40)
    fig7 = plot_degree_log_log(results, paths)
    save_figure(fig7, "度分布对数对数图", global_num=28,
                title="度分布对数-对数图（幂律检验）")

    print("\n" + "=" * 60)
    print("Q2_06_度分布 完成")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
