# -*- coding: utf-8 -*-
"""
图表编号级联修改脚本
====================
1. 在7.2节末尾（PLS-MGA讨论后）插入新图30（系词功能比较图）
2. 原图30-34 → 图31-35（+1级联）
3. 表92→表90, 表93a→表91（新表重编号）
4. 原表90-105 → 表92-107（+2级联）
"""
import re
import shutil

file_path = r"/home/tomja/projects/博士毕业论文/大论文/论文撰写/正文/基于语料库的汉语系表隐喻构式网络认知机制研究.md"

# 备份
shutil.copy(file_path, file_path + '.bak_renumber')

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"文件共 {len(lines)} 行")

# ============================================================
# STEP 1: 插入新图30（系词功能路径系数比较图）
# ============================================================
# 找到"这一分化模式的认知语言学含义在于"段落后面
insert_after_text = "在参照点锚定到跨域映射的传递中呈现相对较低的路径强度。"
insert_idx = None
for i, line in enumerate(lines):
    if insert_after_text in line:
        insert_idx = i + 1  # 插入在这行后面
        break

if insert_idx is None:
    print("ERROR: 找不到插入位置")
    exit(1)

new_fig_lines = [
    "\n",
    "图[30](#fig:fig30)以点图形式直观呈现了全样本与3类系词功能在两条路径上的系数差异。\n",
    "\n",
    "![图30 各系词功能路径系数比较图（来源：CFMC_5989语料库）](../统计分析/结果_输出/Figures/图31_各系词功能路径系数比较图.png){#fig:fig30}\n",
    "\n",
    "注：灰色菱形为全样本模型A路径系数，彩色标记为各系词功能组缩减模型路径系数。\n",
    "\n",
]

for j, new_line in enumerate(new_fig_lines):
    lines.insert(insert_idx + j, new_line)

print(f"STEP 1: 在第{insert_idx}行后插入新图30（{len(new_fig_lines)}行）")

# ============================================================
# STEP 2: 图编号 +1 级联（原图30→31, 31→32, 32→33, 33→34, 34→35）
# 从大到小替换避免冲突
# ============================================================
# 注意：新插入的图30引用不应被替换，所以先标记它
# 策略：先替换34→35, 33→34, 32→33, 31→32, 30→31
# 但新插入的行已经写的是"图30"和"fig:fig30"，不需要改

# 需要跳过新插入的行（insert_idx到insert_idx+len(new_fig_lines)-1）
new_lines_range = set(range(insert_idx, insert_idx + len(new_fig_lines)))

fig_changes = 0
for old_num in range(34, 29, -1):  # 34, 33, 32, 31, 30
    new_num = old_num + 1
    for i in range(len(lines)):
        if i in new_lines_range:
            continue  # 跳过新插入的行
        
        original = lines[i]
        
        # 图片定义行: ![图N ...]{#fig:figN}
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
        
        # 行内引用: 图[N](#fig:figN)
        lines[i] = re.sub(
            rf'图\[{old_num}\]\(#fig:fig{old_num}\)',
            f'图[{new_num}](#fig:fig{new_num})',
            lines[i]
        )
        
        # 纯文本引用: 图N（不在方括号内、不在![]()内）
        # 匹配 "图30" 但不匹配 "图[30" 或 "[图30" 或 "!图30"
        # 只替换独立的"图N"引用（后面跟非数字字符）
        lines[i] = re.sub(
            rf'(?<!\[)(?<!!)图{old_num}(?!\d)(?!\])',
            f'图{new_num}',
            lines[i]
        )
        
        if lines[i] != original:
            fig_changes += 1

print(f"STEP 2: 图编号+1级联完成，{fig_changes}处修改")

# ============================================================
# STEP 3: 修复新PLS-MGA表编号
# 表92→表90, 表93a→表91
# ============================================================
tbl_fix_changes = 0
for i in range(len(lines)):
    original = lines[i]
    
    # 表93a → 表91（先处理93a，因为93和93a都包含93）
    lines[i] = lines[i].replace('表93a', '表91')
    lines[i] = lines[i].replace('{#tbl:tbl93a}', '{#tbl:tbl91}')
    lines[i] = lines[i].replace('#tbl:tbl93a', '#tbl:tbl91')
    
    if lines[i] != original:
        tbl_fix_changes += 1

# 表92→表90（但只改7.2节的PLS-MGA表92，不改后面的原表92）
# 关键：7.2节的表92在L3951左右（插入行之前），原表92在L4185左右
# 用内容特征区分：PLS-MGA表92的内容是"PLS-MGA各组拟合与路径系数"
for i in range(len(lines)):
    if 'PLS-MGA各组拟合与路径系数' in lines[i]:
        original = lines[i]
        lines[i] = lines[i].replace('表92', '表90')
        lines[i] = lines[i].replace('{#tbl:tbl92}', '{#tbl:tbl90}')
        if lines[i] != original:
            tbl_fix_changes += 1
            print(f"  表92→表90 (PLS-MGA表): 行{i+1}")
    # 也要修复引用这个表的行内引用
    if '表[92](#tbl:tbl92)' in lines[i] and ('PLS-MGA' in lines[i] or '3组系词功能' in lines[i] or '各组路径系数' in lines[i]):
        original = lines[i]
        lines[i] = lines[i].replace('表[92](#tbl:tbl92)', '表[90](#tbl:tbl90)')
        if lines[i] != original:
            tbl_fix_changes += 1
            print(f"  表[92]→表[90] (引用): 行{i+1}")

print(f"STEP 3: PLS-MGA表编号修复，{tbl_fix_changes}处修改")

# ============================================================
# STEP 4: 表编号 +2 级联（原表90-105 → 表92-107）
# 从大到小替换
# ============================================================
# 注意：此时表90(PLS-MGA)和表91(置换检验)已经是新编号了
# 需要替换的是原来的表90-105（现在还是表90-105的那些）
# 但表90已被改为其他值...
# 
# 实际上，当前文件中：
# - 原"表92"(PLS-MGA) → 已改为"表90"
# - 原"表93a"(置换检验) → 已改为"表91"
# - 原"表90"(五个典型语例) → 需要改为"表92"
# - 原"表91"(9类构式) → 需要改为"表93"
# - 原"表92"(原型距离) → 需要改为"表94"（但已有"表92"被改了）
# 
# 问题：原文有两个"表92"，PLS-MGA那个已被改为"表90"
# 剩下的"表92"就是原"原型距离与阶段2指标"那个
#
# 策略：从大到小，105→107, 104→106, ... 90→92
# 但要排除已经被改过的行（表90=PLS-MGA, 表91=置换检验）

tbl_cascade_changes = 0
# 标记已经是新表90/91的行，避免被二次修改
skip_tbl90_line = None
skip_tbl91_line = None
for i in range(len(lines)):
    if '{#tbl:tbl90}' in lines[i]:
        skip_tbl90_line = i
    if '{#tbl:tbl91}' in lines[i]:
        skip_tbl91_line = i

print(f"  新表90定义行: {skip_tbl90_line+1 if skip_tbl90_line else 'N/A'}")
print(f"  新表91定义行: {skip_tbl91_line+1 if skip_tbl91_line else 'N/A'}")

# 收集需要跳过的行（新表90和表91的相关行，包括引用行）
skip_lines_for_cascade = set()
if skip_tbl90_line is not None:
    # 跳过表90定义及其前后几行
    for delta in range(-5, 6):
        idx = skip_tbl90_line + delta
        if 0 <= idx < len(lines):
            skip_lines_for_cascade.add(idx)
if skip_tbl91_line is not None:
    for delta in range(-5, 6):
        idx = skip_tbl91_line + delta
        if 0 <= idx < len(lines):
            skip_lines_for_cascade.add(idx)
# 也跳过新插入的图行
skip_lines_for_cascade.update(new_lines_range)

# 引用表90和表91的行也要标记跳过（已被修改过的行）
for i in range(len(lines)):
    if '表[90](#tbl:tbl90)' in lines[i] and ('PLS-MGA' in lines[i] or '3组系词功能' in lines[i]):
        skip_lines_for_cascade.add(i)

for old_num in range(105, 89, -1):  # 105, 104, ..., 90
    new_num = old_num + 2
    for i in range(len(lines)):
        if i in skip_lines_for_cascade:
            continue
        
        original = lines[i]
        
        # 表头定义: : 表N 内容 {#tbl:tblN}
        lines[i] = re.sub(
            rf'(: 表){old_num}(\s)',
            rf'\g<1>{new_num}\2',
            lines[i]
        )
        lines[i] = re.sub(
            rf'\{{#tbl:tbl{old_num}\}}',
            f'{{#tbl:tbl{new_num}}}',
            lines[i]
        )
        
        # 行内引用: 表[N](#tbl:tblN) 或 表N
        lines[i] = re.sub(
            rf'表\[{old_num}\]\(#tbl:tbl{old_num}\)',
            f'表[{new_num}](#tbl:tbl{new_num})',
            lines[i]
        )
        
        # 纯文本引用: 表N（后面跟非数字字符）
        lines[i] = re.sub(
            rf'(?<!\[)表{old_num}(?!\d)(?!\])',
            f'表{new_num}',
            lines[i]
        )
        
        if lines[i] != original:
            tbl_cascade_changes += 1

print(f"STEP 4: 表编号+2级联完成，{tbl_cascade_changes}处修改")

# ============================================================
# 保存
# ============================================================
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\n总计修改：图+1={fig_changes}, 表修复={tbl_fix_changes}, 表+2={tbl_cascade_changes}")
print("备份保存于: " + file_path + '.bak_renumber')
