#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图6 四阶段认知编码机制流程图

来源：论文正文第1365-1385行ASCII图表
结构：
- 层次1：映射准备层次，即映射发生前的认知准备（阶段1认知域激活 → 阶段2参照点锚定）
- 层次2：构式映射与语码实现层次（阶段3跨域映射 → 阶段4语言编码 → 系表隐喻构式）
- 主路径：η1─β1→η2─β2→η3─γ→Y
- 直接路径：η1─β3→η3
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os
import platform

# ============ 字体设置 ============
def setup_fonts():
    """配置中文字体"""
    if platform.system() == 'Linux':
        font_path = '/mnt/c/Windows/Fonts/msyh.ttc'
    else:
        font_path = 'C:/Windows/Fonts/msyh.ttc'

    if os.path.exists(font_path):
        from matplotlib import font_manager
        font_manager.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = ['Microsoft YaHei']
        print(f"使用字体: {font_path}")
    else:
        plt.rcParams['font.family'] = ['SimHei', 'DejaVu Sans']
        print("使用备用字体")

    plt.rcParams['axes.unicode_minus'] = False

setup_fonts()

# ============ 配色方案 ============
COLORS = {
    # Langacker蓝色系（阶段1、阶段2）
    'langacker_fill': '#e8f4fd',
    'langacker_stroke': '#2980b9',
    'langacker_text': '#1a5276',

    # Sullivan红色系（阶段3、阶段4）
    'sullivan_fill': '#fdedec',
    'sullivan_stroke': '#c0392b',
    'sullivan_text': '#922b21',

    # 层次框
    'level1_fill': '#f8f9fa',
    'level1_stroke': '#3498db',
    'level2_fill': '#fef9f8',
    'level2_stroke': '#e74c3c',

    # 路径颜色
    'path_beta1': '#5d6d7e',       # β1普通路径（灰色）
    'path_beta2': '#8e44ad',       # β2核心路径（深紫色，区分Sullivan红）
    'path_beta3': '#7f8c8d',       # β3直接路径（灰色虚线）
    'path_gamma': '#d35400',       # γ路径（深橙色）
    'path_output': '#27ae60',      # 输出箭头（绿色）

    # 结果框
    'result_fill': '#e8f8f5',
    'result_stroke': '#1abc9c',
    'result_text': '#117864',

    # 文本
    'text_dark': '#2c3e50',
    'text_gray': '#7f8c8d',
    'text_light': '#95a5a6',
}

# ============ 绘图辅助函数 ============
def draw_text(ax, x, y, text, fontsize=10, bold=False, ha='center', va='center',
              color='#2c3e50', rotation=0):
    """绘制文本"""
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, text, fontsize=fontsize, fontweight=weight,
            ha=ha, va=va, color=color, rotation=rotation,
            transform=ax.transAxes)

def draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color,
                     linewidth=1.5, radius=0.02):
    """绘制圆角矩形框"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill_color,
        edgecolor=stroke_color,
        linewidth=linewidth,
        transform=ax.transAxes,
        zorder=2
    )
    ax.add_patch(box)

def draw_arrow(ax, start, end, color, linewidth=1.5, head_width=10, style='->',
               linestyle='-', zorder=3):
    """绘制箭头"""
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle=f'{style},head_width=0.4,head_length=0.3',
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        mutation_scale=15,
        transform=ax.transAxes,
        zorder=zorder
    )
    ax.add_patch(arrow)

def draw_line(ax, start, end, color, linewidth=1.5, linestyle='-', zorder=3):
    """绘制直线"""
    ax.plot([start[0], end[0]], [start[1], end[1]],
            color=color, linewidth=linewidth, linestyle=linestyle,
            transform=ax.transAxes, zorder=zorder)

def draw_stage_box(ax, x, y, width, height, stage_num, stage_name, theory,
                   var_name, indicator_count, fill_color, stroke_color, text_color):
    """绘制阶段框"""
    # 绘制框
    draw_rounded_box(ax, x, y, width, height, fill_color, stroke_color, 2.0, 0.015)

    # 阶段标题
    draw_text(ax, x + width/2, y + height - 0.025, f'阶段{stage_num}：{stage_name}',
              fontsize=13, bold=True, color=text_color)

    # 理论来源
    draw_text(ax, x + width/2, y + height - 0.055, f'({theory})',
              fontsize=11, color=COLORS['text_gray'])

    # 变量信息
    draw_text(ax, x + width/2, y + height - 0.085, f'{var_name}: {indicator_count}',
              fontsize=11, color=text_color)

def draw_level_box(ax, x, y, width, height, level_name, fill_color, stroke_color):
    """绘制层次背景框"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0,rounding_size=0.01",
        facecolor=fill_color,
        edgecolor=stroke_color,
        linewidth=1.0,
        linestyle='--',
        alpha=0.5,
        transform=ax.transAxes,
        zorder=1
    )
    ax.add_patch(box)

    # 层次标签
    draw_text(ax, x + 0.015, y + height - 0.025, level_name,
              fontsize=12, bold=True, ha='left', color=stroke_color)

# ============ 主绘图函数 ============
def create_figure():
    """创建图6"""
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # ========== 主标题（已删除，论文中图表标题应在图表下方以可编辑文字形式呈现）==========

    # ========== 层次背景框 ==========
    # 层次1：映射机制层次（删除标签）
    level1_x, level1_y = 0.08, 0.60
    level1_w, level1_h = 0.84, 0.36
    draw_level_box(ax, level1_x, level1_y, level1_w, level1_h,
                   '', COLORS['level1_fill'], COLORS['level1_stroke'])

    # 层次2：语码实现层次（删除标签）
    level2_x, level2_y = 0.08, 0.22
    level2_w, level2_h = 0.84, 0.36
    draw_level_box(ax, level2_x, level2_y, level2_w, level2_h,
                   '', COLORS['level2_fill'], COLORS['level2_stroke'])

    # ========== 阶段框尺寸 ==========
    box_w = 0.18
    box_w3 = 0.24  # 阶段3单独加宽
    box_w4 = 0.21  # 阶段4容纳 Y: copula_function
    box_h = 0.12

    # 层次1的阶段框位置（阶段1左侧，阶段2右侧）
    stage1_x = 0.12
    stage2_x = 0.65  # 右移以延长β2，同时为输出箭头留空间
    stage_y_top = 0.74

    # 层次2的阶段框位置（阶段3在阶段1正下方，阶段4居中）
    stage3_x = 0.12   # 与阶段1对齐（保持原位）
    stage4_x = 0.43   # 位于阶段3和结果框中间
    stage_y_bottom = 0.34

    # 结果框位置（右边线与阶段2右边线对齐）
    result_x = 0.72
    result_y = 0.36
    result_w = 0.11  # 右边线 = 0.72 + 0.11 = 0.83 = 阶段2右边线
    result_h = 0.08

    # ========== 绘制阶段框 ==========
    # 阶段1：认知域激活
    draw_stage_box(ax, stage1_x, stage_y_top, box_w, box_h,
                   '1', '认知域激活', 'Langacker', 'η1', '3指标',
                   COLORS['langacker_fill'], COLORS['langacker_stroke'],
                   COLORS['langacker_text'])

    # 阶段2：参照点锚定
    draw_stage_box(ax, stage2_x, stage_y_top, box_w, box_h,
                   '2', '参照点锚定', 'Langacker', 'η2', '3指标',
                   COLORS['langacker_fill'], COLORS['langacker_stroke'],
                   COLORS['langacker_text'])

    # 阶段3：跨域映射（使用加宽的box_w3）
    draw_stage_box(ax, stage3_x, stage_y_bottom, box_w3, box_h,
                   '3', '跨域映射', 'CFMC核心', 'η3', '3指标',
                   COLORS['sullivan_fill'], COLORS['sullivan_stroke'],
                   COLORS['sullivan_text'])

    # 阶段4：语言编码
    draw_stage_box(ax, stage4_x, stage_y_bottom, box_w4, box_h,
                   '4', '语言编码', 'Sullivan+功能分类', 'Y', 'copula_function',
                   COLORS['sullivan_fill'], COLORS['sullivan_stroke'],
                   COLORS['sullivan_text'])

    # ========== 结果框：系表隐喻构式 ==========
    draw_rounded_box(ax, result_x, result_y, result_w, result_h,
                     COLORS['result_fill'], COLORS['result_stroke'], 2.0, 0.01)
    draw_text(ax, result_x + result_w/2, result_y + result_h/2, '系表隐喻构式',
              fontsize=12, bold=True, color=COLORS['result_text'])

    # ========== 绘制路径箭头 ==========

    # β1：阶段1 → 阶段2（水平箭头）
    beta1_start = (stage1_x + box_w, stage_y_top + box_h/2)
    beta1_end = (stage2_x - 0.01, stage_y_top + box_h/2)
    draw_arrow(ax, beta1_start, beta1_end, COLORS['path_beta1'], 2.0, 12, '->')
    # β1标签
    draw_text(ax, (beta1_start[0] + beta1_end[0])/2, beta1_start[1] + 0.03, 'β1',
              fontsize=13, bold=True, color=COLORS['path_beta1'])

    # 层次分隔线y坐标
    mid_y = (stage_y_top + stage_y_bottom + box_h) / 2

    # β3：阶段1 → 阶段3（直接路径，虚线，垂直向下）
    # 阶段1和阶段3上下对齐，直接垂直向下
    beta3_x = stage1_x + box_w/2
    beta3_arrow_start = stage_y_bottom + box_h + 0.06  # 箭头起点
    # 虚线部分（不含箭头段）
    draw_line(ax, (beta3_x, stage_y_top - 0.01),
              (beta3_x, beta3_arrow_start), COLORS['path_beta3'], 1.5, '--')
    # 箭头段（实线带箭头）
    draw_arrow(ax, (beta3_x, beta3_arrow_start),
               (beta3_x, stage_y_bottom + box_h + 0.008),
               COLORS['path_beta3'], 1.8, 12, '->')
    # β3标签（右移靠近虚线，上移）
    draw_text(ax, beta3_x - 0.02, mid_y + 0.05, 'β3',
              fontsize=12, color=COLORS['path_beta3'])
    draw_text(ax, beta3_x - 0.035, mid_y + 0.02, '(直接路径)',
              fontsize=10, color=COLORS['path_beta3'])

    # β2：阶段2 → 阶段3（核心路径，L形：垂直向下+水平向左+垂直向下）
    beta2_x = stage2_x + box_w/2  # 从阶段2下中心开始
    stage3_target = stage3_x + box_w3/2  # 指向阶段3中心，延长水平线
    beta2_arrow_start = stage_y_bottom + box_h + 0.06  # 箭头起点
    # 从阶段2底部垂直向下到中间线
    draw_line(ax, (beta2_x, stage_y_top - 0.01),
              (beta2_x, mid_y), COLORS['path_beta2'], 2.5)
    # 水平向左到阶段3中心上方
    draw_line(ax, (beta2_x, mid_y),
              (stage3_target, mid_y), COLORS['path_beta2'], 2.5)
    # 垂直向下（不含箭头段）
    draw_line(ax, (stage3_target, mid_y),
              (stage3_target, beta2_arrow_start), COLORS['path_beta2'], 2.5)
    # 箭头段
    draw_arrow(ax, (stage3_target, beta2_arrow_start),
               (stage3_target, stage_y_bottom + box_h + 0.008),
               COLORS['path_beta2'], 2.5, 14, '->')
    # β2标签（核心路径）
    draw_text(ax, (beta2_x + stage3_target)/2, mid_y + 0.025, 'β2',
              fontsize=14, bold=True, color=COLORS['path_beta2'])
    draw_text(ax, (beta2_x + stage3_target)/2, mid_y - 0.02, '(核心路径)',
              fontsize=11, color=COLORS['path_beta2'])

    # γ：阶段3 → 阶段4（水平箭头，使用box_w3）
    gamma_start = (stage3_x + box_w3, stage_y_bottom + box_h/2)
    gamma_end = (stage4_x - 0.01, stage_y_bottom + box_h/2)
    draw_arrow(ax, gamma_start, gamma_end, COLORS['path_gamma'], 2.0, 12, '->')
    # γ标签
    draw_text(ax, (gamma_start[0] + gamma_end[0])/2, gamma_start[1] + 0.03, 'γ',
              fontsize=13, bold=True, color=COLORS['path_gamma'])

    # 输出箭头：阶段4 → 系表隐喻构式
    output_start = (stage4_x + box_w4, stage_y_bottom + box_h/2)
    output_end = (result_x - 0.01, result_y + result_h/2)
    draw_arrow(ax, output_start, output_end, COLORS['path_output'], 2.0, 12, '->')

    # ========== 底部注释（分两行）==========
    note_y1 = 0.075
    note_y2 = 0.045
    note_text1 = '注：主路径为η1─β1→η2─β2→η3─γ→Y（实线），直接路径为η1─β3→η3（虚线）'
    note_text2 = 'β2为CFMC核心接口路径；Y为语言编码边界端点；箭头表示逻辑依赖，非严格时序'
    draw_text(ax, 0.5, note_y1, note_text1, fontsize=12, ha='center', color=COLORS['text_gray'])
    draw_text(ax, 0.5, note_y2, note_text2, fontsize=12, ha='center', color=COLORS['text_gray'])

    # ========== 图例 ==========
    legend_y = 0.012
    legend_items = [
        ('Langacker认知语法', COLORS['langacker_stroke'], '-'),
        ('Sullivan/系词功能理论', COLORS['sullivan_stroke'], '-'),
        ('构式输出', COLORS['result_stroke'], '-'),
        ('主路径（实线）', COLORS['path_beta2'], '-'),
        ('直接路径（虚线）', COLORS['path_beta3'], '--'),
    ]

    legend_x_start = 0.08
    legend_spacing = 0.18

    for i, (label, color, linestyle) in enumerate(legend_items):
        x = legend_x_start + i * legend_spacing
        if linestyle == '--':
            # 虚线图例（用线条表示）
            ax.plot([x, x + 0.025], [legend_y + 0.009, legend_y + 0.009],
                    color=color, linewidth=2, linestyle='--',
                    transform=ax.transAxes, zorder=2)
        else:
            # 实线/色块图例
            box = FancyBboxPatch(
                (x, legend_y), 0.025, 0.018,
                boxstyle="round,pad=0,rounding_size=0.003",
                facecolor=color,
                edgecolor=color,
                linewidth=1,
                transform=ax.transAxes,
                zorder=2
            )
            ax.add_patch(box)
        # 标签
        draw_text(ax, x + 0.032, legend_y + 0.009, label,
                  fontsize=10, ha='left', color=COLORS['text_dark'])

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
    png_path = os.path.join(output_dir, '图6 四阶段认知编码机制流程图.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"已保存: {png_path}")

    # 保存PDF
    # pdf_path = os.path.join(script_dir, '图6 四阶段认知编码机制流程图.pdf')  # 已禁用PDF输出
    # fig.savefig(pdf_path, format='pdf', bbox_inches='tight',  # 已禁用PDF输出
                # facecolor='white', edgecolor='none')  # 已禁用PDF输出
    # print(f"已保存: {pdf_path}")  # 已禁用PDF输出

    print("图6 四阶段认知编码机制流程图 绘制完成！")


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
