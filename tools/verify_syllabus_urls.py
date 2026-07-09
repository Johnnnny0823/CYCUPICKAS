from __future__ import annotations

import argparse
from datetime import datetime, timezone

import requests

try:
    from common import build_syllabus_url, clean_text, read_json, write_json
except ImportError:
    from .common import build_syllabus_url, clean_text, read_json, write_json

KEYWORDS = ["課程教學目標", "課程綱要", "課程進度", "評量矩陣", "評分", "平時", "期中", "期末", "先備", "先修", "教學目標", "評量方式"]


def pdf_text(content):
    try:
        import fitz

        doc = fitz.open(stream=content, filetype="pdf")
        return clean_text(" ".join(page.get_text() for page in doc))
    except Exception:
        return ""


def response_text(response):
    content_type = response.headers.get("content-type", "").lower()
    if response.content.startswith(b"%PDF") or "pdf" in content_type:
        return pdf_text(response.content), "pdf"
    return response.text, "html"


def verify_course(course, timeout=12):
    url = course.get("syllabusUrl") or build_syllabus_url(course.get("yearTerm", "1142"), course.get("opCode") or course.get("courseCode", ""))
    result = {
        "courseCode": course.get("courseCode", ""),
        "opCode": course.get("opCode", ""),
        "courseName": course.get("courseName", ""),
        "teacher": course.get("teacher", ""),
        "syllabusUrl": url,
        "httpStatus": None,
        "contentType": "",
        "reachable": False,
        "hasUsefulContent": False,
        "matchedKeywords": [],
        "message": "無法讀取課綱頁面或課綱尚未開放",
    }
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "AI-Course-Watch/1.1"})
        result["httpStatus"] = response.status_code
        text, content_type = response_text(response)
        result["contentType"] = content_type
        result["matchedKeywords"] = [keyword for keyword in KEYWORDS if keyword in text]
        result["reachable"] = response.ok
        result["hasUsefulContent"] = response.ok and bool(result["matchedKeywords"])
        if result["hasUsefulContent"]:
            result["message"] = "課綱頁面可讀取"
    except requests.RequestException as exc:
        result["message"] = f"無法讀取課綱頁面或課綱尚未開放：{exc}"
    return result


def verify(input_path, output_path):
    courses = read_json(input_path, [])
    results = [verify_course(course) for course in courses]
    data = {
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "yearTerm": courses[0].get("yearTerm", "1142") if courses else "1142",
        "total": len(results),
        "success": sum(1 for item in results if item["hasUsefulContent"]),
        "failed": sum(1 for item in results if not item["hasUsefulContent"]),
        "results": results,
    }
    write_json(output_path, data)
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = verify(args.input, args.output)
    print(f"成功：{data['success']} 筆；失敗：{data['failed']} 筆")
    for item in data["results"]:
        print(f"- {item['courseCode']} ({item.get('opCode')}) {item['message']}")


if __name__ == "__main__":
    main()
