#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图31 Q2与Q1/Q3的整合关系示意图
用途：展示Q2网络组织分析在三个研究问题中的整合作用
输出：图31_Q2与Q1Q3的整合关系示意图.png
兼容：Windows / Linux / WSL
数据：动态读取自 结果_输出/Data/ 目录
"""

import os
import sys
import json
import platform
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties
import matplotlib
matplotlib.use('Agg')

# =============================================================================
# 跨平台字体配置
# =============================================================================
def get_chinese_font():
    """获取中文字体，自动适配Windows/Linux/WSL"""
    system = platform.system()

    # 候选字体路径
    font_candidates = []

    if system == 'Windows':
        # Windows原生
        font_candidates = [
            r'C:\Windows\Fonts\msyh.ttc',
            r'C:\Windows\Fonts\simhei.ttf',
            r'C:\Windows\Fonts\simsun.ttc',
        ]
    else:
        # Linux / WSL
        font_candidates = [
            '/mnt/c/Windows/Fonts/msyh.ttc',      # WSL访问Windows字体
            '/mnt/c/Windows/Fonts/simhei.ttf',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # Linux原生
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        ]

    # 查找可用字体
    for font_path in font_candidates:
        if os.path.exists(font_path):
            return font_path

    # 未找到中文字体，返回None（使用默认字体）
    print("⚠️ 未找到中文字体，图表中文可能无法正常显示")
    return None

# 初始化字体
font_path = get_chinese_font()
if font_path:
    font_prop = FontProperties(fname=font_path)
    font_prop_bold = FontProperties(fname=font_path, weight='bold')
else:
    font_prop = FontProperties()
    font_prop_bold = FontProperties(weight='bold')

# =============================================================================
# 数据加载
# =============================================================================
def get_data_dir():
    """获取Data目录路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', '结果_输出', 'Data')
    return os.path.normpath(data_dir)

def load_data():
    """从Data目录动态加载统计数据"""
    data_dir = get_data_dir()
    
    # 读取表74_小世界性质检验结果
    with open(os.path.join(data_dir, '表74_小世界性质检验结果.json'), 'r', encoding='utf-8') as f:
        table74 = json.load(f)
    
    # 读取表75_四类链接关系频率分布
    with open(os.path.join(data_dir, '表75_四类链接关系频率分布.json'), 'r', encoding='utf-8') as f:
        table75 = json.load(f)
    
    # 读取表60_双维度相关分析
    with open(os.path.join(data_dir, '表60_双维度相关分析.json'), 'r', encoding='utf-8') as f:
        table60 = json.load(f)
    
    # 提取数据（按指标名查找，更健壮）
    data = {}
    
    # 从表74提取小世界性质
    for item in table74:
        if item.get('指标') == '聚类系数C':
            data['C'] = item['实测值']
        elif item.get('指标') == '平均路径长度L':
            data['L'] = item['实测值']
        elif item.get('指标') == '小世界系数sigma':
            data['sigma'] = item['实测值']
    
    # 从表75提取隐喻扩展占比
    for item in table75:
        if item.get('链接类型') == '隐喻扩展链接':
            data['metaphor_pct'] = item['占比(%)']
            break
    
    # 从表60提取Pearson r
    for item in table60:
        if item.get('分析项目') == 'Pearson r':
            data['r'] = float(item['值'])
            break
    
    return data

# =============================================================================
# 图表生成
# =============================================================================
def create_figure(data):
    """创建Q2整合关系示意图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10), dpi=1200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # 颜色方案
    color_q1 = '#E3F2FD'
    color_q2 = '#FFF3E0'
    color_q3 = '#E8F5E9'
    border_q1 = '#1976D2'
    border_q2 = '#F57C00'
    border_q3 = '#388E3C'

    # Q1 框 (左)
    q1_box = FancyBboxPatch((0.5, 6), 4, 2.5, boxstyle="round,pad=0.1",
                             facecolor=color_q1, edgecolor=border_q1, linewidth=2)
    ax.add_patch(q1_box)
    ax.text(2.5, 7.8, '第5章 Q1类型体系', fontsize=18, fontproperties=font_prop_bold,
            ha='center', va='center', color=border_q1)
    ax.text(2.5, 7.1, '12类构式', fontsize=16, fontproperties=font_prop, ha='center', va='center')
    ax.text(2.5, 6.5, '原型梯度', fontsize=16, fontproperties=font_prop, ha='center', va='center')

    # Q3 框 (右)
    q3_box = FancyBboxPatch((9.5, 6), 4, 2.5, boxstyle="round,pad=0.1",
                             facecolor=color_q3, edgecolor=border_q3, linewidth=2)
    ax.add_patch(q3_box)
    ax.text(11.5, 7.8, '第7章 Q3认知机制', fontsize=18, fontproperties=font_prop_bold,
            ha='center', va='center', color=border_q3)
    ax.text(11.5, 7.1, '四阶段编码机制', fontsize=16, fontproperties=font_prop, ha='center', va='center')
    ax.text(11.5, 6.5, '汉语认知特色', fontsize=16, fontproperties=font_prop, ha='center', va='center')

    # 核心递进箭头 (Q1 → Q3)
    ax.annotate('', xy=(9.3, 7.25), xytext=(4.7, 7.25),
                arrowprops=dict(arrowstyle='->', color='#424242', lw=2.5))
    ax.text(7, 7.6, '核心递进', fontsize=17, fontproperties=font_prop_bold, ha='center', va='center',
            color='#424242')

    # Q2 框 (中下)
    q2_box = FancyBboxPatch((3.5, 1), 7, 3.5, boxstyle="round,pad=0.1",
                             facecolor=color_q2, edgecolor=border_q2, linewidth=2.5)
    ax.add_patch(q2_box)
    ax.text(7, 4, '第6章 Q2网络组织', fontsize=20, fontproperties=font_prop_bold,
            ha='center', va='center', color=border_q2)
    ax.text(7, 3.3, '本章核心发现：', fontsize=15, fontproperties=font_prop_bold,
            ha='center', va='center')
    
    # 动态数据：小世界性质
    ax.text(7, 2.7, f'• 小世界性质（C={data["C"]:.2f}, L={data["L"]:.2f}, σ={data["sigma"]:.2f}）',
            fontsize=14, fontproperties=font_prop, ha='center', va='center')
    
    # 动态数据：隐喻扩展占比
    ax.text(7, 2.2, f'• 四类链接共同构成（隐喻扩展{data["metaphor_pct"]:.2f}%主导）',
            fontsize=14, fontproperties=font_prop, ha='center', va='center')
    
    ax.text(7, 1.7, '• 双社区结构（C1低/中通达, C2高通达）',
            fontsize=14, fontproperties=font_prop, ha='center', va='center')

    # Q2 → Q1 连接 (证据反馈)
    ax.annotate('', xy=(2.5, 5.8), xytext=(5, 4.6),
                arrowprops=dict(arrowstyle='->', color=border_q2, lw=1.8,
                              connectionstyle='arc3,rad=0.2'))
    ax.text(2.8, 5.3, '证据反馈', fontsize=14, fontproperties=font_prop_bold, ha='center', va='center',
            color=border_q2)
    
    # 动态数据：相关系数
    ax.text(2.8, 4.9, f'(r≈{data["r"]:.2f})', fontsize=12, fontproperties=font_prop, ha='center', va='center',
            color=border_q2)

    # Q2 → Q3 连接 (结构铺垫)
    ax.annotate('', xy=(11.5, 5.8), xytext=(9, 4.6),
                arrowprops=dict(arrowstyle='->', color=border_q2, lw=1.8,
                              connectionstyle='arc3,rad=-0.2'))
    ax.text(11.2, 5.3, '结构铺垫', fontsize=14, fontproperties=font_prop_bold, ha='center', va='center',
            color=border_q2)
    ax.text(11.2, 4.9, '(认知基础)', fontsize=12, fontproperties=font_prop, ha='center', va='center',
            color=border_q2)

    # 底部说明
    ax.text(7, 0.3, '注：Q1→Q3为Sullivan理论修补的核心轴线，Q2提供网络层面独立证据',
            fontsize=14, fontproperties=font_prop, ha='center', va='center', color='#616161')

    plt.tight_layout()
    return fig

# =============================================================================
# 跨平台路径处理
# =============================================================================
def get_output_dir():
    """获取输出目录，自动适配Windows/Linux路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 向上一级到统计分析目录，再进入结果_输出/Figures
    output_dir = os.path.join(script_dir, '..', '结果_输出', 'Figures')
    output_dir = os.path.normpath(output_dir)

    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)

    return output_dir

# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    # 加载数据
    data = load_data()
    print(f"📊 加载数据：C={data['C']:.2f}, L={data['L']:.2f}, σ={data['sigma']:.2f}, r={data['r']:.2f}")
    
    output_dir = get_output_dir()

    fig = create_figure(data)

    # 保存PNG
    png_path = os.path.join(output_dir, "图31_Q2与Q1Q3的整合关系示意图.png")
    fig.savefig(png_path, dpi=1200, bbox_inches='tight', facecolor='white', edgecolor='none')

    plt.close()

    print(f"✅ 图31 已生成：")
    print(f"   PNG: {png_path}")
    print(f"   平台: {platform.system()}")
