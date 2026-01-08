#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_04_LDA判别.py
================
线性判别分析验证聚类结果

输出：
- 图17: LDA判别函数二维投影图（LD1xLD2）
- 图18: 12类构式LDA分类混淆矩阵热力图
- 表64: LDA判别分析结果
- 表65: 各类型LDA分类准确率

验证标准：10折交叉验证准确率 >= 85%

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
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import cross_val_score, cross_val_predict, StratifiedKFold
from sklearn.metrics import (classification_report, confusion_matrix,
                            accuracy_score, precision_recall_fscore_support)
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, load_cfmc_data, get_font_paths,
    save_figure, save_table, CONSTRUCTION_COLORS
)


def load_clustered_data(paths: dict) -> tuple:
    """
    加载带聚类标签的数据

    Parameters
    ----------
    paths : dict
        路径字典

    Returns
    -------
    tuple
        (数据框, 特征矩阵, 标签)
    """
    # 尝试加载聚类结果
    cluster_file = paths['output_data'] / 'CFMC_with_clusters.csv'

    if cluster_file.exists():
        df = pd.read_csv(cluster_file, index_col=0)
        print(f"[OK] 已加载聚类结果: {cluster_file}")
    else:
        # 如果没有聚类结果，运行聚类
        print("[WARN] 未找到聚类结果，正在运行GMM聚类...")
        from Q1_03_GMM聚类 import main as run_clustering
        _, labels, _, _ = run_clustering()
        df = pd.read_csv(cluster_file, index_col=0)

    # 准备特征（与Q1_03分类维度一致：认知通达度x映射方向）
    features = ['cognitive_accessibility', 'mapping_direction']
    X = df[features].values
    y = df['cluster_label'].values

    return df, X, y, features


def perform_lda(X: np.ndarray, y: np.ndarray) -> tuple:
    """
    执行LDA判别分析

    Parameters
    ----------
    X : np.ndarray
        特征矩阵
    y : np.ndarray
        类别标签

    Returns
    -------
    tuple
        (LDA模型, 变换后数据, 10折CV准确率)
    """
    # 拟合LDA
    n_classes = len(np.unique(y))
    n_components = min(n_classes - 1, X.shape[1])

    lda = LinearDiscriminantAnalysis(n_components=n_components)
    X_lda = lda.fit_transform(X, y)

    # 10折交叉验证
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    cv_scores = cross_val_score(lda, X, y, cv=cv, scoring='accuracy')

    print(f"\nLDA判别分析结果:")
    print(f"  判别函数数: {n_components}")
    print(f"  解释方差比: {lda.explained_variance_ratio_}")
    print(f"  10折CV准确率: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"  CV准确率范围: [{cv_scores.min():.4f}, {cv_scores.max():.4f}]")

    return lda, X_lda, cv_scores


def create_classification_report(X: np.ndarray, y: np.ndarray, lda) -> tuple:
    """
    创建分类报告

    Parameters
    ----------
    X : np.ndarray
        特征矩阵
    y : np.ndarray
        真实标签
    lda : LinearDiscriminantAnalysis
        LDA模型

    Returns
    -------
    tuple
        (混淆矩阵, 分类报告DataFrame)
    """
    # 10折交叉验证预测
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    y_pred = cross_val_predict(lda, X, y, cv=cv)

    # 混淆矩阵
    cm = confusion_matrix(y, y_pred)

    # 各类别指标
    precision, recall, f1, support = precision_recall_fscore_support(y, y_pred)

    report_data = []
    for i in range(len(np.unique(y))):
        report_data.append({
            '类型': f'T{i+1}',
            '样本量': int(support[i]),
            '精确率': round(precision[i], 4),
            '召回率': round(recall[i], 4),
            'F1分数': round(f1[i], 4),
            '正确分类数': cm[i, i],
            '分类准确率(%)': round(cm[i, i] / support[i] * 100, 2)
        })

    report_df = pd.DataFrame(report_data)

    # 添加整体指标
    overall = {
        '类型': '整体',
        '样本量': int(support.sum()),
        '精确率': round(precision.mean(), 4),
        '召回率': round(recall.mean(), 4),
        'F1分数': round(f1.mean(), 4),
        '正确分类数': cm.diagonal().sum(),
        '分类准确率(%)': round(accuracy_score(y, y_pred) * 100, 2)
    }
    report_df = pd.concat([report_df, pd.DataFrame([overall])], ignore_index=True)

    return cm, report_df


def create_lda_summary_table(lda, cv_scores: np.ndarray, X: np.ndarray, y: np.ndarray) -> pd.DataFrame:
    """
    创建LDA判别分析结果汇总表（表64）

    Parameters
    ----------
    lda : LinearDiscriminantAnalysis
        LDA模型
    cv_scores : np.ndarray
        交叉验证分数
    X : np.ndarray
        特征矩阵
    y : np.ndarray
        标签

    Returns
    -------
    pd.DataFrame
        汇总表
    """
    table_data = [
        {'指标': '样本量', '值': len(y)},
        {'指标': '类别数', '值': len(np.unique(y))},
        {'指标': '特征数', '值': X.shape[1]},
        {'指标': '判别函数数', '值': lda.n_components if hasattr(lda, 'n_components') else 'N/A'},
        {'指标': 'LD1解释方差比', '值': f"{lda.explained_variance_ratio_[0]:.4f}" if len(lda.explained_variance_ratio_) > 0 else 'N/A'},
        {'指标': '10折CV准确率', '值': f"{cv_scores.mean():.4f}"},
        {'指标': 'CV标准差', '值': f"{cv_scores.std():.4f}"},
        {'指标': 'CV最小值', '值': f"{cv_scores.min():.4f}"},
        {'指标': 'CV最大值', '值': f"{cv_scores.max():.4f}"},
        {'指标': '验证标准', '值': '>= 85%'},
        {'指标': '是否达标', '值': '是' if cv_scores.mean() >= 0.85 else '否'}
    ]

    return pd.DataFrame(table_data)


def plot_lda_projection(X_lda: np.ndarray, y: np.ndarray, paths: dict) -> plt.Figure:
    """
    绘制LDA判别函数二维投影图（图17）

    Parameters
    ----------
    X_lda : np.ndarray
        LDA变换后的数据
    y : np.ndarray
        类别标签
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

    fig, ax = plt.subplots(figsize=(12, 9))

    # 12类构式语义化名称映射（按聚类标签顺序）
    TYPE_NAMES = {
        0: '低_具具', 1: '低_具抽', 2: '低_抽抽', 3: '低_抽具',
        4: '中_具具', 5: '中_具抽', 6: '中_抽抽', 7: '中_抽具',
        8: '高_具具', 9: '高_具抽', 10: '高_抽抽', 11: '高_抽具'
    }

    # 按认知通达度分配颜色
    TYPE_COLORS = {
        0: '#3498db', 1: '#2980b9', 2: '#1f618d', 3: '#154360',  # 低通达：蓝色系
        4: '#27ae60', 5: '#229954', 6: '#1e8449', 7: '#196f3d',  # 中通达：绿色系
        8: '#e74c3c', 9: '#cb4335', 10: '#b03a2e', 11: '#943126'  # 高通达：红色系
    }

    # 如果只有一个判别函数，创建第二个维度（随机抖动）
    if X_lda.shape[1] == 1:
        np.random.seed(42)  # 固定随机种子保证可重复性
        X_plot = np.column_stack([X_lda, np.random.randn(len(X_lda)) * 0.5])
        xlabel = 'LD1'
        ylabel = '随机抖动'
    else:
        X_plot = X_lda[:, :2]
        xlabel = 'LD1'
        ylabel = 'LD2'

    # 绘制各类散点（降低透明度和大小，减少视觉干扰）
    unique_labels = np.unique(y)
    for i, label in enumerate(unique_labels):
        mask = y == label
        color = TYPE_COLORS.get(label, CONSTRUCTION_COLORS[i % len(CONSTRUCTION_COLORS)])
        type_name = TYPE_NAMES.get(label, f'T{label+1}')

        ax.scatter(X_plot[mask, 0], X_plot[mask, 1],
                  c=color, label=f'{type_name} (n={mask.sum()})',
                  alpha=0.25, s=15, edgecolors='none')

    # 计算类中心位置
    centers = {}
    for label in unique_labels:
        mask = y == label
        centers[label] = X_plot[mask].mean(axis=0)

    # 绘制类中心标记（使用对应颜色，更醒目）
    for label in unique_labels:
        center = centers[label]
        color = TYPE_COLORS.get(label, 'black')
        ax.scatter(center[0], center[1], c=color, marker='o', s=200,
                  edgecolors='white', linewidths=2.5, zorder=10)

    # 智能标签位置调整：基于实际类心位置动态分组
    # 按LD1位置排序，分成3组，每组内部错开y方向
    sorted_labels = sorted(unique_labels, key=lambda l: centers[l][0])

    # 为每个标签单独设置偏移量，解决重叠问题
    # 格式: {组内索引: (x_offset, y_offset)}
    label_offsets = {
        # 第一组（LD1最小，高通达红色）：标签放在左侧，y方向交错分布
        (0, 0): (-60, 45),    # 高通达第1个
        (0, 1): (-60, 15),    # 高通达第2个
        (0, 2): (-60, -15),   # 高通达第3个
        (0, 3): (-60, -45),   # 高通达第4个
        # 第二组（LD1中间，中通达绿色）：上下交替分布
        (1, 0): (-50, 55),    # 中通达第1个（上方偏左）
        (1, 1): (20, 35),     # 中通达第2个（上方偏右）
        (1, 2): (-50, -35),   # 中通达第3个（下方偏左）
        (1, 3): (20, -55),    # 中通达第4个（下方偏右）
        # 第三组（LD1最大，低通达蓝色）：标签放在右侧，y方向交错分布
        (2, 0): (20, 50),     # 低通达第1个
        (2, 1): (20, 18),     # 低通达第2个
        (2, 2): (20, -18),    # 低通达第3个
        (2, 3): (20, -50),    # 低通达第4个
    }

    for idx, label in enumerate(sorted_labels):
        center = centers[label]
        color = TYPE_COLORS.get(label, 'black')
        type_name = TYPE_NAMES.get(label, f'T{label+1}')

        # 确定所属组（每4个一组）
        group = idx // 4
        in_group_idx = idx % 4

        # 获取该标签的偏移量
        x_offset, y_offset = label_offsets.get((group, in_group_idx), (-45, 0))

        ax.annotate(type_name, xy=(center[0], center[1]),
                   xytext=(x_offset, y_offset), textcoords='offset points',
                   fontsize=10, fontproperties=font_cn, fontweight='bold',
                   color=color,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            edgecolor=color, alpha=0.9),
                   arrowprops=dict(arrowstyle='-', color=color, alpha=0.6))

    ax.set_xlabel(xlabel, fontproperties=font_cn, fontsize=12)
    ax.set_ylabel(ylabel, fontproperties=font_cn, fontsize=12)

    # 标题根据实际维度调整（避免与ylabel矛盾）
    if X_lda.shape[1] == 1:
        # ax.set_title('图17 LDA判别函数投影图（LD1）',
        #             fontproperties=font_cn_title, fontsize=14, pad=15)
        pass
    else:
        # ax.set_title('图17 LDA判别函数二维投影图（LD1xLD2）',
        #             fontproperties=font_cn_title, fontsize=14, pad=15)
        pass

    # 图例放在右侧，使用语义化名称
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
             prop=font_cn, fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.2)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.4)

    plt.tight_layout()

    return fig


def plot_confusion_matrix(cm: np.ndarray, paths: dict) -> plt.Figure:
    """
    绘制混淆矩阵热力图（图18）

    Parameters
    ----------
    cm : np.ndarray
        混淆矩阵
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
    font_en = fm.FontProperties(fname=font_paths['english'], size=9)

    fig, ax = plt.subplots(figsize=(12, 10))

    # 计算百分比
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    # 热力图
    im = ax.imshow(cm_percent, cmap='Blues', aspect='auto')

    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('分类准确率(%)', fontproperties=font_cn, fontsize=12)

    # 设置标签
    n_classes = len(cm)
    labels = [f'T{i+1}' for i in range(n_classes)]

    ax.set_xticks(np.arange(n_classes))
    ax.set_yticks(np.arange(n_classes))
    ax.set_xticklabels(labels, fontproperties=font_cn, fontsize=10)
    ax.set_yticklabels(labels, fontproperties=font_cn, fontsize=10)

    # 添加数值标注
    for i in range(n_classes):
        for j in range(n_classes):
            value = cm[i, j]
            pct = cm_percent[i, j]
            text_color = 'white' if pct > 50 else 'black'
            ax.text(j, i, f'{value}\n({pct:.1f}%)',
                   ha='center', va='center', color=text_color,
                   fontsize=9, fontproperties=font_en)

    ax.set_xlabel('预测类别', fontproperties=font_cn, fontsize=13)
    ax.set_ylabel('实际类别', fontproperties=font_cn, fontsize=13)
    # ax.set_title('图18 12类构式LDA分类混淆矩阵热力图',
                # fontproperties=font_cn_title, fontsize=14, pad=15)

    plt.tight_layout()

    return fig


def main():
    """主函数"""
    print("=" * 60)
    print("Q1_04_LDA判别.py")
    print("线性判别分析验证聚类结果")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载聚类数据
    print("\n" + "-" * 40)
    print("1. 加载聚类数据")
    print("-" * 40)
    df, X, y, features = load_clustered_data(paths)
    print(f"样本量: {len(y)}")
    print(f"类别数: {len(np.unique(y))}")

    # 2. 执行LDA判别分析
    print("\n" + "-" * 40)
    print("2. 执行LDA判别分析")
    print("-" * 40)
    lda, X_lda, cv_scores = perform_lda(X, y)

    # 验证标准
    print(f"\nH1-2 LDA验证:")
    print(f"  标准: 10折交叉验证准确率 >= 85%")
    print(f"  实际: 准确率 = {cv_scores.mean()*100:.2f}%")
    print(f"  结论: {'[OK] 支持' if cv_scores.mean() >= 0.85 else '[X] 不支持'}")

    # 3. 创建分类报告
    print("\n" + "-" * 40)
    print("3. 创建分类报告")
    print("-" * 40)
    cm, class_report = create_classification_report(X, y, lda)

    print("\n各类型分类准确率:")
    print(class_report.to_string(index=False))

    # 4. 保存表64
    print("\n" + "-" * 40)
    print("4. 保存表64: LDA判别分析结果")
    print("-" * 40)
    lda_summary = create_lda_summary_table(lda, cv_scores, X, y)
    save_table(lda_summary, "LDA判别分析结果", global_num=64,
               title="LDA判别分析结果", formats=['csv', 'json'])

    # 5. 保存表65
    print("\n" + "-" * 40)
    print("5. 保存表65: 各类型LDA分类准确率")
    print("-" * 40)
    save_table(class_report, "各类型LDA分类准确率", global_num=65,
               title="各类型LDA分类准确率", formats=['csv', 'json'])

    # 6. 绘制图17
    print("\n" + "-" * 40)
    print("6. 绘制图17: LDA判别函数二维投影图")
    print("-" * 40)
    fig6 = plot_lda_projection(X_lda, y, paths)
    save_figure(fig6, "LDA判别函数二维投影图", global_num=17,
                title="LDA判别函数二维投影图（LD1xLD2）")

    # 7. 绘制图18
    print("\n" + "-" * 40)
    print("7. 绘制图18: LDA分类混淆矩阵热力图")
    print("-" * 40)
    fig7 = plot_confusion_matrix(cm, paths)
    save_figure(fig7, "LDA分类混淆矩阵热力图", global_num=18,
                title="12类构式LDA分类混淆矩阵热力图")

    print("\n" + "=" * 60)
    print("Q1_04_LDA判别 完成")
    print("=" * 60)

    return lda, cv_scores, cm, class_report


if __name__ == "__main__":
    lda, cv_scores, cm, class_report = main()
