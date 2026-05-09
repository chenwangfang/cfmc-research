#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q2_04_中心性分析.py
==================
网络中心性分析（度中心性、中介中心性、特征向量中心性）

输出：
- 图22: 构式类型组三种中心性指标对比（原图21）
- 表76: 构式类型组网络中心性指标（原表77）

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
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, get_font_paths, save_figure, save_table, CONSTRUCTION_COLORS,
    load_cfmc_data, NETWORK_FUNCTION_CODES
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


def calculate_centrality_metrics(G: nx.Graph) -> pd.DataFrame:
    """
    计算三种中心性指标

    Parameters
    ----------
    G : nx.Graph
        网络图

    Returns
    -------
    pd.DataFrame
        中心性指标表
    """
    # 度中心性
    degree_centrality = nx.degree_centrality(G)

    # 中介中心性
    betweenness_centrality = nx.betweenness_centrality(G)

    # 特征向量中心性
    try:
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=500)
    except:
        # 如果不收敛，使用度中心性替代
        eigenvector_centrality = degree_centrality.copy()
        print("  [WARN] 特征向量中心性不收敛，使用度中心性替代")

    # 接近中心性
    if nx.is_connected(G):
        closeness_centrality = nx.closeness_centrality(G)
    else:
        # 对于非连通图，分别计算
        closeness_centrality = {}
        for node in G.nodes():
            try:
                closeness_centrality[node] = nx.closeness_centrality(G, node)
            except:
                closeness_centrality[node] = 0

    # 创建数据框
    centrality_data = []
    for node in G.nodes():
        node_data = dict(G.nodes[node])
        centrality_data.append({
            '构式类型': node,
            '样本量': node_data.get('size', 0),
            '度中心性': round(degree_centrality.get(node, 0), 4),
            '中介中心性': round(betweenness_centrality.get(node, 0), 4),
            '特征向量中心性': round(eigenvector_centrality.get(node, 0), 4),
            '接近中心性': round(closeness_centrality.get(node, 0), 4),
            '度数': G.degree(node),
            '认知通达度均值': round(node_data.get('ca_mean', 0), 2),
            '概念复杂度均值': round(node_data.get('cc_mean', 0), 2)
        })

    df = pd.DataFrame(centrality_data)
    df = df.sort_values('度中心性', ascending=False).reset_index(drop=True)

    return df


def analyze_hub_nodes(centrality_df: pd.DataFrame) -> dict:
    """
    分析枢纽节点

    Parameters
    ----------
    centrality_df : pd.DataFrame
        中心性指标表

    Returns
    -------
    dict
        枢纽节点分析结果
    """
    results = {}

    # 度中心性前3
    top_degree = centrality_df.nlargest(3, '度中心性')[['构式类型', '度中心性', '样本量']].values.tolist()
    results['度中心性前3'] = top_degree

    # 中介中心性前3
    top_between = centrality_df.nlargest(3, '中介中心性')[['构式类型', '中介中心性', '样本量']].values.tolist()
    results['中介中心性前3'] = top_between

    # 特征向量中心性前3
    top_eigen = centrality_df.nlargest(3, '特征向量中心性')[['构式类型', '特征向量中心性', '样本量']].values.tolist()
    results['特征向量中心性前3'] = top_eigen

    # 综合得分（三种中心性的标准化平均）
    for col in ['度中心性', '中介中心性', '特征向量中心性']:
        mean_val = centrality_df[col].mean()
        std_val = centrality_df[col].std()
        if std_val > 0:
            centrality_df[f'{col}_z'] = (centrality_df[col] - mean_val) / std_val
        else:
            centrality_df[f'{col}_z'] = 0

    centrality_df['综合中心性'] = (centrality_df['度中心性_z'] +
                                 centrality_df['中介中心性_z'] +
                                 centrality_df['特征向量中心性_z']) / 3

    # 综合排名前3
    top_overall = centrality_df.nlargest(3, '综合中心性')[['构式类型', '综合中心性', '样本量']].values.tolist()
    results['综合中心性前3'] = top_overall

    return results


def plot_centrality_comparison(centrality_df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制三种中心性指标分布对比图（图22）

    颜色编码：按认知通达度等级分组（与图21一致）
    认知通达度1-5级：1=最难通达，5=最易通达
    - 低通达度（T1-T4，均值≈2.0）：青蓝色系
    - 中通达度（T5-T8，均值≈3.0）：绿色系
    - 高通达度（T9-T12，均值≈4.5）：橙红色系

    Parameters
    ----------
    centrality_df : pd.DataFrame
        中心性指标表
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

    # 认知通达度分组颜色方案（与图21一致）
    # 认知通达度1-5级：1=最难通达，5=最易通达
    # 低通达度（T1-T4，均值≈2.0）：青蓝色系
    # 中通达度（T5-T8，均值≈3.0）：绿色系
    # 高通达度（T9-T12，均值≈4.5）：红色系
    accessibility_colors = {
        'T1': '#1a5276', 'T2': '#2874a6', 'T3': '#3498db', 'T4': '#85c1e9',  # 青蓝色系（低通达度）
        'T5': '#145a32', 'T6': '#1e8449', 'T7': '#27ae60', 'T8': '#82e0aa',  # 绿色系（中通达度）
        'T9': '#922b21', 'T10': '#c0392b', 'T11': '#e74c3c', 'T12': '#f1948a'  # 红色系（高通达度）
    }

    # 分组标签（修正：按实际认知通达度均值划分）
    group_labels = {
        'low': ('低通达度 (T1-T4)', '#2874a6'),
        'medium': ('中通达度 (T5-T8)', '#1e8449'),
        'high': ('高通达度 (T9-T12)', '#c0392b')
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 1. 度中心性条形图
    ax1 = axes[0, 0]
    types = centrality_df['构式类型'].tolist()
    degree_values = centrality_df['度中心性'].tolist()

    # 根据构式类型名称分配颜色
    colors = [accessibility_colors.get(t, '#888888') for t in types]

    bars = ax1.barh(types, degree_values, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
    ax1.set_xlabel('度中心性', fontproperties=font_cn, fontsize=11)
    ax1.set_ylabel('构式类型', fontproperties=font_cn, fontsize=11)
    ax1.set_title('（a）度中心性', fontproperties=font_cn, fontsize=12)
    ax1.invert_yaxis()

    # 添加数值标签
    for bar, val in zip(bars, degree_values):
        ax1.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=9, fontproperties=font_en)

    # 2. 中介中心性条形图
    ax2 = axes[0, 1]
    between_values = centrality_df['中介中心性'].tolist()

    bars = ax2.barh(types, between_values, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
    ax2.set_xlabel('中介中心性', fontproperties=font_cn, fontsize=11)
    ax2.set_ylabel('构式类型', fontproperties=font_cn, fontsize=11)
    ax2.set_title('（b）中介中心性', fontproperties=font_cn, fontsize=12)
    ax2.invert_yaxis()

    for bar, val in zip(bars, between_values):
        ax2.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=9, fontproperties=font_en)

    # 3. 特征向量中心性条形图
    ax3 = axes[1, 0]
    eigen_values = centrality_df['特征向量中心性'].tolist()

    bars = ax3.barh(types, eigen_values, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
    ax3.set_xlabel('特征向量中心性', fontproperties=font_cn, fontsize=11)
    ax3.set_ylabel('构式类型', fontproperties=font_cn, fontsize=11)
    ax3.set_title('（c）特征向量中心性', fontproperties=font_cn, fontsize=12)
    ax3.invert_yaxis()

    for bar, val in zip(bars, eigen_values):
        ax3.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=9, fontproperties=font_en)

    # 在子图(c)下方添加图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=group_labels['high'][1], label=group_labels['high'][0], alpha=0.85),
        Patch(facecolor=group_labels['medium'][1], label=group_labels['medium'][0], alpha=0.85),
        Patch(facecolor=group_labels['low'][1], label=group_labels['low'][0], alpha=0.85)
    ]
    ax3.legend(handles=legend_elements, loc='lower right', prop=font_cn, framealpha=0.9)

    # 4. 三种中心性的相关性热力图
    ax4 = axes[1, 1]

    corr_data = centrality_df[['度中心性', '中介中心性', '特征向量中心性']].corr()

    # 使用柔和的蓝色渐变配色（vmin=0.5因为相关系数都较高）
    im = ax4.imshow(corr_data.values, cmap='Blues', vmin=0.5, vmax=1.0)

    ax4.set_xticks(np.arange(3))
    ax4.set_yticks(np.arange(3))
    labels = ['度中心性', '中介中心性', '特征向量中心性']
    ax4.set_xticklabels(labels, fontproperties=font_cn, fontsize=10, rotation=45, ha='right')
    ax4.set_yticklabels(labels, fontproperties=font_cn, fontsize=10)

    # 添加相关系数
    for i in range(3):
        for j in range(3):
            # 对角线1.00用白色，其他根据深浅调整
            if i == j:
                text_color = 'white'
            else:
                text_color = 'white' if corr_data.values[i, j] > 0.85 else 'black'
            ax4.text(j, i, f'{corr_data.values[i, j]:.2f}',
                    ha='center', va='center', color=text_color, fontsize=11, fontproperties=font_en)

    ax4.set_title('（d）中心性指标相关矩阵', fontproperties=font_cn, fontsize=12)
    plt.colorbar(im, ax=ax4, shrink=0.8)

    # plt.suptitle('图19 构式类型组三种中心性指标对比',
                # fontproperties=font_cn_title, fontsize=14, y=1.02)
    plt.tight_layout()

    return fig


def correlate_centrality_with_features(centrality_df: pd.DataFrame) -> pd.DataFrame:
    """
    描述中心性与构式特征的相关趋势。

    12类类型节点只形成少量中心性取值组，因此这里只输出
    Pearson r 作为方向和强度描述，不输出显著性概率或星号标注。

    Parameters
    ----------
    centrality_df : pd.DataFrame
        中心性指标表

    Returns
    -------
    pd.DataFrame
        相关分析结果
    """
    results = []

    centrality_cols = ['度中心性', '中介中心性', '特征向量中心性']
    feature_cols = ['认知通达度均值', '概念复杂度均值', '样本量']

    for c_col in centrality_cols:
        for f_col in feature_cols:
            if f_col in centrality_df.columns:
                r = centrality_df[c_col].corr(centrality_df[f_col])
                results.append({
                    '中心性指标': c_col,
                    '构式特征': f_col,
                    'r': round(r, 4),
                    '推断状态': '不作显著性检验',
                    '说明': '12类构式仅形成少量取值组，相关系数只描述方向与强度'
                })

    return pd.DataFrame(results)


def analyze_function_in_network(paths: dict) -> pd.DataFrame:
    """
    分析function_in_network字段的分布（表81a）

    Parameters
    ----------
    paths : dict
        路径字典

    Returns
    -------
    pd.DataFrame
        节点功能角色分布表
    """
    # 加载原始数据
    df, _ = load_cfmc_data()

    if 'function_in_network' not in df.columns:
        print("  [WARN] 数据中无function_in_network字段")
        return pd.DataFrame()

    # 功能角色编码反转
    func_labels = {v: k for k, v in NETWORK_FUNCTION_CODES.items()}
    func_names_cn = {
        1: '中心节点',
        2: '边缘节点',
        3: '桥接节点',
        4: '创新节点',
        5: '模块核心节点'
    }

    # 统计分布
    table_data = []
    total = len(df)

    for code in sorted(df['function_in_network'].dropna().unique()):
        code = int(code)
        mask = df['function_in_network'] == code
        n = mask.sum()

        # 获取该类型的认知特征均值
        subset = df[mask]

        table_data.append({
            '功能角色': func_names_cn.get(code, f'未知({code})'),
            '角色编码': code,
            '样本量': n,
            '占比(%)': round(n / total * 100, 2),
            '认知通达度M': round(subset['cognitive_accessibility'].mean(), 3) if 'cognitive_accessibility' in subset.columns else '-',
            '概念复杂度M': round(subset['conceptual_complexity'].mean(), 3) if 'conceptual_complexity' in subset.columns else '-'
        })

    result_df = pd.DataFrame(table_data)
    result_df = result_df.sort_values('样本量', ascending=False).reset_index(drop=True)

    print("\n节点功能角色分布:")
    print(result_df.to_string(index=False))

    return result_df


def analyze_function_centrality_consistency(centrality_df: pd.DataFrame, paths: dict) -> pd.DataFrame:
    """
    分析function_in_network标签与实际中心性指标的一致性（表83b）

    Parameters
    ----------
    centrality_df : pd.DataFrame
        中心性指标表
    paths : dict
        路径字典

    Returns
    -------
    pd.DataFrame
        一致性分析结果
    """
    # 加载原始数据
    df, _ = load_cfmc_data()

    if 'function_in_network' not in df.columns:
        print("  [WARN] 数据中无function_in_network字段")
        return pd.DataFrame()

    func_names_cn = {
        1: '中心节点',
        2: '边缘节点',
        3: '桥接节点',
        4: '创新节点',
        5: '模块核心节点'
    }

    # 按功能角色分组计算平均中心性
    # 首先需要关联到T1-T12。发布语料有时只有CA和MD字段，因此需要现场派生类型标签。
    type_col = '_centrality_type_label'
    if 'construction_type_12' in df.columns:
        type_order = [
            '低_具具', '低_具抽', '低_抽抽', '低_抽具',
            '中_具具', '中_具抽', '中_抽抽', '中_抽具',
            '高_具具', '高_具抽', '高_抽抽', '高_抽具'
        ]
        type_map = {label: f'T{i + 1}' for i, label in enumerate(type_order)}
        df[type_col] = df['construction_type_12'].map(type_map).fillna(df['construction_type_12'])
    elif 'cluster_label' in df.columns:
        cluster_values = pd.to_numeric(df['cluster_label'], errors='coerce')
        if cluster_values.dropna().between(0, 11).all():
            df[type_col] = cluster_values.apply(lambda x: f'T{int(x) + 1}' if pd.notna(x) else np.nan)
        elif cluster_values.dropna().between(1, 12).all():
            df[type_col] = cluster_values.apply(lambda x: f'T{int(x)}' if pd.notna(x) else np.nan)
        else:
            df[type_col] = df['cluster_label']
    elif {'cognitive_accessibility', 'mapping_direction'}.issubset(df.columns):
        ca_values = pd.to_numeric(df['cognitive_accessibility'], errors='coerce')
        md_values = pd.to_numeric(df['mapping_direction'], errors='coerce')

        def build_type_label(ca, md):
            if pd.isna(ca) or pd.isna(md):
                return np.nan
            ca = float(ca)
            md = int(md)
            if md < 1 or md > 4:
                return np.nan
            ca_offset = 0 if ca <= 2 else 4 if ca <= 3 else 8
            return f'T{ca_offset + md}'

        df[type_col] = [build_type_label(ca, md) for ca, md in zip(ca_values, md_values)]
    else:
        print("  [WARN] 无法找到或派生构式类型列")
        return pd.DataFrame()

    # 按功能角色分组
    results = []
    for code in sorted(df['function_in_network'].dropna().unique()):
        code = int(code)
        mask = df['function_in_network'] == code
        subset = df[mask]

        # 获取该功能角色下各构式类型
        types_in_group = subset[type_col].unique()

        # 从centrality_df获取这些类型的平均中心性
        centrality_subset = centrality_df[centrality_df['构式类型'].isin(types_in_group)]

        if len(centrality_subset) > 0:
            results.append({
                '功能角色': func_names_cn.get(code, f'未知({code})'),
                '覆盖构式类型数': len(centrality_subset),
                '度中心性M': round(centrality_subset['度中心性'].mean(), 4),
                '中介中心性M': round(centrality_subset['中介中心性'].mean(), 4),
                '特征向量中心性M': round(centrality_subset['特征向量中心性'].mean(), 4),
                '样本量': mask.sum()
            })

    result_df = pd.DataFrame(results)

    # 添加理论预期标注
    # 中心节点应有最高度中心性，桥接节点应有最高中介中心性
    if len(result_df) > 0:
        print("\n功能角色与中心性一致性:")
        print(result_df.to_string(index=False))

        # 一致性检验
        print("\n一致性检验:")
        if '中心节点' in result_df['功能角色'].values:
            center_row = result_df[result_df['功能角色'] == '中心节点']
            if not center_row.empty:
                max_degree = result_df['度中心性M'].max()
                center_degree = center_row['度中心性M'].values[0]
                if center_degree == max_degree:
                    print("  [OK] 中心节点具有最高度中心性（一致）")
                else:
                    print(f"  [WARN] 中心节点度中心性={center_degree:.4f}，最高={max_degree:.4f}（不一致）")

        if '桥接节点' in result_df['功能角色'].values:
            bridge_row = result_df[result_df['功能角色'] == '桥接节点']
            if not bridge_row.empty:
                max_between = result_df['中介中心性M'].max()
                bridge_between = bridge_row['中介中心性M'].values[0]
                if bridge_between == max_between:
                    print("  [OK] 桥接节点具有最高中介中心性（一致）")
                else:
                    print(f"  [WARN] 桥接节点中介中心性={bridge_between:.4f}，最高={max_between:.4f}（不一致）")

    return result_df


def main():
    """主函数"""
    print("=" * 60)
    print("Q2_04_中心性分析.py")
    print("网络中心性分析")
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

    # 2. 计算中心性指标
    print("\n" + "-" * 40)
    print("2. 计算中心性指标")
    print("-" * 40)
    centrality_df = calculate_centrality_metrics(G)

    # 3. 分析枢纽节点
    print("\n" + "-" * 40)
    print("3. 枢纽节点分析")
    print("-" * 40)
    hub_results = analyze_hub_nodes(centrality_df)

    print("\n枢纽节点:")
    for metric, nodes in hub_results.items():
        print(f"\n  {metric}:")
        for node in nodes:
            print(f"    {node[0]}: {node[1]:.4f} (n={int(node[2]) if isinstance(node[2], (int, float)) else node[2]})")

    # 4. 保存表76
    print("\n" + "-" * 40)
    print("4. 保存表76: 构式类型组网络中心性指标")
    print("-" * 40)
    # 选择主要列
    output_cols = ['构式类型', '样本量', '度数', '度中心性', '中介中心性',
                  '特征向量中心性', '接近中心性', '认知通达度均值', '概念复杂度均值']
    output_df = centrality_df[output_cols].copy()
    print(output_df.to_string(index=False))
    save_table(output_df, "构式类型组网络中心性指标", global_num=76,
               title="构式类型组网络中心性指标", formats=['csv', 'json'])

    # 5. 绘制图19
    print("\n" + "-" * 40)
    print("5. 绘制图22: 构式类型组三种中心性指标对比")
    print("-" * 40)
    fig = plot_centrality_comparison(centrality_df, paths)
    save_figure(fig, "构式类型组三种中心性指标对比", global_num=21,
                title="构式类型组三种中心性指标对比")

    # 6. 中心性与特征的相关分析
    print("\n" + "-" * 40)
    print("6. 保存表78: 网络中心性与认知维度相关分析")
    print("-" * 40)
    corr_results = correlate_centrality_with_features(centrality_df)
    print(corr_results.to_string(index=False))
    save_table(corr_results, "网络中心性与认知维度相关分析", global_num=78,
               title="网络中心性与认知维度相关分析", formats=['csv', 'json'])

    # 7. 节点功能角色分布分析（表81a）
    print("\n" + "-" * 40)
    print("7. 保存表78: 节点功能角色分布")
    print("-" * 40)
    func_dist = analyze_function_in_network(paths)
    if not func_dist.empty:
        save_table(func_dist, "节点功能角色分布", global_num=78,
                   title="节点功能角色分布", formats=['csv', 'json'])

    # 8. 功能角色与中心性一致性分析（表83b）
    print("\n" + "-" * 40)
    print("8. 保存表83b: 功能角色与中心性一致性分析")
    print("-" * 40)
    consistency_df = analyze_function_centrality_consistency(centrality_df, paths)
    if not consistency_df.empty:
        save_table(consistency_df, "功能角色与中心性一致性分析", global_num="83b",
                   title="功能角色与中心性一致性分析", formats=['csv', 'json'])

    print("\n" + "=" * 60)
    print("Q2_04_中心性分析 完成")
    print("=" * 60)

    return centrality_df, hub_results, func_dist, consistency_df


if __name__ == "__main__":
    centrality_df, hub_results, func_dist, consistency_df = main()
