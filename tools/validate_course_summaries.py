from __future__ import annotations

import argparse

try:
    from common import read_json
except ImportError:
    from .common import read_json

FORBIDDEN_WORDS = ["甜課", "涼課", "雷課", "老師很爛", "很爽", "必修爽課"]


def validate_summary_data(data):
    errors = []
    warnings = []
    courses = data.get("courses")
    if not isinstance(courses, dict):
        return ["courses 必須是物件"], warnings
    for code, course in courses.items():
        for field in ["courseCode", "courseName", "teacher", "syllabusUrl"]:
            if not course.get(field):
                errors.append(f"{code} 缺少 {field}")
        grading = course.get("grading")
        if not isinstance(grading, list):
            errors.append(f"{code} grading 必須是陣列")
            grading = []
        total = 0
        has_percent = False
        for item in grading:
            percent = item.get("percent")
            if percent is not None and not isinstance(percent, (int, float)):
                errors.append(f"{code} grading percent 必須是數字或 null")
            if isinstance(percent, (int, float)):
                total += percent
                has_percent = True
        if has_percent and total != 100:
            warnings.append(f"{code} grading 比例合計為 {total}，請人工確認")
        if len(course.get("plainSummary", "")) > 120:
            errors.append(f"{code} plainSummary 超過 120 字")
        visible = " ".join(str(course.get(field, "")) for field in ["plainSummary", "prerequisites", "note"])
        for word in FORBIDDEN_WORDS:
            if word in visible:
                errors.append(f"{code} 出現禁止詞：{word}")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    errors, warnings = validate_summary_data(read_json(args.input, {}))
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("course_summaries.json 驗證通過")


if __name__ == "__main__":
    main()


