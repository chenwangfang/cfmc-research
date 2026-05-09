#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图8 研究问题、假设、方法与数据的对应关系
用于博士论文第四章
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.font_manager as fm
import os

# =============================================================================
# 字体设置
# =============================================================================
font_paths = [
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "/mnt/c/Windows/Fonts/msyhbd.ttc",
    "/mnt/c/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]

FONT_PROP = None
FONT_PROP_BOLD = None
for font_path in font_paths:
    if os.path.exists(font_path):
        FONT_PROP = fm.FontProperties(fname=font_path)
        FONT_PROP_BOLD = fm.FontProperties(fname=font_path, weight='bold')
        print(f"使用字体: {font_path}")
        break

if FONT_PROP is None:
    FONT_PROP = fm.FontProperties(family='Microsoft YaHei')
    FONT_PROP_BOLD = fm.FontProperties(family='Microsoft YaHei', weight='bold')

plt.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 颜色定义
# =============================================================================
COLORS = {
    'title_blue': '#1a5276',
    'q1_fill': '#ebf5fb',
    'q1_stroke': '#2980b9',
    'q2_fill': '#e8f8f5',
    'q2_stroke': '#17a589',
    'q3_fill': '#f5eef8',
    'q3_stroke': '#8e44ad',
    'method_fill': '#fef9e7',
    'method_stroke': '#d4ac0d',
    'chapter_fill': '#fadbd8',
    'chapter_stroke': '#c0392b',
    'data_fill': '#d5f5e3',
    'data_stroke': '#1e8449',
    'gray': '#4a5568',
    'arrow': '#2d3748',
    'white': '#ffffff',
    'bg': '#f8f9fa',
}

# =============================================================================
# 绘图辅助函数
# =============================================================================
def draw_text(ax, x, y, text, fontsize=12, bold=False, **kwargs):
    fp = FONT_PROP_BOLD if bold else FONT_PROP
    return ax.text(x, y, text, fontsize=fontsize, fontproperties=fp, **kwargs)

def draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color, linewidth=1.5, radius=0.015):
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill_color,
        edgecolor=stroke_color,
        linewidth=linewidth
    )
    ax.add_patch(box)
    return box

def draw_arrow(ax, start, end, color='#2d3748', linewidth=2.0, head_scale=12):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=linewidth,
                               mutation_scale=head_scale))

# =============================================================================
# 主绘图函数
# =============================================================================
def create_figure():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 标题
    draw_text(ax, 0.5, 0.92, '研究问题、假设、方法与数据的对应关系', fontsize=16, bold=True,
              ha='center', va='center', color=COLORS['title_blue'])

    # 分隔线
    ax.plot([0.06, 0.94], [0.87, 0.87], color=COLORS['title_blue'], linewidth=1.5)

    # 列标题
    col_x = [0.14, 0.34, 0.58, 0.85]
    headers = ['研究问题', '假设', '分析方法', '验证章节']
    for i, (x, h) in enumerate(zip(col_x, headers)):
        draw_text(ax, x, 0.82, h, fontsize=13, bold=True, ha='center', va='center', color=COLORS['gray'])

    # 表头分隔线
    ax.plot([0.06, 0.94], [0.77, 0.77], color=COLORS['gray'], linewidth=0.8, linestyle='--')

    # ==========================================================================
    # Q1 行
    # ==========================================================================
    q1_y = 0.65
    # Q1框
    draw_rounded_box(ax, 0.06, q1_y - 0.06, 0.16, 0.12, COLORS['q1_fill'], COLORS['q1_stroke'], 2)
    draw_text(ax, 0.14, q1_y + 0.02, 'Q1', fontsize=14, bold=True, ha='center', va='center', color=COLORS['q1_stroke'])
    draw_text(ax, 0.14, q1_y - 0.025, '类型特征', fontsize=12, ha='center', va='center', color=COLORS['q1_stroke'])

    # 箭头Q1→假设
    draw_arrow(ax, (0.23, q1_y), (0.27, q1_y), COLORS['arrow'], 1.8)

    # 假设框
    draw_rounded_box(ax, 0.28, q1_y - 0.05, 0.12, 0.10, COLORS['method_fill'], COLORS['method_stroke'], 1.5)
    draw_text(ax, 0.34, q1_y + 0.015, 'H1-1', fontsize=11, ha='center', va='center', color=COLORS['method_stroke'])
    draw_text(ax, 0.34, q1_y - 0.025, 'H1-2', fontsize=11, ha='center', va='center', color=COLORS['method_stroke'])

    # 箭头假设→方法
    draw_arrow(ax, (0.41, q1_y), (0.45, q1_y), COLORS['arrow'], 1.8)

    # 方法框
    draw_rounded_box(ax, 0.46, q1_y - 0.06, 0.24, 0.12, COLORS['white'], COLORS['gray'], 1.5)
    draw_text(ax, 0.58, q1_y + 0.025, '双维度分类、GMM聚类', fontsize=11, ha='center', va='center', color=COLORS['gray'])
    draw_text(ax, 0.58, q1_y - 0.015, 'LDA判别、原型距离分析', fontsize=11, ha='center', va='center', color=COLORS['gray'])

    # 箭头方法→章节
    draw_arrow(ax, (0.71, q1_y), (0.78, q1_y), COLORS['arrow'], 1.8)

    # 章节框
    draw_rounded_box(ax, 0.79, q1_y - 0.04, 0.12, 0.08, COLORS['chapter_fill'], COLORS['chapter_stroke'], 1.5)
    draw_text(ax, 0.85, q1_y, '第5章', fontsize=12, bold=True, ha='center', va='center', color=COLORS['chapter_stroke'])

    # ==========================================================================
    # Q2 行
    # ==========================================================================
    q2_y = 0.45
    # Q2框
    draw_rounded_box(ax, 0.06, q2_y - 0.06, 0.16, 0.12, COLORS['q2_fill'], COLORS['q2_stroke'], 2)
    draw_text(ax, 0.14, q2_y + 0.02, 'Q2', fontsize=14, bold=True, ha='center', va='center', color=COLORS['q2_stroke'])
    draw_text(ax, 0.14, q2_y - 0.025, '网络组织', fontsize=12, ha='center', va='center', color=COLORS['q2_stroke'])

    # 箭头Q2→假设
    draw_arrow(ax, (0.23, q2_y), (0.27, q2_y), COLORS['arrow'], 1.8)

    # 假设框
    draw_rounded_box(ax, 0.28, q2_y - 0.04, 0.12, 0.08, COLORS['method_fill'], COLORS['method_stroke'], 1.5)
    draw_text(ax, 0.34, q2_y, 'H2', fontsize=12, ha='center', va='center', color=COLORS['method_stroke'])

    # 箭头假设→方法
    draw_arrow(ax, (0.41, q2_y), (0.45, q2_y), COLORS['arrow'], 1.8)

    # 方法框
    draw_rounded_box(ax, 0.46, q2_y - 0.06, 0.24, 0.12, COLORS['white'], COLORS['gray'], 1.5)
    draw_text(ax, 0.58, q2_y + 0.025, '宏观类型网络小世界检验', fontsize=11, ha='center', va='center', color=COLORS['gray'])
    draw_text(ax, 0.58, q2_y - 0.015, '链接类型、模块化与中心性分析', fontsize=11, ha='center', va='center', color=COLORS['gray'])

    # 箭头方法→章节
    draw_arrow(ax, (0.71, q2_y), (0.78, q2_y), COLORS['arrow'], 1.8)

    # 章节框
    draw_rounded_box(ax, 0.79, q2_y - 0.04, 0.12, 0.08, COLORS['chapter_fill'], COLORS['chapter_stroke'], 1.5)
    draw_text(ax, 0.85, q2_y, '第6章', fontsize=12, bold=True, ha='center', va='center', color=COLORS['chapter_stroke'])

    # ==========================================================================
    # Q3 行
    # ==========================================================================
    q3_y = 0.25
    # Q3框
    draw_rounded_box(ax, 0.06, q3_y - 0.06, 0.16, 0.12, COLORS['q3_fill'], COLORS['q3_stroke'], 2)
    draw_text(ax, 0.14, q3_y + 0.02, 'Q3', fontsize=14, bold=True, ha='center', va='center', color=COLORS['q3_stroke'])
    draw_text(ax, 0.14, q3_y - 0.025, '认知机制', fontsize=12, ha='center', va='center', color=COLORS['q3_stroke'])

    # 箭头Q3→假设
    draw_arrow(ax, (0.23, q3_y), (0.27, q3_y), COLORS['arrow'], 1.8)

    # 假设框
    draw_rounded_box(ax, 0.28, q3_y - 0.05, 0.12, 0.10, COLORS['method_fill'], COLORS['method_stroke'], 1.5)
    draw_text(ax, 0.34, q3_y + 0.015, 'H3-1', fontsize=11, ha='center', va='center', color=COLORS['method_stroke'])
    draw_text(ax, 0.34, q3_y - 0.025, 'H3-2', fontsize=11, ha='center', va='center', color=COLORS['method_stroke'])

    # 箭头假设→方法
    draw_arrow(ax, (0.41, q3_y), (0.45, q3_y), COLORS['arrow'], 1.8)

    # 方法框
    draw_rounded_box(ax, 0.46, q3_y - 0.06, 0.24, 0.12, COLORS['white'], COLORS['gray'], 1.5)
    draw_text(ax, 0.58, q3_y + 0.025, 'PLS-SEM路径、PLS-MGA', fontsize=11, ha='center', va='center', color=COLORS['gray'])
    draw_text(ax, 0.58, q3_y - 0.015, 'Pearson近似相关与中介检验', fontsize=11, ha='center', va='center', color=COLORS['gray'])

    # 箭头方法→章节
    draw_arrow(ax, (0.71, q3_y), (0.78, q3_y), COLORS['arrow'], 1.8)

    # 章节框
    draw_rounded_box(ax, 0.79, q3_y - 0.04, 0.12, 0.08, COLORS['chapter_fill'], COLORS['chapter_stroke'], 1.5)
    draw_text(ax, 0.85, q3_y, '第7章', fontsize=12, bold=True, ha='center', va='center', color=COLORS['chapter_stroke'])

    # ==========================================================================
    # 数据基础（底部）
    # ==========================================================================
    ax.plot([0.06, 0.94], [0.12, 0.12], color=COLORS['title_blue'], linewidth=1.5)

    draw_rounded_box(ax, 0.25, 0.045, 0.50, 0.06, COLORS['data_fill'], COLORS['data_stroke'], 2)
    draw_text(ax, 0.5, 0.075, '数据基础：BCC语料库 - 5,971条CFMC-33发布标注语料', fontsize=12, bold=True,
              ha='center', va='center', color=COLORS['data_stroke'])

    return fig, ax

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 输出目录（与脚本目录分离）
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    fig, ax = create_figure()

    png_path = os.path.join(output_dir, '图8 研究问题、假设与方法对应关系.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f'已保存: {png_path}')

    # pdf_path = os.path.join(script_dir, '图8 研究问题、假设与方法对应关系.pdf')  # 已禁用PDF输出
    # fig.savefig(pdf_path, format='pdf', bbox_inches='tight', facecolor='white', edgecolor='none')  # 已禁用PDF输出
    # print(f'已保存: {pdf_path}')  # 已禁用PDF输出


    # 高清输出（1200 DPI）
    hd_dir = '/home/tomja/projects/博士毕业论文/大论文/论文撰写/正文/毕业论文高清图'
    os.makedirs(hd_dir, exist_ok=True)
    hd_path = os.path.join(hd_dir, os.path.basename(png_path))
    fig.savefig(hd_path, dpi=1200, bbox_inches='tight', facecolor='white', edgecolor='none')
    svg_path = hd_path.replace('.png', '.svg')
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f'已保存高清: {hd_path}')
    print(f'已保存矢量: {svg_path}')

    plt.close(fig)
    print('图8 研究问题、假设、方法与数据的对应关系 绘制完成！')
