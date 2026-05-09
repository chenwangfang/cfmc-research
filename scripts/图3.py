#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图3 Sullivan理论的学术脉络与本研究定位（重新设计布局）
用于博士论文第二章

设计要点：
- Sullivan框下移，使两个红色箭头长度相等
- Fillmore→Goldberg用L型虚线：从Fillmore框下方→向下→向左→连接Goldberg框右侧中间
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
    'theory_fill': '#f8f9fa',
    'theory_stroke': '#6c757d',
    'theory_text': '#2c3e50',
    'era_bg': '#e9ecef',
    'era_text': '#495057',
    'sullivan_fill': '#fff5f5',
    'sullivan_stroke': '#c0392b',
    'sullivan_text': '#922b21',
    'current_fill': '#ebf3fb',
    'current_stroke': '#2874a6',
    'current_text': '#1a5276',
    'arrow_gray': '#7f8c8d',
    'influence_line': '#95a5a6',
    'white': '#ffffff',
    'light_gray': '#dee2e6',
    'text_gray': '#6c757d',
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

def draw_line(ax, start, end, color='#2d3748', linewidth=1.5, linestyle='-'):
    ax.plot([start[0], end[0]], [start[1], end[1]], color=color,
            linewidth=linewidth, linestyle=linestyle, solid_capstyle='round')

def draw_theory_box(ax, x, y, width, height, author, year, title, contribution,
                    fill_color, stroke_color, text_color):
    """绘制理论框"""
    draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color, 1.5, 0.008)
    draw_text(ax, x + width/2, y + height - 0.016, f'{author} ({year})',
              fontsize=10, bold=True, ha='center', va='center', color=text_color)
    if title and contribution:
        draw_text(ax, x + width/2, y + height/2, title,
                  fontsize=9, ha='center', va='center', color=text_color)
        draw_text(ax, x + width/2, y + 0.014, contribution,
                  fontsize=8, ha='center', va='center', color=COLORS['text_gray'])
    elif title:
        draw_text(ax, x + width/2, y + height/2 - 0.005, title,
                  fontsize=9, ha='center', va='center', color=text_color)
    elif contribution:
        draw_text(ax, x + width/2, y + height/2 - 0.005, contribution,
                  fontsize=8, ha='center', va='center', color=COLORS['text_gray'])

# =============================================================================
# 主绘图函数
# =============================================================================
def create_timeline_figure():
    fig, ax = plt.subplots(1, 1, figsize=(14, 13))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # ==========================================================================
    # 布局参数
    # ==========================================================================
    box_w = 0.155
    box_h = 0.065
    left_margin = 0.105
    gap = 0.030
    era_x = 0.038

    # 四列位置
    col1_x = left_margin
    col2_x = left_margin + box_w + gap
    col3_x = left_margin + 2 * (box_w + gap)
    col4_x = left_margin + 3 * (box_w + gap)

    # 列中心
    col1_center = col1_x + box_w / 2
    col2_center = col2_x + box_w / 2
    col3_center = col3_x + box_w / 2
    col4_center = col4_x + box_w / 2

    # ==========================================================================
    # 四大理论传统标题
    # ==========================================================================
    title_y = 0.950
    draw_text(ax, col1_center, title_y, '概念隐喻理论', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['theory_text'])
    draw_text(ax, col2_center, title_y, '认知语法', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['theory_text'])
    draw_text(ax, col3_center, title_y, '构式语法', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['theory_text'])
    draw_text(ax, col4_center, title_y, '框架语义学', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['theory_text'])

    # ==========================================================================
    # 1980s - 理论奠基
    # ==========================================================================
    y_1980 = 0.870

    draw_rounded_box(ax, 0.012, y_1980 + 0.006, 0.052, 0.025,
                     COLORS['era_bg'], COLORS['light_gray'], 1, 0.004)
    draw_text(ax, era_x, y_1980 + 0.018, '1980s', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['era_text'])

    # 列1：Lakoff & Johnson (1980)
    draw_theory_box(ax, col1_x, y_1980, box_w, box_h,
                    'Lakoff & Johnson', '1980', '概念隐喻理论', '奠基之作',
                    COLORS['theory_fill'], COLORS['theory_stroke'], COLORS['theory_text'])

    # 列2：Langacker (1987)
    draw_theory_box(ax, col2_x, y_1980, box_w, box_h,
                    'Langacker', '1987', '认知语法奠基', '自主-依存性理论',
                    COLORS['theory_fill'], COLORS['theory_stroke'], COLORS['theory_text'])

    # 列4：Fillmore (1982)
    draw_theory_box(ax, col4_x, y_1980, box_w, box_h,
                    'Fillmore', '1982', '框架语义学', '',
                    COLORS['theory_fill'], COLORS['theory_stroke'], COLORS['theory_text'])

    # ==========================================================================
    # 1990s - 理论发展
    # ==========================================================================
    y_1990 = 0.785

    draw_rounded_box(ax, 0.012, y_1990 + 0.006, 0.052, 0.025,
                     COLORS['era_bg'], COLORS['light_gray'], 1, 0.004)
    draw_text(ax, era_x, y_1990 + 0.018, '1990s', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['era_text'])

    # 列1：Grady (1997)
    draw_theory_box(ax, col1_x, y_1990, box_w, box_h,
                    'Grady', '1997', '初级隐喻理论', '',
                    COLORS['theory_fill'], COLORS['theory_stroke'], COLORS['theory_text'])

    # 列2：Langacker (1991)
    draw_theory_box(ax, col2_x, y_1990, box_w, box_h,
                    'Langacker', '1991', '系词认知分析', '',
                    COLORS['theory_fill'], COLORS['theory_stroke'], COLORS['theory_text'])

    # 列3：Goldberg (1995)
    draw_theory_box(ax, col3_x, y_1990, box_w, box_h,
                    'Goldberg', '1995', '构式语法奠基', '四类继承链接',
                    COLORS['theory_fill'], COLORS['theory_stroke'], COLORS['theory_text'])

    # ==========================================================================
    # 2000s - 理论深化
    # ==========================================================================
    y_2000 = 0.700

    draw_rounded_box(ax, 0.012, y_2000 + 0.006, 0.052, 0.025,
                     COLORS['era_bg'], COLORS['light_gray'], 1, 0.004)
    draw_text(ax, era_x, y_2000 + 0.018, '2000s', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['era_text'])

    # 列3：Goldberg (2006)
    draw_theory_box(ax, col3_x, y_2000, box_w, box_h,
                    'Goldberg', '2006', '构式网络理论', '',
                    COLORS['theory_fill'], COLORS['theory_stroke'], COLORS['theory_text'])

    # ==========================================================================
    # 理论传承线（实线 = 同一传统内发展）
    # ==========================================================================
    line_gap = 0.006

    # 列1：Lakoff & Johnson → Grady
    draw_line(ax, (col1_center, y_1980 - line_gap), (col1_center, y_1990 + box_h + line_gap),
              COLORS['arrow_gray'], 1.3)

    # 列2：Langacker (1987) → Langacker (1991)
    draw_line(ax, (col2_center, y_1980 - line_gap), (col2_center, y_1990 + box_h + line_gap),
              COLORS['arrow_gray'], 1.3)

    # 列3：Goldberg (1995) → Goldberg (2006)
    draw_line(ax, (col3_center, y_1990 - line_gap), (col3_center, y_2000 + box_h + line_gap),
              COLORS['arrow_gray'], 1.3)

    # ==========================================================================
    # 跨传统理论影响（L型虚线：Fillmore → Goldberg）
    # 从Fillmore框下方出发→向下→向左→连接Goldberg框右侧中间
    # ==========================================================================
    fillmore_bottom_center = (col4_center, y_1880 - line_gap) if 'y_1880' in dir() else (col4_center, y_1980 - line_gap)
    goldberg_right_mid = (col3_x + box_w + line_gap, y_1990 + box_h / 2)

    # L型拐点（先向下到Goldberg同一水平线，再向左）
    turn_y = y_1990 + box_h / 2
    turn_point = (col4_center, turn_y)

    # 绘制L型虚线
    # 第一段：从Fillmore下方向下
    draw_line(ax, (col4_center, y_1980 - line_gap), turn_point,
              COLORS['influence_line'], 1.3, '--')
    # 第二段：向左到Goldberg右侧（带箭头）
    ax.annotate('', xy=goldberg_right_mid, xytext=turn_point,
                arrowprops=dict(arrowstyle='->', color=COLORS['influence_line'],
                               lw=1.3, linestyle='--'))

    # 理论影响标注（在L型横线上方）
    mid_x = (turn_point[0] + goldberg_right_mid[0]) / 2
    draw_text(ax, mid_x, turn_y + 0.016, '理论影响', fontsize=8,
              ha='center', va='bottom', color=COLORS['text_gray'], style='italic')

    # ==========================================================================
    # 汇聚区（调整：缩短四根汇聚线）
    # ==========================================================================
    converge_y = 0.630  # 保持四根线短

    # 列1-3到汇聚线的竖线
    draw_line(ax, (col1_center, y_1990 - line_gap), (col1_center, converge_y),
              COLORS['arrow_gray'], 1.3)
    draw_line(ax, (col2_center, y_1990 - line_gap), (col2_center, converge_y),
              COLORS['arrow_gray'], 1.3)
    draw_line(ax, (col3_center, y_2000 - line_gap), (col3_center, converge_y),
              COLORS['arrow_gray'], 1.3)
    # 列4：Fillmore的线已经用于L型虚线，这里另起一条到汇聚线
    # Fillmore既影响Goldberg，也汇入Sullivan，所以需要分叉
    # 从L型拐点再引出一条到汇聚线
    draw_line(ax, turn_point, (col4_center, converge_y),
              COLORS['arrow_gray'], 1.3)

    # 汇聚横线
    draw_line(ax, (col1_center, converge_y), (col4_center, converge_y),
              COLORS['arrow_gray'], 1.8)

    sullivan_center_x = 0.5

    # ==========================================================================
    # Sullivan (2013) 核心整合框 - 下移使两个箭头等长
    # ==========================================================================
    # 本研究框底部位置（恢复，保持红色箭头区域小）
    current_y = 0.180
    current_h = 0.150

    # Sullivan框位置：使 (converge_y - sullivan_top) = (sullivan_bottom - current_top)
    # 即 sullivan_y + sullivan_h 到 converge_y 的距离 = current_y + current_h 到 sullivan_y 的距离
    # 设 sullivan_h = 0.085
    # converge_y - (sullivan_y + sullivan_h) = sullivan_y - (current_y + current_h)
    # converge_y - sullivan_y - sullivan_h = sullivan_y - current_y - current_h
    # converge_y + current_y + current_h - sullivan_h = 2 * sullivan_y
    # sullivan_y = (converge_y + current_y + current_h - sullivan_h) / 2
    sullivan_h = 0.085
    sullivan_y = (converge_y + current_y + current_h - sullivan_h) / 2
    sullivan_w = 0.50
    sullivan_x = sullivan_center_x - sullivan_w / 2

    # 从汇聚点到Sullivan的箭头（第一个红色箭头）
    arrow1_top = converge_y - 0.008
    arrow1_bottom = sullivan_y + sullivan_h + 0.008
    draw_arrow(ax, (sullivan_center_x, arrow1_top),
               (sullivan_center_x, arrow1_bottom),
               COLORS['sullivan_stroke'], 2.2, 12)

    # "四大理论传统汇聚"标签（放在第一个红色箭头右侧）
    arrow1_mid_y = (arrow1_top + arrow1_bottom) / 2
    draw_text(ax, sullivan_center_x + 0.035, arrow1_mid_y, '四大理论传统汇聚',
              fontsize=10, ha='left', va='center', color=COLORS['text_gray'])

    draw_rounded_box(ax, sullivan_x, sullivan_y, sullivan_w, sullivan_h,
                     COLORS['sullivan_fill'], COLORS['sullivan_stroke'], 2.5, 0.010)

    draw_rounded_box(ax, 0.012, sullivan_y + 0.024, 0.052, 0.025,
                     COLORS['era_bg'], COLORS['light_gray'], 1, 0.004)
    draw_text(ax, era_x, sullivan_y + 0.036, '2010s', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['era_text'])

    draw_text(ax, sullivan_center_x, sullivan_y + sullivan_h - 0.016,
              'Sullivan (2013)', fontsize=14, bold=True,
              ha='center', va='center', color=COLORS['sullivan_text'])

    draw_text(ax, sullivan_center_x, sullivan_y + sullivan_h / 2,
              '自主-依存原则：隐喻如何在构式中编码', fontsize=11,
              ha='center', va='center', color=COLORS['sullivan_text'])

    draw_text(ax, sullivan_center_x, sullivan_y + 0.013,
              '整合：概念隐喻理论 + 认知语法 + 构式语法 + 框架语义学', fontsize=9,
              ha='center', va='center', color=COLORS['text_gray'])

    # 理论整合标签
    draw_text(ax, sullivan_x + sullivan_w + 0.018, sullivan_y + sullivan_h / 2,
              '[ 理论整合 ]', fontsize=10, bold=True,
              ha='left', va='center', color=COLORS['sullivan_stroke'])

    # ==========================================================================
    # 本研究：三向整合
    # ==========================================================================
    current_w = 0.68
    current_x = sullivan_center_x - current_w / 2

    # 从Sullivan到本研究的箭头
    draw_arrow(ax, (sullivan_center_x, sullivan_y - 0.008),
               (sullivan_center_x, current_y + current_h + 0.008),
               COLORS['sullivan_stroke'], 2.2, 12)

    draw_text(ax, sullivan_center_x + 0.032, (sullivan_y + current_y + current_h) / 2,
              '汉语验证与整合', fontsize=10, ha='left', va='center',
              color=COLORS['sullivan_stroke'])

    draw_rounded_box(ax, current_x, current_y, current_w, current_h,
                     COLORS['current_fill'], COLORS['current_stroke'], 2, 0.010)

    draw_rounded_box(ax, 0.012, current_y + 0.055, 0.052, 0.025,
                     COLORS['era_bg'], COLORS['light_gray'], 1, 0.004)
    draw_text(ax, era_x, current_y + 0.067, '本研究', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['current_text'])

    draw_text(ax, sullivan_center_x, current_y + current_h - 0.020,
              'Sullivan理论的汉语检验与三向整合', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['current_text'])

    # 三个整合方向框
    int_box_w = 0.185
    int_box_h = 0.078
    int_box_y = current_y + 0.016
    int_gap = 0.022
    int_start_x = current_x + 0.030

    # 借鉴Langacker
    draw_rounded_box(ax, int_start_x, int_box_y, int_box_w, int_box_h,
                     COLORS['white'], COLORS['current_stroke'], 1.2, 0.005)
    draw_text(ax, int_start_x + int_box_w/2, int_box_y + int_box_h - 0.016,
              '借鉴Langacker', fontsize=11, bold=True,
              ha='center', va='center', color=COLORS['current_text'])
    draw_text(ax, int_start_x + int_box_w/2, int_box_y + int_box_h/2,
              '认知语法', fontsize=10,
              ha='center', va='center', color=COLORS['current_text'])
    draw_text(ax, int_start_x + int_box_w/2, int_box_y + 0.014,
              '深化认知机制', fontsize=9,
              ha='center', va='center', color=COLORS['text_gray'])

    # 整合Goldberg
    int_x2 = int_start_x + int_box_w + int_gap
    draw_rounded_box(ax, int_x2, int_box_y, int_box_w, int_box_h,
                     COLORS['white'], COLORS['current_stroke'], 1.2, 0.005)
    draw_text(ax, int_x2 + int_box_w/2, int_box_y + int_box_h - 0.016,
              '整合Goldberg', fontsize=11, bold=True,
              ha='center', va='center', color=COLORS['current_text'])
    draw_text(ax, int_x2 + int_box_w/2, int_box_y + int_box_h/2,
              '构式网络理论', fontsize=10,
              ha='center', va='center', color=COLORS['current_text'])
    draw_text(ax, int_x2 + int_box_w/2, int_box_y + 0.014,
              '补充网络组织', fontsize=9,
              ha='center', va='center', color=COLORS['text_gray'])

    # 聚焦汉语特色
    int_x3 = int_x2 + int_box_w + int_gap
    draw_rounded_box(ax, int_x3, int_box_y, int_box_w, int_box_h,
                     COLORS['white'], COLORS['current_stroke'], 1.2, 0.005)
    draw_text(ax, int_x3 + int_box_w/2, int_box_y + int_box_h - 0.016,
              '聚焦汉语特色', fontsize=11, bold=True,
              ha='center', va='center', color=COLORS['current_text'])
    draw_text(ax, int_x3 + int_box_w/2, int_box_y + int_box_h/2,
              '类型学特征', fontsize=10,
              ha='center', va='center', color=COLORS['current_text'])
    draw_text(ax, int_x3 + int_box_w/2, int_box_y + 0.014,
              '零系词、话题突出', fontsize=9,
              ha='center', va='center', color=COLORS['text_gray'])

    # ==========================================================================
    # 底部说明
    # ==========================================================================
    draw_text(ax, 0.5, 0.080,
              '注：灰色实线表示同一理论传统内的发展脉络，虚线表示跨传统的理论影响',
              fontsize=9, ha='center', va='center', color=COLORS['text_gray'])

    return fig, ax

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 输出目录（与脚本目录分离）
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    fig, ax = create_timeline_figure()

    png_path = os.path.join(output_dir, '图3 Sullivan理论的学术脉络与本研究定位.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f'已保存: {png_path}')

    # pdf_path = os.path.join(script_dir, '图3 Sullivan理论的学术脉络与本研究定位.pdf')  # 已禁用PDF输出
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
    print('图3 Sullivan理论的学术脉络与本研究定位 绘制完成！')
