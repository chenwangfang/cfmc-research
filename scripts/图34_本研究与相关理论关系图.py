# -*- coding: utf-8 -*-
"""
图34 本研究与相关理论关系图
展示本研究在隐喻研究谱系中的定位
兼容WSL和Windows系统
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.patheffects as path_effects
import os
import platform

# ========== 字体配置（WSL/Windows兼容）==========
import matplotlib.font_manager as fm

def setup_chinese_font():
    """配置中文字体，兼容WSL和Windows"""
    system = platform.system()

    if system == 'Windows':
        # Windows原生环境
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf',
        ]
    else:
        # WSL或Linux环境
        font_paths = [
            '/mnt/c/Windows/Fonts/msyh.ttc',
            '/mnt/c/Windows/Fonts/simhei.ttf',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rcParams['font.sans-serif'] = [font_name]
            plt.rcParams['axes.unicode_minus'] = False
            return True

    # 回退方案
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    return False

setup_chinese_font()

# ========== 字号配置 ==========
FONTS = {
    'main_title': 18,
    'theory_name': 14,
    'theory_author': 11,
    'box_title': 15,
    'box_subtitle': 13,
    'content': 12,
    'arrow_label': 11
}

# ========== 颜色配置 ==========
COLORS = {
    'cmt': '#E3F2FD',           # 浅蓝 - CMT
    'cit': '#FCE4EC',           # 浅粉 - CIT
    'sullivan': '#FFF8E1',      # 浅黄 - Sullivan
    'cfmc': '#E8F5E9',          # 浅绿 - CFMC
    'cfmc_inner': '#C8E6C9',    # 稍深绿 - CFMC内框
    'cg': '#F3E5F5',            # 浅紫 - 认知语法
    'cxg': '#FBE9E7',           # 浅橙 - 构式语法
    'border_cmt': '#1565C0',
    'border_cit': '#C2185B',
    'border_sullivan': '#F9A825',
    'border_cfmc': '#2E7D32',
    'border_cg': '#7B1FA2',
    'border_cxg': '#E64A19',
    'arrow': '#546E7A',
    'main_arrow': '#2E7D32'
}

def create_figure_8_2():
    """创建图34：本研究与相关理论关系图"""

    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # ========== 布局参数（等间距设计）==========
    # 四排高度：顶层1.3, 中层1.1, 核心2.4, 底层1.0
    # 间距：0.55
    ROW_GAP = 0.55

    # 从上到下计算y坐标
    row1_h, row2_h, row3_h, row4_h = 1.3, 1.1, 2.4, 1.0

    row1_top = 8.3
    row1_y = row1_top - row1_h  # 7.0

    row2_top = row1_y - ROW_GAP  # 6.45
    row2_y = row2_top - row2_h  # 5.35

    row3_top = row2_y - ROW_GAP  # 4.8
    row3_y = row3_top - row3_h  # 2.4

    row4_top = row3_y - ROW_GAP  # 1.85
    row4_y = row4_top - row4_h  # 0.85

    # ========== 主标题 ==========
    # ax.text(6, 8.65, '图34 本研究与相关理论关系图',
            # fontsize=FONTS['main_title'], ha='center', va='center', fontweight='bold')

    # ========== 顶层：CMT 与 CIT ==========
    # CMT框
    cmt_width = 4.7
    cmt_x = 0.9
    cmt_box = FancyBboxPatch((cmt_x, row1_y), cmt_width, row1_h,
                              boxstyle="round,pad=0.02,rounding_size=0.1",
                              facecolor=COLORS['cmt'],
                              edgecolor=COLORS['border_cmt'],
                              linewidth=2)
    ax.add_patch(cmt_box)
    ax.text(cmt_x + cmt_width / 2, row1_y + row1_h - 0.45, '概念隐喻理论（CMT）',
            fontsize=FONTS['theory_name'], ha='center', fontweight='bold',
            color=COLORS['border_cmt'])
    ax.text(cmt_x + cmt_width / 2, row1_y + 0.35, 'Lakoff & Johnson (1980)',
            fontsize=FONTS['theory_author'], ha='center', color='#424242', style='italic')

    # CIT框
    cit_width = 4.7
    cit_x = 6.4
    cit_box = FancyBboxPatch((cit_x, row1_y), cit_width, row1_h,
                              boxstyle="round,pad=0.02,rounding_size=0.1",
                              facecolor=COLORS['cit'],
                              edgecolor=COLORS['border_cit'],
                              linewidth=2)
    ax.add_patch(cit_box)
    ax.text(cit_x + cit_width / 2, row1_y + row1_h - 0.45, '概念整合理论（CIT）',
            fontsize=FONTS['theory_name'], ha='center', fontweight='bold',
            color=COLORS['border_cit'])
    ax.text(cit_x + cit_width / 2, row1_y + 0.35, 'Fauconnier & Turner (2002)',
            fontsize=FONTS['theory_author'], ha='center', color='#424242', style='italic')

    # CMT → Sullivan 箭头
    ax.annotate('', xy=(4.2, row2_top + 0.05), xytext=(cmt_x + cmt_width / 2, row1_y - 0.05),
                arrowprops=dict(arrowstyle='->,head_length=0.25,head_width=0.18',
                               color=COLORS['arrow'], lw=1.5))
    ax.text(4.35, (row1_y + row2_top) / 2, '概念基础',
            fontsize=FONTS['arrow_label'], ha='left', color=COLORS['arrow'])

    # CIT → CFMC 虚线箭头
    ax.annotate('', xy=(9.4, row3_top + 0.05), xytext=(cit_x + cit_width / 2, row1_y - 0.05),
                arrowprops=dict(arrowstyle='->,head_length=0.22,head_width=0.16',
                               color=COLORS['border_cit'], lw=1.5,
                               linestyle='--'))
    ax.text(9.55, 5.65, '意义建构参照',
            fontsize=FONTS['arrow_label'], ha='left', color=COLORS['border_cit'])

    # ========== 中层：Sullivan理论 ==========
    sullivan_box = FancyBboxPatch((2.5, row2_y), 7, row2_h,
                                   boxstyle="round,pad=0.02,rounding_size=0.1",
                                   facecolor=COLORS['sullivan'],
                                   edgecolor=COLORS['border_sullivan'],
                                   linewidth=2.5)
    ax.add_patch(sullivan_box)
    ax.text(6, row2_y + row2_h - 0.35, 'Sullivan (2013) 隐喻构式理论',
            fontsize=FONTS['box_title'], ha='center', fontweight='bold',
            color=COLORS['border_sullivan'])
    ax.text(6, row2_y + 0.3, '整合CMT与构式语法',
            fontsize=FONTS['box_subtitle'], ha='center', color='#5D4037')

    # Sullivan → CFMC 箭头（主要箭头，加粗）
    ax.annotate('', xy=(6, row3_top + 0.05), xytext=(6, row2_y - 0.05),
                arrowprops=dict(arrowstyle='->,head_length=0.3,head_width=0.22',
                               color=COLORS['main_arrow'], lw=2.5))
    ax.text(6.15, (row2_y + row3_top) / 2, '本研究：汉语验证与类型学补充',
            fontsize=FONTS['arrow_label'], ha='left', fontweight='bold',
            color=COLORS['main_arrow'])

    # ========== 核心：CFMC理论框架 ==========
    # 外框
    cfmc_box = FancyBboxPatch((1.5, row3_y), 9, row3_h,
                               boxstyle="round,pad=0.02,rounding_size=0.1",
                               facecolor=COLORS['cfmc'],
                               edgecolor=COLORS['border_cfmc'],
                               linewidth=3)
    ax.add_patch(cfmc_box)
    ax.text(6, row3_y + row3_h - 0.35, 'CFMC理论框架',
            fontsize=FONTS['box_title'], ha='center', fontweight='bold',
            color=COLORS['border_cfmc'])

    # 内框：三个要点
    inner_box = FancyBboxPatch((2.0, row3_y + 0.2), 8, 1.6,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=COLORS['cfmc_inner'],
                                edgecolor=COLORS['border_cfmc'],
                                linewidth=1.5,
                                linestyle='--')
    ax.add_patch(inner_box)

    # 三个要点
    content_base = row3_y + 0.45
    ax.text(2.3, content_base + 1.0, '• 借鉴Langacker认知语法：操作化参照点锚定',
            fontsize=FONTS['content'], ha='left', color='#1B5E20')
    ax.text(2.3, content_base + 0.5, '• 整合Goldberg构式网络理论：补充网络组织（Q2）',
            fontsize=FONTS['content'], ha='left', color='#1B5E20')
    ax.text(2.3, content_base, '• 纳入汉语类型学与文化认知线索：零系词、话题突出、整体性/关系性',
            fontsize=FONTS['content'], ha='left', color='#1B5E20')

    # ========== 底层：认知语法 和 构式语法 ==========
    # 认知语法框
    cg_box = FancyBboxPatch((1.2, row4_y), 3.8, row4_h,
                             boxstyle="round,pad=0.02,rounding_size=0.1",
                             facecolor=COLORS['cg'],
                             edgecolor=COLORS['border_cg'],
                             linewidth=2)
    ax.add_patch(cg_box)
    ax.text(3.1, row4_y + row4_h - 0.35, '认知语法（CG）',
            fontsize=FONTS['theory_name'], ha='center', fontweight='bold',
            color=COLORS['border_cg'])
    ax.text(3.1, row4_y + 0.25, 'Langacker (1987, 2008)',
            fontsize=FONTS['theory_author'], ha='center', color='#424242', style='italic')

    # 构式语法框
    cxg_box = FancyBboxPatch((7, row4_y), 3.8, row4_h,
                              boxstyle="round,pad=0.02,rounding_size=0.1",
                              facecolor=COLORS['cxg'],
                              edgecolor=COLORS['border_cxg'],
                              linewidth=2)
    ax.add_patch(cxg_box)
    ax.text(8.9, row4_y + row4_h - 0.35, '构式语法（CxG）',
            fontsize=FONTS['theory_name'], ha='center', fontweight='bold',
            color=COLORS['border_cxg'])
    ax.text(8.9, row4_y + 0.25, 'Goldberg (1995, 2006)',
            fontsize=FONTS['theory_author'], ha='center', color='#424242', style='italic')

    # 底层 → CFMC 虚线连接
    # CG → CFMC
    ax.annotate('', xy=(3.5, row3_y), xytext=(3.1, row4_top + 0.05),
                arrowprops=dict(arrowstyle='->,head_length=0.2,head_width=0.15',
                               color=COLORS['border_cg'], lw=1.5,
                               linestyle='--'))

    # CxG → CFMC
    ax.annotate('', xy=(8.5, row3_y), xytext=(8.9, row4_top + 0.05),
                arrowprops=dict(arrowstyle='->,head_length=0.2,head_width=0.15',
                               color=COLORS['border_cxg'], lw=1.5,
                               linestyle='--'))

    plt.tight_layout()
    return fig


def get_output_dir():
    """获取输出目录，兼容WSL和Windows"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.normpath(os.path.join(script_dir, '..', '结果_输出', 'Figures'))

    os.makedirs(base_path, exist_ok=True)
    return base_path


def get_hd_dir():
    """获取高清图目录，自动适配 WSL 与 Windows UNC。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, '..', '..', '正文', '毕业论文高清图'))


def main():
    """主函数"""
    output_dir = get_output_dir()

    fig = create_figure_8_2()

    png_path = os.path.join(output_dir, "图34_本研究与相关理论关系图.png")

    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')

    # 高清输出（1200 DPI）
    hd_dir = get_hd_dir()
    os.makedirs(hd_dir, exist_ok=True)
    hd_path = os.path.join(hd_dir, os.path.basename(png_path))
    fig.savefig(hd_path, dpi=1200, bbox_inches='tight', facecolor='white')
    svg_path = hd_path.replace('.png', '.svg')
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')

    plt.close(fig)

    print(f"图34已保存:\n  PNG: {png_path}")
    print(f"  高清: {hd_path}")
    print(f"  矢量: {svg_path}")


if __name__ == "__main__":
    main()
