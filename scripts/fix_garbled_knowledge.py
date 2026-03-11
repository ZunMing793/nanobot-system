import ftfy
from pathlib import Path
import re

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def has_garbled(text):
    patterns = ['ã', 'è', 'ç', '、', '"', 'â"', 'â"', 'â"', 'Ã', 'æ\x94', '¥', '§', '¶', '¼', '½']
    return any(p in text for p in patterns)

def fix_file(path):
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        # Try to decode
        try:
            content = raw.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            for enc in ['gbk', 'gb2312', 'gb18030', 'latin-1']:
                try:
                    content = raw.decode(enc)
                    break
                except:
                    continue
            else:
                return None

        if not has_garbled(content):
            return None
        fixed = ftfy.fix_text(content)
        if fixed != content and has_chinese(fixed):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return str(path)
    except Exception as e:
        print(f'  ERROR: {path} - {e}')
    return None

base = Path('shared/knowledge')
files_scanned = 0
files_with_garbled = 0
fixed = []

for f in base.rglob('*'):
    if f.is_file() and f.suffix in ['.md', '.json', '.txt', '.py']:
        files_scanned += 1
        result = fix_file(f)
        if result:
            fixed.append(result)
            files_with_garbled += 1

print('Scanned shared/knowledge: {} files'.format(files_scanned))
print('Found garbled: {} files'.format(files_with_garbled))
print('Fixed: {} files'.format(len(fixed)))
for f in fixed:
    print('  FIXED: {}'.format(f))
