# -*- coding: utf-8 -*-
"""
图33 Q1-Q2-Q3研究发现整合框架
极简版：Q1-Q3为Sullivan主轴，Q2作为Goldberg横向结构参照
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

    # H3-2主指标：原型距离 × 认知通达度，成员级Spearman ρ
    if 'Spearman ρ' in pls_corr.columns:
        target = pls_corr[
            pls_corr['分析内容'].astype(str).str.contains('原型距离.*认知通达度', regex=True, na=False)
        ]
        if target.empty:
            raise ValueError('未找到H3-2主指标：原型距离 × 认知通达度')
        rho_val = target.iloc[0]['Spearman ρ']
        data['h3_2_rho'] = abs(float(rho_val))

    return data

def create_figure_8_1(data):
    """创建Q1-Q3主轴与Q2横向参照框架图"""

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
    main_x, main_w = 0.9, 4.35
    q1_y, q1_h = 5.35, 1.55
    q1_box = FancyBboxPatch((main_x, q1_y), main_w, q1_h,
                            boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor=colors['q1'],
                            edgecolor=colors['border_q1'],
                            linewidth=2.5)
    ax.add_patch(q1_box)

    # Q1内容
    y = q1_y + q1_h - 0.25
    main_center = main_x + main_w / 2
    ax.text(main_center, y, 'Q1 类型特征', fontsize=FONTS['box_title'], ha='center',
            fontweight='bold', color=colors['border_q1'])
    y -= LINE_SPACE['title_to_subtitle']
    ax.text(main_center, y, '（描述充分性 · Sullivan主线起点）', fontsize=FONTS['subtitle'], ha='center',
            color=colors['border_q1'])
    y -= LINE_SPACE['subtitle_to_content']
    ax.text(main_x + 0.25, y, '• 双维度分类体系   • 12类构式类型',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_line']
    ax.text(main_x + 0.25, y, '• 原型梯度结构',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_to_hypo']
    ax.text(main_center, y, f'H1-1: r={data["h1_1_r"]:.2f} 支持；H1-2: 限定支持',
            fontsize=FONTS['hypothesis'], ha='center', color='#0D47A1', style='italic')

    # ========== Q2 网络组织框 ==========
    q2_x, q2_w = 5.85, 3.7
    q2_y, q2_h = 3.15, 2.05
    q2_box = FancyBboxPatch((q2_x, q2_y), q2_w, q2_h,
                            boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor=colors['q2'],
                            edgecolor=colors['border_q2'],
                            linewidth=2.5)
    ax.add_patch(q2_box)

    # Q2内容
    y = q2_y + q2_h - 0.25
    q2_center = q2_x + q2_w / 2
    ax.text(q2_center, y, 'Q2 网络组织', fontsize=FONTS['box_title'], ha='center',
            fontweight='bold', color=colors['border_q2'])
    y -= LINE_SPACE['title_to_subtitle']
    ax.text(q2_center, y, '（横向扩展 · Goldberg构式网络）', fontsize=FONTS['subtitle'],
            ha='center', color=colors['border_q2'])
    y -= LINE_SPACE['subtitle_to_content']
    ax.text(q2_x + 0.25, y, f'• 描述性小世界：C={data["C"]:.2f}, L={data["L"]:.2f}, $\\sigma$={data["sigma"]:.2f}',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_line']
    ax.text(q2_x + 0.25, y, f'• 实例层链接：隐喻扩展{data["metaphor_pct"]:.2f}%',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_line']
    ax.text(q2_x + 0.25, y, '• 宏观类型社区与中心性趋势',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_to_hypo']
    ax.text(q2_center, y, 'H2: 描述性支持',
            fontsize=FONTS['hypothesis'], ha='center', color='#E65100', style='italic')

    # ========== Q3 认知机制框 ==========
    q3_y, q3_h = 0.85, 1.95
    q3_box = FancyBboxPatch((main_x, q3_y), main_w, q3_h,
                            boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor=colors['q3'],
                            edgecolor=colors['border_q3'],
                            linewidth=2.5)
    ax.add_patch(q3_box)

    # Q3内容
    y = q3_y + q3_h - 0.25
    ax.text(main_center, y, 'Q3 认知机制', fontsize=FONTS['box_title'], ha='center',
            fontweight='bold', color=colors['border_q3'])
    y -= LINE_SPACE['title_to_subtitle']
    ax.text(main_center, y, '（解释充分性 · Sullivan主线深化）', fontsize=FONTS['subtitle'], ha='center',
            color=colors['border_q3'])
    y -= LINE_SPACE['subtitle_to_content']
    ax.text(main_x + 0.25, y, '• 四阶段编码机制   • PLS-MGA结构共享',
            fontsize=FONTS['content'], ha='left')
    y -= LINE_SPACE['content_line']
    ax.text(main_x + 0.25, y, '• 路径强度分化',
            fontsize=FONTS['content'], ha='left')
    ax.text(main_center, q3_y + 0.48,
            f'H3-1: GoF={data["gof"]:.3f} 前三阶段支持',
            fontsize=FONTS['hypothesis'], ha='center', color='#1B5E20', style='italic')
    ax.text(main_center, q3_y + 0.22,
            f'H3-2: |ρ|={data["h3_2_rho"]:.2f} 限定性支持',
            fontsize=FONTS['hypothesis'], ha='center', color='#1B5E20', style='italic')

    # ========== Sullivan主轴：Q1 → Q3 ==========
    axis_x = main_center
    ax.annotate('', xy=(axis_x, q3_y + q3_h + 0.18), xytext=(axis_x, q1_y - 0.18),
                arrowprops=dict(arrowstyle='->,head_length=0.35,head_width=0.2',
                               color=colors['sullivan'], lw=2.8))
    ax.text(axis_x - 0.35, 4.0, 'Sullivan核心递进', fontsize=10, ha='center', va='center',
            color=colors['sullivan'], fontweight='bold', rotation=90)
    ax.text(axis_x + 0.38, 4.0, '类型描述 → 机制解释', fontsize=9.5, ha='center', va='center',
            color=colors['sullivan'], fontweight='bold', rotation=90)

    # ========== Q2侧向关系：输入依赖与结构参照 ==========
    ax.annotate('', xy=(q2_x, q2_y + q2_h - 0.25), xytext=(main_x + main_w, q1_y + 0.45),
                arrowprops=dict(arrowstyle='->,head_length=0.25,head_width=0.18',
                               color=colors['arrow'], lw=2.2))
    ax.text(5.55, 5.35, '输入依赖', fontsize=10, ha='center',
            color=colors['arrow'], fontweight='bold')

    ax.annotate('', xy=(main_x + main_w, q3_y + q3_h - 0.35), xytext=(q2_x, q2_y + 0.45),
                arrowprops=dict(arrowstyle='->,head_length=0.25,head_width=0.18',
                               color=colors['arrow'], lw=2.2))
    ax.text(5.55, 2.98, '结构参照', fontsize=10, ha='center',
            color=colors['arrow'], fontweight='bold')

    # ========== 底部总结 ==========
    ax.text(5, 0.35, 'Sullivan主线核心递进，Goldberg维度横向扩展',
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, '..', '结果_输出', 'Figures'))


def get_hd_dir():
    """获取高清图目录，自动适配 WSL 与 Windows UNC。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, '..', '..', '正文', '毕业论文高清图'))

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

    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')

    # 高清输出（1200 DPI）
    hd_dir = get_hd_dir()
    os.makedirs(hd_dir, exist_ok=True)
    hd_path = os.path.join(hd_dir, os.path.basename(png_path))
    fig.savefig(hd_path, dpi=1200, bbox_inches='tight', facecolor='white')
    svg_path = hd_path.replace('.png', '.svg')
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')

    plt.close(fig)

    print(f"✅ 图33已保存:\n  PNG: {png_path}")
    print(f"  高清: {hd_path}")
    print(f"  矢量: {svg_path}")

if __name__ == "__main__":
    main()
