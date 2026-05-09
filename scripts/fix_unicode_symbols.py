#!/usr/bin/env python3
"""
修复脚本：将 matplotlib 图表文本中的 Unicode 希腊字母替换为 LaTeX 数学模式
- σ → $\\sigma$
- β → $\\beta$
- η → $\\eta$
- R2 → $R^2$
等
"""
import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def fix_file(filename, replacements):
    """对指定文件执行一系列字符串替换"""
    filepath = os.path.join(SCRIPT_DIR, filename)

    # 备份
    backup = filepath + '.bak'
    if not os.path.exists(backup):
        shutil.copy(filepath, backup)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            changed += 1
        else:
            print(f"  [WARNING] 未找到: {repr(old[:60])}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  {filename}: {changed}/{len(replacements)} 处替换成功")
    return changed


def fix_Q2_02():
    """Q2_02_小世界检验.py: σ → $\\sigma$"""
    print("\n== Q2_02_小世界检验.py ==")
    replacements = [
        # Line 349: 非小世界区域标签
        ("'非小世界区域\\n(σ ≤ 1)'", "'非小世界区域\\n($\\\\sigma$ ≤ 1)'"),
        # Line 354: 小世界区域标签
        ("'小世界区域\\n(σ > 1)'", "'小世界区域\\n($\\\\sigma$ > 1)'"),
        # Line 359: 临界线标签
        ("'σ = 1 (临界值)'", "'$\\\\sigma$ = 1 (临界值)'"),
        # Line 367: 实测值标注
        ("f'σ = {sigma:.2f}'", "f'$\\\\sigma$ = {sigma:.2f}'"),
        # Line 372: 结果框（>1）
        ("f'σ = {sigma:.2f} > 1\\n✓ 支持小世界性质'",
         "f'$\\\\sigma$ = {sigma:.2f} > 1\\n✓ 支持小世界性质'"),
        # Line 376: 结果框（≤1）
        ("f'σ = {sigma:.2f} ≤ 1\\n✗ 不支持小世界性质'",
         "f'$\\\\sigma$ = {sigma:.2f} ≤ 1\\n✗ 不支持小世界性质'"),
        # Line 389: 图例 - 非小世界
        ("label='非小世界 (σ≤1)'", "label='非小世界 ($\\\\sigma$≤1)'"),
        # Line 390: 图例 - 小世界
        ("label='小世界 (σ>1)'", "label='小世界 ($\\\\sigma$>1)'"),
        # Line 391: 图例 - 实测值
        ("label=f'实测σ={sigma:.2f}'", "label=f'实测$\\\\sigma$={sigma:.2f}'"),
        # Line 397: Y轴标签
        ("'小世界系数 σ'", "'小世界系数 $\\\\sigma$'"),
        # Line 399: 标题
        ("'（c）小世界系数 σ 检验'", "'（c）小世界系数 $\\\\sigma$ 检验'"),
    ]
    fix_file('Q2_02_小世界检验.py', replacements)


def fix_Q3_02():
    """Q3_02_PLS_SEM基础模型.py: β → $\\beta$, η → $\\eta$, R2 → $R^2$"""
    print("\n== Q3_02_PLS_SEM基础模型.py ==")
    replacements = [
        # Line 696: 路径系数标注 β
        ("f'β={beta:.3f}{sig}'", "f'$\\\\beta$={beta:.3f}{sig}'"),
        # Line 731-733: 外部权重分组标签 η
        ("'η1 域激活': ['embodied_experience'",
         "'$\\\\eta_1$ 域激活': ['embodied_experience'"),
        ("'η2 参照点锚定': ['conventionality'",
         "'$\\\\eta_2$ 参照点锚定': ['conventionality'"),
        ("'η3 跨域映射': ['mapping_direction'",
         "'$\\\\eta_3$ 跨域映射': ['mapping_direction'"),
        # Line 813: R2=0.25 legend
        ("label='R2=0.25 (中等)'", "label='$R^2$=0.25 (中等)'"),
        # Line 814: R2=0.50 legend
        ("label='R2=0.50 (强)'", "label='$R^2$=0.50 (强)'"),
        # Line 815: R2(η3)对比 title
        ("'R2(η3)对比'", "'$R^2$($\\\\eta_3$)对比'"),
        # Line 816: R2 ylabel
        ("axes[1].set_ylabel('R2'", "axes[1].set_ylabel('$R^2$'"),
    ]
    fix_file('Q3_02_PLS_SEM基础模型.py', replacements)


def fix_图33():
    """图33_Q1Q2Q3整合框架图.py: σ → $\\sigma$"""
    print("\n== 图33_Q1Q2Q3整合框架图.py ==")
    replacements = [
        # Line 195: 小世界性质数据
        ("σ={data[\"sigma\"]:.2f}'", "$\\\\sigma$={data[\"sigma\"]:.2f}'"),
        # Line 205: H2假设结果
        ("σ>1 [√]'", "$\\\\sigma$>1 [√]'"),
    ]
    fix_file('图33_Q1Q2Q3整合框架图.py', replacements)


def fix_图25():
    """图25_整合关系示意图.py: σ → $\\sigma$"""
    print("\n== 图25_整合关系示意图.py ==")
    replacements = [
        # Line 168: 小世界性质数据
        ("σ={data[\"sigma\"]:.2f}）'", "$\\\\sigma$={data[\"sigma\"]:.2f}）'"),
    ]
    fix_file('图25_整合关系示意图.py', replacements)


def fix_Q2_06():
    """Q2_06_度分布.py: ≥ → $\\geq$ in axis label"""
    print("\n== Q2_06_度分布.py ==")
    replacements = [
        # Line 272: 累积概率 Y轴标签
        ("'累积概率 P(X ≥ k)'", "'累积概率 P(X $\\\\geq$ k)'"),
    ]
    fix_file('Q2_06_度分布.py', replacements)


if __name__ == '__main__':
    print("=" * 60)
    print("修复 matplotlib 图表文本中的 Unicode 符号 → LaTeX 数学模式")
    print("=" * 60)

    fix_Q2_02()
    fix_Q3_02()
    fix_图33()
    fix_图25()
    fix_Q2_06()

    print("\n" + "=" * 60)
    print("修复完成！请重新运行脚本生成图表以验证效果。")
    print("备份文件：*.py.bak")
    print("=" * 60)
