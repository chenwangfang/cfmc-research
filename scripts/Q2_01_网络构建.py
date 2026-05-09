#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q2_01_网络构建.py
================
构建两层构式网络（类型层+实例层）

输出：
- 图17: 两层网络结构示意图
- 表70: 两层网络基本参数（整合网络行仅为图17(b)可视化抽样元数据）

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
from matplotlib.patches import Rectangle
from collections import defaultdict
import json
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, LINK_TYPE_CODES, CONSTRUCTION_COLORS
)


def load_prototype_data(paths: dict) -> pd.DataFrame:
    """加载带原型梯度的数据"""
    proto_file = paths['output_data'] / 'CFMC_with_prototype_grades.csv'
    cluster_file = paths['output_data'] / 'CFMC_with_clusters.csv'

    if proto_file.exists():
        df = pd.read_csv(proto_file, index_col=0)
        print(f"[OK] 已加载原型梯度数据: {proto_file}")
    elif cluster_file.exists():
        df = pd.read_csv(cluster_file, index_col=0)
        print(f"[OK] 已加载聚类数据: {cluster_file}")
    else:
        # 如果没有聚类结果，加载原始数据并创建简单聚类
        df, _ = load_cfmc_data()
        print("[WARN] 未找到聚类结果，使用原始数据")
        # 基于认知通达度和映射方向创建简单聚类
        df['cluster_label'] = (df['cognitive_accessibility'] - 1) * 4 + df['mapping_direction'] - 1
        df['cluster_label'] = df['cluster_label'] % 12

    return df


def build_type_network(df: pd.DataFrame) -> nx.Graph:
    """
    构建类型层网络（12个类型节点）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    nx.Graph
        类型层网络
    """
    G_type = nx.Graph()

    # 添加12个类型节点
    for cluster in range(12):
        mask = df['cluster_label'] == cluster
        subset = df[mask]

        if len(subset) > 0:
            G_type.add_node(
                f'T{cluster + 1}',
                node_type='type',
                size=len(subset),
                ca_mean=subset['cognitive_accessibility'].mean(),
                cc_mean=subset['conceptual_complexity'].mean(),
                md_mode=subset['mapping_direction'].mode().iloc[0] if len(subset['mapping_direction'].mode()) > 0 else 0
            )

    # 基于认知通达度均值差和映射方向组合添加宏观操作边。
    # 隐喻扩展边：映射方向相同，认知通达度均值差在阈值内。
    # 多义型操作边：映射方向不同，认知通达度均值差在阈值内。
    nodes = list(G_type.nodes())

    for i, node1 in enumerate(nodes):
        for node2 in nodes[i+1:]:
            attr1 = G_type.nodes[node1]
            attr2 = G_type.nodes[node2]

            ca_diff = abs(attr1['ca_mean'] - attr2['ca_mean'])
            md_same = attr1['md_mode'] == attr2['md_mode']

            # 隐喻扩展边：映射方向相同，认知通达度相近
            # 阈值1.7确保中→高的连接（CA差约1.5-1.6）能够建立
            if md_same and ca_diff <= 1.7:
                G_type.add_edge(node1, node2,
                              link_type=1,
                              weight=1.0 / (1 + ca_diff))

            # 多义型操作边：认知通达度相近，映射方向不同
            elif not md_same and ca_diff <= 1.0:
                G_type.add_edge(node1, node2,
                              link_type=2,
                              weight=0.8 / (1 + ca_diff))

    print(f"\n类型层网络构建完成:")
    print(f"  节点数: {G_type.number_of_nodes()}")
    print(f"  边数: {G_type.number_of_edges()}")

    return G_type


def build_instance_network(df: pd.DataFrame) -> nx.Graph:
    """
    构建实例层网络。实例层边为同类内部按CA/CC相近性生成的抽样相似性边，
    用于观察局部结构，不等同于link_type字段中的理论链接类型。

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    nx.Graph
        实例层网络
    """
    G_instance = nx.Graph()

    # 添加实例节点
    for idx, row in df.iterrows():
        G_instance.add_node(
            str(idx),
            node_type='instance',
            cluster=row.get('cluster_label', 0),
            ca=row['cognitive_accessibility'],
            cc=row['conceptual_complexity'],
            md=row['mapping_direction']
        )

    # 若存在link_type字段，则在保留节点标签的前提下生成实例层局部相似性边
    if 'link_type' in df.columns:
        # 按聚类分组，组内按CA/CC相近性生成抽样相似性边
        for cluster in df['cluster_label'].unique():
            mask = df['cluster_label'] == cluster
            cluster_indices = df[mask].index.tolist()

            # 组内样本的抽样相似性链接
            for i, idx1 in enumerate(cluster_indices[:100]):  # 限制边数
                row1 = df.loc[idx1]
                for idx2 in cluster_indices[i+1:min(i+10, len(cluster_indices))]:
                    row2 = df.loc[idx2]

                    # 计算相似度
                    ca_sim = 1 - abs(row1['cognitive_accessibility'] - row2['cognitive_accessibility']) / 5
                    cc_sim = 1 - abs(row1['conceptual_complexity'] - row2['conceptual_complexity']) / 5

                    if ca_sim > 0.6 and cc_sim > 0.6:
                        G_instance.add_edge(
                            str(idx1), str(idx2),
                            link_type=3,
                            weight=(ca_sim + cc_sim) / 2
                        )

    print(f"\n实例层网络构建完成:")
    print(f"  节点数: {G_instance.number_of_nodes()}")
    print(f"  边数: {G_instance.number_of_edges()}")

    return G_instance


def build_two_layer_network(df: pd.DataFrame) -> tuple:
    """
    构建两层网络（类型层+实例层+层间连接）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    tuple
        (类型层网络, 实例层网络, 整合网络)
    """
    # 构建类型层
    G_type = build_type_network(df)

    # 构建实例层
    G_instance = build_instance_network(df)

    # 构建整合网络（包含层间连接）
    G_full = nx.Graph()

    # 添加类型层节点和边
    G_full.add_nodes_from(G_type.nodes(data=True))
    G_full.add_edges_from(G_type.edges(data=True))

    # 添加实例层节点和边（采样以减少复杂度）
    sample_size = min(500, len(df))
    sampled_indices = df.sample(n=sample_size, random_state=42).index

    for idx in sampled_indices:
        row = df.loc[idx]
        node_id = f'I_{idx}'
        G_full.add_node(
            node_id,
            node_type='instance',
            cluster=row.get('cluster_label', 0),
            ca=row['cognitive_accessibility'],
            cc=row['conceptual_complexity']
        )

        # 添加实例到类型的链接
        cluster = row.get('cluster_label', 0)
        type_node = f'T{cluster + 1}'
        if type_node in G_full.nodes():
            G_full.add_edge(node_id, type_node, link_type=4, weight=1.0)

    print(f"\n整合网络构建完成:")
    print(f"  总节点数: {G_full.number_of_nodes()}")
    print(f"  总边数: {G_full.number_of_edges()}")

    return G_type, G_instance, G_full


def create_network_params_table(G_type: nx.Graph, G_instance: nx.Graph,
                                 G_full: nx.Graph, df: pd.DataFrame) -> pd.DataFrame:
    """
    创建两层网络基本参数表（表70）

    Parameters
    ----------
    G_type : nx.Graph
        类型层网络
    G_instance : nx.Graph
        实例层网络
    G_full : nx.Graph
        整合网络
    df : pd.DataFrame
        原始数据

    Returns
    -------
    pd.DataFrame
        参数表
    """
    table_data = []

    # 类型层参数
    table_data.append({
        '网络层级': '类型层',
        '节点数': G_type.number_of_nodes(),
        '边数': G_type.number_of_edges(),
        '平均度': round(2 * G_type.number_of_edges() / G_type.number_of_nodes(), 2) if G_type.number_of_nodes() > 0 else 0,
        '网络密度': round(nx.density(G_type), 4) if G_type.number_of_nodes() > 1 else 0,
        '连通分量数': nx.number_connected_components(G_type) if G_type.number_of_nodes() > 0 else 0,
        '说明': '12类构式类型节点'
    })

    # 实例层参数
    n_nodes_instance = G_instance.number_of_nodes()
    n_edges_instance = G_instance.number_of_edges()
    table_data.append({
        '网络层级': '实例层',
        '节点数': n_nodes_instance,
        '边数': n_edges_instance,
        '平均度': round(2 * n_edges_instance / n_nodes_instance, 2) if n_nodes_instance > 0 else 0,
        '网络密度': round(nx.density(G_instance), 6) if n_nodes_instance > 1 else 0,
        '连通分量数': nx.number_connected_components(G_instance) if n_nodes_instance > 0 else 0,
        '说明': f'{len(df)}个构式实例节点'
    })

    # 整合网络参数
    n_type_nodes = sum(1 for n, d in G_full.nodes(data=True) if d.get('node_type') == 'type')
    n_instance_nodes = sum(1 for n, d in G_full.nodes(data=True) if d.get('node_type') == 'instance')

    table_data.append({
        '网络层级': '整合网络',
        '节点数': G_full.number_of_nodes(),
        '边数': G_full.number_of_edges(),
        '平均度': round(2 * G_full.number_of_edges() / G_full.number_of_nodes(), 2) if G_full.number_of_nodes() > 0 else 0,
        '网络密度': round(nx.density(G_full), 6) if G_full.number_of_nodes() > 1 else 0,
        '连通分量数': nx.number_connected_components(G_full) if G_full.number_of_nodes() > 0 else 0,
        '说明': f'类型{n_type_nodes}+实例{n_instance_nodes}'
    })

    return pd.DataFrame(table_data)


def get_ca_level(ca_mean: float) -> int:
    """根据认知通达度均值返回等级（0=低，1=中，2=高）"""
    if ca_mean <= 2:
        return 0  # 低
    elif ca_mean <= 3.5:
        return 1  # 中
    else:
        return 2  # 高


def plot_two_layer_network(G_type: nx.Graph, G_full: nx.Graph,
                           paths: dict) -> plt.Figure:
    """
    绘制两层网络结构示意图（图18）

    Parameters
    ----------
    G_type : nx.Graph
        类型层网络
    G_full : nx.Graph
        整合网络
    paths : dict
        路径字典

    Returns
    -------
    Figure
        matplotlib图表对象
    """
    import matplotlib.patheffects as path_effects

    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=11)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_cn_small = fm.FontProperties(fname=font_paths['chinese'], size=9)
    font_en = fm.FontProperties(fname=font_paths['english'], size=9)

    # 清除字体缓存
    plt.rcParams['font.family'] = ['sans-serif']

    fig, axes = plt.subplots(1, 2, figsize=(18, 9))

    # 认知通达度三色系统
    # 高=红系, 中=绿系, 低=蓝系
    CA_COLORS = {
        0: '#5DADE2',  # 低通达度 - 浅蓝色（更亮）
        1: '#58D68D',  # 中通达度 - 浅绿色（更亮）
        2: '#EC7063',  # 高通达度 - 浅红色（更亮）
    }
    CA_COLORS_LIGHT = {
        0: '#AED6F1',  # 低通达度 - 极浅蓝（实例节点用）
        1: '#ABEBC6',  # 中通达度 - 极浅绿
        2: '#F5B7B1',  # 高通达度 - 极浅红
    }
    CA_LABELS = {0: '低通达度', 1: '中通达度', 2: '高通达度'}

    # 为每个类型节点计算认知通达度等级和颜色
    node_ca_levels = {}
    for node in G_type.nodes():
        ca_mean = G_type.nodes[node].get('ca_mean', 3)
        ca_level = get_ca_level(ca_mean)
        node_ca_levels[node] = ca_level

    # ============ 左图：类型层网络（结构化布局） ============
    ax1 = axes[0]

    # 按认知通达度分组
    ca_groups = {0: [], 1: [], 2: []}
    for node in G_type.nodes():
        ca_level = node_ca_levels[node]
        ca_groups[ca_level].append(node)

    # 结构化布局：3行，按认知通达度从高到低排列
    pos_type = {}
    y_positions = {2: 2.0, 1: 0, 0: -2.0}  # 高/中/低
    for ca_level, nodes in ca_groups.items():
        if nodes:
            nodes_sorted = sorted(nodes, key=lambda x: int(x[1:]))  # 按T后面的数字排序
            n = len(nodes_sorted)
            x_span = 5.0
            x_start = -x_span / 2
            x_step = x_span / max(n - 1, 1) if n > 1 else 0
            for i, node in enumerate(nodes_sorted):
                pos_type[node] = (x_start + i * x_step if n > 1 else 0, y_positions[ca_level])

    # 节点大小基于样本量
    node_sizes = []
    node_colors_type = []
    for node in G_type.nodes():
        size = G_type.nodes[node].get('size', 100)
        node_sizes.append(max(size * 2.5, 400))
        node_colors_type.append(CA_COLORS[node_ca_levels[node]])

    # 绘制边（按类型着色）- 先绘制边
    me_edges = [(u, v) for u, v, d in G_type.edges(data=True)
                if d.get('link_type') == 1]
    poly_edges = [(u, v) for u, v, d in G_type.edges(data=True)
                  if d.get('link_type') == 2]

    # 隐喻扩展链接 - 红色
    nx.draw_networkx_edges(G_type, pos_type, ax=ax1,
                          edgelist=me_edges,
                          edge_color='#C0392B',
                          width=2.5, alpha=0.75,
                          connectionstyle='arc3,rad=0.1')
    # 多义链接 - 蓝色
    nx.draw_networkx_edges(G_type, pos_type, ax=ax1,
                          edgelist=poly_edges,
                          edge_color='#2980B9',
                          width=2.0, alpha=0.75,
                          connectionstyle='arc3,rad=0.1')

    # 绘制节点（按认知通达度着色）
    nx.draw_networkx_nodes(G_type, pos_type, ax=ax1,
                          node_size=node_sizes,
                          node_color=node_colors_type,
                          alpha=0.9,
                          edgecolors='#2C3E50',
                          linewidths=2)

    # 绘制标签（黑色+白色描边，提高可读性）
    for node, (x, y) in pos_type.items():
        txt = ax1.text(x, y, node, ha='center', va='center',
                      fontsize=11, fontweight='bold', color='#1A1A1A',
                      fontproperties=font_en)
        txt.set_path_effects([
            path_effects.Stroke(linewidth=3, foreground='white'),
            path_effects.Normal()
        ])

    ax1.set_title('（a）类型层网络（12类构式）', fontproperties=font_cn, fontsize=13, pad=15)
    ax1.axis('off')

    # 设置坐标轴范围
    ax1.set_xlim(-4, 4)
    ax1.set_ylim(-3.5, 3.5)

    # 添加完整图例
    from matplotlib.lines import Line2D
    legend_elements = [
        # 边类型
        Line2D([0], [0], color='#C0392B', linewidth=3, label='隐喻扩展链接'),
        Line2D([0], [0], color='#2980B9', linewidth=3, label='多义链接'),
        # 节点颜色（认知通达度）
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#EC7063',
               markersize=14, markeredgecolor='#2C3E50', markeredgewidth=1.5, label='高通达度'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#58D68D',
               markersize=14, markeredgecolor='#2C3E50', markeredgewidth=1.5, label='中通达度'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#5DADE2',
               markersize=14, markeredgecolor='#2C3E50', markeredgewidth=1.5, label='低通达度'),
    ]
    ax1.legend(handles=legend_elements, loc='lower left', prop=font_cn_small,
               framealpha=0.95, ncol=1, fontsize=9)

    # ============ 右图：两层整合网络（清晰分层布局） ============
    ax2 = axes[1]

    # 分离类型节点和实例节点
    type_nodes = [n for n, d in G_full.nodes(data=True) if d.get('node_type') == 'type']
    instance_nodes = [n for n, d in G_full.nodes(data=True) if d.get('node_type') == 'instance']

    # 创建布局
    pos_full = {}

    # 类型节点在上层（按认知通达度分行，水平均匀排列）
    type_by_ca = {0: [], 1: [], 2: []}
    for node in type_nodes:
        ca_mean = G_full.nodes[node].get('ca_mean', G_type.nodes.get(node, {}).get('ca_mean', 3))
        ca_level = get_ca_level(ca_mean)
        type_by_ca[ca_level].append(node)

    # 按认知通达度分行布局（高在上，低在下）
    y_type_positions = {2: 4.0, 1: 3.0, 0: 2.0}  # 高/中/低
    for ca_level, nodes in type_by_ca.items():
        if nodes:
            nodes_sorted = sorted(nodes, key=lambda x: int(x[1:]))
            n = len(nodes_sorted)
            x_span = 8.0
            x_start = -x_span / 2
            x_step = x_span / max(n - 1, 1) if n > 1 else 0
            for i, node in enumerate(nodes_sorted):
                pos_full[node] = (x_start + i * x_step if n > 1 else 0, y_type_positions[ca_level])

    # 实例节点在下层（网格排列，每类显示6个代表性节点）
    instance_by_cluster = defaultdict(list)
    for node in instance_nodes:
        cluster = G_full.nodes[node].get('cluster', 0)
        instance_by_cluster[cluster].append(node)

    # 计算每个类型节点下方的实例节点位置
    n_instances_per_type = 6  # 每类显示6个
    instance_y_base = 0.3  # 实例节点基准y坐标
    instance_y_step = 0.5  # 实例节点行间距

    for cluster, nodes in instance_by_cluster.items():
        type_node = f'T{cluster + 1}'
        if type_node in pos_full:
            tx, ty = pos_full[type_node]
            # 在类型节点下方以2行3列网格排列
            n_show = min(len(nodes), n_instances_per_type)
            for j, node in enumerate(nodes[:n_show]):
                row = j // 3  # 行号 (0 或 1)
                col = j % 3   # 列号 (0, 1, 2)
                x_offset = (col - 1) * 0.35  # 列偏移
                y_offset = -row * instance_y_step  # 行偏移
                pos_full[node] = (tx + x_offset, instance_y_base + y_offset)

    # ====== 层次感优化：添加层背景 ======
    # 类型层背景（淡蓝色）
    type_layer_bg = Rectangle((-5, 1.4), 10, 3.8,
                              facecolor='#E8F4FD', edgecolor='none', alpha=0.5)
    ax2.add_patch(type_layer_bg)

    # 实例层背景（淡灰色）
    instance_layer_bg = Rectangle((-5, -0.7), 10, 2.0,
                                  facecolor='#F5F6F7', edgecolor='none', alpha=0.5)
    ax2.add_patch(instance_layer_bg)

    # ====== 层次感优化：强化分隔线（双层效果）======
    ax2.axhline(y=1.2, color='#FFFFFF', linestyle='-', linewidth=6, alpha=1.0)  # 白色底线
    ax2.axhline(y=1.2, color='#5D6D7E', linestyle='--', linewidth=2.5, alpha=0.9)  # 深色虚线

    # ====== 层次感优化：添加层级标签 ======
    ax2.text(-4.75, 3.0, '类型层', fontproperties=font_cn, fontsize=11,
             rotation=90, va='center', ha='center', color='#2C3E50', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.8))
    ax2.text(-4.75, 0.15, '实例层', fontproperties=font_cn, fontsize=11,
             rotation=90, va='center', ha='center', color='#5D6D7E', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.8))

    # 绘制层间连接（实例到类型）- 使用浅灰色细线
    instance_nodes_in_pos = [n for n in instance_nodes if n in pos_full]
    for node in instance_nodes_in_pos:
        cluster = G_full.nodes[node].get('cluster', 0)
        type_node = f'T{cluster + 1}'
        if type_node in pos_full:
            x1, y1 = pos_full[node]
            x2, y2 = pos_full[type_node]
            ax2.plot([x1, x2], [y1, y2], color='#BDC3C7', linewidth=0.6, alpha=0.5)

    # 绘制实例节点（按所属类型的认知通达度着色，使用浅色）
    for cluster, nodes in instance_by_cluster.items():
        type_node = f'T{cluster + 1}'
        if type_node in node_ca_levels:
            ca_level = node_ca_levels[type_node]
        else:
            ca_level = 1
        color = CA_COLORS_LIGHT[ca_level]

        nodes_in_pos = [n for n in nodes if n in pos_full]
        if nodes_in_pos:
            nx.draw_networkx_nodes(G_full, pos_full, ax=ax2,
                                  nodelist=nodes_in_pos,
                                  node_size=80,
                                  node_color=color,
                                  alpha=0.85,
                                  edgecolors=CA_COLORS[ca_level],
                                  linewidths=0.8)

    # 绘制类型节点（与左图颜色一致，增大尺寸以增强层次对比）
    for node in type_nodes:
        if node in pos_full:
            ca_level = node_ca_levels.get(node, 1)
            color = CA_COLORS[ca_level]
            size = G_type.nodes[node].get('size', 100) * 2.2  # 增大系数

            nx.draw_networkx_nodes(G_full, pos_full, ax=ax2,
                                  nodelist=[node],
                                  node_size=max(size, 550),  # 提高最小尺寸
                                  node_color=color,
                                  alpha=0.95,
                                  edgecolors='#1A252F',  # 更深的边框色
                                  linewidths=2.5)  # 加粗边框

    # 绘制类型节点标签（黑色+白色描边）
    for node in type_nodes:
        if node in pos_full:
            x, y = pos_full[node]
            txt = ax2.text(x, y, node, ha='center', va='center',
                          fontsize=10, fontweight='bold', color='#1A1A1A',
                          fontproperties=font_en)
            txt.set_path_effects([
                path_effects.Stroke(linewidth=3, foreground='white'),
                path_effects.Normal()
            ])

    ax2.set_title('（b）两层整合网络示意图', fontproperties=font_cn, fontsize=13, pad=15)
    ax2.axis('off')

    # 设置坐标轴范围（扩大左侧以容纳层标签）
    ax2.set_xlim(-5.3, 5)
    ax2.set_ylim(-0.8, 5.3)

    # 添加底部说明
    ax2.text(0.5, -0.02, '上层：类型节点（按认知通达度分行）｜ 下层：实例节点（网格分布）｜ 灰线：层间连接',
            transform=ax2.transAxes, ha='center', fontproperties=font_cn_small,
            fontsize=9, color='#5D6D7E')
    ax2.text(0.5, -0.06, '节点大小 ∝ 样本量',
            transform=ax2.transAxes, ha='center', fontproperties=font_cn_small,
            fontsize=9, color='#7F8C8D')

    # plt.suptitle('图18 两层网络结构示意图', fontproperties=font_cn_title, fontsize=16, y=0.98)
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])

    return fig


def convert_to_serializable(obj):
    """将numpy类型转换为Python原生类型以支持JSON序列化"""
    import numpy as np
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def save_networks(G_type: nx.Graph, G_instance: nx.Graph, G_full: nx.Graph,
                  paths: dict) -> None:
    """保存网络数据"""
    output_dir = paths['output_data']

    # 保存为GraphML格式
    nx.write_graphml(G_type, output_dir / 'network_type_layer.graphml')
    nx.write_graphml(G_full, output_dir / 'network_full.graphml')

    # 保存节点和边列表为JSON（转换numpy类型）
    type_data = {
        'nodes': [convert_to_serializable({'id': n, **d}) for n, d in G_type.nodes(data=True)],
        'edges': [convert_to_serializable({'source': u, 'target': v, **d}) for u, v, d in G_type.edges(data=True)]
    }
    with open(output_dir / 'network_type_layer.json', 'w', encoding='utf-8') as f:
        json.dump(type_data, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 网络数据已保存到: {output_dir}")


def main():
    """主函数"""
    print("=" * 60)
    print("Q2_01_网络构建.py")
    print("构建两层构式网络（类型层+实例层）")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载数据
    print("\n" + "-" * 40)
    print("1. 加载数据")
    print("-" * 40)
    df = load_prototype_data(paths)
    print(f"样本量: {len(df)}")

    # 2. 构建两层网络
    print("\n" + "-" * 40)
    print("2. 构建两层网络")
    print("-" * 40)
    G_type, G_instance, G_full = build_two_layer_network(df)

    # 3. 创建表70
    print("\n" + "-" * 40)
    print("3. 保存表70: 两层网络基本参数")
    print("-" * 40)
    params_table = create_network_params_table(G_type, G_instance, G_full, df)
    print(params_table.to_string(index=False))
    save_table(params_table, "两层网络基本参数", global_num=70,
               title="两层网络基本参数", formats=['csv', 'json'])

    # 4. 绘制图17
    print("\n" + "-" * 40)
    print("4. 绘制图17: 两层网络结构示意图")
    print("-" * 40)
    fig = plot_two_layer_network(G_type, G_full, paths)
    save_figure(fig, "两层网络结构示意图", global_num=17,
                title="两层网络结构示意图")

    # 5. 保存网络数据
    print("\n" + "-" * 40)
    print("5. 保存网络数据")
    print("-" * 40)
    save_networks(G_type, G_instance, G_full, paths)

    print("\n" + "=" * 60)
    print("Q2_01_网络构建 完成")
    print("=" * 60)

    return G_type, G_instance, G_full


if __name__ == "__main__":
    G_type, G_instance, G_full = main()
