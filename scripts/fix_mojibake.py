#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 mojibake（乱码）问题。

问题原因：UTF-8 内容被错误地当作 Latin-1 读取，然后保存为 UTF-8。
修复方法：反向操作 - 读取当前 UTF-8，编码为 Latin-1，解码为 UTF-8。
"""

import sys
import io
from pathlib import Path

# 设置 stdout 为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def fix_mojibake(text: str) -> str:
    """修复 UTF-8 -> Latin-1 -> UTF-8 导致的乱码。"""
    try:
        # 当前文本是 UTF-8 被当作 Latin-1 保存后的结果
        # 我们需要：编码为 Latin-1（还原原始字节）-> 解码为 UTF-8
        fixed = text.encode("latin-1").decode("utf-8")
        return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        # 如果转换失败，说明不是这种类型的乱码
        return None


def check_and_fix_file(file_path: Path, dry_run: bool = False) -> bool:
    """检查并修复单个文件。

    Returns:
        True 如果文件需要修复或已修复
        False 如果文件正常
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [X] 无法读取 {file_path.name}: {e}")
        return False

    # 检测常见的乱码模式
    mojibake_patterns = ["ä", "è", "é", "ç", "å", "†", "œ", "¼", "»", "ï"]
    has_mojibake = any(pattern in content for pattern in mojibake_patterns)

    if not has_mojibake:
        return False

    # 尝试修复
    fixed_content = fix_mojibake(content)
    if fixed_content is None:
        print(f"  [?] {file_path.name}: 检测到乱码但无法自动修复")
        return True

    if dry_run:
        print(f"  [CHECK] {file_path.name}: 需要修复")
    else:
        file_path.write_text(fixed_content, encoding="utf-8", newline="\n")
        print(f"  [OK] {file_path.name}: 已修复")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="修复 mojibake 乱码问题")
    parser.add_argument("--dry-run", action="store_true", help="只检测不修改")
    parser.add_argument("paths", nargs="+", type=Path, help="要检查的文件或目录")
    args = parser.parse_args()

    files_to_check = []
    for path in args.paths:
        if path.is_file():
            files_to_check.append(path)
        elif path.is_dir():
            files_to_check.extend(path.rglob("*.md"))

    print(f"检查 {len(files_to_check)} 个文件...")
    print()

    fixed_count = 0
    for f in sorted(files_to_check):
        if check_and_fix_file(f, dry_run=args.dry_run):
            fixed_count += 1

    print()
    if args.dry_run:
        print(f"检测结果: {fixed_count} 个文件需要修复")
    else:
        print(f"修复完成: {fixed_count} 个文件已修复")


if __name__ == "__main__":
    main()
