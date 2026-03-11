#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix garbled Chinese text using ftfy library."""

import sys
import re
from pathlib import Path

try:
    import ftfy
except ImportError:
    print("ftfy not installed. Run: pip install ftfy")
    sys.exit(1)

def has_chinese(text):
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def has_garbled(text):
    """Check if text has garbled patterns."""
    # Patterns that indicate UTF-8 was misinterpreted
    patterns = [
        '\ufffd',  # replacement character
        '\xe6', '\xe7', '\xe8', '\xe9', '\xe4', '\xe5',  # common UTF-8 lead bytes as Latin-1
        '\u00e6', '\u00e7', '\u00e8', '\u00e9', '\u00e4', '\u00e5',
    ]
    for p in patterns:
        if p in text:
            return True
    # Check for double-encoded patterns
    if re.search(r'[\x80-\xff]{2,}', text):
        return True
    return False

def fix_file(file_path, dry_run=False):
    """Fix a single file using ftfy."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Use ftfy to fix encoding
        fixed = ftfy.fix_text(content)

        # Check if anything changed
        if fixed == content:
            return (False, "same")

        # Check if fixed version has Chinese
        if not has_chinese(fixed):
            return (False, "no_chinese")

        if dry_run:
            return (True, "will_fix")

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed)

        return (True, "fixed")

    except Exception as e:
        return (False, f"error:{e}")

def main():
    base_dir = Path(__file__).parent.parent / "shared" / "skills"
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    # Avoid encoding issues in console
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print(f"Dir: {base_dir}")
    print(f"Mode: {'dry-run' if dry_run else 'fix'}")
    print("-" * 50)

    stats = {"total": 0, "fixed": 0, "skipped": 0, "error": 0}
    fixed_files = []

    for md_file in sorted(base_dir.rglob("*.md")):
        stats["total"] += 1
        fixed, msg = fix_file(md_file, dry_run)

        rel = str(md_file.relative_to(base_dir))

        if fixed:
            stats["fixed"] += 1
            fixed_files.append(rel)
        elif "error" in str(msg):
            stats["error"] += 1
        else:
            stats["skipped"] += 1

    for path in fixed_files:
        print(f"[FIX] {path}")

    print("-" * 50)
    print(f"Total: {stats['total']}")
    print(f"Fixed: {stats['fixed']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['error']}")

if __name__ == "__main__":
    main()
