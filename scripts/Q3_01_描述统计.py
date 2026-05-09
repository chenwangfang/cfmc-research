#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q3_01_描述统计.py
=================
认知加工指标的描述统计分析

输出：
- 表85: 认知编码机制相关变量描述统计
- 表92b: 四阶段指标相关矩阵
- 图26: 四阶段指标分布图
- 图27: 四阶段指标相关矩阵热力图

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
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, get_font_paths, load_cfmc_data,
    save_figure, save_table, CONSTRUCTION_COLORS,
    COPULA_FUNCTION_CODES
)


# 四阶段认知编码机制的字段映射（使用ASCII安全字符避免乱码）
STAGE_FIELDS = {
    'eta1_认知域激活': ['embodied_experience', 'source_domain', 'target_domain'],
    'eta2_参照点锚定': ['conventionality', 'cognitive_accessibility', 'prototype_distance'],
    'eta3_跨域映射': ['mapping_direction', 'systematicity', 'entailment_richness'],
    'X11_系词功能': ['copula_function']
}

# 阶段符号映射（用于图表标注，使用LaTeX格式）
STAGE_SYMBOLS = {
    'eta1_认知域激活': r'$\eta_1$',
    'eta2_参照点锚定': r'$\eta_2$',
    'eta3_跨域映射': r'$\eta_3$',
    'X11_系词功能': r'$X_{11}$'
}

# 阶段中文名称（用于图例）
STAGE_NAMES_CN = {
    'eta1_认知域激活': '认知域激活',
    'eta2_参照点锚定': '参照点锚定',
    'eta3_跨域映射': '跨域映射',
    'X11_系词功能': '系词功能'
}

# 所有SEM分析使用的字段
SEM_FIELDS = [
    'embodied_experience', 'source_domain', 'target_domain',
    'conventionality', 'cognitive_accessibility', 'prototype_distance',
    'mapping_direction', 'systematicity', 'entailment_richness',
    'copula_function'
]

# 字段中文名称
FIELD_NAMES_CN = {
    'embodied_experience': '具身体验',
    'source_domain': '源域',
    'target_domain': '目标域',
    'conventionality': '常规度',
    'cognitive_accessibility': '认知通达度',
    'prototype_distance': '原型距离',
    'mapping_direction': '映射方向',
    'systematicity': '系统性',
    'entailment_richness': '蕴涵丰富度',
    'copula_function': '系词功能'
}


def prepare_sem_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    准备SEM分析数据

    Parameters
    ----------
    df : pd.DataFrame
        原始数据

    Returns
    -------
    pd.DataFrame
        处理后的数据
    """
    sem_df = df.copy()

    # 检查并处理各字段
    for field in SEM_FIELDS:
        if field not in sem_df.columns:
            print(f"  [WARN] 缺失字段: {field}，将尝试推断或填充")
            sem_df[field] = np.nan

    # 1. 处理源域和目标域（分类变量转换为数值）
    if 'source_domain' in sem_df.columns:
        # 源域编码为数值（基于出现频率排序）
        source_map = {s: i+1 for i, s in enumerate(sem_df['source_domain'].value_counts().index)}
        sem_df['source_domain_num'] = sem_df['source_domain'].map(source_map)

    if 'target_domain' in sem_df.columns:
        target_map = {t: i+1 for i, t in enumerate(sem_df['target_domain'].value_counts().index)}
        sem_df['target_domain_num'] = sem_df['target_domain'].map(target_map)

    # 2. 处理具身体验（如果是分类变量）
    if 'embodied_experience' in sem_df.columns:
        if sem_df['embodied_experience'].dtype == 'object':
            # 假设是等级变量，转换为数值
            exp_map = {'low': 1, 'medium': 2, 'high': 3}
            sem_df['embodied_experience'] = sem_df['embodied_experience'].map(
                lambda x: exp_map.get(str(x).lower(), 2) if pd.notna(x) else 2
            )

    # 3. 处理系词功能（结果变量）- 使用utils常量
    if 'copula_function' in sem_df.columns:
        if sem_df['copula_function'].dtype == 'object':
            sem_df['copula_function_num'] = sem_df['copula_function'].map(
                lambda x: COPULA_FUNCTION_CODES.get(str(x).lower(), 1) if pd.notna(x) else 1
            )

    # 4. 用Q1_05输出的连续标准化欧氏距离替换JSON中的等级值（1/2/3→连续值）
    from pathlib import Path as _Path
    grades_path = _Path(__file__).resolve().parent.parent / '结果_输出' / 'Data' / 'CFMC_with_prototype_grades.csv'
    if grades_path.exists():
        grades_df = pd.read_csv(str(grades_path))
        id_to_dist = dict(zip(grades_df['id'], grades_df['prototype_distance']))
        id_to_grade = dict(zip(grades_df['id'], grades_df['prototype_grade']))
        if 'id' in sem_df.columns:
            sem_df['prototype_distance'] = sem_df['id'].map(id_to_dist)
            sem_df['prototype_grade'] = sem_df['id'].map(id_to_grade)
        else:
            sem_df['prototype_distance'] = sem_df.index.map(id_to_dist)
            sem_df['prototype_grade'] = sem_df.index.map(id_to_grade)
        print(f"  [OK] prototype_distance已替换为连续标准化欧氏距离 (from {grades_path.name})")
        print(f"       prototype_grade分布: {sem_df['prototype_grade'].value_counts().sort_index().to_dict()}")
    else:
        print(f"  [WARN] {grades_path}不存在，prototype_distance保留原值")

    # 5. 处理其他数值字段中的缺失值
    numeric_fields = ['conventionality', 'cognitive_accessibility', 'prototype_distance',
                     'mapping_direction', 'systematicity', 'entailment_richness',
                     'embodied_experience']

    for field in numeric_fields:
        if field in sem_df.columns:
            # 使用中位数填充
            median_val = sem_df[field].median()
            if pd.isna(median_val):
                median_val = 3  # 默认中间值
            sem_df[field] = sem_df[field].fillna(median_val)

    return sem_df


def calculate_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算四阶段指标的描述统计

    Parameters
    ----------
    df : pd.DataFrame
        数据

    Returns
    -------
    pd.DataFrame
        描述统计表
    """
    stats_data = []

    # 确定要分析的数值字段
    numeric_fields = []
    for field in SEM_FIELDS:
        if field in df.columns:
            # 检查是否为数值型或有对应的数值版本
            if pd.api.types.is_numeric_dtype(df[field]):
                numeric_fields.append(field)
            elif f'{field}_num' in df.columns:
                numeric_fields.append(f'{field}_num')

    # 添加额外的数值版本字段
    for field in ['source_domain_num', 'target_domain_num', 'copula_function_num']:
        if field in df.columns and field not in numeric_fields:
            numeric_fields.append(field)

    for field in numeric_fields:
        values = df[field].dropna()
        if len(values) == 0:
            continue

        # 确定字段的中文名称
        base_field = field.replace('_num', '')
        cn_name = FIELD_NAMES_CN.get(base_field, field)

        # 确定所属阶段
        stage = '未分类'
        for stage_name, fields in STAGE_FIELDS.items():
            if base_field in fields:
                stage = stage_name
                break

        stats_data.append({
            '阶段': stage,
            '变量': cn_name,
            '字段名': field,
            'N': len(values),
            '均值': round(values.mean(), 3),
            '标准差': round(values.std(), 3),
            '最小值': round(values.min(), 2),
            '最大值': round(values.max(), 2),
            '偏度': round(stats.skew(values), 3),
            '峰度': round(stats.kurtosis(values), 3)
        })

    result = pd.DataFrame(stats_data)

    # 按阶段排序
    stage_order = ['eta1_认知域激活', 'eta2_参照点锚定', 'eta3_跨域映射', 'X11_系词功能', '未分类']
    result['阶段排序'] = result['阶段'].apply(lambda x: stage_order.index(x) if x in stage_order else 99)
    result = result.sort_values('阶段排序').drop('阶段排序', axis=1)

    return result


def calculate_correlation_matrix(df: pd.DataFrame) -> tuple:
    """
    计算四阶段指标的相关矩阵

    Parameters
    ----------
    df : pd.DataFrame
        数据

    Returns
    -------
    tuple
        (相关矩阵DataFrame, p值矩阵DataFrame)
    """
    # 选择用于相关分析的字段（按阶段顺序）
    corr_fields = []
    field_labels = []
    field_stages = []  # 记录每个字段所属阶段

    # 按STAGE_FIELDS顺序遍历，确保变量按阶段排列
    for stage_name, fields in STAGE_FIELDS.items():
        stage_symbol = STAGE_SYMBOLS.get(stage_name, '')
        for field in fields:
            field_added = False
            # 支持多种数值类型：int64, float64, Int64, Float64
            if field in df.columns and str(df[field].dtype) in ['int64', 'float64', 'Int64', 'Float64']:
                corr_fields.append(field)
                field_labels.append(f'{FIELD_NAMES_CN.get(field, field)}({stage_symbol})')
                field_stages.append(stage_name)
                field_added = True
            elif f'{field}_num' in df.columns:
                corr_fields.append(f'{field}_num')
                field_labels.append(f'{FIELD_NAMES_CN.get(field, field)}({stage_symbol})')
                field_stages.append(stage_name)
                field_added = True

            if not field_added:
                print(f"  [WARN] 字段 {field} 未找到数值版本")

    if len(corr_fields) < 2:
        print("  [WARN] 可用于相关分析的字段不足")
        return pd.DataFrame(), pd.DataFrame()

    # 计算相关矩阵
    corr_data = df[corr_fields].dropna()
    n = len(corr_data)

    corr_matrix = corr_data.corr()
    corr_matrix.columns = field_labels
    corr_matrix.index = field_labels

    # 计算p值矩阵
    p_matrix = pd.DataFrame(np.zeros((len(corr_fields), len(corr_fields))),
                           columns=field_labels, index=field_labels)

    for i, col1 in enumerate(corr_fields):
        for j, col2 in enumerate(corr_fields):
            if i != j:
                r, p = stats.pearsonr(corr_data[col1], corr_data[col2])
                p_matrix.iloc[i, j] = p
            else:
                p_matrix.iloc[i, j] = 0

    return corr_matrix, p_matrix


def plot_stage_distributions(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制四阶段指标分布图（图26）

    Parameters
    ----------
    df : pd.DataFrame
        数据
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
    font_cn_legend = fm.FontProperties(fname=font_paths['chinese'], size=11)

    fig = plt.figure(figsize=(16, 12))

    # 创建3x4子图（4个阶段，每个阶段若干指标）
    gs = fig.add_gridspec(3, 4, hspace=0.35, wspace=0.3)

    plot_idx = 0
    stage_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']

    for stage_idx, (stage_name, fields) in enumerate(STAGE_FIELDS.items()):
        stage_symbol = STAGE_SYMBOLS.get(stage_name, '')

        for field in fields:
            if plot_idx >= 11:  # 保留第12个位置给图例
                break

            row = plot_idx // 4
            col = plot_idx % 4
            ax = fig.add_subplot(gs[row, col])

            # 获取数据
            values = None
            if field in df.columns:
                if pd.api.types.is_numeric_dtype(df[field]):
                    values = df[field].dropna()
                elif df[field].dtype == 'object':
                    # 分类字段：使用类别编码
                    categories = df[field].dropna().astype('category')
                    values = pd.Series(categories.cat.codes, index=categories.index)
                    values = values[values >= 0]  # 排除-1（NaN编码）
            elif f'{field}_num' in df.columns:
                values = df[f'{field}_num'].dropna()

            if values is None or len(values) == 0:
                ax.text(0.5, 0.5, f'{FIELD_NAMES_CN.get(field, field)}\n数据不可用',
                       ha='center', va='center', fontproperties=font_cn)
                ax.axis('off')
                plot_idx += 1
                continue

            # 绘制直方图
            ax.hist(values, bins=20, color=stage_colors[stage_idx], alpha=0.7, edgecolor='black')
            # 使用LaTeX格式的斜体M
            ax.axvline(values.mean(), color='red', linestyle='--', linewidth=2,
                      label=f'$M$={values.mean():.2f}')

            # 子图标题添加阶段符号
            ax.set_title(f'{FIELD_NAMES_CN.get(field, field)} ({stage_symbol})',
                        fontproperties=font_cn, fontsize=10)
            ax.set_xlabel('取值', fontproperties=font_cn, fontsize=9)
            ax.set_ylabel('频数', fontproperties=font_cn, fontsize=9)

            # 根据数据分布自动选择图例位置：数据偏右则图例放左上角
            data_midpoint = (values.min() + values.max()) / 2
            legend_loc = 'upper left' if values.mean() > data_midpoint else 'upper right'
            ax.legend(prop=font_cn, fontsize=8, loc=legend_loc)

            plot_idx += 1

    # 在第12个子图位置绘制阶段颜色图例
    ax_legend = fig.add_subplot(gs[2, 3])
    ax_legend.axis('off')

    # 创建阶段颜色图例
    legend_elements = []
    for stage_idx, (stage_name, _) in enumerate(STAGE_FIELDS.items()):
        stage_symbol = STAGE_SYMBOLS.get(stage_name, '')
        stage_cn = STAGE_NAMES_CN.get(stage_name, stage_name)
        from matplotlib.patches import Patch
        legend_elements.append(Patch(facecolor=stage_colors[stage_idx],
                                     edgecolor='black', alpha=0.7,
                                     label=f'{stage_symbol} {stage_cn}'))

    ax_legend.legend(handles=legend_elements, loc='center',
                    prop=font_cn_legend, frameon=True,
                    fancybox=True, shadow=True,
                    title='阶段说明', title_fontproperties=font_cn_legend)

    # plt.suptitle('图27 四阶段认知编码指标分布图',
                # fontproperties=font_cn_title, fontsize=14, y=0.98)

    return fig


def plot_correlation_heatmap(corr_matrix: pd.DataFrame, p_matrix: pd.DataFrame,
                            paths: dict) -> plt.Figure:
    """
    绘制相关矩阵热力图

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        相关矩阵
    p_matrix : pd.DataFrame
        p值矩阵
    paths : dict
        路径字典

    Returns
    -------
    Figure
        matplotlib图表对象
    """
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=9)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)

    # 根据变量数量调整图表尺寸
    n_vars = len(corr_matrix)
    fig_size = max(12, n_vars * 1.1)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size * 0.85))

    # 创建注释矩阵（显示相关系数和显著性标记）
    annot_matrix = corr_matrix.copy()
    for i in range(len(corr_matrix)):
        for j in range(len(corr_matrix)):
            r = corr_matrix.iloc[i, j]
            p = p_matrix.iloc[i, j]

            if i == j:
                annot_matrix.iloc[i, j] = '1.00'
            else:
                sig = ''
                if p < 0.001:
                    sig = '***'
                elif p < 0.01:
                    sig = '**'
                elif p < 0.05:
                    sig = '*'
                annot_matrix.iloc[i, j] = f'{r:.2f}{sig}'

    # 绘制热力图
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)

    heatmap = sns.heatmap(corr_matrix, ax=ax, mask=mask,
               cmap='RdYlBu_r', center=0, vmin=-1, vmax=1,
               annot=annot_matrix.values, fmt='',
               square=True, linewidths=0.5,
               annot_kws={'fontsize': 9},
               cbar_kws={'shrink': 0.8})

    # 设置颜色条标签（需要单独设置字体）
    cbar = heatmap.collections[0].colorbar
    cbar.set_label('相关系数 $r$', fontproperties=font_cn, fontsize=11)

    # 设置标签
    ax.set_xticklabels(corr_matrix.columns, fontproperties=font_cn, rotation=45, ha='right')
    ax.set_yticklabels(corr_matrix.index, fontproperties=font_cn, rotation=0)

    # 标题中p使用斜体（LaTeX格式）
    # ax.set_title(r'图27 四阶段指标相关矩阵热力图' + '\n' + r'(*$p$<.05, **$p$<.01, ***$p$<.001)',
                # fontproperties=font_cn_title, fontsize=12, pad=20)

    plt.tight_layout()

    return fig


def analyze_stage_relationships(df: pd.DataFrame) -> None:
    """
    分析阶段间关系

    Parameters
    ----------
    df : pd.DataFrame
        数据
    """
    print("\n阶段间关系分析:")
    print("-" * 60)

    # 计算各阶段的综合得分
    stage_scores = {}

    for stage_name, fields in STAGE_FIELDS.items():
        values = []
        for field in fields:
            if field in df.columns and pd.api.types.is_numeric_dtype(df[field]):
                # 标准化后求均值
                v = df[field].dropna()
                if len(v) > 0:
                    v_std = (v - v.mean()) / v.std()
                    values.append(v_std)
            elif f'{field}_num' in df.columns:
                v = df[f'{field}_num'].dropna()
                if len(v) > 0:
                    v_std = (v - v.mean()) / v.std()
                    values.append(v_std)

        if values:
            # 取交集索引的均值
            stage_scores[stage_name] = pd.concat(values, axis=1).mean(axis=1)
            print(f"\n{stage_name}:")
            print(f"  综合得分均值: {stage_scores[stage_name].mean():.4f}")
            print(f"  综合得分标准差: {stage_scores[stage_name].std():.4f}")

    # 阶段间相关
    if len(stage_scores) >= 2:
        print("\n阶段间相关:")
        stage_names = list(stage_scores.keys())
        for i in range(len(stage_names)):
            for j in range(i+1, len(stage_names)):
                s1, s2 = stage_names[i], stage_names[j]
                # 找到共同索引
                common_idx = stage_scores[s1].dropna().index.intersection(
                    stage_scores[s2].dropna().index)
                if len(common_idx) > 2:
                    r, p = stats.pearsonr(
                        stage_scores[s1].loc[common_idx],
                        stage_scores[s2].loc[common_idx]
                    )
                    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
                    print(f"  {s1} ↔ {s2}: r={r:.3f}{sig}")



def calculate_kmo_bartlett(df: pd.DataFrame):
    """计算KMO检验和Bartlett球形检验，保存结果到Data目录。

    KMO采用反映像相关矩阵方法手动计算，不依赖factor_analyzer库。
    """
    import json

    paths = get_paths()

    # 使用PLS-SEM模型A的10个指标变量（与Q3_02 build_model_A一致）
    all_vars = [
        'embodied_experience', 'source_domain_num', 'target_domain_num',  # η₁
        'conventionality', 'cognitive_accessibility', 'prototype_distance',  # η₂
        'mapping_direction', 'systematicity', 'entailment_richness',  # η₃
        'copula_function_num'  # Y
    ]

    X = df[all_vars].dropna().astype(float)
    n, k = X.shape

    # 相关矩阵
    R = np.corrcoef(X.values, rowvar=False)

    # --- KMO ---
    # 反映像矩阵 = diag(R_inv)^{-1/2} @ R_inv @ diag(R_inv)^{-1/2}
    R_inv = np.linalg.inv(R)
    D = np.diag(1.0 / np.sqrt(np.diag(R_inv)))
    anti_image = D @ R_inv @ D  # 偏相关矩阵

    # KMO = sum(r_ij^2) / (sum(r_ij^2) + sum(a_ij^2))，仅取非对角元素
    np.fill_diagonal(R, 0)
    np.fill_diagonal(anti_image, 0)
    sum_r2 = np.sum(R ** 2)
    sum_a2 = np.sum(anti_image ** 2)
    kmo_overall = sum_r2 / (sum_r2 + sum_a2)

    # --- Bartlett球形检验 ---
    # 恢复对角线
    np.fill_diagonal(R, 1.0)
    det_R = np.linalg.det(R)
    chi2 = -(n - 1 - (2 * k + 5) / 6) * np.log(det_R)
    dof = k * (k - 1) / 2
    p_value = 1 - stats.chi2.cdf(chi2, dof)

    # 输出结果
    print(f"  KMO = {kmo_overall:.4f}")
    print(f"  Bartlett χ² = {chi2:.2f}, df = {int(dof)}, p < .001" if p_value < 0.001
          else f"  Bartlett χ² = {chi2:.2f}, df = {int(dof)}, p = {p_value:.4f}")

    # 保存为JSON
    result = {
        'KMO': round(kmo_overall, 4),
        'Bartlett_chi2': round(chi2, 2),
        'Bartlett_df': int(dof),
        'Bartlett_p': round(p_value, 6),
        'n': int(n),
        'k': int(k),
        'variables': all_vars
    }

    output_path = paths['output_data'] / '表85b_KMO与Bartlett检验.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 已保存: {output_path.name}")

    return result


def main():
    """主函数"""
    print("=" * 60)
    print("Q3_01_描述统计.py")
    print("认知加工指标的描述统计分析")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载数据
    print("\n" + "-" * 40)
    print("1. 加载数据")
    print("-" * 40)
    df, _ = load_cfmc_data()
    print(f"样本量: {len(df)}")
    print(f"字段数: {len(df.columns)}")

    # 2. 准备SEM数据
    print("\n" + "-" * 40)
    print("2. 准备SEM分析数据")
    print("-" * 40)
    sem_df = prepare_sem_data(df)

    # 检查可用字段
    available_fields = []
    for field in SEM_FIELDS:
        if field in sem_df.columns:
            if pd.api.types.is_numeric_dtype(sem_df[field]):
                available_fields.append(field)
                print(f"  [OK] {field}: 数值型")
            else:
                print(f"  [~] {field}: 非数值型 ({sem_df[field].dtype})")
        elif f'{field}_num' in sem_df.columns:
            available_fields.append(f'{field}_num')
            print(f"  [OK] {field}_num: 数值型（转换）")
        else:
            print(f"  [X] {field}: 不可用")

    # 保存处理后的数据
    sem_output_file = paths['output_data'] / 'CFMC_for_SEM.csv'
    sem_df.to_csv(sem_output_file, index=True, encoding='utf-8-sig')
    print(f"\n[OK] 已保存SEM分析数据: {sem_output_file}")

    # 3. 描述统计
    print("\n" + "-" * 40)
    print("3. 计算描述统计")
    print("-" * 40)
    desc_stats = calculate_descriptive_stats(sem_df)
    print(desc_stats.to_string(index=False))

    # 保存表85
    save_table(desc_stats, "认知编码机制相关变量描述统计", global_num=85,
               title="认知编码机制相关变量描述统计", formats=['csv', 'json'])

    # 4. 相关分析
    print("\n" + "-" * 40)
    print("4. 计算相关矩阵")
    print("-" * 40)
    corr_matrix, p_matrix = calculate_correlation_matrix(sem_df)

    if not corr_matrix.empty:
        print(corr_matrix.round(3).to_string())

        # 保存表92b
        save_table(corr_matrix.round(3), "四阶段指标相关矩阵", global_num="92b",
                   title="四阶段指标相关矩阵", formats=['csv', 'json'])

        # 绘制相关热力图（图27）
        fig_corr = plot_correlation_heatmap(corr_matrix, p_matrix, paths)
        save_figure(fig_corr, "四阶段指标相关矩阵热力图", global_num=27,
                    title="四阶段指标相关矩阵")

    # 5. 绘制图26
    print("\n" + "-" * 40)
    print("5. 绘制图26: 四阶段指标分布图")
    print("-" * 40)
    fig = plot_stage_distributions(sem_df, paths)
    save_figure(fig, "四阶段指标分布图", global_num=26,
                title="四阶段认知编码指标分布图")

    # 6. 阶段间关系分析
    print("\n" + "-" * 40)
    print("6. 阶段间关系分析")
    print("-" * 40)
    analyze_stage_relationships(sem_df)


    # 7. KMO与Bartlett检验
    print("\n" + "-" * 40)
    print("7. KMO与Bartlett检验")
    print("-" * 40)
    calculate_kmo_bartlett(sem_df)

    print("\n" + "=" * 60)
    print("Q3_01_描述统计 完成")
    print("=" * 60)

    return sem_df, desc_stats, corr_matrix


if __name__ == "__main__":
    sem_df, desc_stats, corr_matrix = main()
