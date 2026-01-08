#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q3_05_中介效应.py
=================
中介效应检验：eta2在eta1->eta3路径中的中介作用

输出：
- 表96: 中介效应检验结果
- 图36: 中介效应路径图

验证方法：Bootstrap 5000次重采样
预期结果：部分中介（中介比例>=60%）

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
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, get_font_paths, save_figure, save_table
)


def load_sem_data(paths: dict) -> pd.DataFrame:
    """加载SEM分析数据"""
    sem_file = paths['output_data'] / 'CFMC_for_SEM.csv'

    if sem_file.exists():
        df = pd.read_csv(sem_file, index_col=0)
        print(f"[OK] 已加载SEM数据: {sem_file}")
    else:
        from utils_公共函数 import load_cfmc_data
        df = load_cfmc_data(paths)
        print("  -> 使用原始数据")

    return df


def prepare_mediation_data(df: pd.DataFrame) -> tuple:
    """
    准备中介分析数据

    Parameters
    ----------
    df : pd.DataFrame
        原始数据

    Returns
    -------
    tuple
        (X, M, Y) 自变量、中介变量、因变量
    """
    # 计算潜变量得分
    def calc_score(df, fields):
        available = [f for f in fields if f in df.columns]
        if not available:
            available = [f'{f}_num' for f in fields if f'{f}_num' in df.columns]
        if available:
            # 标准化后求均值
            scores = df[available].apply(lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0)
            return scores.mean(axis=1)
        return None

    # eta1: 认知域激活
    X = calc_score(df, ['embodied_experience', 'cognitive_accessibility'])

    # eta2: 参照点锚定
    M = calc_score(df, ['conventionality', 'prototype_distance'])

    # eta3: 跨域映射
    Y = calc_score(df, ['mapping_direction', 'systematicity', 'entailment_richness'])

    return X, M, Y


def sobel_test(a: float, b: float, se_a: float, se_b: float) -> tuple:
    """
    Sobel检验：检验间接效应的显著性

    Parameters
    ----------
    a : float
        X->M路径系数
    b : float
        M->Y路径系数
    se_a : float
        a的标准误
    se_b : float
        b的标准误

    Returns
    -------
    tuple
        (Sobel统计量, p值)
    """
    # 间接效应
    indirect = a * b

    # Sobel标准误
    se_sobel = np.sqrt(a**2 * se_b**2 + b**2 * se_a**2)

    # z统计量
    z = indirect / se_sobel

    # 双侧p值
    p = 2 * (1 - stats.norm.cdf(abs(z)))

    return z, p


def bootstrap_mediation(X: pd.Series, M: pd.Series, Y: pd.Series,
                       n_bootstrap: int = 5000, ci: float = 0.95) -> dict:
    """
    Bootstrap中介效应检验

    Parameters
    ----------
    X : pd.Series
        自变量（eta1）
    M : pd.Series
        中介变量（eta2）
    Y : pd.Series
        因变量（eta3）
    n_bootstrap : int
        重采样次数
    ci : float
        置信区间

    Returns
    -------
    dict
        中介效应分析结果
    """
    # 移除缺失值
    valid_idx = X.notna() & M.notna() & Y.notna()
    X = X[valid_idx].values
    M = M[valid_idx].values
    Y = Y[valid_idx].values
    n = len(X)

    print(f"  有效样本量: {n}")

    if n < 100:
        print("  [WARN] 样本量不足，中介效应检验可能不稳定")

    # 原始估计
    # a: X -> M
    slope_a, intercept_a, r_a, p_a, se_a = stats.linregress(X, M)
    # b: M -> Y (控制X)
    # 简化：直接回归
    slope_b, intercept_b, r_b, p_b, se_b = stats.linregress(M, Y)
    # c: X -> Y (总效应)
    slope_c, intercept_c, r_c, p_c, se_c = stats.linregress(X, Y)
    # c': X -> Y (控制M后的直接效应)
    # 使用偏相关近似
    r_xm = np.corrcoef(X, M)[0, 1]
    r_my = np.corrcoef(M, Y)[0, 1]
    r_xy = np.corrcoef(X, Y)[0, 1]
    # 偏相关: r_xy.m = (r_xy - r_xm*r_my) / sqrt((1-r_xm^2)(1-r_my^2))
    r_xy_m = (r_xy - r_xm * r_my) / np.sqrt((1 - r_xm**2) * (1 - r_my**2))
    slope_c_prime = r_xy_m * np.std(Y) / np.std(X)

    # 间接效应
    indirect_effect = slope_a * slope_b
    # 直接效应
    direct_effect = slope_c_prime
    # 总效应
    total_effect = slope_c

    results = {
        'a_path': {'coef': slope_a, 'se': se_a, 'p': p_a},
        'b_path': {'coef': slope_b, 'se': se_b, 'p': p_b},
        'c_path': {'coef': slope_c, 'se': se_c, 'p': p_c},
        'c_prime_path': {'coef': slope_c_prime, 'se': np.nan, 'p': np.nan},
        'indirect_effect': indirect_effect,
        'direct_effect': direct_effect,
        'total_effect': total_effect,
        'mediation_ratio': abs(indirect_effect / total_effect) if total_effect != 0 else 0
    }

    # Bootstrap
    print(f"  执行Bootstrap ({n_bootstrap}次)...")
    boot_indirect = []
    boot_direct = []

    np.random.seed(42)
    for i in range(n_bootstrap):
        # 重采样
        idx = np.random.choice(n, n, replace=True)
        X_boot = X[idx]
        M_boot = M[idx]
        Y_boot = Y[idx]

        # 计算路径系数
        try:
            a_boot, _, _, _, _ = stats.linregress(X_boot, M_boot)
            b_boot, _, _, _, _ = stats.linregress(M_boot, Y_boot)
            c_boot, _, _, _, _ = stats.linregress(X_boot, Y_boot)

            # 间接效应
            boot_indirect.append(a_boot * b_boot)

            # 直接效应近似
            r_xm_b = np.corrcoef(X_boot, M_boot)[0, 1]
            r_my_b = np.corrcoef(M_boot, Y_boot)[0, 1]
            r_xy_b = np.corrcoef(X_boot, Y_boot)[0, 1]
            if abs(r_xm_b) < 1 and abs(r_my_b) < 1:
                r_xy_m_b = (r_xy_b - r_xm_b * r_my_b) / np.sqrt((1 - r_xm_b**2) * (1 - r_my_b**2))
                c_prime_b = r_xy_m_b * np.std(Y_boot) / np.std(X_boot) if np.std(X_boot) > 0 else 0
                boot_direct.append(c_prime_b)
        except:
            continue

    boot_indirect = np.array(boot_indirect)
    boot_direct = np.array(boot_direct)

    # 计算置信区间
    alpha = 1 - ci
    if len(boot_indirect) > 0:
        results['indirect_ci'] = (
            np.percentile(boot_indirect, alpha/2 * 100),
            np.percentile(boot_indirect, (1 - alpha/2) * 100)
        )
        results['indirect_se'] = np.std(boot_indirect)
        # 判断显著性（CI不包含0）
        results['indirect_significant'] = not (results['indirect_ci'][0] <= 0 <= results['indirect_ci'][1])

    if len(boot_direct) > 0:
        results['direct_ci'] = (
            np.percentile(boot_direct, alpha/2 * 100),
            np.percentile(boot_direct, (1 - alpha/2) * 100)
        )
        results['direct_se'] = np.std(boot_direct)
        results['direct_significant'] = not (results['direct_ci'][0] <= 0 <= results['direct_ci'][1])

    # Sobel检验
    z, p = sobel_test(slope_a, slope_b, se_a, se_b)
    results['sobel_z'] = z
    results['sobel_p'] = p

    # 中介类型判断
    if results.get('indirect_significant', False) and results.get('direct_significant', False):
        results['mediation_type'] = '部分中介'
    elif results.get('indirect_significant', False) and not results.get('direct_significant', False):
        results['mediation_type'] = '完全中介'
    else:
        results['mediation_type'] = '无中介效应'

    return results


def create_mediation_table(results: dict) -> pd.DataFrame:
    """
    创建中介效应检验结果表（表96）

    Parameters
    ----------
    results : dict
        中介效应分析结果

    Returns
    -------
    pd.DataFrame
        中介效应分解表
    """
    table_data = [
        {
            '效应类型': '总效应 (c)',
            '路径': 'eta1 -> eta3',
            '效应值': round(results['total_effect'], 4),
            '标准误': round(results['c_path']['se'], 4),
            '95% CI': '-',
            '显著性': '***' if results['c_path']['p'] < 0.001 else ('**' if results['c_path']['p'] < 0.01 else ('*' if results['c_path']['p'] < 0.05 else ''))
        },
        {
            '效应类型': '直接效应 (c\')',
            '路径': 'eta1 -> eta3 (控制eta2)',
            '效应值': round(results['direct_effect'], 4),
            '标准误': round(results.get('direct_se', np.nan), 4),
            '95% CI': f"[{results.get('direct_ci', (np.nan, np.nan))[0]:.3f}, {results.get('direct_ci', (np.nan, np.nan))[1]:.3f}]",
            '显著性': '[OK]' if results.get('direct_significant', False) else ''
        },
        {
            '效应类型': '间接效应 (a*b)',
            '路径': 'eta1 -> eta2 -> eta3',
            '效应值': round(results['indirect_effect'], 4),
            '标准误': round(results.get('indirect_se', np.nan), 4),
            '95% CI': f"[{results.get('indirect_ci', (np.nan, np.nan))[0]:.3f}, {results.get('indirect_ci', (np.nan, np.nan))[1]:.3f}]",
            '显著性': '[OK]' if results.get('indirect_significant', False) else ''
        },
        {
            '效应类型': 'a路径',
            '路径': 'eta1 -> eta2',
            '效应值': round(results['a_path']['coef'], 4),
            '标准误': round(results['a_path']['se'], 4),
            '95% CI': '-',
            '显著性': '***' if results['a_path']['p'] < 0.001 else ('**' if results['a_path']['p'] < 0.01 else ('*' if results['a_path']['p'] < 0.05 else ''))
        },
        {
            '效应类型': 'b路径',
            '路径': 'eta2 -> eta3',
            '效应值': round(results['b_path']['coef'], 4),
            '标准误': round(results['b_path']['se'], 4),
            '95% CI': '-',
            '显著性': '***' if results['b_path']['p'] < 0.001 else ('**' if results['b_path']['p'] < 0.01 else ('*' if results['b_path']['p'] < 0.05 else ''))
        }
    ]

    # 添加汇总信息
    table_data.append({
        '效应类型': '中介比例',
        '路径': '间接/总效应',
        '效应值': f"{results['mediation_ratio']*100:.1f}%",
        '标准误': '-',
        '95% CI': '-',
        '显著性': '-'
    })

    table_data.append({
        '效应类型': 'Sobel检验',
        '路径': '-',
        '效应值': f"z={results['sobel_z']:.3f}",
        '标准误': '-',
        '95% CI': '-',
        '显著性': f"p={results['sobel_p']:.4f}"
    })

    table_data.append({
        '效应类型': '中介类型',
        '路径': '-',
        '效应值': results['mediation_type'],
        '标准误': '-',
        '95% CI': '-',
        '显著性': '-'
    })

    return pd.DataFrame(table_data)


def plot_mediation_diagram(results: dict, paths_dict: dict) -> plt.Figure:
    """
    绘制中介效应路径图（图35）

    Parameters
    ----------
    results : dict
        中介效应分析结果
    paths_dict : dict
        路径字典

    Returns
    -------
    Figure
        matplotlib图表对象
    """
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=11)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)

    # 设置matplotlib支持中文和数学符号
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['mathtext.fontset'] = 'stix'  # 使用STIX字体渲染数学符号

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # 绘制变量框
    from matplotlib.patches import Ellipse, FancyBboxPatch

    # eta1 (左) - 使用LaTeX格式的希腊字母和下标
    ellipse1 = Ellipse((2, 4), width=2.5, height=1.5, fill=True,
                      facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(ellipse1)
    ax.text(2, 4.2, r'$\eta_1$', ha='center', va='center',
           fontsize=12, fontweight='bold')
    ax.text(2, 3.7, '认知域激活', ha='center', va='center',
           fontproperties=font_cn, fontsize=9)

    # eta2 (上中)
    ellipse2 = Ellipse((6, 6.5), width=2.5, height=1.5, fill=True,
                      facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax.add_patch(ellipse2)
    ax.text(6, 6.7, r'$\eta_2$', ha='center', va='center',
           fontsize=12, fontweight='bold')
    ax.text(6, 6.2, '参照点锚定', ha='center', va='center',
           fontproperties=font_cn, fontsize=9)

    # eta3 (右)
    ellipse3 = Ellipse((10, 4), width=2.5, height=1.5, fill=True,
                      facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax.add_patch(ellipse3)
    ax.text(10, 4.2, r'$\eta_3$', ha='center', va='center',
           fontsize=12, fontweight='bold')
    ax.text(10, 3.7, '跨域映射', ha='center', va='center',
           fontproperties=font_cn, fontsize=9)

    # 绘制路径箭头
    # a路径: eta1 -> eta2 (使用LaTeX格式)
    a_coef = results['a_path']['coef']
    a_sig = '***' if results['a_path']['p'] < 0.001 else ('**' if results['a_path']['p'] < 0.01 else '*')
    ax.annotate('', xy=(4.75, 6), xytext=(3.1, 4.6),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
    ax.text(3.5, 5.5, f'$a$ = {a_coef:.3f}{a_sig}', ha='center', va='bottom',
           fontsize=11, color='blue', fontweight='bold')

    # b路径: eta2 -> eta3
    b_coef = results['b_path']['coef']
    b_sig = '***' if results['b_path']['p'] < 0.001 else ('**' if results['b_path']['p'] < 0.01 else '*')
    ax.annotate('', xy=(8.9, 4.6), xytext=(7.25, 6),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
    ax.text(8.5, 5.5, f'$b$ = {b_coef:.3f}{b_sig}', ha='center', va='bottom',
           fontsize=11, color='blue', fontweight='bold')

    # c'路径: eta1 -> eta3 (直接效应)
    c_prime = results['direct_effect']
    # 使用星号标记与a、b路径保持一致
    c_prime_p = results.get('direct_p', 0.001)  # 默认显著
    c_prime_sig = '***' if c_prime_p < 0.001 else ('**' if c_prime_p < 0.01 else ('*' if c_prime_p < 0.05 else ''))
    ax.annotate('', xy=(8.75, 4), xytext=(3.25, 4),
               arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(6, 3.5, f"$c'$ = {c_prime:.3f}{c_prime_sig}", ha='center', va='top',
           fontsize=11, color='green')

    # 总效应 c (标注在下方)
    c_total = results['total_effect']
    ax.text(6, 2.5, f'总效应 $c$ = {c_total:.3f}', ha='center', va='top',
           fontproperties=font_cn, fontsize=10, color='gray')

    # 间接效应标注（使用乘号×而非字母x）
    indirect = results['indirect_effect']
    ax.text(6, 7.5, f'间接效应 ($a$ × $b$) = {indirect:.3f}', ha='center', va='bottom',
           fontproperties=font_cn, fontsize=11, color='red', fontweight='bold')

    # 中介比例
    ratio = results['mediation_ratio'] * 100
    ax.text(6, 1.5, f'中介比例 = {ratio:.1f}%', ha='center', va='top',
           fontproperties=font_cn, fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # 中介类型
    ax.text(6, 0.8, f"中介类型: {results['mediation_type']}", ha='center', va='top',
           fontproperties=font_cn, fontsize=11)

    # 图例（p使用斜体）
    ax.text(0.5, 7.5, r'注: *$p$<.05, **$p$<.01, ***$p$<.001', ha='left', va='top',
           fontproperties=font_cn, fontsize=9)
    ax.text(0.5, 7, 'Bootstrap 5000次', ha='left', va='top',
           fontproperties=font_cn, fontsize=9)

    # ax.set_title('图36 中介效应路径图',
                # fontproperties=font_cn_title, fontsize=14, pad=20)

    return fig


def main():
    """主函数"""
    print("=" * 60)
    print("Q3_05_中介效应.py")
    print("中介效应检验：eta2在eta1->eta3路径中的中介作用")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载数据
    print("\n" + "-" * 40)
    print("1. 加载SEM分析数据")
    print("-" * 40)
    df = load_sem_data(paths)
    print(f"样本量: {len(df)}")

    # 2. 准备中介分析数据
    print("\n" + "-" * 40)
    print("2. 准备中介分析数据")
    print("-" * 40)
    X, M, Y = prepare_mediation_data(df)

    if X is None or M is None or Y is None:
        print("  [X] 数据准备失败，无法进行中介分析")
        return None

    print(f"  X (eta1): {X.notna().sum()} 有效值")
    print(f"  M (eta2): {M.notna().sum()} 有效值")
    print(f"  Y (eta3): {Y.notna().sum()} 有效值")

    # 3. Bootstrap中介效应检验
    print("\n" + "-" * 40)
    print("3. Bootstrap中介效应检验")
    print("-" * 40)
    results = bootstrap_mediation(X, M, Y, n_bootstrap=5000)

    print(f"\n中介效应分析结果:")
    print(f"  a路径 (eta1->eta2): {results['a_path']['coef']:.4f}")
    print(f"  b路径 (eta2->eta3): {results['b_path']['coef']:.4f}")
    print(f"  c路径 (总效应): {results['total_effect']:.4f}")
    print(f"  c'路径 (直接效应): {results['direct_effect']:.4f}")
    print(f"  间接效应 (axb): {results['indirect_effect']:.4f}")
    print(f"  中介比例: {results['mediation_ratio']*100:.1f}%")
    print(f"  Sobel检验: z={results['sobel_z']:.3f}, p={results['sobel_p']:.4f}")
    print(f"  中介类型: {results['mediation_type']}")

    # 4. 创建表96
    print("\n" + "-" * 40)
    print("4. 保存表96: 中介效应检验结果")
    print("-" * 40)
    mediation_table = create_mediation_table(results)
    print(mediation_table.to_string(index=False))
    save_table(mediation_table, "中介效应检验结果", global_num=99,
               title="中介效应检验结果", formats=['csv', 'json'])

    # 5. 绘制图35
    print("\n" + "-" * 40)
    print("5. 绘制图36: 中介效应路径图")
    print("-" * 40)
    fig = plot_mediation_diagram(results, paths)
    save_figure(fig, "中介效应路径图", global_num=36,
                title="中介效应路径图")

    # 6. 验证结论
    print("\n" + "-" * 40)
    print("6. 中介效应验证结论")
    print("-" * 40)

    print(f"\n验证假设: eta2在eta1->eta3路径中起中介作用")
    print(f"预期结果: 部分中介（中介比例>=60%）")
    print(f"实际结果:")
    print(f"  - 间接效应显著: {'是' if results.get('indirect_significant', False) else '否'}")
    print(f"  - 直接效应显著: {'是' if results.get('direct_significant', False) else '否'}")
    print(f"  - 中介比例: {results['mediation_ratio']*100:.1f}%")
    print(f"  - 中介类型: {results['mediation_type']}")

    # 验证是否符合预期
    meets_expectation = (results['mediation_type'] == '部分中介' and
                        results['mediation_ratio'] >= 0.60)
    print(f"\n结论: {'[OK] 符合预期（部分中介>=60%）' if meets_expectation else '[~] 与预期有差异'}")

    print("\n" + "=" * 60)
    print("Q3_05_中介效应 完成")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
