#!/usr/bin/env python3
# compare_dirs.py
"""
用法:
    python compare_dirs.py DIR_A DIR_B [-e .png .pdf ...]
说明:
    - 递归遍历 DIR_A；若在 DIR_B 中找到同样的相对路径文件，则逐行比较。
    - 非文本文件可用 -e 忽略其后缀（如二进制、图片等）。
"""
# to support checking the difference between two directories
import argparse
import os
from pathlib import Path
from itertools import zip_longest

def gather_files(root: Path):
    """返回 {相对路径: 绝对路径}"""
    mapping = {}
    for path in root.rglob('*'):
        if path.is_file():
            mapping[path.relative_to(root)] = path
    return mapping

def compare_text_files(path_a: Path, path_b: Path, rel_path: Path):
    """逐行比较两文件，输出差异"""
    try:
        with path_a.open('r', encoding='utf-8') as fa, path_b.open('r', encoding='utf-8') as fb:
            for lineno, (line_a, line_b) in enumerate(zip_longest(fa, fb, fillvalue=''), start=1):
                if line_a != line_b:
                    # 去掉换行符，保持输出简洁
                    clean_a = line_a.rstrip('\n')
                    clean_b = line_b.rstrip('\n')
                    print(f"{rel_path} : 第 {lineno} 行 | {clean_a} || {clean_b}")
    except UnicodeDecodeError:
        # 如果不是纯文本，给个提示
        print(f"[跳过] 可能为二进制文件: {rel_path}")

def main():
    parser = argparse.ArgumentParser(description="对比两个目录中同名文件内容是否一致")
    parser.add_argument("dir1", type=Path, help="目录 1（基准）")
    parser.add_argument("dir2", type=Path, help="目录 2（对比）")
    parser.add_argument("-e", "--exclude-ext", nargs='*', default=[],
                        help="排除这些扩展名的文件（如 .png .exe）")
    args = parser.parse_args()

    dir1_map = gather_files(args.dir1)
    dir2_map = gather_files(args.dir2)

    common_files = set(dir1_map.keys()) & set(dir2_map.keys())
    if not common_files:
        print("两个目录没有同名文件。")
        return

    for rel_path in sorted(common_files):
        if rel_path.suffix in args.exclude_ext:
            continue
        compare_text_files(dir1_map[rel_path], dir2_map[rel_path], rel_path)

if __name__ == "__main__":
    main()
