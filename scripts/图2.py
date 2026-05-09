#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图2 论文整体结构
用于博士论文第一章
展示论文四个部分的层级关系与逻辑递进
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
    # 第一部分：研究缘起与文献综述（蓝色系）
    'part1_fill': '#e8f4f8',
    'part1_stroke': '#2980b9',
    'part1_text': '#1a5276',
    # 第二部分：理论构建（绿色系）
    'part2_fill': '#e8f8f0',
    'part2_stroke': '#27ae60',
    'part2_text': '#1e8449',
    # 第三部分：实证分析（金色系）
    'part3_fill': '#fef9e7',
    'part3_stroke': '#d68910',
    'part3_text': '#7d6608',
    # 第四部分：综合讨论（紫色系）
    'part4_fill': '#f5eef8',
    'part4_stroke': '#8e44ad',
    'part4_text': '#5b2c6f',
    # 通用
    'chapter_fill': '#ffffff',
    'chapter_stroke': '#5d6d7e',
    'chapter_text': '#2c3e50',
    'arrow_gray': '#7f8c8d',
    'text_gray': '#5d6d7e',
    'highlight_stroke': '#c0392b',
    'highlight_text': '#922b21',
}

# =============================================================================
# 绘图辅助函数
# =============================================================================
def draw_text(ax, x, y, text, fontsize=12, bold=False, **kwargs):
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

# =============================================================================
# 主绘图函数
# =============================================================================
def create_structure_figure():
    fig, ax = plt.subplots(1, 1, figsize=(14, 15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    PART_X = 0.08
    PART_W = 0.84

    # ==================================================================
    # 第一部分：研究缘起与文献综述（第1-3章）
    # ==================================================================
    p1_y, p1_h = 0.825, 0.140

    draw_rounded_box(ax, PART_X, p1_y, PART_W, p1_h,
                     COLORS['part1_fill'], COLORS['part1_stroke'], 2.0, 0.015)
    draw_text(ax, 0.5, p1_y + p1_h - 0.022,
              '第一部分：研究缘起与文献综述（第1-3章）',
              fontsize=14, bold=True, ha='center', va='center',
              color=COLORS['part1_text'])

    # 三个章节框
    ch_w, ch_h, ch_gap = 0.21, 0.080, 0.05
    total_cw = 3 * ch_w + 2 * ch_gap
    ch_sx = PART_X + (PART_W - total_cw) / 2
    ch_y = p1_y + 0.015

    chapters_p1 = [
        ('第1章', '绪论', '问题识别'),
        ('第2章', '文献综述', '理论梳理'),
        ('第3章', '理论框架', 'CFMC构建'),
    ]
    for i, (num, title, desc) in enumerate(chapters_p1):
        cx = ch_sx + i * (ch_w + ch_gap)
        draw_rounded_box(ax, cx, ch_y, ch_w, ch_h,
                         COLORS['chapter_fill'], COLORS['chapter_stroke'],
                         1.2, 0.008)
        draw_text(ax, cx + ch_w / 2, ch_y + ch_h - 0.016, num,
                  fontsize=12, bold=True, ha='center', va='center',
                  color=COLORS['chapter_text'])
        draw_text(ax, cx + ch_w / 2, ch_y + ch_h / 2, title,
                  fontsize=11, ha='center', va='center',
                  color=COLORS['chapter_text'])
        draw_text(ax, cx + ch_w / 2, ch_y + 0.012, f'（{desc}）',
                  fontsize=9.5, ha='center', va='center',
                  color=COLORS['text_gray'])
        # 章节间箭头
        if i < 2:
            draw_arrow(ax,
                       (cx + ch_w + 0.005, ch_y + ch_h / 2),
                       (cx + ch_w + ch_gap - 0.005, ch_y + ch_h / 2),
                       COLORS['arrow_gray'], 1.5, 10)

    # ==================================================================
    # 第一部分 → 第二部分 箭头
    # ==================================================================
    p2_y, p2_h = 0.695, 0.098
    draw_arrow(ax, (0.5, p1_y - 0.005), (0.5, p2_y + p2_h + 0.005),
               COLORS['arrow_gray'], 2.0, 12)

    # ==================================================================
    # 第二部分：理论构建（第4章）
    # ==================================================================
    draw_rounded_box(ax, PART_X, p2_y, PART_W, p2_h,
                     COLORS['part2_fill'], COLORS['part2_stroke'], 2.0, 0.015)
    draw_text(ax, 0.5, p2_y + p2_h - 0.018,
              '第二部分：理论构建（第4章）',
              fontsize=14, bold=True, ha='center', va='center',
              color=COLORS['part2_text'])

    # 单个章节框（居中）
    ch4_w, ch4_h = 0.45, 0.058
    ch4_x = 0.5 - ch4_w / 2
    ch4_y = p2_y + 0.008
    draw_rounded_box(ax, ch4_x, ch4_y, ch4_w, ch4_h,
                     COLORS['chapter_fill'], COLORS['chapter_stroke'],
                     1.2, 0.008)
    draw_text(ax, 0.5, ch4_y + ch4_h - 0.014, '第4章',
              fontsize=12, bold=True, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, 0.5, ch4_y + ch4_h / 2 - 0.002, '研究设计与方法',
              fontsize=11, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, 0.5, ch4_y + 0.008, '（假设与方法）',
              fontsize=9.5, ha='center', va='center',
              color=COLORS['text_gray'])

    # ==================================================================
    # 第二部分 → 第三部分 箭头
    # ==================================================================
    p3_y, p3_h = 0.365, 0.295
    draw_arrow(ax, (0.5, p2_y - 0.005), (0.5, p3_y + p3_h + 0.005),
               COLORS['arrow_gray'], 2.0, 12)

    # ==================================================================
    # 第三部分：实证分析（第5-7章）
    # ==================================================================
    draw_rounded_box(ax, PART_X, p3_y, PART_W, p3_h,
                     COLORS['part3_fill'], COLORS['part3_stroke'], 2.0, 0.015)
    draw_text(ax, 0.5, p3_y + p3_h - 0.022,
              '第三部分：实证分析（第5-7章）',
              fontsize=14, bold=True, ha='center', va='center',
              color=COLORS['part3_text'])

    # 三个Q章节框
    q_w, q_h, q_gap = 0.22, 0.145, 0.05
    total_qw = 3 * q_w + 2 * q_gap
    q_sx = PART_X + (PART_W - total_qw) / 2
    q_y = p3_y + 0.045

    # Q1 - 第5章
    q1_x = q_sx
    draw_rounded_box(ax, q1_x, q_y, q_w, q_h,
                     COLORS['chapter_fill'], COLORS['chapter_stroke'],
                     1.5, 0.010)
    draw_text(ax, q1_x + q_w / 2, q_y + q_h - 0.020, '第5章',
              fontsize=12, bold=True, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, q1_x + q_w / 2, q_y + q_h - 0.044, 'Q1 类型特征',
              fontsize=11, bold=True, ha='center', va='center',
              color=COLORS['highlight_text'])
    draw_text(ax, q1_x + q_w / 2, q_y + q_h / 2 - 0.008, 'H1-1, H1-2',
              fontsize=10, ha='center', va='center',
              color=COLORS['text_gray'])
    draw_text(ax, q1_x + q_w / 2, q_y + 0.015, '（描述充分性）',
              fontsize=9.5, ha='center', va='center',
              color=COLORS['text_gray'])

    # Q2 - 第6章
    q2_x = q_sx + q_w + q_gap
    draw_rounded_box(ax, q2_x, q_y, q_w, q_h,
                     COLORS['chapter_fill'], COLORS['chapter_stroke'],
                     1.5, 0.010)
    draw_text(ax, q2_x + q_w / 2, q_y + q_h - 0.020, '第6章',
              fontsize=12, bold=True, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, q2_x + q_w / 2, q_y + q_h - 0.044, 'Q2 网络组织',
              fontsize=11, bold=True, ha='center', va='center',
              color=COLORS['part3_text'])
    draw_text(ax, q2_x + q_w / 2, q_y + q_h / 2 - 0.008, 'H2',
              fontsize=10, ha='center', va='center',
              color=COLORS['text_gray'])
    draw_text(ax, q2_x + q_w / 2, q_y + 0.015, '（横向扩展）',
              fontsize=9.5, ha='center', va='center',
              color=COLORS['text_gray'])

    # Q3 - 第7章
    q3_x = q_sx + 2 * (q_w + q_gap)
    draw_rounded_box(ax, q3_x, q_y, q_w, q_h,
                     COLORS['chapter_fill'], COLORS['chapter_stroke'],
                     1.5, 0.010)
    draw_text(ax, q3_x + q_w / 2, q_y + q_h - 0.020, '第7章',
              fontsize=12, bold=True, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, q3_x + q_w / 2, q_y + q_h - 0.044, 'Q3 认知机制',
              fontsize=11, bold=True, ha='center', va='center',
              color=COLORS['highlight_text'])
    draw_text(ax, q3_x + q_w / 2, q_y + q_h / 2 - 0.008, 'H3-1, H3-2',
              fontsize=10, ha='center', va='center',
              color=COLORS['text_gray'])
    draw_text(ax, q3_x + q_w / 2, q_y + 0.015, '（解释充分性）',
              fontsize=9.5, ha='center', va='center',
              color=COLORS['text_gray'])

    # Q1-Q3 认识论递进 U形括号
    q1_cx = q1_x + q_w / 2
    q3_cx = q3_x + q_w / 2
    bracket_by = q_y - 0.030

    bc = COLORS['highlight_stroke']
    blw = 1.8
    # Q1底部竖线
    ax.plot([q1_cx, q1_cx], [q_y - 0.003, bracket_by],
            color=bc, linewidth=blw, solid_capstyle='round')
    # Q3底部竖线
    ax.plot([q3_cx, q3_cx], [q_y - 0.003, bracket_by],
            color=bc, linewidth=blw, solid_capstyle='round')
    # 底部水平线（左半）
    ax.plot([q1_cx, 0.5 - 0.050], [bracket_by, bracket_by],
            color=bc, linewidth=blw, solid_capstyle='round')
    # 底部水平线（右半）
    ax.plot([0.5 + 0.050, q3_cx], [bracket_by, bracket_by],
            color=bc, linewidth=blw, solid_capstyle='round')
    # "认识论递进"标签
    draw_text(ax, 0.5, bracket_by, '认识论递进',
              fontsize=10, bold=True, ha='center', va='center',
              color=COLORS['highlight_text'],
              bbox=dict(boxstyle='round,pad=0.2',
                        facecolor=COLORS['part3_fill'],
                        edgecolor='none', alpha=1.0))

    # Q1→Q2 箭头
    draw_arrow(ax, (q1_x + q_w + 0.008, q_y + q_h / 2),
               (q2_x - 0.008, q_y + q_h / 2),
               COLORS['part3_stroke'], 1.8, 10)
    # Q3→Q2 箭头
    draw_arrow(ax, (q3_x - 0.008, q_y + q_h / 2),
               (q2_x + q_w + 0.008, q_y + q_h / 2),
               COLORS['part3_stroke'], 1.8, 10)

    # ==================================================================
    # 第三部分 → 第四部分 箭头
    # ==================================================================
    p4_y, p4_h = 0.090, 0.240
    draw_arrow(ax, (0.5, p3_y - 0.005), (0.5, p4_y + p4_h + 0.005),
               COLORS['arrow_gray'], 2.0, 12)

    # ==================================================================
    # 第四部分：综合讨论（第8-9章）
    # ==================================================================
    draw_rounded_box(ax, PART_X, p4_y, PART_W, p4_h,
                     COLORS['part4_fill'], COLORS['part4_stroke'], 2.0, 0.015)
    draw_text(ax, 0.5, p4_y + p4_h - 0.022,
              '第四部分：综合讨论（第8-9章）',
              fontsize=14, bold=True, ha='center', va='center',
              color=COLORS['part4_text'])

    # 两个章节框
    ch8_w, ch9_w = 0.30, 0.25
    ch89_h = 0.115
    ch89_gap = 0.12
    total_89w = ch8_w + ch9_w + ch89_gap
    ch89_sx = PART_X + (PART_W - total_89w) / 2
    ch89_y = p4_y + 0.040

    # 第8章
    ch8_x = ch89_sx
    draw_rounded_box(ax, ch8_x, ch89_y, ch8_w, ch89_h,
                     COLORS['chapter_fill'], COLORS['chapter_stroke'],
                     1.5, 0.010)
    draw_text(ax, ch8_x + ch8_w / 2, ch89_y + ch89_h - 0.020, '第8章',
              fontsize=12, bold=True, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, ch8_x + ch8_w / 2, ch89_y + ch89_h / 2, '综合讨论',
              fontsize=12, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, ch8_x + ch8_w / 2, ch89_y + 0.016, '（发现整合与理论贡献）',
              fontsize=9.5, ha='center', va='center',
              color=COLORS['text_gray'])

    # 第9章
    ch9_x = ch89_sx + ch8_w + ch89_gap
    draw_rounded_box(ax, ch9_x, ch89_y, ch9_w, ch89_h,
                     COLORS['chapter_fill'], COLORS['chapter_stroke'],
                     1.5, 0.010)
    draw_text(ax, ch9_x + ch9_w / 2, ch89_y + ch89_h - 0.020, '第9章',
              fontsize=12, bold=True, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, ch9_x + ch9_w / 2, ch89_y + ch89_h / 2, '结论',
              fontsize=12, ha='center', va='center',
              color=COLORS['chapter_text'])
    draw_text(ax, ch9_x + ch9_w / 2, ch89_y + 0.016, '（总结与展望）',
              fontsize=9.5, ha='center', va='center',
              color=COLORS['text_gray'])

    # 第8章 → 第9章 箭头
    draw_arrow(ax, (ch8_x + ch8_w + 0.015, ch89_y + ch89_h / 2),
               (ch9_x - 0.015, ch89_y + ch89_h / 2),
               COLORS['arrow_gray'], 1.8, 12)

    # ==================================================================
    # 底部说明
    # ==================================================================
    draw_text(ax, 0.5, 0.035,
              '注：四个部分体现\u201c问题驱动理论\u2014理论指导实证\u2014'
              '实证检验理论\u201d的逻辑闭环',
              fontsize=10, ha='center', va='center',
              color=COLORS['text_gray'])

    return fig, ax

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    fig, ax = create_structure_figure()

    png_path = os.path.join(output_dir, '图2 论文整体结构.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f'已保存: {png_path}')


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
    print('图2 论文整体结构 绘制完成！')
