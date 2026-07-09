from __future__ import annotations

import argparse
import csv
from pathlib import Path

try:
    from common import build_preview_url, build_syllabus_url, clean_text, write_json
except ImportError:
    from .common import build_preview_url, build_syllabus_url, clean_text, write_json


FIELD_ALIASES = {
    "courseCode": ["課程代碼", "課號", "courseCode"],
    "courseName": ["課程名稱", "科目名稱", "課名", "courseName"],
    "teacher": ["授課教師", "教師", "任課教師", "teacher"],
    "credits": ["學分", "credits"],
    "timeText": ["上課時間", "時間", "時間1", "timeText"],
    "classroom": ["教室", "上課教室", "教室1", "classroom"],
    "department": ["開課系所", "系所", "權責單位", "department"],
    "courseCategory": ["課程類別", "類別", "courseCategory"],
    "className": ["開課班級", "班級", "className"],
    "requiredOrElective": ["必選修", "必修或選修", "requiredOrElective"],
    "language": ["授課語言", "語言", "language"],
    "quota": ["選課餘額", "餘額", "quota"],
    "note": ["備註", "note"],
}


def pick(row, aliases):
    normalized = {clean_text(k).lower(): v for k, v in row.items()}
    for alias in aliases:
        key = clean_text(alias).lower()
        if key in normalized:
            return normalized[key]
    for key, value in row.items():
        key_text = clean_text(key).lower()
        if any(clean_text(alias).lower() in key_text for alias in aliases):
            return value
    return ""


def load_rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as fh:
            return list(csv.DictReader(fh))
    try:
        import pandas as pd

        return pd.read_excel(path).fillna("").to_dict(orient="records")
    except Exception as exc:
        raise SystemExit(f"無法讀取 {path}。若是舊版 .xls，請用 Excel 另存為 .csv 後重跑。原始錯誤：{exc}")


def convert(input_path, year_term, output_path):
    rows = load_rows(Path(input_path))
    courses = []
    for row in rows:
        course = {field: clean_text(pick(row, aliases)) for field, aliases in FIELD_ALIASES.items()}
        if not course["courseCode"] and not course["courseName"]:
            continue
        course["courseCode"] = course["courseCode"].upper()
        course["opCode"] = course["courseCode"]
        course["yearTerm"] = clean_text(year_term)
        course["syllabusUrl"] = build_syllabus_url(year_term, course["opCode"])
        course["previewUrl"] = build_preview_url(year_term, course["opCode"])
        courses.append(course)
    write_json(output_path, courses)
    return courses


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--year-term", default="1142")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    courses = convert(args.input, args.year_term, args.output)
    print(f"已輸出 {len(courses)} 筆課程到 {args.output}")


if __name__ == "__main__":
    main()
