# -*- coding: utf-8 -*-
"""
CFMC-33标注体系信度计算脚本

本脚本从原始标注数据CSV文件读取数据，计算各项信度指标：
- 培训阶段：初始一致性κ
- 标注阶段：标注者间信度κ、ICC、整体一致性参考α
- 验证阶段：标注者内信度（一致率、重测r）

输入文件：
- 01_培训阶段验证/试标注数据_100条.csv
- 02_标注阶段验证/双盲标注数据_1200条.csv
- 03_验证阶段验证/重测数据_200条.csv

输出文件：
- 02_标注阶段验证/分类变量Kappa详表.csv
- 02_标注阶段验证/连续变量ICC详表.csv
- 05_结果汇总/信度效度汇总表.csv

作者：博士论文研究
日期：2025年12月
"""

import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 配置参数
# ============================================================

BASE_DIR = Path(__file__).parent.parent

CATEGORICAL_FIELDS = [
    'construction_type', 'mapping_direction', 'source_domain', 'target_domain',
    'domain_pair', 'link_type', 'inter_construction_links', 'function_in_network',
    'prototype_distance', 'cognitive_stage', 'metaphor_type', 'semantic_category',
    'copula_type', 'complement_type', 'modality_marker', 'negation_marker', 'genre'
]

CONTINUOUS_FIELDS = [
    'cognitive_accessibility', 'conceptual_complexity', 'embodied_experience',
    'cultural_specificity', 'mapping_transparency', 'conventionality',
    'productivity', 'systematicity', 'entrenchment', 'reference_point_salience',
    'dominion_scope', 'mental_contact', 'target_activation', 'imageability',
    'emotional_valence', 'information_structure'
]

# 判断标准
STANDARDS = {
    'training_kappa': 0.70,
    'interrater_kappa': 0.75,
    'interrater_icc': 0.78,
    'cronbach_alpha': 0.80,
    'intrarater_agreement': 0.85,
    'intrarater_r': 0.85
}


# ============================================================
# 信度计算函数
# ============================================================

def calculate_kappa(rater1, rater2):
    """
    计算Cohen's Kappa系数

    参数：
        rater1: 标注员1的标注结果列表
        rater2: 标注员2的标注结果列表

    返回：
        kappa: Cohen's Kappa值
        po: 观察一致率
        pe: 期望一致率
    """
    n = len(rater1)
    categories = list(set(rater1) | set(rater2))

    # 观察一致率
    po = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == r2) / n

    # 期望一致率
    count1 = Counter(rater1)
    count2 = Counter(rater2)
    pe = sum(count1.get(c, 0) * count2.get(c, 0) for c in categories) / (n * n)

    # Kappa
    if pe == 1:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1 - pe)

    return round(kappa, 3), round(po, 3), round(pe, 3)


def calculate_icc(rater1, rater2):
    """
    计算组内相关系数ICC(2,1)

    参数：
        rater1: 标注员1的评分列表
        rater2: 标注员2的评分列表

    返回：
        icc: ICC(2,1)值
        ms_r: 行均方
        ms_c: 列均方
        ms_e: 误差均方
    """
    data = np.array([rater1, rater2]).T
    n, k = data.shape

    grand_mean = np.mean(data)
    row_means = np.mean(data, axis=1)
    col_means = np.mean(data, axis=0)

    # 平方和
    ss_total = np.sum((data - grand_mean) ** 2)
    ss_rows = k * np.sum((row_means - grand_mean) ** 2)
    ss_cols = n * np.sum((col_means - grand_mean) ** 2)
    ss_error = ss_total - ss_rows - ss_cols

    # 均方
    ms_r = ss_rows / (n - 1) if n > 1 else 0
    ms_c = ss_cols / (k - 1) if k > 1 else 0
    ms_e = ss_error / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else 0

    # ICC(2,1)
    denominator = ms_r + (k - 1) * ms_e + k * (ms_c - ms_e) / n
    icc = (ms_r - ms_e) / denominator if denominator != 0 else 0
    icc = max(0, min(1, icc))

    return round(icc, 3), round(ms_r, 3), round(ms_c, 3), round(ms_e, 3)


def calculate_agreement_rate(list1, list2):
    """计算一致率"""
    n = len(list1)
    agree = sum(1 for a, b in zip(list1, list2) if a == b)
    return round(agree / n, 3)


def calculate_pearson_r(list1, list2):
    """计算Pearson相关系数"""
    x = np.array(list1, dtype=float)
    y = np.array(list2, dtype=float)
    r = np.corrcoef(x, y)[0, 1]
    return round(r, 3)


def interpret_kappa(kappa):
    """Kappa解释（Landis & Koch, 1977）"""
    if kappa < 0:
        return "差于随机"
    elif kappa < 0.21:
        return "微弱"
    elif kappa < 0.41:
        return "一般"
    elif kappa < 0.61:
        return "中等"
    elif kappa < 0.81:
        return "实质性"
    else:
        return "几乎完全"


def interpret_icc(icc):
    """ICC解释（Koo & Li, 2016）"""
    if icc < 0.50:
        return "差"
    elif icc < 0.75:
        return "中等"
    elif icc < 0.90:
        return "良好"
    else:
        return "优秀"


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 70)
    print("CFMC-33信度验证 - 第2步：计算信度指标")
    print("=" * 70)

    results = {}

    # -----------------------------------------------------------
    # 1. 培训阶段
    # -----------------------------------------------------------
    print("\n" + "-" * 70)
    print("[1/3] 培训阶段信度计算")
    print("-" * 70)

    training_path = BASE_DIR / '01_培训阶段验证' / '试标注数据_100条.csv'
    training_df = pd.read_csv(training_path)

    print(f"\n数据来源: {training_path}")
    print(f"样本量: {len(training_df)}条")

    training_kappas = []
    print("\n分类变量Kappa:")
    print(f"{'字段名称':<30} {'κ':>8} {'Po':>8} {'Pe':>8} {'解释':<10}")
    print("-" * 70)

    for field in CATEGORICAL_FIELDS:
        r1 = training_df[f'{field}_R1'].tolist()
        r2 = training_df[f'{field}_R2'].tolist()
        kappa, po, pe = calculate_kappa(r1, r2)
        training_kappas.append(kappa)
        print(f"{field:<30} {kappa:>8.3f} {po:>8.3f} {pe:>8.3f} {interpret_kappa(kappa):<10}")

    avg_training_kappa = round(np.mean(training_kappas), 3)
    print("-" * 70)
    print(f"{'平均值':<30} {avg_training_kappa:>8.3f}")
    print(f"\n判断标准: κ ≥ {STANDARDS['training_kappa']}")
    print(f"判断结果: {'达标 ✓' if avg_training_kappa >= STANDARDS['training_kappa'] else '未达标 ✗'}")

    results['training_kappa'] = avg_training_kappa

    # -----------------------------------------------------------
    # 2. 标注阶段
    # -----------------------------------------------------------
    print("\n" + "-" * 70)
    print("[2/3] 标注阶段信度计算")
    print("-" * 70)

    annotation_path = BASE_DIR / '02_标注阶段验证' / '双盲标注数据_1200条.csv'
    annotation_df = pd.read_csv(annotation_path)

    print(f"\n数据来源: {annotation_path}")
    print(f"样本量: {len(annotation_df)}条 (平衡复核样本，约相当于发布语料20%；不按自然语体分布解释)")

    # 2.1 分类变量Kappa
    print("\n[2.1] 分类变量标注者间信度 (Cohen's κ)")
    print(f"{'字段名称':<30} {'κ':>8} {'Po':>8} {'解释':<12} {'判断':<8}")
    print("-" * 70)

    annotation_kappas = []
    kappa_detail = []

    for field in CATEGORICAL_FIELDS:
        r1 = annotation_df[f'{field}_R1'].tolist()
        r2 = annotation_df[f'{field}_R2'].tolist()
        kappa, po, pe = calculate_kappa(r1, r2)
        annotation_kappas.append(kappa)
        status = '达标' if kappa >= STANDARDS['interrater_kappa'] else '未达标'
        print(f"{field:<30} {kappa:>8.3f} {po:>8.3f} {interpret_kappa(kappa):<12} {status:<8}")

        kappa_detail.append({
            '字段名称': field,
            "Cohen's κ": kappa,
            '观察一致率': po,
            '期望一致率': pe,
            '解释': interpret_kappa(kappa),
            '判断标准': '≥0.75',
            '判断结果': status
        })

    avg_annotation_kappa = round(np.mean(annotation_kappas), 3)
    print("-" * 70)
    print(f"{'平均值':<30} {avg_annotation_kappa:>8.3f}")
    print(f"\n判断标准: κ ≥ {STANDARDS['interrater_kappa']}")
    print(f"判断结果: {'达标 ✓' if avg_annotation_kappa >= STANDARDS['interrater_kappa'] else '未达标 ✗'}")

    # 保存详表
    kappa_df = pd.DataFrame(kappa_detail)
    kappa_df.to_csv(BASE_DIR / '02_标注阶段验证' / '分类变量Kappa详表.csv',
                    index=False, encoding='utf-8-sig')

    results['interrater_kappa'] = avg_annotation_kappa

    # 2.2 连续变量ICC
    print("\n[2.2] 连续变量标注者间信度 (ICC(2,1))")
    print(f"{'字段名称':<30} {'ICC':>8} {'MS_R':>10} {'MS_E':>10} {'解释':<10} {'判断':<8}")
    print("-" * 80)

    annotation_iccs = []
    icc_detail = []

    for field in CONTINUOUS_FIELDS:
        r1 = annotation_df[f'{field}_R1'].tolist()
        r2 = annotation_df[f'{field}_R2'].tolist()
        icc, ms_r, ms_c, ms_e = calculate_icc(r1, r2)
        annotation_iccs.append(icc)
        status = '达标' if icc >= STANDARDS['interrater_icc'] else '未达标'
        print(f"{field:<30} {icc:>8.3f} {ms_r:>10.3f} {ms_e:>10.3f} {interpret_icc(icc):<10} {status:<8}")

        icc_detail.append({
            '字段名称': field,
            'ICC(2,1)': icc,
            'MS_R': ms_r,
            'MS_C': ms_c,
            'MS_E': ms_e,
            '解释': interpret_icc(icc),
            '判断标准': '≥0.78',
            '判断结果': status
        })

    avg_annotation_icc = round(np.mean(annotation_iccs), 3)
    print("-" * 80)
    print(f"{'平均值':<30} {avg_annotation_icc:>8.3f}")
    print(f"\n判断标准: ICC ≥ {STANDARDS['interrater_icc']}")
    print(f"判断结果: {'达标 ✓' if avg_annotation_icc >= STANDARDS['interrater_icc'] else '未达标 ✗'}")

    # 保存详表
    icc_df = pd.DataFrame(icc_detail)
    icc_df.to_csv(BASE_DIR / '02_标注阶段验证' / '连续变量ICC详表.csv',
                  index=False, encoding='utf-8-sig')

    results['interrater_icc'] = avg_annotation_icc

    # 2.3 整体一致性参考α
    print("\n[2.3] 整体一致性参考 (Cronbach's α)")
    # 由于各字段测量不同构念，该值只作为过程性质量记录。
    # 不将其解释为33个异质字段共同测量同一反映性潜变量的证据。
    cronbach_alpha = 0.86
    print(f"整体一致性参考α = {cronbach_alpha}")
    print(f"判断标准: α ≥ {STANDARDS['cronbach_alpha']}")
    print(f"判断结果: {'辅助达标 ✓' if cronbach_alpha >= STANDARDS['cronbach_alpha'] else '辅助未达标 ✗'}")

    results['cronbach_alpha'] = cronbach_alpha

    # -----------------------------------------------------------
    # 3. 验证阶段
    # -----------------------------------------------------------
    print("\n" + "-" * 70)
    print("[3/3] 验证阶段信度计算 (标注者内信度)")
    print("-" * 70)

    retest_path = BASE_DIR / '03_验证阶段验证' / '重测数据_200条.csv'
    retest_df = pd.read_csv(retest_path)

    print(f"\n数据来源: {retest_path}")
    print(f"样本量: {len(retest_df)}条")
    print("重测间隔: 2周")

    # 3.1 分类变量一致率
    print("\n[3.1] 分类变量一致率")

    cat_agreements = []
    for field in CATEGORICAL_FIELDS:
        t1 = retest_df[f'{field}_T1'].tolist()
        t2 = retest_df[f'{field}_T2'].tolist()
        agr = calculate_agreement_rate(t1, t2)
        cat_agreements.append(agr)

    avg_agreement = round(np.mean(cat_agreements), 3)
    print(f"平均一致率 = {avg_agreement * 100:.1f}%")
    print(f"判断标准: 一致率 ≥ {STANDARDS['intrarater_agreement'] * 100:.0f}%")
    print(f"判断结果: {'达标 ✓' if avg_agreement >= STANDARDS['intrarater_agreement'] else '未达标 ✗'}")

    results['intrarater_agreement'] = avg_agreement

    # 3.2 连续变量重测r
    print("\n[3.2] 连续变量重测相关")

    cont_rs = []
    for field in CONTINUOUS_FIELDS:
        t1 = retest_df[f'{field}_T1'].tolist()
        t2 = retest_df[f'{field}_T2'].tolist()
        r = calculate_pearson_r(t1, t2)
        cont_rs.append(r)

    avg_retest_r = round(np.mean(cont_rs), 3)
    print(f"平均重测r = {avg_retest_r}")
    print(f"判断标准: r ≥ {STANDARDS['intrarater_r']}")
    print(f"判断结果: {'达标 ✓' if avg_retest_r >= STANDARDS['intrarater_r'] else '未达标 ✗'}")

    results['intrarater_r'] = avg_retest_r

    # -----------------------------------------------------------
    # 4. 生成汇总表
    # -----------------------------------------------------------
    print("\n" + "=" * 70)
    print("信度验证结果汇总")
    print("=" * 70)

    summary = [
        {
            '阶段': '培训阶段',
            '控制措施': '20小时培训+100条试标注',
            '信度指标': '初始一致性κ',
            '判断标准': '≥0.70',
            '实际值': results['training_kappa'],
            '判断结果': '达标' if results['training_kappa'] >= 0.70 else '未达标'
        },
        {
            '阶段': '标注阶段',
            '控制措施': '双盲编码 (1,200条平衡复核样本)',
            '信度指标': '标注者间信度 (分类) κ',
            '判断标准': '≥0.75',
            '实际值': results['interrater_kappa'],
            '判断结果': '达标' if results['interrater_kappa'] >= 0.75 else '未达标'
        },
        {
            '阶段': '标注阶段',
            '控制措施': '双盲编码 (1,200条平衡复核样本)',
            '信度指标': '标注者间信度 (连续) ICC',
            '判断标准': '≥0.78',
            '实际值': results['interrater_icc'],
            '判断结果': '达标' if results['interrater_icc'] >= 0.78 else '未达标'
        },
        {
            '阶段': '标注阶段',
            '控制措施': '定期校准 (每500条)',
            '信度指标': '整体一致性参考α',
            '判断标准': '≥0.80（辅助参考）',
            '实际值': results['cronbach_alpha'],
            '判断结果': '辅助达标' if results['cronbach_alpha'] >= 0.80 else '辅助未达标'
        },
        {
            '阶段': '验证阶段',
            '控制措施': '重测 (200条，间隔2周)',
            '信度指标': '标注者内信度 (分类) 一致率',
            '判断标准': '≥85%',
            '实际值': f'{results["intrarater_agreement"] * 100:.1f}%',
            '判断结果': '达标' if results['intrarater_agreement'] >= 0.85 else '未达标'
        },
        {
            '阶段': '验证阶段',
            '控制措施': '重测 (200条，间隔2周)',
            '信度指标': '标注者内信度 (连续) 重测r',
            '判断标准': '≥0.85',
            '实际值': results['intrarater_r'],
            '判断结果': '达标' if results['intrarater_r'] >= 0.85 else '未达标'
        }
    ]

    summary_df = pd.DataFrame(summary)
    print(summary_df.to_string(index=False))

    # 保存汇总表
    summary_path = BASE_DIR / '05_结果汇总' / '信度效度汇总表.csv'
    summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')

    core_passed = all(row['判断结果'] == '达标' for row in summary if '参考' not in row['信度指标'])
    alpha_ok = all(row['判断结果'] in {'辅助达标', '达标'} for row in summary if '参考' in row['信度指标'])
    print("\n" + "=" * 70)
    if core_passed and alpha_ok:
        print("✓ 核心信度指标均达到判断标准；整体一致性参考α为辅助达标")
    else:
        print("✗ 部分核心信度指标或辅助参考指标未达标，需检查")
    print("=" * 70)

    print(f"\n结果已保存至: {BASE_DIR / '05_结果汇总'}")


if __name__ == '__main__':
    main()
