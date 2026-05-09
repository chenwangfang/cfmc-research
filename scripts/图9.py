#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图9 研究程序流程图
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
    'stage1_fill': '#ebf5fb',
    'stage1_stroke': '#2980b9',
    'stage2_fill': '#fef9e7',
    'stage2_stroke': '#d4ac0d',
    'stage3_fill': '#e8f8f5',
    'stage3_stroke': '#17a589',
    'stage4_fill': '#f5eef8',
    'stage4_stroke': '#8e44ad',
    'q1_fill': '#d4e6f1',
    'q1_stroke': '#2874a6',
    'q2_fill': '#d5f5e3',
    'q2_stroke': '#1e8449',
    'q3_fill': '#e8daef',
    'q3_stroke': '#6c3483',
    'bridge_fill': '#fadbd8',
    'bridge_stroke': '#c0392b',
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

def draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color, linewidth=1.5, radius=0.012):
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
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # ==========================================================================
    # 阶段1：理论建构
    # ==========================================================================
    stage1_y = 0.76
    stage1_h = 0.10

    draw_text(ax, 0.08, stage1_y + stage1_h/2, '阶段1', fontsize=13, bold=True,
              ha='left', va='center', color=COLORS['stage1_stroke'])
    draw_text(ax, 0.08, stage1_y + stage1_h/2 - 0.025, '理论建构', fontsize=11,
              ha='left', va='center', color=COLORS['stage1_stroke'])

    draw_rounded_box(ax, 0.18, stage1_y, 0.74, stage1_h, COLORS['stage1_fill'], COLORS['stage1_stroke'], 2)

    # 内部流程
    items1 = [('文献综述', '（第2章）'), ('CFMC理论框架', '（第3章）'), ('研究假设', '（第4章4.1节）')]
    x_pos1 = [0.28, 0.50, 0.75]
    for i, ((main, sub), x) in enumerate(zip(items1, x_pos1)):
        draw_text(ax, x, stage1_y + stage1_h/2 + 0.015, main, fontsize=11, bold=True,
                  ha='center', va='center', color=COLORS['stage1_stroke'])
        draw_text(ax, x, stage1_y + stage1_h/2 - 0.018, sub, fontsize=9,
                  ha='center', va='center', color=COLORS['gray'])
        if i < len(items1) - 1:
            draw_arrow(ax, (x + 0.08, stage1_y + stage1_h/2), (x_pos1[i+1] - 0.08, stage1_y + stage1_h/2),
                      COLORS['arrow'], 1.5, 10)

    # 阶段间箭头
    draw_arrow(ax, (0.5, stage1_y - 0.01), (0.5, stage1_y - 0.04), COLORS['arrow'], 2.0, 15)

    # ==========================================================================
    # 阶段2：数据准备
    # ==========================================================================
    stage2_y = 0.62
    stage2_h = 0.10

    draw_text(ax, 0.08, stage2_y + stage2_h/2, '阶段2', fontsize=13, bold=True,
              ha='left', va='center', color=COLORS['stage2_stroke'])
    draw_text(ax, 0.08, stage2_y + stage2_h/2 - 0.025, '数据准备', fontsize=11,
              ha='left', va='center', color=COLORS['stage2_stroke'])

    draw_rounded_box(ax, 0.18, stage2_y, 0.74, stage2_h, COLORS['stage2_fill'], COLORS['stage2_stroke'], 2)

    # 内部流程
    items2 = [('语料筛选', '（发布5,971条）'), ('核心标注', '（33项必填）'), ('质量控制', '（κ≥0.75）')]
    x_pos2 = [0.28, 0.50, 0.75]
    for i, ((main, sub), x) in enumerate(zip(items2, x_pos2)):
        draw_text(ax, x, stage2_y + stage2_h/2 + 0.015, main, fontsize=11, bold=True,
                  ha='center', va='center', color=COLORS['stage2_stroke'])
        draw_text(ax, x, stage2_y + stage2_h/2 - 0.018, sub, fontsize=9,
                  ha='center', va='center', color=COLORS['gray'])
        if i < len(items2) - 1:
            draw_arrow(ax, (x + 0.08, stage2_y + stage2_h/2), (x_pos2[i+1] - 0.08, stage2_y + stage2_h/2),
                      COLORS['arrow'], 1.5, 10)

    # 阶段间箭头
    draw_arrow(ax, (0.5, stage2_y - 0.01), (0.5, stage2_y - 0.04), COLORS['arrow'], 2.0, 15)

    # ==========================================================================
    # 阶段3：实证分析
    # ==========================================================================
    stage3_y = 0.28
    stage3_h = 0.30

    draw_text(ax, 0.08, stage3_y + stage3_h - 0.04, '阶段3', fontsize=13, bold=True,
              ha='left', va='center', color=COLORS['stage3_stroke'])
    draw_text(ax, 0.08, stage3_y + stage3_h - 0.065, '实证分析', fontsize=11,
              ha='left', va='center', color=COLORS['stage3_stroke'])

    draw_rounded_box(ax, 0.18, stage3_y, 0.74, stage3_h, COLORS['stage3_fill'], COLORS['stage3_stroke'], 2)

    # Q1框
    q_box_w = 0.15
    q_box_h = 0.12
    q1_x = 0.22
    q_y = stage3_y + stage3_h - 0.05 - q_box_h

    draw_rounded_box(ax, q1_x, q_y, q_box_w, q_box_h, COLORS['q1_fill'], COLORS['q1_stroke'], 1.5)
    draw_text(ax, q1_x + q_box_w/2, q_y + q_box_h - 0.025, 'Q1类型', fontsize=11, bold=True,
              ha='center', va='center', color=COLORS['q1_stroke'])
    draw_text(ax, q1_x + q_box_w/2, q_y + q_box_h/2, '(第5章)', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])
    draw_text(ax, q1_x + q_box_w/2, q_y + 0.025, 'H1-1, H1-2', fontsize=9,
              ha='center', va='center', color=COLORS['q1_stroke'])

    # Q2框
    q2_x = 0.425
    draw_rounded_box(ax, q2_x, q_y, q_box_w, q_box_h, COLORS['q2_fill'], COLORS['q2_stroke'], 1.5)
    draw_text(ax, q2_x + q_box_w/2, q_y + q_box_h - 0.025, 'Q2网络', fontsize=11, bold=True,
              ha='center', va='center', color=COLORS['q2_stroke'])
    draw_text(ax, q2_x + q_box_w/2, q_y + q_box_h/2, '(第6章)', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])
    draw_text(ax, q2_x + q_box_w/2, q_y + 0.025, 'H2', fontsize=9,
              ha='center', va='center', color=COLORS['q2_stroke'])

    # Q3框
    q3_x = 0.63
    draw_rounded_box(ax, q3_x, q_y, q_box_w, q_box_h, COLORS['q3_fill'], COLORS['q3_stroke'], 1.5)
    draw_text(ax, q3_x + q_box_w/2, q_y + q_box_h - 0.025, 'Q3机制', fontsize=11, bold=True,
              ha='center', va='center', color=COLORS['q3_stroke'])
    draw_text(ax, q3_x + q_box_w/2, q_y + q_box_h/2, '(第7章)', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])
    draw_text(ax, q3_x + q_box_w/2, q_y + 0.025, 'H3-1, EA-1/2', fontsize=9,
              ha='center', va='center', color=COLORS['q3_stroke'])

    # Q1→Q2箭头
    draw_arrow(ax, (q1_x + q_box_w + 0.01, q_y + q_box_h/2), (q2_x - 0.01, q_y + q_box_h/2),
               COLORS['arrow'], 1.5, 10)
    # Q3→Q2箭头
    draw_arrow(ax, (q3_x - 0.01, q_y + q_box_h/2), (q2_x + q_box_w + 0.01, q_y + q_box_h/2),
               COLORS['arrow'], 1.5, 10)

    # 向下的连线和H3-2桥梁。H3-2只连接Q1与Q3，Q2作为横向结构证据进入整合。
    bridge_y = stage3_y + 0.04
    # Q1向下连线
    ax.plot([q1_x + q_box_w/2, q1_x + q_box_w/2], [q_y - 0.005, bridge_y + 0.035],
            color=COLORS['gray'], linewidth=1.5)
    # Q3向下连线
    ax.plot([q3_x + q_box_w/2, q3_x + q_box_w/2], [q_y - 0.005, bridge_y + 0.035],
            color=COLORS['gray'], linewidth=1.5)
    # 横向连线
    ax.plot([q1_x + q_box_w/2, q3_x + q_box_w/2], [bridge_y + 0.035, bridge_y + 0.035],
            color=COLORS['gray'], linewidth=1.5)
    draw_text(ax, q2_x + q_box_w/2, bridge_y + 0.053, '横向结构证据', fontsize=8,
              ha='center', va='center', color=COLORS['gray'])
    # 向下到桥梁
    draw_arrow(ax, (q2_x + q_box_w/2, bridge_y + 0.035), (q2_x + q_box_w/2, bridge_y + 0.025),
               COLORS['bridge_stroke'], 1.5, 10)

    # H3-2桥梁框
    bridge_w = 0.18
    draw_rounded_box(ax, q2_x + q_box_w/2 - bridge_w/2, bridge_y - 0.01, bridge_w, 0.035,
                     COLORS['bridge_fill'], COLORS['bridge_stroke'], 1.5)
    draw_text(ax, q2_x + q_box_w/2, bridge_y + 0.005, 'H3-2桥梁验证', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['bridge_stroke'])

    # 阶段间箭头
    draw_arrow(ax, (0.5, stage3_y - 0.01), (0.5, stage3_y - 0.04), COLORS['arrow'], 2.0, 15)

    # ==========================================================================
    # 阶段4：理论整合
    # ==========================================================================
    stage4_y = 0.14
    stage4_h = 0.10

    draw_text(ax, 0.08, stage4_y + stage4_h/2, '阶段4', fontsize=13, bold=True,
              ha='left', va='center', color=COLORS['stage4_stroke'])
    draw_text(ax, 0.08, stage4_y + stage4_h/2 - 0.025, '理论整合', fontsize=11,
              ha='left', va='center', color=COLORS['stage4_stroke'])

    draw_rounded_box(ax, 0.18, stage4_y, 0.74, stage4_h, COLORS['stage4_fill'], COLORS['stage4_stroke'], 2)

    # 内部流程
    items4 = [('综合讨论', '（第8章）'), ('理论贡献', 'Sullivan修补'), ('结论', '（第9章）')]
    x_pos4 = [0.28, 0.50, 0.75]
    for i, ((main, sub), x) in enumerate(zip(items4, x_pos4)):
        draw_text(ax, x, stage4_y + stage4_h/2 + 0.015, main, fontsize=11, bold=True,
                  ha='center', va='center', color=COLORS['stage4_stroke'])
        draw_text(ax, x, stage4_y + stage4_h/2 - 0.018, sub, fontsize=9,
                  ha='center', va='center', color=COLORS['gray'])
        if i < len(items4) - 1:
            draw_arrow(ax, (x + 0.08, stage4_y + stage4_h/2), (x_pos4[i+1] - 0.08, stage4_y + stage4_h/2),
                      COLORS['arrow'], 1.5, 10)

    return fig, ax

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 输出目录（与脚本目录分离）
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    fig, ax = create_figure()

    png_path = os.path.join(output_dir, '图9 研究程序流程图.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f'已保存: {png_path}')

    # pdf_path = os.path.join(script_dir, '图9 研究程序流程图.pdf')  # 已禁用PDF输出
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
    print('图9 研究程序流程图 绘制完成！')
