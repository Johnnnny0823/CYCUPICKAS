from __future__ import annotations

import re
from urllib.parse import urlencode


DEFAULT_YEAR_TERM = "1142"
SYLLABUS_BASE_URL = "https://cmap.cycu.edu.tw:8443/Syllabus/syllabus/outPutCoursePreView.action"
PREVIEW_BASE_URL = "https://cmap.cycu.edu.tw:8443/Syllabus/CoursePreview.html"


def clean_text(value) -> str:
    text = "" if value is None else str(value)
    return re.sub(r"\s+", " ", text).strip()


def build_syllabus_url(year_term=DEFAULT_YEAR_TERM, op_code="") -> str:
    year_term = clean_text(year_term) or DEFAULT_YEAR_TERM
    op_code = clean_text(op_code).upper()
    return f"{SYLLABUS_BASE_URL}?{urlencode({'yearTerm': year_term, 'opCode': op_code, 'langId': 'zh_TW'})}"


def build_preview_url(year_term=DEFAULT_YEAR_TERM, op_code="") -> str:
    year_term = clean_text(year_term) or DEFAULT_YEAR_TERM
    op_code = clean_text(op_code).upper()
    return f"{PREVIEW_BASE_URL}?{urlencode({'yearTerm': year_term, 'opCode': op_code})}"


def read_json(path, default=None):
    import json
    from pathlib import Path

    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    import json
    from pathlib import Path

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
