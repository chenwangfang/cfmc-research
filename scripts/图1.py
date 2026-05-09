#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图1 研究路径图（按论文实际内容修正）
用于博士论文第一章
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import matplotlib.font_manager as fm
import os

# =============================================================================
# 字体设置
# =============================================================================
font_paths = [
    "/mnt/c/Windows/Fonts/msyh.ttc",      # WSL路径 - 微软雅黑
    "/mnt/c/Windows/Fonts/msyhbd.ttc",    # 微软雅黑粗体
    "/mnt/c/Windows/Fonts/simsun.ttc",    # 宋体
    "C:/Windows/Fonts/msyh.ttc",          # Windows原生路径
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
    'sullivan_red_fill': '#fadbd8',
    'sullivan_red_stroke': '#c0392b',
    'sullivan_red_text': '#922b21',
    'integration_blue_fill': '#eaf2f8',
    'integration_blue_stroke': '#2874a6',
    'integration_blue_light': '#d4e6f1',
    'cfmc_green_fill': '#d5f5e3',
    'cfmc_green_stroke': '#1e8449',
    'cfmc_green_text': '#145a32',
    'cfmc_green_light': '#27ae60',
    'tool_yellow_fill': '#fef9e7',
    'tool_yellow_stroke': '#d4ac0d',
    'tool_yellow_text': '#7d6608',
    'tool_purple_fill': '#f5eef8',
    'tool_purple_stroke': '#8e44ad',
    'tool_purple_text': '#512e5f',
    'tool_cyan_fill': '#e8f6f3',
    'tool_cyan_stroke': '#17a589',
    'tool_cyan_text': '#0e6655',
    'question_bg': '#fdfefe',
    'q1q3_fill': '#ebf5fb',
    'q1q3_stroke': '#2980b9',
    'q2_fill': '#e8f8f5',
    'q2_stroke': '#17a589',
    'q2_text': '#0e6655',
    'gray': '#4a5568',
    'arrow_dark': '#2d3748',
    'white': '#ffffff',
    'border': '#2d3748',
}

# =============================================================================
# 绘图辅助函数
# =============================================================================
def draw_text(ax, x, y, text, fontsize=10, bold=False, **kwargs):
    """绘制文本（自动应用中文字体）"""
    fp = FONT_PROP_BOLD if bold else FONT_PROP
    return ax.text(x, y, text, fontsize=fontsize, fontproperties=fp, **kwargs)

def draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color, linewidth=1.5, radius=0.02):
    """绘制圆角矩形"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill_color,
        edgecolor=stroke_color,
        linewidth=linewidth,
        transform=ax.transData
    )
    ax.add_patch(box)
    return box

def draw_arrow(ax, start, end, color='#2d3748', linewidth=2.0, head_scale=15):
    """绘制箭头"""
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=linewidth,
                               mutation_scale=head_scale))

def draw_line(ax, start, end, color='#2d3748', linewidth=1.5):
    """绘制直线"""
    ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=linewidth)

# =============================================================================
# 主绘图函数
# =============================================================================
def create_research_path_figure():
    """创建研究路径图"""

    # 创建画布（宽10英寸，高16英寸，纵向流程图，增加高度以容纳三个工具框）
    fig, ax = plt.subplots(1, 1, figsize=(10, 16))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 不绘制外边框，使图形更简洁美观

    # ==========================================================================
    # 统一间距参数
    # ==========================================================================
    gap = 0.028  # 统一的垂直间距（增大以使各部分间隔更明显）

    # ==========================================================================
    # 标题（已删除，论文中图表标题应在图表下方以可编辑文字形式呈现）
    # ==========================================================================

    # ==========================================================================
    # Sullivan理论框（顶部红色框）
    # ==========================================================================
    sullivan_y = 0.920
    sullivan_h = 0.038
    draw_rounded_box(ax, 0.35, sullivan_y, 0.30, sullivan_h,
                     COLORS['sullivan_red_fill'], COLORS['sullivan_red_stroke'], 2, 0.012)
    draw_text(ax, 0.5, sullivan_y + 0.025, 'Sullivan理论', fontsize=15, bold=True,
              ha='center', va='center', color=COLORS['sullivan_red_text'])
    draw_text(ax, 0.5, sullivan_y + 0.009, '七类待拓展领域', fontsize=11,
              ha='center', va='center', color=COLORS['sullivan_red_text'])

    # ==========================================================================
    # 三向整合策略框
    # ==========================================================================
    integration_h = 0.062
    integration_y = sullivan_y - gap - integration_h

    # Sullivan到三向整合的箭头
    draw_arrow(ax, (0.5, sullivan_y - 0.003), (0.5, integration_y + integration_h + 0.003),
               COLORS['arrow_dark'], 2.0, 16)

    draw_rounded_box(ax, 0.08, integration_y, 0.84, integration_h,
                     COLORS['integration_blue_fill'], COLORS['integration_blue_stroke'], 2, 0.015)
    draw_text(ax, 0.5, integration_y + integration_h - 0.014, '三向整合策略', fontsize=15, bold=True,
              ha='center', va='center', color=COLORS['title_blue'])

    # 三个子框
    sub_box_y = integration_y + 0.008
    sub_box_h = 0.032
    sub_box_w = 0.24

    # 借鉴Langacker (Q1,Q3)
    draw_rounded_box(ax, 0.10, sub_box_y, sub_box_w, sub_box_h,
                     COLORS['integration_blue_light'], COLORS['integration_blue_stroke'], 1.2, 0.008)
    draw_text(ax, 0.22, sub_box_y + 0.021, '借鉴Langacker', fontsize=11,
              ha='center', va='center', color=COLORS['title_blue'])
    draw_text(ax, 0.22, sub_box_y + 0.007, '(Q1,Q3)', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # 整合Goldberg (Q2)
    draw_rounded_box(ax, 0.38, sub_box_y, sub_box_w, sub_box_h,
                     COLORS['integration_blue_light'], COLORS['integration_blue_stroke'], 1.2, 0.008)
    draw_text(ax, 0.50, sub_box_y + 0.021, '整合Goldberg', fontsize=11,
              ha='center', va='center', color=COLORS['title_blue'])
    draw_text(ax, 0.50, sub_box_y + 0.007, '(Q2)', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # 聚焦汉语特色 (Q1-Q3)
    draw_rounded_box(ax, 0.66, sub_box_y, sub_box_w, sub_box_h,
                     COLORS['integration_blue_light'], COLORS['integration_blue_stroke'], 1.2, 0.008)
    draw_text(ax, 0.78, sub_box_y + 0.021, '聚焦汉语特色', fontsize=11,
              ha='center', va='center', color=COLORS['title_blue'])
    draw_text(ax, 0.78, sub_box_y + 0.007, '(Q1-Q3)', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # ==========================================================================
    # CFMC框（三层次协同）- 增大高度，确保标题与内容不重叠
    # ==========================================================================
    cfmc_h = 0.125
    cfmc_y = integration_y - gap - cfmc_h
    cfmc_top = cfmc_y + cfmc_h

    # 三个箭头从三向整合到CFMC
    draw_arrow(ax, (0.22, integration_y - 0.003), (0.22, cfmc_top + 0.003), COLORS['arrow_dark'], 1.8, 14)
    draw_arrow(ax, (0.50, integration_y - 0.003), (0.50, cfmc_top + 0.003), COLORS['arrow_dark'], 1.8, 14)
    draw_arrow(ax, (0.78, integration_y - 0.003), (0.78, cfmc_top + 0.003), COLORS['arrow_dark'], 1.8, 14)

    draw_rounded_box(ax, 0.08, cfmc_y, 0.84, cfmc_h,
                     COLORS['cfmc_green_fill'], COLORS['cfmc_green_stroke'], 2, 0.015)
    draw_text(ax, 0.5, cfmc_y + cfmc_h - 0.018, 'CFMC（三层次协同）', fontsize=15, bold=True,
              ha='center', va='center', color=COLORS['cfmc_green_text'])

    # 层次1+2子框（标题下方留足间距）
    level12_y = cfmc_y + 0.062
    level12_h = 0.038
    draw_rounded_box(ax, 0.12, level12_y, 0.76, level12_h,
                     COLORS['white'], COLORS['cfmc_green_stroke'], 1.2, 0.008)
    draw_text(ax, 0.5, level12_y + 0.025, '层次1 映射机制  —  层次2 语码实现', fontsize=11,
              ha='center', va='center', color=COLORS['cfmc_green_stroke'])
    draw_text(ax, 0.5, level12_y + 0.009, '(Q1+Q3)', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # 层次3子框
    level3_y = cfmc_y + 0.012
    level3_h = 0.032
    draw_rounded_box(ax, 0.12, level3_y, 0.76, level3_h,
                     COLORS['white'], COLORS['cfmc_green_stroke'], 1.2, 0.008)
    draw_text(ax, 0.5, level3_y + 0.016, '层次3 网络关联 (Q2)', fontsize=11,
              ha='center', va='center', color=COLORS['cfmc_green_stroke'])

    # 协同标记放在右侧
    mid_point_y = (level12_y + level3_y + level3_h) / 2
    draw_arrow(ax, (0.89, level12_y + 0.008), (0.89, level3_y + level3_h - 0.008),
               COLORS['cfmc_green_text'], 1.5, 10)
    draw_arrow(ax, (0.91, level3_y + level3_h - 0.008), (0.91, level12_y + 0.008),
               COLORS['cfmc_green_text'], 1.5, 10)
    draw_text(ax, 0.94, mid_point_y, '协同', fontsize=11,
              ha='left', va='center', color=COLORS['cfmc_green_text'])

    # ==========================================================================
    # 三个核心工具框
    # ==========================================================================
    tool_h = 0.155
    gap_cfmc_to_tool = 0.048  # CFMC → 核心工具框的间距
    tool_y = cfmc_y - gap_cfmc_to_tool - tool_h
    tool_top = tool_y + tool_h
    tool_w = 0.26

    left_x = 0.17      # 左框中心（双维度分类体系）
    mid_x = 0.50       # 中框中心（四类链接关系）
    right_x = 0.83     # 右框中心（四阶段认知编码机制）

    fork_start_y = cfmc_y
    branch_y = cfmc_y - gap_cfmc_to_tool/2  # 分叉线位于间距中间

    draw_line(ax, (0.5, fork_start_y), (0.5, branch_y), COLORS['arrow_dark'], 2.0)
    draw_line(ax, (left_x, branch_y), (right_x, branch_y), COLORS['arrow_dark'], 2.0)
    draw_arrow(ax, (left_x, branch_y), (left_x, tool_top + 0.002), COLORS['arrow_dark'], 2.0, 14)
    draw_arrow(ax, (mid_x, branch_y), (mid_x, tool_top + 0.002), COLORS['arrow_dark'], 2.0, 14)
    draw_arrow(ax, (right_x, branch_y), (right_x, tool_top + 0.002), COLORS['arrow_dark'], 2.0, 14)

    # ==========================================================================
    # 双维度分类体系框（左侧黄色框）- Q1核心工具
    # ==========================================================================
    left_box_x = 0.04
    draw_rounded_box(ax, left_box_x, tool_y, tool_w, tool_h,
                     COLORS['tool_yellow_fill'], COLORS['tool_yellow_stroke'], 2, 0.015)
    draw_text(ax, left_x, tool_y + tool_h - 0.018, '双维度分类体系', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['tool_yellow_text'])
    draw_text(ax, left_x, tool_y + tool_h - 0.035, '（Q1核心工具）', fontsize=10,
              ha='center', va='center', color=COLORS['tool_yellow_stroke'])

    # 认知通达度
    draw_text(ax, left_x, tool_y + tool_h - 0.058, '认知通达度', fontsize=10,
              ha='center', va='center', color=COLORS['tool_yellow_text'])
    draw_text(ax, left_x, tool_y + tool_h - 0.073, '(3级)', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # 乘号 ×
    draw_text(ax, left_x, tool_y + tool_h - 0.090, '×', fontsize=16, bold=True,
              ha='center', va='center', color=COLORS['tool_yellow_text'])

    # 概念复杂度
    draw_text(ax, left_x, tool_y + tool_h - 0.108, '概念复杂度', fontsize=10,
              ha='center', va='center', color=COLORS['tool_yellow_text'])
    draw_text(ax, left_x, tool_y + tool_h - 0.123, '(4类)', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # 箭头
    draw_text(ax, left_x, tool_y + tool_h - 0.138, '↓', fontsize=14,
              ha='center', va='center', color=COLORS['tool_yellow_text'])

    # 12类构式
    draw_text(ax, left_x, tool_y + 0.012, '12类构式', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['tool_yellow_text'])

    # ==========================================================================
    # 四类链接关系框（中间青色框）- Q2核心工具
    # ==========================================================================
    mid_box_x = 0.37
    draw_rounded_box(ax, mid_box_x, tool_y, tool_w, tool_h,
                     COLORS['tool_cyan_fill'], COLORS['tool_cyan_stroke'], 2, 0.015)
    draw_text(ax, mid_x, tool_y + tool_h - 0.018, '四类链接关系', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['tool_cyan_text'])
    draw_text(ax, mid_x, tool_y + tool_h - 0.035, '（Q2核心工具）', fontsize=10,
              ha='center', va='center', color=COLORS['tool_cyan_stroke'])

    # 四类链接
    links = ['· 隐喻扩展链接', '· 多义链接', '· 实例链接', '· 子部分链接']
    for i, link in enumerate(links):
        draw_text(ax, mid_x, tool_y + tool_h - 0.060 - i*0.022, link, fontsize=10,
                  ha='center', va='center', color=COLORS['tool_cyan_text'])

    # ==========================================================================
    # 四阶段认知编码机制框（右侧紫色框）- Q3核心工具
    # ==========================================================================
    right_box_x = 0.70
    draw_rounded_box(ax, right_box_x, tool_y, tool_w, tool_h,
                     COLORS['tool_purple_fill'], COLORS['tool_purple_stroke'], 2, 0.015)
    draw_text(ax, right_x, tool_y + tool_h - 0.018, '四阶段认知编码机制', fontsize=13, bold=True,
              ha='center', va='center', color=COLORS['tool_purple_text'])
    draw_text(ax, right_x, tool_y + tool_h - 0.035, '（Q3核心工具）', fontsize=10,
              ha='center', va='center', color=COLORS['tool_purple_stroke'])

    # 四个阶段
    stages = ['认知域激活 →', '参照点锚定 →', '跨域映射 →', '语言编码']
    for i, stage in enumerate(stages):
        draw_text(ax, right_x, tool_y + tool_h - 0.060 - i*0.025, stage, fontsize=10,
                  ha='center', va='center', color=COLORS['tool_purple_text'])

    # ==========================================================================
    # 三个工具框汇合到研究问题（动态计算位置）
    # ==========================================================================
    gap_tool_to_q = 0.048  # 核心工具框 → 研究问题的间距
    q_area_y = 0.040  # 底部固定位置
    q_area_top = tool_y - gap_tool_to_q  # 顶部根据工具框位置计算
    q_area_h = q_area_top - q_area_y  # 高度动态计算

    merge_start_y = tool_y
    merge_line_y = tool_y - gap_tool_to_q/2  # 汇合线位于间距中间

    draw_line(ax, (left_x, merge_start_y), (left_x, merge_line_y), COLORS['arrow_dark'], 2.0)
    draw_line(ax, (mid_x, merge_start_y), (mid_x, merge_line_y), COLORS['arrow_dark'], 2.0)
    draw_line(ax, (right_x, merge_start_y), (right_x, merge_line_y), COLORS['arrow_dark'], 2.0)
    draw_line(ax, (left_x, merge_line_y), (right_x, merge_line_y), COLORS['arrow_dark'], 2.0)
    draw_arrow(ax, (0.5, merge_line_y), (0.5, q_area_top + 0.002), COLORS['arrow_dark'], 2.0, 16)

    # ==========================================================================
    # 三个研究问题区域框（内部使用相对定位）
    # ==========================================================================
    draw_rounded_box(ax, 0.06, q_area_y, 0.88, q_area_h,
                     COLORS['question_bg'], COLORS['title_blue'], 2.5, 0.020)
    draw_text(ax, 0.5, q_area_y + q_area_h - 0.018, '三个研究问题（核心递进 + 横向扩展）',
              fontsize=15, bold=True, ha='center', va='center', color=COLORS['title_blue'])

    # 内部可用空间（去除标题和边距）
    inner_top = q_area_y + q_area_h - 0.038  # 标题下方
    inner_bottom = q_area_y + 0.012  # 底部边距
    inner_h = inner_top - inner_bottom

    # ==========================================================================
    # Sullivan核心主线框（占内部空间上部55%）
    # ==========================================================================
    sullivan_main_h = inner_h * 0.52
    sullivan_main_y = inner_top - sullivan_main_h
    draw_rounded_box(ax, 0.10, sullivan_main_y, 0.80, sullivan_main_h,
                     COLORS['q1q3_fill'], COLORS['q1q3_stroke'], 1.5, 0.015)
    draw_text(ax, 0.5, sullivan_main_y + sullivan_main_h - 0.015, 'Sullivan核心主线（描写-解释递进）',
              fontsize=13, bold=True, ha='center', va='center', color=COLORS['title_blue'])

    # Q1框和Q3框（适当高度，文字不重叠）
    q_box_w = 0.20
    q_box_h = 0.078  # 适当高度，确保4行文字不重叠
    q1_x = 0.14
    # 垂直居中放置在Sullivan主线框内
    q1_y = sullivan_main_y + (sullivan_main_h - 0.030 - q_box_h) / 2

    draw_rounded_box(ax, q1_x, q1_y, q_box_w, q_box_h,
                     COLORS['white'], COLORS['q1q3_stroke'], 1.5, 0.010)
    # 4行文字均匀分布（从上到下）
    draw_text(ax, q1_x + q_box_w/2, q1_y + q_box_h - 0.012, 'Q1', fontsize=15, bold=True,
              ha='center', va='center', color=COLORS['title_blue'])
    draw_text(ax, q1_x + q_box_w/2, q1_y + q_box_h - 0.030, '类型特征', fontsize=11,
              ha='center', va='center', color=COLORS['integration_blue_stroke'])
    draw_text(ax, q1_x + q_box_w/2, q1_y + q_box_h - 0.048, '(WHAT)', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])
    draw_text(ax, q1_x + q_box_w/2, q1_y + q_box_h - 0.066, '层次1+2', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # Q3框
    q3_x = 0.66
    q3_y = q1_y

    draw_rounded_box(ax, q3_x, q3_y, q_box_w, q_box_h,
                     COLORS['white'], COLORS['q1q3_stroke'], 1.5, 0.010)
    draw_text(ax, q3_x + q_box_w/2, q3_y + q_box_h - 0.012, 'Q3', fontsize=15, bold=True,
              ha='center', va='center', color=COLORS['title_blue'])
    draw_text(ax, q3_x + q_box_w/2, q3_y + q_box_h - 0.030, '认知机制', fontsize=11,
              ha='center', va='center', color=COLORS['integration_blue_stroke'])
    draw_text(ax, q3_x + q_box_w/2, q3_y + q_box_h - 0.048, '(WHY)', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])
    draw_text(ax, q3_x + q_box_w/2, q3_y + q_box_h - 0.066, '层次1+2', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # Q1到Q3的描写-解释递进箭头
    arrow_y = q1_y + q_box_h/2
    ax.annotate('', xy=(q3_x - 0.012, arrow_y), xytext=(q1_x + q_box_w + 0.012, arrow_y),
                arrowprops=dict(arrowstyle='->', color=COLORS['title_blue'], lw=2.5,
                               mutation_scale=16))
    draw_text(ax, 0.5, arrow_y + 0.015, '描写-解释递进', fontsize=10, bold=True,
              ha='center', va='center', color=COLORS['title_blue'])

    # ==========================================================================
    # Goldberg扩展维度框（占内部空间下部40%）
    # ==========================================================================
    goldberg_h = inner_h * 0.40
    goldberg_y = inner_bottom
    draw_rounded_box(ax, 0.10, goldberg_y, 0.80, goldberg_h,
                     COLORS['q2_fill'], COLORS['q2_stroke'], 1.5, 0.015)
    draw_text(ax, 0.5, goldberg_y + goldberg_h - 0.015, 'Goldberg扩展维度（网络组织）',
              fontsize=13, bold=True, ha='center', va='center', color=COLORS['q2_text'])

    # Q2框（适当高度，文字不重叠）
    q2_w = 0.20
    q2_h = 0.058  # 适当高度，确保3行文字不重叠
    q2_x = 0.5 - q2_w/2
    # 垂直居中放置在Goldberg框内
    q2_y = goldberg_y + (goldberg_h - 0.030 - q2_h) / 2

    draw_rounded_box(ax, q2_x, q2_y, q2_w, q2_h,
                     COLORS['white'], COLORS['q2_stroke'], 1.5, 0.010)
    # 3行文字均匀分布（从上到下）
    draw_text(ax, 0.5, q2_y + q2_h - 0.012, 'Q2', fontsize=15, bold=True,
              ha='center', va='center', color=COLORS['q2_text'])
    draw_text(ax, 0.5, q2_y + q2_h - 0.030, '网络组织', fontsize=11,
              ha='center', va='center', color=COLORS['q2_stroke'])
    draw_text(ax, 0.5, q2_y + q2_h - 0.048, '(HOW)  层次3', fontsize=11,
              ha='center', va='center', color=COLORS['gray'])

    # Q1到Q2的节点输入线
    q1_center_x = q1_x + q_box_w/2
    q2_left = q2_x
    link_y = q2_y + q2_h/2 + 0.008

    draw_line(ax, (q1_center_x, q1_y - 0.002), (q1_center_x, link_y), COLORS['gray'], 1.5)
    draw_arrow(ax, (q1_center_x, link_y), (q2_left - 0.010, link_y), COLORS['gray'], 1.5, 10)
    draw_text(ax, (q1_center_x + q2_left)/2 - 0.015, link_y + 0.012, '节点输入', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    # Q3到Q2的机制参照线
    q3_center_x = q3_x + q_box_w/2
    q2_right = q2_x + q2_w

    draw_line(ax, (q3_center_x, q3_y - 0.002), (q3_center_x, link_y), COLORS['gray'], 1.5)
    draw_arrow(ax, (q3_center_x, link_y), (q2_right + 0.010, link_y), COLORS['gray'], 1.5, 10)
    draw_text(ax, (q3_center_x + q2_right)/2 + 0.015, link_y + 0.012, '机制参照', fontsize=10,
              ha='center', va='center', color=COLORS['gray'])

    # 横向扩展文字（放在Goldberg框底部）
    draw_text(ax, 0.5, goldberg_y + 0.006, '横向扩展', fontsize=11,
              ha='center', va='center', color=COLORS['q2_stroke'])

    return fig, ax

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 输出目录（与脚本目录分离）
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    fig, ax = create_research_path_figure()

    # 保存为PNG（300 DPI）
    png_path = os.path.join(output_dir, '图1 研究路径图.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f'已保存: {png_path}')

    # 保存为PDF（矢量格式）
    # pdf_path = os.path.join(script_dir, '图1 研究路径图.pdf')  # 已禁用PDF输出
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
    print('图1 研究路径图 绘制完成！')
