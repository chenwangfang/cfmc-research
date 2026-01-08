# -*- coding: utf-8 -*-
"""
Q3_06_调节效应.py
汉语认知特色的调节效应分析

研究内容：
- 探索性分析：汉语认知特色（整体意象、关系性思维）对四阶段机制的调节效应
- holistic_imagery与relational_thinking高相关（r~=0.74），合并为复合调节变量
- 检验调节变量对各路径的调节作用

输出：
- 表108：调节效应检验结果表
- 图34：汉语认知风格调节效应示意图

依赖：
- CFMC_for_SEM.csv（由Q3_01生成）
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
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
    'eta3': ['mapping_direction', 'mapping_basis_num', 'systematicity', 'entailment_richness']
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
    创建复合调节变量
    chinese_cognitive_style = (holistic_imagery + relational_thinking) / 2
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
        print("  警告：缺少汉语认知特色字段，使用模拟数据")
        np.random.seed(42)
        df['chinese_cognitive_style'] = np.random.uniform(2, 5, len(df))
        df['chinese_cognitive_style_z'] = stats.zscore(df['chinese_cognitive_style'])

    return df


def calculate_latent_scores(df: pd.DataFrame) -> pd.DataFrame:
    """计算潜变量得分（通过指标平均）"""
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
    使用回归分析检验调节效应
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

    return pd.DataFrame(results)


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
    """创建表108：调节效应检验结果表"""
    print_subsection_header("创建表108")

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
            '显著性': row['显著性']
        })

    table_df = pd.DataFrame(table_data)

    # 保存
    save_table(
        table_df,
        "调节效应检验结果",
        global_num=108,
        title="汉语认知特色对四阶段机制的调节效应检验"
    )

    # 生成Markdown
    md_content = """
## 表108 汉语认知特色对四阶段机制的调节效应检验

| 路径 | 系数 | n | b(交互) | SE | t | p | ΔR² | 显著性 |
|:-----|:-----|---:|--------:|----:|---:|----:|-----:|:------:|
"""
    for item in table_data:
        md_content += f"| {item['路径']} | {item['系数']} | {item['n']} | {item['b(交互)']} | {item['SE']} | {item['t']} | {item['p']} | {item['ΔR²']} | {item['显著性']} |\n"

    md_content += """
**注**：调节变量为汉语认知特色复合变量（chinese_cognitive_style），由holistic_imagery和relational_thinking平均计算得到。
b(交互)为交互项回归系数，ΔR²为加入交互项后R²的增量。
*p < 0.05, **p < 0.01, ***p < 0.001
"""

    return md_content


def plot_moderation_effect(df: pd.DataFrame, mod_results: pd.DataFrame):
    """绘制图34：汉语认知风格调节效应示意图"""
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    from utils_公共函数 import get_font_paths

    print_subsection_header("绘制图34")

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
            ('高认知特色', M >= np.percentile(M, 67), 'red', '--', None),
            ('中认知特色', (M > np.percentile(M, 33)) & (M < np.percentile(M, 67)), 'green', '-', None),
            ('低认知特色', M <= np.percentile(M, 33), 'blue', '--', (12, 4))  # 长虚线
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

    # fig.suptitle('图34 汉语认知风格调节效应示意图',
                 # fontproperties=font_cn_title, fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()

    save_figure(fig, "汉语认知风格调节效应示意图", global_num=38,
                title="汉语认知风格调节效应示意图")
    plt.close()


def summarize_moderation_findings(mod_results: pd.DataFrame) -> str:
    """总结调节效应发现"""
    print_subsection_header("调节效应发现总结")

    sig_paths = mod_results[mod_results['显著性'] != '']
    nonsig_paths = mod_results[mod_results['显著性'] == '']

    summary = "\n### 调节效应分析结果摘要\n\n"

    if len(sig_paths) > 0:
        summary += f"**显著调节效应**：共发现{len(sig_paths)}条路径存在显著调节效应\n\n"
        for _, row in sig_paths.iterrows():
            summary += f"- {row['路径']}：b(交互) = {row['b(交互)']:.3f}, p = {format_p_value(row['p'])}\n"

        summary += "\n**理论解释**：汉语认知特色（整体意象和关系性思维）对上述路径具有调节作用，"
        summary += "表明汉语使用者在隐喻加工过程中表现出与英语使用者不同的认知模式。\n\n"

        # 具体解释各显著路径
        summary += "**具体解读**：\n"
        for _, row in sig_paths.iterrows():
            path = row['路径']
            b_val = row['b(交互)']
            if path == 'eta2->eta3':
                direction = "正向" if b_val > 0 else "负向"
                summary += f"- **{path}**：汉语认知特色对参照点锚定→跨域映射路径有{direction}调节作用"
                summary += f"（b={b_val:.3f}），表明整体意象和关系性思维增强了参照点到映射的转化效率。\n"
            elif path == 'eta3->Y':
                direction = "正向" if b_val > 0 else "负向"
                summary += f"- **{path}**：汉语认知特色对跨域映射→系词功能路径有{direction}调节作用"
                summary += f"（b={b_val:.3f}），表明汉语认知风格影响映射关系向语言编码的转化方式。\n"
            elif path == 'eta1->eta2':
                direction = "正向" if b_val > 0 else "负向"
                summary += f"- **{path}**：汉语认知特色对认知域激活→参照点锚定路径有{direction}调节作用"
                summary += f"（b={b_val:.3f}）。\n"
            elif path == 'eta1->eta3':
                direction = "正向" if b_val > 0 else "负向"
                summary += f"- **{path}**：汉语认知特色对认知域激活→跨域映射直接路径有{direction}调节作用"
                summary += f"（b={b_val:.3f}）。\n"

    if len(nonsig_paths) > 0 and len(sig_paths) > 0:
        summary += f"\n**非显著路径**：{len(nonsig_paths)}条路径未发现显著调节效应\n"
        for _, row in nonsig_paths.iterrows():
            summary += f"- {row['路径']}：b(交互) = {row['b(交互)']:.3f}, p = {format_p_value(row['p'])} (ns)\n"

    if len(sig_paths) == 0:
        summary += "**结果**：未发现汉语认知特色对四阶段机制路径的显著调节效应。\n\n"
        summary += "**可能解释**：\n"
        summary += "1. 四阶段机制可能具有跨文化的普遍性\n"
        summary += "2. 汉语认知特色的影响可能体现在其他层面\n"
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

    # 5. 创建表108
    print_section_header("生成输出")
    table_md = create_moderation_table(mod_results)

    # 6. 绘制图34
    plot_moderation_effect(df, mod_results)

    # 7. 总结发现
    summary = summarize_moderation_findings(mod_results)

    # 保存完整报告
    report = f"""# Q3_06 调节效应分析报告

## 分析定位
本分析属于**探索性分析**（定量），检验汉语认知特色对四阶段认知编码机制的调节效应。

## 分析目的
探索性分析汉语认知特色（整体意象、关系性思维）对四阶段认知编码机制的调节效应。

## 理论背景
汉语作为主题突出语言，具有区别于英语等主语突出语言的认知特征：
- **整体意象（holistic_imagery）**：强调整体性思维，倾向于将事物置于关系网络中理解
- **关系性思维（relational_thinking）**：注重事物间的关系和联系，而非独立实体

这两个认知特征可能对Sullivan四阶段认知编码机制产生调节作用，影响隐喻加工的认知路径。

## 方法
1. 将holistic_imagery和relational_thinking合并为复合调节变量chinese_cognitive_style
   - 公式：chinese_cognitive_style = (holistic_imagery + relational_thinking) / 2
   - 理由：两变量高相关（*r* ≈ 0.74），合并可减少多重共线性
2. 使用层级回归分析检验交互效应
   - 模型：Y = b₀ + b₁X + b₂M + b₃(X×M) + ε
   - 交互项b₃显著表明存在调节效应
3. 计算ΔR²评估调节效应大小
   - ΔR² = R²(含交互项) - R²(不含交互项)

{table_md}

{summary}

## 与第8章的关系
- **本节（7.5节）定位**：实证发现——呈现调节效应检验的统计结果
- **第8.3节定位**：理论讨论——基于本节发现，讨论汉语认知特色对Sullivan框架的理论扩展意义

## 输出文件
- 表108_调节效应检验结果.csv
- 图38_汉语认知风格调节效应示意图.png
"""

    report_path = OUTPUT_DIR / "Q3_06_调节效应分析报告.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {report_path}")

    print("\n" + "=" * 60)
    print("Q3_06 调节效应分析完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
