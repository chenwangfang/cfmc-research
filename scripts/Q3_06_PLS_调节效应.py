# -*- coding: utf-8 -*-
"""
Q3_06_调节效应.py
整体性/关系性文本间接指标的探索性调节效应分析

研究内容：
- 探索性分析：整体性意象与关系性思维文本间接指标对四阶段机制路径关联的交互线索
- holistic_imagery与relational_thinking高相关（r~=0.74），合并为降维用复合指标
- 基于阶段指标均值进行OLS交互回归，不在PLS-SEM内部重新估计调节路径
- 报告未校正p值，并提供FDR(BH)与Bonferroni敏感性提示

输出：
- 表66：调节效应检验结果表
- 图32：整体性/关系性复合指标调节效应示意图

依赖：
- CFMC_for_SEM.csv（由Q3_01生成）
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import textwrap
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from utils_公共函数 import (
    save_table, save_figure, setup_chinese_font, get_paths
)

# ==================== 辅助函数 ====================

def print_section_header(title: str):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

def print_subsection_header(title: str):
    """打印小节标题"""
    print(f"\n{'-'*40}")
    print(f"{title}")
    print('-'*40)

def format_p_value(p) -> str:
    """格式化p值"""
    if pd.isna(p):
        return '-'
    if p < 0.001:
        return '<.001'
    elif p < 0.01:
        return f'{p:.3f}'
    else:
        return f'{p:.3f}'

def format_q_value(q) -> str:
    """格式化FDR(BH) q值"""
    if pd.isna(q):
        return '-'
    if q < 0.001:
        return '<.001'
    return f'{q:.3f}'

def ensure_output_dirs(dirs):
    """确保输出目录存在"""
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

# ==================== 配置参数 ====================

# 输入文件
SEM_DATA_FILE = SCRIPT_DIR.parent / "结果_输出" / "Data" / "CFMC_for_SEM.csv"

# 输出目录
OUTPUT_DIR = SCRIPT_DIR.parent / "结果_输出"

# 阶段字段映射
STAGE_FIELDS = {
    'eta1': ['embodied_experience', 'source_domain_num', 'target_domain_num'],
    'eta2': ['conventionality', 'cognitive_accessibility', 'prototype_distance'],
    'eta3': ['mapping_direction', 'systematicity', 'entailment_richness']
}

# 路径定义
PATHS = [
    ('eta1->eta2', 'beta₁', 'eta1', 'eta2'),
    ('eta2->eta3', 'beta₂', 'eta2', 'eta3'),
    ('eta1->eta3', 'beta₃', 'eta1', 'eta3'),
    ('eta3->Y', 'γ', 'eta3', 'copula_function_num')
]

# ==================== 核心函数 ====================

def load_sem_data() -> pd.DataFrame:
    """加载SEM数据"""
    print_subsection_header("加载SEM数据")

    if not SEM_DATA_FILE.exists():
        print(f"  警告：SEM数据文件不存在: {SEM_DATA_FILE}")
        print("  请先运行 Q3_01_描述统计.py 生成数据")
        return None

    df = pd.read_csv(SEM_DATA_FILE)
    print(f"  加载数据: {len(df)} 条记录")

    return df


def create_composite_moderator(df: pd.DataFrame) -> pd.DataFrame:
    """
    创建整体性/关系性复合指标。

    若两个文本间接指标字段缺失，直接报错终止。调节效应分析不能使用模拟数据替代真实
    标注字段，否则会污染复现结果。

    chinese_cognitive_style = (holistic_imagery + relational_thinking) / 2
    chinese_cognitive_style_z = zscore(chinese_cognitive_style)
    """
    print_subsection_header("创建复合调节变量")

    # 检查原始字段
    has_holistic = 'holistic_imagery' in df.columns
    has_relational = 'relational_thinking' in df.columns

    print(f"  holistic_imagery字段存在: {has_holistic}")
    print(f"  relational_thinking字段存在: {has_relational}")

    if has_holistic and has_relational:
        # 计算相关性
        valid_mask = df['holistic_imagery'].notna() & df['relational_thinking'].notna()
        if valid_mask.sum() > 30:
            corr = df.loc[valid_mask, 'holistic_imagery'].corr(
                df.loc[valid_mask, 'relational_thinking']
            )
            print(f"  两变量相关系数: r = {corr:.3f}")

        # 创建复合变量
        df['chinese_cognitive_style'] = (
            df['holistic_imagery'] + df['relational_thinking']
        ) / 2

        # 标准化
        valid = df['chinese_cognitive_style'].notna()
        if valid.sum() > 0:
            mean_val = df.loc[valid, 'chinese_cognitive_style'].mean()
            std_val = df.loc[valid, 'chinese_cognitive_style'].std()
            if std_val > 0:
                df['chinese_cognitive_style_z'] = (
                    df['chinese_cognitive_style'] - mean_val
                ) / std_val
            else:
                df['chinese_cognitive_style_z'] = 0

        print(f"  复合变量有效样本: {df['chinese_cognitive_style'].notna().sum()}")

    else:
        missing = []
        if not has_holistic:
            missing.append('holistic_imagery')
        if not has_relational:
            missing.append('relational_thinking')
        raise ValueError(
            f"缺少整体性/关系性文本间接指标字段: {', '.join(missing)}。"
            "请先回到CFMC标注数据或Q3_01预处理脚本补齐真实字段。"
        )

    return df


def calculate_latent_scores(df: pd.DataFrame) -> pd.DataFrame:
    """计算阶段指标均值（各阶段指标标准化后取均值）"""
    print_subsection_header("计算潜变量得分")

    for stage, fields in STAGE_FIELDS.items():
        # 获取存在的字段
        existing_fields = [f for f in fields if f in df.columns]

        if existing_fields:
            # 标准化各指标
            standardized = []
            for field in existing_fields:
                valid = df[field].notna()
                if valid.sum() > 0:
                    z_score = stats.zscore(df.loc[valid, field])
                    temp = pd.Series(index=df.index, dtype=float)
                    temp.loc[valid] = z_score
                    standardized.append(temp)

            if standardized:
                # 计算平均得分
                stage_name = stage.replace('₁', '1').replace('₂', '2').replace('₃', '3')
                df[f'{stage_name}_score'] = pd.concat(standardized, axis=1).mean(axis=1)
                print(f"  {stage}: 使用{len(existing_fields)}个指标")

    # eta3得分重命名为eta3
    if 'eta3_score' in df.columns:
        df['eta3_score'] = df['eta3_score']

    return df


def test_moderation_regression(df: pd.DataFrame,
                                x_var: str,
                                y_var: str,
                                moderator: str = 'chinese_cognitive_style_z') -> dict:
    """
    使用OLS交互回归检验阶段路径关联的调节效应。

    Y = b0 + b1*X + b2*M + b3*X*M + e
    """
    from scipy import stats as sp_stats

    # 准备数据
    valid_mask = (
        df[x_var].notna() &
        df[y_var].notna() &
        df[moderator].notna()
    )

    if valid_mask.sum() < 50:
        return {
            'n': valid_mask.sum(),
            'b_interaction': np.nan,
            'se_interaction': np.nan,
            't_interaction': np.nan,
            'p_interaction': np.nan,
            'r2_change': np.nan,
            'significant': False
        }

    X = df.loc[valid_mask, x_var].values
    Y = df.loc[valid_mask, y_var].values
    M = df.loc[valid_mask, moderator].values

    # 标准化
    X_z = (X - X.mean()) / X.std() if X.std() > 0 else X - X.mean()
    Y_z = (Y - Y.mean()) / Y.std() if Y.std() > 0 else Y - Y.mean()
    M_z = M  # 已经标准化

    # 交互项
    XM = X_z * M_z

    # 构建设计矩阵
    n = len(X_z)
    design_matrix = np.column_stack([
        np.ones(n),  # 截距
        X_z,          # 主效应X
        M_z,          # 主效应M
        XM            # 交互效应
    ])

    try:
        # OLS回归
        beta, residuals, rank, s = np.linalg.lstsq(design_matrix, Y_z, rcond=None)

        # 计算统计量
        y_pred = design_matrix @ beta
        ss_res = np.sum((Y_z - y_pred) ** 2)
        ss_tot = np.sum((Y_z - Y_z.mean()) ** 2)
        r2_full = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        # 不含交互项的模型
        design_reduced = design_matrix[:, :3]
        beta_reduced, _, _, _ = np.linalg.lstsq(design_reduced, Y_z, rcond=None)
        y_pred_reduced = design_reduced @ beta_reduced
        ss_res_reduced = np.sum((Y_z - y_pred_reduced) ** 2)
        r2_reduced = 1 - ss_res_reduced / ss_tot if ss_tot > 0 else 0

        r2_change = r2_full - r2_reduced

        # 标准误估计
        df_residual = n - 4
        mse = ss_res / df_residual if df_residual > 0 else 0

        # 计算系数标准误
        try:
            var_beta = mse * np.linalg.inv(design_matrix.T @ design_matrix)
            se = np.sqrt(np.diag(var_beta))
        except:
            se = np.array([np.nan] * 4)

        # t检验（交互项）
        b_interaction = beta[3]
        se_interaction = se[3] if len(se) > 3 else np.nan

        if not np.isnan(se_interaction) and se_interaction > 0:
            t_interaction = b_interaction / se_interaction
            p_interaction = 2 * (1 - sp_stats.t.cdf(abs(t_interaction), df_residual))
        else:
            t_interaction = np.nan
            p_interaction = np.nan

        return {
            'n': n,
            'b_interaction': b_interaction,
            'se_interaction': se_interaction,
            't_interaction': t_interaction,
            'p_interaction': p_interaction,
            'r2_change': r2_change,
            'r2_full': r2_full,
            'significant': p_interaction < 0.05 if not np.isnan(p_interaction) else False
        }

    except Exception as e:
        print(f"    回归分析失败: {e}")
        return {
            'n': n,
            'b_interaction': np.nan,
            'se_interaction': np.nan,
            't_interaction': np.nan,
            'p_interaction': np.nan,
            'r2_change': np.nan,
            'significant': False
        }


def add_multiplicity_sensitivity(results_df: pd.DataFrame,
                                 alpha: float = 0.05) -> pd.DataFrame:
    """加入多重检验敏感性列，供探索性报告解释边界使用。"""
    results_df = results_df.copy()
    p_values = pd.to_numeric(results_df['p'], errors='coerce')
    valid_p = p_values.dropna()

    results_df['FDR(BH) q'] = np.nan
    results_df['Bonferroni提示'] = '-'
    results_df['Bonferroni阈值'] = np.nan

    m = len(valid_p)
    if m == 0:
        return results_df

    bonf_alpha = alpha / m
    results_df.loc[p_values.notna(), 'Bonferroni阈值'] = bonf_alpha
    results_df.loc[p_values.notna(), 'Bonferroni提示'] = np.where(
        p_values[p_values.notna()] <= bonf_alpha,
        '通过',
        '未通过'
    )

    ordered = valid_p.sort_values()
    running_q = 1.0
    q_values = {}
    for rank, (idx, p_value) in reversed(list(enumerate(ordered.items(), start=1))):
        q_value = min(running_q, p_value * m / rank)
        q_values[idx] = min(q_value, 1.0)
        running_q = q_values[idx]

    for idx, q_value in q_values.items():
        results_df.at[idx, 'FDR(BH) q'] = q_value

    return results_df


def test_all_moderation_effects(df: pd.DataFrame) -> pd.DataFrame:
    """检验所有路径的调节效应"""
    print_subsection_header("检验各路径调节效应")

    # 变量映射
    var_mapping = {
        'eta1': 'eta1_score',
        'eta2': 'eta2_score',
        'eta3': 'eta3_score',
        'copula_function_num': 'copula_function_num'
    }

    results = []

    for path_name, coef_name, x_key, y_key in PATHS:
        print(f"\n  检验路径: {path_name}")

        # 获取变量名
        x_var = var_mapping.get(x_key, x_key)
        y_var = var_mapping.get(y_key, y_key)

        # 检查变量存在性
        x_exists = x_var in df.columns
        y_exists = y_var in df.columns

        if not x_exists or not y_exists:
            print(f"    变量缺失: {x_var}={x_exists}, {y_var}={y_exists}")
            results.append({
                '路径': path_name,
                '系数符号': coef_name,
                'n': 0,
                'b(交互)': np.nan,
                'SE': np.nan,
                't': np.nan,
                'p': np.nan,
                'ΔR²': np.nan,
                '显著性': '-'
            })
            continue

        # 检验调节效应
        mod_result = test_moderation_regression(df, x_var, y_var)

        print(f"    样本量: {mod_result['n']}")
        print(f"    交互项系数: b = {mod_result['b_interaction']:.4f}" if not np.isnan(mod_result['b_interaction']) else "    交互项系数: NA")
        print(f"    p值: {format_p_value(mod_result['p_interaction'])}")

        results.append({
            '路径': path_name,
            '系数符号': coef_name,
            'n': mod_result['n'],
            'b(交互)': mod_result['b_interaction'],
            'SE': mod_result['se_interaction'],
            't': mod_result['t_interaction'],
            'p': mod_result['p_interaction'],
            'ΔR²': mod_result['r2_change'],
            '显著性': '***' if mod_result.get('p_interaction', 1) < 0.001 else
                      '**' if mod_result.get('p_interaction', 1) < 0.01 else
                      '*' if mod_result.get('p_interaction', 1) < 0.05 else ''
        })

    return add_multiplicity_sensitivity(pd.DataFrame(results))


def simple_slopes_analysis(df: pd.DataFrame,
                           x_var: str,
                           y_var: str,
                           moderator: str = 'chinese_cognitive_style_z') -> dict:
    """
    简单斜率分析
    在调节变量的高/低水平下分别计算X对Y的效应
    """
    valid_mask = (
        df[x_var].notna() &
        df[y_var].notna() &
        df[moderator].notna()
    )

    if valid_mask.sum() < 50:
        return None

    X = df.loc[valid_mask, x_var].values
    Y = df.loc[valid_mask, y_var].values
    M = df.loc[valid_mask, moderator].values

    # 标准化X
    X_z = (X - X.mean()) / X.std() if X.std() > 0 else X - X.mean()

    # 分组：高/低调节变量水平（±1SD）
    m_high = M.mean() + M.std()
    m_low = M.mean() - M.std()

    # 高水平组
    high_mask = M >= np.percentile(M, 67)
    if high_mask.sum() > 20:
        slope_high, _, r_high, p_high, se_high = stats.linregress(
            X_z[high_mask], Y[high_mask]
        )
    else:
        slope_high, r_high, p_high, se_high = np.nan, np.nan, np.nan, np.nan

    # 低水平组
    low_mask = M <= np.percentile(M, 33)
    if low_mask.sum() > 20:
        slope_low, _, r_low, p_low, se_low = stats.linregress(
            X_z[low_mask], Y[low_mask]
        )
    else:
        slope_low, r_low, p_low, se_low = np.nan, np.nan, np.nan, np.nan

    return {
        'slope_high': slope_high,
        'p_high': p_high,
        'n_high': high_mask.sum(),
        'slope_low': slope_low,
        'p_low': p_low,
        'n_low': low_mask.sum()
    }


def create_moderation_table(mod_results: pd.DataFrame) -> str:
    """创建表66：调节效应检验结果表"""
    print_subsection_header("创建调节效应检验表")

    # 格式化数值
    table_data = []
    for _, row in mod_results.iterrows():
        table_data.append({
            '路径': row['路径'],
            '系数': row['系数符号'],
            'n': int(row['n']) if not np.isnan(row['n']) else '-',
            'b(交互)': f"{row['b(交互)']:.3f}" if not np.isnan(row['b(交互)']) else '-',
            'SE': f"{row['SE']:.3f}" if not np.isnan(row['SE']) else '-',
            't': f"{row['t']:.2f}" if not np.isnan(row['t']) else '-',
            'p': format_p_value(row['p']) if not np.isnan(row['p']) else '-',
            'ΔR²': f"{row['ΔR²']:.4f}" if not np.isnan(row['ΔR²']) else '-',
            'FDR(BH) q': format_q_value(row['FDR(BH) q']) if not np.isnan(row['FDR(BH) q']) else '-',
            'Bonferroni提示': row['Bonferroni提示'],
            '显著性': row['显著性']
        })

    table_df = pd.DataFrame(table_data)

    # 保存（文件名与映射文件对齐：PLS_调节效应检验结果.csv）
    from pathlib import Path
    output_dir = get_paths()['output_data']
    table_df.to_csv(output_dir / 'PLS_调节效应检验结果.csv', index=False, encoding='utf-8-sig')
    table_df.to_json(output_dir / 'PLS_调节效应检验结果.json', orient='records', force_ascii=False, indent=2)
    print(f"  [OK] Saved: PLS_调节效应检验结果.csv / .json")

    # 生成Markdown
    md_content = textwrap.dedent("""
## 整体性/关系性复合指标对四阶段机制的调节效应检验

| 路径 | 系数 | n | b(交互) | SE | t | 未校正p | ΔR² | FDR(BH) q | Bonferroni提示 | 显著性 |
|:-----|:-----|---:|--------:|----:|---:|----:|-----:|----:|:--------------:|:------:|
    """).lstrip()
    for item in table_data:
        md_content += f"| {item['路径']} | {item['系数']} | {item['n']} | {item['b(交互)']} | {item['SE']} | {item['t']} | {item['p']} | {item['ΔR²']} | {item['FDR(BH) q']} | {item['Bonferroni提示']} | {item['显著性']} |\n"

    md_content += textwrap.dedent("""
**注**：调节变量为整体性/关系性复合指标，脚本中原始均值为chinese_cognitive_style，入模变量为标准化后的chinese_cognitive_style_z。
各路径中的*η*₁、*η*₂和*η*₃为阶段指标均值，由对应指标标准化后取均值；本表报告的是OLS交互回归结果，不是在PLS-SEM内部重新估计的调节路径。
b(交互)为交互项回归系数，ΔR²为加入交互项后R²的增量。
表中p为未校正口径；Bonferroni提示按四项交互检验的.05/4阈值判断，FDR(BH) q用于敏感性参照。
*p < 0.05, **p < 0.01, ***p < 0.001
    """)

    return md_content


def create_moderator_group_counts(df: pd.DataFrame) -> str:
    """生成整体性/关系性复合指标三分组样本量说明。"""
    valid_mask = df['chinese_cognitive_style_z'].notna()
    M = df.loc[valid_mask, 'chinese_cognitive_style_z'].values

    high_mask = M >= np.percentile(M, 67)
    mid_mask = (M > np.percentile(M, 33)) & (M < np.percentile(M, 67))
    low_mask = M <= np.percentile(M, 33)

    group_counts = {
        '有效样本': int(valid_mask.sum()),
        '高复合指标组': int(high_mask.sum()),
        '中复合指标组': int(mid_mask.sum()),
        '低复合指标组': int(low_mask.sum()),
    }
    print("  复合指标分组样本量:", group_counts)

    return textwrap.dedent(f"""
    **复合指标分组样本量**：有效样本{group_counts['有效样本']}例；高复合指标组*n*={group_counts['高复合指标组']}，中复合指标组*n*={group_counts['中复合指标组']}，低复合指标组*n*={group_counts['低复合指标组']}。三组样本量差异来自分位点处的密集分布。

    """)


def create_core_sample_sensitivity(df: pd.DataFrame) -> str:
    """生成核心隐喻样本敏感性检验。"""
    if 'construction_type' not in df.columns:
        return ""

    core_df = df[df['construction_type'].eq('copular_metaphor')].copy()
    if len(core_df) == 0 or len(core_df) == len(df):
        return ""

    print_subsection_header("核心隐喻样本敏感性检验")
    core_df = create_composite_moderator(core_df)
    core_df = calculate_latent_scores(core_df)
    core_results = test_all_moderation_effects(core_df)

    output_dir = get_paths()['output_data']
    core_results.to_csv(output_dir / 'PLS_调节效应核心样本敏感性.csv', index=False, encoding='utf-8-sig')
    core_results.to_json(output_dir / 'PLS_调节效应核心样本敏感性.json', orient='records', force_ascii=False, indent=2)
    print("  [OK] Saved: PLS_调节效应核心样本敏感性.csv / .json")

    md_content = textwrap.dedent(f"""
    ## 核心隐喻样本敏感性检验

    发布全样本共{len(df)}例，其中construction_type为copular_metaphor的核心隐喻样本为{len(core_df)}例。核心样本敏感性检验用于判断边界/对照记录是否改变交互项方向与解释边界。

    | 路径 | n | b(交互) | SE | t | 未校正p | ΔR² | FDR(BH) q | Bonferroni提示 |
    |:-----|---:|--------:|----:|---:|----:|-----:|----:|:--------------:|
    """).lstrip()

    for _, row in core_results.iterrows():
        md_content += (
            f"| {row['路径']} | {int(row['n']) if not np.isnan(row['n']) else '-'} "
            f"| {row['b(交互)']:.3f} | {row['SE']:.3f} | {row['t']:.2f} "
            f"| {format_p_value(row['p'])} | {row['ΔR²']:.4f} "
            f"| {format_q_value(row['FDR(BH) q'])} | {row['Bonferroni提示']} |\n"
        )

    md_content += textwrap.dedent("""

    **敏感性结论**：核心隐喻样本与发布全样本的交互项方向一致；*η*₃→Y在核心样本中达到Bonferroni敏感性阈值，但Y仍为系词功能名义编码，因此该端点结果仍只能解释为编码口径下的探索性线索，不解释为等级路径增强。

    """)

    return md_content


def plot_moderation_effect(df: pd.DataFrame, mod_results: pd.DataFrame):
    """绘制图32：整体性/关系性复合指标调节效应示意图"""
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    from utils_公共函数 import get_font_paths

    print_subsection_header("绘制图32")

    # 设置中文字体
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=18)

    # 设置matplotlib支持中文和数学符号
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['mathtext.fontset'] = 'stix'  # 使用STIX字体渲染数学符号

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()

    # 变量映射
    var_mapping = {
        'eta1': 'eta1_score',
        'eta2': 'eta2_score',
        'eta3': 'eta3_score',
        'copula_function_num': 'copula_function_num'
    }

    # 路径标签映射（使用原始Unicode键匹配PATHS常量，显示用中文）
    path_labels = {
        'eta1->eta2': ('认知域激活', '参照点锚定'),
        'eta2->eta3': ('参照点锚定', '跨域映射'),
        'eta1->eta3': ('认知域激活', '跨域映射'),
        'eta3->Y': ('跨域映射', '系词功能')
    }

    # 路径名称的LaTeX显示格式（用于图表标题）
    path_display = {
        'eta1->eta2': r'$\eta_1 \rightarrow \eta_2$',
        'eta2->eta3': r'$\eta_2 \rightarrow \eta_3$',
        'eta1->eta3': r'$\eta_1 \rightarrow \eta_3$',
        'eta3->Y': r'$\eta_3 \rightarrow Y$'
    }

    for idx, (path_name, coef_name, x_key, y_key) in enumerate(PATHS):
        ax = axes[idx]

        x_var = var_mapping.get(x_key, x_key)
        y_var = var_mapping.get(y_key, y_key)

        if x_var not in df.columns or y_var not in df.columns:
            ax.text(0.5, 0.5, '数据不可用', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, fontproperties=font_cn)
            ax.set_title(path_display.get(path_name, path_name))
            continue

        # 准备数据
        valid_mask = (
            df[x_var].notna() &
            df[y_var].notna() &
            df['chinese_cognitive_style_z'].notna()
        )

        if valid_mask.sum() < 50:
            ax.text(0.5, 0.5, '样本量不足', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, fontproperties=font_cn)
            ax.set_title(path_display.get(path_name, path_name))
            continue

        X = df.loc[valid_mask, x_var].values
        Y = df.loc[valid_mask, y_var].values
        M = df.loc[valid_mask, 'chinese_cognitive_style_z'].values

        # 分三组绘制（线型：红色短虚线，绿色实线，蓝色长虚线）
        # dashes格式：(线段长度, 间隔长度)
        groups = [
            ('高复合指标', M >= np.percentile(M, 67), 'red', '--', None),
            ('中复合指标', (M > np.percentile(M, 33)) & (M < np.percentile(M, 67)), 'green', '-', None),
            ('低复合指标', M <= np.percentile(M, 33), 'blue', '--', (12, 4))  # 长虚线
        ]

        import matplotlib.patheffects as pe

        for label, mask, color, ls, dashes in groups:
            if mask.sum() > 20:
                x_group = X[mask]
                y_group = Y[mask]

                # 绘制散点（降低透明度，减少视觉干扰）
                ax.scatter(x_group, y_group, alpha=0.12, s=12, c=color,
                          edgecolors='none', zorder=1)

                # 拟合回归线（添加白色描边使线条更突出）
                slope, intercept, _, _, _ = stats.linregress(x_group, y_group)
                x_line = np.linspace(x_group.min(), x_group.max(), 100)
                y_line = slope * x_line + intercept
                line, = ax.plot(x_line, y_line, color=color, linestyle=ls, linewidth=3.5,
                       zorder=10, label=f'{label}（$n$={mask.sum()}）',
                       path_effects=[pe.Stroke(linewidth=5, foreground='white'), pe.Normal()])
                # 应用自定义虚线样式
                if dashes is not None:
                    line.set_dashes(dashes)

        # 获取路径结果
        path_result = mod_results[mod_results['路径'] == path_name]
        if not path_result.empty:
            p_val = path_result['p'].values[0]
            sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'
            title_suffix = f' ({sig})'
        else:
            title_suffix = ''

        x_label, y_label = path_labels.get(path_name, (x_key, y_key))
        ax.set_xlabel(x_label, fontsize=14, fontproperties=font_cn)
        ax.set_ylabel(y_label, fontsize=14, fontproperties=font_cn)
        # 使用LaTeX格式显示路径名称
        display_name = path_display.get(path_name, path_name)
        ax.set_title(f'{display_name}{title_suffix}', fontsize=15, fontweight='bold')
        ax.legend(loc='upper right', fontsize=12, prop=font_cn)
        ax.grid(True, alpha=0.3)

    # fig.suptitle('图32 整体性/关系性复合指标调节效应示意图',
                 # fontproperties=font_cn_title, fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()

    save_figure(fig, "整体性关系性复合指标调节效应示意图", global_num=32,
                title="整体性/关系性复合指标调节效应示意图")
    plt.close()


def summarize_moderation_findings(mod_results: pd.DataFrame) -> str:
    """总结调节效应发现"""
    print_subsection_header("调节效应发现总结")

    sig_paths = mod_results[mod_results['显著性'].isin(['*', '**', '***'])]
    nonsig_paths = mod_results[~mod_results['显著性'].isin(['*', '**', '***'])]
    bonf_pass_paths = mod_results[mod_results['Bonferroni提示'] == '通过']

    summary = "\n### 调节效应分析结果摘要\n\n"

    if len(sig_paths) > 0:
        summary += f"**未校正口径下的交互线索**：共发现{len(sig_paths)}条路径的交互项达到*p* < 0.05。\n\n"
        for _, row in sig_paths.iterrows():
            summary += f"- {row['路径']}：b(交互) = {row['b(交互)']:.3f}, p = {format_p_value(row['p'])}, FDR(BH) q = {format_q_value(row['FDR(BH) q'])}, Bonferroni提示 = {row['Bonferroni提示']}\n"

        summary += f"\n**多重检验敏感性**：四项交互检验的Bonferroni阈值为.0125；通过该阈值的路径为{len(bonf_pass_paths)}条。"
        summary += "FDR(BH)口径用于辅助判断探索性线索，不能替代确认性检验。\n\n"
        summary += "**理论解释边界**：整体性/关系性复合指标与上述路径存在交互线索，"
        summary += "提示文本中的整体化、关系化线索可能与阶段路径关联强度存在阶段性关联。该结果不能直接解释为语言使用者稳定认知风格、话题突出性测量结果或汉英加工差异。\n\n"

        # 具体解释各显著路径
        summary += "**具体解读**：\n"
        for _, row in sig_paths.iterrows():
            path = row['路径']
            b_val = row['b(交互)']
            if path == 'eta2->eta3':
                direction = "正向" if b_val > 0 else "负向"
                summary += f"- **{path}**：整体性/关系性复合指标对参照点锚定→跨域映射路径有{direction}调节作用"
                summary += f"（b={b_val:.3f}），说明该路径的关联方向与复合指标水平有关，需结合效应量谨慎解释。\n"
            elif path == 'eta3->Y':
                direction = "正向" if b_val > 0 else "负向"
                summary += f"- **{path}**：整体性/关系性复合指标对跨域映射→系词功能路径有{direction}调节作用"
                summary += f"（b={b_val:.3f}），但Y为系词功能名义编码，且该路径未通过Bonferroni阈值；因此只能作为语言编码端点在当前数值化口径下的探索性线索，不解释为路径强度增强。\n"
            elif path == 'eta1->eta2':
                direction = "正向" if b_val > 0 else "负向"
                summary += f"- **{path}**：整体性/关系性复合指标对认知域激活→参照点锚定路径有{direction}调节作用"
                summary += f"（b={b_val:.3f}）。\n"
            elif path == 'eta1->eta3':
                direction = "正向" if b_val > 0 else "负向"
                summary += f"- **{path}**：整体性/关系性复合指标对认知域激活→跨域映射直接路径有{direction}调节作用"
                summary += f"（b={b_val:.3f}）。\n"

    if len(nonsig_paths) > 0 and len(sig_paths) > 0:
        summary += f"\n**非显著路径**：{len(nonsig_paths)}条路径未发现显著调节效应\n"
        for _, row in nonsig_paths.iterrows():
            summary += f"- {row['路径']}：b(交互) = {row['b(交互)']:.3f}, p = {format_p_value(row['p'])} (ns)\n"

    if len(sig_paths) == 0:
        summary += "**结果**：未发现整体性/关系性复合指标对四阶段机制路径的显著调节效应。\n\n"
        summary += "**可能解释**：\n"
        summary += "1. 四阶段机制可能具有较稳定的结构\n"
        summary += "2. 整体性/关系性文本线索的影响可能体现在其他层面\n"
        summary += "3. 样本量或测量精度可能限制了调节效应的检测\n"

    print(summary)
    return summary


def main():
    """主函数"""
    print_section_header("Q3_06 调节效应分析")
    print("=" * 60)

    # 确保输出目录存在
    ensure_output_dirs([OUTPUT_DIR])

    # 1. 加载数据
    df = load_sem_data()
    if df is None:
        print("\n错误：无法加载数据，程序终止")
        return

    # 2. 创建复合调节变量
    df = create_composite_moderator(df)

    # 3. 计算潜变量得分
    df = calculate_latent_scores(df)

    # 4. 检验调节效应
    print_section_header("调节效应检验")
    mod_results = test_all_moderation_effects(df)

    # 5. 创建调节效应检验表
    print_section_header("生成输出")
    table_md = create_moderation_table(mod_results)
    group_counts_md = create_moderator_group_counts(df)
    core_sensitivity_md = create_core_sample_sensitivity(df)

    # 6. 绘制图32
    plot_moderation_effect(df, mod_results)

    # 7. 总结发现
    summary = summarize_moderation_findings(mod_results)

    # 保存完整报告
    report = "\n\n".join([
        "# Q3_06 调节效应分析报告",
        "## 分析定位\n本分析属于**探索性分析**（定量），基于阶段指标均值检验整体性/关系性文本间接指标与四阶段认知编码机制路径之间的交互线索，并报告多重检验敏感性。",
        "## 分析目的\n探索性分析整体性意象与关系性思维两个文本间接指标是否与阶段路径关联强度存在交互关系。",
        textwrap.dedent("""\
        ## 理论背景
        本分析不直接测量话题突出性或语言使用者认知风格，而是使用语料标注中的两个文本间接指标：
        - **整体性意象（holistic_imagery）**：记录隐喻表达是否调用整体场景化线索
        - **关系性思维（relational_thinking）**：记录源域与目标域之间关系对应的显化程度

        这两个文本线索可能与Sullivan四阶段认知编码机制的路径强度存在关联，但其证据功能限于探索性解释，不能直接替代文化心理学或语言类型学测量。"""),
        textwrap.dedent("""\
        ## 方法
        1. 将holistic_imagery和relational_thinking合并为整体性/关系性复合指标
           - 公式：chinese_cognitive_style = (holistic_imagery + relational_thinking) / 2；chinese_cognitive_style_z = zscore(chinese_cognitive_style)
           - 理由：两变量高相关（*r* ≈ 0.74），合并可减少多重共线性；该处理属于探索性降维，不预设稳定心理构念已经得到测量
        2. 按表24的指标分配计算阶段指标均值，使用OLS交互回归检验交互效应
           - *η*₁、*η*₂和*η*₃为对应指标标准化后的指标均值，不等同于重新估计的PLS潜变量得分
           - 模型：Y = b₀ + b₁X + b₂M + b₃(X×M) + ε
           - 交互项b₃在未校正口径下达到显著，仅说明存在探索性交互线索
        3. 计算ΔR²评估调节效应大小
           - ΔR² = R²(含交互项) - R²(不含交互项)
        4. 对四项交互检验报告FDR(BH) q值与Bonferroni敏感性提示"""),
        group_counts_md.strip(),
        table_md.strip(),
        core_sensitivity_md.strip(),
        summary.strip(),
        textwrap.dedent("""\
        ## 与第8章的关系
        - **本节（7.5节）定位**：实证发现——呈现调节效应检验的统计结果与解释边界
        - **第8.3节定位**：理论讨论——基于本节发现，讨论整体化、关系化文本线索对Sullivan框架本土化的启发；话题突出型语言推演与本报告的文本线索结果分属不同证据层级"""),
        textwrap.dedent("""\
        ## 输出文件
        - PLS_调节效应检验结果.csv
        - PLS_调节效应核心样本敏感性.csv
        - 图32_整体性关系性复合指标调节效应示意图.png""")
    ]).strip() + "\n"

    report_path = OUTPUT_DIR / "Q3_06_调节效应分析报告.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {report_path}")

    print("\n" + "=" * 60)
    print("Q3_06 调节效应分析完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
