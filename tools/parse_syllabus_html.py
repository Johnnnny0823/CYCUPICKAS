from __future__ import annotations

import argparse
import re
from pathlib import Path

from bs4 import BeautifulSoup

try:
    from common import clean_text, write_json
except ImportError:
    from .common import clean_text, write_json

OUTPUT_KEYWORDS = ["作業", "報告", "專題", "上機", "測驗", "討論", "實作", "期中", "期末"]
PREREQ_KEYWORDS = ["先修", "先備", "建議具備", "prerequisite", "Python", "Java", "資料庫", "統計", "程式", "英文"]
GRADING_KEYWORDS = ["評量", "評分", "成績", "平時", "期中", "期末", "報告", "作業", "測驗"]


def text_after_keyword(text, keywords, limit=160):
    for keyword in keywords:
        index = text.lower().find(keyword.lower())
        if index >= 0:
            return clean_text(text[index : index + limit])
    return ""


def parse_percent(text):
    match = re.search(r"(\d{1,3})\s*%", text)
    return int(match.group(1)) if match else None


def parse_grading_lines(text):
    grading = []
    for raw in re.split(r"[\n\r]+|(?<=%)\s+", text):
        raw = clean_text(raw)
        if not raw or not any(keyword in raw for keyword in GRADING_KEYWORDS):
            continue
        percent = parse_percent(raw)
        if percent is None and "%" not in raw:
            continue
        item = re.sub(r"\d{1,3}\s*%", "", raw).strip(" ：:-") or raw
        grading.append({"item": item[:60], "percent": percent, "rawText": raw[:160]})
    return grading[:12]


def parse_grading_tables(soup):
    grading = []
    for table in soup.find_all("table"):
        table_text = clean_text(table.get_text(" "))
        if not any(keyword in table_text for keyword in GRADING_KEYWORDS):
            continue
        for row in table.find_all("tr"):
            cells = [clean_text(cell.get_text(" ")) for cell in row.find_all(["td", "th"])]
            raw = " ".join(cell for cell in cells if cell)
            if not raw or not any(keyword in raw for keyword in GRADING_KEYWORDS):
                continue
            percent = parse_percent(raw)
            item = re.sub(r"\d{1,3}\s*%", "", raw).strip(" ：:-")
            if item and item not in ["評分", "成績"]:
                grading.append({"item": item[:60], "percent": percent, "rawText": raw[:160]})
        if grading:
            break
    return grading


def pdf_to_text(path):
    try:
        import fitz

        doc = fitz.open(path)
        return clean_text("\n".join(page.get_text() for page in doc))
    except Exception as exc:
        return f"PDF 文字擷取失敗：{exc}"


def path_to_text_and_grading(path):
    if path.suffix.lower() == ".pdf":
        text = pdf_to_text(path)
        return text, parse_grading_lines(text)
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return clean_text(soup.get_text("\n")), parse_grading_tables(soup)


def course_code_from_path(path):
    return path.stem.split("_")[0].upper()


def extract_summary(text):
    match = re.search(r"(?:課程教學目標|教學目標|課程概述)\s+(.+?)(?:其他注意事項|成果導向|校指標|課程綱要及進度)", text)
    if not match:
        return "課綱已取得，但自動解析未擷取到明確課程摘要。"
    summary = clean_text(match.group(1))
    summary = re.sub(r"^[:：\s]+", "", summary)
    return summary[:118]


def extract_prerequisites(text):
    match = re.search(r"學前科目或能\s*力需求\s*(.*?)(?:教學助理|\(TA\)|辦公室時間|課程網址)", text)
    if match:
        value = clean_text(match.group(1)).strip("：:() ")
        if not value or value in ["空白", "(空白)"]:
            return "課綱未列明學前科目或能力需求。"
        if value.lower() in ["none", "no"] or value == "無":
            return "無。"
        return value[:80]
    return text_after_keyword(text, PREREQ_KEYWORDS, 120) or "課綱未列明學前科目或能力需求。"


def parse_one(path):
    text, grading = path_to_text_and_grading(path)
    plain_summary = extract_summary(text)
    prereq = extract_prerequisites(text)
    outputs = []
    source = " ".join([item["rawText"] for item in grading] + [text_after_keyword(text, OUTPUT_KEYWORDS, 260)])
    for keyword in OUTPUT_KEYWORDS:
        if keyword in source:
            outputs.append({"期中": "期中評量", "期末": "期末評量"}.get(keyword, keyword))
    return {
        "courseCode": course_code_from_path(path),
        "sourceFile": path.name,
        "plainSummary": plain_summary,
        "grading": grading,
        "gradingStatus": "success" if grading else "not_found",
        "gradingMessage": "" if grading else "課綱頁面未成功解析到評分表格",
        "prerequisites": prereq,
        "courseOutputs": list(dict.fromkeys(outputs)),
        "parseStatus": "success",
    }


def parse_dir(input_dir, output):
    files = list(Path(input_dir).glob("*.html")) + list(Path(input_dir).glob("*.pdf"))
    parsed = {}
    for path in files:
        item = parse_one(path)
        parsed[item["courseCode"]] = item
    write_json(output, parsed)
    return parsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="tools/raw/syllabus_html")
    parser.add_argument("--output", default="tools/output/syllabus_parsed.json")
    args = parser.parse_args()
    parsed = parse_dir(args.input_dir, args.output)
    print(f"已解析 {len(parsed)} 筆課綱")


if __name__ == "__main__":
    main()
