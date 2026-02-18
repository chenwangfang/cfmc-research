#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图29 路径系数比较图

从表87_路径系数估计表动态加载优化模型的路径系数，
绘制水平条形图展示各路径的非标准化系数及显著性。
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import json
import os
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils_公共函数 import get_paths, get_font_paths, save_figure


def load_path_data():
    """
    从表87_路径系数估计表.json动态加载优化模型路径系数。

    Returns
    -------
    list[dict]
        每个dict包含 label, value, significance 三个键。
        仅包含非固定路径（排除系数为1.000且无标准误的约束路径）。
    """
    paths = get_paths()
    data_dir = paths['output_data']

    json_path = os.path.join(data_dir, '表87_路径系数估计表.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    result = []
    for item in raw_data:
        # 跳过固定约束路径（系数=1.000，标准误="-"）
        if item['标准误'] == '-':
            continue

        path_name = item['路径']
        coeff = float(item['系数beta'])
        sig = item['显著性'].strip()

        # 构建 LaTeX 标签
        label = _make_label(path_name)

        result.append({
            'label': label,
            'value': coeff,
            'significance': sig,
            'path_name': path_name
        })

    return result


def _make_label(path_name):
    """
    将路径名称转换为带 LaTeX 下标的标签。

    Examples
    --------
    'eta2->eta3 (beta2)' -> r'$\\eta_2 \\rightarrow \\eta_3$ ($\\beta_2$)'
    'eta3->Y (gamma)'    -> r'$\\eta_3 \\rightarrow Y$ ($\\gamma$)'
    """
    # 映射表：路径名 -> LaTeX标签
    label_map = {
        'eta2->eta3 (beta2)': r'$\eta_2 \rightarrow \eta_3$ ($\beta_2$)',
        'eta3->Y (gamma)': r'$\eta_3 \rightarrow Y$ ($\gamma$)',
        'eta2->cognitive_accessibility': r'$\eta_2 \rightarrow$ CA',
        'eta2->prototype_distance': r'$\eta_2 \rightarrow$ PD',
        'eta3->mapping_direction': r'$\eta_3 \rightarrow$ MD',
        'eta3->systematicity': r'$\eta_3 \rightarrow$ SYS',
        'eta3->entailment_richness': r'$\eta_3 \rightarrow$ ER',
        'eta1->eta2 (beta1)': r'$\eta_1 \rightarrow \eta_2$ ($\beta_1$)',
        'eta1->eta3 (beta3)': r'$\eta_1 \rightarrow \eta_3$ ($\beta_3$)',
    }

    return label_map.get(path_name, path_name)


def plot_path_coefficients():
    """
    绘制图29: 路径系数比较图

    基于表87的数据，展示优化模型中各路径的非标准化系数。
    """
    # 加载数据
    path_data = load_path_data()

    if not path_data:
        raise ValueError("表87中未找到可展示的路径系数数据")

    # 获取字体路径
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=11)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_cn_small = fm.FontProperties(fname=font_paths['chinese'], size=9)

    # 按系数绝对值降序排列
    path_data.sort(key=lambda x: abs(x['value']), reverse=True)

    labels = [d['label'] for d in path_data]
    values = [d['value'] for d in path_data]
    sigs = [d['significance'] for d in path_data]

    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=1200)

    # 设置颜色：显著路径用深色，不显著用浅灰
    colors = []
    for d in path_data:
        if d['significance'] == '***':
            if d['value'] >= 0:
                colors.append('#2E7D32')   # 深绿色 - 显著正效应
            else:
                colors.append('#EF5350')   # 红色 - 显著负效应
        else:
            colors.append('#BDBDBD')       # 灰色 - 不显著

    # 绘制水平条形图
    bars = ax.barh(range(len(labels)), values, color=colors,
                   edgecolor='black', linewidth=0.5, height=0.6)

    # 添加数值标签和显著性标记
    for i, (bar, val, sig) in enumerate(zip(bars, values, sigs)):
        sig_mark = f'  {sig}' if sig else '  n.s.'
        label_text = f'{val:.3f}{sig_mark}'
        if val >= 0:
            ax.text(val + 0.3, i, label_text, va='center', ha='left',
                    fontproperties=font_cn, fontsize=10, fontweight='bold')
        else:
            ax.text(val - 0.3, i, label_text, va='center', ha='right',
                    fontproperties=font_cn, fontsize=10, fontweight='bold')

    # 设置Y轴标签
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=font_cn)

    # 设置X轴范围（根据数据自动调整，留出标签空间）
    x_max = max(abs(v) for v in values)
    margin = x_max * 0.4
    ax.set_xlim(-x_max - margin, x_max + margin)
    ax.set_xlabel('非标准化路径系数', fontproperties=font_cn)

    # 添加垂直参考线
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)

    # 添加注释（仅解释图中使用的缩写）
    note_text = (r'注: ***$p$ < 0.001; n.s.表示不显著。'
                 r'CA=认知通达度, PD=原型距离, SYS=系统性, ER=蕴涵丰富度, Y=系词功能。'
                 r'数据来源：表87（优化模型）')
    ax.text(0.5, -0.18, note_text, transform=ax.transAxes, ha='center',
            fontproperties=font_cn_small, fontsize=8, style='italic')

    # 设置网格
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # 移除顶部和右侧边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    return fig


def main():
    """主函数"""
    print("=" * 50)
    print("生成图29: 路径系数比较图")
    print("=" * 50)

    # 生成图表
    fig = plot_path_coefficients()

    # 保存图表
    save_figure(fig, "路径系数比较图", global_num=29,
                title="路径系数比较图")

    print("\n图29生成完成！")


if __name__ == '__main__':
    main()
