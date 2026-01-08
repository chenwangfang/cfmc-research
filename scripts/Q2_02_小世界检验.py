#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q2_02_小世界检验.py
==================
小世界性质检验（H2核心验证）

输出：
- 图22: 网络聚类系数与平均路径长度对比图
- 表74: 小世界性质检验结果

验证标准：C >= 0.60，L <= 3.0，sigma > 1

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
import warnings
warnings.filterwarnings('ignore')

# 设置随机种子以确保结果可重复
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, HYPOTHESIS_CRITERIA
)


def load_network(paths: dict) -> nx.Graph:
    """加载类型层网络"""
    network_file = paths['output_data'] / 'network_type_layer.graphml'

    if network_file.exists():
        G = nx.read_graphml(network_file)
        print(f"[OK] 已加载网络: {network_file}")
    else:
        # 如果网络文件不存在，重新构建
        print("[WARN] 未找到网络文件，重新构建...")
        from Q2_01_网络构建 import main as build_network
        G, _, _ = build_network()

    return G


def calculate_small_world_metrics(G: nx.Graph) -> dict:
    """
    计算小世界网络指标

    Parameters
    ----------
    G : nx.Graph
        网络图

    Returns
    -------
    dict
        小世界指标
    """
    metrics = {}

    # 确保网络连通
    if not nx.is_connected(G):
        # 取最大连通分量
        largest_cc = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest_cc).copy()
        print(f"  使用最大连通分量: {len(G.nodes())}节点")

    n = G.number_of_nodes()
    m = G.number_of_edges()

    # 基本指标
    metrics['节点数'] = n
    metrics['边数'] = m
    metrics['平均度'] = 2 * m / n if n > 0 else 0

    # 聚类系数
    metrics['聚类系数C'] = nx.average_clustering(G)

    # 平均路径长度
    metrics['平均路径长度L'] = nx.average_shortest_path_length(G) if n > 1 else 0

    # 生成随机网络进行比较
    n_random = 100
    C_random_list = []
    L_random_list = []

    k = int(metrics['平均度'])
    p = 2 * m / (n * (n - 1)) if n > 1 else 0

    for _ in range(n_random):
        try:
            # Erdos-Renyi随机图
            G_random = nx.erdos_renyi_graph(n, p, seed=RANDOM_SEED + _)
            if nx.is_connected(G_random):
                C_random_list.append(nx.average_clustering(G_random))
                L_random_list.append(nx.average_shortest_path_length(G_random))
        except:
            continue

    if C_random_list:
        metrics['随机网络C均值'] = np.mean(C_random_list)
        metrics['随机网络C标准差'] = np.std(C_random_list)
        metrics['随机网络L均值'] = np.mean(L_random_list)
        metrics['随机网络L标准差'] = np.std(L_random_list)

        # 小世界系数
        # sigma = (C/C_random) / (L/L_random)
        C_ratio = metrics['聚类系数C'] / metrics['随机网络C均值'] if metrics['随机网络C均值'] > 0 else 0
        L_ratio = metrics['平均路径长度L'] / metrics['随机网络L均值'] if metrics['随机网络L均值'] > 0 else 0

        metrics['C/C_random'] = C_ratio
        metrics['L/L_random'] = L_ratio
        metrics['小世界系数sigma'] = C_ratio / L_ratio if L_ratio > 0 else 0
    else:
        metrics['随机网络C均值'] = 0
        metrics['随机网络L均值'] = 0
        metrics['小世界系数sigma'] = 0

    # omega系数 (Telesford et al., 2011)
    # omega = L_random/L - C/C_lattice
    # 近似：omega ~= L_random/L - C/1
    if metrics['平均路径长度L'] > 0 and metrics.get('随机网络L均值', 0) > 0:
        metrics['omega系数'] = metrics['随机网络L均值'] / metrics['平均路径长度L'] - metrics['聚类系数C']
    else:
        metrics['omega系数'] = 0

    return metrics


def verify_h2(metrics: dict) -> dict:
    """
    验证H2假设

    Parameters
    ----------
    metrics : dict
        小世界指标

    Returns
    -------
    dict
        验证结果
    """
    criteria = HYPOTHESIS_CRITERIA['H2']

    result = {
        '假设': 'H2',
        '假设内容': '构式网络呈现小世界性质',
        '判断标准': f"C >= {criteria['C']}, L <= {criteria['L']}, sigma > {criteria['sigma']}",
        '实际聚类系数C': round(metrics['聚类系数C'], 4),
        '实际路径长度L': round(metrics['平均路径长度L'], 4),
        '实际小世界系数sigma': round(metrics['小世界系数sigma'], 4)
    }

    # 判断是否支持
    c_pass = metrics['聚类系数C'] >= criteria['C']
    l_pass = metrics['平均路径长度L'] <= criteria['L']
    sigma_pass = metrics['小世界系数sigma'] > criteria['sigma']

    if c_pass and l_pass and sigma_pass:
        result['验证结论'] = '支持'
        result['支持程度'] = '强' if metrics['小世界系数sigma'] > 2.0 else '中等'
    elif (c_pass and l_pass) or (c_pass and sigma_pass) or (l_pass and sigma_pass):
        result['验证结论'] = '部分支持'
        result['支持程度'] = '中等'
    else:
        result['验证结论'] = '不支持'
        result['支持程度'] = '无'

    result['C达标'] = '是' if c_pass else '否'
    result['L达标'] = '是' if l_pass else '否'
    result['sigma达标'] = '是' if sigma_pass else '否'

    return result


def create_small_world_table(metrics: dict, h2_result: dict) -> pd.DataFrame:
    """
    创建小世界性质检验结果表（表74）

    Parameters
    ----------
    metrics : dict
        小世界指标
    h2_result : dict
        H2验证结果

    Returns
    -------
    pd.DataFrame
        检验结果表
    """
    table_data = [
        {'指标': '节点数', '实测值': metrics['节点数'], '标准': '-', '达标': '-'},
        {'指标': '边数', '实测值': metrics['边数'], '标准': '-', '达标': '-'},
        {'指标': '平均度', '实测值': round(metrics['平均度'], 2), '标准': '-', '达标': '-'},
        {'指标': '聚类系数C', '实测值': round(metrics['聚类系数C'], 4), '标准': '>= 0.60', '达标': h2_result['C达标']},
        {'指标': '平均路径长度L', '实测值': round(metrics['平均路径长度L'], 4), '标准': '<= 3.0', '达标': h2_result['L达标']},
        {'指标': '随机网络C', '实测值': round(metrics.get('随机网络C均值', 0), 4), '标准': '-', '达标': '-'},
        {'指标': '随机网络L', '实测值': round(metrics.get('随机网络L均值', 0), 4), '标准': '-', '达标': '-'},
        {'指标': 'C/C_random', '实测值': round(metrics.get('C/C_random', 0), 4), '标准': '> 1', '达标': '是' if metrics.get('C/C_random', 0) > 1 else '否'},
        {'指标': 'L/L_random', '实测值': round(metrics.get('L/L_random', 0), 4), '标准': '~= 1', '达标': '-'},
        {'指标': '小世界系数sigma', '实测值': round(metrics['小世界系数sigma'], 4), '标准': '> 1', '达标': h2_result['sigma达标']},
        {'指标': 'omega系数', '实测值': round(metrics.get('omega系数', 0), 4), '标准': '-1~1', '达标': '-'},
        {'指标': 'H2验证结论', '实测值': h2_result['验证结论'], '标准': '-', '达标': h2_result['支持程度']}
    ]

    return pd.DataFrame(table_data)


def plot_small_world_comparison(metrics: dict, paths: dict) -> plt.Figure:
    """
    绘制网络聚类系数与平均路径长度对比图（图22）

    优化设计：
    - 左图：水平条形图分两行展示C和L，各带阈值线和达标标记
    - 右图：简化为双色区域（非小世界/小世界），去除不准确的"弱/强"分类

    Parameters
    ----------
    metrics : dict
        小世界指标
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
    font_cn_small = fm.FontProperties(fname=font_paths['chinese'], size=10)
    font_en = fm.FontProperties(fname=font_paths['english'], size=10)

    # 使用GridSpec实现灵活布局
    fig = plt.figure(figsize=(14, 6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1], height_ratios=[1, 1],
                          hspace=0.35, wspace=0.3)

    # ============ 左上：聚类系数C ============
    ax1_top = fig.add_subplot(gs[0, 0])

    C_actual = metrics['聚类系数C']
    C_random = metrics.get('随机网络C均值', 0)
    C_threshold = 0.60
    C_ratio = metrics.get('C/C_random', C_actual / C_random if C_random > 0 else 0)

    # 绘制条形（实测值和随机网络）
    bars_c = ['实测值', '随机网络']
    values_c = [C_actual, C_random]
    colors_c = ['#3498DB', '#ABB2B9']
    y_pos_c = [0.6, 0.2]

    for i, (label, val, color, y) in enumerate(zip(bars_c, values_c, colors_c, y_pos_c)):
        ax1_top.barh(y, val, height=0.3, color=color, alpha=0.85, edgecolor='#2C3E50', linewidth=1)
        ax1_top.text(val + 0.02, y, f'{val:.2f}', va='center', ha='left', fontsize=11, fontweight='bold')

    # 阈值线（限制长度，避免与标题重叠）
    ax1_top.plot([C_threshold, C_threshold], [0, 0.85], color='#E74C3C', linestyle='--', linewidth=2.5)
    ax1_top.text(C_threshold, 0.88, f'阈值={C_threshold}', ha='center', va='bottom',
                fontsize=9, color='#E74C3C', fontproperties=font_cn)

    # 达标标记
    if C_actual >= C_threshold:
        ax1_top.text(0.95, 0.6, '✓', ha='center', va='center', fontsize=20, color='#27AE60', fontweight='bold')
        status_c = '达标'
    else:
        ax1_top.text(0.95, 0.6, '✗', ha='center', va='center', fontsize=20, color='#E74C3C', fontweight='bold')
        status_c = '未达标'

    ax1_top.set_xlim(0, 1.0)
    ax1_top.set_ylim(0, 1.0)
    ax1_top.set_yticks(y_pos_c)
    ax1_top.set_yticklabels(bars_c, fontproperties=font_cn, fontsize=10)
    ax1_top.set_xlabel('聚类系数 C（越大越好，≥0.60达标）', fontproperties=font_cn, fontsize=10)
    ax1_top.set_title(f'（a）聚类系数 C = {C_actual:.2f}（C/C_random = {C_ratio:.2f}）',
                     fontproperties=font_cn, fontsize=11)
    ax1_top.grid(axis='x', alpha=0.3)
    ax1_top.spines['top'].set_visible(False)
    ax1_top.spines['right'].set_visible(False)

    # ============ 左下：平均路径长度L ============
    ax1_bottom = fig.add_subplot(gs[1, 0])

    L_actual = metrics['平均路径长度L']
    L_random = metrics.get('随机网络L均值', 0)
    L_threshold = 3.0
    L_ratio = metrics.get('L/L_random', L_actual / L_random if L_random > 0 else 0)

    # 绘制条形
    bars_l = ['实测值', '随机网络']
    values_l = [L_actual, L_random]
    colors_l = ['#3498DB', '#ABB2B9']
    y_pos_l = [0.6, 0.2]

    for i, (label, val, color, y) in enumerate(zip(bars_l, values_l, colors_l, y_pos_l)):
        ax1_bottom.barh(y, val, height=0.3, color=color, alpha=0.85, edgecolor='#2C3E50', linewidth=1)
        ax1_bottom.text(val + 0.05, y, f'{val:.2f}', va='center', ha='left', fontsize=11, fontweight='bold')

    # 阈值线（限制长度，避免与标题重叠）
    ax1_bottom.plot([L_threshold, L_threshold], [0, 0.85], color='#E74C3C', linestyle='--', linewidth=2.5)
    ax1_bottom.text(L_threshold, 0.88, f'阈值={L_threshold}', ha='center', va='bottom',
                   fontsize=9, color='#E74C3C', fontproperties=font_cn)

    # 达标标记（L是越小越好）
    if L_actual <= L_threshold:
        ax1_bottom.text(3.4, 0.6, '✓', ha='center', va='center', fontsize=20, color='#27AE60', fontweight='bold')
        status_l = '达标'
    else:
        ax1_bottom.text(3.4, 0.6, '✗', ha='center', va='center', fontsize=20, color='#E74C3C', fontweight='bold')
        status_l = '未达标'

    ax1_bottom.set_xlim(0, 3.6)
    ax1_bottom.set_ylim(0, 1.0)
    ax1_bottom.set_yticks(y_pos_l)
    ax1_bottom.set_yticklabels(bars_l, fontproperties=font_cn, fontsize=10)
    ax1_bottom.set_xlabel('平均路径长度 L（越小越好，≤3.0达标）', fontproperties=font_cn, fontsize=10)
    ax1_bottom.set_title(f'（b）平均路径长度 L = {L_actual:.2f}（L/L_random = {L_ratio:.2f}）',
                        fontproperties=font_cn, fontsize=11)
    ax1_bottom.grid(axis='x', alpha=0.3)
    ax1_bottom.spines['top'].set_visible(False)
    ax1_bottom.spines['right'].set_visible(False)

    # ============ 右侧：小世界系数sigma检验（合并两行） ============
    ax2 = fig.add_subplot(gs[:, 1])

    sigma = metrics['小世界系数sigma']

    # 简化为双色区域（学术上更准确）
    y_max = max(2.5, sigma + 0.5)

    # 非小世界区域（红色）
    ax2.axhspan(0, 1, alpha=0.25, color='#FADBD8', edgecolor='none')
    ax2.text(0.5, 0.5, '非小世界区域\n(σ ≤ 1)', ha='center', va='center',
            fontsize=11, fontproperties=font_cn, color='#922B21', alpha=0.8)

    # 小世界区域（绿色）
    ax2.axhspan(1, y_max, alpha=0.25, color='#D5F5E3', edgecolor='none')
    ax2.text(0.5, (1 + y_max) / 2, '小世界区域\n(σ > 1)', ha='center', va='center',
            fontsize=11, fontproperties=font_cn, color='#1E8449', alpha=0.8)

    # 临界线（sigma=1）
    ax2.axhline(y=1, color='#2C3E50', linestyle='--', linewidth=2.5, alpha=0.8)
    ax2.text(0.98, 1.05, 'σ = 1 (临界值)', ha='right', va='bottom',
            fontsize=10, fontproperties=font_cn, color='#2C3E50')

    # 实测值水平线
    ax2.axhline(y=sigma, color='#2980B9', linestyle='-', linewidth=2, alpha=0.9)

    # 实测点（大号星形）
    ax2.scatter([0.5], [sigma], s=400, c='#2980B9', marker='*', zorder=5, edgecolors='#1A5276', linewidths=1.5)
    ax2.text(0.58, sigma, f'σ = {sigma:.2f}', ha='left', va='center',
            fontsize=14, fontweight='bold', color='#1A5276')

    # 判断结果框
    if sigma > 1:
        result_text = f'σ = {sigma:.2f} > 1\n✓ 支持小世界性质'
        box_color = '#27AE60'
        box_bg = '#D5F5E3'
    else:
        result_text = f'σ = {sigma:.2f} ≤ 1\n✗ 不支持小世界性质'
        box_color = '#E74C3C'
        box_bg = '#FADBD8'

    ax2.text(0.05, 0.95, result_text, transform=ax2.transAxes,
            ha='left', va='top', fontsize=13, fontproperties=font_cn,
            color=box_color, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=box_bg, alpha=0.95, edgecolor=box_color, linewidth=2))

    # 图例
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#FADBD8', edgecolor='#922B21', alpha=0.5, label='非小世界 (σ≤1)'),
        Patch(facecolor='#D5F5E3', edgecolor='#1E8449', alpha=0.5, label='小世界 (σ>1)'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor='#2980B9', markersize=15, label=f'实测σ={sigma:.2f}')
    ]
    ax2.legend(handles=legend_elements, loc='lower right', prop=font_cn, framealpha=0.95)

    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, y_max)
    ax2.set_ylabel('小世界系数 σ', fontproperties=font_cn, fontsize=11)
    ax2.set_xticks([])
    ax2.set_title('（c）小世界系数 σ 检验', fontproperties=font_cn, fontsize=11)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)

    # plt.suptitle('图22 小世界性质检验结果',
                # fontproperties=font_cn_title, fontsize=14, y=0.98)

    return fig


def sensitivity_analysis(G: nx.Graph, metrics_original: dict, n_trials: int = 100) -> pd.DataFrame:
    """
    敏感性分析：测试小世界性质的稳健性

    Parameters
    ----------
    G : nx.Graph
        原始网络
    metrics_original : dict
        原始指标
    n_trials : int
        模拟次数

    Returns
    -------
    pd.DataFrame
        敏感性分析结果
    """
    import random

    results = []
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()

    # 测试不同扰动水平
    perturbation_levels = [0.05, 0.10, 0.15, 0.20]

    for level in perturbation_levels:
        c_values = []
        l_values = []
        sigma_values = []

        for _ in range(min(n_trials, 20)):  # 减少试验次数以提高效率
            # 复制网络
            G_pert = G.copy()

            # 随机删除一定比例的边
            edges_to_remove = random.sample(list(G_pert.edges()),
                                           int(n_edges * level * 0.5))
            G_pert.remove_edges_from(edges_to_remove)

            # 随机添加同数量的边
            non_edges = list(nx.non_edges(G_pert))
            if len(non_edges) > len(edges_to_remove):
                edges_to_add = random.sample(non_edges, len(edges_to_remove))
                G_pert.add_edges_from(edges_to_add)

            # 确保连通
            if nx.is_connected(G_pert):
                try:
                    c = nx.average_clustering(G_pert)
                    l = nx.average_shortest_path_length(G_pert)
                    c_values.append(c)
                    l_values.append(l)

                    # 计算sigma (简化版)
                    if metrics_original.get('随机网络C均值', 0) > 0 and metrics_original.get('随机网络L均值', 0) > 0:
                        c_ratio = c / metrics_original['随机网络C均值']
                        l_ratio = l / metrics_original['随机网络L均值']
                        sigma_values.append(c_ratio / l_ratio if l_ratio > 0 else 0)
                except:
                    continue

        if c_values:
            results.append({
                '扰动水平': f'{int(level*100)}%',
                'C均值': round(np.mean(c_values), 4),
                'C标准差': round(np.std(c_values), 4),
                'L均值': round(np.mean(l_values), 4),
                'L标准差': round(np.std(l_values), 4),
                'sigma均值': round(np.mean(sigma_values), 2) if sigma_values else '-',
                'C达标率': f"{sum(1 for c in c_values if c >= 0.60)/len(c_values)*100:.0f}%",
                'L达标率': f"{sum(1 for l in l_values if l <= 3.0)/len(l_values)*100:.0f}%",
                '结论稳健': '是' if (np.mean(c_values) >= 0.60 and np.mean(l_values) <= 3.0) else '否'
            })

    return pd.DataFrame(results)


def main():
    """主函数"""
    print("=" * 60)
    print("Q2_02_小世界检验.py")
    print("小世界性质检验（H2核心验证）")
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

    # 2. 计算小世界指标
    print("\n" + "-" * 40)
    print("2. 计算小世界指标")
    print("-" * 40)
    metrics = calculate_small_world_metrics(G)

    print(f"\n小世界指标:")
    print(f"  聚类系数C: {metrics['聚类系数C']:.4f}")
    print(f"  平均路径长度L: {metrics['平均路径长度L']:.4f}")
    print(f"  小世界系数sigma: {metrics['小世界系数sigma']:.4f}")

    # 3. H2假设验证
    print("\n" + "-" * 40)
    print("3. H2假设验证")
    print("-" * 40)
    h2_result = verify_h2(metrics)

    print(f"\nH2验证结果:")
    print(f"  标准: C >= 0.60, L <= 3.0, sigma > 1")
    print(f"  实测: C={metrics['聚类系数C']:.4f}, L={metrics['平均路径长度L']:.4f}, sigma={metrics['小世界系数sigma']:.4f}")
    print(f"  结论: {h2_result['验证结论']} ({h2_result['支持程度']})")

    # 4. 创建表74
    print("\n" + "-" * 40)
    print("4. 保存表74: 小世界性质检验结果")
    print("-" * 40)
    result_table = create_small_world_table(metrics, h2_result)
    print(result_table.to_string(index=False))
    save_table(result_table, "小世界性质检验结果", global_num=74,
               title="小世界性质检验结果", formats=['csv', 'json'])

    # 5. 敏感性分析
    print("\n" + "-" * 40)
    print("5. 敏感性分析（表76）")
    print("-" * 40)
    sensitivity_df = sensitivity_analysis(G, metrics, n_trials=20)
    print(sensitivity_df.to_string(index=False))
    save_table(sensitivity_df, "敏感性分析结果汇总", global_num=76,
               title="小世界性质敏感性分析结果", formats=['csv', 'json'])

    # 6. 绘制图22
    print("\n" + "-" * 40)
    print("6. 绘制图22: 网络聚类系数与平均路径长度对比图")
    print("-" * 40)
    fig = plot_small_world_comparison(metrics, paths)
    save_figure(fig, "小世界性质对比图", global_num=22,
                title="网络聚类系数与平均路径长度对比图")

    print("\n" + "=" * 60)
    print("Q2_02_小世界检验 完成")
    print("=" * 60)

    return metrics, h2_result


if __name__ == "__main__":
    metrics, h2_result = main()
