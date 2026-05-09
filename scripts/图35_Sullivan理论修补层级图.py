# -*- coding: utf-8 -*-
"""
图35 Sullivan理论修补层级图
展示本研究对Sullivan (2013)理论的双重修补：C1跨语言适用性检验 + C2机制形式化
数据：动态读取自 结果_输出/Data/ 目录
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np
import json
import pandas as pd

# ============ 字体配置（适配Linux/Windows/WSL）============
import platform
import os

def get_chinese_font():
    """获取中文字体路径，适配不同操作系统"""
    font_paths = [
        # WSL环境
        '/mnt/c/Windows/Fonts/msyh.ttc',
        '/mnt/c/Windows/Fonts/msyh.ttf',
        # Linux环境
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
        # Windows环境
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/msyh.ttf',
        # macOS环境
        '/System/Library/Fonts/PingFang.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
    ]

    for path in font_paths:
        if os.path.exists(path):
            return path

    print("警告：未找到中文字体，尝试使用系统默认字体")
    return None

def get_output_dir():
    """获取输出目录路径，适配不同操作系统"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, '..', '结果_输出', 'Figures'))

def get_hd_dir():
    """获取高清图目录，自动适配 WSL 与 Windows UNC。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, '..', '..', '正文', '毕业论文高清图'))

def get_data_dir():
    """获取Data目录路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', '结果_输出', 'Data')
    return os.path.normpath(data_dir)

def load_data():
    """从Data目录动态加载统计数据"""
    data_dir = get_data_dir()

    # 读取表59_双维度相关分析（C1证据：r值）
    with open(os.path.join(data_dir, '表59_双维度相关分析.json'), 'r', encoding='utf-8') as f:
        table60 = json.load(f)

    # 读取PLS_模型拟合比较.csv（C2证据：GoF）
    pls_fit = pd.read_csv(os.path.join(data_dir, 'PLS_模型拟合比较.csv'), index_col=0)

    # 读取PLS_路径系数表.csv（C2证据：beta）
    pls_paths = pd.read_csv(os.path.join(data_dir, 'PLS_路径系数表.csv'), index_col=0)

    data = {}

    # C1证据：从表60提取Pearson r
    for item in table60:
        if item.get('分析项目') == 'Pearson r':
            data['c1_r'] = float(item['值'])
            break

    # C2证据：从PLS_模型拟合比较.csv提取模型A的GoF
    model_a_row = pls_fit[pls_fit['模型'].str.contains('模型A', na=False)]
    if not model_a_row.empty:
        data['gof'] = float(model_a_row.iloc[0]['GoF'])

    # C2证据：从PLS_路径系数表.csv提取模型A的eta2->eta3路径系数
    model_a_paths = pls_paths[pls_paths['模型'].str.contains('模型A', na=False)]
    eta2_eta3 = model_a_paths[model_a_paths['路径'].str.contains('eta2', na=False) &
                               model_a_paths['路径'].str.contains('eta3', na=False)]
    if not eta2_eta3.empty:
        data['beta2'] = float(eta2_eta3.iloc[0]['系数β'])

    return data

# ============ 主程序 ============
def main():
    # 加载数据
    data = load_data()
    print(f"  加载数据：")
    print(f"   C1证据: r={data['c1_r']:.3f}")
    print(f"   C2证据: GoF={data['gof']:.3f}, beta(eta2->eta3)={data['beta2']:.3f}")
    
    font_path = get_chinese_font()
    if font_path:
        font_prop = fm.FontProperties(fname=font_path)
        font_prop_bold = fm.FontProperties(fname=font_path, weight='bold')
        font_prop_italic = fm.FontProperties(fname=font_path, style='italic')
    else:
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        font_prop = None
        font_prop_bold = None
        font_prop_italic = None

    plt.close('all')

    # ============ 创建图形 ============
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # ============ 颜色定义 ============
    color_top = '#E8F4E8'
    color_mid = '#FFF8E1'
    color_base = '#E3F2FD'
    border_top = '#4CAF50'
    border_mid = '#FF9800'
    border_base = '#1976D2'

    # ============ 绘制三层结构 ============

    # --- 底层：Sullivan原理论 ---
    base_box = FancyBboxPatch((1, 0.8), 10, 2.2,
                              boxstyle="round,pad=0.05,rounding_size=0.3",
                              facecolor=color_base, edgecolor=border_base, linewidth=2.5)
    ax.add_patch(base_box)

    ax.text(6, 2.3, 'Sullivan (2013) 隐喻构式理论', fontsize=16,
            ha='center', va='center', color=border_base, fontproperties=font_prop_bold)
    ax.text(6, 1.65, '自主-依存原则：隐喻映射的认知分工', fontsize=12,
            ha='center', va='center', color='#333', fontproperties=font_prop)
    ax.text(6, 1.15, '两步程序：概念隐喻激活 → 构式选择', fontsize=12,
            ha='center', va='center', color='#333', fontproperties=font_prop)

    ax.text(0.3, 1.9, '基\n础\n层', fontsize=12, ha='center', va='center',
            color=border_base, fontproperties=font_prop_bold)

    # --- 中层：C1跨语言适用性检验 ---
    mid_box = FancyBboxPatch((1, 3.6), 10, 2.2,
                             boxstyle="round,pad=0.05,rounding_size=0.3",
                             facecolor=color_mid, edgecolor=border_mid, linewidth=2.5)
    ax.add_patch(mid_box)

    ax.text(6, 5.1, 'C1：跨语言适用性检验', fontsize=16,
            ha='center', va='center', color=border_mid, fontproperties=font_prop_bold)
    ax.text(6, 4.45, '检验范围：英语 → 汉语（印欧语系 → 汉藏语系）', fontsize=12,
            ha='center', va='center', color='#333', fontproperties=font_prop)
    # 动态数据：C1相关系数
    ax.text(6, 3.95, f'核心证据：认知通达度×概念复杂度负相关（r = {data["c1_r"]:.3f}）', fontsize=12,
            ha='center', va='center', color='#333', fontproperties=font_prop)

    ax.text(0.3, 4.7, '检\n验\n层', fontsize=12, ha='center', va='center',
            color=border_mid, fontproperties=font_prop_bold)

    # --- 顶层：C2机制形式化 ---
    top_box = FancyBboxPatch((1, 6.4), 10, 2.2,
                             boxstyle="round,pad=0.05,rounding_size=0.3",
                             facecolor=color_top, edgecolor=border_top, linewidth=2.5)
    ax.add_patch(top_box)

    ax.text(6, 7.9, 'C2：机制形式化', fontsize=16,
            ha='center', va='center', color=border_top, fontproperties=font_prop_bold)
    ax.text(6, 7.25, '细化路径：两步程序 → 四阶段认知编码机制', fontsize=12,
            ha='center', va='center', color='#333', fontproperties=font_prop)
    # 动态数据：C2 PLS-SEM指标
    ax.text(6, 6.75, f'量化检验：PLS-SEM建模（GoF = {data["gof"]:.3f}，beta = {data["beta2"]:.3f}）', fontsize=12,
            ha='center', va='center', color='#333', fontproperties=font_prop)

    ax.text(0.3, 7.5, '形\n式\n化\n层', fontsize=12, ha='center', va='center',
            color=border_top, fontproperties=font_prop_bold)

    # ============ 绘制层间箭头 ============
    arrow_style = "Simple, tail_width=8, head_width=20, head_length=15"

    arrow1 = FancyArrowPatch((6, 3.0), (6, 3.6),
                             arrowstyle=arrow_style, color='#666',
                             mutation_scale=1)
    ax.add_patch(arrow1)
    ax.text(6.4, 3.3, '跨语言适用性检验', fontsize=10, ha='left', va='center',
            color='#666', fontproperties=font_prop_italic)

    arrow2 = FancyArrowPatch((6, 5.8), (6, 6.4),
                             arrowstyle=arrow_style, color='#666',
                             mutation_scale=1)
    ax.add_patch(arrow2)
    ax.text(6.4, 6.1, '操作化与量化', fontsize=10, ha='left', va='center',
            color='#666', fontproperties=font_prop_italic)

    # ============ 右侧递进箭头 ============
    ax.annotate('', xy=(11.7, 8.2), xytext=(11.7, 1.2),
                arrowprops=dict(arrowstyle='->', color='#C62828', lw=2.5))
    ax.text(11.9, 4.7, '理\n论\n修\n补\n递\n进', fontsize=12, ha='left', va='center',
            color='#C62828', fontproperties=font_prop_bold)

    # ============ 底部说明 ============
    note_text = '说明：底层为Sullivan原理论基础；中层C1提供跨语言适用性检验；顶层C2聚焦前三阶段机制形式化及语言编码边界'
    ax.text(6, 0.3, note_text, fontsize=10, ha='center', va='center',
            color='#666', fontproperties=font_prop_italic)

    # ============ 保存图片 ============
    output_dir = get_output_dir()
    os.makedirs(output_dir, exist_ok=True)

    plt.tight_layout()
    png_path = f"{output_dir}/图35_Sullivan理论修补层级图.png"
    plt.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')

    # 高清输出（1200 DPI）
    hd_dir = get_hd_dir()
    os.makedirs(hd_dir, exist_ok=True)
    hd_path = os.path.join(hd_dir, os.path.basename(png_path))
    plt.savefig(hd_path, dpi=1200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    svg_path = hd_path.replace('.png', '.svg')
    plt.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')

    print("✅ 图35已保存至:")
    print(f"  - {png_path}")
    print(f"  - 高清: {hd_path}")
    print(f"  - 矢量: {svg_path}")

    plt.close()

if __name__ == "__main__":
    main()
