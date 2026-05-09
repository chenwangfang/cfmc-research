#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图4 本研究理论定位图
用于博士论文第二章
展示Sullivan理论框架下的三重学术定位及其相互关系
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm
import os

# =============================================================================
# 字体设置
# =============================================================================
font_paths = [
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "/mnt/c/Windows/Fonts/msyhbd.ttc",
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
    'primary_blue': '#2c3e50',
    'sullivan_fill': '#e8f4f8',
    'sullivan_stroke': '#2980b9',
    'sullivan_text': '#1a5276',
    'position1_fill': '#fef9e7',
    'position1_stroke': '#d4ac0d',
    'position1_text': '#7d6608',
    'position2_fill': '#fadbd8',
    'position2_stroke': '#c0392b',
    'position2_text': '#922b21',
    'position3_fill': '#e8daef',
    'position3_stroke': '#8e44ad',
    'position3_text': '#5b2c6f',
    'gap_fill': '#f8f9fa',
    'gap_stroke': '#5d6d7e',
    'gap_text': '#2c3e50',
    'question_fill': '#d5f5e3',
    'question_stroke': '#1e8449',
    'question_text': '#145a32',
    'arrow_gray': '#7f8c8d',
    'white': '#ffffff',
    'text_gray': '#5d6d7e',
}

# =============================================================================
# 绘图辅助函数
# =============================================================================
def draw_text(ax, x, y, text, fontsize=10, bold=False, **kwargs):
    fp = FONT_PROP_BOLD if bold else FONT_PROP
    return ax.text(x, y, text, fontsize=fontsize, fontproperties=fp, **kwargs)

def draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color,
                     linewidth=1.5, radius=0.012):
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill_color,
        edgecolor=stroke_color,
        linewidth=linewidth
    )
    ax.add_patch(box)
    return box

def draw_arrow(ax, start, end, color='#2d3748', linewidth=1.5, head_scale=10):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=linewidth,
                               mutation_scale=head_scale))

def draw_line(ax, start, end, color='#7f8c8d', linewidth=1.5):
    ax.plot([start[0], end[0]], [start[1], end[1]],
            color=color, linewidth=linewidth, solid_capstyle='round')

# =============================================================================
# 主绘图函数
# =============================================================================
def create_positioning_figure():
    fig, ax = plt.subplots(1, 1, figsize=(14, 13))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # =========================================================================
    # 标题（已删除，论文中图表标题应在图表下方以可编辑文字形式呈现）
    # =========================================================================

    # =========================================================================
    # 顶层：Sullivan理论框
    # =========================================================================
    sullivan_w = 0.22
    sullivan_h = 0.10
    sullivan_x = 0.5 - sullivan_w / 2
    sullivan_y = 0.825

    draw_rounded_box(ax, sullivan_x, sullivan_y, sullivan_w, sullivan_h,
                     COLORS['sullivan_fill'], COLORS['sullivan_stroke'], 2.0, 0.012)
    draw_text(ax, 0.5, sullivan_y + sullivan_h - 0.025, 'Sullivan (2013)',
              fontsize=14, bold=True, ha='center', va='center', color=COLORS['sullivan_text'])
    draw_text(ax, 0.5, sullivan_y + sullivan_h / 2, '隐喻构式理论',
              fontsize=13, ha='center', va='center', color=COLORS['sullivan_text'])
    draw_text(ax, 0.5, sullivan_y + 0.018, '(自主-依存原则)',
              fontsize=11, ha='center', va='center', color=COLORS['text_gray'])

    # =========================================================================
    # Sullivan到三个定位的连线
    # =========================================================================
    sullivan_bottom_y = sullivan_y
    branch_y = sullivan_bottom_y - 0.025

    # Sullivan底部中心点
    sullivan_center_x = 0.5

    # 三个定位的x坐标
    pos1_center_x = 0.18
    pos2_center_x = 0.50
    pos3_center_x = 0.82

    # 从Sullivan底部向下画线
    draw_line(ax, (sullivan_center_x, sullivan_bottom_y),
              (sullivan_center_x, branch_y), COLORS['arrow_gray'], 1.8)

    # 水平分叉线
    draw_line(ax, (pos1_center_x, branch_y),
              (pos3_center_x, branch_y), COLORS['arrow_gray'], 1.8)

    # 三条向下的箭头
    position_top_y = 0.720
    draw_arrow(ax, (pos1_center_x, branch_y), (pos1_center_x, position_top_y + 0.003),
               COLORS['arrow_gray'], 1.8, 12)
    draw_arrow(ax, (pos2_center_x, branch_y), (pos2_center_x, position_top_y + 0.003),
               COLORS['arrow_gray'], 1.8, 12)
    draw_arrow(ax, (pos3_center_x, branch_y), (pos3_center_x, position_top_y + 0.003),
               COLORS['arrow_gray'], 1.8, 12)

    # =========================================================================
    # 三个定位框（上半部分：标题+内容）
    # =========================================================================
    pos_w = 0.24
    pos_h = 0.165
    pos_y = position_top_y - pos_h

    positions = [
        {
            'x': pos1_center_x - pos_w / 2,
            'title': '定位一',
            'subtitle': '汉语验证者',
            'content': ['系统验证', '自主-依存原则', '在汉语中的适用性'],
            'fill': COLORS['position1_fill'],
            'stroke': COLORS['position1_stroke'],
            'text': COLORS['position1_text'],
        },
        {
            'x': pos2_center_x - pos_w / 2,
            'title': '定位二',
            'subtitle': '汉语适应者',
            'content': ['三向整合：', '·Langacker深化', '·Goldberg扩展', '·汉语特色聚焦'],
            'fill': COLORS['position2_fill'],
            'stroke': COLORS['position2_stroke'],
            'text': COLORS['position2_text'],
        },
        {
            'x': pos3_center_x - pos_w / 2,
            'title': '定位三',
            'subtitle': '方法创新者',
            'content': ['系统标注体系', 'GMM+网络+SEM', '定量与质性整合'],
            'fill': COLORS['position3_fill'],
            'stroke': COLORS['position3_stroke'],
            'text': COLORS['position3_text'],
        },
    ]

    for pos in positions:
        # 绘制定位框
        draw_rounded_box(ax, pos['x'], pos_y, pos_w, pos_h,
                         pos['fill'], pos['stroke'], 1.8, 0.010)

        # 定位编号和副标题
        draw_text(ax, pos['x'] + pos_w / 2, pos_y + pos_h - 0.022, pos['title'],
                  fontsize=13, bold=True, ha='center', va='center', color=pos['text'])
        draw_text(ax, pos['x'] + pos_w / 2, pos_y + pos_h - 0.048, pos['subtitle'],
                  fontsize=13, bold=True, ha='center', va='center', color=pos['text'])

        # 分隔线
        line_y = pos_y + pos_h - 0.065
        ax.plot([pos['x'] + 0.015, pos['x'] + pos_w - 0.015], [line_y, line_y],
                color=pos['stroke'], linewidth=1.0, alpha=0.5)

        # 内容文本
        content_start_y = line_y - 0.022
        for i, line in enumerate(pos['content']):
            draw_text(ax, pos['x'] + pos_w / 2, content_start_y - i * 0.022, line,
                      fontsize=11, ha='center', va='center', color=COLORS['text_gray'])

    # =========================================================================
    # 定位框到"回应空白"的箭头
    # =========================================================================
    pos_bottom_y = pos_y
    gap_top_y = 0.400
    gap_h = 0.055

    # 三条向下的箭头
    draw_arrow(ax, (pos1_center_x, pos_bottom_y - 0.005),
               (pos1_center_x, gap_top_y + gap_h + 0.005),
               COLORS['arrow_gray'], 1.5, 10)
    draw_arrow(ax, (pos2_center_x, pos_bottom_y - 0.005),
               (pos2_center_x, gap_top_y + gap_h + 0.005),
               COLORS['arrow_gray'], 1.5, 10)
    draw_arrow(ax, (pos3_center_x, pos_bottom_y - 0.005),
               (pos3_center_x, gap_top_y + gap_h + 0.005),
               COLORS['arrow_gray'], 1.5, 10)

    # =========================================================================
    # "回应空白"框
    # =========================================================================
    gap_w = 0.18
    gap_y = gap_top_y

    gaps = [
        {'x': pos1_center_x - gap_w / 2, 'text': '回应空白6'},
        {'x': pos2_center_x - gap_w / 2, 'text': '回应空白1/3/4/5'},
        {'x': pos3_center_x - gap_w / 2, 'text': '回应空白2'},
    ]

    for gap in gaps:
        draw_rounded_box(ax, gap['x'], gap_y, gap_w, gap_h,
                         COLORS['gap_fill'], COLORS['gap_stroke'], 1.5, 0.008)
        draw_text(ax, gap['x'] + gap_w / 2, gap_y + gap_h / 2, gap['text'],
                  fontsize=12, bold=True, ha='center', va='center', color=COLORS['gap_text'])

    # =========================================================================
    # "回应空白"到"研究问题"的汇聚连线
    # =========================================================================
    gap_bottom_y = gap_y
    converge_y = gap_bottom_y - 0.035
    question_top_y = 0.235

    # 三条向下的线
    draw_line(ax, (pos1_center_x, gap_bottom_y - 0.005),
              (pos1_center_x, converge_y), COLORS['arrow_gray'], 1.5)
    draw_line(ax, (pos2_center_x, gap_bottom_y - 0.005),
              (pos2_center_x, converge_y), COLORS['arrow_gray'], 1.5)
    draw_line(ax, (pos3_center_x, gap_bottom_y - 0.005),
              (pos3_center_x, converge_y), COLORS['arrow_gray'], 1.5)

    # 水平汇聚线
    draw_line(ax, (pos1_center_x, converge_y),
              (pos3_center_x, converge_y), COLORS['arrow_gray'], 1.5)

    # 向下箭头到研究问题框
    question_h = 0.085
    draw_arrow(ax, (0.5, converge_y),
               (0.5, question_top_y + question_h + 0.005),
               COLORS['arrow_gray'], 2.0, 12)

    # =========================================================================
    # "三个研究问题"框
    # =========================================================================
    question_w = 0.30
    question_x = 0.5 - question_w / 2
    question_y = question_top_y

    draw_rounded_box(ax, question_x, question_y, question_w, question_h,
                     COLORS['question_fill'], COLORS['question_stroke'], 2.0, 0.012)
    draw_text(ax, 0.5, question_y + question_h - 0.025, '三个研究问题',
              fontsize=14, bold=True, ha='center', va='center', color=COLORS['question_text'])
    draw_text(ax, 0.5, question_y + 0.022, 'Q1类型  Q2网络  Q3机制',
              fontsize=13, ha='center', va='center', color=COLORS['question_text'])

    # =========================================================================
    # 底部说明
    # =========================================================================
    draw_text(ax, 0.5, 0.080,
              '注：定位一验证Sullivan理论跨语言适用性；定位二通过三向整合填补理论盲点；',
              fontsize=11, ha='center', va='center', color=COLORS['text_gray'])
    draw_text(ax, 0.5, 0.055,
              '定位三提供系统标注与分析工具。三重定位汇聚于Q1、Q2、Q3三个研究问题',
              fontsize=11, ha='center', va='center', color=COLORS['text_gray'])

    return fig, ax

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 输出目录（与脚本目录分离）
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    fig, ax = create_positioning_figure()

    png_path = os.path.join(output_dir, '图4 本研究理论定位图.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f'已保存: {png_path}')

    # pdf_path = os.path.join(script_dir, '图4 本研究理论定位图.pdf')  # 已禁用PDF输出
    # fig.savefig(pdf_path, format='pdf', bbox_inches='tight',  # 已禁用PDF输出
                # facecolor='white', edgecolor='none')  # 已禁用PDF输出
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
    print('图4 本研究理论定位图 绘制完成！')
