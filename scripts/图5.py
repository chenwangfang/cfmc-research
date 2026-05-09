#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图5 CFMC三层框架结构图
用于博士论文第三章
来源：论文正文《汉语“是”字系表隐喻构式网络的认知机制分析》主稿文件第1224-1267行
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
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
    # 主色调
    'primary_blue': '#2c3e50',
    'white': '#ffffff',

    # Sullivan核心框（突出显示）
    'sullivan_fill': '#fff8f0',
    'sullivan_stroke': '#c0392b',
    'sullivan_text': '#922b21',

    # 三向整合框
    'langacker_fill': '#e8f4fd',
    'langacker_stroke': '#2874a6',
    'langacker_text': '#1a5276',

    'goldberg_fill': '#e8f8f5',
    'goldberg_stroke': '#1e8449',
    'goldberg_text': '#145a32',

    'chinese_fill': '#fef9e7',
    'chinese_stroke': '#b7950b',
    'chinese_text': '#7d6608',

    # CFMC三层结构框
    'cfmc_fill': '#f4f6f7',
    'cfmc_stroke': '#5d6d7e',
    'cfmc_text': '#2c3e50',

    # 研究问题框
    'q1_fill': '#fadbd8',
    'q1_stroke': '#c0392b',
    'q1_text': '#922b21',

    'q3_fill': '#f9ebea',      # 浅红色（比Q1稍浅，便于区分）
    'q3_stroke': '#a93226',    # 红色边框（比Q1稍深）
    'q3_text': '#7b241c',      # 深红文字

    'q2_fill': '#d6eaf8',
    'q2_stroke': '#2874a6',
    'q2_text': '#1a5276',

    # 辅助颜色
    'arrow_gray': '#7f8c8d',
    'text_gray': '#5d6d7e',
    'light_gray': '#ecf0f1',
    'outer_stroke': '#34495e',
}

# =============================================================================
# 绘图辅助函数
# =============================================================================
def draw_text(ax, x, y, text, fontsize=10, bold=False, **kwargs):
    fp = FONT_PROP_BOLD if bold else FONT_PROP
    return ax.text(x, y, text, fontsize=fontsize, fontproperties=fp, **kwargs)

def draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color,
                     linewidth=1.5, radius=0.01):
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill_color,
        edgecolor=stroke_color,
        linewidth=linewidth
    )
    ax.add_patch(box)
    return box

def draw_double_box(ax, x, y, width, height, fill_color, stroke_color, linewidth=2):
    """绘制双线框（用于Sullivan核心主干）- 增强双线效果"""
    # 外框（更粗，更深色）
    outer_color = '#8b0000'  # 深红色外框
    draw_rounded_box(ax, x, y, width, height, fill_color, outer_color, linewidth + 1, 0.012)
    # 内框（增大间距使双线更明显）
    margin = 0.012  # 增大margin使内外框间距更明显
    draw_rounded_box(ax, x + margin, y + margin, width - 2*margin, height - 2*margin,
                     fill_color, stroke_color, linewidth, 0.008)

def draw_arrow(ax, start, end, color='#2d3748', linewidth=1.5, head_scale=10, style='->'):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle=style, color=color, lw=linewidth,
                               mutation_scale=head_scale))

def draw_line(ax, start, end, color='#2d3748', linewidth=1.5, linestyle='-'):
    ax.plot([start[0], end[0]], [start[1], end[1]], color=color,
            linewidth=linewidth, linestyle=linestyle)

def draw_integration_box(ax, x, y, width, height, title, subtitle, items,
                         fill_color, stroke_color, text_color):
    """绘制三向整合的单个框 - 列表项横排布局"""
    draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color, 1.5, 0.008)

    # 标题
    draw_text(ax, x + width/2, y + height - 0.022, title,
              fontsize=13, bold=True, ha='center', va='center', color=text_color)
    # 副标题
    draw_text(ax, x + width/2, y + height - 0.046, subtitle,
              fontsize=12, ha='center', va='center', color=text_color)

    # 分隔线
    line_y = y + height - 0.064
    draw_line(ax, (x + 0.008, line_y), (x + width - 0.008, line_y), stroke_color, 0.8)

    # 列表项 - 横排布局
    row1_y = line_y - 0.022
    row2_y = line_y - 0.044

    if len(items) == 2:
        # 只有两项：居中显示在一排，用顿号分隔
        draw_text(ax, x + width/2, (row1_y + row2_y) / 2, f"{items[0]}、{items[1]}",
                  fontsize=11, ha='center', va='center', color=COLORS['text_gray'])
    elif len(items) >= 3:
        # 三项：前两项一排，第三项单独一排
        draw_text(ax, x + width/2, row1_y, f"{items[0]}、{items[1]}",
                  fontsize=11, ha='center', va='center', color=COLORS['text_gray'])
        draw_text(ax, x + width/2, row2_y, items[2],
                  fontsize=11, ha='center', va='center', color=COLORS['text_gray'])

def draw_q_box(ax, x, y, width, height, q_name, q_label, layer_info,
               fill_color, stroke_color, text_color):
    """绘制研究问题框"""
    draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color, 1.8, 0.006)

    # Q编号
    draw_text(ax, x + width/2, y + height - 0.018, q_name,
              fontsize=15, bold=True, ha='center', va='center', color=text_color)
    # 标签
    draw_text(ax, x + width/2, y + height/2, q_label,
              fontsize=13, ha='center', va='center', color=text_color)
    # 层次信息
    draw_text(ax, x + width/2, y + 0.016, layer_info,
              fontsize=11, ha='center', va='center', color=COLORS['text_gray'])

# =============================================================================
# 主绘图函数
# =============================================================================
def create_cfmc_figure():
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # =========================================================================
    # 框架标题（已删除，论文中图表标题应在图表下方以可编辑文字形式呈现）
    # =========================================================================

    # =========================================================================
    # Sullivan核心主干框（双线框）- 增大高度避免文字与框线重叠
    # =========================================================================
    sullivan_w = 0.72
    sullivan_h = 0.12  # 增大高度
    sullivan_x = 0.5 - sullivan_w / 2
    sullivan_y = 0.795

    draw_double_box(ax, sullivan_x, sullivan_y, sullivan_w, sullivan_h,
                    COLORS['sullivan_fill'], COLORS['sullivan_stroke'], 2)

    draw_text(ax, 0.5, sullivan_y + sullivan_h - 0.028, 'Sullivan (2013) 核心主干',
              fontsize=15, bold=True, ha='center', va='center', color=COLORS['sullivan_text'])
    draw_text(ax, 0.5, sullivan_y + sullivan_h/2, '自主-依存原则',
              fontsize=14, bold=True, ha='center', va='center', color=COLORS['sullivan_text'])
    draw_text(ax, 0.5, sullivan_y + 0.025, '"概念依存元素编码源域，概念自主元素编码目标域"',
              fontsize=12, ha='center', va='center', color=COLORS['text_gray'],
              style='italic')

    # =========================================================================
    # 从Sullivan到三向整合的连接线
    # =========================================================================
    branch_y = sullivan_y - 0.015
    converge_y = branch_y - 0.035

    # 垂直线
    draw_line(ax, (0.5, sullivan_y), (0.5, converge_y), COLORS['arrow_gray'], 1.5)

    # 三分支
    left_x = 0.22
    mid_x = 0.50
    right_x = 0.78

    draw_line(ax, (left_x, converge_y), (right_x, converge_y), COLORS['arrow_gray'], 1.5)

    # 三个垂直箭头
    arrow_end_y = 0.715
    draw_arrow(ax, (left_x, converge_y), (left_x, arrow_end_y + 0.003), COLORS['arrow_gray'], 1.5, 10)
    draw_arrow(ax, (mid_x, converge_y), (mid_x, arrow_end_y + 0.003), COLORS['arrow_gray'], 1.5, 10)
    draw_arrow(ax, (right_x, converge_y), (right_x, arrow_end_y + 0.003), COLORS['arrow_gray'], 1.5, 10)

    # =========================================================================
    # 三向整合框
    # =========================================================================
    int_box_w = 0.22
    int_box_h = 0.125
    int_box_y = 0.590

    # 借鉴认知语法（Langacker）
    draw_integration_box(ax, left_x - int_box_w/2, int_box_y, int_box_w, int_box_h,
                         '借鉴认知语法', 'Langacker (1987, 2008)',
                         ['认知参照点', '侧显/基底', '认知固化'],
                         COLORS['langacker_fill'], COLORS['langacker_stroke'],
                         COLORS['langacker_text'])

    # 整合构式网络（Goldberg）
    draw_integration_box(ax, mid_x - int_box_w/2, int_box_y, int_box_w, int_box_h,
                         '整合构式网络', 'Goldberg (1995, 2006)',
                         ['四类链接关系', '构式网络', '小世界性质'],
                         COLORS['goldberg_fill'], COLORS['goldberg_stroke'],
                         COLORS['goldberg_text'])

    # 聚焦汉语特征
    draw_integration_box(ax, right_x - int_box_w/2, int_box_y, int_box_w, int_box_h,
                         '聚焦汉语特征', '',
                         ['零系词', '话题突出', '认知风格线索'],
                         COLORS['chinese_fill'], COLORS['chinese_stroke'],
                         COLORS['chinese_text'])

    # =========================================================================
    # 从三向整合到CFMC三层结构的连接线
    # =========================================================================
    int_bottom_y = int_box_y

    # 三条垂直线汇聚
    converge2_y = int_bottom_y - 0.020
    draw_line(ax, (left_x, int_bottom_y), (left_x, converge2_y), COLORS['arrow_gray'], 1.2)
    draw_line(ax, (mid_x, int_bottom_y), (mid_x, converge2_y), COLORS['arrow_gray'], 1.2)
    draw_line(ax, (right_x, int_bottom_y), (right_x, converge2_y), COLORS['arrow_gray'], 1.2)

    # 汇聚横线
    draw_line(ax, (left_x, converge2_y), (right_x, converge2_y), COLORS['arrow_gray'], 1.2)

    # 汇聚到CFMC的箭头 (cfmc_top_y = cfmc_y + cfmc_h = 0.385 + 0.160 = 0.545)
    cfmc_top_y = 0.545
    draw_arrow(ax, (0.5, converge2_y), (0.5, cfmc_top_y + 0.003), COLORS['arrow_gray'], 1.5, 10)

    # =========================================================================
    # CFMC三层次结构框
    # =========================================================================
    cfmc_w = 0.78
    cfmc_h = 0.160
    cfmc_x = 0.5 - cfmc_w / 2
    cfmc_y = 0.385

    draw_rounded_box(ax, cfmc_x, cfmc_y, cfmc_w, cfmc_h,
                     COLORS['cfmc_fill'], COLORS['cfmc_stroke'], 2, 0.010)

    # 标题
    draw_text(ax, 0.5, cfmc_y + cfmc_h - 0.024, 'CFMC三层次结构',
              fontsize=14, bold=True, ha='center', va='center', color=COLORS['cfmc_text'])

    # 分隔线
    sep_y = cfmc_y + cfmc_h - 0.044
    draw_line(ax, (cfmc_x + 0.015, sep_y), (cfmc_x + cfmc_w - 0.015, sep_y),
              COLORS['cfmc_stroke'], 1)

    # 三个层次
    layer_start_y = sep_y - 0.030
    layer_gap = 0.038

    layers = [
        ('层次1：映射准备层次', '域激活 + 参照点锚定', COLORS['langacker_text']),
        ('层次2：构式映射与语码实现层次', 'Sullivan核心 + 汉语边界', COLORS['sullivan_text']),
        ('层次3：网络关联层次', 'Sullivan机制 + Goldberg扩展', COLORS['goldberg_text']),
    ]

    for i, (layer_name, theory, color) in enumerate(layers):
        y_pos = layer_start_y - i * layer_gap
        draw_text(ax, cfmc_x + 0.025, y_pos, layer_name,
                  fontsize=13, bold=True, ha='left', va='center', color=COLORS['cfmc_text'])
        # 使用真正的箭头绘制（从右向左的箭头）
        arrow_start_x = cfmc_x + cfmc_w/2 + 0.05
        arrow_end_x = cfmc_x + cfmc_w/2 - 0.03
        draw_arrow(ax, (arrow_start_x, y_pos), (arrow_end_x, y_pos),
                   COLORS['text_gray'], 1.2, 8, '<-')
        draw_text(ax, cfmc_x + cfmc_w/2 + 0.10, y_pos, theory,
                  fontsize=12, ha='left', va='center', color=color)

    # =========================================================================
    # 从CFMC到研究问题的连接线
    # =========================================================================
    cfmc_bottom_y = cfmc_y
    q_top_y = 0.335

    # 三分支
    q_left_x = 0.25
    q_mid_x = 0.50
    q_right_x = 0.75

    converge3_y = cfmc_bottom_y - 0.025

    # 垂直线
    draw_line(ax, (0.5, cfmc_bottom_y), (0.5, converge3_y), COLORS['arrow_gray'], 1.5)

    # 横线
    draw_line(ax, (q_left_x, converge3_y), (q_right_x, converge3_y), COLORS['arrow_gray'], 1.5)

    # 三个箭头
    draw_arrow(ax, (q_left_x, converge3_y), (q_left_x, q_top_y + 0.003), COLORS['arrow_gray'], 1.5, 10)
    draw_arrow(ax, (q_mid_x, converge3_y), (q_mid_x, q_top_y + 0.003), COLORS['arrow_gray'], 1.5, 10)
    draw_arrow(ax, (q_right_x, converge3_y), (q_right_x, q_top_y + 0.003), COLORS['arrow_gray'], 1.5, 10)

    # =========================================================================
    # 研究问题框
    # =========================================================================
    q_box_w = 0.12
    q_box_h = 0.095
    q_box_y = 0.240

    # Q1
    draw_q_box(ax, q_left_x - q_box_w/2, q_box_y, q_box_w, q_box_h,
               'Q1', '类型特征', '层次1+2',
               COLORS['q1_fill'], COLORS['q1_stroke'], COLORS['q1_text'])

    # Q3
    draw_q_box(ax, q_mid_x - q_box_w/2, q_box_y, q_box_w, q_box_h,
               'Q3', '机制阐释', '层次1+2',
               COLORS['q3_fill'], COLORS['q3_stroke'], COLORS['q3_text'])

    # Q2
    draw_q_box(ax, q_right_x - q_box_w/2, q_box_y, q_box_w, q_box_h,
               'Q2', '网络组织', '层次3',
               COLORS['q2_fill'], COLORS['q2_stroke'], COLORS['q2_text'])

    # =========================================================================
    # 研究问题间的关系箭头
    # =========================================================================
    q_center_y = q_box_y + q_box_h / 2

    # Q1 → Q3：核心递进（双线箭头）
    q1_right = q_left_x + q_box_w/2
    q3_left = q_mid_x - q_box_w/2
    arrow_y = q_center_y + 0.012

    # 双线效果
    draw_arrow(ax, (q1_right + 0.008, arrow_y + 0.003), (q3_left - 0.008, arrow_y + 0.003),
               COLORS['q1_stroke'], 2.0, 12, '->')
    draw_arrow(ax, (q1_right + 0.008, arrow_y - 0.003), (q3_left - 0.008, arrow_y - 0.003),
               COLORS['q1_stroke'], 2.0, 12, '->')
    draw_text(ax, (q1_right + q3_left) / 2, arrow_y + 0.025, '核心递进',
              fontsize=11, bold=True, ha='center', va='center', color=COLORS['q1_text'])

    # Q1 → Q2：节点输入（L形路径：Q1底部向下→水平向右→垂直向上到Q2）
    node_input_y = q_box_y - 0.028  # 节点输入线的y位置
    # 从Q1底部向下的垂直线
    draw_line(ax, (q_left_x, q_box_y), (q_left_x, node_input_y), COLORS['text_gray'], 1.2)
    # 水平线延伸到Q2正下方
    draw_line(ax, (q_left_x, node_input_y), (q_right_x, node_input_y), COLORS['text_gray'], 1.2)
    # 垂直向上的箭头指向Q2底部
    draw_arrow(ax, (q_right_x, node_input_y), (q_right_x, q_box_y - 0.003),
               COLORS['text_gray'], 1.2, 8, '->')
    # 标签
    draw_text(ax, (q_left_x + q_right_x) / 2, node_input_y - 0.018, '节点输入',
              fontsize=11, ha='center', va='center', color=COLORS['text_gray'])

    # Q2 → Q3：结构参照
    q3_right = q_mid_x + q_box_w/2
    q2_left = q_right_x - q_box_w/2

    draw_arrow(ax, (q2_left - 0.008, q_center_y), (q3_right + 0.008, q_center_y),
               COLORS['q2_stroke'], 1.5, 10, '<-')
    draw_text(ax, (q3_right + q2_left) / 2, q_center_y + 0.025, '结构参照',
              fontsize=11, ha='center', va='center', color=COLORS['q2_text'])

    # =========================================================================
    # 横向扩展标注
    # =========================================================================
    draw_text(ax, q_right_x, q_box_y - 0.028, '横向扩展',
              fontsize=12, ha='center', va='center', color=COLORS['text_gray'])

    # =========================================================================
    # 底部说明（上移，减少与图的空白）
    # =========================================================================
    note_y = 0.12
    draw_text(ax, 0.5, note_y,
              '注：Sullivan自主-依存原则贯穿三个层次，为Q1和Q3提供核心分析框架；',
              fontsize=11, ha='center', va='center', color=COLORS['text_gray'])
    draw_text(ax, 0.5, note_y - 0.025,
              'Q1与Q3形成核心递进关系，Q2基于Q1类型划分进行横向扩展',
              fontsize=11, ha='center', va='center', color=COLORS['text_gray'])

    return fig, ax

# =============================================================================
# 主程序
# =============================================================================
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 输出目录（与脚本目录分离）
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    fig, ax = create_cfmc_figure()

    # 保存PNG
    png_path = os.path.join(output_dir, '图5 CFMC三层框架结构图.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f'已保存: {png_path}')

    # 保存PDF
    # pdf_path = os.path.join(script_dir, '图5 CFMC三层框架结构图.pdf')  # 已禁用PDF输出
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
    print('图5 CFMC三层框架结构图 绘制完成！')
