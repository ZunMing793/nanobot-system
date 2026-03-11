#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 shared/ 目录下所有 .md 文件的乱码问题
"""
import os
import re
import sys
from pathlib import Path

# Windows 控制台 UTF-8 支持
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 常见乱码模式
GARBLED_PATTERNS = [
    r'æ',           # UTF-8 错误解码为 Latin-1
    r'å',           # UTF-8 错误解码为 Latin-1
    r'â',           # UTF-8 错误解码为 Latin-1
    r'Ã',           # UTF-8 错误解码为 Latin-1 (大写)
    r'锟斤拷',       # 经典 GBK/UTF-8 乱码
    r'烫烫烫',       # 未初始化内存显示
]

def check_for_garbled_text(text, filename):
    """检查文本中是否包含乱码"""
    issues = []
    lines = text.split('\n')

    for line_num, line in enumerate(lines, 1):
        # 跳过空行和只包含标点的行
        if not line.strip() or line.strip() in ['', '-', '*', '#']:
            continue

        # 检查每个乱码模式
        for pattern in GARBLED_PATTERNS:
            if re.search(pattern, line):
                issues.append({
                    'line_num': line_num,
                    'line_content': line.strip(),
                    'pattern': pattern
                })
                break  # 每行只记录第一个匹配的乱码模式

    return issues

def check_file(filepath):
    """检查单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        issues = check_for_garbled_text(content, filepath)
        if issues:
            print(f"\n[FILE] {filepath}")
            print(f"   Found {len(issues)} garbled text occurrences:")
            for issue in issues[:3]:  # 只显示前3处
                print(f"   Line {issue['line_num']}: {issue['line_content'][:80]}...")
            if len(issues) > 3:
                print(f"   ... and {len(issues) - 3} more")
            return True
        return False
    except UnicodeDecodeError:
        print(f"\n[ERROR] {filepath}")
        print(f"   Encoding error: Cannot read with UTF-8")
        return True
    except Exception as e:
        print(f"\n[WARN] {filepath}")
        print(f"   Read error: {e}")
        return True

def main():
    shared_dir = Path(__file__).parent.parent / 'shared'

    if not shared_dir.exists():
        print(f"[ERROR] Directory not found: {shared_dir}")
        return

    # 查找所有 .md 文件
    md_files = list(shared_dir.rglob('*.md'))

    print(f"[SCAN] Scanning directory: {shared_dir}")
    print(f"[INFO] Found {len(md_files)} .md files")
    print("=" * 70)

    garbled_count = 0
    checked_count = 0
    garbled_files = []

    for filepath in sorted(md_files):
        if check_file(filepath):
            garbled_count += 1
            garbled_files.append(filepath)
        checked_count += 1

        # 进度显示
        if checked_count % 50 == 0:
            print(f"\n... Checked {checked_count}/{len(md_files)} files ...")

    print("\n" + "=" * 70)
    print(f"[DONE] Scan complete!")
    print(f"   Checked: {checked_count} files")
    print(f"   Garbled: {garbled_count} files")

    if garbled_count == 0:
        print(f"\n[PASS] No garbled text issues found!")
    else:
        print(f"\n[WARN] Found {garbled_count} files with garbled text:")
        for f in garbled_files[:20]:
            print(f"   - {f}")
        if len(garbled_files) > 20:
            print(f"   ... and {len(garbled_files) - 20} more")

if __name__ == '__main__':
    main()
