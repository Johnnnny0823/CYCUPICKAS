import json
import re
from pathlib import Path

root = Path('.')
html = (root / 'demo/fake_selection_system.html').read_text(encoding='utf-8-sig')
js = (root / 'demo/fake_selection_system.js').read_text(encoding='utf-8-sig')
content = (root / 'extension/content.js').read_text(encoding='utf-8-sig')
manifest = json.loads((root / 'extension/manifest.json').read_text(encoding='utf-8-sig'))
seed = json.loads((root / 'extension/data/course_seed_itouch.json').read_text(encoding='utf-8-sig'))
s1 = json.loads((root / 'extension/data/course_summaries.json').read_text(encoding='utf-8-sig'))['courses']
s2 = json.loads((root / 'extension/data/course_summaries_itouch.json').read_text(encoding='utf-8-sig'))['courses']
summaries = {**s1, **s2}

assert 'course_seed_itouch.json' in js, 'Demo JS must load full course seed'
assert len(seed) >= 50, f'Expected full course list, got {len(seed)}'
assert all(c.get('courseCode') for c in seed), 'Every seed row needs courseCode'
assert set(['一','二','三','四']).issubset(set(re.findall(r'data-grade="(.)"', html))), 'Grade filters missing'
for grade in ['一','二','三','四']:
    assert any(f'資管{grade}' in (c.get('className') or '') for c in seed), f'No courses for grade {grade}'

matched = sum(1 for c in seed if c['courseCode'].upper() in summaries)
assert matched >= 50, f'Too few summaries matched seed rows: {matched}/{len(seed)}'

for required in ['AI 篩選', 'no-report', 'no-exam', 'no-homework', '比較清單', 'aiwatch-compare-modal', 'isDemoCoursePage']:
    assert required in content, f'Missing content feature: {required}'
assert 'itouch.cycu.edu.tw' not in json.dumps(manifest, ensure_ascii=False), 'Manifest should not match itouch anymore'
assert 'https://*.cycu.edu.tw/*' not in json.dumps(manifest, ensure_ascii=False), 'Manifest should not inject into CYCU real pages'
assert manifest['content_scripts'][0]['matches'] == ['http://localhost:*/*', 'http://127.0.0.1:*/*', 'file:///*']

print(json.dumps({
    'seed_rows': len(seed),
    'summary_matches': matched,
    'grades': {g: sum(1 for c in seed if f'資管{g}' in (c.get('className') or '')) for g in ['一','二','三','四']},
    'manifest_matches': manifest['content_scripts'][0]['matches'],
}, ensure_ascii=False, indent=2))
