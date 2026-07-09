import fitz, re
from pathlib import Path
for path in sorted(Path('tools/raw/syllabus_html').glob('*.pdf')):
    text='\n'.join(page.get_text() for page in fitz.open(path))
    i=text.find('考核項目及評量標準')
    print('\n====', path.name, '====')
    if i!=-1:
        print(re.sub(r'\s+',' ', text[i:i+350]))
    else:
        print('not found')
