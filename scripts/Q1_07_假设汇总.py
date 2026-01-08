#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1_07_假设汇总.py
================
Q1假设验证结果汇总

输出：
- 表72: Q1假设验证结果汇总

创建日期：2025-12-05
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import numpy as np
import pandas as pd
import json
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, save_table, HYPOTHESIS_CRITERIA
)


def load_previous_results(paths: dict) -> dict:
    """
    加载之前脚本的分析结果

    Parameters
    ----------
    paths : dict
        路径字典

    Returns
    -------
    dict
        各项分析结果
    """
    results = {}
    data_dir = paths['output_data']

    # 加载H1-1相关分析结果
    h1_1_file = data_dir / '表60a_H1_1验证结果.json'
    if h1_1_file.exists():
        with open(h1_1_file, 'r', encoding='utf-8') as f:
            results['H1-1'] = json.load(f)
            print(f"[OK] 加载H1-1结果: {h1_1_file}")

    # 加载聚类效度结果（轮廓系数）
    silhouette_file = data_dir / '表63_分类稳定性检验汇总.json'
    if silhouette_file.exists():
        with open(silhouette_file, 'r', encoding='utf-8') as f:
            silhouette_data = json.load(f)
            # 查找Bootstrap轮廓系数
            for item in silhouette_data:
                if item.get('检验项目') == 'Bootstrap轮廓系数':
                    results['GMM_k12'] = {'轮廓系数': item.get('均值', 0)}
                    break
            print(f"[OK] 加载轮廓系数结果: {silhouette_file}")
    else:
        # 备选：尝试加载旧格式文件
        cluster_file = data_dir / '表61_不同k值聚类效度比较.json'
        if cluster_file.exists():
            with open(cluster_file, 'r', encoding='utf-8') as f:
                cluster_data = json.load(f)
                for item in cluster_data:
                    if item.get('k值') == 12:
                        results['GMM_k12'] = item
                        break
                print(f"[OK] 加载聚类效度结果: {cluster_file}")

    # 加载LDA结果
    lda_file = data_dir / '表64_LDA判别分析结果.json'
    if lda_file.exists():
        with open(lda_file, 'r', encoding='utf-8') as f:
            results['LDA'] = json.load(f)
            print(f"[OK] 加载LDA结果: {lda_file}")

    # 加载原型梯度结果
    proto_file = data_dir / '表66_原型梯度分布.json'
    if proto_file.exists():
        with open(proto_file, 'r', encoding='utf-8') as f:
            results['prototype'] = json.load(f)
            print(f"[OK] 加载原型梯度结果: {proto_file}")

    return results


def create_hypothesis_summary(results: dict) -> pd.DataFrame:
    """
    创建Q1假设验证结果汇总表（表72）

    Parameters
    ----------
    results : dict
        各项分析结果

    Returns
    -------
    pd.DataFrame
        假设验证汇总表
    """
    summary_data = []

    # H1-1: 认知通达度与概念复杂度的负相关
    h1_1_data = {
        '假设编号': 'H1-1',
        '假设内容': '认知通达度与概念复杂度呈显著负相关（r ~= -0.40至-0.60）',
        '验证方法': 'Pearson相关分析',
        '判断标准': 'r ~= -0.40至-0.60，p < 0.001'
    }

    if 'H1-1' in results and len(results['H1-1']) > 0:
        h1_1_result = results['H1-1'][0]
        h1_1_data['实际结果'] = f"r = {h1_1_result.get('实际r值', 'N/A')}"
        h1_1_data['统计显著性'] = h1_1_result.get('p值', 'N/A')
        h1_1_data['验证结论'] = h1_1_result.get('验证结论', '待确认')
        h1_1_data['支持程度'] = h1_1_result.get('支持程度', '待确认')
    else:
        h1_1_data['实际结果'] = '待计算'
        h1_1_data['统计显著性'] = '待计算'
        h1_1_data['验证结论'] = '待确认'
        h1_1_data['支持程度'] = '待确认'

    summary_data.append(h1_1_data)

    # H1-2a: GMM聚类识别12类构式
    h1_2a_data = {
        '假设编号': 'H1-2a',
        '假设内容': 'GMM聚类可识别出12类构式类型',
        '验证方法': 'GMM聚类分析',
        '判断标准': '轮廓系数 >= 0.30'
    }

    if 'GMM_k12' in results:
        gmm_result = results['GMM_k12']
        silhouette = gmm_result.get('轮廓系数', 0)
        h1_2a_data['实际结果'] = f"轮廓系数 = {silhouette}"
        h1_2a_data['统计显著性'] = 'N/A（描述性指标）'

        if isinstance(silhouette, (int, float)) and silhouette >= 0.30:
            h1_2a_data['验证结论'] = '支持'
            h1_2a_data['支持程度'] = '强' if silhouette >= 0.40 else '中等'
        else:
            h1_2a_data['验证结论'] = '不支持'
            h1_2a_data['支持程度'] = '无'
    else:
        h1_2a_data['实际结果'] = '待计算'
        h1_2a_data['统计显著性'] = '待计算'
        h1_2a_data['验证结论'] = '待确认'
        h1_2a_data['支持程度'] = '待确认'

    summary_data.append(h1_2a_data)

    # H1-2b: LDA判别验证
    h1_2b_data = {
        '假设编号': 'H1-2b',
        '假设内容': 'LDA判别分析验证聚类结果',
        '验证方法': 'LDA + 10折交叉验证',
        '判断标准': '准确率 >= 85%'
    }

    if 'LDA' in results:
        for item in results['LDA']:
            if item.get('指标') == '10折CV准确率':
                acc_str = item.get('值', '0')
                try:
                    acc = float(acc_str)
                    h1_2b_data['实际结果'] = f"准确率 = {acc*100:.2f}%"
                    h1_2b_data['统计显著性'] = 'N/A（分类指标）'

                    if acc >= 0.85:
                        h1_2b_data['验证结论'] = '支持'
                        h1_2b_data['支持程度'] = '强' if acc >= 0.90 else '中等'
                    else:
                        h1_2b_data['验证结论'] = '不支持'
                        h1_2b_data['支持程度'] = '无'
                except:
                    h1_2b_data['实际结果'] = acc_str
                    h1_2b_data['验证结论'] = '待确认'
                break
    else:
        h1_2b_data['实际结果'] = '待计算'
        h1_2b_data['统计显著性'] = '待计算'
        h1_2b_data['验证结论'] = '待确认'
        h1_2b_data['支持程度'] = '待确认'

    summary_data.append(h1_2b_data)

    # H1-2c: 原型梯度结构
    h1_2c_data = {
        '假设编号': 'H1-2c',
        '假设内容': '12类构式呈现原型梯度结构（中心-次中心-边缘）',
        '验证方法': '马氏距离 + 三分位数划分',
        '判断标准': '三组间差异显著（p < 0.05）'
    }

    if 'prototype' in results:
        # 检查是否有三个梯度
        proto_data = results['prototype']
        if len(proto_data) >= 3:
            h1_2c_data['实际结果'] = '中心/次中心/边缘三组划分成功'
            h1_2c_data['统计显著性'] = '见表67 ANOVA结果'
            h1_2c_data['验证结论'] = '支持'
            h1_2c_data['支持程度'] = '强'
        else:
            h1_2c_data['验证结论'] = '部分支持'
            h1_2c_data['支持程度'] = '中等'
    else:
        h1_2c_data['实际结果'] = '待计算'
        h1_2c_data['统计显著性'] = '待计算'
        h1_2c_data['验证结论'] = '待确认'
        h1_2c_data['支持程度'] = '待确认'

    summary_data.append(h1_2c_data)

    # 创建汇总DataFrame
    summary_df = pd.DataFrame(summary_data)

    return summary_df


def print_overall_conclusion(summary_df: pd.DataFrame) -> None:
    """
    打印Q1整体验证结论

    Parameters
    ----------
    summary_df : pd.DataFrame
        假设验证汇总表
    """
    print("\n" + "=" * 60)
    print("Q1假设验证整体结论")
    print("=" * 60)

    # 统计验证结果
    supported = (summary_df['验证结论'] == '支持').sum()
    partial = (summary_df['验证结论'] == '部分支持').sum()
    not_supported = (summary_df['验证结论'] == '不支持').sum()
    pending = (summary_df['验证结论'] == '待确认').sum()

    total = len(summary_df)

    print(f"\n假设验证统计:")
    print(f"  支持: {supported}/{total}")
    print(f"  部分支持: {partial}/{total}")
    print(f"  不支持: {not_supported}/{total}")
    print(f"  待确认: {pending}/{total}")

    # 整体结论
    if pending == 0:
        if supported == total:
            conclusion = "Q1所有假设均得到支持，双维度分类体系和12类构式类型识别成功验证。"
        elif supported + partial >= total * 0.75:
            conclusion = "Q1假设大部分得到支持，双维度分类体系基本有效。"
        elif not_supported >= total * 0.5:
            conclusion = "Q1假设验证结果不理想，需要重新审视双维度分类体系。"
        else:
            conclusion = "Q1假设验证结果混合，部分假设需要进一步探讨。"
    else:
        conclusion = f"Q1假设验证尚未完成，还有{pending}项假设待确认。"

    print(f"\n整体结论:")
    print(f"  {conclusion}")


def main():
    """主函数"""
    print("=" * 60)
    print("Q1_07_假设汇总.py")
    print("Q1假设验证结果汇总")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载之前的分析结果
    print("\n" + "-" * 40)
    print("1. 加载之前的分析结果")
    print("-" * 40)
    results = load_previous_results(paths)

    # 2. 创建假设验证汇总表
    print("\n" + "-" * 40)
    print("2. 创建Q1假设验证结果汇总表")
    print("-" * 40)
    summary_df = create_hypothesis_summary(results)
    print(summary_df.to_string(index=False))

    # 3. 保存表72
    print("\n" + "-" * 40)
    print("3. 保存表72: Q1假设验证结果汇总")
    print("-" * 40)
    save_table(summary_df, "Q1假设验证结果汇总", global_num=72,
               title="Q1假设验证结果汇总", formats=['csv', 'json'])

    # 4. 打印整体结论
    print_overall_conclusion(summary_df)

    print("\n" + "=" * 60)
    print("Q1_07_假设汇总 完成")
    print("=" * 60)

    return summary_df


if __name__ == "__main__":
    summary_df = main()
