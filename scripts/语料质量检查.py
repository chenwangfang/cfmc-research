#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语料库标注质量检查脚本

功能：
1. P1致命问题检查（JSON格式、必填字段、语料条数）
2. P2严重问题检查（ID唯一性、逻辑一致性）
3. P3中等问题检查（取值范围、编码规范）
4. P4轻微问题检查（Level 4字段、衍生文件对齐）

用法：
  python3 语料质量检查.py          # 完整检查
  python3 语料质量检查.py --p1     # 仅P1检查
  python3 语料质量检查.py --p2     # P1+P2检查
  python3 语料质量检查.py --alignment  # 衍生文件对齐检查
  python3 语料质量检查.py --report # 生成Markdown报告

作者：Claude Code
日期：2026-01-06
"""

import json
import re
import argparse
from pathlib import Path
from collections import Counter
from datetime import datetime
import sys

# ============================================================
# 路径配置
# ============================================================
BASE_PATH = Path("/mnt/e/博士毕业论文/大论文/论文撰写/统计分析")
JSON_PATH = BASE_PATH / "语料_输入/CFMC_5989.json"
TYPICAL_MD = BASE_PATH / "语料_输入/典型语例汇总.md"
TYPE12_DIR = BASE_PATH / "语料_输入/12类构式语料库"
REPORT_PATH = BASE_PATH / "结果_输出/语料质量检查报告.md"

# ============================================================
# 字段规范定义
# ============================================================

# 必填字段（33项）
REQUIRED_FIELDS = {
    # 基础字段（6项）
    'basic': ['original_id', 'full_sentence', 'construction', 'time', 'source', 'genre'],
    # Level 1核心字段（23项）
    'level1_a': ['construction_type', 'subject', 'copula', 'predicate'],
    'level1_b': ['source_domain', 'target_domain', 'mapping_direction', 'metaphor_type',
                 'thematic_role', 'copula_function', 'constructional_meaning'],
    'level1_c': ['cognitive_accessibility', 'mapping_basis', 'conceptual_complexity'],
    'level1_d': ['embodied_experience', 'cognitive_reference_point', 'entailment_richness'],
    'level1_e': ['prototype_distance', 'link_type', 'inter_construction_links',
                 'systematicity', 'conventionality', 'function_in_network'],
    # Level 2补充字段（4项）
    'level2': ['copula_type', 'holistic_imagery', 'relational_thinking', 'metaphor_novelty'],
}

# Level 4选填字段（6项）
LEVEL4_FIELDS = ['mapping_content', 'entailment', 'inheritance_links_detail',
                 'polysemy_links_detail', 'subpart_links_detail',
                 'cognitive_reference_point_description']

# 字段取值范围
FIELD_RANGES = {
    'cognitive_accessibility': {'type': 'range', 'min': 1, 'max': 5},
    'conceptual_complexity': {'type': 'range', 'min': 1, 'max': 5},
    'mapping_direction': {'type': 'enum', 'values': [1, 2, 3, 4]},
    'prototype_distance': {'type': 'enum', 'values': [1, 2, 3]},
    'link_type': {'type': 'enum', 'values': [1, 2, 3, 4]},
    'function_in_network': {'type': 'enum', 'values': [1, 2, 3, 4, 5]},
    'embodied_experience': {'type': 'range', 'min': 0.0, 'max': 1.0},
    'entailment_richness': {'type': 'range', 'min': 0.0, 'max': 1.0},
    'systematicity': {'type': 'range', 'min': 0.0, 'max': 1.0},
    'conventionality': {'type': 'range', 'min': 0.0, 'max': 1.0},
    'holistic_imagery': {'type': 'range', 'min': 0.0, 'max': 2.0},
    'relational_thinking': {'type': 'range', 'min': 0.0, 'max': 2.0},
    'metaphor_novelty': {'type': 'range', 'min': 0.0, 'max': 1.0},
}

# 编码取值规范
ENUM_VALUES = {
    'source_domain': ['SP', 'MV', 'OB', 'LV', 'BD', 'SN', 'FC', 'NT', 'HM', 'WR', 'EC', 'TR', 'FD', 'MC', 'GM'],
    'target_domain': ['TM', 'LF', 'EM', 'TH', 'SC', 'MR', 'AB', 'CM', 'ST', 'EV'],
    'construction_type': ['copular_metaphor', 'copular_simile', 'other'],
    'metaphor_type': ['ontological', 'structural', 'orientational'],
    'copula_type': ['standard', 'extended', 'negative', 'simile'],
    'copula_function': ['equative', 'attributive', 'identificational'],
    'genre': ['学术', '文学', '新闻', '网络', '对话'],
}

# ============================================================
# 检查函数
# ============================================================

def load_json():
    """加载JSON数据"""
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"P1-01 JSON解析错误: {e}"
    except FileNotFoundError:
        return None, f"P1-00 文件不存在: {JSON_PATH}"

def check_p1(data):
    """P1致命问题检查"""
    errors = []

    # P1-02: 顶层结构
    required_keys = ['metadata', 'field_definitions', 'field_types', 'constructions']
    for key in required_keys:
        if key not in data:
            errors.append(f"P1-02 缺少顶层键: {key}")

    if 'constructions' not in data:
        return errors  # 无法继续检查

    constructions = data['constructions']

    # P1-03: 语料条数
    if len(constructions) != 5989:
        errors.append(f"P1-03 语料条数异常: 预期5989条，实际{len(constructions)}条")

    # P1-04: ID格式
    id_pattern = re.compile(r'^xb_\d{5}$')
    invalid_ids = []
    for c in constructions:
        cid = c.get('id', '')
        if not id_pattern.match(cid):
            invalid_ids.append(cid)
    if invalid_ids:
        errors.append(f"P1-04 ID格式错误: {invalid_ids[:5]}{'...' if len(invalid_ids) > 5 else ''} (共{len(invalid_ids)}个)")

    # P1-05: 必填字段缺失
    all_required = []
    for fields in REQUIRED_FIELDS.values():
        all_required.extend(fields)

    missing_summary = Counter()
    for c in constructions:
        for field in all_required:
            if field not in c or c[field] is None:
                missing_summary[field] += 1

    if missing_summary:
        top_missing = missing_summary.most_common(5)
        errors.append(f"P1-05 必填字段缺失: {dict(top_missing)}")

    return errors

def check_p2(data):
    """P2严重问题检查"""
    errors = []
    constructions = data.get('constructions', [])

    # P2-01: ID唯一性
    ids = [c.get('id') for c in constructions]
    duplicates = [cid for cid, count in Counter(ids).items() if count > 1]
    if duplicates:
        errors.append(f"P2-01 重复ID: {duplicates[:5]}{'...' if len(duplicates) > 5 else ''}")

    # P2-02: 认知通达度-概念复杂度相关性
    try:
        ca_values = []
        cc_values = []
        for c in constructions:
            ca = c.get('cognitive_accessibility')
            cc = c.get('conceptual_complexity')
            if ca is not None and cc is not None:
                ca_values.append(float(ca))
                cc_values.append(float(cc))

        if len(ca_values) > 100:
            # 简化的Pearson相关计算
            n = len(ca_values)
            sum_ca = sum(ca_values)
            sum_cc = sum(cc_values)
            sum_ca_sq = sum(x**2 for x in ca_values)
            sum_cc_sq = sum(x**2 for x in cc_values)
            sum_ca_cc = sum(ca_values[i] * cc_values[i] for i in range(n))

            numerator = n * sum_ca_cc - sum_ca * sum_cc
            denominator = ((n * sum_ca_sq - sum_ca**2) * (n * sum_cc_sq - sum_cc**2)) ** 0.5

            if denominator > 0:
                r = numerator / denominator
                if not (-0.70 <= r <= -0.30):
                    errors.append(f"P2-02 认知通达度-概念复杂度相关性异常: r={r:.3f} (预期-0.70至-0.30)")
    except Exception as e:
        errors.append(f"P2-02 相关性计算失败: {e}")

    # P2-03: 原型距离与通达度对应性检查
    mismatch_count = 0
    for c in constructions:
        ca = c.get('cognitive_accessibility')
        pd = c.get('prototype_distance')
        if ca is not None and pd is not None:
            # 高通达(4-5)应对应距离1-2，低通达(1-2)应对应距离2-3
            if ca >= 4 and pd == 3:
                mismatch_count += 1
            elif ca <= 2 and pd == 1:
                mismatch_count += 1

    if mismatch_count > len(constructions) * 0.1:  # 超过10%视为异常
        errors.append(f"P2-03 原型距离与通达度不匹配: {mismatch_count}条 ({mismatch_count/len(constructions)*100:.1f}%)")

    return errors

def check_p3(data):
    """P3中等问题检查"""
    errors = []
    constructions = data.get('constructions', [])

    range_errors = Counter()
    enum_errors = Counter()

    for c in constructions:
        # 数值范围检查
        for field, spec in FIELD_RANGES.items():
            value = c.get(field)
            if value is None:
                continue
            try:
                value = float(value)
                if spec['type'] == 'range':
                    if not (spec['min'] <= value <= spec['max']):
                        range_errors[field] += 1
                elif spec['type'] == 'enum':
                    if int(value) not in spec['values']:
                        range_errors[field] += 1
            except (ValueError, TypeError):
                range_errors[field] += 1

        # 编码取值检查
        for field, valid_values in ENUM_VALUES.items():
            value = c.get(field)
            if value is not None and value not in valid_values:
                enum_errors[field] += 1

    if range_errors:
        errors.append(f"P3-01 取值范围错误: {dict(range_errors.most_common(5))}")

    if enum_errors:
        errors.append(f"P3-02 编码取值错误: {dict(enum_errors.most_common(5))}")

    return errors

def check_p4(data):
    """P4轻微问题检查"""
    errors = []
    constructions = data.get('constructions', [])

    # P4-01: Level 4字段填充统计
    level4_stats = {}
    for field in LEVEL4_FIELDS:
        count = sum(1 for c in constructions if c.get(field))
        level4_stats[field] = count

    low_fill = {k: v for k, v in level4_stats.items() if v < 100}
    if low_fill:
        errors.append(f"P4-01 Level 4字段填充不足(<100条): {low_fill}")

    # P4-02: 衍生文件存在性检查
    if not TYPICAL_MD.exists():
        errors.append(f"P4-02 衍生文件缺失: 典型语例汇总.md")

    if not TYPE12_DIR.exists():
        errors.append(f"P4-02 衍生目录缺失: 12类构式语料库/")
    elif TYPE12_DIR.is_dir():
        files = list(TYPE12_DIR.glob("*.md"))
        if len(files) < 12:
            errors.append(f"P4-02 12类构式文件不完整: 仅{len(files)}个文件")

    return errors

def check_alignment(data):
    """衍生文件对齐检查"""
    errors = []
    constructions = data.get('constructions', [])
    json_ids = set(c.get('id') for c in constructions)

    # 检查典型语例汇总.md中的ID
    if TYPICAL_MD.exists():
        with open(TYPICAL_MD, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有xb_XXXXX格式的ID
        md_ids = set(re.findall(r'xb_\d{5}', content))

        # 检查MD中引用但JSON中不存在的ID
        missing_in_json = md_ids - json_ids
        if missing_in_json:
            errors.append(f"对齐错误: 典型语例汇总.md引用了{len(missing_in_json)}个不存在的ID: {list(missing_in_json)[:5]}")

    return errors

def generate_statistics(data):
    """生成统计信息"""
    constructions = data.get('constructions', [])
    stats = {
        '总条数': len(constructions),
        '认知通达度分布': Counter(c.get('cognitive_accessibility') for c in constructions),
        '概念复杂度分布': Counter(c.get('conceptual_complexity') for c in constructions),
        '映射方向分布': Counter(c.get('mapping_direction') for c in constructions),
        '原型距离分布': Counter(c.get('prototype_distance') for c in constructions),
        '链接类型分布': Counter(c.get('link_type') for c in constructions),
    }
    return stats

def generate_report(p1_errors, p2_errors, p3_errors, p4_errors, stats):
    """生成Markdown报告"""
    report = f"""# 语料质量检查报告

**检查时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据文件**：{JSON_PATH.name}
**总条数**：{stats.get('总条数', 'N/A')}

---

## 问题汇总

| 级别 | 数量 | 状态 |
|:-----|:----:|:----:|
| P1致命 | {len(p1_errors)} | {'✓ 通过' if len(p1_errors)==0 else '✗ 需修复'} |
| P2严重 | {len(p2_errors)} | {'✓ 通过' if len(p2_errors)==0 else '✗ 需修复'} |
| P3中等 | {len(p3_errors)} | {'✓ 通过' if len(p3_errors)==0 else '△ 建议修复'} |
| P4轻微 | {len(p4_errors)} | {'✓ 通过' if len(p4_errors)==0 else '○ 可选修复'} |

---

## 详细问题列表

### P1 致命问题
"""
    if p1_errors:
        for e in p1_errors:
            report += f"- {e}\n"
    else:
        report += "无\n"

    report += "\n### P2 严重问题\n"
    if p2_errors:
        for e in p2_errors:
            report += f"- {e}\n"
    else:
        report += "无\n"

    report += "\n### P3 中等问题\n"
    if p3_errors:
        for e in p3_errors:
            report += f"- {e}\n"
    else:
        report += "无\n"

    report += "\n### P4 轻微问题\n"
    if p4_errors:
        for e in p4_errors:
            report += f"- {e}\n"
    else:
        report += "无\n"

    report += f"""
---

## 数据分布统计

### 认知通达度分布
{dict(stats.get('认知通达度分布', {}))}

### 概念复杂度分布
{dict(stats.get('概念复杂度分布', {}))}

### 映射方向分布
{dict(stats.get('映射方向分布', {}))}

---

*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return report

# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='语料库标注质量检查')
    parser.add_argument('--p1', action='store_true', help='仅P1检查')
    parser.add_argument('--p2', action='store_true', help='P1+P2检查')
    parser.add_argument('--alignment', action='store_true', help='衍生文件对齐检查')
    parser.add_argument('--report', action='store_true', help='生成Markdown报告')
    parser.add_argument('--quiet', '-q', action='store_true', help='安静模式，仅输出错误')
    args = parser.parse_args()

    print("=" * 60)
    print("语料库标注质量检查")
    print("=" * 60)
    print(f"数据文件: {JSON_PATH}")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    # 加载数据
    data, load_error = load_json()
    if load_error:
        print(f"\n✗ {load_error}")
        sys.exit(1)

    if not args.quiet:
        print(f"✓ JSON加载成功，共 {len(data.get('constructions', []))} 条语料")

    # P1检查
    print("\n[P1] 致命问题检查...")
    p1_errors = check_p1(data)
    if p1_errors:
        for e in p1_errors:
            print(f"  ✗ {e}")
    else:
        print("  ✓ P1检查通过")

    if args.p1:
        sys.exit(0 if len(p1_errors) == 0 else 1)

    # P2检查
    print("\n[P2] 严重问题检查...")
    p2_errors = check_p2(data)
    if p2_errors:
        for e in p2_errors:
            print(f"  ✗ {e}")
    else:
        print("  ✓ P2检查通过")

    if args.p2:
        sys.exit(0 if len(p1_errors) + len(p2_errors) == 0 else 1)

    # P3检查
    print("\n[P3] 中等问题检查...")
    p3_errors = check_p3(data)
    if p3_errors:
        for e in p3_errors:
            print(f"  △ {e}")
    else:
        print("  ✓ P3检查通过")

    # P4检查
    print("\n[P4] 轻微问题检查...")
    p4_errors = check_p4(data)
    if p4_errors:
        for e in p4_errors:
            print(f"  ○ {e}")
    else:
        print("  ✓ P4检查通过")

    # 对齐检查
    if args.alignment:
        print("\n[对齐] 衍生文件对齐检查...")
        align_errors = check_alignment(data)
        if align_errors:
            for e in align_errors:
                print(f"  ✗ {e}")
        else:
            print("  ✓ 对齐检查通过")

    # 统计
    stats = generate_statistics(data)

    # 汇总
    print("\n" + "=" * 60)
    print("检查汇总")
    print("=" * 60)
    total_errors = len(p1_errors) + len(p2_errors) + len(p3_errors) + len(p4_errors)
    print(f"P1致命: {len(p1_errors)}  P2严重: {len(p2_errors)}  P3中等: {len(p3_errors)}  P4轻微: {len(p4_errors)}")

    if len(p1_errors) == 0 and len(p2_errors) == 0:
        print("\n✓ 核心检查通过（无P1/P2问题），可以运行统计脚本")
    else:
        print("\n✗ 存在致命/严重问题，请先修复后再运行统计脚本")

    # 生成报告
    if args.report:
        report = generate_report(p1_errors, p2_errors, p3_errors, p4_errors, stats)
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存至: {REPORT_PATH}")

    sys.exit(0 if total_errors == 0 else 1)

if __name__ == "__main__":
    main()
