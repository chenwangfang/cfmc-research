#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图35 路径系数比较图

根据表96数据生成简单的路径系数条形图。
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils_公共函数 import get_paths, get_font_paths, save_figure


def plot_path_coefficients():
    """
    绘制图35: 路径系数比较图

    基于表96的数据，展示四条路径的标准化系数。
    """
    # 获取字体路径
    font_paths = get_font_paths()
    font_cn = fm.FontProperties(fname=font_paths['chinese'], size=11)
    font_cn_title = fm.FontProperties(fname=font_paths['chinese'], size=14)
    font_cn_small = fm.FontProperties(fname=font_paths['chinese'], size=9)

    # 表96数据（使用LaTeX格式以正确显示下标）
    paths = {
        r'$\eta_2 \rightarrow \eta_3$ ($\beta_2$)': 0.802,
        r'$\eta_1 \rightarrow \eta_2$ ($\beta_1$)': 0.836,
        r'$\eta_3 \rightarrow X_{11}$ ($\gamma$)': -0.451,
        r'$\eta_1 \rightarrow \eta_3$ ($\beta_3$)': 0.045
    }

    # 排序：按系数绝对值降序
    sorted_paths = dict(sorted(paths.items(), key=lambda x: abs(x[1]), reverse=True))

    labels = list(sorted_paths.keys())
    values = list(sorted_paths.values())

    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=1200)

    # 设置颜色
    colors = []
    for v in values:
        if v >= 0.7:
            colors.append('#2E7D32')  # 深绿色 - 强效应
        elif v >= 0.4:
            colors.append('#43A047')  # 绿色 - 中等效应
        elif v >= 0:
            colors.append('#81C784')  # 浅绿色 - 弱正效应
        else:
            colors.append('#EF5350')  # 红色 - 负效应

    # 绘制水平条形图
    bars = ax.barh(range(len(labels)), values, color=colors, edgecolor='black', linewidth=0.5, height=0.6)

    # 添加数值标签和显著性标记（统一格式：数值 ***）
    for i, (bar, val) in enumerate(zip(bars, values)):
        label = f'{val:.3f}  ***'
        if val >= 0:
            # 正值：标签在条形右侧
            ax.text(val + 0.02, i, label, va='center', ha='left',
                    fontproperties=font_cn, fontsize=11, fontweight='bold')
        else:
            # 负值：标签在条形左侧
            ax.text(val - 0.18, i, label, va='center', ha='left',
                    fontproperties=font_cn, fontsize=11, fontweight='bold')

    # 设置Y轴标签
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=font_cn)

    # 设置X轴
    ax.set_xlim(-0.7, 1.1)
    ax.set_xlabel('标准化路径系数', fontproperties=font_cn)

    # 添加垂直参考线
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax.axvline(x=0.40, color='#FFA726', linestyle='--', linewidth=1.5, alpha=0.7,
               label='H3-1判断标准 (β≥0.40)')

    # 添加图例
    ax.legend(loc='lower left', prop=font_cn_small, framealpha=0.9)

    # 添加注释（使用LaTeX格式）
    note_text = r'注: ***$p$ < 0.001。$\eta_1$=认知域激活, $\eta_2$=认知参照点锚定, $\eta_3$=跨域映射, $X_{11}$=系词功能'
    ax.text(0.5, -0.15, note_text, transform=ax.transAxes, ha='center',
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
    print("生成图35: 路径系数比较图")
    print("=" * 50)

    # 生成图表
    fig = plot_path_coefficients()

    # 保存图表
    save_figure(fig, "路径系数比较图", global_num=35,
                title="路径系数比较图")

    print("\n图35生成完成！")


if __name__ == '__main__':
    main()
