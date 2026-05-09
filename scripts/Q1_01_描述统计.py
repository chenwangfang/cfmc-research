#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_01_描述统计.py
==================
认知通达度与映射类型的描述性统计

输出：
- 图12: 认知通达度分布直方图
- 图12: 映射类型分布条形图
- 表58: 认知通达度分布
- 表58: 映射类型分布与概念复杂度对应
- 表58b: 映射类型与概念复杂度Tukey HSD事后检验
- 表58c: 映射类型与概念复杂度Kruskal-Wallis稳健性检验

创建日期：2025-12-05
"""

import sys
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import stats

from utils_公共函数 import (
    CONSTRUCTION_TYPE_12, MAPPING_DIRECTION_SHORT,
    DOMAIN_CODES,
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, format_stats,
    MAPPING_DIRECTION_CODES, setup_matplotlib_chinese
)


def analyze_cognitive_accessibility(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析认知通达度分布

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        认知通达度分布统计表
    """
    # 基本统计（确保数值类型）
    ca = pd.to_numeric(df['cognitive_accessibility'], errors='coerce').dropna()

    # 频率分布
    value_counts = ca.value_counts().sort_index()
    total = len(ca)

    # 构建分布表
    dist_data = []
    for level in sorted(ca.unique()):
        count = value_counts.get(level, 0)
        pct = count / total * 100
        cum_pct = value_counts[value_counts.index <= level].sum() / total * 100

        # 认知通达度等级标签
        if level <= 2:
            label = "低通达"
        elif level == 3:
            label = "中通达"
        else:
            label = "高通达"

        dist_data.append({
            '认知通达度': int(level),
            '等级': label,
            '频数': count,
            '百分比(%)': round(pct, 2),
            '累计百分比(%)': round(cum_pct, 2)
        })

    # 添加汇总统计
    dist_df = pd.DataFrame(dist_data)

    # 打印描述统计
    print("\n认知通达度描述统计:")
    print(f"  N = {len(ca)}")
    print(f"  M = {ca.mean():.3f}")
    print(f"  SD = {ca.std():.3f}")
    print(f"  Median = {ca.median():.1f}")
    print(f"  Range = {ca.min():.0f} - {ca.max():.0f}")
    print(f"  Skewness = {stats.skew(ca.astype(float)):.3f}")
    print(f"  Kurtosis = {stats.kurtosis(ca.astype(float)):.3f}")

    return dist_df


def analyze_mapping_direction(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析映射类型分布及其与概念复杂度的对应关系

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        映射类型分布统计表
    """
    # 映射方向频率
    md = df['mapping_direction'].dropna()
    cc = df['conceptual_complexity'].dropna()

    # 计算各类型的统计
    dist_data = []
    for code in sorted(md.unique()):
        mask = df['mapping_direction'] == code
        count = mask.sum()
        pct = count / len(md) * 100

        # 该类型的概念复杂度统计
        cc_subset = df.loc[mask, 'conceptual_complexity'].dropna()
        cc_mean = cc_subset.mean() if len(cc_subset) > 0 else np.nan
        cc_sd = cc_subset.std() if len(cc_subset) > 0 else np.nan

        label = MAPPING_DIRECTION_CODES.get(int(code), f'类型{int(code)}')

        dist_data.append({
            '映射类型': label,
            '代码': int(code),
            '频数': count,
            '百分比(%)': round(pct, 2),
            '概念复杂度M': round(cc_mean, 3) if not np.isnan(cc_mean) else '—',
            '概念复杂度SD': round(cc_sd, 3) if not np.isnan(cc_sd) else '—'
        })

    dist_df = pd.DataFrame(dist_data)

    # 打印映射类型分布
    print("\n映射类型分布:")
    for _, row in dist_df.iterrows():
        print(f"  {row['映射类型']}: n={row['频数']} ({row['百分比(%)']:.1f}%)")

    return dist_df






def analyze_source_domain(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析源域分布
    
    Parameters
    ----------
    df : pd.DataFrame
        构式数据
        
    Returns
    -------
    pd.DataFrame
        源域分布统计表
    """
    sd = df['source_domain'].dropna()
    total = len(sd)
    
    # 频率分布
    value_counts = sd.value_counts()
    
    dist_data = []
    cum_pct = 0
    for domain, count in value_counts.items():
        pct = count / total * 100
        cum_pct += pct
        label = DOMAIN_CODES.get(domain, domain)
        
        dist_data.append({
            '源域代码': domain,
            '源域名称': label,
            '频数': count,
            '百分比(%)': round(pct, 2),
            '累计百分比(%)': round(cum_pct, 2)
        })
    
    dist_df = pd.DataFrame(dist_data)
    
    print(f"\n源域分布 (共{len(value_counts)}类):")
    for _, row in dist_df.head(10).iterrows():
        print(f"  {row['源域名称']}({row['源域代码']}): n={row['频数']} ({row['百分比(%)']:.1f}%)")
    if len(dist_df) > 10:
        print(f"  ... 等共{len(dist_df)}类")
    
    return dist_df


def analyze_target_domain(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析目标域分布
    
    Parameters
    ----------
    df : pd.DataFrame
        构式数据
        
    Returns
    -------
    pd.DataFrame
        目标域分布统计表
    """
    td = df['target_domain'].dropna()
    total = len(td)
    
    # 频率分布
    value_counts = td.value_counts()
    
    dist_data = []
    cum_pct = 0
    for domain, count in value_counts.items():
        pct = count / total * 100
        cum_pct += pct
        label = DOMAIN_CODES.get(domain, domain)
        
        dist_data.append({
            '目标域代码': domain,
            '目标域名称': label,
            '频数': count,
            '百分比(%)': round(pct, 2),
            '累计百分比(%)': round(cum_pct, 2)
        })
    
    dist_df = pd.DataFrame(dist_data)
    
    print(f"\n目标域分布 (共{len(value_counts)}类):")
    for _, row in dist_df.head(10).iterrows():
        print(f"  {row['目标域名称']}({row['目标域代码']}): n={row['频数']} ({row['百分比(%)']:.1f}%)")
    if len(dist_df) > 10:
        print(f"  ... 等共{len(dist_df)}类")
    
    return dist_df


def analyze_domain_mapping_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析源域→目标域映射矩阵（交叉分布）
    
    Parameters
    ----------
    df : pd.DataFrame
        构式数据
        
    Returns
    -------
    pd.DataFrame
        源域×目标域交叉表
    """
    # 创建交叉表
    cross_tab = pd.crosstab(
        df['source_domain'].map(lambda x: DOMAIN_CODES.get(x, x)),
        df['target_domain'].map(lambda x: DOMAIN_CODES.get(x, x)),
        margins=True,
        margins_name='合计'
    )
    
    # 打印主要映射关系（频数>=50）
    print("\n主要源域→目标域映射关系 (频数≥50):")
    for sd in cross_tab.index[:-1]:  # 排除'合计'行
        for td in cross_tab.columns[:-1]:  # 排除'合计'列
            count = cross_tab.loc[sd, td]
            if count >= 50:
                pct = count / len(df) * 100
                print(f"  {sd}→{td}: n={count} ({pct:.1f}%)")
    
    return cross_tab




def get_construction_type_label(ca: int, md: int) -> str:
    """
    根据认知通达度和映射方向生成12类构式标签
    
    Parameters
    ----------
    ca : int
        认知通达度 (1-5)
    md : int
        映射方向 (1-4)
        
    Returns
    -------
    str
        构式类型标签，如 '高_具抽'
    """
    # 认知通达度分组
    if ca <= 2:
        ca_label = '低'
    elif ca == 3:
        ca_label = '中'
    else:
        ca_label = '高'
    
    # 映射方向简称
    md_short = MAPPING_DIRECTION_SHORT.get(md, str(md))
    
    return f'{ca_label}_{md_short}'


def analyze_domain_by_construction_type(df: pd.DataFrame) -> tuple:
    """
    按12类构式分析源域/目标域分布
    
    Parameters
    ----------
    df : pd.DataFrame
        构式数据
        
    Returns
    -------
    tuple
        (源域分布DataFrame, 目标域分布DataFrame)
    """
    # 生成构式类型标签
    df = df.copy()
    df['construction_type'] = df.apply(
        lambda row: get_construction_type_label(
            int(row['cognitive_accessibility']), 
            int(row['mapping_direction'])
        ), axis=1
    )
    
    # 按12类构式统计源域分布
    print("\n按12类构式统计源域分布:")
    source_data = []
    for ctype in CONSTRUCTION_TYPE_12:
        subset = df[df['construction_type'] == ctype]
        if len(subset) == 0:
            continue
        
        # 该类型的源域分布（Top 5）
        sd_counts = subset['source_domain'].value_counts()
        top5_sd = []
        for domain, count in sd_counts.head(5).items():
            pct = count / len(subset) * 100
            label = DOMAIN_CODES.get(domain, domain)
            top5_sd.append(f'{label}({pct:.0f}%)')
        
        source_data.append({
            '构式类型': ctype,
            '样本量': len(subset),
            '源域种类数': len(sd_counts),
            '主要源域(Top5)': ', '.join(top5_sd)
        })
        
        print(f"  {ctype} (n={len(subset)}): {', '.join(top5_sd[:3])}")
    
    source_df = pd.DataFrame(source_data)
    
    # 按12类构式统计目标域分布
    print("\n按12类构式统计目标域分布:")
    target_data = []
    for ctype in CONSTRUCTION_TYPE_12:
        subset = df[df['construction_type'] == ctype]
        if len(subset) == 0:
            continue
        
        # 该类型的目标域分布（Top 5）
        td_counts = subset['target_domain'].value_counts()
        top5_td = []
        for domain, count in td_counts.head(5).items():
            pct = count / len(subset) * 100
            label = DOMAIN_CODES.get(domain, domain)
            top5_td.append(f'{label}({pct:.0f}%)')
        
        target_data.append({
            '构式类型': ctype,
            '样本量': len(subset),
            '目标域种类数': len(td_counts),
            '主要目标域(Top5)': ', '.join(top5_td)
        })
        
        print(f"  {ctype} (n={len(subset)}): {', '.join(top5_td[:3])}")
    
    target_df = pd.DataFrame(target_data)
    
    return source_df, target_df


def analyze_domain_diversity_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析12类构式的源域/目标域多样性
    
    Parameters
    ----------
    df : pd.DataFrame
        构式数据
        
    Returns
    -------
    pd.DataFrame
        多样性统计表
    """
    from scipy.stats import entropy
    
    df = df.copy()
    df['construction_type'] = df.apply(
        lambda row: get_construction_type_label(
            int(row['cognitive_accessibility']), 
            int(row['mapping_direction'])
        ), axis=1
    )
    
    diversity_data = []
    for ctype in CONSTRUCTION_TYPE_12:
        subset = df[df['construction_type'] == ctype]
        if len(subset) == 0:
            continue
        
        # 源域多样性（Shannon熵）
        sd_counts = subset['source_domain'].value_counts()
        sd_probs = sd_counts / sd_counts.sum()
        sd_entropy = entropy(sd_probs, base=2)
        
        # 目标域多样性
        td_counts = subset['target_domain'].value_counts()
        td_probs = td_counts / td_counts.sum()
        td_entropy = entropy(td_probs, base=2)
        
        diversity_data.append({
            '构式类型': ctype,
            '样本量': len(subset),
            '源域种类': len(sd_counts),
            '源域熵': round(sd_entropy, 3),
            '目标域种类': len(td_counts),
            '目标域熵': round(td_entropy, 3)
        })
    
    diversity_df = pd.DataFrame(diversity_data)
    
    print("\n12类构式源域/目标域多样性:")
    print(diversity_df.to_string(index=False))
    
    return diversity_df


def analyze_md_cc_anova(df: pd.DataFrame) -> dict:
    """
    映射类型与概念复杂度的单因素方差分析、事后检验与稳健性检验
    
    Parameters
    ----------
    df : pd.DataFrame
        构式数据
        
    Returns
    -------
    dict
        ANOVA结果，包含F值、p值、η²、df、Tukey HSD与Kruskal-Wallis结果等
    """
    from scipy.stats import f_oneway
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    
    # 按映射类型分组
    groups = []
    group_labels = []
    for code in [1, 2, 3, 4]:
        mask = df['mapping_direction'] == code
        cc_data = df.loc[mask, 'conceptual_complexity'].dropna()
        if len(cc_data) > 0:
            groups.append(cc_data)
            group_labels.append(code)
    
    # 单因素方差分析
    f_stat, p_value = f_oneway(*groups)

    # Tukey HSD事后检验
    tukey_input = df[['mapping_direction', 'conceptual_complexity']].dropna().copy()
    tukey_input['映射类型'] = tukey_input['mapping_direction'].map(MAPPING_DIRECTION_CODES)
    tukey_result = pairwise_tukeyhsd(
        endog=tukey_input['conceptual_complexity'],
        groups=tukey_input['映射类型'],
        alpha=0.05
    )
    tukey_rows = tukey_result.summary().data
    tukey_df = pd.DataFrame(tukey_rows[1:], columns=tukey_rows[0])
    tukey_df = tukey_df.rename(columns={
        'group1': '组1',
        'group2': '组2',
        'meandiff': '均值差',
        'p-adj': 'p_adj',
        'lower': '95%CI下限',
        'upper': '95%CI上限',
        'reject': '是否显著'
    })
    for col in ['均值差', '95%CI下限', '95%CI上限']:
        tukey_df[col] = pd.to_numeric(tukey_df[col], errors='coerce').round(4)
    p_adj_numeric = pd.to_numeric(tukey_df['p_adj'], errors='coerce')
    tukey_df['p_adj'] = p_adj_numeric.map(
        lambda value: '<.001' if pd.notna(value) and value < 0.001 else f'{value:.4f}'
    )

    # 概念复杂度为1-4级有序评分，补充非参数稳健性检验
    h_stat, kruskal_p = stats.kruskal(*groups)
    
    # 计算η² (eta squared)
    # η² = SS_between / SS_total
    all_cc = df['conceptual_complexity'].dropna()
    grand_mean = all_cc.mean()
    
    # SS_between: 组间平方和
    ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
    
    # SS_total: 总平方和
    ss_total = sum((all_cc - grand_mean)**2)
    
    eta_squared = ss_between / ss_total
    
    # 自由度
    k = len(groups)  # 组数
    n = sum(len(g) for g in groups)  # 总样本量
    df_between = k - 1
    df_within = n - k
    
    result = {
        'F': f_stat,
        'p': p_value,
        'eta_squared': eta_squared,
        'df_between': df_between,
        'df_within': df_within,
        'k': k,
        'n': n,
        'tukey_hsd': tukey_df,
        'kruskal_h': h_stat,
        'kruskal_p': kruskal_p,
        'kruskal_df': k - 1
    }
    
    print("\n映射类型与概念复杂度ANOVA分析:")
    print(f"  F({df_between}, {df_within}) = {f_stat:.3f}")
    print(f"  p < .001" if p_value < 0.001 else f"  p = {p_value:.4f}")
    print(f"  η² = {eta_squared:.4f}")
    print(f"  Kruskal-Wallis H({k - 1}) = {h_stat:.3f}")
    print(f"  Kruskal-Wallis p < .001" if kruskal_p < 0.001 else f"  Kruskal-Wallis p = {kruskal_p:.4f}")
    print(f"  效应量解释: ", end="")
    if eta_squared < 0.01:
        print("极小效应")
    elif eta_squared < 0.06:
        print("小效应")
    elif eta_squared < 0.14:
        print("中等效应")
    else:
        print("大效应")
    print("  Tukey HSD: 四类映射类型两两差异均显著" if tukey_df['是否显著'].all() else "  Tukey HSD: 存在未达显著的两两差异")
    
    return result


def plot_cognitive_accessibility_histogram(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制认知通达度分布直方图（图12）

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
    # 设置字体
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=12)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_en = fm.FontProperties(fname=font_paths['english'], size=10)

    ca = df['cognitive_accessibility'].dropna()

    fig, ax = plt.subplots(figsize=(10, 6))

    # 直方图
    counts, bins, patches = ax.hist(ca, bins=5, range=(0.5, 5.5),
                                    color='#3498db', edgecolor='white',
                                    alpha=0.8, rwidth=0.85)

    # 添加频数标签
    for count, patch in zip(counts, patches):
        height = patch.get_height()
        ax.annotate(f'{int(count)}',
                   xy=(patch.get_x() + patch.get_width() / 2, height),
                   ha='center', va='bottom', fontsize=11,
                   fontproperties=font_en)

    # 添加均值线
    mean_val = ca.mean()
    ax.axvline(x=mean_val, color='#e74c3c', linestyle='--', linewidth=2,
               label=f'均值 = {mean_val:.2f}')

    # 设置坐标轴
    ax.set_xlabel('认知通达度', fontproperties=font_cn, fontsize=12)
    ax.set_ylabel('频数', fontproperties=font_cn, fontsize=12)
    # ax.set_title('图12 认知通达度分布直方图', fontproperties=font_cn_title, fontsize=14, pad=15)

    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(['1\n（极低）', '2\n（低）', '3\n（中）', '4\n（高）', '5\n（极高）'],
                       fontproperties=font_cn, fontsize=10)

    # 添加统计信息文本框（位置左移避免覆盖柱子）
    stats_text = f'N = {len(ca)}\nM = {ca.mean():.2f}\nSD = {ca.std():.2f}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.68, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=props, fontproperties=font_en)

    ax.legend(loc='upper left', prop=font_cn)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    return fig


def plot_mapping_direction_bar(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制映射类型分布条形图（图12）

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
    # 设置字体
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=12)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_en = fm.FontProperties(fname=font_paths['english'], size=10)

    md = df['mapping_direction'].dropna()
    cc = df['conceptual_complexity']

    # 准备数据
    labels = []
    counts = []
    cc_means = []
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']

    for code in [1, 2, 3, 4]:
        mask = md == code
        label = MAPPING_DIRECTION_CODES.get(code, f'类型{code}')
        labels.append(label)
        counts.append(mask.sum())
        cc_means.append(df.loc[mask, 'conceptual_complexity'].mean())

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 条形图（频数）
    x = np.arange(len(labels))
    width = 0.6
    bars = ax1.bar(x, counts, width, color=colors, edgecolor='white', alpha=0.8)

    # 添加频数标签
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        pct = count / sum(counts) * 100
        ax1.annotate(f'{count}\n（{pct:.1f}%）',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    ha='center', va='bottom', fontsize=10,
                    fontproperties=font_cn)

    # 设置主坐标轴
    ax1.set_xlabel('映射类型', fontproperties=font_cn, fontsize=12)
    ax1.set_ylabel('频数', fontproperties=font_cn, fontsize=12)
    # ax1.set_title('图12 映射类型分布条形图', fontproperties=font_cn_title, fontsize=14, pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontproperties=font_cn, fontsize=11)
    ax1.set_ylim(0, 3000)  # 设置Y轴范围，使柱子比例更合适

    # 次坐标轴（概念复杂度均值）- 使用红色区分
    ax2 = ax1.twinx()
    ax2.plot(x, cc_means, 'ro-', markersize=8, linewidth=2, label='概念复杂度均值')
    ax2.set_ylabel('概念复杂度均值', fontproperties=font_cn, fontsize=12, color='#e74c3c')
    ax2.set_ylim(1, 5)
    ax2.tick_params(axis='y', colors='#e74c3c')  # 右侧刻度也用红色

    # 添加概念复杂度标签
    for i, (xi, yi) in enumerate(zip(x, cc_means)):
        ax2.annotate(f'{yi:.2f}', xy=(xi, yi), xytext=(5, 5),
                    textcoords='offset points', fontsize=9,
                    fontproperties=font_en, color='#e74c3c')

    # 图例
    ax2.legend(loc='upper right', prop=font_cn, labelcolor='#e74c3c')

    ax1.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    return fig


def main():
    """主函数"""
    print("=" * 60)
    print("Q1_01_描述统计.py")
    print("认知通达度与映射类型的描述性统计")
    print("=" * 60)

    # 获取路径
    paths = get_paths()
    print(f"\n数据文件: {paths['data_file']}")

    # 加载数据
    df, meta = load_cfmc_data()
    print(f"数据量: {len(df)} 条")

    # 1. 认知通达度分布分析
    print("\n" + "-" * 40)
    print("1. 认知通达度分布分析")
    print("-" * 40)
    ca_dist = analyze_cognitive_accessibility(df)

    # [已移至附录F] 保存表58
    # [已移至附录F] save_table(ca_dist, "认知通达度分布", global_num=58,
    # [已移至附录F] title="认知通达度分布", formats=['csv', 'json'])

    # 输出附录F表格到Data目录
    save_table(ca_dist, "认知通达度分布_附录F", global_num='F1',
               title="认知通达度分布", formats=['csv', 'json'])
    print("[OK] 表F-1 已保存")


    # 2. 映射类型分布分析
    print("\n" + "-" * 40)
    print("2. 映射类型分布分析")
    print("-" * 40)
    md_dist = analyze_mapping_direction(df)

    # 保存表58
    save_table(md_dist, "映射类型分布与概念复杂度对应", global_num=58,
               title="映射类型分布与概念复杂度对应", formats=['csv', 'json'])

    # [已移至附录F] 3. 绘制图12: 认知通达度分布直方图
    # [已移至附录F] print("\n" + "-" * 40)
    # [已移至附录F] print("3. 绘制图12: 认知通达度分布直方图")
    # [已移至附录F] print("-" * 40)
    # [已移至附录F] fig1 = plot_cognitive_accessibility_histogram(df, paths)
    # [已移至附录F] save_figure(fig1, "认知通达度分布直方图", global_num=12,
    # [已移至附录F] title="认知通达度分布直方图")


    # 2.1 源域分布分析
    print("\n" + "-" * 40)
    print("2.1 源域分布分析")
    print("-" * 40)
    sd_dist = analyze_source_domain(df)
    save_table(sd_dist, "源域分布", global_num="57a",
               title="源域分布统计", formats=['csv', 'json'])
    
    # 2.2 目标域分布分析
    print("\n" + "-" * 40)
    print("2.2 目标域分布分析")
    print("-" * 40)
    td_dist = analyze_target_domain(df)
    save_table(td_dist, "目标域分布", global_num="57b",
               title="目标域分布统计", formats=['csv', 'json'])
    
    # 2.3 源域×目标域交叉分布
    print("\n" + "-" * 40)
    print("2.3 源域×目标域交叉分布")
    print("-" * 40)
    cross_matrix = analyze_domain_mapping_matrix(df)
    save_table(cross_matrix, "源域目标域交叉分布", global_num="57c",
               title="源域×目标域交叉分布矩阵", formats=['csv', 'json'])


    # 4. 绘制图12
    print("\n" + "-" * 40)
    print("4. 绘制图12: 映射类型分布条形图")
    print("-" * 40)
    fig2 = plot_mapping_direction_bar(df, paths)
    save_figure(fig2, "映射类型分布条形图", global_num=11,
                title="映射类型分布条形图")



    # 2.4 按12类构式分析源域/目标域分布
    print("\n" + "-" * 40)
    print("2.4 按12类构式分析源域/目标域分布")
    print("-" * 40)
    sd_by_type, td_by_type = analyze_domain_by_construction_type(df)
    save_table(sd_by_type, "12类构式源域分布", global_num="57d",
               title="12类构式源域分布", formats=['csv', 'json'])
    save_table(td_by_type, "12类构式目标域分布", global_num="57e",
               title="12类构式目标域分布", formats=['csv', 'json'])
    
    # 2.5 源域/目标域多样性分析
    print("\n" + "-" * 40)
    print("2.5 源域/目标域多样性分析")
    print("-" * 40)
    diversity_df = analyze_domain_diversity_by_type(df)
    save_table(diversity_df, "12类构式域多样性", global_num="57f",
               title="12类构式源域目标域多样性", formats=['csv', 'json'])


    # 2.7 映射类型与概念复杂度ANOVA分析
    print("\n" + "-" * 40)
    print("2.7 映射类型与概念复杂度ANOVA分析")
    print("-" * 40)
    anova_result = analyze_md_cc_anova(df)
    
    # 保存ANOVA结果
    anova_df = pd.DataFrame([{
        '分析项目': '映射类型→概念复杂度',
        'df_between': anova_result['df_between'],
        'df_within': anova_result['df_within'],
        'F': round(anova_result['F'], 3),
        'p': '<.001' if anova_result['p'] < 0.001 else f"{anova_result['p']:.4f}",
        'η²': round(anova_result['eta_squared'], 4)
    }])
    save_table(anova_df, "映射类型与概念复杂度ANOVA", global_num="58_anova",
               title="映射类型与概念复杂度单因素方差分析", formats=['csv', 'json'])

    save_table(anova_result['tukey_hsd'], "映射类型概念复杂度TukeyHSD", global_num="58b",
               title="映射类型与概念复杂度Tukey HSD事后检验", formats=['csv', 'json'])

    kruskal_df = pd.DataFrame([{
        '分析项目': '映射类型→概念复杂度',
        'df': anova_result['kruskal_df'],
        'H': round(anova_result['kruskal_h'], 3),
        'p': '<.001' if anova_result['kruskal_p'] < 0.001 else f"{anova_result['kruskal_p']:.4f}",
        '说明': '概念复杂度为1-4级有序评分，Kruskal-Wallis作为非参数稳健性检验'
    }])
    save_table(kruskal_df, "映射类型概念复杂度KruskalWallis", global_num="58c",
               title="映射类型与概念复杂度Kruskal-Wallis稳健性检验", formats=['csv', 'json'])


    # 5. 汇总描述统计
    print("\n" + "-" * 40)
    print("5. 核心变量汇总描述统计")
    print("-" * 40)

    # 创建汇总统计表
    summary_vars = ['cognitive_accessibility', 'conceptual_complexity',
                    'mapping_direction', 'prototype_distance']
    summary_data = []

    for var in summary_vars:
        if var in df.columns:
            data = pd.to_numeric(df[var], errors='coerce').dropna().astype(float)
            summary_data.append({
                '变量': var,
                'N': len(data),
                '均值': round(data.mean(), 3),
                '标准差': round(data.std(), 3),
                '最小值': round(data.min(), 3),
                '最大值': round(data.max(), 3),
                '偏度': round(stats.skew(data), 3),
                '峰度': round(stats.kurtosis(data), 3)
            })

    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))

    print("\n" + "=" * 60)
    print("Q1_01_描述统计 完成")
    print("=" * 60)

    return ca_dist, md_dist


if __name__ == "__main__":
    ca_dist, md_dist = main()
