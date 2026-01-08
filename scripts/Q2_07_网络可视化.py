#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q2_07_网络可视化.py
==================
综合网络可视化

输出：
- 图30: 构式网络综合可视化图（含多视角）

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
from matplotlib.patches import Patch
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, get_font_paths, save_figure, CONSTRUCTION_COLORS,
    MAPPING_DIRECTION_CODES, PROTOTYPE_DISTANCE_LABELS
)


def load_network_and_data(paths: dict) -> tuple:
    """加载网络和相关数据"""
    # 加载网络
    network_file = paths['output_data'] / 'network_type_layer.graphml'
    if network_file.exists():
        G = nx.read_graphml(network_file)
        print(f"[OK] 已加载网络: {network_file}")
    else:
        from Q2_01_网络构建 import main as build_network
        G, _, _ = build_network()

    # 加载构式数据
    proto_file = paths['output_data'] / 'CFMC_with_prototype_grades.csv'
    cluster_file = paths['output_data'] / 'CFMC_with_clusters.csv'

    if proto_file.exists():
        df = pd.read_csv(proto_file, index_col=0)
    elif cluster_file.exists():
        df = pd.read_csv(cluster_file, index_col=0)
    else:
        from utils_公共函数 import load_cfmc_data
        df = load_cfmc_data(paths)

    return G, df


def plot_comprehensive_network(G: nx.Graph, df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制构式网络综合可视化图（图30）

    Parameters
    ----------
    G : nx.Graph
        网络图
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
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=10)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_en = fm.FontProperties(fname=font_paths['english'], size=9)

    fig = plt.figure(figsize=(20, 16))

    # 创建2x2子图布局
    gs = fig.add_gridspec(2, 2, hspace=0.25, wspace=0.2)

    # ========== (a) 基础网络结构 ==========
    ax1 = fig.add_subplot(gs[0, 0])

    pos = nx.spring_layout(G, seed=42, k=2.5)

    # 节点大小基于样本量（使用平方根变换避免差异过大）
    node_sizes = []
    for node in G.nodes():
        size = G.nodes[node].get('size', 100)
        # 将size转换为数值
        try:
            size = float(size)
        except:
            size = 100
        # 平方根变换 + 最小/最大尺寸限制
        size_transformed = max(400, min(2500, 200 + 40 * np.sqrt(size)))
        node_sizes.append(size_transformed)

    # 节点颜色基于认知通达度
    node_colors = []
    for node in G.nodes():
        ca = G.nodes[node].get('ca_mean', 3)
        try:
            ca = float(ca)
        except:
            ca = 3
        # 归一化到0-1
        ca_norm = (ca - 1) / 4
        node_colors.append(plt.cm.RdYlGn(ca_norm))

    nx.draw_networkx_nodes(G, pos, ax=ax1,
                          node_size=node_sizes,
                          node_color=node_colors,
                          alpha=0.85,
                          edgecolors='black',
                          linewidths=1)

    nx.draw_networkx_edges(G, pos, ax=ax1,
                          edge_color='gray',
                          width=1.5,
                          alpha=0.5)

    # 根据背景颜色深浅自动调整标签颜色（RdYlGn：两端深中间浅）
    for node in G.nodes():
        x, y = pos[node]
        ca = G.nodes[node].get('ca_mean', 3)
        try:
            ca = float(ca)
        except:
            ca = 3
        ca_norm = (ca - 1) / 4
        # RdYlGn中：<0.3(红)和>0.7(绿)较深，需要白字
        font_color = 'white' if ca_norm < 0.3 or ca_norm > 0.7 else 'black'
        ax1.text(x, y, node, fontsize=10, fontweight='bold',
                ha='center', va='center', color=font_color)

    ax1.set_title('（a）基础网络结构\n节点大小=样本量，颜色=认知通达度',
                 fontproperties=font_cn, fontsize=20)
    ax1.axis('off')

    # 添加颜色条
    sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=plt.Normalize(vmin=1, vmax=5))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax1, shrink=0.6, aspect=20)
    cbar.set_label('认知通达度', fontproperties=font_cn, fontsize=16)

    # ========== (b) 映射类型视角 ==========
    ax2 = fig.add_subplot(gs[0, 1])

    # 按映射方向着色
    md_colors = {1: '#e74c3c', 2: '#3498db', 3: '#2ecc71', 4: '#f39c12'}
    node_colors_md = []
    for node in G.nodes():
        md = G.nodes[node].get('md_mode', 1)
        try:
            md = int(float(md))
        except:
            md = 1
        node_colors_md.append(md_colors.get(md, '#95a5a6'))

    nx.draw_networkx_nodes(G, pos, ax=ax2,
                          node_size=node_sizes,
                          node_color=node_colors_md,
                          alpha=0.85,
                          edgecolors='black',
                          linewidths=1)

    nx.draw_networkx_edges(G, pos, ax=ax2,
                          edge_color='gray',
                          width=1.5,
                          alpha=0.5)

    # 根据映射类型颜色深浅自动调整标签颜色
    md_font_colors = {1: 'white', 2: 'white', 3: 'white', 4: 'black'}  # 红蓝绿用白字，橙用黑字
    for node in G.nodes():
        x, y = pos[node]
        md = G.nodes[node].get('md_mode', 1)
        try:
            md = int(float(md))
        except:
            md = 1
        font_color = md_font_colors.get(md, 'black')
        ax2.text(x, y, node, fontsize=10, fontweight='bold',
                ha='center', va='center', color=font_color)

    ax2.set_title('（b）映射类型分布\n颜色=映射方向',
                 fontproperties=font_cn, fontsize=20)
    ax2.axis('off')

    # 添加图例
    legend_elements = [Patch(facecolor=color, edgecolor='black',
                            label=MAPPING_DIRECTION_CODES.get(md, f'类型{md}'))
                      for md, color in md_colors.items()]
    ax2.legend(handles=legend_elements, loc='lower left', prop=font_cn, fontsize=8)

    # ========== (c) 链接类型视角 ==========
    ax3 = fig.add_subplot(gs[1, 0])

    # 按链接类型给边着色
    edge_colors_by_type = []
    for u, v, d in G.edges(data=True):
        link_type = d.get('link_type', 'unknown')
        if link_type == 'metaphorical_extension':
            edge_colors_by_type.append('#e74c3c')
        elif link_type == 'polysemy':
            edge_colors_by_type.append('#3498db')
        else:
            edge_colors_by_type.append('#95a5a6')

    nx.draw_networkx_nodes(G, pos, ax=ax3,
                          node_size=node_sizes,
                          node_color='lightblue',
                          alpha=0.85,
                          edgecolors='black',
                          linewidths=1)

    nx.draw_networkx_edges(G, pos, ax=ax3,
                          edge_color=edge_colors_by_type,
                          width=2.5,
                          alpha=0.7)

    nx.draw_networkx_labels(G, pos, ax=ax3,
                           font_size=10,
                           font_weight='bold')

    ax3.set_title('（c）链接类型分布\n红=隐喻扩展，蓝=多义链接',
                 fontproperties=font_cn, fontsize=20)
    ax3.axis('off')

    # 添加边类型图例
    from matplotlib.lines import Line2D
    edge_legend = [
        Line2D([0], [0], color='#e74c3c', linewidth=3, label='隐喻扩展链接'),
        Line2D([0], [0], color='#3498db', linewidth=3, label='多义链接'),
        Line2D([0], [0], color='#95a5a6', linewidth=3, label='其他链接')
    ]
    ax3.legend(handles=edge_legend, loc='lower left', prop=font_cn, fontsize=8)

    # ========== (d) 概念复杂度热力图 ==========
    ax4 = fig.add_subplot(gs[1, 1])

    # 节点颜色基于概念复杂度
    node_colors_cc = []
    for node in G.nodes():
        cc = G.nodes[node].get('cc_mean', 3)
        try:
            cc = float(cc)
        except:
            cc = 3
        # 归一化到0-1
        cc_norm = (cc - 1) / 4
        node_colors_cc.append(plt.cm.YlOrRd(cc_norm))

    nx.draw_networkx_nodes(G, pos, ax=ax4,
                          node_size=node_sizes,
                          node_color=node_colors_cc,
                          alpha=0.85,
                          edgecolors='black',
                          linewidths=1)

    nx.draw_networkx_edges(G, pos, ax=ax4,
                          edge_color='gray',
                          width=1.5,
                          alpha=0.5)

    # 根据概念复杂度颜色深浅自动调整标签颜色（YlOrRd：高值深色需白字）
    for node in G.nodes():
        x, y = pos[node]
        cc = G.nodes[node].get('cc_mean', 3)
        try:
            cc = float(cc)
        except:
            cc = 3
        cc_norm = (cc - 1) / 4
        font_color = 'white' if cc_norm > 0.5 else 'black'
        ax4.text(x, y, node, fontsize=10, fontweight='bold',
                ha='center', va='center', color=font_color)

    ax4.set_title('（d）概念复杂度分布\n颜色深浅=复杂度高低',
                 fontproperties=font_cn, fontsize=20)
    ax4.axis('off')

    # 添加颜色条
    sm2 = plt.cm.ScalarMappable(cmap='YlOrRd', norm=plt.Normalize(vmin=1, vmax=5))
    sm2.set_array([])
    cbar2 = plt.colorbar(sm2, ax=ax4, shrink=0.6, aspect=20)
    cbar2.set_label('概念复杂度', fontproperties=font_cn, fontsize=16)

    # plt.suptitle('图30 构式网络综合可视化图',
                # fontproperties=font_cn_title, fontsize=16, y=0.98)

    return fig


def plot_forceatlas2_layout(G: nx.Graph, df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制ForceAtlas2布局可视化图（图29）

    ForceAtlas2是一种力导向布局算法，特别适合展示社区结构

    Parameters
    ----------
    G : nx.Graph
        网络图
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
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=11)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # 使用spring_layout模拟ForceAtlas2效果
    # ForceAtlas2特点：强调社区结构，中心紧凑，边缘分散
    pos_fa2 = nx.spring_layout(G, seed=42, k=3.0, iterations=100, scale=2.0)

    # 节点大小基于度中心性
    degree_centrality = nx.degree_centrality(G)
    node_sizes = [3000 * (degree_centrality.get(node, 0.1) + 0.1) for node in G.nodes()]

    # 节点颜色基于模块（使用社区检测）
    try:
        from networkx.algorithms import community
        communities = list(community.greedy_modularity_communities(G))
        community_map = {}
        for i, comm in enumerate(communities):
            for node in comm:
                community_map[node] = i
        n_communities = len(communities)
    except:
        community_map = {node: 0 for node in G.nodes()}
        n_communities = 1

    # 使用高对比度的自定义颜色方案
    community_colors = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6', '#F39C12']  # 红、蓝、绿、紫、橙
    node_colors = [community_colors[community_map.get(node, 0) % len(community_colors)] for node in G.nodes()]

    # ========== 左图：ForceAtlas2布局（社区视角） ==========
    ax1 = axes[0]

    nx.draw_networkx_nodes(G, pos_fa2, ax=ax1,
                          node_size=node_sizes,
                          node_color=node_colors,
                          alpha=0.85,
                          edgecolors='black',
                          linewidths=1.5)

    # 边宽度基于权重
    edge_weights = []
    for u, v, d in G.edges(data=True):
        w = d.get('weight', 1)
        try:
            w = float(w)
        except:
            w = 1
        edge_weights.append(w)

    max_w = max(edge_weights) if edge_weights else 1
    edge_widths = [0.2 + 11.8 * (w / max_w) for w in edge_weights]

    nx.draw_networkx_edges(G, pos_fa2, ax=ax1,
                          edge_color='#555555',
                          width=edge_widths,
                          alpha=0.65)

    nx.draw_networkx_labels(G, pos_fa2, ax=ax1,
                           font_size=11,
                           font_weight='bold')

    ax1.set_title('（a）ForceAtlas2布局（社区结构）\n节点大小=度中心性，颜色=社区归属',
                 fontproperties=font_cn, fontsize=20)
    ax1.axis('off')

    # 添加社区图例
    legend_elements = [Patch(facecolor=community_colors[i], edgecolor='black',
                            label=f'社区{i+1}（n={len(communities[i])}）')
                      for i in range(min(n_communities, 5))]
    if legend_elements:
        ax1.legend(handles=legend_elements, loc='lower left', prop=font_cn, fontsize=16)

    # ========== 右图：中心性热力图 ==========
    ax2 = axes[1]

    # 计算betweenness centrality
    betweenness = nx.betweenness_centrality(G)
    node_colors_bc = [betweenness.get(node, 0) for node in G.nodes()]

    nodes = nx.draw_networkx_nodes(G, pos_fa2, ax=ax2,
                                   node_size=node_sizes,
                                   node_color=node_colors_bc,
                                   cmap='plasma',  # 使用plasma配色增强区分度
                                   alpha=0.85,
                                   edgecolors='black',
                                   linewidths=1.5)

    nx.draw_networkx_edges(G, pos_fa2, ax=ax2,
                          edge_color='#555555',
                          width=edge_widths,
                          alpha=0.65)

    # 根据节点颜色深浅自动调整标签颜色（深色背景用白字，浅色背景用黑字）
    bc_min, bc_max = min(node_colors_bc), max(node_colors_bc)
    for node in G.nodes():
        x, y = pos_fa2[node]
        bc_val = betweenness.get(node, 0)
        # 归一化到0-1，plasma色图中<0.5为深色
        bc_norm = (bc_val - bc_min) / (bc_max - bc_min) if bc_max > bc_min else 0.5
        font_color = 'white' if bc_norm < 0.5 else 'black'
        ax2.text(x, y, node, fontsize=11, fontweight='bold',
                ha='center', va='center', color=font_color)

    ax2.set_title('（b）中介中心性分布\n颜色深浅=中介中心性高低',
                 fontproperties=font_cn, fontsize=20)
    ax2.axis('off')

    # 添加颜色条
    sm = plt.cm.ScalarMappable(cmap='plasma',
                               norm=plt.Normalize(vmin=min(node_colors_bc),
                                                  vmax=max(node_colors_bc)))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax2, shrink=0.7, aspect=20)
    cbar.set_label('中介中心性', fontproperties=font_cn, fontsize=20)

    # plt.suptitle('图29 ForceAtlas2布局网络可视化',
                # fontproperties=font_cn_title, fontsize=16, y=0.98)
    plt.tight_layout()

    return fig


def create_network_summary(G: nx.Graph, df: pd.DataFrame) -> None:
    """
    打印网络摘要信息

    Parameters
    ----------
    G : nx.Graph
        网络图
    df : pd.DataFrame
        构式数据
    """
    print("\n网络结构摘要:")
    print("-" * 60)

    print(f"\n基本统计:")
    print(f"  类型节点数: {G.number_of_nodes()}")
    print(f"  边数: {G.number_of_edges()}")
    print(f"  网络密度: {nx.density(G):.4f}")

    if nx.is_connected(G):
        print(f"  直径: {nx.diameter(G)}")
        print(f"  平均路径长度: {nx.average_shortest_path_length(G):.4f}")
    else:
        print(f"  连通分量数: {nx.number_connected_components(G)}")

    print(f"  平均聚类系数: {nx.average_clustering(G):.4f}")

    print(f"\n节点属性摘要:")
    sizes = []
    cas = []
    ccs = []
    for node in G.nodes():
        try:
            sizes.append(float(G.nodes[node].get('size', 0)))
            cas.append(float(G.nodes[node].get('ca_mean', 0)))
            ccs.append(float(G.nodes[node].get('cc_mean', 0)))
        except:
            continue

    if sizes:
        print(f"  样本量: 总计={sum(sizes):.0f}, 均值={np.mean(sizes):.1f}, 范围=[{min(sizes):.0f}, {max(sizes):.0f}]")
    if cas:
        print(f"  认知通达度: 均值={np.mean(cas):.2f}, 范围=[{min(cas):.2f}, {max(cas):.2f}]")
    if ccs:
        print(f"  概念复杂度: 均值={np.mean(ccs):.2f}, 范围=[{min(ccs):.2f}, {max(ccs):.2f}]")

    print(f"\n边属性摘要:")
    link_types = defaultdict(int)
    for u, v, d in G.edges(data=True):
        link_types[d.get('link_type', 'unknown')] += 1

    for lt, count in sorted(link_types.items(), key=lambda x: -x[1]):
        print(f"  {lt}: {count} ({count/G.number_of_edges()*100:.1f}%)")


def main():
    """主函数"""
    print("=" * 60)
    print("Q2_07_网络可视化.py")
    print("综合网络可视化")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载数据
    print("\n" + "-" * 40)
    print("1. 加载网络和数据")
    print("-" * 40)
    G, df = load_network_and_data(paths)
    print(f"网络节点数: {G.number_of_nodes()}")
    print(f"网络边数: {G.number_of_edges()}")
    print(f"数据样本量: {len(df)}")

    # 2. 网络摘要
    print("\n" + "-" * 40)
    print("2. 网络结构摘要")
    print("-" * 40)
    create_network_summary(G, df)

    # 3. 绘制图29: ForceAtlas2布局
    print("\n" + "-" * 40)
    print("3. 绘制图29: ForceAtlas2布局网络可视化")
    print("-" * 40)
    fig_fa2 = plot_forceatlas2_layout(G, df, paths)
    save_figure(fig_fa2, "ForceAtlas2布局网络图", global_num=29,
                title="ForceAtlas2布局网络可视化")

    # 4. 绘制图30
    print("\n" + "-" * 40)
    print("4. 绘制图30: 构式网络综合可视化图")
    print("-" * 40)
    fig = plot_comprehensive_network(G, df, paths)
    save_figure(fig, "构式网络综合可视化图", global_num=30,
                title="构式网络综合可视化图")

    print("\n" + "=" * 60)
    print("Q2_07_网络可视化 完成")
    print("=" * 60)

    return G, df


if __name__ == "__main__":
    G, df = main()
