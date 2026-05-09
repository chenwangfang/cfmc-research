#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图10 语料筛选流程图
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
    'source_fill': '#d4e6f1',
    'source_stroke': '#2874a6',
    'stage1_fill': '#ebf5fb',
    'stage1_stroke': '#2980b9',
    'stage2_fill': '#fef9e7',
    'stage2_stroke': '#d4ac0d',
    'stage3_fill': '#e8f8f5',
    'stage3_stroke': '#17a589',
    'stage4_fill': '#f5eef8',
    'stage4_stroke': '#8e44ad',
    'result_fill': '#d5f5e3',
    'result_stroke': '#1e8449',
    'remove_fill': '#fadbd8',
    'remove_stroke': '#c0392b',
    'gray': '#4a5568',
    'arrow': '#2d3748',
    'white': '#ffffff',
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

def draw_arrow(ax, start, end, color='#2d3748', linewidth=2.0, head_scale=15):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=linewidth,
                               mutation_scale=head_scale))

# =============================================================================
# 主绘图函数
# =============================================================================
def create_figure():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 主流程Y坐标
    y_source = 0.88
    y_stage1 = 0.70
    y_stage2 = 0.52
    y_stage3 = 0.34
    y_stage4 = 0.16

    box_h = 0.10
    main_box_w = 0.28
    result_box_w = 0.18
    side_box_w = 0.20

    # ==========================================================================
    # 数据源（顶部）
    # ==========================================================================
    draw_rounded_box(ax, 0.36, y_source, main_box_w, box_h, COLORS['source_fill'], COLORS['source_stroke'], 2.5)
    draw_text(ax, 0.5, y_source + box_h/2 + 0.015, 'BCC语料库', fontsize=14, bold=True,
              ha='center', va='center', color=COLORS['source_stroke'])
    draw_text(ax, 0.5, y_source + box_h/2 - 0.022, '（150亿字规模）', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    draw_arrow(ax, (0.5, y_source - 0.01), (0.5, y_stage1 + box_h + 0.01), COLORS['arrow'], 2.0, 15)

    # ==========================================================================
    # 阶段1：原始抽样
    # ==========================================================================
    draw_rounded_box(ax, 0.36, y_stage1, main_box_w, box_h, COLORS['stage1_fill'], COLORS['stage1_stroke'], 2)
    draw_text(ax, 0.5, y_stage1 + box_h/2 + 0.018, '阶段1：原始抽样', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['stage1_stroke'])
    draw_text(ax, 0.5, y_stage1 + box_h/2 - 0.018, '以“是”字句为入口', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    # 结果框
    draw_rounded_box(ax, 0.70, y_stage1 + 0.01, result_box_w, box_h - 0.02,
                     COLORS['result_fill'], COLORS['result_stroke'], 1.5)
    draw_text(ax, 0.79, y_stage1 + box_h/2, '100,000条', fontsize=12, bold=True,
              ha='center', va='center', color=COLORS['result_stroke'])

    draw_arrow(ax, (0.64, y_stage1 + box_h/2), (0.69, y_stage1 + box_h/2), COLORS['arrow'], 1.5, 12)
    draw_arrow(ax, (0.5, y_stage1 - 0.01), (0.5, y_stage2 + box_h + 0.01), COLORS['arrow'], 2.0, 15)

    # ==========================================================================
    # 阶段2：机器筛选
    # ==========================================================================
    draw_rounded_box(ax, 0.36, y_stage2, main_box_w, box_h, COLORS['stage2_fill'], COLORS['stage2_stroke'], 2)
    draw_text(ax, 0.5, y_stage2 + box_h/2 + 0.018, '阶段2：机器筛选', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['stage2_stroke'])
    draw_text(ax, 0.5, y_stage2 + box_h/2 - 0.018, 'LSTM + SVM混合模型', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    # 结果框
    draw_rounded_box(ax, 0.70, y_stage2 + 0.01, result_box_w, box_h - 0.02,
                     COLORS['result_fill'], COLORS['result_stroke'], 1.5)
    draw_text(ax, 0.79, y_stage2 + box_h/2, '14,531条', fontsize=12, bold=True,
              ha='center', va='center', color=COLORS['result_stroke'])

    draw_arrow(ax, (0.64, y_stage2 + box_h/2), (0.69, y_stage2 + box_h/2), COLORS['arrow'], 1.5, 12)
    draw_arrow(ax, (0.5, y_stage2 - 0.01), (0.5, y_stage3 + box_h + 0.01), COLORS['arrow'], 2.0, 15)

    # ==========================================================================
    # 阶段3：人工验证
    # ==========================================================================
    draw_rounded_box(ax, 0.36, y_stage3, main_box_w, box_h, COLORS['stage3_fill'], COLORS['stage3_stroke'], 2)
    draw_text(ax, 0.5, y_stage3 + box_h/2 + 0.018, '阶段3：人工验证', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['stage3_stroke'])
    draw_text(ax, 0.5, y_stage3 + box_h/2 - 0.018, 'MIPVU隐喻识别程序', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    # 结果框
    draw_rounded_box(ax, 0.70, y_stage3 + 0.01, result_box_w, box_h - 0.02,
                     COLORS['result_fill'], COLORS['result_stroke'], 1.5)
    draw_text(ax, 0.79, y_stage3 + box_h/2 + 0.012, '14,263条', fontsize=12, bold=True,
              ha='center', va='center', color=COLORS['result_stroke'])
    draw_text(ax, 0.79, y_stage3 + box_h/2 - 0.018, '(保留率98.16%)', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    draw_arrow(ax, (0.64, y_stage3 + box_h/2), (0.69, y_stage3 + box_h/2), COLORS['arrow'], 1.5, 12)

    # 剔除框（右侧分支）
    draw_rounded_box(ax, 0.12, y_stage3 + 0.01, side_box_w, box_h - 0.02,
                     COLORS['remove_fill'], COLORS['remove_stroke'], 1.5)
    draw_text(ax, 0.22, y_stage3 + box_h/2 + 0.012, '剔除268条', fontsize=11, bold=True,
              ha='center', va='center', color=COLORS['remove_stroke'])
    draw_text(ax, 0.22, y_stage3 + box_h/2 - 0.018, '（不含隐喻义）', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    draw_arrow(ax, (0.36, y_stage3 + box_h/2), (0.32, y_stage3 + box_h/2), COLORS['remove_stroke'], 1.5, 12)

    draw_arrow(ax, (0.5, y_stage3 - 0.01), (0.5, y_stage4 + box_h + 0.01), COLORS['arrow'], 2.0, 15)

    # ==========================================================================
    # 阶段4：发布整理
    # ==========================================================================
    draw_rounded_box(ax, 0.36, y_stage4, main_box_w, box_h, COLORS['stage4_fill'], COLORS['stage4_stroke'], 2)
    draw_text(ax, 0.5, y_stage4 + box_h/2 + 0.018, '阶段4：发布整理', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['stage4_stroke'])
    draw_text(ax, 0.5, y_stage4 + box_h/2 - 0.018, '抽样、补全与去重', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    # 结果框（含发布清理）
    draw_rounded_box(ax, 0.70, y_stage4 + 0.01, result_box_w, box_h - 0.02,
                     COLORS['result_fill'], COLORS['result_stroke'], 1.5)
    draw_text(ax, 0.79, y_stage4 + box_h/2 + 0.012, '6,022条', fontsize=12, bold=True,
              ha='center', va='center', color=COLORS['result_stroke'])
    draw_text(ax, 0.79, y_stage4 + box_h/2 - 0.018, '(裁定后5,971条)', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    draw_arrow(ax, (0.64, y_stage4 + box_h/2), (0.69, y_stage4 + box_h/2), COLORS['arrow'], 1.5, 12)

    # ==========================================================================
    # 左侧说明框
    # ==========================================================================
    # 阶段说明
    note_x = 0.08
    notes = [
        (y_stage1 + box_h/2, '随机抽取'),
        (y_stage2 + box_h/2, '深度学习'),
        (y_stage3 + box_h/2, 'MIPVU'),
        (y_stage4 + box_h/2, '发布整理'),
    ]
    for y, txt in notes:
        draw_text(ax, note_x, y, txt, fontsize=10, ha='center', va='center', color=COLORS['gray'])

    # ==========================================================================
    # 底部最终结果
    # ==========================================================================
    final_y = 0.03
    draw_rounded_box(ax, 0.30, final_y, 0.40, 0.06, COLORS['result_fill'], COLORS['result_stroke'], 2.5)
    draw_text(ax, 0.5, final_y + 0.03, '最终语料：5,971条发布标注语料', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['result_stroke'])

    # L型箭头：从发布整理框向下，再向左连接到最终语料框右边线中间
    final_box_right = 0.70  # 最终语料框右边线x坐标
    final_box_mid_y = final_y + 0.03  # 最终语料框中间y坐标
    # 垂直线：从发布整理框底部向下
    ax.plot([0.79, 0.79], [y_stage4, final_box_mid_y], color=COLORS['arrow'], linewidth=2.0)
    # 水平箭头：向左连接到最终语料框右边线
    draw_arrow(ax, (0.79, final_box_mid_y), (final_box_right + 0.01, final_box_mid_y), COLORS['arrow'], 2.0, 15)

    return fig, ax

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 输出目录（与脚本目录分离）
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    fig, ax = create_figure()

    png_path = os.path.join(output_dir, '图10 语料筛选流程图.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f'已保存: {png_path}')

    # pdf_path = os.path.join(script_dir, '图10 语料筛选流程图.pdf')  # 已禁用PDF输出
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
    print('图10 语料筛选流程图 绘制完成！')
