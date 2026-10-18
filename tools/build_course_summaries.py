from __future__ import annotations

import argparse
from datetime import datetime, timezone

try:
    from common import build_preview_url, build_syllabus_url, read_json, write_json
except ImportError:
    from .common import build_preview_url, build_syllabus_url, read_json, write_json


def merge_course(seed, parsed=None, override=None):
    parsed = parsed or {}
    override = override or {}
    code = seed.get("courseCode", "").upper()
    op_code = seed.get("opCode") or code
    course = {
        **seed,
        "courseCode": code,
        "opCode": op_code,
        "syllabusUrl": seed.get("syllabusUrl") or build_syllabus_url(seed.get("yearTerm", "1142"), op_code),
        "previewUrl": seed.get("previewUrl") or build_preview_url(seed.get("yearTerm", "1142"), op_code),
        "plainSummary": parsed.get("plainSummary", "課綱尚未成功解析，請開啟原始課綱確認課程內容。"),
        "grading": parsed.get("grading", []),
        "gradingStatus": parsed.get("gradingStatus", "not_found"),
        "gradingMessage": parsed.get("gradingMessage", "課綱頁面未成功解析到評分表格"),
        "prerequisites": parsed.get("prerequisites", "課綱未明確要求。"),
        "courseOutputs": parsed.get("courseOutputs", []),
        "urlCheckStatus": seed.get("urlCheckStatus", "unknown"),
        "parseStatus": parsed.get("parseStatus", "not_parsed"),
        "manualReviewed": bool(override),
    }
    course.update(override)
    course["manualReviewed"] = bool(override)
    return course


def build(seed_path, parsed_path, override_path, output_path):
    seeds = read_json(seed_path, [])
    parsed = read_json(parsed_path, {})
    overrides = read_json(override_path, {})
    year_term = seeds[0].get("yearTerm", "1142") if seeds else "1142"
    courses = {}
    for seed in seeds:
        code = seed.get("courseCode", "").upper()
        courses[code] = merge_course(seed, parsed.get(code), overrides.get(code))
    data = {
        "metadata": {
            "version": "1.1.0",
            "school": "中原大學",
            "source": "開課查詢系統匯出資料與公開課綱頁面",
            "yearTerm": year_term,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "description": "AI 幫你監 Chrome Extension 使用的課綱摘要資料，本版本不使用外部 AI API",
        },
        "courses": courses,
    }
    write_json(output_path, data)
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="extension/data/course_seed.json")
    parser.add_argument("--parsed", default="tools/output/syllabus_parsed.json")
    parser.add_argument("--overrides", default="tools/manual_overrides.json")
    parser.add_argument("--output", default="extension/data/course_summaries.json")
    args = parser.parse_args()
    data = build(args.seed, args.parsed, args.overrides, args.output)
    print(f"已輸出 {len(data['courses'])} 筆摘要到 {args.output}")


if __name__ == "__main__":
    main()
