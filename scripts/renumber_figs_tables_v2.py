# -*- coding: utf-8 -*-
"""
图表编号全面修正脚本 v2
========================
策略：逐表逐图基于内容定位，避免编号冲突

当前问题：
- PLS-MGA表使用了重复编号（表92, 表93a）
- 行内引用和定义行使用不同的编号系统（引用偏移+3）
- 需要统一为正确的连续编号

目标编号（表89之后的18张表）：
  表90: PLS-MGA各组拟合与路径系数
  表91: PLS-MGA置换检验结果
  表92: 五个典型语例的认知指标对比
  表93: 9类构式路径系数比较
  表94-107: 后续14张表
"""
import re
import shutil
import sys

file_path = r"/home/tomja/projects/博士毕业论文/大论文/论文撰写/正文/基于语料库的汉语系表隐喻构式网络认知机制研究.md"

# 备份
shutil.copy(file_path, file_path + '.bak_renumber_v2')

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"原始文件大小: {len(content)} 字符")

# ================================================================
# 核心数据：每张表的完整映射信息
# ================================================================
# 格式: (内容标记, 定义行旧anchor, 定义行旧显示名, 引用行旧anchor, 引用行旧显示名, 新编号)
# 注意：有些表的定义和引用使用不同的anchor

TABLE_MAP = [
    # --- PLS-MGA两张新表（定义与引用一致）---
    {
        'content': 'PLS-MGA各组拟合与路径系数',
        'def_anchor': 'tbl:tbl92',     # 定义行 {#tbl:tbl92}
        'def_display': '表92',          # 定义行显示名
        'ref_anchor': 'tbl:tbl92',     # 行内引用 (#tbl:tbl92)
        'ref_display': '表[92]',        # 行内引用显示名
        'new_num': 90,
    },
    {
        'content': 'PLS-MGA置换检验结果',
        'def_anchor': 'tbl:tbl93a',
        'def_display': '表93a',
        'ref_anchor': 'tbl:tbl93a',
        'ref_display': '表[93a]',
        'new_num': 91,
    },
    # --- 后续表（定义和引用使用不同编号）---
    {
        'content': '五个典型语例的认知指标对比',
        'def_anchor': 'tbl:tbl90',
        'def_display': '表90',
        'ref_anchor': 'tbl:tbl93',   # 引用偏移+3
        'ref_display': '表[93]',
        'new_num': 92,
    },
    {
        'content': '9类构式路径系数比较',
        'def_anchor': 'tbl:tbl91',
        'def_display': '表91',
        'ref_anchor': 'tbl:tbl94',
        'ref_display': '表[94]',
        'new_num': 93,
    },
    {
        'content': '原型距离与阶段2',
        'def_anchor': 'tbl:tbl92',    # 与PLS-MGA表anchor冲突！
        'def_display': '表92',
        'ref_anchor': 'tbl:tbl95',
        'ref_display': '表[95]',
        'new_num': 94,
    },
    {
        'content': '原型梯度组间η₂指标均值',
        'def_anchor': 'tbl:tbl93',
        'def_display': '表93',
        'ref_anchor': 'tbl:tbl96',
        'ref_display': '表[96]',
        'new_num': 95,
    },
    {
        'content': '原型距离与阶段3',
        'def_anchor': 'tbl:tbl94',
        'def_display': '表94',
        'ref_anchor': 'tbl:tbl97',
        'ref_display': '表[97]',
        'new_num': 96,
    },
    {
        'content': '原型梯度组间系统性均值',
        'def_anchor': 'tbl:tbl95',
        'def_display': '表95',
        'ref_anchor': 'tbl:tbl98',
        'ref_display': '表[98]',
        'new_num': 97,
    },
    {
        'content': 'H3-2假设判断标准与实测值对照',
        'def_anchor': 'tbl:tbl96',
        'def_display': '表96',
        'ref_anchor': 'tbl:tbl99',
        'ref_display': '表[99]',
        'new_num': 98,
    },
    {
        'content': '汉语认知风格的调节效应检验结果',
        'def_anchor': 'tbl:tbl97',
        'def_display': '表97',
        'ref_anchor': 'tbl:tbl100',
        'ref_display': '表[100]',
        'new_num': 99,
    },
    {
        'content': '零系词构式与显性系词构式的四阶段加工比较',
        'def_anchor': 'tbl:tbl98',
        'def_display': '表98',
        'ref_anchor': 'tbl:tbl101',
        'ref_display': '表[101]',
        'new_num': 100,
    },
    {
        'content': 'Q3假设验证结果汇总',
        'def_anchor': 'tbl:tbl99',
        'def_display': '表99',
        'ref_anchor': 'tbl:tbl102',
        'ref_display': '表[102]',
        'new_num': 101,
    },
    {
        'content': 'Q1-Q2-Q3假设验证结果汇总',
        'def_anchor': 'tbl:tbl100',
        'def_display': '表100',
        'ref_anchor': 'tbl:tbl103',
        'ref_display': '表[103]',
        'new_num': 102,
    },
    {
        'content': 'Sullivan七类理论缺陷与本研究回应对照',
        'def_anchor': 'tbl:tbl101',
        'def_display': '表101',
        'ref_anchor': 'tbl:tbl104',
        'ref_display': '表[104]',
        'new_num': 103,
    },
    {
        'content': '汉英系表隐喻构式类型学特征对比',
        'def_anchor': 'tbl:tbl102',
        'def_display': '表102',
        'ref_anchor': 'tbl:tbl105',
        'ref_display': '表[105]',
        'new_num': 104,
    },
    {
        'content': '四阶段机制与CIT四空间的初步对应',
        'def_anchor': 'tbl:tbl103',
        'def_display': '表103',
        'ref_anchor': None,  # 无行内引用
        'ref_display': None,
        'new_num': 105,
    },
    {
        'content': '研究贡献一览',
        'def_anchor': 'tbl:tbl104',
        'def_display': '表104',
        'ref_anchor': None,
        'ref_display': None,
        'new_num': 106,
    },
    {
        'content': '局限与展望对应表',
        'def_anchor': 'tbl:tbl105',
        'def_display': '表105',
        'ref_anchor': None,
        'ref_display': None,
        'new_num': 107,
    },
]

# ================================================================
# 阶段1: 逐行处理表格编号
# ================================================================
lines = content.split('\n')
print(f"文件共 {len(lines)} 行\n")

# 策略：逐行扫描，基于内容匹配确定每行属于哪张表，然后替换
# 第一步：为每张表找到定义行位置
print("=== 步骤1: 定位所有表格定义行 ===")
for tbl in TABLE_MAP:
    tbl['def_line'] = None
    tbl['ref_lines'] = []
    for i, line in enumerate(lines):
        if tbl['content'] in line and '{#' + tbl['def_anchor'] + '}' in line:
            tbl['def_line'] = i
            print(f"  表{tbl['new_num']}: L{i+1} ← {tbl['content'][:30]}... [{tbl['def_anchor']}]")
            break
    if tbl['def_line'] is None:
        print(f"  WARNING: 找不到表{tbl['new_num']}的定义行! (content={tbl['content'][:30]}, anchor={tbl['def_anchor']})")

# 第二步：为每张表找到行内引用位置
print("\n=== 步骤2: 定位所有表格引用行 ===")
for tbl in TABLE_MAP:
    if tbl['ref_anchor'] is None:
        continue
    ref_pattern = '(#' + tbl['ref_anchor'] + ')'
    for i, line in enumerate(lines):
        if ref_pattern in line:
            tbl['ref_lines'].append(i)
    if tbl['ref_lines']:
        print(f"  表{tbl['new_num']}: 引用在 {['L'+str(l+1) for l in tbl['ref_lines']]} [{tbl['ref_anchor']}]")
    else:
        print(f"  表{tbl['new_num']}: 无引用行 [{tbl['ref_anchor']}]")

# 第三步：两阶段替换
# 阶段3a: 所有旧anchor → 临时anchor
print("\n=== 步骤3a: 旧anchor → 临时anchor ===")
changes_3a = 0

for tbl in TABLE_MAP:
    new_num = tbl['new_num']
    temp_def_anchor = f'tbl:__TEMP_DEF_{new_num}__'
    temp_ref_anchor = f'tbl:__TEMP_REF_{new_num}__'
    temp_display = f'__DISP_{new_num}__'

    # 替换定义行
    if tbl['def_line'] is not None:
        i = tbl['def_line']
        old_anchor_str = '{#' + tbl['def_anchor'] + '}'
        new_anchor_str = '{#' + temp_def_anchor + '}'
        old_display_str = ': ' + tbl['def_display'] + ' '
        new_display_str = ': ' + temp_display + ' '

        if old_anchor_str in lines[i]:
            lines[i] = lines[i].replace(old_anchor_str, new_anchor_str, 1)
            lines[i] = lines[i].replace(old_display_str, new_display_str, 1)
            changes_3a += 1

    # 替换引用行
    if tbl['ref_anchor'] is not None:
        old_ref_str = '(#' + tbl['ref_anchor'] + ')'
        new_ref_str = '(#' + temp_ref_anchor + ')'

        for i in tbl['ref_lines']:
            if old_ref_str in lines[i]:
                # 替换引用anchor
                lines[i] = lines[i].replace(old_ref_str, new_ref_str)
                # 替换引用显示名
                if tbl['ref_display'] is not None:
                    # 表[N] → 临时显示
                    old_disp = tbl['ref_display']
                    lines[i] = lines[i].replace(old_disp + new_ref_str, temp_display + new_ref_str)
                changes_3a += 1

print(f"  完成: {changes_3a}处替换")

# 阶段3b: 临时anchor → 最终anchor
print("\n=== 步骤3b: 临时anchor → 最终编号 ===")
content = '\n'.join(lines)

for tbl in TABLE_MAP:
    new_num = tbl['new_num']
    final_anchor = f'tbl:tbl{new_num}'
    final_display = f'表{new_num}'

    # 定义行临时anchor → 最终
    temp_def = f'tbl:__TEMP_DEF_{new_num}__'
    content = content.replace('{#' + temp_def + '}', '{#' + final_anchor + '}')

    # 引用行临时anchor → 最终
    temp_ref = f'tbl:__TEMP_REF_{new_num}__'
    content = content.replace('(#' + temp_ref + ')', '(#' + final_anchor + ')')

    # 显示名临时 → 最终
    temp_disp = f'__DISP_{new_num}__'
    # 在定义行: ": __DISP_N__ " → ": 表N "
    content = content.replace(': ' + temp_disp + ' ', ': ' + final_display + ' ')
    # 在引用行: "__DISP_N__(#" → "表[N](#"
    content = content.replace(temp_disp + '(#' + final_anchor + ')', f'表[{new_num}](#' + final_anchor + ')')

lines = content.split('\n')
print(f"  完成")

# ================================================================
# 阶段2: 修复目录区表格引用
# ================================================================
print("\n=== 步骤4: 修复目录区 ===")
toc_fixes = 0

# 目录区表格引用格式: [[@tbl:tblN] 表题 ...]
# 需要基于内容匹配修正anchor
toc_content_to_anchor = {
    '五个典型语例': 'tbl92',
    '9类构式路径系数': 'tbl93',
    '原型距离与阶段2': 'tbl94',
    '原型梯度组间η₂': 'tbl95',
    '原型距离与阶段3': 'tbl96',
    '原型梯度组间系统性': 'tbl97',
    'H3-2假设判断标准': 'tbl98',
    '调节效应检验': 'tbl99',
    '零系词构式与显性系词': 'tbl100',
    'Q3假设验证': 'tbl101',
    'Q1-Q2-Q3假设验证': 'tbl102',
    'Sullivan七类': 'tbl103',
    '汉英系表隐喻': 'tbl104',
    '四阶段机制与CIT': 'tbl105',
    '研究贡献': 'tbl106',
    '局限与展望': 'tbl107',
}

for i in range(min(900, len(lines))):
    if '@tbl:tbl' not in lines[i]:
        continue
    for content_key, correct_anchor in toc_content_to_anchor.items():
        if content_key in lines[i]:
            old_match = re.search(r'@tbl:tbl\w+', lines[i])
            if old_match and old_match.group() != f'@tbl:{correct_anchor}':
                lines[i] = lines[i].replace(old_match.group(), f'@tbl:{correct_anchor}')
                toc_fixes += 1
                print(f"  目录 L{i+1}: {old_match.group()} → @tbl:{correct_anchor}")
            break

# 在目录区添加 表90 和 表91 的条目
# 找到目录中表89的位置，在其后插入
for i in range(min(900, len(lines))):
    if '@tbl:tbl89' in lines[i]:
        # 在表89后插入表90和表91
        new_toc_90 = "[[@tbl:tbl90] PLS-MGA各组拟合与路径系数 [0](#_Toc_tbl90)](#_Toc_tbl90)"
        new_toc_91 = "[[@tbl:tbl91] PLS-MGA置换检验结果 [0](#_Toc_tbl91)](#_Toc_tbl91)"
        lines.insert(i + 1, "")
        lines.insert(i + 2, new_toc_91)
        lines.insert(i + 1, "")
        lines.insert(i + 2, new_toc_90)
        toc_fixes += 2
        print(f"  目录 L{i+2}: 新增 @tbl:tbl90")
        print(f"  目录 L{i+4}: 新增 @tbl:tbl91")
        break

print(f"  目录修复: {toc_fixes}处")

# ================================================================
# 阶段3: 图片编号修正
# ================================================================
print("\n=== 步骤5: 插入新图30 ===")

insert_marker = "在参照点锚定到跨域映射的传递中呈现相对较低的路径强度。"
insert_idx = None
for i, line in enumerate(lines):
    if insert_marker in line:
        insert_idx = i + 1
        break

if insert_idx is None:
    print("ERROR: 找不到图30插入位置!")
    sys.exit(1)

new_fig_lines = [
    "",
    "图[30](#fig:fig30)以点图形式直观呈现了全样本与3类系词功能在两条路径上的系数差异。",
    "",
    "![图30 各系词功能路径系数比较图（来源：CFMC_5989语料库）](../统计分析/结果_输出/Figures/图31_各系词功能路径系数比较图.png){#fig:fig30}",
    "",
    "注：灰色菱形为全样本模型A路径系数，彩色标记为各系词功能组缩减模型路径系数。",
    "",
]

for j, new_line in enumerate(new_fig_lines):
    lines.insert(insert_idx + j, new_line)

print(f"  在L{insert_idx+1}后插入新图30（{len(new_fig_lines)}行）")
new_fig_range = set(range(insert_idx, insert_idx + len(new_fig_lines)))

print("\n=== 步骤6: 图编号级联+1 (图30-34 → 图31-35) ===")
fig_changes = 0

for old_num in range(34, 29, -1):
    new_num = old_num + 1
    for i in range(len(lines)):
        if i in new_fig_range:
            continue

        original = lines[i]

        # 图片定义行
        lines[i] = re.sub(
            rf'!\[图{old_num}\s',
            f'![图{new_num} ',
            lines[i]
        )
        lines[i] = re.sub(
            rf'\{{#fig:fig{old_num}\}}',
            f'{{#fig:fig{new_num}}}',
            lines[i]
        )

        # 行内引用
        lines[i] = re.sub(
            rf'图\[{old_num}\]\(#fig:fig{old_num}\)',
            f'图[{new_num}](#fig:fig{new_num})',
            lines[i]
        )

        # 纯文本引用
        lines[i] = re.sub(
            rf'(?<!\[)(?<!!)图{old_num}(?!\d)(?!\])',
            f'图{new_num}',
            lines[i]
        )

        # 目录区 @fig:figN
        lines[i] = re.sub(
            rf'@fig:fig{old_num}\b',
            f'@fig:fig{new_num}',
            lines[i]
        )

        if lines[i] != original:
            fig_changes += 1

print(f"  图级联完成: {fig_changes}处修改")

# 在目录区新增图30条目
print("\n=== 步骤7: 目录区新增图30 ===")
for i in range(min(700, len(lines))):
    if '@fig:fig31' in lines[i] and '构式类型' in lines[i]:
        new_toc_fig = "[[@fig:fig30] 各系词功能路径系数比较图 [0](#_Toc_fig30)](#_Toc_fig30)"
        lines.insert(i, new_toc_fig)
        print(f"  在目录L{i+1}前插入图30条目")
        break

# ================================================================
# 保存
# ================================================================
content = '\n'.join(lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n=== 保存完成 ===")
print(f"文件行数: {len(lines)}")
print(f"备份: {file_path}.bak_renumber_v2")

# ================================================================
# 验证
# ================================================================
print("\n=== 验证 ===")

# 检查表90-107的定义行是否都存在且唯一
for num in range(90, 108):
    anchor = f'{{#tbl:tbl{num}}}'
    count = content.count(anchor)
    if count == 0:
        print(f"  ERROR: 表{num} 定义缺失!")
    elif count > 1:
        print(f"  WARNING: 表{num} 定义出现{count}次!")
    else:
        print(f"  OK: 表{num} ✓")

# 检查是否有残留的临时标记
if '__TEMP_' in content or '__DISP_' in content:
    print("\n  ERROR: 残留临时标记!")
    for i, line in enumerate(lines):
        if '__TEMP_' in line or '__DISP_' in line:
            print(f"    L{i+1}: {line[:80]}...")
else:
    print("\n  OK: 无残留临时标记")

# 检查图30-35定义
for num in range(30, 36):
    anchor = f'{{#fig:fig{num}}}'
    count = content.count(anchor)
    if count == 0:
        print(f"  ERROR: 图{num} 定义缺失!")
    elif count > 1:
        print(f"  WARNING: 图{num} 定义出现{count}次!")
    else:
        print(f"  OK: 图{num} ✓")
