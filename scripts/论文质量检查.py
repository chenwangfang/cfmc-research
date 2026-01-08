#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文质量检查脚本
配套Skill: thesis-checking

功能：自动扫描论文中的格式问题、禁用表达、一致性问题
输出：检查报告（按优先级P1-P4分类）

修复日志：
- 2025-12-18: 修复章节检测正则（中文→阿拉伯数字）
- 2025-12-18: 修复术语检测正则（添加T1-T12格式）
- 2025-12-18: 补充缺失检测规则（说白了、程式化句式）
- 2025-12-18: 添加段落长度检查
- 2025-12-18 v2: 修复S1引用正则跨括号bug
- 2025-12-18 v2: 修复S2删除过于宽泛的P1规则
- 2025-12-18 v2: 补充M1-M4缺失检测规则
- 2025-12-18 v2: 补充L1破折号格式检查、L2段落过短检查
"""

import re
import os
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ============ 路径配置 ============
BASE_PATH = Path("/mnt/e/博士毕业论文/大论文/论文撰写")
THESIS_PATH = BASE_PATH / "正文/基于语料库的汉语系表隐喻构式网络认知机制研究.md"
DATA_PATH = BASE_PATH / "统计分析/结果_输出/Data"
FIGURES_PATH = BASE_PATH / "统计分析/结果_输出/Figures"
MAPPING_FILE = BASE_PATH / "统计分析/图-表-语例编号对应关系.md"
LITERATURE_FILE = BASE_PATH / "正文/论文实际引用的文献.md"

# ============ 检查规则定义 ============

# P1 致命问题
# 注意：仅保留明确的AI痕迹词，删除过于宽泛的规则
P1_PATTERNS = {
    # 原规则已删除：过于宽泛导致大量误报
    # 以下为保留的高置信度检测项
    "非隐喻句_量化百分比": r"是[0-9]+(\.[0-9]+)?%",  # 精确匹配百分比
}

# P2 严重问题
P2_PATTERNS = {
    # 统计符号（补充：t, F, χ², n, k, df）
    "统计符号_p值": r"(?<![*\w])p\s*[<>=]",
    "统计符号_r值": r"(?<![*\w])r\s*=",
    "统计符号_beta": r"(?<![*])β\s*=",
    "统计符号_M值": r"(?<![*\w])M\s*=",
    "统计符号_SD": r"(?<![*])SD\s*=",
    "统计符号_t值": r"(?<![*\w])t\s*[=(]",  # 新增
    "统计符号_F值": r"(?<![*\w])F\s*[=(]",  # 新增
    "统计符号_卡方": r"(?<![*])χ²?\s*[=(]",  # 新增
    "统计符号_n值": r"(?<![*\w])n\s*=\s*[0-9]",  # 新增
    "统计符号_k值": r"(?<![*\w])k\s*=\s*[0-9]",  # 新增
    "统计符号_df": r"(?<![*])df\s*=",  # 新增
    # 引用格式（修复：排除中英文括号，限制匹配长度）
    "引用_中文括号": r"（[^）（\(\)]{0,50}[12][0-9]{3}[^）（\(\)]{0,30}）",
    "引用_缺逗号": r"\([A-Z][a-z]+\s+[12][0-9]{3}\)",
    # 术语（补充：概念难度、参照点）
    "术语_系词隐喻": r"系词隐喻构式",
    "术语_自主依存": r"自主依存原则(?!.*-)",
    "术语_认知可及": r"认知可及性",
    "术语_概念难度": r"概念难度",  # 新增：应为"概念复杂度"
    "术语_参照点": r"(?<!认知)参照点",  # 新增：应为"认知参照点"
}

# P3 中等问题
P3_PATTERNS = {
    # AI痕迹词
    "AI痕迹_值得注意": r"值得注意的是",
    "AI痕迹_需要强调": r"需要强调的是",
    "AI痕迹_特别值得": r"特别值得一提的是",
    "AI痕迹_不容忽视": r"不容忽视的是",
    "AI痕迹_重要的是": r"重要的是",
    "AI痕迹_有趣的是": r"有趣的是",
    "AI痕迹_令人惊讶": r"令人惊讶的是",
    # 过度自评
    "过度自评_首创": r"首创",
    "过度自评_开创性": r"开创性",
    "过度自评_填补空白": r"填补.*空白",
    "过度自评_里程碑": r"里程碑式",
    "过度自评_前所未有": r"前所未有",
    "过度自评_重大意义": r"具有重大意义",
    # 口语化
    "口语化_其实": r"其实",
    "口语化_当然": r"当然(?!规)",
    "口语化_毕竟": r"毕竟",
    "口语化_可以说": r"可以说",
    "口语化_不得不说": r"不得不说",
    "口语化_说白了": r"说白了",
    # 主观评价
    "主观_显然": r"显然",
    "主观_众所周知": r"众所周知",
    "主观_毫无疑问": r"毫无疑问",
    "主观_不言而喻": r"不言而喻",
    "主观_理所当然": r"理所当然",
    # 模糊量词（补充：少数、绝大多数、极少数）
    "模糊_很多": r"很多",
    "模糊_大量": r"大量",
    "模糊_部分": r"部分(?!分)",
    "模糊_若干": r"若干",
    "模糊_某种程度": r"某种程度上",
    "模糊_少数": r"(?<!极)少数",  # 新增：排除"极少数"
    "模糊_绝大多数": r"绝大多数",  # 新增
    "模糊_极少数": r"极少数",  # 新增
    # 破折号格式（新增L1）
    "格式_英文破折号连中文": r"[\u4e00-\u9fff]-[\u4e00-\u9fff]",  # 中文字间不应用英文-
}

# P4 轻微问题
P4_PATTERNS = {
    # 格式问题
    "格式_中文序号": r"^#+\s*[一二三四五六七八九十]+[、．.]",
    "格式_标签式": r"【[^】]+】",
    # 程式化表述（补充：总之）
    "程式化_本节分析了": r"本节分析了",
    "程式化_本章讨论了": r"本章讨论了",
    "程式化_本节介绍了": r"本节介绍了",
    "程式化_本章阐述了": r"本章阐述了",
    "程式化_综上所述": r"综上所述",
    "程式化_总而言之": r"总而言之",
    "程式化_总之": r"总之[，,]",  # 新增M4
    "程式化_以上内容表明": r"以上内容表明",
    # 做了什么句式
    "程式化_进行了分析": r"进行了.*分析",
    "程式化_开展了研究": r"开展了.*研究",
    "程式化_完成了讨论": r"完成了.*讨论",
}

# ============ 检查函数 ============

def load_thesis():
    """加载论文正文"""
    if not THESIS_PATH.exists():
        print(f"错误：论文文件不存在 - {THESIS_PATH}")
        return None
    with open(THESIS_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def scan_patterns(content, patterns, priority):
    """扫描正则表达式模式"""
    issues = []
    lines = content.split('\n')

    for name, pattern in patterns.items():
        regex = re.compile(pattern)
        for i, line in enumerate(lines, 1):
            matches = regex.findall(line)
            if matches:
                issues.append({
                    "priority": priority,
                    "type": name,
                    "line": i,
                    "content": line.strip()[:80],
                    "matches": matches
                })
    return issues

def check_figure_table_alignment(content):
    """检查图表引用与实际文件对齐"""
    issues = []

    # 提取正文中的图表引用
    figure_refs = set(re.findall(r'图([0-9]+-[0-9]+[a-z]?)', content))
    table_refs = set(re.findall(r'表([0-9]+-[0-9]+[a-z]?)', content))

    # 检查实际文件
    if FIGURES_PATH.exists():
        actual_figures = set()
        for f in FIGURES_PATH.glob("*.png"):
            match = re.search(r'图([0-9]+-[0-9]+)', f.name)
            if match:
                actual_figures.add(match.group(1))

        # 对比：文件存在但未引用
        missing_refs = actual_figures - figure_refs
        for fig in missing_refs:
            # 排除临时文件（如包含"0"的编号）
            if "-0" not in fig:
                issues.append({
                    "priority": "P3",
                    "type": "图表_未引用",
                    "line": 0,
                    "content": f"图{fig}存在于文件夹但未在正文中引用",
                    "matches": [fig]
                })

    if DATA_PATH.exists():
        actual_tables = set()
        for f in DATA_PATH.glob("表*.csv"):
            match = re.search(r'表([0-9]+-[0-9]+)', f.name)
            if match:
                actual_tables.add(match.group(1))

        missing_refs = actual_tables - table_refs
        for tbl in missing_refs:
            # 排除临时文件
            if "-0" not in tbl:
                issues.append({
                    "priority": "P3",
                    "type": "图表_未引用",
                    "line": 0,
                    "content": f"表{tbl}存在于文件夹但未在正文中引用",
                    "matches": [tbl]
                })

    return issues

def check_hypothesis_mentions(content):
    """检查假设在各章节的分布"""
    hypotheses = ["H1-1", "H1-2", "H2", "H3-1", "H3-2"]
    chapters = {}

    current_chapter = "0"
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # 检测阿拉伯数字章节标题（如"# 第1章 绪论"）
        chapter_match = re.match(r'^#\s*第(\d+)章', line)
        if chapter_match:
            current_chapter = chapter_match.group(1)

        # 检测假设提及
        for h in hypotheses:
            if h in line:
                if h not in chapters:
                    chapters[h] = set()
                chapters[h].add(current_chapter)

    # 分析闭环完整性
    issues = []
    expected = {
        "H1-1": ["4", "5", "9"],
        "H1-2": ["4", "5", "9"],
        "H2": ["4", "6", "9"],
        "H3-1": ["4", "7", "9"],
        "H3-2": ["4", "7", "9"],
    }

    for h, expected_chapters in expected.items():
        found = chapters.get(h, set())
        for ec in expected_chapters:
            if ec not in found:
                issues.append({
                    "priority": "P2",
                    "type": "假设闭环_缺失",
                    "line": 0,
                    "content": f"{h}在第{ec}章缺少提及",
                    "matches": [h]
                })

    return issues

def check_data_consistency(content):
    """检查关键数据一致性"""
    issues = []

    # 检查语料数量表述
    corpus_mentions = re.findall(r'(\d[,\d]*)\s*(?:例|条)', content)
    unique_counts = set(corpus_mentions)

    # 允许的数值
    allowed = {"6000", "6,000", "5989", "5,989"}
    unexpected = unique_counts - allowed

    for val in unexpected:
        try:
            if int(val.replace(",", "")) > 1000:  # 只关注大数
                issues.append({
                    "priority": "P2",
                    "type": "数据一致性_语料数量",
                    "line": 0,
                    "content": f"发现意外的语料数量表述：{val}",
                    "matches": [val]
                })
        except ValueError:
            pass

    return issues

def check_term_consistency(content):
    """检查12类构式命名一致性"""
    issues = []

    # 提取T1-T12格式的构式命名
    pattern = r'T(\d+)[（(]([^）)]+)[）)]'
    mentions = re.findall(pattern, content)

    # 按T编号分组
    type_variants = defaultdict(set)
    for t_num, desc in mentions:
        type_variants[f"T{t_num}"].add(desc)

    # 检查命名不一致
    inconsistent_types = []
    for t_type, variants in type_variants.items():
        if len(variants) > 1:
            inconsistent_types.append(f"{t_type}有{len(variants)}种写法")
            issues.append({
                "priority": "P2",
                "type": "术语一致性_T类型命名",
                "line": 0,
                "content": f"{t_type}命名不一致：{', '.join(list(variants)[:3])}",
                "matches": list(variants)
            })

    # 检查是否覆盖12类
    found_types = set(type_variants.keys())
    expected_types = {f"T{i}" for i in range(1, 13)}
    missing_types = expected_types - found_types

    if missing_types:
        issues.append({
            "priority": "P3",
            "type": "术语一致性_T类型缺失",
            "line": 0,
            "content": f"未发现以下类型的命名：{', '.join(sorted(missing_types))}",
            "matches": list(missing_types)
        })

    # 检查括号一致性（中英文混用）
    cn_brackets = len(re.findall(r'T\d+（', content))
    en_brackets = len(re.findall(r'T\d+\(', content))
    if cn_brackets > 0 and en_brackets > 0:
        issues.append({
            "priority": "P3",
            "type": "格式一致性_括号混用",
            "line": 0,
            "content": f"T类型使用中英文括号混用（中文{cn_brackets}次，英文{en_brackets}次）",
            "matches": [f"中文{cn_brackets}", f"英文{en_brackets}"]
        })

    return issues

def check_paragraph_length(content):
    """检查段落长度（优化L2：添加过短段落检查）"""
    issues = []

    # 按空行分割段落
    paragraphs = re.split(r'\n\s*\n', content)

    for i, para in enumerate(paragraphs, 1):
        # 跳过标题行、代码块、表格等
        if para.strip().startswith('#') or para.strip().startswith('|') or para.strip().startswith('```'):
            continue
        # 跳过空段落
        if not para.strip():
            continue

        # 计算中文字符数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', para))

        # 超过400字需要拆分
        if chinese_chars > 400:
            preview = para.strip()[:50].replace('\n', ' ')
            issues.append({
                "priority": "P4",
                "type": "段落过长",
                "line": 0,
                "content": f"段落{chinese_chars}字（超400字应拆分）：{preview}...",
                "matches": [str(chinese_chars)]
            })
        # 过短段落（小于50字但不是标题或列表项）
        elif chinese_chars > 0 and chinese_chars < 50 and not re.match(r'^[\-\*\d]', para.strip()):
            # 排除语例行（包含例（N）格式）
            if not re.search(r'例（\d+）', para):
                preview = para.strip()[:30].replace('\n', ' ')
                issues.append({
                    "priority": "P4",
                    "type": "段落过短",
                    "line": 0,
                    "content": f"段落仅{chinese_chars}字（可能需合并）：{preview}",
                    "matches": [str(chinese_chars)]
                })

    return issues

def generate_report(issues):
    """生成检查报告"""
    # 按优先级分组
    by_priority = defaultdict(list)
    for issue in issues:
        by_priority[issue["priority"]].append(issue)

    report = []
    report.append("# 论文质量检查报告\n")
    report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"检查文件：{THESIS_PATH.name}\n")
    report.append(f"问题总数：{len(issues)}\n")
    report.append("\n**修复版本**：v2 (2025-12-18) - 修复正则跨括号bug，优化P1规则\n")
    report.append("---\n")

    priority_names = {
        "P1": "致命问题",
        "P2": "严重问题",
        "P3": "中等问题",
        "P4": "轻微问题"
    }

    for p in ["P1", "P2", "P3", "P4"]:
        p_issues = by_priority.get(p, [])
        report.append(f"\n## {p} {priority_names[p]}（{len(p_issues)}项）\n")

        if not p_issues:
            report.append("无\n")
            continue

        report.append("| 序号 | 类型 | 行号 | 内容摘要 |\n")
        report.append("|:-----|:-----|:----:|:---------|\n")

        for i, issue in enumerate(p_issues, 1):
            line = issue["line"] if issue["line"] > 0 else "-"
            content = issue["content"][:50] + "..." if len(issue["content"]) > 50 else issue["content"]
            # 转义管道符
            content = content.replace("|", "\\|")
            report.append(f"| {i} | {issue['type']} | {line} | {content} |\n")

    report.append("\n---\n")
    report.append("\n## 修复优先级建议\n")
    report.append("1. 首先处理P1致命问题（数据错误）\n")
    report.append("2. 其次处理P2严重问题（统计符号、引用格式、假设闭环、术语错误）\n")
    report.append("3. 逐步清理P3中等问题（AI痕迹、口语化、术语不一致）\n")
    report.append("4. 定稿前处理P4轻微问题（格式统一、段落长度）\n")
    report.append("\n---\n")
    report.append(f"\n*报告生成脚本：论文质量检查.py*\n")
    report.append(f"*配套Skill：thesis-checking*\n")

    return "".join(report)

def main():
    """主函数"""
    print("=" * 60)
    print("论文质量检查脚本（v2 修复版 2025-12-18）")
    print("=" * 60)

    # 加载论文
    content = load_thesis()
    if content is None:
        return

    print(f"已加载论文，共 {len(content)} 字符\n")

    # 执行各类检查
    all_issues = []

    print("执行P1致命问题检查...")
    all_issues.extend(scan_patterns(content, P1_PATTERNS, "P1"))

    print("执行P2严重问题检查...")
    all_issues.extend(scan_patterns(content, P2_PATTERNS, "P2"))

    print("执行P3中等问题检查...")
    all_issues.extend(scan_patterns(content, P3_PATTERNS, "P3"))

    print("执行P4轻微问题检查...")
    all_issues.extend(scan_patterns(content, P4_PATTERNS, "P4"))

    print("执行图表对齐检查...")
    all_issues.extend(check_figure_table_alignment(content))

    print("执行假设闭环检查...")
    all_issues.extend(check_hypothesis_mentions(content))

    print("执行数据一致性检查...")
    all_issues.extend(check_data_consistency(content))

    print("执行术语一致性检查...")
    all_issues.extend(check_term_consistency(content))

    print("执行段落长度检查...")
    all_issues.extend(check_paragraph_length(content))

    # 生成报告
    print("\n生成检查报告...")
    report = generate_report(all_issues)

    # 输出到控制台
    print("\n" + report)

    # 保存报告
    report_path = BASE_PATH / "统计分析/结果_输出/论文质量检查报告.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存至：{report_path}")

    # 统计摘要
    print("\n" + "=" * 60)
    print("检查完成摘要")
    print("=" * 60)
    by_p = defaultdict(int)
    for issue in all_issues:
        by_p[issue["priority"]] += 1

    for p in ["P1", "P2", "P3", "P4"]:
        print(f"  {p}: {by_p[p]} 项")
    print(f"  总计: {len(all_issues)} 项")

if __name__ == "__main__":
    main()
