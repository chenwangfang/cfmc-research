#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修正论文正文中第1-4章图片的alt属性
使alt属性与图片实际标题保持一致
"""

import re

# 论文正文路径
THESIS_PATH = "/home/tomja/projects/博士毕业论文/大论文/论文撰写/正文/基于语料库的汉语系表隐喻构式网络认知机制研究.md"

# image编号与图表标题的对应关系（基于第1-4章图目录）
# 格式：image编号 -> 正确的alt属性
IMAGE_ALT_MAPPING = {
    "image1.png": "研究路径图",           # 图1-1
    "image2.png": "论文整体结构",         # 图1-2
    "image3.png": "Sullivan理论的四大理论来源",  # 图2-1
    "image4.png": "本研究理论定位图",     # 图2-2
    "image5.png": "CFMC三层框架结构图",   # 图3-1（需确认）
    "image6.png": "四阶段认知编码机制流程图",  # 图3-2（需确认）
    "image7.png": "双维度分类空间示意图", # 图3-3（需确认）
    "image8.png": "研究问题、假设、方法与数据的对应关系",  # 图4-1（需确认）
    "image9.png": "研究程序流程图",       # 图4-2（需确认）
    "image10.png": "语料筛选流程图",      # 图4-3（需确认）
    "image11.png": "CFMC-33字段体系结构图",  # 图4-4（需确认）
}

def fix_alt_attributes(dry_run=True):
    """修正img标签的alt属性"""
    
    with open(THESIS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    for image_name, correct_alt in IMAGE_ALT_MAPPING.items():
        # 匹配该图片的img标签
        pattern = rf'({image_name}"[^>]*alt=")([^"]*)'
        matches = list(re.finditer(pattern, content))
        
        for match in matches:
            old_alt = match.group(2)
            if old_alt != correct_alt:
                changes.append({
                    'image': image_name,
                    'old_alt': old_alt,
                    'new_alt': correct_alt
                })
                # 执行替换
                content = content.replace(
                    match.group(0),
                    f'{match.group(1)}{correct_alt}'
                )
    
    # 输出变更报告
    print("=" * 60)
    print("图片alt属性修正报告")
    print("=" * 60)
    
    if changes:
        print(f"\n共发现 {len(changes)} 处需要修正：\n")
        for i, change in enumerate(changes, 1):
            print(f"{i}. {change['image']}")
            print(f"   旧值: {change['old_alt']}")
            print(f"   新值: {change['new_alt']}")
            print()
    else:
        print("\n所有alt属性已正确，无需修改。")
    
    # 保存或预览
    if dry_run:
        print("=" * 60)
        print("【预览模式】未实际修改文件")
        print("如需执行修改，请运行: python3 修正正文图片alt属性.py --execute")
    else:
        if content != original_content:
            with open(THESIS_PATH, 'w', encoding='utf-8') as f:
                f.write(content)
            print("=" * 60)
            print(f"✓ 已修改并保存到: {THESIS_PATH}")
        else:
            print("文件内容无变化，未保存。")

if __name__ == "__main__":
    import sys
    dry_run = "--execute" not in sys.argv
    fix_alt_attributes(dry_run=dry_run)
