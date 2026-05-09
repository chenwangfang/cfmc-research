#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q2_05_模块检测.py
================
社区/模块检测（模块度优化）

输出：
- 图22: 网络社区结构可视化图
- 表77: 社区检测结果
- 表82a: 社区与构式类型对应表

验证标准：模块度Q >= 0.40

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
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# 优先使用python-louvain；不可用时回退到NetworkX贪婪模块度优化，并在输出中记录实际算法。
try:
    import community as community_louvain
    HAS_COMMUNITY = True
except ImportError:
    HAS_COMMUNITY = False
    print("[WARN] python-louvain未安装，将使用networkx内置方法")

from utils_公共函数 import (
    get_paths, get_font_paths, save_figure, save_table, CONSTRUCTION_COLORS
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


def detect_communities(G: nx.Graph) -> tuple:
    """
    检测网络社区

    Parameters
    ----------
    G : nx.Graph
        网络图

    Returns
    -------
    tuple
        (社区划分字典, 模块度Q, 实际算法名称)
    """
    if HAS_COMMUNITY:
        # 使用Louvain算法
        partition = community_louvain.best_partition(G, random_state=42)
        modularity = community_louvain.modularity(partition, G)
        algorithm_name = "Louvain (python-louvain)"
        print(f"  使用Louvain算法")
    else:
        # 使用networkx内置的贪婪模块度优化
        from networkx.algorithms.community import greedy_modularity_communities
        communities = list(greedy_modularity_communities(G))

        # 转换为partition格式
        partition = {}
        for i, comm in enumerate(communities):
            for node in comm:
                partition[node] = i

        # 计算模块度
        modularity = nx.algorithms.community.modularity(G, communities)
        algorithm_name = "NetworkX greedy modularity"
        print(f"  使用贪婪模块度优化算法")

    print(f"  检测到 {len(set(partition.values()))} 个社区")
    print(f"  模块度Q = {modularity:.4f}")
    print(f"  实际算法: {algorithm_name}")

    return partition, modularity, algorithm_name


def create_community_table(G: nx.Graph, partition: dict,
                           modularity: float,
                           algorithm_name: str) -> pd.DataFrame:
    """
    创建社区检测结果表（表77）

    Parameters
    ----------
    G : nx.Graph
        网络图
    partition : dict
        社区划分
    modularity : float
        模块度
    algorithm_name : str
        实际使用的社区检测算法

    Returns
    -------
    pd.DataFrame
        社区检测结果表
    """
    # 统计每个社区的信息
    community_stats = defaultdict(lambda: {
        'nodes': [],
        'size': 0,
        'total_size': 0,
        'internal_edges': 0,
        'ca_sum': 0,
        'cc_sum': 0
    })

    for node, comm_id in partition.items():
        community_stats[comm_id]['nodes'].append(node)
        community_stats[comm_id]['size'] += 1

        node_data = dict(G.nodes.get(node, {}))
        community_stats[comm_id]['total_size'] += node_data.get('size', 0)
        community_stats[comm_id]['ca_sum'] += node_data.get('ca_mean', 0)
        community_stats[comm_id]['cc_sum'] += node_data.get('cc_mean', 0)

    # 计算社区内边数
    for u, v in G.edges():
        if partition.get(u) == partition.get(v):
            community_stats[partition[u]]['internal_edges'] += 1

    table_data = []
    for comm_id in sorted(community_stats.keys()):
        stats = community_stats[comm_id]
        n = stats['size']

        table_data.append({
            '社区编号': f'C{comm_id + 1}',
            '节点数': n,
            '成员构式': ', '.join(sorted(stats['nodes'])),
            '社区内边数': stats['internal_edges'],
            '模块度Q': round(modularity, 4),
            '社区检测算法': algorithm_name,
            '平均认知通达度': round(stats['ca_sum'] / n, 2) if n > 0 else 0,
            '平均概念复杂度': round(stats['cc_sum'] / n, 2) if n > 0 else 0,
            '样本总量': int(stats['total_size'])
        })

    # 添加整体信息
    table_data.append({
        '社区编号': '整体',
        '节点数': len(partition),
        '成员构式': f'共{len(set(partition.values()))}个社区',
        '社区内边数': sum(s['internal_edges'] for s in community_stats.values()),
        '模块度Q': round(modularity, 4),
        '社区检测算法': algorithm_name,
        '平均认知通达度': '-',
        '平均概念复杂度': '-',
        '样本总量': sum(int(s['total_size']) for s in community_stats.values())
    })

    return pd.DataFrame(table_data)


def create_community_type_mapping(partition: dict, algorithm_name: str) -> pd.DataFrame:
    """
    创建社区与构式类型对应表（表82a）

    Parameters
    ----------
    partition : dict
        社区划分
    algorithm_name : str
        实际使用的社区检测算法

    Returns
    -------
    pd.DataFrame
        对应表
    """
    table_data = []

    for node, comm_id in sorted(partition.items(), key=lambda x: (x[1], x[0])):
        table_data.append({
            '构式类型': node,
            '所属社区': f'C{comm_id + 1}',
            '社区检测算法': algorithm_name
        })

    return pd.DataFrame(table_data)


def plot_community_structure(G: nx.Graph, partition: dict,
                            modularity: float, paths: dict) -> plt.Figure:
    """
    绘制网络社区结构可视化图（图22）

    Parameters
    ----------
    G : nx.Graph
        网络图
    partition : dict
        社区划分
    modularity : float
        模块度
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
    font_en = fm.FontProperties(fname=font_paths['english'], size=10)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 左图：社区结构网络图
    ax1 = axes[0]

    # 使用spring布局
    pos = nx.spring_layout(G, seed=42, k=2)

    # 按社区着色
    n_communities = len(set(partition.values()))
    community_colors = plt.cm.Set3(np.linspace(0, 1, max(n_communities, 3)))

    node_colors = [community_colors[partition.get(node, 0)] for node in G.nodes()]
    # 使用对数缩放使节点大小差异更明显
    node_sizes = [np.log1p(G.nodes[n].get('size', 100)) * 80 for n in G.nodes()]

    # 绘制节点
    nx.draw_networkx_nodes(G, pos, ax=ax1,
                          node_color=node_colors,
                          node_size=node_sizes,
                          alpha=0.8)

    # 绘制边（社区内边用实线，社区间边用虚线）
    internal_edges = [(u, v) for u, v in G.edges()
                     if partition.get(u) == partition.get(v)]
    external_edges = [(u, v) for u, v in G.edges()
                     if partition.get(u) != partition.get(v)]

    nx.draw_networkx_edges(G, pos, ax=ax1,
                          edgelist=internal_edges,
                          edge_color='gray', width=2, alpha=0.8)
    nx.draw_networkx_edges(G, pos, ax=ax1,
                          edgelist=external_edges,
                          edge_color='gray', width=0.5, alpha=0.3,
                          style='dashed')

    nx.draw_networkx_labels(G, pos, ax=ax1, font_size=9)

    ax1.set_title(f'（a）社区结构（Q={modularity:.3f}）', fontproperties=font_cn, fontsize=12)
    ax1.axis('off')

    # 添加社区图例（显示完整成员列表 + 语义说明）
    # 计算各社区的认知通达度均值来确定语义标签
    comm_ca_means = {}
    for comm_id in set(partition.values()):
        members = [n for n, c in partition.items() if c == comm_id]
        ca_values = [G.nodes[n].get('ca_mean', 0) for n in members]
        comm_ca_means[comm_id] = np.mean(ca_values)

    legend_elements = []
    for comm_id in sorted(set(partition.values())):
        members = [n for n, c in partition.items() if c == comm_id]
        # 按数字排序（T1, T2, ..., T9, T10, T11, T12）
        members_sorted = sorted(members, key=lambda x: int(x[1:]))
        # 根据认知通达度均值确定语义标签（与图21一致）
        # 认知通达度1-5级：1=最难通达，5=最易通达
        # T1-T4 均值≈2.0 = 低通达度；T5-T8 均值≈3.0 = 中通达度；T9-T12 均值≈4.5 = 高通达度
        ca_mean = comm_ca_means[comm_id]
        if ca_mean <= 2.5:
            semantic_label = "低通达度"
        elif ca_mean <= 3.5:
            semantic_label = "低-中通达度"
        else:
            semantic_label = "高通达度"
        # 完整显示社区成员 + 语义标签
        legend_elements.append(plt.scatter([], [], c=[community_colors[comm_id]],
                                          s=100, label=f'C{comm_id+1} ({semantic_label}): {", ".join(members_sorted)}'))

    # 添加节点大小说明
    legend_elements.append(plt.scatter([], [], c='gray', s=50, alpha=0.5,
                                       label='节点大小 ∝ 样本量'))

    # 图例放置在图外下方，避免遮挡节点
    ax1.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, -0.05),
               prop=font_cn, fontsize=9, framealpha=0.95, edgecolor='gray')

    # 右图：社区大小分布
    ax2 = axes[1]

    community_sizes = defaultdict(int)
    for node, comm_id in partition.items():
        community_sizes[comm_id] += 1

    comm_ids = sorted(community_sizes.keys())
    sizes = [community_sizes[c] for c in comm_ids]
    colors = [community_colors[c] for c in comm_ids]
    labels = [f'C{c+1}' for c in comm_ids]

    # 调整柱子宽度，避免太宽
    bar_width = 0.5 if len(labels) <= 3 else 0.7
    bars = ax2.bar(labels, sizes, width=bar_width, color=colors, alpha=0.8, edgecolor='black')

    # 添加数值标签
    for bar, size in zip(bars, sizes):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(size), ha='center', va='bottom', fontsize=11)

    ax2.set_xlabel('社区', fontproperties=font_cn, fontsize=11)
    ax2.set_ylabel('节点数', fontproperties=font_cn, fontsize=11)
    ax2.set_title('（b）社区规模分布', fontproperties=font_cn, fontsize=12)
    ax2.grid(axis='y', alpha=0.3)

    # 添加平均规模线
    avg_size = len(partition) / len(set(partition.values()))
    ax2.axhline(y=avg_size, color='#c0392b', linestyle='--', linewidth=1.5, alpha=0.7)
    # 文本放在图内中央位置
    ax2.text(0.5, avg_size + 0.3, f'平均规模={avg_size:.1f}',
             fontproperties=font_cn, fontsize=10, color='#c0392b', ha='center')

    # plt.suptitle('图22 网络社区结构可视化图',
                # fontproperties=font_cn_title, fontsize=14, y=1.02)
    plt.tight_layout()

    return fig


def analyze_community_characteristics(G: nx.Graph, partition: dict) -> None:
    """
    分析社区特征

    Parameters
    ----------
    G : nx.Graph
        网络图
    partition : dict
        社区划分
    """
    print("\n社区特征分析:")
    print("-" * 60)

    community_nodes = defaultdict(list)
    for node, comm_id in partition.items():
        community_nodes[comm_id].append(node)

    for comm_id in sorted(community_nodes.keys()):
        nodes = community_nodes[comm_id]
        print(f"\n【社区C{comm_id + 1}】")
        print(f"  成员: {', '.join(sorted(nodes))}")

        # 计算社区特征
        ca_values = [G.nodes[n].get('ca_mean', 0) for n in nodes]
        cc_values = [G.nodes[n].get('cc_mean', 0) for n in nodes]
        sizes = [G.nodes[n].get('size', 0) for n in nodes]

        print(f"  认知通达度: M={np.mean(ca_values):.2f}, 范围=[{min(ca_values):.2f}, {max(ca_values):.2f}]")
        print(f"  概念复杂度: M={np.mean(cc_values):.2f}, 范围=[{min(cc_values):.2f}, {max(cc_values):.2f}]")
        print(f"  样本总量: {sum(sizes)}")

        # 社区内密度
        subgraph = G.subgraph(nodes)
        internal_density = nx.density(subgraph) if len(nodes) > 1 else 0
        print(f"  社区内密度: {internal_density:.4f}")


def main():
    """主函数"""
    print("=" * 60)
    print("Q2_05_模块检测.py")
    print("社区/模块检测（模块度优化）")
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

    # 2. 社区检测
    print("\n" + "-" * 40)
    print("2. 社区检测")
    print("-" * 40)
    partition, modularity, algorithm_name = detect_communities(G)

    # 验证模块度标准
    print(f"\n模块度验证:")
    print(f"  标准: Q >= 0.40")
    print(f"  实际: Q = {modularity:.4f}")
    print(f"  结论: {'[OK] 达标' if modularity >= 0.40 else '[X] 未达标'}")

    # 3. 创建表77
    print("\n" + "-" * 40)
    print("3. 保存表77: 社区检测结果")
    print("-" * 40)
    community_table = create_community_table(G, partition, modularity, algorithm_name)
    print(community_table.to_string(index=False))
    save_table(community_table, "社区检测结果", global_num=77,
               title="社区检测结果", formats=['csv', 'json'])

    # 4. 创建表82a
    print("\n" + "-" * 40)
    print("4. 保存表82a: 社区结构与类型特征对应分析")
    print("-" * 40)
    mapping_table = create_community_type_mapping(partition, algorithm_name)
    print(mapping_table.to_string(index=False))
    save_table(mapping_table, "社区结构与类型特征对应分析", global_num="82a",
               title="社区结构与类型特征对应分析", formats=['csv', 'json'])

    # 5. 绘制图22
    print("\n" + "-" * 40)
    print("5. 绘制图22: 网络社区结构可视化图")
    print("-" * 40)
    fig = plot_community_structure(G, partition, modularity, paths)
    save_figure(fig, "网络社区结构可视化图", global_num=22,
                title="网络社区结构可视化图")

    # 6. 社区特征分析
    print("\n" + "-" * 40)
    print("6. 社区特征分析")
    print("-" * 40)
    analyze_community_characteristics(G, partition)

    print("\n" + "=" * 60)
    print("Q2_05_模块检测 完成")
    print("=" * 60)

    return partition, modularity, algorithm_name


if __name__ == "__main__":
    partition, modularity, algorithm_name = main()
