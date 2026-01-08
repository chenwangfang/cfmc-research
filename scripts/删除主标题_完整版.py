#!/usr/bin/env python3
"""
批量删除统计脚本中的图表主标题（完整版）

删除规则：
- 删除 suptitle() 调用（整体主标题）
- 删除以 "图X-Y" 开头的 set_title() 和 plt.title() 调用
- 删除以 "图X-Y" 开头的 ax.text() 调用（第8-9章图脚本）
- 保留以 "（a）"、"（b）"、"(a)"、"(b)" 等开头的子图标题
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def comment_out_main_titles(filepath):
    """注释掉主标题相关行"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 跳过已注释的行
        if stripped.startswith('#'):
            i += 1
            continue

        # 检测需要注释的模式
        should_comment = False
        is_multiline = False

        # 模式1: suptitle
        if 'suptitle(' in line and not stripped.startswith('#'):
            should_comment = True
            if line.count('(') > line.count(')'):
                is_multiline = True

        # 模式2: set_title 或 plt.title 以 '图' 开头的标题
        title_pattern = r"(set_title|plt\.title)\s*\(\s*[rf]?['\"]图"
        if re.search(title_pattern, line) and not stripped.startswith('#'):
            should_comment = True
            if line.count('(') > line.count(')'):
                is_multiline = True

        # 模式3: ax.text 以 '图X-Y' 开头的标题（第8-9章图脚本）
        ax_text_pattern = r"ax\.text\s*\([^)]*['\"]图\d+-\d+"
        if re.search(ax_text_pattern, line) and not stripped.startswith('#'):
            should_comment = True
            if line.count('(') > line.count(')'):
                is_multiline = True

        if should_comment:
            # 注释当前行
            indent = len(line) - len(line.lstrip())
            lines[i] = line[:indent] + '# ' + line[indent:]
            modified = True

            # 如果是多行，继续注释后续行直到括号闭合
            if is_multiline:
                open_count = line.count('(') - line.count(')')
                j = i + 1
                while j < len(lines) and open_count > 0:
                    next_line = lines[j]
                    if not next_line.strip().startswith('#'):
                        indent = len(next_line) - len(next_line.lstrip())
                        lines[j] = next_line[:indent] + '# ' + next_line[indent:]
                    open_count += next_line.count('(') - next_line.count(')')
                    j += 1
                i = j - 1

        i += 1

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False


def main():
    print("=" * 70)
    print("删除图表主标题（完整版）")
    print("=" * 70)
    print("删除规则：")
    print("  - suptitle() 调用")
    print("  - 以 '图X-Y' 开头的 set_title() 和 plt.title()")
    print("  - 以 '图X-Y' 开头的 ax.text()（第8-9章图）")
    print("  - 保留子图标题（以 '（a）' 等开头）")
    print("=" * 70)

    # 获取所有需要处理的脚本
    all_scripts = []

    # Q*.py 脚本
    q_scripts = [f for f in os.listdir(SCRIPT_DIR)
                 if f.startswith('Q') and f.endswith('.py')]
    all_scripts.extend(q_scripts)

    # 图*.py 脚本（第8-9章）
    figure_scripts = [f for f in os.listdir(SCRIPT_DIR)
                      if f.startswith('图') and f.endswith('.py')]
    all_scripts.extend(figure_scripts)

    all_scripts.sort()

    modified_files = []

    for script in all_scripts:
        filepath = os.path.join(SCRIPT_DIR, script)
        if comment_out_main_titles(filepath):
            modified_files.append(script)
            print(f"[已修改] {script}")
        else:
            print(f"[无需修改] {script}")

    print("=" * 70)
    print(f"完成！共修改 {len(modified_files)} 个文件")
    if modified_files:
        print("已修改的文件：")
        for f in modified_files:
            print(f"  - {f}")
    print("=" * 70)
    print("请运行 'python3 一键运行全部脚本.py' 重新生成图表")


if __name__ == "__main__":
    main()
