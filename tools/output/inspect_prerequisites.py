import fitz, re
from pathlib import Path
for path in sorted(Path('tools/raw/syllabus_html').glob('*.pdf')):
    text='\n'.join(page.get_text() for page in fitz.open(path))
    print('\n====', path.name, '====')
    for key in ['學前科目或能', '能力需求', '先修', '先備', 'prerequisite', 'Prerequisite']:
        i=text.find(key)
        if i >= 0:
            print('--', key, '--')
            print(re.sub(r'\s+',' ', text[max(0,i-120):i+260]))
            break
    else:
        print('找不到先備相關段落')
