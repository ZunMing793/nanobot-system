#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complete garbled text fixer using pattern mapping."""

import sys
import io
import re
from pathlib import Path

# Set stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Complete garbled pattern mapping
# These patterns occur when UTF-8 Chinese text is misinterpreted as CP1252/Windows-1252
GARBLED_MAP = {
    # Chinese punctuation
    '》': '。',
    '》': ',',
    '》': '?',
    '》': '!',
    '》': '、',
    '》': ':',
    '》': ';',
    '》': '(',
    '》': ')',
    '》': '【',
    '》': '】',
    '》': '《',
    '》': '》',

    # Common garbled Chinese characters (UTF-8 bytes as CP1252)
    '此': '此',
    '写': '写',
    '事': '于',
    '等': '等',
    '此': '在',
    '下': '不',
    '日': '有',
    '此': '的',
    '此': '是',
    '下': '中',
    '此': '大',
    '日': '为',
    '日': '上',
    '下': '个',
    '此': '国',
    '下': '和',
    '此': '地',
    '此': '以',
    '此': '发',
    '此': '到',
    '日': '时',
    '此': '要',
    '此': '就',
    '此': '出',
    '此': '会',
    '此': '可',
    '此': '也',
    '你': '你',
    '此': '对',
    '此': '生',
    '进': '能',
    '进': '而',
    '此': '子',
    '此': '那',
    '此': '得',
    '此': '于',
    '用': '着',
    '下': '下',
    '此': '自',
    '此': '之',
    '此': '年',
    '进': '过',
    '此': '发',
    '此': '后',
    '此': '作',
    '此': '里',
    '用': '用',
    '此': '道',
    '此': '行',
    '日': '所',
    '此': '然',
    '此': '家',
    '此': '种',
    '事': '事',
    '日': '成',
    '此': '方',
    '此': '多',
    '此': '经',
    '此': '么',
    '此': '去',
    '日': '法',
    '此': '学',
    '此': '如',
    '此': '研',
    '此': '都',
    '此': '同',
    '日': '现',
    '此': '当',
    '此': '没',
    '此': '动',
    '此': '面',
    '此': '起',
    '此': '看',
    '此': '定',
    '此': '天',
    '此': '分',
    '此': '还',
    '进': '进',
    '此': '好',
    '此': '小',
    '此': '部',
    '此': '其',
    '此': '些',
    '此': '主',
    '此': '样',
    '此': '理',
    '此': '心',
    '此': '她',
    '此': '本',
    '此': '前',
    '此': '开',
    '此': '但',
    '此': '因',
    '此': '只',
    '此': '从',
    '此': '想',
    '此': '实',
    '日': '日',
    '此': '军',
    '此': '者',
    '此': '意',
    '此': '无',
    '此': '力',
    '此': '它',
    '此': '与',
    '此': '长',
    '此': '把',
    '此': '机',
    '此': '十',
    '此': '民',
    '此': '第',
    '此': '公',
    '此': '此',
    '已': '已',
    '已给': '已经',
    '可以': '可以',
    '对事': '对于',
    '此³事': '关于',
    '此为': '因为',
    '日以': '所以',
    '日?': '有',

    # English punctuation artifacts
    '"': '"',
    '"': '"',
    ''': "'",
    '-': '—',
    '-': '-',
    ',
    ''': ': ''',
    ''': ''',
}

def has_chinese(text):
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def has_garbled(text):
    """Check if text has garbled patterns."""
    for pattern in GARBLED_MAP.keys():
        if pattern in text:
            return True
    return False

def fix_file(file_path, dry_run=False):
    """Fix a single file using pattern mapping."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not has_garbled(content):
            return (False, "no_garbled")

        # Apply all pattern replacements
        fixed = content
        patterns_found = []
        for garbled, correct in GARBLED_MAP.items():
            if garbled in fixed:
                patterns_found.append(garbled)
                fixed = fixed.replace(garbled, correct)

        if fixed == content:
            return (False, "no_change")

        if not has_chinese(fixed):
            return (False, "no_chinese")

        if dry_run:
            return (True, f"will_fix: {len(patterns_found)} patterns")

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed)

        return (True, f"fixed: {len(patterns_found)} patterns")

    except Exception as e:
        return (False, f"error: {e}")

def main():
    base_dir = Path(__file__).parent.parent
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    print(f"Base directory: {base_dir}")
    print(f"Mode: {'dry-run' if dry_run else 'fix'}")
    print("-" * 60)

    stats = {"total": 0, "fixed": 0, "skipped": 0, "error": 0}
    fixed_files = []

    # Directories to scan
    dirs_to_scan = [
        base_dir / "shared" / "skills",
        base_dir / "shared" / "knowledge",
        base_dir / "NanoBot",
        base_dir / "scripts",
    ]

    # Extensions to check
    extensions = ['.md', '.py', '.json', '.txt']

    for dir_path in dirs_to_scan:
        if not dir_path.exists():
            continue
        for ext in extensions:
            for file_path in dir_path.rglob(f'*{ext}'):
                stats["total"] += 1
                fixed, msg = fix_file(file_path, dry_run)
                rel_path = file_path.relative_to(base_dir)

                if fixed:
                    stats["fixed"] += 1
                    fixed_files.append((str(rel_path), msg))
                elif "error" in str(msg):
                    stats["error"] += 1
                    print(f"[ERROR] {rel_path}: {msg}")
                else:
                    stats["skipped"] += 1

    # Check bot directories
    for bot_dir in base_dir.glob("bot*"):
        if bot_dir.is_dir():
            for ext in extensions:
                for file_path in bot_dir.rglob(f'*{ext}'):
                    stats["total"] += 1
                    fixed, msg = fix_file(file_path, dry_run)
                    rel_path = file_path.relative_to(base_dir)

                    if fixed:
                        stats["fixed"] += 1
                        fixed_files.append((str(rel_path), msg))
                    elif "error" in str(msg):
                        stats["error"] += 1
                    else:
                        stats["skipped"] += 1

    # Check root md files
    for file_path in base_dir.glob("*.md"):
        stats["total"] += 1
        fixed, msg = fix_file(file_path, dry_run)
        rel_path = file_path.relative_to(base_dir)

        if fixed:
            stats["fixed"] += 1
            fixed_files.append((str(rel_path), msg))
        elif "error" in str(msg):
            stats["error"] += 1
        else:
            stats["skipped"] += 1

    print("-" * 60)
    print(f"Total files scanned: {stats['total']}")
    print(f"Files fixed: {stats['fixed']}")
    print(f"Files skipped: {stats['skipped']}")
    print(f"Errors: {stats['error']}")

    if fixed_files:
        print("\nFixed files:")
        for path, msg in fixed_files:
            print(f"  [FIX] {path} ({msg})")

if __name__ == "__main__":
    main()
