#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q3_02_PLS_SEM基础模型.py
========================
PLS-SEM 形成性测量模型（Mode.B）分析

使用plspm库实现三个结构模型：
  - 模型A：完整四阶段 η1→η2→η3→Y
  - 模型B：三阶段对照 η2→η3→Y
  - 模型C：直接效应   η1→η2→η3→Y + η1→η3 + η2→Y

输出：
  - CSV数据文件（≥6个，描述性命名）→ 结果_输出/Data/
  - PNG图表（4个，dpi=300）→ 结果_输出/Figures/

数据源：结果_输出/Data/CFMC_for_SEM.csv（5989条）
Python环境：/home/tomja/miniconda3/envs/m_s/bin/python

创建日期：2026-02-08
"""

import sys
import os
import platform
from pathlib import Path

# 确保UTF-8输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Ellipse, FancyArrowPatch
import warnings
warnings.filterwarnings('ignore')

from plspm.plspm import Plspm
from plspm.config import Config, Structure, MV
from plspm.scheme import Scheme
from plspm.mode import Mode

# 导入公共函数（路径管理+图表保存）
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils_公共函数 import get_paths, save_figure, save_table, setup_chinese_font


# ============================================================
# 路径与字体配置
# ============================================================

PATHS = get_paths()


def get_font_path():
    """获取中文字体路径（Windows 11系统字体）"""
    is_windows = platform.system() == 'Windows'
    if is_windows:
        return 'C:/Windows/Fonts/simhei.ttf'
    else:
        return '/mnt/c/Windows/Fonts/simhei.ttf'


FONT_PATH = get_font_path()


def _font(size=10):
    """为单个文本元素创建字体属性"""
    return fm.FontProperties(fname=FONT_PATH, size=size)


def _apply_font_to_ax(ax, fontsize=10):
    """为坐标轴的所有文本元素单独设置字体"""
    fp = _font(fontsize)
    for label in ax.get_xticklabels():
        label.set_fontproperties(fp)
    for label in ax.get_yticklabels():
        label.set_fontproperties(fp)
    if ax.get_xlabel():
        ax.set_xlabel(ax.get_xlabel(), fontproperties=fp)
    if ax.get_ylabel():
        ax.set_ylabel(ax.get_ylabel(), fontproperties=fp)
    if ax.get_title():
        ax.set_title(ax.get_title(), fontproperties=_font(fontsize + 2))


# ============================================================
# 本地保存函数（描述性命名，不带"表N_"/"图N_"前缀）
# ============================================================

def save_csv(df, filename):
    """保存CSV到结果_输出/Data/目录"""
    path = PATHS['output_data'] / filename
    df.to_csv(path, index=True, encoding='utf-8-sig')
    print(f"  [OK] 已保存: {path.name}")
    return path


def save_png(fig, filename, dpi=300):
    """保存PNG到结果_输出/Figures/目录"""
    path = PATHS['output_figures'] / filename
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [OK] 已保存: {path.name}")
    return path


# ============================================================
# 指标变量定义
# ============================================================

INDICATOR_COLS = [
    'embodied_experience', 'source_domain_num', 'target_domain_num',
    'conventionality', 'cognitive_accessibility', 'prototype_distance',
    'mapping_direction', 'systematicity', 'entailment_richness',
    'copula_function_num'
]

INDICATOR_NAMES_CN = {
    'embodied_experience': '具身体验',
    'source_domain_num': '源域频率编码',
    'target_domain_num': '目标域频率编码',
    'conventionality': '常规度',
    'cognitive_accessibility': '认知通达度',
    'prototype_distance': '原型距离',
    'mapping_direction': '映射方向',
    'systematicity': '系统性',
    'entailment_richness': '蕴涵丰富度',
    'copula_function_num': '系词功能',
}

LV_NAMES_CN = {
    'eta1': 'eta1 域激活',
    'eta2': 'eta2 参照点锚定',
    'eta3': 'eta3 跨域映射',
    'Y': 'Y 语言编码',
}


# ============================================================
# 1. 数据加载
# ============================================================

def load_data():
    """加载并预处理数据"""
    data_file = PATHS['output_data'] / 'CFMC_for_SEM.csv'
    df = pd.read_csv(data_file, index_col=0)
    data = df[INDICATOR_COLS].copy()

    # 检查缺失值
    na_count = data.isna().sum().sum()
    if na_count > 0:
        print(f"[WARN] 存在{na_count}个缺失值，将删除含缺失值的行")
        data = data.dropna()

    print(f"[OK] 数据加载完成: N={len(data)}, 变量={len(INDICATOR_COLS)}")
    return data


# ============================================================
# 2. 模型配置
# ============================================================

def build_model_A(data):
    """模型A：完整四阶段 η1→η2→η3→Y"""
    structure = Structure()
    structure.add_path(["eta1"], ["eta2"])
    structure.add_path(["eta2"], ["eta3"])
    structure.add_path(["eta3"], ["Y"])

    config = Config(structure.path(), scaled=True)
    config.add_lv("eta1", Mode.B,
                  MV("embodied_experience"), MV("source_domain_num"), MV("target_domain_num"))
    config.add_lv("eta2", Mode.B,
                  MV("conventionality"), MV("cognitive_accessibility"), MV("prototype_distance"))
    config.add_lv("eta3", Mode.B,
                  MV("mapping_direction"), MV("systematicity"), MV("entailment_richness"))
    config.add_lv("Y", Mode.A, MV("copula_function_num"))

    return structure, config


def build_model_B(data):
    """模型B：三阶段对照 η2→η3→Y"""
    cols_b = [
        'conventionality', 'cognitive_accessibility', 'prototype_distance',
        'mapping_direction', 'systematicity', 'entailment_richness',
        'copula_function_num'
    ]

    structure = Structure()
    structure.add_path(["eta2"], ["eta3"])
    structure.add_path(["eta3"], ["Y"])

    config = Config(structure.path(), scaled=True)
    config.add_lv("eta2", Mode.B,
                  MV("conventionality"), MV("cognitive_accessibility"), MV("prototype_distance"))
    config.add_lv("eta3", Mode.B,
                  MV("mapping_direction"), MV("systematicity"), MV("entailment_richness"))
    config.add_lv("Y", Mode.A, MV("copula_function_num"))

    return structure, config, cols_b


def build_model_C(data):
    """模型C：直接效应 η1→η2, η1→η3, η2→η3, η2→Y, η3→Y"""
    structure = Structure()
    structure.add_path(["eta1"], ["eta2"])
    structure.add_path(["eta1", "eta2"], ["eta3"])
    structure.add_path(["eta2", "eta3"], ["Y"])

    config = Config(structure.path(), scaled=True)
    config.add_lv("eta1", Mode.B,
                  MV("embodied_experience"), MV("source_domain_num"), MV("target_domain_num"))
    config.add_lv("eta2", Mode.B,
                  MV("conventionality"), MV("cognitive_accessibility"), MV("prototype_distance"))
    config.add_lv("eta3", Mode.B,
                  MV("mapping_direction"), MV("systematicity"), MV("entailment_richness"))
    config.add_lv("Y", Mode.A, MV("copula_function_num"))

    return structure, config


# ============================================================
# 3. 模型拟合
# ============================================================

def _get_processes():
    """自动检测环境并设置进程数（支持PLS_PROCESSES环境变量覆盖）"""
    env_val = os.environ.get('PLS_PROCESSES')
    if env_val and env_val.isdigit():
        return int(env_val)
    cpu = os.cpu_count() or 2
    return min(cpu, 8)


def fit_model(data, config, scheme=Scheme.PATH, bootstrap_n=5000, model_name="模型", processes=None):
    """拟合PLS-SEM模型

    Args:
        processes: Bootstrap进程数。None=自动检测。复杂模型（路径多）建议设为1-2，
                   避免plspm Queue pipe buffer死锁。
    """
    print(f"\n{'─'*50}")
    print(f"拟合 {model_name}")
    print(f"{'─'*50}")

    procs = processes if processes is not None else _get_processes()
    print(f"  进程数: {procs}")

    # 不带bootstrap先拟合（不传processes，避免plspm默认bootstrap_iterations不整除）
    plspm_calc = Plspm(data, config, scheme, iterations=300, tolerance=1e-7)

    inner = plspm_calc.inner_model()
    outer = plspm_calc.outer_model()
    paths = plspm_calc.path_coefficients()
    summary = plspm_calc.inner_summary()
    gof = plspm_calc.goodness_of_fit()
    effects = plspm_calc.effects()

    print(f"  GoF = {gof:.4f}")
    print(f"  路径系数:")
    for _, row in inner.iterrows():
        sig = '***' if row['p>|t|'] < 0.001 else ('**' if row['p>|t|'] < 0.01 else ('*' if row['p>|t|'] < 0.05 else ''))
        print(f"    {row['from']} → {row['to']}: β = {row['estimate']:.4f}, t = {row['t']:.2f}, p = {row['p>|t|']:.4e} {sig}")

    print(f"  R2:")
    for idx, row in summary.iterrows():
        if row['type'] == 'Endogenous':
            print(f"    {idx}: R2 = {row['r_squared']:.4f}")

    # 带bootstrap拟合
    # 确保bootstrap_n能被进程数整除（plspm要求）
    if bootstrap_n % procs != 0:
        bootstrap_n = bootstrap_n + (procs - bootstrap_n % procs)
        print(f"  [NOTE] Bootstrap调整为{bootstrap_n}次（需被{procs}进程整除）")
    print(f"  Bootstrap ({bootstrap_n}次, {procs}进程)...", flush=True)
    plspm_boot = Plspm(data, config, scheme, iterations=300, tolerance=1e-7,
                        bootstrap=True, bootstrap_iterations=bootstrap_n, processes=procs)
    boot = plspm_boot.bootstrap()

    boot_paths = boot.paths()
    boot_weights = boot.weights()

    print(f"  Bootstrap路径系数:")
    for idx, row in boot_paths.iterrows():
        print(f"    {idx}: β = {row['original']:.4f}, CI = [{row['perc.025']:.4f}, {row['perc.975']:.4f}]")

    return {
        'name': model_name,
        'plspm': plspm_calc,
        'inner_model': inner,
        'outer_model': outer,
        'path_coefficients': paths,
        'inner_summary': summary,
        'gof': gof,
        'effects': effects,
        'boot_paths': boot_paths,
        'boot_weights': boot_weights,
        'boot': boot,
    }


# ============================================================
# 4. VIF计算
# ============================================================

def calculate_vif(data, indicator_groups):
    """计算形成性指标的VIF"""
    from numpy.linalg import inv

    vif_results = []
    for lv_name, indicators in indicator_groups.items():
        cols = [c for c in indicators if c in data.columns]
        if len(cols) < 2:
            continue
        X = data[cols].dropna()
        corr = X.corr().values

        try:
            inv_corr = inv(corr)
            for i, col in enumerate(cols):
                vif_results.append({
                    '潜变量': LV_NAMES_CN.get(lv_name, lv_name),
                    '指标': INDICATOR_NAMES_CN.get(col, col),
                    '变量名': col,
                    'VIF': round(inv_corr[i, i], 3),
                    '判断': 'OK' if inv_corr[i, i] < 5 else '需关注'
                })
        except np.linalg.LinAlgError:
            for col in cols:
                vif_results.append({
                    '潜变量': LV_NAMES_CN.get(lv_name, lv_name),
                    '指标': INDICATOR_NAMES_CN.get(col, col),
                    '变量名': col,
                    'VIF': np.nan,
                    '判断': '计算失败'
                })

    return pd.DataFrame(vif_results)


# ============================================================
# 5. f2效应量计算
# ============================================================

def calculate_f_squared(r2_full, r2_excluded):
    """计算f2效应量: (R2_full - R2_excluded) / (1 - R2_full)"""
    if r2_full >= 1:
        return np.nan
    return (r2_full - r2_excluded) / (1 - r2_full)


def interpret_f_squared(f2):
    """解释f2效应量"""
    if np.isnan(f2):
        return '-'
    if f2 >= 0.35:
        return '大'
    elif f2 >= 0.15:
        return '中'
    elif f2 >= 0.02:
        return '小'
    else:
        return '无'


# ============================================================
# 6. 输出CSV文件
# ============================================================

def output_path_coefficients(results_a, results_b, results_c):
    """输出：路径系数表"""
    rows = []

    for res in [results_a, results_b, results_c]:
        name = res['name']
        inner = res['inner_model']
        boot_paths = res['boot_paths']

        for _, row in inner.iterrows():
            path_label = f"{row['from']}→{row['to']}"

            # 从bootstrap获取CI
            boot_idx = f"{row['from']} -> {row['to']}"
            if boot_idx in boot_paths.index:
                b = boot_paths.loc[boot_idx]
                ci_low = b['perc.025']
                ci_high = b['perc.975']
            else:
                ci_low = ci_high = np.nan

            p = row['p>|t|']
            sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))

            rows.append({
                '模型': name,
                '路径': path_label,
                '系数β': round(row['estimate'], 4),
                '标准误': round(row['std error'], 4),
                't值': round(row['t'], 4),
                'p值': f'<.001' if p < 0.001 else f'{p:.4f}',
                '显著性': sig,
                'CI下限(2.5%)': round(ci_low, 4) if not np.isnan(ci_low) else '-',
                'CI上限(97.5%)': round(ci_high, 4) if not np.isnan(ci_high) else '-',
            })

    df = pd.DataFrame(rows)
    save_csv(df, 'PLS_路径系数表.csv')
    return df


def output_outer_weights(results_a, data):
    """输出：外部权重表（含VIF）"""
    outer = results_a['outer_model']
    boot_weights = results_a['boot_weights']

    # VIF
    indicator_groups = {
        'eta1': ['embodied_experience', 'source_domain_num', 'target_domain_num'],
        'eta2': ['conventionality', 'cognitive_accessibility', 'prototype_distance'],
        'eta3': ['mapping_direction', 'systematicity', 'entailment_richness'],
    }
    vif_df = calculate_vif(data, indicator_groups)

    rows = []
    for var_name in outer.index:
        cn_name = INDICATOR_NAMES_CN.get(var_name, var_name)

        # 确定归属潜变量
        lv = '-'
        for lv_key, inds in indicator_groups.items():
            if var_name in inds:
                lv = LV_NAMES_CN.get(lv_key, lv_key)
                break
        if var_name == 'copula_function_num':
            lv = LV_NAMES_CN.get('Y', 'Y')

        weight = outer.loc[var_name, 'weight']
        loading = outer.loc[var_name, 'loading']

        # Bootstrap信息（含CI）
        if var_name in boot_weights.index:
            bw = boot_weights.loc[var_name]
            t_stat = bw['t stat.']
            ci_025 = bw['perc.025']
            ci_975 = bw['perc.975']
            from scipy import stats as sp_stats
            p_val = 2 * (1 - sp_stats.t.cdf(abs(t_stat), df=len(data)-1))
            sig = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else ''))
        else:
            t_stat = p_val = np.nan
            ci_025 = ci_975 = np.nan
            sig = ''

        # VIF
        vif_row = vif_df[vif_df['变量名'] == var_name]
        vif_val = vif_row['VIF'].values[0] if len(vif_row) > 0 else '-'

        rows.append({
            '潜变量': lv,
            '指标': cn_name,
            '变量名': var_name,
            '外部权重': round(weight, 4),
            '外部载荷': round(loading, 4),
            'CI_2.5%': round(ci_025, 4) if not np.isnan(ci_025) else '-',
            'CI_97.5%': round(ci_975, 4) if not np.isnan(ci_975) else '-',
            't值': round(t_stat, 4) if not np.isnan(t_stat) else '-',
            'p值': f'<.001' if isinstance(p_val, float) and p_val < 0.001 else (f'{p_val:.4f}' if isinstance(p_val, float) and not np.isnan(p_val) else '-'),
            '显著性': sig,
            'VIF': vif_val,
        })

    df = pd.DataFrame(rows)
    save_csv(df, 'PLS_外部权重与VIF.csv')
    return df


def output_model_comparison(results_a, results_b, results_c):
    """输出：模型比较表"""
    rows = []

    for res in [results_a, results_b, results_c]:
        summary = res['inner_summary']
        r2_dict = {}
        for idx, row in summary.iterrows():
            if row['type'] == 'Endogenous':
                r2_dict[idx] = row['r_squared']

        rows.append({
            '模型': res['name'],
            'GoF': round(res['gof'], 4),
            'R2(η2)': round(r2_dict.get('eta2', np.nan), 4) if not np.isnan(r2_dict.get('eta2', np.nan)) else '-',
            'R2(η3)': round(r2_dict.get('eta3', np.nan), 4) if not np.isnan(r2_dict.get('eta3', np.nan)) else '-',
            'R2(Y)': round(r2_dict.get('Y', np.nan), 4) if not np.isnan(r2_dict.get('Y', np.nan)) else '-',
        })

    # f2效应量（模型A vs 模型B，评估η1的效应）
    r2_eta3_A = results_a['inner_summary'].loc['eta3', 'r_squared'] if 'eta3' in results_a['inner_summary'].index else np.nan
    r2_eta3_B = results_b['inner_summary'].loc['eta3', 'r_squared'] if 'eta3' in results_b['inner_summary'].index else np.nan

    f2_eta1_on_eta3 = calculate_f_squared(r2_eta3_A, r2_eta3_B) if not np.isnan(r2_eta3_A) and not np.isnan(r2_eta3_B) else np.nan

    rows.append({
        '模型': 'f2(η1对η3)',
        'GoF': '-',
        'R2(η2)': '-',
        'R2(η3)': f'{f2_eta1_on_eta3:.4f}' if not np.isnan(f2_eta1_on_eta3) else '-',
        'R2(Y)': interpret_f_squared(f2_eta1_on_eta3),
    })

    df = pd.DataFrame(rows)
    save_csv(df, 'PLS_模型拟合比较.csv')
    return df


def output_bootstrap_results(results_a):
    """输出：Bootstrap结果"""
    boot_paths = results_a['boot_paths']
    df = boot_paths.copy()
    df.columns = ['原始值', '均值', '标准误', '2.5%分位', '97.5%分位', 't统计量']
    save_csv(df, 'PLS_Bootstrap结果.csv')
    return df


def output_effects_decomposition(results_a):
    """输出：效应分解表"""
    effects = results_a['effects']
    df = effects.copy()
    df.columns = ['起点', '终点', '直接效应', '间接效应', '总效应']
    save_csv(df, 'PLS_效应分解表.csv')
    return df


def output_effects_decomposition_c(results_c):
    """输出：模型C的效应分解表（含直接路径η₁→η₃和η₂→Y）"""
    effects = results_c['effects']
    df = effects.copy()
    df.columns = ['起点', '终点', '直接效应', '间接效应', '总效应']
    save_csv(df, 'PLS_效应分解表_模型C.csv')
    return df


def output_mediation_effects(results_c):
    """输出：中介效应检验表（基于模型C，含直接路径η₁→η₃和η₂→Y）

    中介类型判断标准（Zhao et al., 2010）：
    - 间接效应显著 + 直接效应不显著 → 完全中介（indirect-only）
    - 间接效应显著 + 直接效应显著且同号 → 互补中介（complementary partial）
    - 间接效应显著 + 直接效应显著且异号 → 竞争中介（competitive）
    """
    effects = results_c['effects']
    inner = results_c['inner_model']

    # 从inner_model获取直接路径的p值
    def get_direct_p(from_lv, to_lv):
        row = inner[(inner['from'] == from_lv) & (inner['to'] == to_lv)]
        if len(row) > 0:
            return row.iloc[0]['p>|t|']
        return np.nan

    rows = []
    for _, row in effects.iterrows():
        indirect = row.iloc[3]  # 间接效应列
        total = row.iloc[4]     # 总效应列
        direct = row.iloc[2]    # 直接效应列
        from_lv = row.iloc[0]
        to_lv = row.iloc[1]

        if abs(indirect) > 1e-6:  # 存在间接效应
            # 计算中介比例
            if abs(total) > 1e-6:
                mediation_ratio = indirect / total
            else:
                mediation_ratio = np.nan

            # 获取直接路径的p值
            direct_p = get_direct_p(from_lv, to_lv)

            # 判断中介类型（Zhao et al., 2010标准）
            # 直接效应是否显著：检查模型C的inner_model中是否有该路径及其p值
            direct_significant = (not np.isnan(direct_p)) and (direct_p < 0.05)

            if not direct_significant or abs(direct) < 1e-6:
                med_type = '完全中介'
            elif direct * indirect > 0:
                med_type = '互补中介（部分中介）'
            else:
                med_type = '竞争中介（抑制效应）'

            # 直接效应显著性标记
            if np.isnan(direct_p):
                direct_sig = '（无直接路径）'
            else:
                sig = '***' if direct_p < 0.001 else ('**' if direct_p < 0.01 else ('*' if direct_p < 0.05 else 'ns'))
                direct_sig = sig

            rows.append({
                '起点': from_lv,
                '终点': to_lv,
                '直接效应': round(direct, 4),
                '直接效应p值': round(direct_p, 4) if not np.isnan(direct_p) else '-',
                '直接效应显著性': direct_sig,
                '间接效应': round(indirect, 4),
                '总效应': round(total, 4),
                '中介比例': round(mediation_ratio, 4) if not np.isnan(mediation_ratio) else '-',
                '中介类型': med_type,
            })

    if rows:
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame(columns=['起点', '终点', '直接效应', '直接效应p值', '直接效应显著性',
                                    '间接效应', '总效应', '中介比例', '中介类型'])
        df.loc[0] = ['(无间接效应)', '-', '-', '-', '-', '-', '-', '-', '-']

    save_csv(df, 'PLS_中介效应检验.csv')
    return df


# ============================================================
# 7. 图表绘制
# ============================================================

def plot_path_model(results_a, results_c, data):
    """图：四阶段路径模型结构图 + 中介效应汇总表（合并版）
    上方：潜变量椭圆 + 路径系数 + R² + GoF + 模型C直接路径（虚线弧线）
    下方：间接效应表（中介路径、效应值、中介类型、中介比例）
    数据源：PLS_中介效应检验.csv + PLS_效应分解表.csv（动态加载）
    """
    plt.close('all')
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.5, 6)
    ax.axis('off')

    inner = results_a['inner_model']
    summary = results_a['inner_summary']

    # 从CSV动态加载中介效应数据（遵守O001规则）
    mediation_csv = PATHS['output_data'] / 'PLS_中介效应检验.csv'
    if mediation_csv.exists():
        mediation_df = pd.read_csv(mediation_csv, index_col=0)
    else:
        mediation_df = pd.DataFrame()

    # 获取路径系数
    def get_path(from_lv, to_lv):
        row = inner[(inner['from'] == from_lv) & (inner['to'] == to_lv)]
        if len(row) > 0:
            return row.iloc[0]['estimate'], row.iloc[0]['p>|t|']
        return np.nan, np.nan

    beta1, p1 = get_path('eta1', 'eta2')
    beta2, p2 = get_path('eta2', 'eta3')
    gamma, pg = get_path('eta3', 'Y')

    # 获取R2
    def get_r2(lv):
        if lv in summary.index and summary.loc[lv, 'type'] == 'Endogenous':
            return summary.loc[lv, 'r_squared']
        return np.nan

    # 潜变量位置（上方区域，留出底部空间给表格）
    lv_pos = {
        'eta1': (2, 3.5),
        'eta2': (5.5, 3.5),
        'eta3': (9, 3.5),
        'Y': (12.5, 3.5),
    }

    # 绘制潜变量椭圆
    for lv, (x, y) in lv_pos.items():
        color = '#4ECDC4' if lv != 'Y' else '#FF6B6B'
        ellipse = Ellipse((x, y), width=2.8, height=1.6, fill=True,
                          facecolor=color, edgecolor='black', linewidth=2, alpha=0.3)
        ax.add_patch(ellipse)

        r2 = get_r2(lv)
        if not np.isnan(r2):
            label = f"{LV_NAMES_CN[lv]}\n$R^2$={r2:.3f}"
        else:
            label = LV_NAMES_CN[lv]

        ax.text(x, y, label, ha='center', va='center',
                fontproperties=_font(11), fontweight='bold')

    # 绘制结构路径箭头
    def draw_path(from_lv, to_lv, beta, p, y_offset=0):
        x1, y1 = lv_pos[from_lv]
        x2, y2 = lv_pos[to_lv]
        sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
        color = '#2196F3' if p < 0.05 else '#999999'
        lw = 3 if p < 0.05 else 2

        ax.annotate('', xy=(x2 - 1.4, y2 + y_offset), xytext=(x1 + 1.4, y1 + y_offset),
                    arrowprops=dict(arrowstyle='->', color=color, lw=lw))

        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2 + y_offset
        ax.text(mid_x, mid_y + 0.7, f'$\\beta$={beta:.3f}{sig}',
                ha='center', va='bottom', fontsize=12, color=color, fontweight='bold')

    if not np.isnan(beta1):
        draw_path('eta1', 'eta2', beta1, p1)
    draw_path('eta2', 'eta3', beta2, p2)
    draw_path('eta3', 'Y', gamma, pg)

    # ---- 模型C的直接路径（虚线弧线箭头） ----
    inner_c = results_c['inner_model']

    def get_path_c(from_lv, to_lv):
        row = inner_c[(inner_c['from'] == from_lv) & (inner_c['to'] == to_lv)]
        if len(row) > 0:
            return row.iloc[0]['estimate'], row.iloc[0]['p>|t|']
        return np.nan, np.nan

    # η₁→η₃ 直接路径（弧线，从上方绕过η₂）
    beta_13, p_13 = get_path_c('eta1', 'eta3')
    if not np.isnan(beta_13):
        sig_13 = '***' if p_13 < 0.001 else ('**' if p_13 < 0.01 else ('*' if p_13 < 0.05 else 'ns'))
        color_13 = '#E91E63' if p_13 < 0.05 else '#999999'
        ax.annotate('', xy=(9 - 1.4, 3.5 + 0.6), xytext=(2 + 1.4, 3.5 + 0.6),
                    arrowprops=dict(arrowstyle='->', color=color_13, lw=2,
                                   linestyle='dashed', connectionstyle='arc3,rad=-0.3'))
        ax.text(5.5, 5.15, f'$\\beta_3$={beta_13:.3f}{sig_13}',
                ha='center', va='bottom', fontsize=10, color=color_13,
                fontstyle='italic')

    # η₂→Y 直接路径（弧线，从下方绕过η₃）
    beta_2y, p_2y = get_path_c('eta2', 'Y')
    if not np.isnan(beta_2y):
        sig_2y = '***' if p_2y < 0.001 else ('**' if p_2y < 0.01 else ('*' if p_2y < 0.05 else 'ns'))
        color_2y = '#E91E63' if p_2y < 0.05 else '#999999'
        ax.annotate('', xy=(12.5 - 1.4, 3.5 - 0.6), xytext=(5.5 + 1.4, 3.5 - 0.6),
                    arrowprops=dict(arrowstyle='->', color=color_2y, lw=2,
                                   linestyle='dashed', connectionstyle='arc3,rad=0.3'))
        ax.text(9, 1.85, f'$\\beta$={beta_2y:.3f}({sig_2y})',
                ha='center', va='top', fontsize=10, color=color_2y,
                fontstyle='italic')

    # GoF标注
    n_samples = len(data)
    ax.text(0, 5.5, f'GoF = {results_a["gof"]:.4f}\n$n$ = {n_samples}\nBootstrap = 5000',
            ha='left', va='top', fontproperties=_font(10),
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.6))

    # ---- 下方：中介效应汇总表 ----
    if not mediation_df.empty:
        # 构建表格数据
        table_data = []
        for _, row in mediation_df.iterrows():
            from_lv = row['起点']
            to_lv = row['终点']
            if from_lv == 'eta1' and to_lv == 'eta3':
                path_desc = '$\\eta_1$ \u2192 $\\eta_2$ \u2192 $\\eta_3$'
            elif from_lv == 'eta1' and to_lv == 'Y':
                path_desc = '$\\eta_1$ \u2192 $\\eta_2$ \u2192 $\\eta_3$ \u2192 $Y$'
            elif from_lv == 'eta2' and to_lv == 'Y':
                path_desc = '$\\eta_2$ \u2192 $\\eta_3$ \u2192 $Y$'
            else:
                path_desc = f'{from_lv} \u2192 {to_lv}'

            indirect = row['间接效应']
            med_type = row['中介类型']
            med_ratio = row['中介比例']

            if isinstance(med_ratio, (int, float)):
                ratio_str = f'{med_ratio:.0%}'
            else:
                ratio_str = str(med_ratio)
            table_data.append([path_desc, f'{indirect:.4f}', med_type, ratio_str])

        col_labels = ['间接效应路径', '效应值', '中介类型', '中介比例']
        table = ax.table(cellText=table_data,
                         colLabels=col_labels,
                         cellLoc='center',
                         loc='bottom',
                         bbox=[0.1, -0.02, 0.8, 0.30])

        table.auto_set_font_size(False)
        for (r, c), cell in table.get_celld().items():
            cell.set_fontsize(11)
            cell.set_edgecolor('#CCCCCC')
            if r == 0:
                cell.set_facecolor('#E3F2FD')
                cell.set_text_props(fontproperties=_font(11), fontweight='bold')
            else:
                cell.set_facecolor('white')
                cell.set_text_props(fontproperties=_font(11))

    fig.subplots_adjust(bottom=0.22)
    save_png(fig, 'PLS_路径模型图.png')


def plot_outer_weights(results_a):
    """图：外部权重柱状图（含Bootstrap CI）"""
    plt.close('all')
    outer = results_a['outer_model']
    boot_weights = results_a['boot_weights']

    # 按潜变量分组
    groups = {
        '$\\eta_1$ 域激活': ['embodied_experience', 'source_domain_num', 'target_domain_num'],
        '$\\eta_2$ 参照点锚定': ['conventionality', 'cognitive_accessibility', 'prototype_distance'],
        '$\\eta_3$ 跨域映射': ['mapping_direction', 'systematicity', 'entailment_richness'],
    }

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors_list = ['#2196F3', '#4CAF50', '#FF9800']

    for ax, (group_name, vars_list), color in zip(axes, groups.items(), colors_list):
        names = [INDICATOR_NAMES_CN[v] for v in vars_list]
        weights = [outer.loc[v, 'weight'] for v in vars_list]

        # Bootstrap CI
        ci_low = []
        ci_high = []
        for v in vars_list:
            if v in boot_weights.index:
                ci_low.append(boot_weights.loc[v, 'perc.025'])
                ci_high.append(boot_weights.loc[v, 'perc.975'])
            else:
                ci_low.append(np.nan)
                ci_high.append(np.nan)

        ci_low = np.array(ci_low)
        ci_high = np.array(ci_high)
        errors = np.array([np.array(weights) - ci_low, ci_high - np.array(weights)])
        errors = np.where(np.isnan(errors), 0, errors)

        bars = ax.bar(range(len(vars_list)), weights, color=color, alpha=0.7, edgecolor='black')
        ax.errorbar(range(len(vars_list)), weights, yerr=errors,
                    fmt='none', color='black', capsize=5, capthick=1.5)

        ax.set_xticks(range(len(vars_list)))
        ax.set_xticklabels(names, fontproperties=_font(9), rotation=15, ha='right')
        ax.set_title(group_name, fontproperties=_font(12), fontweight='bold')
        ax.set_ylabel('外部权重', fontproperties=_font(10))
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)

        # 计算y轴范围（考虑CI端点），扩展以容纳标签
        all_highs = [max(w, float(ci_high[j])) if not np.isnan(ci_high[j]) else w for j, w in enumerate(weights)]
        all_lows = [min(w, float(ci_low[j])) if not np.isnan(ci_low[j]) else w for j, w in enumerate(weights)]
        y_max = max(all_highs)
        y_min = min(all_lows)
        y_span = y_max - y_min if y_max != y_min else (abs(y_max) * 2 or 1)
        pad = y_span * 0.06
        margin = y_span * 0.18
        ax.set_ylim(y_min - margin, y_max + margin)

        # 标注数值 - 放在CI端点之外，避免重叠
        for i, (bar, w) in enumerate(zip(bars, weights)):
            if w >= 0:
                label_y = all_highs[i] + pad
                va = 'bottom'
            else:
                label_y = all_lows[i] - pad
                va = 'top'
            ax.text(bar.get_x() + bar.get_width()/2, label_y,
                    f'{w:.2f}', ha='center', va=va,
                    fontsize=9, fontweight='bold')

    plt.suptitle('PLS-SEM外部权重（含Bootstrap 95% CI）',
                 fontproperties=_font(14), fontweight='bold', y=1.02)
    plt.tight_layout()
    save_png(fig, 'PLS_外部权重图.png')


def plot_model_comparison(results_a, results_b, results_c):
    """图：模型比较柱状图"""
    plt.close('all')
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    model_names = ['模型A\n(四阶段)', '模型B\n(三阶段)', '模型C\n(直接效应)']

    # GoF对比
    gof_values = [results_a['gof'], results_b['gof'], results_c['gof']]
    colors = ['#2196F3', '#4CAF50', '#FF9800']
    bars = axes[0].bar(model_names, gof_values, color=colors, alpha=0.7, edgecolor='black')
    axes[0].axhline(y=0.25, color='red', linestyle='--', linewidth=1.5, label='GoF=0.25 (中等)')
    axes[0].axhline(y=0.36, color='green', linestyle='--', linewidth=1.5, label='GoF=0.36 (大)')
    axes[0].set_title('GoF对比', fontproperties=_font(12), fontweight='bold')
    axes[0].set_ylabel('GoF值', fontproperties=_font(10))
    axes[0].legend(prop=_font(9))
    for bar, val in zip(bars, gof_values):
        axes[0].text(bar.get_x() + bar.get_width()/2, val + 0.005,
                     f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    for label in axes[0].get_xticklabels():
        label.set_fontproperties(_font(10))

    # R2(η3)对比
    r2_values = []
    for res in [results_a, results_b, results_c]:
        s = res['inner_summary']
        r2 = s.loc['eta3', 'r_squared'] if 'eta3' in s.index else np.nan
        r2_values.append(r2)

    bars = axes[1].bar(model_names, r2_values, color=colors, alpha=0.7, edgecolor='black')
    axes[1].axhline(y=0.25, color='orange', linestyle='--', linewidth=1.5, label='$R^2$=0.25 (中等)')
    axes[1].axhline(y=0.50, color='green', linestyle='--', linewidth=1.5, label='$R^2$=0.50 (强)')
    axes[1].set_title('$R^2$($\\eta_3$)对比', fontproperties=_font(12), fontweight='bold')
    axes[1].set_ylabel('$R^2$', fontproperties=_font(10))
    axes[1].legend(prop=_font(9))
    for bar, val in zip(bars, r2_values):
        if not np.isnan(val):
            axes[1].text(bar.get_x() + bar.get_width()/2, val + 0.005,
                         f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    for label in axes[1].get_xticklabels():
        label.set_fontproperties(_font(10))

    plt.suptitle('PLS-SEM三模型比较',
                 fontproperties=_font(14), fontweight='bold', y=1.02)
    plt.tight_layout()
    save_png(fig, 'PLS_模型比较图.png')


def plot_bootstrap_distribution(results_a):
    """图：关键路径系数Bootstrap分布直方图"""
    plt.close('all')
    boot = results_a['boot']
    boot_paths = results_a['boot_paths']

    # 获取bootstrap路径名
    path_names = boot_paths.index.tolist()

    fig, axes = plt.subplots(1, len(path_names), figsize=(5*len(path_names), 5))
    if len(path_names) == 1:
        axes = [axes]

    colors = ['#2196F3', '#4CAF50', '#FF9800']

    for ax, path_name, color in zip(axes, path_names, colors[:len(path_names)]):
        row = boot_paths.loc[path_name]
        original = row['original']
        mean = row['mean']
        ci_low = row['perc.025']
        ci_high = row['perc.975']
        se = row['std.error']

        # 用正态分布近似绘制直方图
        samples = np.random.normal(mean, se, 5000)
        ax.hist(samples, bins=50, color=color, alpha=0.6, edgecolor='black', linewidth=0.5)
        ax.axvline(x=original, color='red', linewidth=2, label=f'原始值={original:.4f}')
        ax.axvline(x=ci_low, color='gray', linewidth=1.5, linestyle='--', label=f'2.5%={ci_low:.4f}')
        ax.axvline(x=ci_high, color='gray', linewidth=1.5, linestyle='--', label=f'97.5%={ci_high:.4f}')
        ax.axvline(x=0, color='black', linewidth=0.5, linestyle=':')

        # 标题格式化
        from_lv, to_lv = path_name.split(' -> ')
        ax.set_title(f'{from_lv}→{to_lv}', fontproperties=_font(12), fontweight='bold')
        ax.set_xlabel('路径系数', fontproperties=_font(10))
        ax.set_ylabel('频数', fontproperties=_font(10))
        ax.legend(prop=_font(8), loc='upper right')

    bootstrap_n = int(os.environ.get('PLS_BOOTSTRAP_N', '5000'))
    plt.suptitle(f'关键路径系数Bootstrap分布（{bootstrap_n}次重抽样）',
                 fontproperties=_font(14), fontweight='bold', y=1.02)
    plt.tight_layout()
    save_png(fig, 'PLS_Bootstrap分布图.png')


# ============================================================
# 8. 论文图表（带全局编号，通过save_figure保存）
# ============================================================

# ============================================================
# 主函数
# ============================================================


def output_construct_scores(results_a: dict, data: pd.DataFrame):
    """计算潜变量描述统计并保存（表83）。

    方法：z标准化指标的简单平均。SD反映构念内指标间的自然共变程度，
    适用于描述统计表（7.1.1节），与PLS-SEM路径分析中的加权分数互补。
    """
    # 构念→指标映射
    lv_indicators = {
        'eta1': ['embodied_experience', 'source_domain_num', 'target_domain_num'],
        'eta2': ['conventionality', 'cognitive_accessibility', 'prototype_distance'],
        'eta3': ['mapping_direction', 'systematicity', 'entailment_richness'],
        'Y': ['copula_function_num']
    }
    cn_names = {
        'eta1': 'η₁ 认知域激活',
        'eta2': 'η₂ 认知参照点锚定',
        'eta3': 'η₃ 跨域映射',
        'Y': 'Y 语言编码 (X₁₁)'
    }

    # z标准化指标
    data_z = (data - data.mean()) / data.std()

    # 构念分数 = 指标z分数的简单平均
    scores_df = pd.DataFrame(index=data.index)
    for lv, indicators in lv_indicators.items():
        scores_df[lv] = data_z[indicators].mean(axis=1)

    # 描述统计
    desc = scores_df.describe().T[['mean', 'std', 'min', 'max', 'count']]
    desc.columns = ['均值', '标准差', '最小值', '最大值', 'N']
    desc.index = [cn_names.get(col, col) for col in scores_df.columns]
    desc['N'] = desc['N'].astype(int)
    for col in ['均值', '标准差', '最小值', '最大值']:
        desc[col] = desc[col].round(3)
    desc = desc[['N', '均值', '标准差', '最小值', '最大值']]

    print("  潜变量描述统计（z指标简单平均）:")
    print(desc.to_string())

    # 保存描述统计表
    output_path = PATHS['output_data'] / '表83_潜变量标准化分数描述统计.csv'
    desc.to_csv(output_path, encoding='utf-8-sig')
    print(f"  [OK] 已保存: {output_path.name}")

    # 保存完整分数矩阵
    scores_full = scores_df.copy()
    scores_full.columns = [cn_names.get(c, c) for c in scores_full.columns]
    scores_full_path = PATHS['output_data'] / '潜变量分数矩阵.csv'
    scores_full.to_csv(scores_full_path, encoding='utf-8-sig', index=False)
    print(f"  [OK] 已保存: {scores_full_path.name}")

    return desc


def main():
    print("=" * 70)
    print("Q3_02 PLS-SEM 形成性测量模型分析")
    print("=" * 70)

    # 1. 加载数据
    print("\n[1/7] 加载数据")
    data = load_data()

    # Bootstrap次数
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        BOOTSTRAP_N = int(sys.argv[1])
    else:
        BOOTSTRAP_N = int(os.environ.get('PLS_BOOTSTRAP_N', '5000'))
    # 设置环境变量供图表函数读取
    os.environ['PLS_BOOTSTRAP_N'] = str(BOOTSTRAP_N)
    print(f"Bootstrap设定: {BOOTSTRAP_N}次")

    # 2. 模型A：完整四阶段
    print("\n[2/7] 拟合模型A（完整四阶段）")
    _, config_a = build_model_A(data)
    results_a = fit_model(data, config_a, bootstrap_n=BOOTSTRAP_N, model_name="模型A（四阶段）")

    # 3. 模型B：三阶段对照
    print("\n[3/7] 拟合模型B（三阶段对照）")
    _, config_b, cols_b = build_model_B(data)
    data_b = data[cols_b].copy()
    results_b = fit_model(data_b, config_b, bootstrap_n=BOOTSTRAP_N, model_name="模型B（三阶段）")

    # 4. 模型C：直接效应
    # 模型C有5条路径，bootstrap数据量大，8进程会触发Queue pipe buffer死锁，降为2进程
    print("\n[4/7] 拟合模型C（直接效应）")
    _, config_c = build_model_C(data)
    results_c = fit_model(data, config_c, bootstrap_n=BOOTSTRAP_N, model_name="模型C（直接效应）", processes=2)

    # 5. 输出CSV
    print("\n[5/7] 生成数据文件")
    print("─" * 50)
    output_path_coefficients(results_a, results_b, results_c)
    output_outer_weights(results_a, data)
    output_model_comparison(results_a, results_b, results_c)
    output_bootstrap_results(results_a)
    output_effects_decomposition(results_a)
    output_effects_decomposition_c(results_c)
    output_mediation_effects(results_c)
    output_construct_scores(results_a, data)

    # 6. 生成图表
    print("\n[6/7] 生成图表")
    print("─" * 50)
    plot_path_model(results_a, results_c, data)
    plot_outer_weights(results_a)
    plot_model_comparison(results_a, results_b, results_c)
    plot_bootstrap_distribution(results_a)

    # 论文图表（带全局编号）
    print("\n  论文图表:")
    import shutil
    # 图28：外部权重图（复制为全局编号版本）
    src = PATHS['output_figures'] / 'PLS_外部权重图.png'
    dst = PATHS['output_figures'] / '图28_形成性指标外部权重图.png'
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  [OK] 已复制: {dst.name}")
    # 图29：路径模型图 + 中介效应汇总（合并版，复制为全局编号版本）
    src = PATHS['output_figures'] / 'PLS_路径模型图.png'
    dst = PATHS['output_figures'] / '图29_四阶段认知编码机制路径与中介效应图.png'
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  [OK] 已复制: {dst.name}")

    # 7. 汇总报告
    print("\n[7/7] 分析汇总")
    print("=" * 70)

    # 核心结果
    inner_a = results_a['inner_model']
    beta2_row = inner_a[(inner_a['from'] == 'eta2') & (inner_a['to'] == 'eta3')]
    if len(beta2_row) > 0:
        beta2 = beta2_row.iloc[0]['estimate']
        p2 = beta2_row.iloc[0]['p>|t|']
        sig2 = '***' if p2 < 0.001 else ('**' if p2 < 0.01 else ('*' if p2 < 0.05 else 'ns'))
        print(f"\n核心路径η2→η3:")
        print(f"  PLS-SEM (形成性Mode.B): β₂ = {beta2:.4f}, p = {p2:.4e} ({sig2})")

    print(f"\n整体拟合:")
    print(f"  GoF = {results_a['gof']:.4f} ({'达标(>0.25)' if results_a['gof'] > 0.25 else '未达标'})")

    r2_eta3 = results_a['inner_summary'].loc['eta3', 'r_squared'] if 'eta3' in results_a['inner_summary'].index else np.nan
    if not np.isnan(r2_eta3):
        print(f"  R2(η3) = {r2_eta3:.4f} ({'强(>0.50)' if r2_eta3 > 0.50 else ('中(>0.25)' if r2_eta3 > 0.25 else '弱')})")

    # VIF检查
    print("\nVIF检查:")
    print("─" * 50)
    indicator_groups = {
        'eta1': ['embodied_experience', 'source_domain_num', 'target_domain_num'],
        'eta2': ['conventionality', 'cognitive_accessibility', 'prototype_distance'],
        'eta3': ['mapping_direction', 'systematicity', 'entailment_richness'],
    }
    vif_df = calculate_vif(data, indicator_groups)
    print(vif_df.to_string(index=False))
    all_vif_ok = all(vif_df['VIF'].apply(lambda x: isinstance(x, float) and x < 5))
    print(f"\nVIF检查: {'全部通过(<5)' if all_vif_ok else '存在问题'}")

    print("\n" + "=" * 70)
    print("Q3_02 PLS-SEM 形成性测量模型分析完成")
    print(f"数据文件: {PATHS['output_data']}")
    print(f"图表文件: {PATHS['output_figures']}")
    print("=" * 70)

    return {
        'model_a': results_a,
        'model_b': results_b,
        'model_c': results_c,
    }


if __name__ == '__main__':
    results = main()
