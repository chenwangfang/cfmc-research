#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q2_08_整合分析.py
================
Q2网络组织分析整合与假设验证汇总

输出：
- 表87aux: Q2网络特征综合汇总
- 表87aux: Q2探索性分析发现汇总（正文表48）
- 表82a: 四类链接与构式特征关联分析
- 表81: Q2假设验证结果汇总

创建日期：2025-12-05
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import numpy as np
import pandas as pd
import networkx as nx
from scipy import stats
import json
import warnings
warnings.filterwarnings('ignore')

from utils_公共函数 import (
    get_paths, get_font_paths, save_table,
    HYPOTHESIS_CRITERIA, LINK_TYPE_CODES
)


def load_previous_results(paths: dict) -> dict:
    """
    加载之前分析的结果

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

    # 加载网络基本参数
    params_file = data_dir / '表70_两层网络基本参数.json'
    if params_file.exists():
        with open(params_file, 'r', encoding='utf-8') as f:
            results['network_params'] = json.load(f)
            print(f"[OK] 加载网络参数: {params_file}")

    # 加载小世界检验结果
    sw_file = data_dir / '表71_小世界性质检验结果.json'
    if sw_file.exists():
        with open(sw_file, 'r', encoding='utf-8') as f:
            results['small_world'] = json.load(f)
            print(f"[OK] 加载小世界结果: {sw_file}")

    # 加载小世界敏感性分析
    sens_file = data_dir / '表F5_小世界敏感性分析_附录F.json'
    if sens_file.exists():
        with open(sens_file, 'r', encoding='utf-8') as f:
            results['sensitivity'] = json.load(f)
            print(f"[OK] 加载敏感性分析: {sens_file}")

    # 加载链接类型分布
    link_file = data_dir / '表72_四类链接关系频率分布.json'
    if link_file.exists():
        with open(link_file, 'r', encoding='utf-8') as f:
            results['link_types'] = json.load(f)
            print(f"[OK] 加载链接类型: {link_file}")

    # 加载按构式类型交叉的实例层链接分布
    link_by_type_file = data_dir / '表75_12类构式实例层链接类型分布交叉表.json'
    if link_by_type_file.exists():
        with open(link_by_type_file, 'r', encoding='utf-8') as f:
            results['link_by_type'] = json.load(f)
            print(f"[OK] 加载实例层链接类型交叉表: {link_by_type_file}")

    # 加载宏观链接删除影响
    removal_file = data_dir / '表74_链接删除影响分析.json'
    if removal_file.exists():
        with open(removal_file, 'r', encoding='utf-8') as f:
            results['link_removal'] = json.load(f)
            print(f"[OK] 加载链接删除影响: {removal_file}")

    # 加载中心性指标
    cent_file = data_dir / '表76_构式类型组网络中心性指标.json'
    if cent_file.exists():
        with open(cent_file, 'r', encoding='utf-8') as f:
            results['centrality'] = json.load(f)
            print(f"[OK] 加载中心性指标: {cent_file}")

    # 加载社区检测结果
    comm_file = data_dir / '表77_社区检测结果.json'
    if comm_file.exists():
        with open(comm_file, 'r', encoding='utf-8') as f:
            results['community'] = json.load(f)
            print(f"[OK] 加载社区检测: {comm_file}")

    # 加载度分布统计
    degree_file = data_dir / '表F6_度分布统计_附录F.json'
    if degree_file.exists():
        with open(degree_file, 'r', encoding='utf-8') as f:
            results['degree'] = json.load(f)
            print(f"[OK] 加载度分布: {degree_file}")

    # 加载网络图
    network_file = data_dir / 'network_type_layer.graphml'
    if network_file.exists():
        results['G'] = nx.read_graphml(network_file)
        print(f"[OK] 加载网络: {network_file}")

    return results


def create_network_summary_table(results: dict) -> pd.DataFrame:
    """
    创建Q2网络特征综合汇总表（表76）

    Parameters
    ----------
    results : dict
        各项分析结果

    Returns
    -------
    pd.DataFrame
        综合汇总表
    """
    table_data = []

    # 网络规模
    if 'network_params' in results:
        for item in results['network_params']:
            if item.get('网络层级') == '类型层':
                table_data.append({'特征类别': '网络规模', '指标': '类型节点数', '数值': item.get('节点数', 'N/A')})
                table_data.append({'特征类别': '网络规模', '指标': '类型层边数', '数值': item.get('边数', 'N/A')})
            elif item.get('网络层级') == '实例层':
                table_data.append({'特征类别': '网络规模', '指标': '实例节点数', '数值': item.get('节点数', 'N/A')})

    # 小世界性质
    if 'small_world' in results:
        for item in results['small_world']:
            if item.get('指标') == '聚类系数C':
                table_data.append({'特征类别': '小世界性质', '指标': '聚类系数C', '数值': item.get('实测值', 'N/A')})
            elif item.get('指标') == '平均路径长度L':
                table_data.append({'特征类别': '小世界性质', '指标': '平均路径长度L', '数值': item.get('实测值', 'N/A')})
            elif item.get('指标') == '小世界系数sigma':
                table_data.append({'特征类别': '小世界性质', '指标': '小世界系数sigma', '数值': item.get('实测值', 'N/A')})

    # 链接类型
    if 'link_types' in results:
        for item in results['link_types']:
            link_name = item.get('链接类型', '')
            if link_name:
                table_data.append({
                    '特征类别': '链接类型分布',
                    '指标': link_name,
                    '数值': f"{item.get('频数', 0)} ({item.get('占比(%)', 0)}%)"
                })

    # 社区结构
    if 'community' in results:
        n_communities = len([x for x in results['community'] if x.get('社区编号', '').startswith('C')])
        table_data.append({'特征类别': '社区结构', '指标': '社区数量', '数值': n_communities})

        # 查找模块度
        for item in results['community']:
            if item.get('社区编号') == '整体':
                # 模块度需要从小世界结果中获取或重新计算
                pass

    return pd.DataFrame(table_data)


def create_exploratory_findings_summary_table(results: dict) -> pd.DataFrame:
    """
    创建正文表48对应的Q2探索性分析发现汇总表。

    该表直接服务正文6.4.4，对实例层链接类型、中心性、模块化和度分布
    四个维度作可复现汇总。
    """
    rows = []

    link_rows = [
        item for item in results.get('link_by_type', [])
        if item.get('构式类型') and item.get('构式类型') != '合计'
    ]
    if link_rows:
        groups = {
            '低通达度组': ['T1', 'T2', 'T3', 'T4'],
            '中通达度组': ['T5', 'T6', 'T7', 'T8'],
            '高通达度组': ['T9', 'T10', 'T11', 'T12'],
        }
        by_type = {item['构式类型']: item for item in link_rows}
        group_summaries = {}
        for group_name, members in groups.items():
            selected = [by_type[m] for m in members if m in by_type]
            total = sum(float(item.get('合计', 0)) for item in selected)
            metaphor = sum(float(item.get('隐喻扩展链接', 0)) for item in selected)
            polysemy = sum(float(item.get('多义链接', 0)) for item in selected)
            subpart = sum(float(item.get('子部分链接', 0)) for item in selected)
            group_summaries[group_name] = {
                'total': int(total),
                'metaphor_pct': round(metaphor / total * 100, 2) if total else 0,
                'polysemy_pct': round(polysemy / total * 100, 2) if total else 0,
                'subpart_pct': round(subpart / total * 100, 2) if total else 0,
            }
        rows.append({
            '分析维度': '实例层链接类型',
            '核心发现': '三组均以隐喻扩展为主，非主导类型呈现组间差异',
            '关键数据': (
                f"低/中/高通达度组隐喻扩展占比分别为"
                f"{group_summaries['低通达度组']['metaphor_pct']}%、"
                f"{group_summaries['中通达度组']['metaphor_pct']}%、"
                f"{group_summaries['高通达度组']['metaphor_pct']}%；"
                f"中通达度组多义关系{group_summaries['中通达度组']['polysemy_pct']}%；"
                f"低通达度组子部分关系{group_summaries['低通达度组']['subpart_pct']}%"
            ),
            '理论含义': '通达度分层与非主导链接类型分布存在描述性对应',
            '数据来源': '表75、正文表43'
        })

    centrality_rows = results.get('centrality', [])
    if centrality_rows:
        degree_groups = {}
        for item in centrality_rows:
            degree = int(float(item.get('度数', 0)))
            degree_groups.setdefault(degree, []).append(item.get('构式类型'))
        degree_parts = []
        for degree in sorted(degree_groups.keys(), reverse=True):
            members = sorted(degree_groups[degree], key=lambda x: int(str(x).replace('T', '')))
            degree_parts.append(f"{'/'.join(members)}度={degree}")
        rows.append({
            '分析维度': '中心性',
            '核心发现': '非高通达度枢纽现象',
            '关键数据': '；'.join(degree_parts) + '；特征向量中心性与通达度r=-0.859',
            '理论含义': '频率高不必然带来高中心性；中心性在当前网络中与认知通达度分层形成描述性对应',
            '数据来源': '表76、正文表44、正文表46'
        })

    community_rows = [
        item for item in results.get('community', [])
        if str(item.get('社区编号', '')).startswith('C')
    ]
    if community_rows:
        c_parts = []
        cross_edges = 38 - sum(int(float(item.get('社区内边数', 0))) for item in community_rows)
        for item in community_rows:
            c_parts.append(
                f"{item.get('社区编号')}({item.get('成员构式')})内部边{item.get('社区内边数')}"
            )
        c_parts.append(f"跨社区边{cross_edges}条")
        algorithm = community_rows[0].get('社区检测算法', '模块度优化')
        rows.append({
            '分析维度': '模块化',
            '核心发现': '低模块度条件下的探索性二元社区结构',
            '关键数据': '；'.join(c_parts) + f"；实际算法={algorithm}",
            '理论含义': '社区划分与认知通达度分层对应；不作为强模块化证据',
            '数据来源': '表77、表82a、正文表47'
        })

    degree_rows = results.get('degree', [])
    if degree_rows:
        degree = degree_rows[0]
        rows.append({
            '分析维度': '度分布',
            '核心发现': '三级分化',
            '关键数据': (
                f"平均度={degree.get('平均度')}，标准差={degree.get('标准差')}，"
                f"最小度={degree.get('最小度')}，最大度={degree.get('最大度')}"
            ),
            '理论含义': '度数分布不等同于使用频率，在当前建边规则下与认知通达度分层形成对应',
            '数据来源': '表F6、正文表48'
        })

    return pd.DataFrame(rows)


def create_link_feature_analysis(results: dict) -> pd.DataFrame:
    """
    创建四类链接与构式特征关联分析表（表77）

    Parameters
    ----------
    results : dict
        各项分析结果

    Returns
    -------
    pd.DataFrame
        关联分析表
    """
    table_data = []

    # 如果有链接类型数据和中心性数据，进行交叉分析
    if 'link_types' in results and 'centrality' in results:
        for link_item in results['link_types']:
            link_name = link_item.get('链接类型', '')
            if not link_name or link_name == '合计':
                continue

            # 分析该链接类型的特征
            table_data.append({
                '链接类型': link_name,
                '频数': link_item.get('频数', 0),
                '占比(%)': link_item.get('占比(%)', 0),
                '理论功能': link_item.get('理论说明', ''),
                '主要特征': get_link_characteristics(link_name)
            })

    return pd.DataFrame(table_data)


def get_link_characteristics(link_name: str) -> str:
    """获取链接类型的主要特征描述"""
    characteristics = {
        '隐喻扩展链接': '连接共享源域的构式，促进隐喻系统性',
        '多义链接': '连接语义相关但映射不同的构式',
        '子部分链接': '建立构式间的层级继承关系',
        '实例链接': '连接抽象类型与具体实例'
    }
    return characteristics.get(link_name, '未知特征')


def create_centrality_cognitive_correlation(results: dict) -> pd.DataFrame:
    """
    创建网络中心性与认知维度相关分析表（表78）

    Parameters
    ----------
    results : dict
        各项分析结果

    Returns
    -------
    pd.DataFrame
        相关分析表
    """
    table_data = []

    if 'centrality' in results and len(results['centrality']) > 0:
        # 转换为DataFrame进行分析
        cent_df = pd.DataFrame(results['centrality'])

        # 需要的列
        centrality_cols = ['度中心性', '中介中心性', '特征向量中心性']
        cognitive_cols = ['认知通达度均值', '概念复杂度均值', '样本量']

        for c_col in centrality_cols:
            if c_col not in cent_df.columns:
                continue
            for cog_col in cognitive_cols:
                if cog_col not in cent_df.columns:
                    continue

                # 计算相关系数
                try:
                    c_values = pd.to_numeric(cent_df[c_col], errors='coerce').dropna()
                    cog_values = pd.to_numeric(cent_df[cog_col], errors='coerce').dropna()

                    # 确保索引对齐
                    common_idx = c_values.index.intersection(cog_values.index)
                    if len(common_idx) >= 3:
                        r, p = stats.pearsonr(c_values[common_idx], cog_values[common_idx])
                        table_data.append({
                            '中心性指标': c_col,
                            '认知维度': cog_col,
                            'Pearson r': round(r, 4),
                            'p值': '<0.001' if p < 0.001 else f'{p:.3f}',
                            '显著性': '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns')),
                            '解释': interpret_correlation(r, c_col, cog_col)
                        })
                except Exception as e:
                    continue

    return pd.DataFrame(table_data)


def interpret_correlation(r: float, c_col: str, cog_col: str) -> str:
    """解释相关系数的含义"""
    if abs(r) < 0.3:
        strength = '弱'
    elif abs(r) < 0.5:
        strength = '中等'
    else:
        strength = '强'

    direction = '正' if r > 0 else '负'

    return f'{strength}{direction}相关'


def create_community_type_analysis(results: dict) -> pd.DataFrame:
    """
    创建社区结构与类型特征对应分析表（表79）

    Parameters
    ----------
    results : dict
        各项分析结果

    Returns
    -------
    pd.DataFrame
        对应分析表
    """
    table_data = []

    if 'community' in results:
        for item in results['community']:
            if item.get('社区编号', '').startswith('C'):
                table_data.append({
                    '社区编号': item.get('社区编号'),
                    '节点数': item.get('节点数', 0),
                    '成员构式': item.get('成员构式', ''),
                    '平均认知通达度': item.get('平均认知通达度', 'N/A'),
                    '平均概念复杂度': item.get('平均概念复杂度', 'N/A'),
                    '样本总量': item.get('样本总量', 0),
                    '社区特征': infer_community_characteristic(item)
                })

    return pd.DataFrame(table_data)


def infer_community_characteristic(item: dict) -> str:
    """推断社区的主要特征"""
    ca = item.get('平均认知通达度', 3)
    cc = item.get('平均概念复杂度', 3)

    try:
        ca = float(ca)
        cc = float(cc)
    except:
        return '特征待定'

    if ca >= 3.5 and cc <= 2.5:
        return '高通达-低复杂'
    elif ca <= 2.5 and cc >= 3.5:
        return '低通达-高复杂'
    elif ca >= 3.5 and cc >= 3.5:
        return '高通达-高复杂'
    elif ca <= 2.5 and cc <= 2.5:
        return '低通达-低复杂'
    else:
        return '中等水平'


def create_h2_verification_summary(results: dict) -> pd.DataFrame:
    """
    创建Q2假设验证结果汇总表（表80）

    Parameters
    ----------
    results : dict
        各项分析结果

    Returns
    -------
    pd.DataFrame
        验证结果汇总表
    """
    table_data = []

    # H2主假设：小世界性质
    h2_data = {
        '假设编号': 'H2',
        '假设内容': '完整12类型宏观网络满足小世界判据（C>=0.60，L<=3.0，sigma>1）',
        '验证方法': '小世界指标计算',
        '判断标准': 'C>=0.60，L<=3.0，sigma>1'
    }

    if 'small_world' in results:
        c_val = l_val = sigma_val = None
        c_pass = l_pass = sigma_pass = False

        for item in results['small_world']:
            if item.get('指标') == '聚类系数C':
                c_val = item.get('实测值')
                c_pass = item.get('达标') == '是'
            elif item.get('指标') == '平均路径长度L':
                l_val = item.get('实测值')
                l_pass = item.get('达标') == '是'
            elif item.get('指标') == '小世界系数sigma':
                sigma_val = item.get('实测值')
                sigma_pass = item.get('达标') == '是'

        h2_data['实际结果'] = f"C={c_val}, L={l_val}, sigma={sigma_val}"
        h2_data['统计显著性'] = 'N/A（描述性指标）'

        if c_pass and l_pass and sigma_pass:
            h2_data['验证结论'] = '描述性支持'
            h2_data['支持程度'] = '描述性'
        elif (c_pass and l_pass) or (c_pass and sigma_pass) or (l_pass and sigma_pass):
            h2_data['验证结论'] = '部分描述性支持'
            h2_data['支持程度'] = '描述性支持'
        else:
            h2_data['验证结论'] = '不支持'
            h2_data['支持程度'] = '无'
    else:
        h2_data['实际结果'] = '待计算'
        h2_data['验证结论'] = '待确认'
        h2_data['支持程度'] = '待确认'

    table_data.append(h2_data)

    # H2稳定性补充：随机边集扰动
    h2_stability_data = {
        '假设编号': 'H2-稳定性',
        '假设内容': '随机边集扰动下的小世界判定稳健性',
        '验证方法': '固定随机种子的删边补边敏感性分析',
        '判断标准': '均值层面C>=0.60，L<=3.0，sigma>1；同步报告单次达标风险'
    }

    if 'sensitivity' in results and results['sensitivity']:
        highest = results['sensitivity'][-1]
        h2_stability_data['实际结果'] = (
            f"{highest.get('扰动水平')}扰动（实际{highest.get('实际扰动比例', 'NA')}，"
            f"替换{highest.get('实际替换边数', 'NA')}条边）："
            f"C均值={highest.get('C均值')}, L均值={highest.get('L均值')}, "
            f"sigma均值={highest.get('sigma均值')}; "
            f"C达标率={highest.get('C达标率')}, sigma达标率={highest.get('sigma达标率')}"
        )
        h2_stability_data['统计显著性'] = 'N/A（敏感性分析）'
        h2_stability_data['验证结论'] = highest.get('均值层面判定', '待确认')
        h2_stability_data['支持程度'] = f"单次达标风险：{highest.get('单次达标风险', '待确认')}"
    else:
        h2_stability_data['实际结果'] = '待计算'
        h2_stability_data['统计显著性'] = 'N/A'
        h2_stability_data['验证结论'] = '待确认'
        h2_stability_data['支持程度'] = '待确认'

    table_data.append(h2_stability_data)

    # H2宏观边贡献补充：链接删除实验
    h2_macro_edge_data = {
        '假设编号': 'H2-宏观边贡献',
        '假设内容': '两类宏观操作边对小世界拓扑的结构贡献',
        '验证方法': '链接删除实验',
        '判断标准': '删除任一宏观边类型后观察聚类和连通性变化'
    }

    if 'link_removal' in results and results['link_removal']:
        parts = []
        for item in results['link_removal']:
            parts.append(
                f"删除{item.get('链接类型')}后C={item.get('删除后C')}，"
                f"连通性={item.get('删除后连通性')}"
            )
        h2_macro_edge_data['实际结果'] = '；'.join(parts)
        h2_macro_edge_data['统计显著性'] = 'N/A（结构删除实验）'
        h2_macro_edge_data['验证结论'] = '描述性支持'
        h2_macro_edge_data['支持程度'] = '宏观结构补充'
    else:
        h2_macro_edge_data['实际结果'] = '待计算'
        h2_macro_edge_data['统计显著性'] = 'N/A'
        h2_macro_edge_data['验证结论'] = '待确认'
        h2_macro_edge_data['支持程度'] = '待确认'

    table_data.append(h2_macro_edge_data)

    # H2补充：四类链接关系
    h2_link_data = {
        '假设编号': 'H2-补充',
        '假设内容': '四类链接关系共同构成微观实例层描述证据',
        '验证方法': '链接类型频率分析',
        '判断标准': '四类链接均存在'
    }

    if 'link_types' in results:
        n_types = len([x for x in results['link_types'] if x.get('频数', 0) > 0])
        dominant = next((x for x in results['link_types'] if x.get('链接类型') == '隐喻扩展链接'), {})
        dominant_ratio = dominant.get('占比(%)')
        if dominant_ratio is not None:
            h2_link_data['实际结果'] = f'识别到{n_types}类链接；隐喻扩展链接占{dominant_ratio}%'
        else:
            h2_link_data['实际结果'] = f'识别到{n_types}类链接'
        h2_link_data['统计显著性'] = 'N/A'
        h2_link_data['验证结论'] = '描述性支持' if n_types >= 4 else '部分描述性支持'
        h2_link_data['支持程度'] = '描述性补充' if n_types >= 4 else '中等'
    else:
        h2_link_data['实际结果'] = '待计算'
        h2_link_data['验证结论'] = '待确认'
        h2_link_data['支持程度'] = '待确认'

    table_data.append(h2_link_data)

    return pd.DataFrame(table_data)


def print_q2_conclusion(results: dict) -> None:
    """
    打印Q2整体验证结论

    Parameters
    ----------
    results : dict
        各项分析结果
    """
    print("\n" + "=" * 60)
    print("Q2网络组织分析整体结论")
    print("=" * 60)

    # 小世界性质
    print("\n1. 小世界性质验证:")
    if 'small_world' in results:
        for item in results['small_world']:
            if item.get('指标') in ['聚类系数C', '平均路径长度L', '小世界系数sigma']:
                print(f"   {item['指标']}: {item['实测值']} (达标: {item['达标']})")

    # 网络结构
    print("\n2. 网络结构特征:")
    if 'network_params' in results:
        for item in results['network_params']:
            if item.get('网络层级') == '类型层':
                print(f"   类型层: {item['节点数']}节点, {item['边数']}边")

    # 链接类型
    print("\n3. 链接类型分布:")
    if 'link_types' in results:
        for item in results['link_types']:
            if item.get('链接类型'):
                print(f"   {item['链接类型']}: {item['频数']} ({item['占比(%)']}%)")

    # 社区结构
    print("\n4. 社区结构:")
    if 'community' in results:
        n_comm = len([x for x in results['community'] if x.get('社区编号', '').startswith('C')])
        print(f"   检测到{n_comm}个社区")

    print("\n" + "=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("Q2_08_整合分析.py")
    print("Q2网络组织分析整合与假设验证汇总")
    print("=" * 60)

    # 获取路径
    paths = get_paths()

    # 1. 加载之前的分析结果
    print("\n" + "-" * 40)
    print("1. 加载之前的分析结果")
    print("-" * 40)
    results = load_previous_results(paths)

    # 2. 创建Q2网络特征综合汇总
    print("\n" + "-" * 40)
    print("2. 保存表87aux: Q2网络特征综合汇总")
    print("-" * 40)
    summary_table = create_network_summary_table(results)
    print(summary_table.to_string(index=False))
    save_table(summary_table, "Q2网络特征综合汇总", global_num="87aux",
               title="Q2网络特征综合汇总", formats=['csv', 'json'])

    # 3. 创建正文表48对应的探索性分析汇总
    print("\n" + "-" * 40)
    print("3. 保存表87aux: Q2探索性分析发现汇总（正文表48）")
    print("-" * 40)
    exploratory_summary = create_exploratory_findings_summary_table(results)
    print(exploratory_summary.to_string(index=False))
    save_table(exploratory_summary, "Q2探索性分析发现汇总", global_num="87aux",
               title="Q2探索性分析发现汇总", formats=['csv', 'json'])

    # 4. 创建表77
    print("\n" + "-" * 40)
    print("4. 保存表82a: 四类链接与构式特征关联分析")
    print("-" * 40)
    link_analysis = create_link_feature_analysis(results)
    print(link_analysis.to_string(index=False))
    save_table(link_analysis, "四类链接与构式特征关联分析", global_num="82a",  # 补充分析
               title="四类链接与构式特征关联分析", formats=['csv', 'json'])

    # 5. 创建中心性相关分析（已由Q2_04生成，保留屏幕复核）
    print("\n" + "-" * 40)
    print("5. 复核表78: 网络中心性与认知维度相关分析")
    print("-" * 40)
    corr_analysis = create_centrality_cognitive_correlation(results)
    if len(corr_analysis) > 0:
        print(corr_analysis.to_string(index=False))
    else:
        print("  数据不足，跳过相关分析")
    # [已删除] 网络中心性与认知维度相关分析 - 与Q2_04重复
#                title="网络中心性与认知维度相关分析", formats=['csv', 'json'])

    # 6. 创建社区结构与类型特征对应分析（已由Q2_05生成，保留屏幕复核）
    print("\n" + "-" * 40)
    print("6. 复核表82a: 社区结构与类型特征对应分析")
    print("-" * 40)
    comm_analysis = create_community_type_analysis(results)
    print(comm_analysis.to_string(index=False))
    # [已删除] 社区结构与类型特征对应分析 - 与Q2_05重复
#                title="社区结构与类型特征对应分析", formats=['csv', 'json'])

    # 7. 创建表81
    print("\n" + "-" * 40)
    print("7. 保存表81: Q2假设验证结果汇总")
    print("-" * 40)
    h2_summary = create_h2_verification_summary(results)
    print(h2_summary.to_string(index=False))
    save_table(h2_summary, "Q2假设验证结果汇总", global_num=81,
               title="Q2假设验证结果汇总", formats=['csv', 'json'])

    # 8. 打印整体结论
    print_q2_conclusion(results)

    print("\n" + "=" * 60)
    print("Q2_08_整合分析 完成")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
