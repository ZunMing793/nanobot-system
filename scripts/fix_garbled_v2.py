#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 garbled text (乱码) - 第二版

这个脚本处理 CP1252 编码问题导致的乱码。
"""

import sys
import io
import re
from pathlib import Path

# 设置 stdout 为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# CP1252 到 UTF-8 的字符映射
# 这是由 Windows-1252 编码被误读为 UTF-8 导致的问题
CP1252_TO_UTF8 = {
    # 中文标点符号
    '\u00bb': '》',  # » (RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK)
    '\u00a9': '，',  # © (COPYRIGHT SIGN) -> 但在 CP1252 中是逗号
    '\u00a8': '，',  # ¨ (DIAERESIS)
    '\u00aa': '，',  # ª (FEMININE ORDINAL INDICATOR)
    '\u00ac': '，',  # ¬ (NOT SIGN)
    '\u00ae': '，',  # ® (REGISTERED SIGN)
    '\u00b0': '，',  # ° (DEGREE SIGN)
    '\u00b1': '，',  # ± (PLUS-MINUS SIGN)
    '\u00b2': '，',  # ² (SUPERSCRIPT TWO)
    '\u00b3': '，',  # ³ (SUPERSCRIPT THREE)
    '\u00b7': '·',  # · (MIDDLE DOT)
    '\u00bc': '，',  # ¼ (VULGAR FRACTION ONE QUARTER)
    '\u00bd': '，',  # ½ (VULGAR FRACTION ONE HALF)
    '\u00be': '，',  # ¾ (VULGAR FRACTION THREE QUARTERS)
    '\u00d7': '×',  # × (MULTIPLICATION SIGN)
    '\u00f7': '÷',  # ÷ (DIVISION SIGN)

    # 常见乱码模式 - 单字符
    '\u00e4': '的',  # ä -> 的
    '\u00e5': '的',  # å -> 的
    '\u00e8': '是',  # è -> 是
    '\u00e9': '的',  # é -> 的
    '\u00ea': '的',  # ê -> 的
    '\u00eb': '的',  # ë -> 的
    '\u00ec': '的',  # ì -> 的
    '\u00ed': '的',  # í -> 的
    '\u00ee': '的',  # î -> 的
    '\u00ef': '的',  # ï -> 的
    '\u00f0': '的',  # ð -> 的
    '\u00f1': '的',  # ñ -> 的
    '\u00f2': '的',  # ò -> 的
    '\u00f3': '的',  # ó -> 的
    '\u00f4': '的',  # ô -> 的
    '\u00f5': '的',  # õ -> 的
    '\u00f6': '的',  # ö -> 的
    '\u00f7': '的',  # ÷ -> 的
    '\u00f8': '的',  # ø -> 的
    '\u00f9': '的',  # ù -> 的
    '\u00fa': '的',  # ú -> 的
    '\u00fb': '的',  # û -> 的
    '\u00fc': '的',  # ü -> 的
    '\u00fd': '的',  # ý -> 的
    '\u00fe': '的',  # þ -> 的
    '\u00ff': '的',  # ÿ -> 的
    '\u00c7': '的',  # Ç -> 的
    '\u00c0': '的',  # À -> 的
    '\u00c1': '的',  # Á -> 的
    '\u00c2': '的',  # Â -> 的
    '\u00c3': '的',  # Ã -> 的
    '\u00c5': '的',  # Å -> 的
    '\u00c6': '的',  # Æ -> 的
    '\u00c8': '的',  # È -> 的
    '\u00c9': '的',  # É -> 的
    '\u00ca': '的',  # Ê -> 的
    '\u00cb': '的',  # Ë -> 的
    '\u00cc': '的',  # Ì -> 的
    '\u00cd': '的',  # Í -> 的
    '\u00ce': '的',  # Î -> 的
    '\u00cf': '的',  # Ï -> 的
    '\u00d0': '的',  # Ð -> 的
    '\u00d1': '的',  # Ñ -> 的
    '\u00d2': '的',  # Ò -> 的
    '\u00d3': '的',  # Ó -> 的
    '\u00d4': '的',  # Ô -> 的
    '\u00d5': '的',  # Õ -> 的
    '\u00d6': '的',  # Ö -> 的
    '\u00d8': '的',  # Ø -> 的
    '\u00d9': '的',  # Ù -> 的
    '\u00da': '的',  # Ú -> 的
    '\u00db': '的',  # Û -> 的
    '\u00dc': '的',  # Ü -> 的
    '\u00dd': '的',  # Ý -> 的
    '\u00de': '的',  # Þ -> 的
    '\u00df': '的',  # ß -> 的
}

# 更多模式 - 基于常见的乱码组合
MORE_PATTERNS = [
    # "此" 开头的常见乱码
    ('此为', '因为'),
    ('此³', '关于'),
    ('日以', '所以'),
    ('日?', '有'),
    ('可以', '可以'),
    ('对事', '对于'),
    ('已给', '已经'),
    ('已', '已'),

    # 更多单字符映射
    ('价', '价'),
    ('数', '数'),
    ('码', '码'),
    ('名', '名'),
    ('称', '称'),
    ('期', '期'),
    ('间', '间'),
    ('度', '度'),
    ('能', '能'),
    ('关', '关'),
    ('入', '入'),
    ('出', '出'),
    ('来', '来'),
    ('去', '去'),
    ('分', '分'),
    ('合', '合'),
    ('变', '变'),
    ('化', '化'),
    ('更', '更'),
    ('新', '新'),
    ('据', '据'),
    ('说', '说'),
    ('应', '应'),
    ('该', '该'),
    ('当', '当'),
    ('时', '时'),
    ('最', '最'),
    ('比', '比'),
    ('或', '或'),
    ('也', '也'),
    ('又', '又'),
    ('再', '再'),
    ('还', '还'),
    ('无', '无'),
    ('只', '只'),
    ('即', '即'),
    ('可', '可'),
    ('需', '需'),
    ('要', '要'),
    ('必', '必'),
    ('及', '及'),
    ('与', '与'),
    ('其', '其'),
    ('它', '它'),
    ('但', '但'),
    ('若', '若'),
    ('则', '则'),
    ('因', '因'),
    ('为', '为'),
    ('所', '所'),
    ('以', '以'),
    ('之', '之'),
    ('于', '于'),
    ('而', '而且'),
    ('并', '并'),
    ('选', '选'),
    ('查', '查'),
    ('找', '找'),
    ('看', '看'),
    ('见', '见'),
    ('想', '想'),
    ('知', '知'),
    ('道', '道'),
    ('行', '行'),
    ('表', '表'),
    ('示', '示'),
    ('显', '显'),
    ('明', '明'),
    ('值', '值'),
    ('类', '类'),
    ('型', '型'),
    ('格', '格'),
    ('式', '式'),
    ('样', '样'),
    ('种', '种'),
    ('个', '个'),
    ('些', '些'),
    ('每', '每'),
    ('各', '各'),
    ('全', '全'),
    ('多', '多'),
    ('少', '少'),
    ('大', '大'),
    ('小', '小'),
    ('长', '长'),
    ('短', '短'),
    ('高', '高'),
    ('低', '低'),
    ('前', '前'),
    ('后', '后'),
    ('左', '左'),
    ('右', '右'),
    ('上', '上'),
    ('下', '下'),
    ('中', '中'),
    ('内', '内'),
    ('外', '外'),
    ('里', '里'),
    ('边', '边'),
    ('头', '头'),
    ('尾', '尾'),
    ('始', '始'),
    ('末', '末'),
    ('初', '初'),
    ('终', '终'),
    ('第', '第'),
    ('总', '总'),
    ('共', '共'),
    ('计', '计'),
    ('算', '算'),
    ('统', '统'),
    ('报', '报'),
    ('告', '告'),
    ('述', '述'),
    ('描', '描'),
    ('写', '写'),
    ('读', '读'),
    ('改', '改'),
    ('换', '换'),
    ('取', '取'),
    ('存', '存'),
    ('传', '传'),
    ('输', '输'),
    ('列', '列'),
    ('排', '排'),
    ('序', '序'),
    ('组', '组'),
    ('块', '块'),
    ('段', '段'),
    ('节', '节'),
    ('章', '章'),
    ('页', '页'),
    ('行', '行'),
    ('列', '列'),
    ('字', '字'),
    ('符', '符'),
    ('号', '号'),
    ('标', '标'),
    ('点', '点'),
    ('线', '线'),
    ('面', '面'),
    ('体', '体'),
    ('方', '方'),
    ('圆', '圆'),
    ('角', '角'),
    ('度', '度'),
    ('毫', '毫'),
    ('秒', '秒'),
    ('分', '分'),
    ('时', '时'),
    ('日', '日'),
    ('周', '周'),
    ('月', '月'),
    ('季', '季'),
    ('年', '年'),
    ('代', '代'),
    ('号', '号'),
    ('股', '股'),
    ('票', '票'),
    ('券', '券'),
    ('金', '金'),
    ('银', '银'),
    ('钱', '钱'),
    ('币', '币'),
    ('元', '元'),
    ('角', '角'),
    ('分', '分'),
    ('万', '万'),
    ('亿', '亿'),
    ('兆', '兆'),
    ('十', '十'),
    ('百', '百'),
    ('千', '千'),
    ('零', '零'),
    ('整', '整'),
]

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def has_garbled(text):
    """检测是否有乱码模式"""
    # 检查 CP1252 字符
    for char in CP1252_TO_UTF8.keys():
        if char in text:
            return True
    # 检查更多模式
    for garbled, _ in MORE_PATTERNS:
        if garbled in text:
            return True
    return False
def fix_text(content):
    """修复乱码文本"""
    fixed = content

    patterns_fixed = []

    # 先应用单字符映射
    for garbled, correct in CP1252_TO_UTF8.items():
        if garbled in fixed:
            fixed = fixed.replace(garbled, correct)
            if garbled not in patterns_fixed:
                patterns_fixed.append(repr(garbled))

    # 再应用多字符映射
    for garbled, correct in MORE_PATTERNS:
        if garbled in fixed:
                fixed = fixed.replace(garbled, correct)
                if garbled not in patterns_fixed:
                    patterns_fixed.append(garbled)

    if fixed == content:
        return None

    return fixed
def fix_file(file_path, dry_run=False):
    """修复单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not has_garbled(content):
            return (False, 'no_garbled')

        fixed = fix_text(content)
        if fixed is None:
            return (False, 'fix_failed')

        if not has_chinese(fixed):
            return (False, 'no_chinese_after_fix')

        if dry_run:
            return (True, 'will_fix')

        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(fixed)

        return (True, 'fixed')

    except Exception as e:
        return (False, f'error: {e}')
def main():
    import argparse
    parser = argparse.ArgumentParser(description='修复 garbled text 乱码')
    parser.add_argument('--dry-run', action='store_true', help='只检测不修改')
    parser.add_argument('paths', nargs='+', type=Path, help='要检查的文件或目录')
    args = parser.parse_args()

    files_to_check = []
    for path in args.paths:
        if path.is_file():
            files_to_check.append(path)
        elif path.is_dir():
                files_to_check.extend(path.rglob('*.md'))
                files_to_check.extend(path.rglob('*.json'))
                files_to_check.extend(path.rglob('*.txt'))
                files_to_check.extend(path.rglob('*.py'))

    print(f'检查 {len(files_to_check)} 个文件...')
    print()

    stats = {'total': len(files_to_check), 'fixed': 0, 'skipped': 0, 'error': 0}
    fixed_files = []

    for file_path in sorted(files_to_check):
        fixed, msg = fix_file(file_path, dry_run=args.dry_run)
        if fixed:
            stats['fixed'] += 1
            fixed_files.append((str(file_path), msg))
        elif 'error' in msg:
            stats['error'] += 1
        else:
            stats['skipped'] += 1

    print()
    print(f'总计: {stats["total"]} 个文件')
    print(f'修复: {stats["fixed"]} 个文件')
    print(f'跳过: {stats["skipped"]} 个文件')
    print(f'错误: {stats["error"]} 个文件')

    if fixed_files:
        print()
        print('已修复的文件:')
        for path, msg in fixed_files[:20]:
            print(f'  {path}: {msg}')
        if len(fixed_files) > 20:
            print(f'  ... 还有 {len(fixed_files) - 20} 个文件')
if __name__ == '__main__':
    main()
