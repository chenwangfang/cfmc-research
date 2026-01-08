#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_03_12类构式分类.py
=====================
理论驱动的12类构式分类（H1-2）

假设H1-2: 双维度分类体系可识别出12类构式类型
分类方法: 3级认知通达度 x 4类映射方向 = 12类构式（理论驱动）

12类构式命名规则：
- 认知通达度：高(H)/中(M)/低(L)
- 映射方向：具->具(CC)/具->抽(CA)/抽->抽(AA)/抽->具(AC)
- 格式：{通达度}_{映射方向}，如"高_具抽"表示高通达+具体->抽象

输出：
- 图15: 理论12类构式分布验证图
- 图16: 12类构式二维分布图
- 表61: 12类构式理论分组与GMM验证对比
- 表62: 12类构式聚类中心参数
- 表63: 分类稳定性检验汇总（Bootstrap）

验证标准：
- 理论12类均有样本覆盖
- GMM验证轮廓系数 >= 0.30

创建日期：2025-12-05
修改日期：2025-12-06（改为理论驱动的3x4交叉分组）
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
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, CONSTRUCTION_COLORS,
    MAPPING_DIRECTION_CODES, bin_accessibility, bin_complexity,
    COGNITIVE_ACCESSIBILITY_LEVELS, MAPPING_DIRECTION_SHORT
)


def prepare_classification_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    准备理论驱动的12类构式分类数据

    Parameters
    ----------
    df : pd.DataFrame
        构式数据

    Returns
    -------
    pd.DataFrame
        包含12类构式标签的数据框
    """
    # 必需字段
    required_fields = ['cognitive_accessibility', 'mapping_direction']

    # 检查字段存在性
    for field in required_fields:
        if field not in df.columns:
            raise ValueError(f"缺少必需字段: {field}")

    # 移除缺失值
    df_valid = df.dropna(subset=required_fields).copy()
    print(f"有效样本: {len(df_valid)} / {len(df)} ({len(df_valid)/len(df)*100:.1f}%)")

    # 1. 认知通达度归并（5->3级）
    df_valid['ca_level'] = df_valid['cognitive_accessibility'].apply(bin_accessibility)

    # 2. 映射方向标签
    df_valid['md_label'] = df_valid['mapping_direction'].map(MAPPING_DIRECTION_SHORT)

    # 3. 生成12类构式标签
    df_valid['construction_type_12'] = df_valid['ca_level'] + '_' + df_valid['md_label']

    # 4. 生成数值编码（用于统计分析）
    # 认知通达度编码: 低=1, 中=2, 高=3
    ca_code_map = {'低': 1, '中': 2, '高': 3}
    df_valid['ca_code'] = df_valid['ca_level'].map(ca_code_map)

    # 映射方向编码: 1-4
    df_valid['md_code'] = df_valid['mapping_direction'].astype(int)

    # 12类编码: (ca_code - 1) * 4 + md_code，范围1-12
    df_valid['type_code'] = (df_valid['ca_code'] - 1) * 4 + df_valid['md_code']

    print(f"\n理论12类构式分类完成:")
    print(f"  分类维度1: 认知通达度（3级）")
    print(f"  分类维度2: 映射方向（4类）")
    print(f"  理论类型数: 3 x 4 = 12类")

    return df_valid


def prepare_gmm_validation_data(df: pd.DataFrame) -> tuple:
    """
    准备GMM验证数据（用于验证理论分类的统计有效性）

    Parameters
    ----------
    df : pd.DataFrame
        包含分类标签的构式数据

    Returns
    -------
    tuple
        (标准化特征矩阵, 特征名列表, 有效索引, 原始特征)
    """
    # 使用认知通达度和映射方向进行GMM验证（与理论分类维度一致）
    features = ['cognitive_accessibility', 'mapping_direction']

    # 移除缺失值
    df_valid = df[features].dropna()
    valid_idx = df_valid.index

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_valid)

    print(f"\nGMM验证数据准备完成:")
    print(f"  有效样本: {len(valid_idx)}")
    print(f"  特征变量: {features}")

    return X_scaled, features, valid_idx, df_valid.values


def find_optimal_k(X: np.ndarray, k_range: tuple = (8, 16)) -> dict:
    """
    使用BIC/AIC寻找最优k值

    Parameters
    ----------
    X : np.ndarray
        标准化特征矩阵
    k_range : tuple
        k值搜索范围

    Returns
    -------
    dict
        包含各k值评估指标的字典
    """
    k_values = list(range(k_range[0], k_range[1] + 1))

    results = {
        'k': k_values,
        'bic': [],
        'aic': [],
        'silhouette': [],
        'calinski_harabasz': [],
        'davies_bouldin': []
    }

    print(f"\n评估k={k_range[0]}至k={k_range[1]}的聚类效果...")

    for k in k_values:
        gmm = GaussianMixture(n_components=k, covariance_type='full',
                              n_init=10, random_state=42, max_iter=500)
        gmm.fit(X)
        labels = gmm.predict(X)

        results['bic'].append(gmm.bic(X))
        results['aic'].append(gmm.aic(X))
        results['silhouette'].append(silhouette_score(X, labels))
        results['calinski_harabasz'].append(calinski_harabasz_score(X, labels))
        results['davies_bouldin'].append(davies_bouldin_score(X, labels))

        print(f"  k={k}: BIC={gmm.bic(X):.1f}, Silhouette={silhouette_score(X, labels):.3f}")

    return results


def fit_gmm_12(X: np.ndarray, random_state: int = 42) -> tuple:
    """
    拟合12类GMM模型

    Parameters
    ----------
    X : np.ndarray
        标准化特征矩阵
    random_state : int
        随机种子

    Returns
    -------
    tuple
        (GMM模型, 聚类标签, 聚类概率)
    """
    gmm = GaussianMixture(n_components=12, covariance_type='full',
                          n_init=20, random_state=random_state, max_iter=500)
    gmm.fit(X)
    labels = gmm.predict(X)
    probs = gmm.predict_proba(X)

    print(f"\n12类GMM模型拟合完成:")
    print(f"  BIC: {gmm.bic(X):.2f}")
    print(f"  AIC: {gmm.aic(X):.2f}")
    print(f"  轮廓系数: {silhouette_score(X, labels):.4f}")
    print(f"  收敛: {'是' if gmm.converged_ else '否'}")
    print(f"  迭代次数: {gmm.n_iter_}")

    return gmm, labels, probs


def bootstrap_stability(X: np.ndarray, n_bootstrap: int = 100) -> dict:
    """
    Bootstrap稳定性检验

    Parameters
    ----------
    X : np.ndarray
        标准化特征矩阵
    n_bootstrap : int
        Bootstrap次数

    Returns
    -------
    dict
        稳定性检验结果
    """
    print(f"\n进行Bootstrap稳定性检验（n={n_bootstrap}）...")

    silhouettes = []
    n_samples = len(X)

    for i in range(n_bootstrap):
        # Bootstrap抽样
        idx = np.random.choice(n_samples, size=n_samples, replace=True)
        X_boot = X[idx]

        # 拟合GMM
        gmm = GaussianMixture(n_components=12, covariance_type='full',
                              n_init=5, random_state=i, max_iter=300)
        gmm.fit(X_boot)
        labels = gmm.predict(X_boot)

        try:
            sil = silhouette_score(X_boot, labels)
            silhouettes.append(sil)
        except:
            continue

        if (i + 1) % 20 == 0:
            print(f"  完成 {i + 1}/{n_bootstrap} 次...")

    results = {
        'n_bootstrap': n_bootstrap,
        'mean_silhouette': np.mean(silhouettes),
        'std_silhouette': np.std(silhouettes),
        'ci_lower': np.percentile(silhouettes, 2.5),
        'ci_upper': np.percentile(silhouettes, 97.5),
        'min_silhouette': np.min(silhouettes),
        'max_silhouette': np.max(silhouettes)
    }

    print(f"  Bootstrap轮廓系数: {results['mean_silhouette']:.4f} ± {results['std_silhouette']:.4f}")
    print(f"  95% CI: [{results['ci_lower']:.4f}, {results['ci_upper']:.4f}]")

    return results


def analyze_12_types_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    分析12类构式的分布情况（表62）

    Parameters
    ----------
    df : pd.DataFrame
        包含12类构式标签的数据框

    Returns
    -------
    pd.DataFrame
        12类构式分布统计表
    """
    # 按理论顺序排列12类
    type_order = []
    for ca in ['低', '中', '高']:
        for md in ['具具', '具抽', '抽抽', '抽具']:
            type_order.append(f"{ca}_{md}")

    table_data = []
    total_n = len(df)

    for i, type_name in enumerate(type_order, 1):
        mask = df['construction_type_12'] == type_name
        subset = df[mask]
        n_samples = len(subset)

        if n_samples > 0:
            # 解析类型名称
            ca_level, md_label = type_name.split('_')

            # 计算该类型的统计量
            ca_mean = subset['cognitive_accessibility'].mean()
            ca_std = subset['cognitive_accessibility'].std()
            cc_mean = subset['conceptual_complexity'].mean() if 'conceptual_complexity' in subset.columns else np.nan
            cc_std = subset['conceptual_complexity'].std() if 'conceptual_complexity' in subset.columns else np.nan

            table_data.append({
                '类型编号': i,
                '类型名称': type_name,
                '认知通达度': ca_level,
                '映射方向': md_label,
                '样本量': n_samples,
                '占比(%)': round(n_samples / total_n * 100, 2),
                '认知通达度M': round(ca_mean, 3),
                '认知通达度SD': round(ca_std, 3) if not np.isnan(ca_std) else 0,
                '概念复杂度M': round(cc_mean, 3) if not np.isnan(cc_mean) else np.nan,
                '概念复杂度SD': round(cc_std, 3) if not np.isnan(cc_std) else np.nan
            })
        else:
            # 类型无样本
            ca_level, md_label = type_name.split('_')
            table_data.append({
                '类型编号': i,
                '类型名称': type_name,
                '认知通达度': ca_level,
                '映射方向': md_label,
                '样本量': 0,
                '占比(%)': 0.0,
                '认知通达度M': np.nan,
                '认知通达度SD': np.nan,
                '概念复杂度M': np.nan,
                '概念复杂度SD': np.nan
            })

    result_df = pd.DataFrame(table_data)

    # 打印分布概况
    print(f"\n12类构式分布概况:")
    non_empty = result_df[result_df['样本量'] > 0]
    print(f"  有样本类型数: {len(non_empty)} / 12")
    print(f"  最大类型: {result_df.loc[result_df['样本量'].idxmax(), '类型名称']} (n={result_df['样本量'].max()})")
    print(f"  最小类型: {non_empty.loc[non_empty['样本量'].idxmin(), '类型名称']} (n={non_empty['样本量'].min()})")

    return result_df


def create_gmm_comparison_table(df_theory: pd.DataFrame, gmm_labels: np.ndarray,
                                  valid_idx: pd.Index) -> pd.DataFrame:
    """
    创建理论分组与GMM验证对比表（表61）

    Parameters
    ----------
    df_theory : pd.DataFrame
        理论分类结果
    gmm_labels : np.ndarray
        GMM聚类标签
    valid_idx : pd.Index
        有效样本索引

    Returns
    -------
    pd.DataFrame
        对比结果表
    """
    # 合并理论标签和GMM标签
    df_compare = df_theory.loc[valid_idx].copy()
    df_compare['gmm_cluster'] = gmm_labels

    # 计算每个理论类型对应的GMM簇分布
    comparison_data = []

    for type_name in df_compare['construction_type_12'].unique():
        mask = df_compare['construction_type_12'] == type_name
        gmm_clusters = df_compare.loc[mask, 'gmm_cluster'].value_counts()
        dominant_cluster = gmm_clusters.index[0] if len(gmm_clusters) > 0 else -1
        purity = gmm_clusters.iloc[0] / mask.sum() if len(gmm_clusters) > 0 else 0

        comparison_data.append({
            '理论类型': type_name,
            '样本量': mask.sum(),
            '主导GMM簇': dominant_cluster + 1,
            '纯度': round(purity, 3),
            'GMM簇分布': dict(gmm_clusters)
        })

    result_df = pd.DataFrame(comparison_data)
    result_df = result_df.sort_values('样本量', ascending=False).reset_index(drop=True)

    # 计算整体一致性
    avg_purity = result_df['纯度'].mean()
    print(f"\n理论分组与GMM验证对比:")
    print(f"  平均纯度: {avg_purity:.3f}")

    return result_df


def plot_bic_curve(k_results: dict, paths: dict) -> plt.Figure:
    """
    绘制k值选择BIC曲线图（图15）

    Parameters
    ----------
    k_results : dict
        k值评估结果
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

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 左图：BIC/AIC曲线
    ax1 = axes[0]
    ax1.plot(k_results['k'], k_results['bic'], 'bo-', label='BIC', linewidth=2, markersize=8)
    ax1.plot(k_results['k'], k_results['aic'], 'rs--', label='AIC', linewidth=2, markersize=8)

    # 标记k=12
    k12_idx = k_results['k'].index(12)
    ax1.axvline(x=12, color='green', linestyle=':', linewidth=2, alpha=0.7)
    ax1.scatter([12], [k_results['bic'][k12_idx]], s=200, c='green', marker='*', zorder=5)

    ax1.set_xlabel('聚类数k', fontproperties=font_cn, fontsize=12)
    ax1.set_ylabel('信息准则值', fontproperties=font_cn, fontsize=12)
    ax1.set_title('(a) BIC/AIC曲线', fontproperties=font_cn_title, fontsize=13)
    ax1.legend(prop=font_cn)
    ax1.grid(alpha=0.3)
    ax1.set_xticks(k_results['k'])

    # 右图：轮廓系数曲线
    ax2 = axes[1]
    ax2.plot(k_results['k'], k_results['silhouette'], 'go-', linewidth=2, markersize=8)

    # 标记阈值线
    ax2.axhline(y=0.30, color='red', linestyle='--', linewidth=2, label='阈值 (0.30)')

    # 标记k=12
    ax2.axvline(x=12, color='green', linestyle=':', linewidth=2, alpha=0.7)
    ax2.scatter([12], [k_results['silhouette'][k12_idx]], s=200, c='green', marker='*', zorder=5)

    ax2.set_xlabel('聚类数k', fontproperties=font_cn, fontsize=12)
    ax2.set_ylabel('轮廓系数', fontproperties=font_cn, fontsize=12)
    ax2.set_title('(b) 轮廓系数曲线', fontproperties=font_cn_title, fontsize=13)
    ax2.legend(prop=font_cn)
    ax2.grid(alpha=0.3)
    ax2.set_xticks(k_results['k'])

    # 添加k=12标注
    ax2.annotate(f'k=12: {k_results["silhouette"][k12_idx]:.3f}',
                xy=(12, k_results['silhouette'][k12_idx]),
                xytext=(13, k_results['silhouette'][k12_idx] + 0.02),
                fontsize=10, fontproperties=font_en,
                arrowprops=dict(arrowstyle='->', color='gray'))

    # plt.suptitle('图15 k值选择BIC曲线图（k=8至k=16）',
                # fontproperties=font_cn_title, fontsize=14, y=1.02)
    plt.tight_layout()

    return fig


def plot_12_types_distribution(df: pd.DataFrame, paths: dict) -> plt.Figure:
    """
    绘制12类构式二维分布气泡图（图16）

    Parameters
    ----------
    df : pd.DataFrame
        包含12类构式标签的数据框
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

    fig, ax = plt.subplots(figsize=(10, 7))

    # 按认知通达度分配颜色（3种主色系）
    ca_colors = {
        '低': '#3498db',  # 蓝色系
        '中': '#27ae60',  # 绿色系
        '高': '#e74c3c'   # 红色系
    }

    # 映射方向对应的Y坐标
    md_y = {'具具': 1, '具抽': 2, '抽抽': 3, '抽具': 4}

    # 认知通达度对应的X坐标（中心位置）
    ca_x = {'低': 1.5, '中': 3.0, '高': 4.5}

    # 添加背景色块区分三个认知通达度区域
    ax.axvspan(0.5, 2.5, alpha=0.08, color='#3498db', zorder=0)
    ax.axvspan(2.5, 3.5, alpha=0.08, color='#27ae60', zorder=0)
    ax.axvspan(3.5, 5.5, alpha=0.08, color='#e74c3c', zorder=0)

    # 收集每个类型的数据
    bubble_data = []
    for ca in ['低', '中', '高']:
        for md in ['具具', '具抽', '抽抽', '抽具']:
            type_name = f"{ca}_{md}"
            mask = df['construction_type_12'] == type_name
            n = mask.sum()
            if n > 0:
                bubble_data.append({
                    'type': type_name,
                    'ca': ca,
                    'md': md,
                    'x': ca_x[ca],
                    'y': md_y[md],
                    'n': n,
                    'color': ca_colors[ca]
                })

    # 计算气泡大小（对数缩放，避免差异过大）
    max_n = max(d['n'] for d in bubble_data)
    min_size, max_size = 200, 2000  # 气泡大小范围

    for d in bubble_data:
        # 对数缩放
        d['size'] = min_size + (max_size - min_size) * (np.log1p(d['n']) / np.log1p(max_n))

    # 绘制气泡（透明度降低便于阅读）
    for d in bubble_data:
        ax.scatter(d['x'], d['y'], s=d['size'], c=d['color'],
                  alpha=0.4, edgecolors='white', linewidths=2, zorder=5)

    # 添加标签（类型名称和样本量）
    for d in bubble_data:
        # 根据位置调整标签偏移，避免重叠
        if d['ca'] == '低':
            # 低通达：标签在气泡左侧上方
            x_offset, ha = -0.35, 'right'
            y_offset = 0.15
            va = 'bottom'
        elif d['ca'] == '高':
            # 高通达：标签在气泡右侧偏下（避免与右上角图例重叠）
            x_offset, ha = 0.45, 'left'
            y_offset = -0.08
            va = 'center'
        else:
            # 中通达：标签上移更多，避免与气泡重叠
            x_offset, ha = 0, 'center'
            y_offset = 0.28
            va = 'bottom'

        # 类型名称（气泡内或旁边）
        ax.text(d['x'] + x_offset, d['y'] + y_offset,
               d['type'], fontproperties=font_cn, fontsize=10,
               ha=ha, va=va, fontweight='bold', color=d['color'])

        # 样本量（气泡内）- 使用深色便于阅读
        ax.text(d['x'], d['y'], f"n={d['n']}",
               fontproperties=font_en, fontsize=9,
               ha='center', va='center', color='#333333', fontweight='bold')

    # 设置坐标轴
    ax.set_xlabel('认知通达度', fontproperties=font_cn, fontsize=12)
    ax.set_ylabel('映射方向', fontproperties=font_cn, fontsize=12)
    # ax.set_title('图16 12类构式二维分布图',
                # fontproperties=font_cn_title, fontsize=14, pad=15)

    # 添加认知通达度区域标签（顶部）
    ax.text(1.5, 4.6, '低通达', fontproperties=font_cn, fontsize=11,
           ha='center', color='#3498db', fontweight='bold')
    ax.text(3.0, 4.6, '中通达', fontproperties=font_cn, fontsize=11,
           ha='center', color='#27ae60', fontweight='bold')
    ax.text(4.5, 4.6, '高通达', fontproperties=font_cn, fontsize=11,
           ha='center', color='#e74c3c', fontweight='bold')

    # 添加分隔线
    ax.axvline(x=2.5, color='gray', linestyle='--', alpha=0.4, zorder=1)
    ax.axvline(x=3.5, color='gray', linestyle='--', alpha=0.4, zorder=1)

    # 设置坐标轴范围和刻度
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 4.8)
    ax.set_xticks([1.5, 3.0, 4.5])
    ax.set_xticklabels(['1-2级\n(低)', '3级\n(中)', '4-5级\n(高)'],
                       fontproperties=font_cn, fontsize=10)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(['具体→具体', '具体→抽象', '抽象→抽象', '抽象→具体'],
                       fontproperties=font_cn, fontsize=10)

    # 添加图例说明气泡大小（缩小图例气泡）
    legend_sizes = [30, 150, 400]
    legend_labels = ['<100', '100-500', '>500']
    for i, (size, label) in enumerate(zip(legend_sizes, legend_labels)):
        ax.scatter([], [], s=size, c='gray', alpha=0.5,
                  label=label, edgecolors='white')
    ax.legend(loc='upper right', prop=font_cn, fontsize=9,
             title='样本量', title_fontproperties=font_cn, framealpha=0.9)

    ax.grid(alpha=0.2, zorder=0)
    plt.tight_layout()

    return fig


def plot_theory_validation(df: pd.DataFrame, type_stats: pd.DataFrame,
                            paths: dict) -> plt.Figure:
    """
    绘制理论12类构式分布验证图（图15）

    Parameters
    ----------
    df : pd.DataFrame
        包含12类构式标签的数据框
    type_stats : pd.DataFrame
        12类构式统计表
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

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 左图：12类构式频率分布条形图
    ax1 = axes[0]
    type_order = type_stats.sort_values('样本量', ascending=True)
    colors = [CONSTRUCTION_COLORS[i % len(CONSTRUCTION_COLORS)]
              for i in range(len(type_order))]

    bars = ax1.barh(range(len(type_order)), type_order['样本量'], color=colors)
    ax1.set_yticks(range(len(type_order)))
    ax1.set_yticklabels(type_order['类型名称'], fontproperties=font_cn)
    ax1.set_xlabel('样本量', fontproperties=font_cn, fontsize=12)
    ax1.set_title('（a）12类构式频率分布', fontproperties=font_cn_title, fontsize=13)

    # 添加数值标签
    for bar, val in zip(bars, type_order['样本量']):
        ax1.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                f'{val}', va='center', fontsize=9)

    # 右图：3x4交叉表热力图
    ax2 = axes[1]

    # 创建3x4矩阵
    ca_levels = ['低', '中', '高']
    md_levels = ['具具', '具抽', '抽抽', '抽具']
    matrix = np.zeros((3, 4))

    for i, ca in enumerate(ca_levels):
        for j, md in enumerate(md_levels):
            type_name = f"{ca}_{md}"
            row = type_stats[type_stats['类型名称'] == type_name]
            if len(row) > 0:
                matrix[i, j] = row['样本量'].values[0]

    im = ax2.imshow(matrix, cmap='YlOrRd', aspect='auto')
    ax2.set_xticks(range(4))
    ax2.set_xticklabels(md_levels, fontproperties=font_cn)
    ax2.set_yticks(range(3))
    ax2.set_yticklabels(ca_levels, fontproperties=font_cn)
    ax2.set_xlabel('映射方向', fontproperties=font_cn, fontsize=12)
    ax2.set_ylabel('认知通达度', fontproperties=font_cn, fontsize=12)
    ax2.set_title('（b）3×4交叉分布热力图', fontproperties=font_cn_title, fontsize=13)

    # 添加数值标签
    for i in range(3):
        for j in range(4):
            ax2.text(j, i, f'{int(matrix[i, j])}',
                    ha='center', va='center', fontsize=11,
                    color='white' if matrix[i, j] > matrix.max()/2 else 'black')

    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax2)
    cbar.set_label('样本量', fontproperties=font_cn)

    # plt.suptitle('图15 理论12类构式分布验证图',
                # fontproperties=font_cn_title, fontsize=14, y=1.02)
    plt.tight_layout()

    return fig


def main():
    """主函数"""
    print("=" * 60)
    print("Q1_03_12类构式分类.py")
    print("理论驱动的12类构式分类（3x4交叉分组）")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 加载数据
    df, meta = load_cfmc_data()
    print(f"数据量: {len(df)} 条")

    # 1. 理论驱动的12类构式分类
    print("\n" + "-" * 40)
    print("1. 理论驱动的12类构式分类")
    print("-" * 40)
    df_classified = prepare_classification_data(df)

    # 2. 分析12类构式分布（表62）
    print("\n" + "-" * 40)
    print("2. 12类构式分布分析")
    print("-" * 40)
    type_stats = analyze_12_types_distribution(df_classified)
    print("\n" + type_stats.to_string(index=False))

    save_table(type_stats, "12类构式聚类中心参数", global_num=62,
               title="12类构式聚类中心参数", formats=['csv', 'json'])

    # 验证H1-2：理论12类是否均有样本覆盖
    n_types_with_data = (type_stats['样本量'] > 0).sum()
    print(f"\nH1-2验证（理论覆盖性）:")
    print(f"  标准: 12类均有样本覆盖")
    print(f"  实际: {n_types_with_data}/12类有样本")
    print(f"  结论: {'[OK] 支持' if n_types_with_data == 12 else '部分支持'}")

    # 3. GMM验证（作为统计验证）
    print("\n" + "-" * 40)
    print("3. GMM统计验证")
    print("-" * 40)
    X, features, valid_idx, X_raw = prepare_gmm_validation_data(df_classified)

    # 拟合12类GMM
    gmm, labels, probs = fit_gmm_12(X)

    # 验证轮廓系数
    sil_score = silhouette_score(X, labels)
    print(f"\nGMM验证结果:")
    print(f"  轮廓系数: {sil_score:.4f}")
    print(f"  标准: >= 0.30")
    print(f"  结论: {'[OK] 达标' if sil_score >= 0.30 else '[X] 未达标'}")

    # 4. 理论分组与GMM验证对比（表61）
    print("\n" + "-" * 40)
    print("4. 理论分组与GMM验证对比")
    print("-" * 40)
    comparison_table = create_gmm_comparison_table(df_classified, labels, valid_idx)

    save_table(comparison_table, "12类构式理论分组与GMM验证对比", global_num=61,
               title="12类构式理论分组与GMM验证对比", formats=['csv', 'json'])

    # 5. Bootstrap稳定性检验
    print("\n" + "-" * 40)
    print("5. Bootstrap稳定性检验")
    print("-" * 40)
    bootstrap_results = bootstrap_stability(X, n_bootstrap=100)

    bootstrap_table = pd.DataFrame([{
        '检验项目': 'Bootstrap轮廓系数',
        'Bootstrap次数': bootstrap_results['n_bootstrap'],
        '均值': round(bootstrap_results['mean_silhouette'], 4),
        '标准差': round(bootstrap_results['std_silhouette'], 4),
        '95% CI下限': round(bootstrap_results['ci_lower'], 4),
        '95% CI上限': round(bootstrap_results['ci_upper'], 4),
        '稳定性': '良好' if bootstrap_results['ci_lower'] >= 0.25 else '一般'
    }])
    save_table(bootstrap_table, "分类稳定性检验汇总", global_num=63,
               title="分类稳定性检验汇总（Bootstrap）", formats=['csv', 'json'])

    # 6. 绘制图15：理论12类构式分布验证图
    print("\n" + "-" * 40)
    print("6. 绘制图15: 理论12类构式分布验证图")
    print("-" * 40)
    fig4 = plot_theory_validation(df_classified, type_stats, paths)
    save_figure(fig4, "理论12类构式分布验证图", global_num=15,
                title="理论12类构式分布验证图")

    # 7. 绘制图16：12类构式二维分布图
    print("\n" + "-" * 40)
    print("7. 绘制图16: 12类构式二维分布图")
    print("-" * 40)
    fig5 = plot_12_types_distribution(df_classified, paths)
    save_figure(fig5, "12类构式二维分布图", global_num=16,
                title="12类构式二维分布图")

    # 8. 保存分类结果数据
    # 保存带分类标签的数据供后续脚本使用
    output_path = paths['output_data'] / 'CFMC_with_12types.csv'
    df_classified.to_csv(output_path, index=True, encoding='utf-8-sig')
    print(f"\n[OK] 已保存带12类构式标签的数据: {output_path}")

    # 同时保存GMM标签用于对比分析
    df_with_gmm = df_classified.loc[valid_idx].copy()
    df_with_gmm['gmm_cluster'] = labels
    df_with_gmm['gmm_prob_max'] = probs.max(axis=1)
    # 添加cluster_label字段供后续脚本使用（基于理论12类分类，标签范围0-11）
    df_with_gmm['cluster_label'] = df_with_gmm['type_code'] - 1
    output_path_gmm = paths['output_data'] / 'CFMC_with_clusters.csv'
    df_with_gmm.to_csv(output_path_gmm, index=True, encoding='utf-8-sig')
    print(f"[OK] 已保存带GMM聚类标签的数据: {output_path_gmm}")

    print("\n" + "=" * 60)
    print("Q1_03_12类构式分类 完成")
    print("=" * 60)

    # 打印最终验证结果汇总
    print("\n【H1-2验证结果汇总】")
    print(f"  1. 理论覆盖性: {n_types_with_data}/12类有样本 -> {'[OK] 支持' if n_types_with_data == 12 else '部分支持'}")
    print(f"  2. GMM验证轮廓系数: {sil_score:.4f} -> {'[OK] 达标' if sil_score >= 0.30 else '[X] 未达标'}")
    print(f"  3. Bootstrap稳定性: {bootstrap_results['mean_silhouette']:.4f} ± {bootstrap_results['std_silhouette']:.4f}")

    return df_classified, type_stats, gmm, labels


if __name__ == "__main__":
    df_classified, type_stats, gmm, labels = main()
