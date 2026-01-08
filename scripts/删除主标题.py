#!/usr/bin/env python3
"""
批量注释掉统计脚本中的 suptitle 调用（删除图表主标题）
保留子图标题（ax.set_title）不变
"""

import os
import re

# 脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 需要修改的文件及其 suptitle 所在行号
# 格式: (文件名, [(起始行, 结束行), ...])  行号是1-indexed
FILES_TO_MODIFY = [
    ("Q1_03_GMM聚类.py", [(472, 473), (700, 701)]),
    ("Q1_05_原型梯度.py", [(328, 329)]),
    ("Q2_01_网络构建.py", [(602, 602)]),
    ("Q2_02_小世界检验.py", [(400, 401)]),
    ("Q2_03_链接分析.py", [(291, 291)]),
    ("Q2_04_中心性分析.py", [(292, 293)]),
    ("Q2_05_模块检测.py", [(333, 334)]),
    ("Q2_06_度分布.py", [(279, 279), (356, 357)]),
    ("Q2_07_网络可视化.py", [(298, 299), (441, 442)]),
    ("Q3_01_描述统计.py", [(392, 393)]),
    ("Q3_04_多组比较.py", [(1080, 1081)]),
    ("Q3_06_调节效应.py", [(592, 593)]),
]


def comment_out_lines(filepath, line_ranges):
    """注释掉指定行范围"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 将行范围转换为0-indexed的行号集合
    lines_to_comment = set()
    for start, end in line_ranges:
        for line_num in range(start, end + 1):
            lines_to_comment.add(line_num - 1)  # 转换为0-indexed

    # 注释掉指定行
    modified = False
    for i in lines_to_comment:
        if i < len(lines):
            line = lines[i]
            # 跳过已经注释的行
            if not line.strip().startswith('#'):
                # 保持缩进，添加注释
                indent = len(line) - len(line.lstrip())
                lines[i] = line[:indent] + '# ' + line[indent:]
                modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False


def main():
    print("=" * 60)
    print("批量删除图表主标题（注释掉 suptitle 调用）")
    print("=" * 60)

    modified_count = 0

    for filename, line_ranges in FILES_TO_MODIFY:
        filepath = os.path.join(SCRIPT_DIR, filename)

        if not os.path.exists(filepath):
            print(f"[警告] 文件不存在: {filename}")
            continue

        if comment_out_lines(filepath, line_ranges):
            print(f"[已修改] {filename} - 注释了 {len(line_ranges)} 处 suptitle")
            modified_count += 1
        else:
            print(f"[跳过] {filename} - 已是注释状态或无需修改")

    print("=" * 60)
    print(f"完成！共修改 {modified_count} 个文件")
    print("请运行 '一键运行全部脚本.py' 重新生成图表")
    print("=" * 60)


if __name__ == "__main__":
    main()
