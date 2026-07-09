import fitz, re
from pathlib import Path
for path in sorted(Path('tools/raw/syllabus_html').glob('*.pdf')):
    text='\n'.join(page.get_text() for page in fitz.open(path))
    print('\n====', path.name, '====')
    for pat in ['課程教學目標','評分','評量','期末報告','在i-learning','課程綱要及進度','學前科目']:
        i=text.find(pat)
        if i!=-1:
            print('--', pat, '--')
            print(re.sub(r'\s+',' ',text[i:i+600])[:600])
