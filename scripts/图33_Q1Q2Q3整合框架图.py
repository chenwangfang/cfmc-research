# -*- coding: utf-8 -*-
"""
图33 Q1-Q2-Q3研究发现整合与证据闭环框架
极简版：左侧括号连接Q1-Q3，右侧只保留图例
数据：动态读取自 结果_输出/Data/ 目录
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import os
import json
import pandas as pd

# 设置中文字体（WSL/Windows兼容）
import matplotlib.font_manager as fm
import platform

def setup_chinese_font():
    """配置中文字体，兼容WSL和Windows"""
    system = platform.system()

    if system == 'Windows':
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf',
        ]
    else:
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

    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    return False

setup_chinese_font()

# 字号配置
FONTS = {
    'main_title': 16,
    'box_title': 14,
    'subtitle': 11,
    'content': 11,
    'hypothesis': 10
}

# 紧凑行间距
LINE_SPACE = {
    'title_to_subtitle': 0.28,
    'subtitle_to_content': 0.30,
    'content_line': 0.26,
    'content_to_hypo': 0.28
}

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

    # 读取表59_双维度相关分析（H1-1）
    with open(os.path.join(data_dir, '表59_双维度相关分析.json'), 'r', encoding='utf-8') as f:
        table60 = json.load(f)

    # 读取表71_小世界性质检验结果（Q2）
    with open(os.path.join(data_dir, '表71_小世界性质检验结果.json'), 'r', encoding='utf-8') as f:
        table74 = json.load(f)

    # 读取表72_四类链接关系频率分布
    with open(os.path.join(data_dir, '表72_四类链接关系频率分布.json'), 'r', encoding='utf-8') as f:
        table75 = json.load(f)

    # 读取PLS_模型拟合比较.csv（H3-1 GoF，PLS模型GoF）
    pls_fit = pd.read_csv(os.path.join(data_dir, 'PLS_模型拟合比较.csv'), index_col=0)

    # 读取PLS_Q1_Q3相关分析.csv（H3-2）
    pls_corr = pd.read_csv(os.path.join(data_dir, 'PLS_Q1_Q3相关分析.csv'), index_col=0)

    data = {}

    # H1-1：从表60提取Pearson r
    for item in table60:
        if item.get('分析项目') == 'Pearson r':
            data['h1_1_r'] = float(item['值'])
            break

    # Q2小世界性质：从表74提取
    for item in table74:
        if item.get('指标') == '聚类系数C':
            data['C'] = item['实测值']
        elif item.get('指标') == '平均路径长度L':
            data['L'] = item['实测值']
        elif item.get('指标') == '小世界系数sigma':
            data['sigma'] = item['实测值']

    # 隐喻扩展占比：从表75提取
    for item in table75:
        if item.get('链接类型') == '隐喻扩展链接':
            data['metaphor_pct'] = item['占比(%)']
            break

    # H3-1 GoF：从PLS_模型拟合比较.csv提取模型A的GoF
    model_a_row = pls_fit[pls_fit['模型'].str.contains('模型A', na=False)]
    if not model_a_row.empty:
        data['gof'] = float(model_a_row.iloc[0]['GoF'])

    # H3-2相关系数：从PLS_Q1_Q3相关分析.csv提取
    if 'Spearman ρ' in pls_corr.columns:
        rho_val = pls_corr.iloc[0]['Spearman ρ']
        data['h3_2_rho'] = abs(float(rho_val))

    return data

def create_figure_8_1(data):
    """创建极简版Q1-Q2-Q3框架图"""

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # 颜色定义
    colors = {
        'q1': '#E3F2FD',
        'q2': '#FFF3E0',
        'q3': '#E8F5E9',
        'border_q1': '#1565C0',
        'border_q2': '#EF6C00',
        'border_q3': '#2E7D32',
        'sullivan': '#7B1FA2',
        'goldberg': '#EF6C00',
        'arrow': '#1565C0',
        'core': '#C62828'
    }

    # ========== Q1 类型特征框 ==========
    q1_y, q1_h = 5.6, 1.45
    q1_box = FancyBboxPatch((1.5, q1_y), 7, q1_h,
                            boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor=colors['q1'],
                            edgecolor=colors['border_q1'],
                            linewidth=2.5)
    ax.add_patch(q1_box)

    # Q1内容
    y = q1_y + q1_h - 0.25
    ax.text(5, y, 'Q1 类型特征', fontsize=FONTS['box_title'], ha='center',
            fontweight='bold', color=colors['border_q1'])
    y -= LINE_SPACE['title_to_subtitle']
    ax.text(5, y, '（描述充分性）', fontsize=FONTS['subtitle'], ha='center',
            color=colors['border_q1'])
    y -= LINE_SPACE['subtitle_to_content']
    ax.text(1.8, y, '• 双维度分类体系   • 12类构式类型   • 原型梯度结构',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_to_hypo']
    # 动态数据：H1-1相关系数
    ax.text(5, y, f'H1-1: r={data["h1_1_r"]:.2f} [√]    H1-2: 12类+梯度 [√]',
            fontsize=FONTS['hypothesis'], ha='center', color='#0D47A1', style='italic')

    # ========== Q2 网络组织框 ==========
    q2_y, q2_h = 3.0, 1.95
    q2_box = FancyBboxPatch((1.5, q2_y), 7, q2_h,
                            boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor=colors['q2'],
                            edgecolor=colors['border_q2'],
                            linewidth=2.5)
    ax.add_patch(q2_box)

    # Q2内容
    y = q2_y + q2_h - 0.25
    ax.text(5, y, 'Q2 网络组织', fontsize=FONTS['box_title'], ha='center',
            fontweight='bold', color=colors['border_q2'])
    y -= LINE_SPACE['title_to_subtitle']
    ax.text(5, y, '（独立研究维度 · Goldberg构式网络理论）', fontsize=FONTS['subtitle'],
            ha='center', color=colors['border_q2'])
    y -= LINE_SPACE['subtitle_to_content']
    # 动态数据：小世界性质
    ax.text(1.8, y, f'• 小世界性质：C={data["C"]:.2f}, L={data["L"]:.2f}, $\\sigma$={data["sigma"]:.2f}',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_line']
    # 动态数据：隐喻扩展占比
    ax.text(1.8, y, f'• 四类链接：隐喻扩展{data["metaphor_pct"]:.2f}%   • 双社区结构',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_line']
    ax.text(1.8, y, '• 中心性分析：枢纽节点连接各模块',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_to_hypo']
    ax.text(5, y, 'H2: C≥0.60 [√], L≤3.0 [√], $\\sigma$>1 [√]',
            fontsize=FONTS['hypothesis'], ha='center', color='#E65100', style='italic')

    # ========== Q3 认知机制框 ==========
    q3_y, q3_h = 0.9, 1.45
    q3_box = FancyBboxPatch((1.5, q3_y), 7, q3_h,
                            boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor=colors['q3'],
                            edgecolor=colors['border_q3'],
                            linewidth=2.5)
    ax.add_patch(q3_box)

    # Q3内容
    y = q3_y + q3_h - 0.25
    ax.text(5, y, 'Q3 认知机制', fontsize=FONTS['box_title'], ha='center',
            fontweight='bold', color=colors['border_q3'])
    y -= LINE_SPACE['title_to_subtitle']
    ax.text(5, y, '（解释充分性）', fontsize=FONTS['subtitle'], ha='center',
            color=colors['border_q3'])
    y -= LINE_SPACE['subtitle_to_content']
    ax.text(1.8, y, '• 四阶段编码机制   • 测量不变性验证   • 路径强度分析',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_to_hypo']
    # 动态数据：H3-1 GoF 和 H3-2 相关系数
    ax.text(5, y, f'H3-1: GoF={data["gof"]:.3f} [√]    H3-2: |rho|={data["h3_2_rho"]:.2f} [√]',
            fontsize=FONTS['hypothesis'], ha='center', color='#1B5E20', style='italic')

    # ========== 左侧：Sullivan理论括号连接Q1和Q3 ==========
    bracket_x = 1.1
    # 上括号臂（Q1）
    ax.plot([bracket_x, bracket_x - 0.15, bracket_x - 0.15],
            [q1_y + q1_h - 0.1, q1_y + q1_h - 0.1, q1_y + 0.1],
            color=colors['sullivan'], linewidth=2.5, solid_capstyle='round')
    # 下括号臂（Q3）
    ax.plot([bracket_x - 0.15, bracket_x - 0.15, bracket_x],
            [q3_y + q3_h - 0.1, q3_y + 0.1, q3_y + 0.1],
            color=colors['sullivan'], linewidth=2.5, solid_capstyle='round')
    # 中间连接竖线
    ax.plot([bracket_x - 0.15, bracket_x - 0.15],
            [q1_y + 0.1, q3_y + q3_h - 0.1],
            color=colors['sullivan'], linewidth=2.5, linestyle='--', alpha=0.5)
    # Sullivan标注
    ax.text(bracket_x - 0.4, (q1_y + q3_y + q3_h) / 2 + 0.8, 'Sullivan',
            fontsize=10, ha='center', va='center', color=colors['sullivan'],
            fontweight='bold', rotation=90)
    ax.text(bracket_x - 0.4, (q1_y + q3_y + q3_h) / 2 + 0.1, '理论',
            fontsize=10, ha='center', va='center', color=colors['sullivan'],
            fontweight='bold', rotation=90)
    ax.text(bracket_x - 0.4, (q1_y + q3_y + q3_h) / 2 - 0.6, '核心轴线',
            fontsize=10, ha='center', va='center', color=colors['sullivan'],
            fontweight='bold', rotation=90)

    # ========== 垂直流程箭头 ==========
    # Q1 → Q2
    ax.annotate('', xy=(5, 5.05), xytext=(5, 5.5),
                arrowprops=dict(arrowstyle='->,head_length=0.25,head_width=0.18',
                               color=colors['arrow'], lw=2.5))
    ax.text(5.5, 5.28, '输入依赖', fontsize=10, ha='left',
            color=colors['arrow'], fontweight='bold')

    # Q2 → Q3
    ax.annotate('', xy=(5, 2.4), xytext=(5, 2.9),
                arrowprops=dict(arrowstyle='->,head_length=0.25,head_width=0.18',
                               color=colors['arrow'], lw=2.5))
    ax.text(5.5, 2.65, '机制解释', fontsize=10, ha='left',
            color=colors['arrow'], fontweight='bold')

    # ========== 右侧：核心递进标注 ==========
    ax.annotate('', xy=(8.9, 1.6), xytext=(8.9, 6.4),
                arrowprops=dict(arrowstyle='->,head_length=0.35,head_width=0.2',
                               color=colors['core'], lw=2.5))
    ax.text(9.4, 4.0, '认识论递进', fontsize=10, ha='center', va='center',
            color=colors['core'], fontweight='bold', rotation=270)

    # ========== 整体目标 ==========
    ax.text(5, 0.35, '整体目标：Sullivan理论的汉语验证与本土化修补',
            fontsize=FONTS['subtitle'], ha='center', fontweight='bold', color='#424242')

    # ========== 图例（右上角） ==========
    legend_x, legend_y = 8.2, 7.55
    ax.plot([legend_x, legend_x + 0.3], [legend_y, legend_y],
            color=colors['sullivan'], linewidth=2.5)
    ax.text(legend_x + 0.4, legend_y, 'Sullivan理论', fontsize=9, ha='left', va='center')

    ax.plot([legend_x, legend_x + 0.3], [legend_y - 0.3, legend_y - 0.3],
            color=colors['goldberg'], linewidth=2.5)
    ax.text(legend_x + 0.4, legend_y - 0.3, 'Goldberg理论', fontsize=9, ha='left', va='center')

    plt.tight_layout()
    return fig

def get_output_dir():
    """获取输出目录，兼容WSL和Windows"""
    system = platform.system()

    if system == 'Windows':
        return r'E:\博士毕业论文\大论文\论文撰写\统计分析\结果_输出\Figures'
    elif system == 'Linux':
        if os.path.exists('/mnt/c/Windows'):
            return '/home/tomja/projects/博士毕业论文/大论文/论文撰写/统计分析/结果_输出/Figures'
        else:
            return os.path.dirname(os.path.abspath(__file__))
    else:
        return os.path.dirname(os.path.abspath(__file__))

def main():
    """主函数"""
    # 加载数据
    data = load_data()
    print(f"  加载数据：")
    print(f"   H1-1: r={data['h1_1_r']:.2f}")
    print(f"   Q2: C={data['C']:.2f}, L={data['L']:.2f}, sigma={data['sigma']:.2f}")
    print(f"   H3-1: GoF={data['gof']:.3f}")
    print(f"   H3-2: |rho|={data['h3_2_rho']:.2f}")
    
    output_dir = get_output_dir()
    os.makedirs(output_dir, exist_ok=True)

    fig = create_figure_8_1(data)

    png_path = os.path.join(output_dir, "图33_Q1Q2Q3研究发现整合框架.png")

    fig.savefig(png_path, dpi=1200, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"✅ 图33已保存:\n  PNG: {png_path}")

if __name__ == "__main__":
    main()
