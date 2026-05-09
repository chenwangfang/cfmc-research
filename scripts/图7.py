#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图7 双维度分类空间理论预期示意图（同心圆/靶心图版本）

以同心圆结构展示12类构式的理论原型梯度"中心-边界"分布：
- 第1层（中心）：原型中心T10
- 第2层：次中心T6、T11
- 第3层：边缘T2、T3、T5、T7、T9
- 第4层（外圈）：边界T1、T4、T8、T12

四象限标注映射方向：
- 右上(0°-90°)：具→抽
- 左上(90°-180°)：具→具
- 左下(180°-270°)：抽→具
- 右下(270°-360°)：抽→抽

说明：本图表达第3章理论预期，不等同于第5章P33/P67实测原型梯度分组。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, FancyBboxPatch
import matplotlib.font_manager as fm
import numpy as np
import os

# ============ 字体设置 ============
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

# ============ 颜色配置 ============
COLORS = {
    # 理论原型梯度颜色（蓝色系：从深到浅表示从中心到边界）
    'prototype': '#1a5276',      # 原型中心 - 深蓝色
    'sub_center': '#2980b9',     # 次中心 - 蓝色
    'peripheral': '#85c1e9',     # 边缘 - 浅蓝色
    'rare': '#d4e6f1',           # 边界 - 最浅蓝色

    # 边框颜色
    'prototype_stroke': '#154360',
    'sub_center_stroke': '#1a5276',
    'peripheral_stroke': '#2980b9',
    'rare_stroke': '#5dade2',

    # 文本颜色
    'text_white': '#ffffff',
    'text_dark': '#2c3e50',
    'text_gray': '#7f8c8d',

    # 坐标轴
    'axis_color': '#34495e',
    'grid_color': '#bdc3c7',

    # 背景
    'bg_light': '#fdfefe',
}

# ============ 12类构式数据（极坐标版本）============
# 格式: 类型编号 -> (简称, 原型等级, 映射方向编码)
# 原型等级: 1=原型中心, 2=次中心, 3=边缘, 4=边界
# 映射方向: 1=具→具, 2=具→抽, 3=抽→抽, 4=抽→具
CONSTRUCTIONS = {
    'T1':  ('低_具具', 4, 1),   # 边界，具→具
    'T2':  ('低_具抽', 3, 2),   # 边缘，具→抽
    'T3':  ('低_抽抽', 3, 3),   # 边缘，抽→抽
    'T4':  ('低_抽具', 4, 4),   # 边界，抽→具
    'T5':  ('中_具具', 3, 1),   # 边缘，具→具
    'T6':  ('中_具抽', 2, 2),   # 次中心，具→抽
    'T7':  ('中_抽抽', 3, 3),   # 边缘，抽→抽
    'T8':  ('中_抽具', 4, 4),   # 边界，抽→具
    'T9':  ('高_具具', 3, 1),   # 边缘，具→具
    'T10': ('高_具抽', 1, 2),   # 原型中心，具→抽
    'T11': ('高_抽抽', 2, 3),   # 次中心，抽→抽
    'T12': ('高_抽具', 4, 4),   # 边界，抽→具
}

# 四象限角度范围（以标准数学坐标系，逆时针）
# 右上: 0°-90° (具→抽)
# 左上: 90°-180° (具→具)
# 左下: 180°-270° (抽→具)
# 右下: 270°-360° (抽→抽)
QUADRANT_ANGLES = {
    2: (0, 90),     # 具→抽: 右上象限
    1: (90, 180),   # 具→具: 左上象限
    4: (180, 270),  # 抽→具: 左下象限
    3: (270, 360),  # 抽→抽: 右下象限
}

# 原型等级对应的层级半径
LEVEL_RADIUS = {
    1: 0.08,   # 原型中心
    2: 0.20,   # 次中心
    3: 0.32,   # 边缘
    4: 0.44,   # 边界
}

# 原型等级对应的颜色和样式
LEVEL_STYLES = {
    1: {'fill': COLORS['prototype'], 'stroke': COLORS['prototype_stroke'],
        'text': COLORS['text_white'], 'label': '原型中心', 'linewidth': 3},
    2: {'fill': COLORS['sub_center'], 'stroke': COLORS['sub_center_stroke'],
        'text': COLORS['text_white'], 'label': '次中心', 'linewidth': 2.5},
    3: {'fill': COLORS['peripheral'], 'stroke': COLORS['peripheral_stroke'],
        'text': COLORS['text_dark'], 'label': '边缘', 'linewidth': 2},
    4: {'fill': COLORS['rare'], 'stroke': COLORS['rare_stroke'],
        'text': '#5d6d7e', 'label': '边界', 'linewidth': 1.5},
}

# ============ 绘图辅助函数 ============
def draw_text(ax, x, y, text, fontsize=12, bold=False, ha='center', va='center',
              color='#2c3e50', rotation=0):
    """绘制文本（使用数据坐标）"""
    font = FONT_PROP_BOLD if bold else FONT_PROP
    ax.text(x, y, text, fontsize=fontsize, fontproperties=font,
            ha=ha, va=va, color=color, rotation=rotation, zorder=15)


def polar_to_cartesian(r, theta_deg):
    """极坐标转笛卡尔坐标"""
    theta_rad = np.radians(theta_deg)
    x = r * np.cos(theta_rad)
    y = r * np.sin(theta_rad)
    return x, y


def create_figure():
    """创建图7（同心圆版本）"""
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)

    # 设置坐标轴范围
    ax.set_xlim(-0.65, 0.75)
    ax.set_ylim(-0.65, 0.65)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('white')

    # 圆心位置
    cx, cy = 0, 0

    # ========== 绘制同心圆环（从外到内，先绘制的在下层）==========
    ring_radii = [0.50, 0.38, 0.26, 0.14]  # 外环半径
    ring_inner = [0.38, 0.26, 0.14, 0.0]   # 内环半径
    ring_colors = [COLORS['rare'], COLORS['peripheral'],
                   COLORS['sub_center'], COLORS['prototype']]
    ring_strokes = [COLORS['rare_stroke'], COLORS['peripheral_stroke'],
                    COLORS['sub_center_stroke'], COLORS['prototype_stroke']]
    ring_lw = [1.5, 2, 2.5, 3]

    for i, (r_out, r_in, fill, stroke, lw) in enumerate(
            zip(ring_radii, ring_inner, ring_colors, ring_strokes, ring_lw)):
        if r_in == 0:
            # 最内层是实心圆
            circle = Circle((cx, cy), r_out, facecolor=fill,
                           edgecolor=stroke, linewidth=lw, zorder=2)
        else:
            # 绘制圆环（用两个圆）
            outer = Circle((cx, cy), r_out, facecolor=fill,
                          edgecolor=stroke, linewidth=lw, zorder=2)
            ax.add_patch(outer)
            # 内圆覆盖
            if i < len(ring_radii) - 1:
                inner_fill = ring_colors[i+1]
            else:
                inner_fill = COLORS['prototype']
            inner = Circle((cx, cy), r_in, facecolor=inner_fill,
                          edgecolor='none', linewidth=0, zorder=2+i+1)
            ax.add_patch(inner)
            continue
        ax.add_patch(circle)

    # ========== 绘制十字分隔线（四象限）==========
    line_radius = 0.52
    # 水平线
    ax.plot([-line_radius, line_radius], [0, 0],
            color=COLORS['grid_color'], linewidth=1.5, linestyle='--', zorder=5)
    # 垂直线
    ax.plot([0, 0], [-line_radius, line_radius],
            color=COLORS['grid_color'], linewidth=1.5, linestyle='--', zorder=5)

    # ========== 绘制12类构式标记 ==========
    # 计算每个构式的位置
    # 按象限和层级分组，然后在象限内均匀分布

    quadrant_types = {1: [], 2: [], 3: [], 4: []}
    for type_id, (abbrev, level, md) in CONSTRUCTIONS.items():
        quadrant_types[md].append((type_id, abbrev, level))

    # 每个象限内按层级排序
    for md in quadrant_types:
        quadrant_types[md].sort(key=lambda x: x[2])  # 按level排序

    # 为每个象限分配角度
    for md, types in quadrant_types.items():
        angle_start, angle_end = QUADRANT_ANGLES[md]
        angle_center = (angle_start + angle_end) / 2

        # 对于每个类型，根据其层级确定半径，根据象限确定角度
        for i, (type_id, abbrev, level) in enumerate(types):
            r = LEVEL_RADIUS[level]

            # 同一层级在同一象限内的类型需要分散角度
            same_level_types = [t for t in types if t[2] == level]
            if len(same_level_types) > 1:
                # 在象限内分散
                idx = same_level_types.index((type_id, abbrev, level))
                angle_spread = 30  # 分散角度范围
                angle = angle_center + (idx - (len(same_level_types)-1)/2) * angle_spread
            else:
                angle = angle_center

            # 极坐标转笛卡尔
            x, y = polar_to_cartesian(r, angle)

            # 获取样式
            style = LEVEL_STYLES[level]

            # 绘制类型标记圆点
            marker_size = 0.045 if level == 1 else 0.035
            marker = Circle((x, y), marker_size, facecolor=style['fill'],
                           edgecolor=style['stroke'], linewidth=2, zorder=10)
            ax.add_patch(marker)

            # 绘制类型编号
            draw_text(ax, x, y + 0.002, type_id, fontsize=12, bold=True,
                     color=style['text'])

            # 绘制简称标签（在圆点外侧）
            # 计算标签位置（向外偏移）
            label_r = r + 0.08
            label_x, label_y = polar_to_cartesian(label_r, angle)

            # 调整标签水平对齐方式
            if 45 < angle < 135:
                ha = 'center'
                label_y += 0.02
            elif 225 < angle < 315:
                ha = 'center'
                label_y -= 0.02
            elif angle <= 45 or angle >= 315:
                ha = 'left'
                label_x += 0.02
            else:
                ha = 'right'
                label_x -= 0.02

            draw_text(ax, label_x, label_y, f"({abbrev})", fontsize=11,
                     color=style['text'] if level <= 2 else COLORS['text_dark'])

    # ========== 四象限标签 ==========
    # 将象限标签放在坐标轴外侧，避免与类型标签重叠
    # 上方标签（具→抽）
    draw_text(ax, 0, 0.58, '具→抽 (MD=2)', fontsize=13, bold=True, color=COLORS['axis_color'])
    # 下方标签（抽→具）
    draw_text(ax, 0, -0.58, '抽→具 (MD=4)', fontsize=13, bold=True, color=COLORS['axis_color'])
    # 左侧标签（具→具）
    draw_text(ax, -0.58, 0, '具→具 (MD=1)', fontsize=13, bold=True, color=COLORS['axis_color'], rotation=90)
    # 右侧标签（抽→抽）
    draw_text(ax, 0.58, 0, '抽→抽 (MD=3)', fontsize=13, bold=True, color=COLORS['axis_color'], rotation=270)

    # ========== 主标题（已删除，论文中图表标题应在图表下方以可编辑文字形式呈现）==========

    # ========== 图例 ==========
    legend_x = 0.56
    legend_y = 0.35
    legend_item_h = 0.08

    ax.text(legend_x + 0.04, legend_y + 0.05, '理论梯度',
            fontsize=13, fontproperties=FONT_PROP_BOLD,
            ha='left', color=COLORS['text_dark'])

    for i, (level, style) in enumerate(LEVEL_STYLES.items()):
        y_pos = legend_y - i * legend_item_h

        # 图例色块
        legend_marker = Circle((legend_x, y_pos), 0.025, facecolor=style['fill'],
                               edgecolor=style['stroke'], linewidth=1.5, zorder=5)
        ax.add_patch(legend_marker)

        # 图例文字
        ax.text(legend_x + 0.045, y_pos, style['label'],
                fontsize=12, fontproperties=FONT_PROP,
                ha='left', va='center', color=COLORS['text_dark'])

    # ========== 底部注释 ==========
    note_text = '注：本图表示第3章理论预期，实测梯度见第5章'
    ax.text(0.5, -0.02, note_text,
            fontsize=12, fontproperties=FONT_PROP,
            ha='center', va='top', color=COLORS['text_gray'],
            transform=ax.transAxes)

    plt.tight_layout()
    return fig, ax


# ============ 主程序 ============
if __name__ == '__main__':
    fig, ax = create_figure()

    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 输出目录（与脚本目录分离）
    output_dir = os.path.join(os.path.dirname(script_dir), '第1-4章脚本输出的图')

    # 保存PNG
    png_path = os.path.join(output_dir, '图7 双维度分类空间示意图.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"已保存: {png_path}")

    # 保存PDF
    # pdf_path = os.path.join(script_dir, '图7 双维度分类空间示意图.pdf')  # 已禁用PDF输出
    # fig.savefig(pdf_path, format='pdf', bbox_inches='tight',  # 已禁用PDF输出
                # facecolor='white', edgecolor='none')  # 已禁用PDF输出
    # print(f"已保存: {pdf_path}")  # 已禁用PDF输出

    print("图7 双维度分类空间理论预期示意图（同心圆版本）绘制完成！")

    # 高清输出（1200 DPI）
    hd_dir = '/home/tomja/projects/博士毕业论文/大论文/论文撰写/正文/毕业论文高清图'
    os.makedirs(hd_dir, exist_ok=True)
    hd_path = os.path.join(hd_dir, os.path.basename(png_path))
    fig.savefig(hd_path, dpi=1200, bbox_inches='tight', facecolor='white', edgecolor='none')
    svg_path = hd_path.replace('.png', '.svg')
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f'已保存高清: {hd_path}')
    print(f'已保存矢量: {svg_path}')

    plt.close()
