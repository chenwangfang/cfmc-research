#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils_公共函数.py
================
汉语系表隐喻构式统计分析——公共函数模块

功能：提供所有脚本共用的工具函数
创建日期：2025-12-05
数据来源：CFMC_5989.json（5,989条有效语料）
"""

import os
import sys
import json
import platform
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams

# 忽略一些常见警告
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


# =============================================================================
# 路径管理
# =============================================================================

def get_paths() -> Dict[str, Path]:
    """
    获取系统路径（WSL/Windows兼容）

    Returns
    -------
    Dict[str, Path]
        包含以下键的字典：
        - 'base': 统计分析根目录
        - 'input': 语料输入目录
        - 'output_data': 数据输出目录
        - 'output_figures': 图表输出目录
        - 'scripts': 脚本目录
        - 'data_file': 主数据文件路径
    """
    # 检测系统环境
    is_wsl = 'microsoft' in platform.uname().release.lower()
    is_windows = platform.system() == 'Windows'

    if is_wsl or not is_windows:
        # WSL或Linux环境
        base_path = Path('/home/tomja/projects/博士毕业论文/大论文/论文撰写/统计分析')
    else:
        # Windows环境
        base_path = Path('/home/tomja/projects/博士毕业论文/大论文/论文撰写/统计分析')

    paths = {
        'base': base_path,
        'input': base_path / '语料_输入',
        'output_data': base_path / '结果_输出' / 'Data',
        'output_figures': base_path / '结果_输出' / 'Figures',
        'scripts': base_path / '脚本',
        'data_file': base_path / '语料_输入' / 'CFMC_5989.json'
    }

    # 确保输出目录存在
    paths['output_data'].mkdir(parents=True, exist_ok=True)
    paths['output_figures'].mkdir(parents=True, exist_ok=True)

    return paths


def get_font_paths() -> Dict[str, str]:
    """
    获取字体路径（WSL/Windows兼容）

    Returns
    -------
    Dict[str, str]
        包含中文和英文字体路径的字典
    """
    is_wsl = 'microsoft' in platform.uname().release.lower()
    is_windows = platform.system() == 'Windows'

    if is_wsl:
        # WSL环境 - 使用Windows字体
        font_paths = {
            'chinese': '/mnt/c/Windows/Fonts/simhei.ttf',      # 黑体
            'chinese_song': '/mnt/c/Windows/Fonts/simsun.ttc', # 宋体
            'english': '/mnt/c/Windows/Fonts/times.ttf',       # Times New Roman
            'english_arial': '/mnt/c/Windows/Fonts/arial.ttf'  # Arial
        }
    elif is_windows:
        # Windows环境
        font_paths = {
            'chinese': 'C:/Windows/Fonts/simhei.ttf',
            'chinese_song': 'C:/Windows/Fonts/simsun.ttc',
            'english': 'C:/Windows/Fonts/times.ttf',
            'english_arial': 'C:/Windows/Fonts/arial.ttf'
        }
    else:
        # Linux环境 - 使用系统字体
        font_paths = {
            'chinese': '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            'chinese_song': '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            'english': '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
            'english_arial': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        }

    return font_paths


# =============================================================================
# 数据加载
# =============================================================================

def load_cfmc_data(file_path: Optional[Union[str, Path]] = None,
                    convert_types: bool = True) -> Tuple[pd.DataFrame, Dict]:
    """
    加载CFMC-33 JSON数据

    Parameters
    ----------
    file_path : str or Path, optional
        数据文件路径，默认使用get_paths()获取
    convert_types : bool, optional
        是否自动转换整数字段类型，默认True

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        (构式数据DataFrame, 元数据字典)
    """
    if file_path is None:
        file_path = get_paths()['data_file']

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"数据文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取元数据
    metadata = data.get('metadata', {})
    field_definitions = data.get('field_definitions', {})
    field_types = data.get('field_types', {})

    # 转换为DataFrame
    df = pd.DataFrame(data['constructions'])

    # 设置id为索引（保留为列）
    if 'id' in df.columns:
        df.set_index('id', drop=False, inplace=True)

    # 自动转换整数字段类型（解决JSON中int存储为float的问题）
    if convert_types:
        int_fields = [
            'mapping_direction',
            'cognitive_accessibility',
            'conceptual_complexity',
            'prototype_distance',
            'link_type',
            'function_in_network'
        ]
        for field in int_fields:
            if field in df.columns:
                # 保留NaN，其他转为整数
                df[field] = pd.to_numeric(df[field], errors='coerce')
                # 使用Int64以支持NaN
                df[field] = df[field].astype('Int64')

    meta = {
        'metadata': metadata,
        'field_definitions': field_definitions,
        'field_types': field_types,
        'n_constructions': len(df)
    }

    print(f"[OK] 已加载 {len(df)} 条构式数据")
    if convert_types:
        print(f"  → 已自动转换整数字段类型")

    return df, meta


def prepare_sem_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    准备SEM分析数据

    对分类变量进行PCA降维，对copula_function进行重编码

    Parameters
    ----------
    df : pd.DataFrame
        原始构式数据

    Returns
    -------
    pd.DataFrame
        SEM就绪数据集
    """
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.decomposition import PCA

    sem_df = df.copy()

    # 1. copula_function重编码: equative=1, attributive=2, identificational=3
    copula_mapping = {
        'equative': 1,
        'attributive': 2,
        'identificational': 3
    }
    if 'copula_function' in sem_df.columns:
        sem_df['copula_function_coded'] = sem_df['copula_function'].map(copula_mapping)

    # 2. 分类变量PCA降维
    categorical_vars = ['source_domain', 'target_domain', 'mapping_basis']

    for var in categorical_vars:
        if var in sem_df.columns:
            # 虚拟编码
            dummies = pd.get_dummies(sem_df[var], prefix=var)

            # 标准化
            scaler = StandardScaler()
            dummies_scaled = scaler.fit_transform(dummies)

            # PCA取第一主成分
            pca = PCA(n_components=1)
            pc1 = pca.fit_transform(dummies_scaled)
            sem_df[f'{var}_pc1'] = pc1.flatten()

            print(f"  {var}: 解释方差比例 = {pca.explained_variance_ratio_[0]:.3f}")

    # 3. 创建汉语认知特色复合变量
    if 'holistic_imagery' in sem_df.columns and 'relational_thinking' in sem_df.columns:
        sem_df['chinese_cognitive_style'] = (
            sem_df['holistic_imagery'] + sem_df['relational_thinking']
        ) / 2

    print(f"[OK] SEM数据准备完成")

    return sem_df


# =============================================================================
# 字体设置
# =============================================================================

def setup_chinese_font(font_type: str = 'chinese') -> fm.FontProperties:
    """
    设置中文字体

    Parameters
    ----------
    font_type : str
        字体类型: 'chinese'(黑体), 'chinese_song'(宋体),
                  'english', 'english_arial'

    Returns
    -------
    FontProperties
        字体属性对象
    """
    font_paths = get_font_paths()
    font_path = font_paths.get(font_type, font_paths['chinese'])

    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
    else:
        # 回退到系统默认
        print(f"警告: 字体文件不存在 {font_path}，使用系统默认字体")
        font_prop = fm.FontProperties()

    return font_prop


def setup_matplotlib_chinese():
    """
    全局设置matplotlib中文显示
    """
    font_paths = get_font_paths()

    # 清除字体缓存
    fm._load_fontmanager(try_read_cache=False)

    # 设置中文字体
    if os.path.exists(font_paths['chinese']):
        rcParams['font.family'] = ['sans-serif']
        rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        # 添加字体路径
        font_dir = os.path.dirname(font_paths['chinese'])
        if font_dir not in rcParams['font.sans-serif']:
            fm.fontManager.addfont(font_paths['chinese'])

    # 解决负号显示问题
    rcParams['axes.unicode_minus'] = False

    # 设置默认图表样式
    rcParams['figure.dpi'] = 150
    rcParams['savefig.dpi'] = 300
    rcParams['figure.figsize'] = [10, 6]

    print("[OK] Matplotlib中文显示已配置")


# =============================================================================
# 图表保存
# =============================================================================

def save_figure(fig: plt.Figure,
                filename: str,
                global_num: int,
                title: str = "",
                dpi: int = 300,
                formats: List[str] = ['png']) -> List[Path]:
    """
    保存图表并清除缓存

    Parameters
    ----------
    fig : Figure
        matplotlib图表对象
    filename : str
        文件名（不含扩展名）
    global_num : int
        全局图表编号（如12表示图12）
    title : str, optional
        图表标题（用于日志）
    dpi : int
        分辨率，默认300
    formats : List[str]
        输出格式列表，默认['png', 'pdf']

    Returns
    -------
    List[Path]
        保存的文件路径列表
    """
    paths = get_paths()
    output_dir = paths['output_figures']

    # 构建文件名：图N_描述
    fig_id = f"图{global_num}"

    saved_paths = []
    for fmt in formats:
        file_path = output_dir / f"{fig_id}_{filename}.{fmt}"
        fig.savefig(file_path, dpi=dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        saved_paths.append(file_path)

    # 清除缓存避免图像重叠
    plt.close(fig)
    plt.clf()

    print(f"[OK] 已保存 {fig_id}: {title or filename}")
    for p in saved_paths:
        print(f"  → {p}")

    return saved_paths


def save_table(data: Union[pd.DataFrame, Dict, List],
               filename: str,
               global_num: int,
               title: str = "",
               formats: List[str] = ['csv', 'json']) -> List[Path]:
    """
    保存数据表格

    Parameters
    ----------
    data : DataFrame, Dict, or List
        要保存的数据
    filename : str
        文件名（不含扩展名）
    global_num : int
        全局表格编号（如58表示表58）
    title : str, optional
        表格标题（用于日志）
    formats : List[str]
        输出格式列表，默认['csv', 'json']

    Returns
    -------
    List[Path]
        保存的文件路径列表
    """
    paths = get_paths()
    output_dir = paths['output_data']

    # 构建文件名：表N_描述
    table_id = f"表{global_num}"

    # 转换为DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data

    saved_paths = []
    for fmt in formats:
        file_path = output_dir / f"{table_id}_{filename}.{fmt}"

        if fmt == 'csv':
            df.to_csv(file_path, index=True, encoding='utf-8-sig')
        elif fmt == 'json':
            df.to_json(file_path, orient='records', force_ascii=False, indent=2)
        elif fmt == 'xlsx':
            df.to_excel(file_path, index=True)

        saved_paths.append(file_path)

    print(f"[OK] 已保存 {table_id}: {title or filename}")
    for p in saved_paths:
        print(f"  → {p}")

    return saved_paths


# =============================================================================
# 图表标签修复辅助函数
# =============================================================================

def fix_axis_labels(ax, ylabel_rotation: int = 0, xlabel_rotation: int = 0):
    """
    修复坐标轴标签旋转问题，确保标签水平显示

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        要修复的坐标轴对象
    ylabel_rotation : int
        Y轴标签旋转角度，默认0（水平）
    xlabel_rotation : int
        X轴标签旋转角度，默认0（水平）
    """
    # 修复Y轴标签
    if ax.get_ylabel():
        ax.yaxis.label.set_rotation(ylabel_rotation)
        ax.yaxis.label.set_ha('right')
        ax.yaxis.label.set_va('center')

    # 修复X轴标签
    if ax.get_xlabel():
        ax.xaxis.label.set_rotation(xlabel_rotation)


def fix_colorbar_label(cbar, rotation: int = 0):
    """
    修复Colorbar标签旋转问题

    Parameters
    ----------
    cbar : matplotlib.colorbar.Colorbar
        Colorbar对象
    rotation : int
        旋转角度，默认0（水平）
    """
    if cbar.ax.get_ylabel():
        cbar.ax.yaxis.label.set_rotation(rotation)
        cbar.ax.yaxis.label.set_ha('right')
        cbar.ax.yaxis.label.set_va('center')


def safe_unicode_text(text: str) -> str:
    """
    将可能导致乱码的Unicode符号替换为matplotlib安全的符号

    Parameters
    ----------
    text : str
        原始文本

    Returns
    -------
    str
        替换后的安全文本
    """
    replacements = {
        '✓': '[OK]',      # 勾号 → [OK]
        '✗': '[X]',       # 叉号 → [X]
        '²': '^2',        # 上标2 → ^2
        '₁': '_1',        # 下标1
        '₂': '_2',        # 下标2
        '₃': '_3',        # 下标3
        'η': 'eta',       # 希腊字母eta → eta
        'β': 'beta',      # 希腊字母beta → beta
        'γ': 'gamma',     # 希腊字母gamma → gamma
        'χ': 'chi',       # 希腊字母chi → chi
    }

    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)

    return result


def get_safe_greek_labels() -> Dict[str, str]:
    """
    获取希腊字母的matplotlib安全LaTeX表示

    Returns
    -------
    Dict[str, str]
        希腊字母及其LaTeX表示的映射
    """
    return {
        'eta1': r'$\eta_1$',
        'eta2': r'$\eta_2$',
        'eta3': r'$\eta_3$',
        'beta': r'$\beta$',
        'gamma': r'$\gamma$',
        'chi2': r'$\chi^2$',
        'R2': r'$R^2$',
    }


# =============================================================================
# 统计格式化
# =============================================================================

def format_stats(stat_name: str,
                 value: float,
                 p_value: Optional[float] = None,
                 df: Optional[Union[int, Tuple[int, int]]] = None,
                 ci: Optional[Tuple[float, float]] = None) -> str:
    """
    格式化统计结果（APA格式）

    Parameters
    ----------
    stat_name : str
        统计量名称: 'r', 't', 'F', 'chi2', 'beta', 'CFI', 'RMSEA'等
    value : float
        统计量值
    p_value : float, optional
        p值
    df : int or tuple, optional
        自由度（F检验需要两个值）
    ci : tuple, optional
        置信区间 (lower, upper)

    Returns
    -------
    str
        格式化的统计结果字符串
    """
    # 格式化统计量
    if stat_name in ['r', 'beta', 'CFI', 'TLI', 'RMSEA', 'SRMR']:
        stat_str = f"*{stat_name}* = {value:.3f}"
    elif stat_name in ['t', 'z']:
        if df is not None:
            stat_str = f"*{stat_name}*({df}) = {value:.2f}"
        else:
            stat_str = f"*{stat_name}* = {value:.2f}"
    elif stat_name == 'F':
        if df is not None and isinstance(df, tuple):
            stat_str = f"*F*({df[0]}, {df[1]}) = {value:.2f}"
        else:
            stat_str = f"*F* = {value:.2f}"
    elif stat_name == 'chi2':
        if df is not None:
            stat_str = f"χ²({df}) = {value:.2f}"
        else:
            stat_str = f"χ² = {value:.2f}"
    else:
        stat_str = f"{stat_name} = {value:.3f}"

    # 添加p值
    if p_value is not None:
        if p_value < 0.001:
            stat_str += ", *p* < 0.001"
        elif p_value < 0.01:
            stat_str += f", *p* < 0.01"
        elif p_value < 0.05:
            stat_str += f", *p* < 0.05"
        else:
            stat_str += f", *p* = {p_value:.3f}"

    # 添加置信区间
    if ci is not None:
        stat_str += f", 95% CI [{ci[0]:.3f}, {ci[1]:.3f}]"

    return stat_str


def format_correlation_matrix(corr_matrix: pd.DataFrame,
                              p_matrix: Optional[pd.DataFrame] = None,
                              decimals: int = 3) -> pd.DataFrame:
    """
    格式化相关矩阵（带显著性标记）

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        相关系数矩阵
    p_matrix : pd.DataFrame, optional
        p值矩阵
    decimals : int
        小数位数

    Returns
    -------
    pd.DataFrame
        格式化后的相关矩阵
    """
    formatted = corr_matrix.round(decimals).astype(str)

    if p_matrix is not None:
        for i in range(len(corr_matrix)):
            for j in range(len(corr_matrix.columns)):
                p = p_matrix.iloc[i, j]
                r = corr_matrix.iloc[i, j]

                if i == j:
                    formatted.iloc[i, j] = "—"
                elif p < 0.001:
                    formatted.iloc[i, j] = f"{r:.{decimals}f}***"
                elif p < 0.01:
                    formatted.iloc[i, j] = f"{r:.{decimals}f}**"
                elif p < 0.05:
                    formatted.iloc[i, j] = f"{r:.{decimals}f}*"

    return formatted


# =============================================================================
# 诊断检验
# =============================================================================

def check_vif(X: pd.DataFrame, threshold: float = 5.0) -> pd.DataFrame:
    """
    VIF多重共线性检验

    Parameters
    ----------
    X : pd.DataFrame
        自变量数据框
    threshold : float
        VIF阈值，默认5.0（>5警告，>10严重）

    Returns
    -------
    pd.DataFrame
        VIF检验结果
    """
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    # 移除常数项和缺失值
    X_clean = X.dropna().select_dtypes(include=[np.number])

    vif_data = []
    for i, col in enumerate(X_clean.columns):
        vif = variance_inflation_factor(X_clean.values, i)
        status = "正常" if vif < threshold else ("警告" if vif < 10 else "严重")
        vif_data.append({
            '变量': col,
            'VIF': round(vif, 3),
            '状态': status
        })

    vif_df = pd.DataFrame(vif_data)

    # 打印警告
    warnings_df = vif_df[vif_df['VIF'] >= threshold]
    if len(warnings_df) > 0:
        print(f"[WARN] VIF警告: 以下变量存在多重共线性问题")
        print(warnings_df.to_string(index=False))
    else:
        print(f"[OK] VIF检验通过: 所有变量VIF < {threshold}")

    return vif_df


def check_normality(data: Union[pd.Series, np.ndarray],
                    var_name: str = "变量") -> Dict:
    """
    正态性检验（Shapiro-Wilk + Kolmogorov-Smirnov）

    Parameters
    ----------
    data : Series or array
        数据
    var_name : str
        变量名称

    Returns
    -------
    Dict
        检验结果
    """
    from scipy import stats

    data_clean = pd.Series(data).dropna()
    n = len(data_clean)

    results = {
        '变量': var_name,
        'N': n,
        '均值': data_clean.mean(),
        '标准差': data_clean.std(),
        '偏度': stats.skew(data_clean),
        '峰度': stats.kurtosis(data_clean)
    }

    # Shapiro-Wilk检验（n < 5000）
    if n < 5000:
        sw_stat, sw_p = stats.shapiro(data_clean)
        results['Shapiro-Wilk W'] = sw_stat
        results['Shapiro-Wilk p'] = sw_p

    # Kolmogorov-Smirnov检验
    ks_stat, ks_p = stats.kstest(data_clean, 'norm',
                                  args=(data_clean.mean(), data_clean.std()))
    results['K-S D'] = ks_stat
    results['K-S p'] = ks_p

    return results


# =============================================================================
# 效果量计算
# =============================================================================

def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """
    计算Cohen's d效果量

    Parameters
    ----------
    group1, group2 : array
        两组数据

    Returns
    -------
    float
        Cohen's d值
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # 池化标准差
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    d = (np.mean(group1) - np.mean(group2)) / pooled_std

    return d


def eta_squared(f_stat: float, df_between: int, df_within: int) -> float:
    """
    计算η²效果量（ANOVA）

    Parameters
    ----------
    f_stat : float
        F统计量
    df_between : int
        组间自由度
    df_within : int
        组内自由度

    Returns
    -------
    float
        η²值
    """
    eta2 = (f_stat * df_between) / (f_stat * df_between + df_within)
    return eta2


def interpret_effect_size(value: float, metric: str = 'd') -> str:
    """
    解释效果量大小

    Parameters
    ----------
    value : float
        效果量值
    metric : str
        效果量类型: 'd'(Cohen's d), 'r'(相关), 'eta2'(η²)

    Returns
    -------
    str
        效果量解释
    """
    value = abs(value)

    if metric == 'd':
        if value < 0.2:
            return "微小"
        elif value < 0.5:
            return "小"
        elif value < 0.8:
            return "中等"
        else:
            return "大"
    elif metric == 'r':
        if value < 0.1:
            return "微小"
        elif value < 0.3:
            return "小"
        elif value < 0.5:
            return "中等"
        else:
            return "大"
    elif metric == 'eta2':
        if value < 0.01:
            return "微小"
        elif value < 0.06:
            return "小"
        elif value < 0.14:
            return "中等"
        else:
            return "大"

    return "未知"


# =============================================================================
# 归并函数
# =============================================================================

def bin_accessibility(value: float) -> str:
    """
    将5级认知通达度归并为3级

    根据CFMC-33定义：1=最难, 5=最易
    归并规则：1-2级=低通达, 3级=中通达, 4-5级=高通达

    Parameters
    ----------
    value : float
        认知通达度原始值（1-5）

    Returns
    -------
    str
        归并后的等级标签：'低'、'中'、'高'
    """
    if pd.isna(value):
        return np.nan
    value = float(value)
    if value <= 2:
        return '低'
    elif value <= 3:
        return '中'
    else:
        return '高'


def bin_complexity(value: float) -> str:
    """
    将5级概念复杂度归并为3级

    归并规则：1-2级=低, 3级=中, 4-5级=高

    Parameters
    ----------
    value : float
        概念复杂度原始值（1-5）

    Returns
    -------
    str
        归并后的等级标签：'低'、'中'、'高'
    """
    if pd.isna(value):
        return np.nan
    value = float(value)
    if value <= 2:
        return '低'
    elif value <= 3:
        return '中'
    else:
        return '高'


def convert_int_fields(df: pd.DataFrame, fields: Optional[List[str]] = None) -> pd.DataFrame:
    """
    将JSON中声明为int但存储为float的字段转换为整数

    Parameters
    ----------
    df : pd.DataFrame
        数据框
    fields : List[str], optional
        要转换的字段列表，默认使用INT_FIELDS

    Returns
    -------
    pd.DataFrame
        转换后的数据框
    """
    if fields is None:
        fields = [
            'mapping_direction',
            'cognitive_accessibility',
            'conceptual_complexity',
            'prototype_distance',
            'link_type',
            'function_in_network'
        ]

    df_converted = df.copy()

    for field in fields:
        if field in df_converted.columns:
            # 保留NaN，其他转为整数
            df_converted[field] = pd.to_numeric(df_converted[field], errors='coerce')
            # 对于非NaN值转为整数（使用Int64以支持NaN）
            df_converted[field] = df_converted[field].astype('Int64')

    return df_converted


def get_construction_type_12(ca_value: float, md_value: float) -> str:
    """
    根据认知通达度和映射方向生成12类构式标签

    Parameters
    ----------
    ca_value : float
        认知通达度（1-5）
    md_value : float
        映射方向（1-4）

    Returns
    -------
    str
        12类构式标签，如'高_具抽'
    """
    ca_level = bin_accessibility(ca_value)
    md_short = {1: '具具', 2: '具抽', 3: '抽抽', 4: '抽具'}
    md_label = md_short.get(int(md_value), '未知')

    if pd.isna(ca_level) or md_label == '未知':
        return np.nan

    return f"{ca_level}_{md_label}"


# =============================================================================
# 常用常量
# =============================================================================

# 域编码（25类，源域和目标域共享）
# 验证日期：2026-02-01
# 说明：实际数据中源域和目标域可以交叉使用，故合并为统一编码
DOMAIN_CODES = {
    # 原SOURCE_DOMAIN典型类别（15类）
    'SP': '空间', 'MV': '运动', 'OB': '物体', 'LV': '生命', 'BD': '身体',
    'SN': '感知', 'FC': '力量', 'NT': '自然', 'HM': '人类活动', 'WR': '战争',
    'EC': '经济', 'TR': '旅行', 'FD': '食物', 'MC': '机器', 'GM': '游戏',
    # 原TARGET_DOMAIN典型类别（10类）
    'TM': '时间', 'LF': '人生', 'EM': '情感', 'TH': '思维', 'SC': '社会',
    'MR': '道德', 'AB': '抽象', 'CM': '语言', 'ST': '状态', 'EV': '事件'
}

# 向后兼容别名（保留原常量名供旧代码使用）
SOURCE_DOMAIN_CODES = DOMAIN_CODES  # 别名，向后兼容
TARGET_DOMAIN_CODES = DOMAIN_CODES  # 别名，向后兼容


# 映射方向编码
MAPPING_DIRECTION_CODES = {
    1: '具体→具体',
    2: '具体→抽象',
    3: '抽象→抽象',
    4: '抽象→具体'
}

# 链接类型编码
LINK_TYPE_CODES = {
    1: '隐喻扩展链接',
    2: '多义链接',
    3: '子部分链接',
    4: '实例链接'
}

# 系词功能编码
COPULA_FUNCTION_CODES = {
    'equative': 1,        # 等同功能
    'attributive': 2,     # 属性功能
    'identificational': 3  # 识别功能
}

# 原型距离编码
PROTOTYPE_DISTANCE_LABELS = {
    1: '中心成员',
    2: '次中心成员',
    3: '边缘成员'
}

# 网络功能编码（5类）
NETWORK_FUNCTION_CODES = {
    1: '中心节点',
    2: '边缘节点',
    3: '桥接节点',
    4: '创新节点',
    5: '模块核心'
}

# 系词类型编码（4类）
COPULA_TYPE_CODES = {
    'standard': '标准型',
    'extended': '扩展型',
    'negative': '否定型',
    'simile': '明喻型'
}

# 映射基础编码（7类）- 中文标签
MAPPING_BASIS_CODES = {
    'similarity': '相似性',
    'correlation': '相关性',
    'function': '功能性',
    'structure': '结构性',
    'causality': '因果性',
    'contiguity': '邻近性',
    'function_similarity': '功能相似性'
}

# 映射基础数值编码（用于SEM分析）
MAPPING_BASIS_NUM = {
    'similarity': 1,
    'correlation': 2,
    'function': 3,
    'structure': 4,
    'causality': 5,
    'contiguity': 6,
    'function_similarity': 7
}

# 隐喻类型编码（3类）
METAPHOR_TYPE_CODES = {
    'ontological': '实体隐喻',
    'structural': '结构隐喻',
    'orientational': '方位隐喻'
}

# 认知通达度归并标准（5级→3级）
# 根据CFMC-33定义：1=最难, 5=最易
# 归并规则：1-2级=低通达, 3级=中通达, 4-5级=高通达
COGNITIVE_ACCESSIBILITY_LEVELS = {
    1: '低',
    2: '低',
    3: '中',
    4: '高',
    5: '高'
}

# 概念复杂度归并标准（5级→3级）
CONCEPTUAL_COMPLEXITY_LEVELS = {
    1: '低',
    2: '低',
    3: '中',
    4: '高',
    5: '高'
}

# 映射方向简称（用于12类构式命名）
MAPPING_DIRECTION_SHORT = {
    1: '具具',   # 具体→具体
    2: '具抽',   # 具体→抽象
    3: '抽抽',   # 抽象→抽象
    4: '抽具'    # 抽象→具体
}

# 12类构式理论框架
# 格式：{通达度}_{映射方向}
CONSTRUCTION_TYPE_12 = [
    '低_具具', '低_具抽', '低_抽抽', '低_抽具',
    '中_具具', '中_具抽', '中_抽抽', '中_抽具',
    '高_具具', '高_具抽', '高_抽抽', '高_抽具'
]

# 需要转换为整数的字段列表（JSON中声明为int但存储为float）
INT_FIELDS = [
    'mapping_direction',
    'cognitive_accessibility',
    'conceptual_complexity',
    'prototype_distance',
    'link_type',
    'function_in_network'
]

# 假设验证标准
HYPOTHESIS_CRITERIA = {
    'H1-1': {'metric': 'r', 'range': (-0.60, -0.40), 'p': 0.001},
    'H1-2': {'silhouette': 0.30, 'lda_accuracy': 0.85},
    'H2': {'C': 0.60, 'L': 3.0, 'sigma': 1.0},
    'H3-1': {'CFI': 0.90, 'RMSEA': 0.08, 'beta': 0.40},
    'H3-2': {'r': 0.30, 'p': 0.05}
}

# 颜色方案（12类构式）
CONSTRUCTION_COLORS = [
    '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33',
    '#a65628', '#f781bf', '#999999', '#66c2a5', '#fc8d62', '#8da0cb'
]


# =============================================================================
# 主函数（测试）
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("汉语系表隐喻构式统计分析——公共函数模块测试")
    print("=" * 60)

    # 测试路径获取
    print("\n1. 测试路径获取:")
    paths = get_paths()
    for key, path in paths.items():
        exists = "[OK]" if path.exists() else "[X]"
        print(f"  {key}: {path} [{exists}]")

    # 测试数据加载（含类型转换）
    print("\n2. 测试数据加载:")
    try:
        df, meta = load_cfmc_data()
        print(f"  数据形状: {df.shape}")
        print(f"  字段数: {len(df.columns)}")
        print(f"  元数据: {list(meta.keys())}")

        # 验证类型转换
        print("\n  整数字段类型验证:")
        int_fields = ['mapping_direction', 'cognitive_accessibility', 'conceptual_complexity']
        for field in int_fields:
            if field in df.columns:
                dtype = df[field].dtype
                print(f"    {field}: {dtype}")
    except Exception as e:
        print(f"  错误: {e}")

    # 测试归并函数
    print("\n3. 测试归并函数:")
    test_values = [1, 2, 3, 4, 5]
    print("  认知通达度归并 (1=最难, 5=最易):")
    for v in test_values:
        print(f"    {v} → {bin_accessibility(v)}")

    print("  概念复杂度归并:")
    for v in test_values:
        print(f"    {v} → {bin_complexity(v)}")

    # 测试12类构式标签生成
    print("\n4. 测试12类构式标签生成:")
    test_cases = [(5, 2), (3, 1), (1, 4)]  # (认知通达度, 映射方向)
    for ca, md in test_cases:
        label = get_construction_type_12(ca, md)
        print(f"    CA={ca}, MD={md} → {label}")

    # 测试字体路径
    print("\n5. 测试字体路径:")
    font_paths = get_font_paths()
    for key, path in font_paths.items():
        exists = "[OK]" if os.path.exists(path) else "[X]"
        print(f"  {key}: {path} [{exists}]")

    # 测试统计格式化
    print("\n6. 测试统计格式化:")
    print(f"  {format_stats('r', -0.52, p_value=0.0001)}")
    print(f"  {format_stats('F', 12.34, p_value=0.001, df=(2, 120))}")
    print(f"  {format_stats('beta', 0.45, p_value=0.001, ci=(0.38, 0.52))}")

    # 显示常量定义
    print("\n7. 常量定义检查:")
    print(f"  DOMAIN_CODES: {len(DOMAIN_CODES)}类（统一域编码）")
    print(f"  SOURCE_DOMAIN_CODES: {len(SOURCE_DOMAIN_CODES)}类（别名）")
    print(f"  TARGET_DOMAIN_CODES: {len(TARGET_DOMAIN_CODES)}类（别名）")
    print(f"  MAPPING_DIRECTION_CODES: {len(MAPPING_DIRECTION_CODES)}类")
    print(f"  MAPPING_DIRECTION_SHORT: {len(MAPPING_DIRECTION_SHORT)}类")
    print(f"  COGNITIVE_ACCESSIBILITY_LEVELS: {len(COGNITIVE_ACCESSIBILITY_LEVELS)}级→3级")
    print(f"  CONSTRUCTION_TYPE_12: {len(CONSTRUCTION_TYPE_12)}类")

    print("\n" + "=" * 60)
    print("公共函数模块测试完成")
    print("=" * 60)
