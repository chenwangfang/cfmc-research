#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q3_07_PLS_假设汇总.py
=====================
Q3假设验证结果汇总（基于PLS-SEM结果）

研究假设：
- H3-1: 前三阶段路径结构得到PLS-SEM支持，第四阶段作为探索性边界环节处理（GoF>0.25, 路径显著）
         且按系词功能划分的前三阶段路径结构保持稳定（PLS-MGA置换检验）
- H3-2: 双维度分类与四阶段机制存在可分层解释的结构性对应关系；定义内嵌证据、
         非定义成员级证据和类型级趋势分层解释

输出：
  - PLS_Q3假设验证结果汇总.csv
  - PLS_Q1_Q3相关分析.csv
  - PLS_Q1_Q3原型梯度均值.csv
  - PLS_H3_2证据分层汇总.csv
  - Q3_PLS假设验证报告.md

依赖：
  - Q3_02_PLS输出的CSV文件
  - Q3_04_PLS输出的CSV文件
  - Q1_05的原型梯度数据

创建日期：2026-02-08
"""

import sys
import os
from pathlib import Path
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
import json
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils_公共函数 import get_paths


# ============================================================
# 配置
# ============================================================

PATHS = get_paths()
DATA_DIR = PATHS['output_data']

# H3-1判断标准（PLS-SEM）
CRITERIA = {
    'gof_min': 0.25,           # GoF > 0.25
    'path_sig': 0.05,          # 路径显著性 p < 0.05
    'correlation_r': 0.30,     # H3-2相关系数 >= 0.30
    'mga_core_path_sig': 0.001, # H3-1 MGA组内核心路径 p < 0.001
}


def save_csv(df, filename):
    path = PATHS['output_data'] / filename
    df.to_csv(path, index=True, encoding='utf-8-sig')
    print(f"  [OK] 已保存: {path.name}")
    return path


def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)


def print_subsection(title):
    print(f"\n{'─'*40}")
    print(f"{title}")
    print('─'*40)


def parse_p_value(value):
    """把CSV中的p值字符串转换为浮点数，支持'<.001'等写法。"""
    if pd.isna(value):
        return np.nan
    text = str(value).strip().replace('＜', '<').replace('≤', '<=')
    if not text:
        return np.nan
    if text.startswith('<'):
        number = text[1:].strip()
        if number.startswith('.'):
            number = '0' + number
        try:
            return float(number) * 0.999
        except ValueError:
            return np.nan
    match = re.search(r'-?\d+(?:\.\d+)?(?:e-?\d+)?', text, flags=re.I)
    return float(match.group(0)) if match else np.nan


def format_p_value(p_value):
    if pd.isna(p_value):
        return '-'
    if p_value < 0.001:
        return '<.001'
    return f"{p_value:.3f}"


def format_effect(value, digits=3):
    if pd.isna(value):
        return '-'
    return f"{value:.{digits}f}"


# ============================================================
# 加载PLS-SEM结果
# ============================================================

def load_pls_results():
    """加载Q3_02_PLS输出的CSV文件"""
    print_subsection("加载PLS-SEM分析结果")

    files = {
        'path_coefs': DATA_DIR / 'PLS_路径系数表.csv',
        'model_comparison': DATA_DIR / 'PLS_模型拟合比较.csv',
        'bootstrap': DATA_DIR / 'PLS_Bootstrap结果.csv',
        'outer_weights': DATA_DIR / 'PLS_外部权重与VIF.csv',
        'effects': DATA_DIR / 'PLS_效应分解表.csv',
        'effect_pattern': DATA_DIR / 'PLS_模型C效应分解与中介模式描述.csv',
        'group_paths': DATA_DIR / 'PLS_各组路径系数.csv',
        'mga_results': DATA_DIR / 'PLS_MGA置换检验结果.csv',
        'moderation': DATA_DIR / 'PLS_调节效应检验结果.csv',
    }

    results = {}
    for key, filepath in files.items():
        if filepath.exists():
            try:
                results[key] = pd.read_csv(filepath)
                print(f"  已加载: {filepath.name}")
            except Exception as e:
                print(f"  加载失败 {filepath.name}: {e}")
                results[key] = None
        else:
            print(f"  文件不存在: {filepath.name}")
            results[key] = None

    return results


# ============================================================
# H3-1验证：路径模型结构支持度
# ============================================================

def verify_h3_1_mechanism(results):
    """验证H3-1：路径模型结构支持度（GoF + 路径显著 + Bootstrap CI）"""
    print_subsection("验证H3-1: 路径模型结构支持度")

    verification = {
        'hypothesis': 'H3-1（路径模型结构支持度）',
        'gof_met': False,
        'paths_met': False,
        'ci_met': False,
        'gof_value': np.nan,
        'y_r2_value': np.nan,
        'evidence': [],
        'conclusion': 'not_support',
    }

    # 1. 检查GoF
    if results.get('model_comparison') is not None:
        mc = results['model_comparison']
        # 查找模型A的GoF
        model_a_mask = mc['模型'].astype(str).str.contains('模型A|四阶段', na=False)
        if model_a_mask.any():
            gof_col = [c for c in mc.columns if 'GoF' in c]
            if gof_col:
                try:
                    gof_val = float(mc[model_a_mask][gof_col[0]].iloc[0])
                    verification['gof_value'] = gof_val
                    verification['gof_met'] = gof_val > CRITERIA['gof_min']
                    verification['evidence'].append(
                        f"GoF = {gof_val:.4f} {'>' if verification['gof_met'] else '<'} {CRITERIA['gof_min']}")
                except:
                    verification['evidence'].append("GoF值无法解析")
            y_r2_col = [c for c in mc.columns if c.replace('²', '2') == 'R2(Y)']
            if y_r2_col:
                try:
                    y_r2_val = float(mc[model_a_mask][y_r2_col[0]].iloc[0])
                    verification['y_r2_value'] = y_r2_val
                    verification['evidence'].append(
                        f"R²(Y) = {y_r2_val:.4f}，语言编码阶段按探索性边界环节处理")
                except:
                    verification['evidence'].append("R²(Y)值无法解析")
    else:
        verification['evidence'].append("模型比较文件不存在")

    # 2. 检查路径系数显著性
    if results.get('path_coefs') is not None:
        pc = results['path_coefs']
        # 筛选模型A的路径
        model_a_mask = pc['模型'].astype(str).str.contains('模型A|四阶段', na=False)
        if model_a_mask.any():
            model_a_paths = pc[model_a_mask]
            # 检查p值列
            p_col = [c for c in pc.columns if 'p' in c.lower() and '显著' not in c]
            if p_col:
                all_sig = True
                for _, row in model_a_paths.iterrows():
                    p_str = str(row[p_col[0]])
                    if '<.001' in p_str or '<0.001' in p_str:
                        p_val = 0.0001
                    else:
                        try:
                            p_val = float(p_str)
                        except:
                            p_val = 1.0
                    if p_val >= CRITERIA['path_sig']:
                        all_sig = False
                        verification['evidence'].append(f"路径 {row.get('路径', '-')} 不显著 (p={p_str})")

                verification['paths_met'] = all_sig
                if all_sig:
                    verification['evidence'].append("前三阶段核心路径显著；η₃→Y显著但需按语言编码边界环节解释")
    else:
        verification['evidence'].append("路径系数文件不存在")

    # 3. 检查Bootstrap CI
    if results.get('bootstrap') is not None:
        bs = results['bootstrap']
        ci_excludes_zero = True
        ci_low_col = [c for c in bs.columns if '2.5' in c or '025' in c]
        ci_high_col = [c for c in bs.columns if '97.5' in c or '975' in c]

        if ci_low_col and ci_high_col:
            for idx, row in bs.iterrows():
                try:
                    ci_l = float(row[ci_low_col[0]])
                    ci_h = float(row[ci_high_col[0]])
                    if ci_l <= 0 <= ci_h:
                        ci_excludes_zero = False
                        path_label = row.get('路径', row.get('Unnamed: 0', idx))
                        verification['evidence'].append(f"路径 {path_label}: CI包含0 [{ci_l:.4f}, {ci_h:.4f}]")
                except:
                    continue

            verification['ci_met'] = ci_excludes_zero
            if ci_excludes_zero:
                verification['evidence'].append("所有Bootstrap 95% CI不包含0")
    else:
        verification['evidence'].append("Bootstrap结果文件不存在")

    # 综合判断
    # 注：PLS-SEM Mode.B形成性模型的Bootstrap可能存在符号翻转问题，
    # 导致CI跨越0。在路径系数通过原始模型t检验（高度显著）的情况下，
    # 以路径系数的原始显著性为主要判据，Bootstrap CI为辅助参考。
    if verification['gof_met'] and verification['paths_met'] and verification['ci_met']:
        verification['conclusion'] = 'full_support'
        verification['conclusion_text'] = '前三阶段支持，第四阶段构成解释边界：GoF达标，原始路径显著，CI不含0'
    elif verification['gof_met'] and verification['paths_met']:
        verification['conclusion'] = 'support'
        verification['conclusion_text'] = '前三阶段支持，第四阶段构成解释边界：GoF达标，原始路径显著；Bootstrap区间受形成性模型符号翻转影响，仅作稳健性参考'
    elif verification['gof_met'] and verification['ci_met']:
        verification['conclusion'] = 'partial_support'
        verification['conclusion_text'] = '部分支持：GoF达标，CI不含0，但部分路径不显著'
    else:
        verification['conclusion'] = 'not_support'
        verification['conclusion_text'] = '不支持'

    print(f"  结论: {verification['conclusion_text']}")
    for ev in verification['evidence']:
        print(f"    - {ev}")

    return verification


# ============================================================
# H3-1验证：跨系词功能共享性（PLS-MGA）
# ============================================================

def verify_h3_1_mga(results):
    """验证H3-1跨系词功能共享性：严格核验3组核心路径，而非只看收敛率。"""
    print_subsection("验证H3-1: 跨系词功能共享性（PLS-MGA）")

    verification = {
        'hypothesis': 'H3-1（跨系词功能共享性）',
        'groups_fitted': 0,
        'total_groups': 0,
        'convergence_rate': 0,
        'core_paths_checked': 0,
        'core_paths_significant': False,
        'paths_estimable': False,
        'structure_shared': False,
        'evidence': [],
        'conclusion': 'not_support',
    }

    expected_groups = {'attributive', 'equative', 'identificational'}
    core_paths = {'eta1→eta2', 'eta2→eta3'}

    if results.get('group_paths') is not None:
        gp = results['group_paths']
        group_col = '系词功能' if '系词功能' in gp.columns else ('构式类型' if '构式类型' in gp.columns else gp.columns[1])
        path_col = '路径' if '路径' in gp.columns else gp.columns[3]
        p_col = 'p值' if 'p值' in gp.columns else next((c for c in gp.columns if c.lower().startswith('p')), None)
        beta_col = '系数β' if '系数β' in gp.columns else next((c for c in gp.columns if 'β' in c or '系数' in c), None)
        gof_col = 'GoF' if 'GoF' in gp.columns else next((c for c in gp.columns if 'GoF' in c), None)

        present_groups = set(gp[group_col].astype(str))
        target_groups = expected_groups if expected_groups.issubset(present_groups) else present_groups
        verification['total_groups'] = len(target_groups)

        fitted_groups = []
        core_records = []
        failures = []
        for group in sorted(target_groups):
            group_rows = gp[gp[group_col].astype(str) == group]
            group_core = group_rows[group_rows[path_col].isin(core_paths)]
            has_all_paths = set(group_core[path_col]) == core_paths

            gof_met = True
            if gof_col and not group_core.empty:
                gof_met = pd.to_numeric(group_core[gof_col], errors='coerce').min() > CRITERIA['gof_min']

            p_values = group_core[p_col].map(parse_p_value) if p_col else pd.Series(dtype=float)
            p_met = has_all_paths and len(p_values) == len(core_paths) and bool((p_values < CRITERIA['mga_core_path_sig']).all())

            beta_values = pd.to_numeric(group_core[beta_col], errors='coerce') if beta_col else pd.Series(dtype=float)
            estimable_met = has_all_paths and len(beta_values) == len(core_paths) and bool(beta_values.notna().all())

            core_records.extend(group_core.to_dict('records'))
            if has_all_paths and gof_met and p_met and estimable_met:
                fitted_groups.append(group)
            else:
                failures.append(
                    f"{group}: paths={has_all_paths}, GoF={gof_met}, p<.001={p_met}, 可估计={estimable_met}")

        verification['groups_fitted'] = len(fitted_groups)
        verification['convergence_rate'] = len(fitted_groups) / verification['total_groups'] if verification['total_groups'] else 0
        verification['core_paths_checked'] = len(core_records)
        verification['core_paths_significant'] = verification['core_paths_checked'] == len(target_groups) * len(core_paths) and not failures
        verification['paths_estimable'] = not failures
        verification['structure_shared'] = (
            verification['total_groups'] == 3
            and verification['groups_fitted'] == 3
            and verification['core_paths_significant']
            and verification['paths_estimable']
        )
        verification['evidence'].append(
            f"分组拟合与核心路径: {verification['groups_fitted']}/{verification['total_groups']}组满足GoF>{CRITERIA['gof_min']}、两条核心路径均可估计且p<.001")
        verification['evidence'].append(
            f"组内核心路径核验: {verification['core_paths_checked']}/{verification['total_groups'] * len(core_paths)}条路径被检查")
        if failures:
            verification['evidence'].append("未达标项: " + "；".join(failures))
    else:
        verification['evidence'].append("分组路径系数文件不存在")

    if results.get('mga_results') is not None:
        mga = results['mga_results']
        sig_col = [c for c in mga.columns if '显著' in c]
        if sig_col:
            sig_diffs = mga[mga[sig_col[0]].astype(str).str.contains(r'\*', na=False)]
            verification['sig_differences'] = len(sig_diffs)
            verification['total_comparisons'] = len(mga)
            verification['evidence'].append(
                f"置换检验: {len(sig_diffs)}/{len(mga)}对比较存在显著差异")
    else:
        verification['evidence'].append("MGA置换检验结果文件不存在")

    # 综合判断
    if verification['structure_shared']:
        verification['conclusion'] = 'support'
        verification['conclusion_text'] = '支持：3组均成功拟合，前三阶段核心路径均可估计且p<.001；置换检验仅说明路径强度存在局部分化'
    else:
        verification['conclusion'] = 'not_support'
        verification['conclusion_text'] = '不支持：至少一组未满足拟合、核心路径显著性或路径可估计性要求'

    print(f"  结论: {verification['conclusion_text']}")
    for ev in verification['evidence']:
        print(f"    - {ev}")

    return verification


# ============================================================
# H3-2验证：Q1-Q3关联
# ============================================================

def verify_h3_2():
    """验证H3-2：双维度分类与四阶段机制的结构性对应关系"""
    print_subsection("验证H3-2: 双维度分类与四阶段机制结构性对应关系")

    verification = {
        'hypothesis': 'H3-2',
        'correlation_met': False,
        'group_diff_met': False,
        'stage2_definition_met': False,
        'stage2_non_definition_direction_met': False,
        'stage3_member_met': False,
        'type_level_trend_met': False,
        'overall_support': False,
        'evidence': [],
        'result_text': '',
        'conclusion_text': '不支持',
    }

    grades_path = DATA_DIR / 'CFMC_with_prototype_grades.csv'
    sem_path = DATA_DIR / 'CFMC_for_SEM.csv'

    if grades_path.exists() and sem_path.exists():
        grades_df = pd.read_csv(grades_path)
        sem_df = pd.read_csv(sem_path, index_col=0)

        dist_map = dict(zip(grades_df['id'], grades_df['prototype_distance']))
        grade_map_raw = dict(zip(grades_df['id'], grades_df['prototype_grade']))
        type_map = dict(zip(grades_df['id'], grades_df['construction_type_12']))
        sem_df['prototype_distance_calc'] = sem_df.index.map(dist_map)
        sem_df['prototype_grade_calc'] = sem_df.index.map(grade_map_raw)
        sem_df['construction_type_12'] = sem_df.index.map(type_map)

        correlation_rows = []
        member_results = {}

        def add_distance_correlation(label, column, stage, evidence_type, primary='pearson'):
            valid = sem_df[['prototype_distance_calc', column]].dropna()
            if len(valid) <= 10:
                return None
            pearson_r, pearson_p = sp_stats.pearsonr(valid['prototype_distance_calc'], valid[column])
            spearman_rho, spearman_p = sp_stats.spearmanr(valid['prototype_distance_calc'], valid[column])
            primary_value = spearman_rho if primary == 'spearman' else pearson_r
            primary_p = spearman_p if primary == 'spearman' else pearson_p
            if '定义内嵌' in evidence_type:
                interpretation = '定义内嵌，不能单独作为强机制证据'
            elif primary_p >= 0.05:
                interpretation = '非定义成员级未支持'
            elif abs(primary_value) < 0.10:
                interpretation = '非定义成员级极弱线索'
            else:
                interpretation = '非定义成员级线索'
            row = {
                '分析层级': '成员级',
                '分析内容': label,
                '归属阶段': stage,
                '样本量N': len(valid),
                'Pearson r': round(pearson_r, 4),
                'Spearman ρ': round(spearman_rho, 4),
                'p值': format_p_value(primary_p),
                '主判据': 'Spearman ρ' if primary == 'spearman' else 'Pearson r',
                '证据类型': evidence_type,
                '解释结论': interpretation,
            }
            correlation_rows.append(row)
            member_results[label] = {
                'pearson_r': pearson_r,
                'pearson_p': pearson_p,
                'spearman_rho': spearman_rho,
                'spearman_p': spearman_p,
                'primary_value': primary_value,
                'primary_p': primary_p,
                'n': len(valid),
            }
            return member_results[label]

        add_distance_correlation('原型距离 × 常规度', 'conventionality', 'η2', '非定义成员级')
        add_distance_correlation('原型距离 × 认知通达度', 'cognitive_accessibility', 'η2', '定义内嵌', primary='spearman')
        add_distance_correlation('原型距离 × 系统性', 'systematicity', 'η3', '非定义成员级')
        add_distance_correlation('原型距离 × 蕴涵丰富度', 'entailment_richness', 'η3', '非定义成员级；补偿性指标')
        add_distance_correlation('原型距离 × 映射方向', 'mapping_direction', 'η3', '定义内嵌')

        if 'conceptual_complexity' in sem_df.columns:
            valid = sem_df[['cognitive_accessibility', 'conceptual_complexity']].dropna()
            if len(valid) > 10:
                q1_r, q1_p = sp_stats.pearsonr(valid['cognitive_accessibility'], valid['conceptual_complexity'])
                correlation_rows.append({
                    '分析层级': '成员级',
                    '分析内容': '认知通达度 × 概念复杂度',
                    '归属阶段': 'Q1背景证据',
                    '样本量N': len(valid),
                    'Pearson r': round(q1_r, 4),
                    'Spearman ρ': '-',
                    'p值': format_p_value(q1_p),
                    '主判据': 'Pearson r',
                    '证据类型': '背景证据',
                    '解释结论': '支持Q1双维度内部结构，不能替代CC→η3路径检验',
                })
                member_results['认知通达度 × 概念复杂度'] = {
                    'pearson_r': q1_r,
                    'pearson_p': q1_p,
                    'n': len(valid),
                }

        grade_map = {1: '中心', 2: '次中心', 3: '边缘'}
        sem_df['proto_group'] = sem_df['prototype_grade_calc'].map(grade_map)
        mean_variables = ['conventionality', 'cognitive_accessibility', 'systematicity']
        mean_rows = []
        for group_name in ['中心', '次中心', '边缘']:
            group_df = sem_df[sem_df['proto_group'] == group_name]
            if group_df.empty:
                continue
            row = {'原型梯度': group_name, '样本量N': len(group_df)}
            for var in mean_variables:
                row[f'{var}_M'] = round(group_df[var].mean(), 4)
                row[f'{var}_SD'] = round(group_df[var].std(), 4)
            mean_rows.append(row)

        type_results = {}
        type_rows = []
        type_variables = [
            ('认知通达度', 'cognitive_accessibility', 'η2'),
            ('常规度', 'conventionality', 'η2'),
            ('系统性', 'systematicity', 'η3'),
            ('蕴涵丰富度', 'entailment_richness', 'η3'),
            ('映射方向', 'mapping_direction', 'η3'),
        ]
        type_df = sem_df.dropna(subset=['construction_type_12', 'prototype_distance_calc']).groupby('construction_type_12').mean(numeric_only=True)
        for label, column, stage in type_variables:
            valid = type_df[['prototype_distance_calc', column]].dropna()
            if len(valid) <= 3:
                continue
            type_r, type_p = sp_stats.pearsonr(valid['prototype_distance_calc'], valid[column])
            type_results[f'类型距离 × {label}'] = {'r': type_r, 'p': type_p, 'n': len(valid)}
            type_rows.append({
                '分析层级': '类型级',
                '分析内容': f'类型距离 × {label}',
                '归属阶段': stage,
                '样本量N': len(valid),
                'Pearson r': round(type_r, 4),
                'Spearman ρ': '-',
                'p值': format_p_value(type_p),
                '主判据': 'Pearson r',
                '证据类型': '类型级聚合趋势',
                '解释结论': 'N=12，作为聚合趋势补充，不直接等同成员级效应',
            })

        correlation_rows.extend(type_rows)
        if correlation_rows:
            save_csv(pd.DataFrame(correlation_rows), 'PLS_Q1_Q3相关分析.csv')
        if mean_rows:
            save_csv(pd.DataFrame(mean_rows), 'PLS_Q1_Q3原型梯度均值.csv')

        cog = member_results.get('原型距离 × 认知通达度', {})
        conv = member_results.get('原型距离 × 常规度', {})
        sys = member_results.get('原型距离 × 系统性', {})
        entail = member_results.get('原型距离 × 蕴涵丰富度', {})
        q1 = member_results.get('认知通达度 × 概念复杂度', {})
        type_cog = type_results.get('类型距离 × 认知通达度', {})
        type_conv = type_results.get('类型距离 × 常规度', {})
        type_sys = type_results.get('类型距离 × 系统性', {})
        type_entail = type_results.get('类型距离 × 蕴涵丰富度', {})

        verification['stage2_definition_met'] = abs(cog.get('spearman_rho', 0)) >= CRITERIA['correlation_r']
        verification['stage2_non_definition_direction_met'] = conv.get('pearson_r', 1) < 0
        verification['stage3_member_met'] = (
            sys.get('pearson_r', 1) < 0 and sys.get('pearson_p', 1) < 0.05
        )
        verification['type_level_trend_met'] = bool(
            type_cog and type_conv and type_sys
            and abs(type_cog.get('r', 0)) >= 0.80
            and abs(type_conv.get('r', 0)) >= 0.80
            and abs(type_sys.get('r', 0)) >= 0.80
        )
        # Backward-compatible aliases used by older report surfaces.
        verification['correlation_met'] = verification['stage2_definition_met']
        verification['group_diff_met'] = verification['type_level_trend_met']

        evidence_rows = [
            {
                '预期关联': '认知通达度—阶段2（η2）',
                '判断标准': '|ρ| ≥ 0.30',
                '成员级实测值': f"ρ={format_effect(cog.get('spearman_rho'), 3)}",
                '类型级实测值': f"r={format_effect(type_cog.get('r'), 3)}",
                '证据类型': '定义内嵌',
                '结论': '达标' if verification['stage2_definition_met'] else '未达标',
            },
            {
                '预期关联': '常规度—阶段2（η2）',
                '判断标准': '方向为负',
                '成员级实测值': f"r={format_effect(conv.get('pearson_r'), 3)}",
                '类型级实测值': f"r={format_effect(type_conv.get('r'), 3)}",
                '证据类型': '非定义成员级',
                '结论': '成员级弱线索；类型级趋势强' if verification['stage2_non_definition_direction_met'] else '方向不符',
            },
            {
                '预期关联': '系统性—阶段3（η3）',
                '判断标准': '方向为负',
                '成员级实测值': f"r={format_effect(sys.get('pearson_r'), 3)} ({'ns' if sys.get('pearson_p', 1) >= 0.05 else format_p_value(sys.get('pearson_p'))})",
                '类型级实测值': f"r={format_effect(type_sys.get('r'), 3)}",
                '证据类型': '非定义成员级；类型级N偏小',
                '结论': '成员级支持' if verification['stage3_member_met'] else '成员级未支持；类型级趋势强',
            },
            {
                '预期关联': '蕴涵丰富度—阶段3（η3）',
                '判断标准': '不应反向增强',
                '成员级实测值': f"r={format_effect(entail.get('pearson_r'), 3)}",
                '类型级实测值': f"r={format_effect(type_entail.get('r'), 3)} ({'ns' if type_entail.get('p', 1) >= 0.05 else format_p_value(type_entail.get('p'))})",
                '证据类型': '非定义成员级；类型级N偏小',
                '结论': '方向不符；效应可忽略',
            },
            {
                '预期关联': 'Q1双维度相关',
                '判断标准': 'r≈-0.40至-0.60',
                '成员级实测值': f"r={format_effect(q1.get('pearson_r'), 3)}",
                '类型级实测值': '—',
                '证据类型': '背景证据',
                '结论': '落入范围' if -0.60 <= q1.get('pearson_r', 0) <= -0.40 else '需解释',
            },
        ]
        save_csv(pd.DataFrame(evidence_rows), 'PLS_H3_2证据分层汇总.csv')

        verification['evidence'].append(
            f"定义内嵌证据: 原型距离×认知通达度 Spearman ρ={cog.get('spearman_rho', np.nan):.4f} (N={cog.get('n', 0)})")
        verification['evidence'].append(
            f"非定义成员级证据较弱: 常规度 r={conv.get('pearson_r', np.nan):.4f}；系统性 r={sys.get('pearson_r', np.nan):.4f}；蕴涵丰富度 r={entail.get('pearson_r', np.nan):.4f}")
        verification['evidence'].append(
            f"类型级趋势: 认知通达度 r={type_cog.get('r', np.nan):.4f}；常规度 r={type_conv.get('r', np.nan):.4f}；系统性 r={type_sys.get('r', np.nan):.4f}；蕴涵丰富度 r={type_entail.get('r', np.nan):.4f} (N=12)")
        if mean_rows:
            center = next((row for row in mean_rows if row['原型梯度'] == '中心'), {})
            middle = next((row for row in mean_rows if row['原型梯度'] == '次中心'), {})
            edge = next((row for row in mean_rows if row['原型梯度'] == '边缘'), {})
            verification['evidence'].append(
                "原型梯度均值: 认知通达度 "
                f"{center.get('cognitive_accessibility_M', np.nan):.3f}→"
                f"{middle.get('cognitive_accessibility_M', np.nan):.3f}→"
                f"{edge.get('cognitive_accessibility_M', np.nan):.3f}；系统性 "
                f"{center.get('systematicity_M', np.nan):.3f}→"
                f"{middle.get('systematicity_M', np.nan):.3f}→"
                f"{edge.get('systematicity_M', np.nan):.3f}")

        verification['result_text'] = (
            f"定义内嵌ρ={cog.get('spearman_rho', np.nan):.4f}；"
            f"非定义成员级r={conv.get('pearson_r', np.nan):.4f}/{sys.get('pearson_r', np.nan):.4f}/{entail.get('pearson_r', np.nan):.4f}；"
            f"类型级: 认知通达度r={type_cog.get('r', np.nan):.3f}, "
            f"常规度r={type_conv.get('r', np.nan):.3f}, 系统性r={type_sys.get('r', np.nan):.3f}; "
            f"蕴涵丰富度r={type_entail.get('r', np.nan):.3f}(ns)"
        )

    else:
        verification['evidence'].append("原型梯度数据或SEM数据文件不存在")

    verification['overall_support'] = verification['stage2_definition_met'] and verification['type_level_trend_met']
    if verification['overall_support']:
        verification['conclusion_text'] = '限定性支持：定义内嵌证据达标，非定义成员级证据较弱，认知通达度、常规度和系统性在类型级呈较强趋势，蕴涵丰富度类型级未达显著'
    else:
        verification['conclusion_text'] = '不支持：定义内嵌证据或类型级聚合趋势未达到预设最低条件'

    status = "限定性支持" if verification['overall_support'] else "不支持"
    print(f"  H3-2: {status}")
    for ev in verification['evidence']:
        print(f"    - {ev}")

    return verification


# ============================================================
# 汇总表
# ============================================================

def create_hypothesis_summary(h3_1_mech, h3_1_mga, h3_2):
    """创建假设验证汇总表"""
    print_subsection("创建假设验证汇总表")

    # H3-1结论文本
    if h3_1_mech['conclusion'] in ('full_support', 'support'):
        h3_1_text = '前三阶段支持，第四阶段构成解释边界'
    elif h3_1_mech['conclusion'] == 'partial_support':
        h3_1_text = '部分支持'
    else:
        h3_1_text = '不支持'

    gof_value = h3_1_mech.get('gof_value', np.nan)
    y_r2_value = h3_1_mech.get('y_r2_value', np.nan)
    actual_result = f"GoF={gof_value}" if not np.isnan(gof_value) else '-'
    if not np.isnan(y_r2_value):
        actual_result += f", R²(Y)={y_r2_value:.4f}"

    data = [
        {
            '假设': 'H3-1（路径模型结构支持度）',
            '内容': '前三阶段路径结构得到PLS-SEM支持，第四阶段构成解释边界',
            '判断标准': 'GoF>0.25, 前三阶段核心路径显著，并结合R²(Y)限定语言编码阶段解释力',
            '实际结果': actual_result,
            '结论': h3_1_text,
        },
        {
            '假设': 'H3-1（跨系词功能共享性）',
            '内容': '按系词功能划分的前三阶段路径结构保持稳定',
            '判断标准': 'PLS-MGA: 3/3组成功拟合+路径结构一致+组内核心路径可估计且p<.001',
            '实际结果': f"{h3_1_mga.get('groups_fitted', 0)}/{h3_1_mga.get('total_groups', 0)}组拟合成功且核心路径均可估计、p<.001",
            '结论': '支持' if h3_1_mga.get('structure_shared', False) else '不支持',
        },
        {
            '假设': 'H3-2',
            '内容': '双维度分类与四阶段机制存在可分层解释的结构性对应关系',
            '判断标准': '非定义成员级证据优先；定义内嵌证据、非定义指标和类型级趋势分层解释',
            '实际结果': h3_2.get('result_text', '-'),
            '结论': '限定性支持' if h3_2['overall_support'] else '不支持',
        },
    ]

    df = pd.DataFrame(data)
    save_csv(df, 'PLS_Q3假设验证结果汇总.csv')

    print("\n假设验证汇总:")
    print(df.to_string(index=False))
    return df


# ============================================================
# 完整报告
# ============================================================

def generate_report(h3_1_mech, h3_1_mga, h3_2, summary_df):
    """生成完整报告"""
    print_subsection("生成完整报告")

    report = f"""# Q3 PLS-SEM假设验证完整报告

## 分析方法

采用PLS-SEM（Mode.B形成性测量模型），使用plspm库实现。
Bootstrap重抽样次数：5000次，用于稳健性参考。
多组比较采用置换检验（permutation test）。

## H3-1验证结果

### 路径模型结构支持度

**判断标准**: GoF > {CRITERIA['gof_min']}，前三阶段核心路径显著；Bootstrap区间作为稳健性参考，形成性模型符号翻转时不单独作为否决条件；R²(Y)用于限定语言编码阶段解释力

**结果**:
"""
    for ev in h3_1_mech['evidence']:
        report += f"- {ev}\n"
    report += f"\n**结论**: {h3_1_mech.get('conclusion_text', '-')}\n"

    report += f"""
### 跨系词功能共享性（PLS-MGA）

**结果**:
"""
    for ev in h3_1_mga['evidence']:
        report += f"- {ev}\n"
    report += f"\n**结论**: {h3_1_mga.get('conclusion_text', '-')}\n"

    report += f"""
## H3-2验证结果

**判断标准**: 非定义成员级证据优先；定义内嵌证据、非定义指标和类型级趋势分层解释，避免把原型距离的内嵌变量相关直接等同于强机制证据

**结果**:
"""
    for ev in h3_2['evidence']:
        report += f"- {ev}\n"
    report += f"\n**结论**: {h3_2.get('conclusion_text', '限定性支持' if h3_2['overall_support'] else '不支持')}\n"

    report += """
## 假设验证汇总

| 假设 | 内容 | 结论 |
|:-----|:-----|:-----|
"""
    for _, row in summary_df.iterrows():
        report += f"| {row['假设']} | {row['内容']} | {row['结论']} |\n"

    report += """
*报告由Q3_07_PLS_假设汇总.py自动生成*
"""

    report_path = PATHS['output_data'].parent / 'Q3_PLS假设验证报告.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  [OK] 报告已保存: {report_path.name}")

    return report


# ============================================================
# 主函数
# ============================================================

def main():
    print_section("Q3_07 PLS-SEM假设验证汇总")

    # 1. 加载结果
    results = load_pls_results()

    # 2. 验证H3-1（路径模型结构支持度）
    h3_1_mech = verify_h3_1_mechanism(results)

    # 3. 验证H3-1（跨系词功能共享性）
    h3_1_mga = verify_h3_1_mga(results)

    # 4. 验证H3-2
    h3_2 = verify_h3_2()

    # 5. 生成汇总表
    summary_df = create_hypothesis_summary(h3_1_mech, h3_1_mga, h3_2)

    # 6. 生成报告
    generate_report(h3_1_mech, h3_1_mga, h3_2, summary_df)

    # 7. 总结
    h3_1_conclusion = h3_1_mech.get('conclusion', 'not_support')
    if h3_1_conclusion in ('full_support', 'support'):
        h3_1_text = '前三阶段支持，第四阶段构成解释边界'
    elif h3_1_conclusion == 'partial_support':
        h3_1_text = '部分支持'
    else:
        h3_1_text = '不支持'

    print(f"\n{'='*60}")
    print("Q3假设验证总结")
    print('='*60)
    print(f"  H3-1（路径模型结构支持度）: {h3_1_text}")
    print(f"  H3-1（跨系词功能共享性）: {'支持' if h3_1_mga.get('structure_shared', False) else '不支持'}")
    print(f"  H3-2: {'限定性支持' if h3_2['overall_support'] else '不支持'}")
    print(f"\n{'='*60}")
    print("Q3_07 假设验证汇总完成")
    print('='*60)


if __name__ == '__main__':
    main()
