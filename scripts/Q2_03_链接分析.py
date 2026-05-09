#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q2_03_链接分析.py
================
四类链接关系分析（Goldberg构式网络理论）

输出：
- 图19: 四类链接关系分布图
- 图20: 12类构式的实例层链接类型分布热力图
- 表72: 四类链接关系频率分布（微观层面节点级统计）
- 表73aux: 四类链接候选语例（自动抽取；正文表41以人工锁定语例为准）
- 表74: 链接删除影响分析（基于真实网络删除实验）
- 表75: 12类构式实例层链接类型分布交叉表（正文表43据此按通达度组汇总）

注：本节直接读取已固化的link_type字段；表77（Cohen's κ）已移除，不重新计算信度。

创建日期：2025-12-05
修改日期：2026-05-01（同步表75为实例层链接类型交叉表口径）
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

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, LINK_TYPE_CODES, CONSTRUCTION_COLORS
)


def load_data_with_links(paths: dict) -> pd.DataFrame:
    """加载带链接类型的数据"""
    proto_file = paths['output_data'] / 'CFMC_with_prototype_grades.csv'
    cluster_file = paths['output_data'] / 'CFMC_with_clusters.csv'

    if proto_file.exists():
        df = pd.read_csv(proto_file, index_col=0)
    elif cluster_file.exists():
        df = pd.read_csv(cluster_file, index_col=0)
    else:
        df = load_cfmc_data(paths)
        df['cluster_label'] = (df['cognitive_accessibility'] - 1) * 4 + df['mapping_direction'] - 1
        df['cluster_label'] = df['cluster_label'] % 12

    return df


def analyze_link_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析四类链接关系的分布

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        链接类型分布表
    """
    if 'link_type' not in df.columns:
        # 如果没有link_type字段，基于其他特征推断
        print("  基于特征推断链接类型...")
        df = infer_link_types(df)

    link_counts = df['link_type'].value_counts()
    total = len(df)

    table_data = []
    for link_code in [1, 2, 3, 4]:
        link_name = LINK_TYPE_CODES.get(link_code, f'类型{link_code}')
        count = link_counts.get(link_code, 0)

        table_data.append({
            '链接类型': link_name,
            '编码': link_code,
            '频数': count,
            '占比(%)': round(count / total * 100, 2) if total > 0 else 0,
            '理论说明': get_link_description(link_code)
        })

    return pd.DataFrame(table_data)


def infer_link_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    基于构式特征推断链接类型

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        添加了link_type的数据框
    """
    df = df.copy()

    # 推断规则：
    # 1. 隐喻扩展链接：高conventionality + 相同source_domain
    # 2. 多义链接：相同construction但不同meaning
    # 3. 子部分链接：构式间存在包含关系
    # 4. 实例链接：具体实例到抽象类型

    link_types = []

    for idx, row in df.iterrows():
        ca = row.get('cognitive_accessibility', 3)
        conv = row.get('conventionality', 3)
        proto_dist = row.get('prototype_distance', 2)

        # 基于特征组合推断
        if conv >= 4 and ca >= 4:
            # 高常规度+高通达度：隐喻扩展链接
            link_type = 1
        elif proto_dist == 1:
            # 中心成员：实例链接
            link_type = 4
        elif ca <= 2:
            # 低通达度：可能是子部分链接
            link_type = 3
        else:
            # 其他：多义链接
            link_type = 2

        link_types.append(link_type)

    df['link_type'] = link_types
    return df


def get_link_description(link_code: int) -> str:
    """获取链接类型的理论说明"""
    descriptions = {
        1: '相同概念隐喻的不同构式表达',
        2: '同一构式的多个相关意义',
        3: '构式间的部分-整体关系',
        4: '具体实例到抽象类型的归属关系'
    }
    return descriptions.get(link_code, '未知')


def create_link_construction_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    """
    创建实例层链接类型与构式类型交叉表（表75）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        交叉表
    """
    if 'link_type' not in df.columns:
        df = infer_link_types(df)

    # 创建交叉表
    crosstab = pd.crosstab(
        df['cluster_label'].apply(lambda x: f'T{x+1}'),
        df['link_type'].map(LINK_TYPE_CODES),
        margins=True,
        margins_name='合计'
    )

    type_order = [f'T{i}' for i in range(1, 13)] + ['合计']
    link_order = [LINK_TYPE_CODES[i] for i in [1, 2, 3, 4]] + ['合计']
    crosstab = crosstab.reindex(index=type_order, columns=link_order, fill_value=0)

    # 重命名索引
    crosstab.index.name = '构式类型'
    crosstab.columns.name = '链接类型'

    return crosstab


def plot_link_sankey(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制四类链接关系分布图（图20）

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
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=11)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_en = fm.FontProperties(fname=font_paths['english'], size=10)

    if 'link_type' not in df.columns:
        df = infer_link_types(df)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 左图：链接类型分布水平条形图（替代饼图，更适合极端分布）
    ax1 = axes[0]

    link_counts = df['link_type'].value_counts().sort_index()
    labels = [LINK_TYPE_CODES.get(i, f'类型{i}') for i in link_counts.index]
    sizes = link_counts.values
    # 统一配色方案
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']

    # 水平条形图
    y_pos = np.arange(len(labels))
    bars = ax1.barh(y_pos, sizes, color=colors, height=0.6, edgecolor='white', linewidth=1)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels, fontproperties=font_cn, fontsize=11)
    ax1.set_xlabel('频数', fontproperties=font_cn, fontsize=11)

    # 在条形右侧标注频数和百分比
    total = sum(sizes)
    for i, (bar, size) in enumerate(zip(bars, sizes)):
        pct = size / total * 100
        # 频数标注在条形内部右侧（白色）
        if size > total * 0.1:  # 大于10%的条形，标注在内部
            ax1.text(bar.get_width() - total*0.02, bar.get_y() + bar.get_height()/2,
                     f'{size} ({pct:.1f}%)', va='center', ha='right',
                     color='white', fontsize=10, fontweight='bold', fontproperties=font_en)
        else:  # 小于10%的条形，标注在外部
            ax1.text(bar.get_width() + total*0.01, bar.get_y() + bar.get_height()/2,
                     f'{size} ({pct:.1f}%)', va='center', ha='left',
                     color='black', fontsize=10, fontproperties=font_en)

    # 设置x轴范围，留出标注空间
    ax1.set_xlim(0, max(sizes) * 1.15)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    ax1.set_title('（a）四类链接关系占比分布', fontproperties=font_cn, fontsize=12)

    # 右图：链接类型与构式类型的关系（热力图形式）
    ax2 = axes[1]

    # 创建交叉频数矩阵
    link_cluster_matrix = np.zeros((4, 12))
    for link_type in range(1, 5):
        for cluster in range(12):
            mask = (df['link_type'] == link_type) & (df['cluster_label'] == cluster)
            link_cluster_matrix[link_type - 1, cluster] = mask.sum()

    # 归一化为百分比
    row_sums = link_cluster_matrix.sum(axis=1, keepdims=True)
    link_cluster_pct = np.divide(link_cluster_matrix, row_sums,
                                  where=row_sums != 0) * 100

    im = ax2.imshow(link_cluster_pct, cmap='YlOrRd', aspect='auto')

    # 设置标签
    ax2.set_xticks(np.arange(12))
    ax2.set_yticks(np.arange(4))
    ax2.set_xticklabels([f'T{i+1}' for i in range(12)], fontproperties=font_cn, fontsize=9)
    ax2.set_yticklabels([LINK_TYPE_CODES[i] for i in range(1, 5)],
                        fontproperties=font_cn, fontsize=10)

    # 添加数值标注
    for i in range(4):
        for j in range(12):
            value = link_cluster_pct[i, j]
            if value > 0:
                text_color = 'white' if value > 30 else 'black'
                ax2.text(j, i, f'{value:.1f}%', ha='center', va='center',
                        fontsize=8, color=text_color)

    ax2.set_xlabel('构式类型', fontproperties=font_cn, fontsize=11)
    ax2.set_ylabel('链接类型', fontproperties=font_cn, fontsize=11)
    ax2.set_title('（b）链接类型在各构式类型中的分布（%）', fontproperties=font_cn, fontsize=12)

    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax2, shrink=0.8)
    cbar.set_label('占比（%）', fontproperties=font_cn)

    # plt.suptitle('图17 四类链接关系分布', fontproperties=font_cn_title, fontsize=14, y=1.02)
    plt.tight_layout()

    return fig


def plot_link_type_heatmap(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制12类构式的实例层链接类型分布热力图（图20）

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
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=11)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)

    if 'link_type' not in df.columns:
        df = infer_link_types(df)

    fig, ax = plt.subplots(figsize=(14, 6))

    # 以真实link_type字段统计各构式类型内的链接类型占比
    n_clusters = 12
    link_types = [1, 2, 3, 4]
    link_matrix = np.zeros((len(link_types), n_clusters))

    for cluster_id in range(n_clusters):
        subset = df[df['cluster_label'] == cluster_id]
        if len(subset) == 0:
            continue
        counts = subset['link_type'].value_counts(normalize=True) * 100
        for row, link_type in enumerate(link_types):
            link_matrix[row, cluster_id] = counts.get(link_type, 0.0)

    im = ax.imshow(link_matrix, cmap='YlOrRd', vmin=0, vmax=max(100, link_matrix.max()))

    # 设置标签
    labels = [f'T{i+1}' for i in range(n_clusters)]
    ax.set_xticks(np.arange(n_clusters))
    ax.set_yticks(np.arange(len(link_types)))
    ax.set_xticklabels(labels, fontproperties=font_cn, fontsize=10)
    ax.set_yticklabels([LINK_TYPE_CODES[i] for i in link_types],
                       fontproperties=font_cn, fontsize=10)

    # 添加占比标注
    for row in range(len(link_types)):
        for col in range(n_clusters):
            value = link_matrix[row, col]
            if value > 0:
                text_color = 'white' if value >= 40 else 'black'
                ax.text(col, row, f'{value:.1f}%', ha='center', va='center',
                        fontsize=8, color=text_color)

    ax.set_xlabel('构式类型', fontproperties=font_cn, fontsize=12)
    ax.set_ylabel('实例层链接类型', fontproperties=font_cn, fontsize=12)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('类型内占比（%）', fontproperties=font_cn)
    plt.tight_layout()

    return fig


# [已移除] calculate_cohen_kappa
# 本节直接读取已固化的link_type字段；宏观层边类型由 Q2_01 的 CA-MD 规则生成，
# 二者不可混同，因此 Cohen's κ 标注者间一致性检验不适用。


def get_typical_examples(df: pd.DataFrame, n_per_type: int = 3) -> pd.DataFrame:
    """
    获取四类链接的候选语例（表73aux）

    Parameters
    ----------
    df : pd.DataFrame
        构式数据
    n_per_type : int
        每类链接的典型语例数量

    Returns
    -------
    pd.DataFrame
        典型语例表
    """
    if 'link_type' not in df.columns:
        df = infer_link_types(df)

    examples = []

    for link_type in [1, 2, 3, 4]:
        mask = df['link_type'] == link_type
        subset = df[mask]
        link_name = LINK_TYPE_CODES.get(link_type, f'类型{link_type}')

        if len(subset) > 0:
            # 优先选择原型距离最近（中心成员）的语例
            if 'prototype_distance' in subset.columns:
                subset_sorted = subset.sort_values('prototype_distance')
            else:
                subset_sorted = subset

            for i, (idx, row) in enumerate(subset_sorted.head(n_per_type).iterrows()):
                sentence = row.get('full_sentence', row.get('construction', f'语例{idx}'))
                # 截取句子长度
                if len(str(sentence)) > 50:
                    sentence = str(sentence)[:47] + '...'

                examples.append({
                    '链接类型': link_name,
                    '序号': i + 1,
                    '典型语例': sentence,
                    '源域': row.get('source_domain', '-'),
                    '目标域': row.get('target_domain', '-'),
                    '认知通达度': row.get('cognitive_accessibility', '-'),
                    '构式类型': f"T{row.get('cluster_label', 0)+1}"
                })

    return pd.DataFrame(examples)


def analyze_link_removal_impact(G: nx.Graph) -> pd.DataFrame:
    """
    链接删除影响分析（表74）

    基于宏观层类型网络，实际删除不同类型链接后重新计算网络拓扑指标。
    宏观网络包含两种边类型：
    - type 1（隐喻扩展边）：跨社区桥梁
    - type 2（多义型操作边）：社区内密集连接

    Parameters
    ----------
    G : nx.Graph
        宏观层类型网络（network_type_layer.graphml）

    Returns
    -------
    pd.DataFrame
        链接删除影响分析结果
    """
    # 基线指标
    baseline_C = nx.average_clustering(G)
    baseline_L = nx.average_shortest_path_length(G) if nx.is_connected(G) else float('inf')
    baseline_edges = G.number_of_edges()

    print(f"  基线: C={baseline_C:.4f}, L={baseline_L:.4f}, 边数={baseline_edges}")

    # 统计实际边类型分布
    edge_by_type = {}
    macro_link_type_names = {
        1: '隐喻扩展边',
        2: '多义型操作边',
    }
    for u, v, d in G.edges(data=True):
        lt = d.get('link_type', 0)
        if lt not in edge_by_type:
            edge_by_type[lt] = []
        edge_by_type[lt].append((u, v))

    for lt in sorted(edge_by_type):
        link_name = macro_link_type_names.get(lt, LINK_TYPE_CODES.get(lt, f'类型{lt}'))
        print(f"  {link_name}: {len(edge_by_type[lt])}条边")

    results = []

    for link_type in sorted(edge_by_type.keys()):
        edges = edge_by_type[link_type]
        edge_count = len(edges)
        link_name = macro_link_type_names.get(link_type, LINK_TYPE_CODES.get(link_type, f'类型{link_type}'))

        # 真实删除并重新计算
        G_copy = G.copy()
        G_copy.remove_edges_from(edges)

        C_after = nx.average_clustering(G_copy)

        if nx.is_connected(G_copy):
            L_after = nx.average_shortest_path_length(G_copy)
            connectivity = '连通'
        else:
            components = list(nx.connected_components(G_copy))
            n_comp = len(components)
            comp_sizes = sorted([len(c) for c in components], reverse=True)
            connectivity = f'断裂（{"+".join(str(s) for s in comp_sizes)}）'
            L_after = float('inf')

        results.append({
            '链接类型': link_name,
            '边数': edge_count,
            '占比': f"{edge_count/baseline_edges*100:.1f}%",
            '删除后C': round(C_after, 4),
            'ΔC': round(C_after - baseline_C, 4),
            '删除后连通性': connectivity,
            '删除后L': round(L_after, 4) if L_after != float('inf') else '∞',
            'ΔL': round(L_after - baseline_L, 4) if L_after != float('inf') else '—'
        })

    return pd.DataFrame(results)


def analyze_link_patterns(df: pd.DataFrame) -> None:
    """
    分析链接模式的详细特征

    Parameters
    ----------
    df : pd.DataFrame
        构式数据
    """
    if 'link_type' not in df.columns:
        df = infer_link_types(df)

    print("\n链接模式详细分析:")
    print("-" * 60)

    for link_type in [1, 2, 3, 4]:
        mask = df['link_type'] == link_type
        subset = df[mask]
        link_name = LINK_TYPE_CODES.get(link_type, f'类型{link_type}')

        print(f"\n【{link_name}】(n={len(subset)})")

        if len(subset) > 0:
            print(f"  认知通达度: M={subset['cognitive_accessibility'].mean():.2f}, "
                  f"SD={subset['cognitive_accessibility'].std():.2f}")
            print(f"  概念复杂度: M={subset['conceptual_complexity'].mean():.2f}, "
                  f"SD={subset['conceptual_complexity'].std():.2f}")

            # 主要构式类型
            top_clusters = subset['cluster_label'].value_counts().head(3)
            print(f"  前3构式类型: {', '.join([f'T{c+1}({n})' for c, n in top_clusters.items()])}")

            # 主要映射方向
            if 'mapping_direction' in subset.columns:
                from utils_公共函数 import MAPPING_DIRECTION_CODES
                top_md = subset['mapping_direction'].value_counts().head(2)
                md_str = ', '.join([f'{MAPPING_DIRECTION_CODES.get(int(md), "未知")}({n})'
                                   for md, n in top_md.items()])
                print(f"  主要映射方向: {md_str}")


def main():
    """主函数"""
    print("=" * 60)
    print("Q2_03_链接分析.py")
    print("四类链接关系分析（Goldberg构式网络理论）")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载数据
    print("\n" + "-" * 40)
    print("1. 加载数据")
    print("-" * 40)
    df = load_data_with_links(paths)
    print(f"样本量: {len(df)}")

    # 2. 分析链接类型分布
    print("\n" + "-" * 40)
    print("2. 保存表72: 四类链接关系频率分布")
    print("-" * 40)
    link_table = analyze_link_types(df)
    print(link_table.to_string(index=False))
    save_table(link_table, "四类链接关系频率分布", global_num=72,
               title="四类链接关系频率分布", formats=['csv', 'json'])

    # 3. 创建交叉表
    print("\n" + "-" * 40)
    print("3. 保存表75: 12类构式实例层链接类型分布交叉表")
    print("-" * 40)
    if 'link_type' not in df.columns:
        df = infer_link_types(df)
    crosstab = create_link_construction_crosstab(df)
    print(crosstab.to_string())
    save_table(crosstab.reset_index(), "12类构式实例层链接类型分布交叉表", global_num=75,
               title="12类构式实例层链接类型分布交叉表", formats=['csv', 'json'])

    # 4. 绘制图19
    print("\n" + "-" * 40)
    print("4. 绘制图19: 四类链接关系分布图")
    print("-" * 40)
    fig = plot_link_sankey(df, paths)
    save_figure(fig, "四类链接关系分布图", global_num=19,
                title="四类链接关系分布")

    # 4a. 绘制图20: 12类构式的实例层链接类型分布热力图
    print("\n" + "-" * 40)
    print("4a. 绘制图20: 12类构式的实例层链接类型分布热力图")
    print("-" * 40)
    fig_heatmap = plot_link_type_heatmap(df, paths)
    save_figure(fig_heatmap, "12类构式的实例层链接类型分布热力图", global_num=20,
                title="12类构式的实例层链接类型分布热力图")

    # 5. 详细模式分析
    print("\n" + "-" * 40)
    print("5. 链接模式详细分析")
    print("-" * 40)
    analyze_link_patterns(df)

    # 6. [已移除] Cohen's κ信度分析
    # 本节直接读取已固化的link_type字段；字段复核口径见主稿4.3.3节。
    print("\n" + "-" * 40)
    print("6. [跳过] Cohen's κ信度分析（本节读取已固化link_type字段，不重新计算一致性）")
    print("-" * 40)

    # 7. 候选语例
    print("\n" + "-" * 40)
    print("7. 保存表73aux: 四类链接候选语例（正文表41以人工锁定语例为准）")
    print("-" * 40)
    examples_table = get_typical_examples(df, n_per_type=3)
    print(examples_table.to_string(index=False))
    save_table(examples_table, "四类链接典型语例", global_num="73aux",
               title="四类链接候选语例（自动抽取）", formats=['csv', 'json'])

    # 8. 链接删除影响分析（基于真实网络删除实验）
    print("\n" + "-" * 40)
    print("8. 保存表74: 链接删除影响分析")
    print("-" * 40)
    # 加载宏观层类型网络
    network_file = paths['output_data'] / 'network_type_layer.graphml'
    if network_file.exists():
        G_macro = nx.read_graphml(network_file)
        print(f"  已加载宏观网络: {G_macro.number_of_nodes()}节点, {G_macro.number_of_edges()}条边")
        impact_table = analyze_link_removal_impact(G_macro)
        print(impact_table.to_string(index=False))
        save_table(impact_table, "链接删除影响分析", global_num=74,
                   title="链接删除对网络拓扑的影响分析", formats=['csv', 'json'])
    else:
        print(f"  [WARN] 未找到宏观网络文件: {network_file}")

    # 保存带链接类型的数据
    output_path = paths['output_data'] / 'CFMC_with_links.csv'
    df.to_csv(output_path, index=True, encoding='utf-8-sig')
    print(f"\n[OK] 已保存带链接类型的数据: {output_path}")

    print("\n" + "=" * 60)
    print("Q2_03_链接分析 完成")
    print("=" * 60)

    return link_table, crosstab


if __name__ == "__main__":
    link_table, crosstab = main()
