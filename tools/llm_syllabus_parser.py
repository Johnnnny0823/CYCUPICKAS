from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    from common import clean_text, write_json
    from parse_syllabus_html import path_to_text_and_grading, course_code_from_path
except ImportError:
    from .common import clean_text, write_json
    from .parse_syllabus_html import path_to_text_and_grading, course_code_from_path

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "plainSummary": {"type": "string", "description": "課程白話摘要，120字以內"},
        "grading": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "percent": {"type": "integer", "nullable": True},
                },
                "required": ["item", "percent"],
            },
        },
        "prerequisites": {"type": "string", "description": "先備知識或先修科目，若無則寫「無」"},
        "courseOutputs": {"type": "array", "items": {"type": "string"}},
        "effortLevel": {
            "type": "string",
            "enum": ["低", "中", "高"],
            "description": "依作業量、報告數、考試頻率推論這門課要花的精力",
        },
        "effortReason": {"type": "string", "description": "一句話說明為何是這個精力等級"},
    },
    "required": ["plainSummary", "grading", "prerequisites", "courseOutputs", "effortLevel", "effortReason"],
}

PROMPT_TEMPLATE = """你是課程課綱分析助手，任務是把下面的課綱原始文字轉成結構化資料，給大學生選課參考。

規則：
- plainSummary 用白話說明這門課在教什麼，不要照抄課綱官方用語。
- grading 從課綱中找出評分比例；找不到就回傳空陣列。
- prerequisites 若課綱沒寫，回答「無」。
- courseOutputs 列出這門課主要產出（如報告、考試、專題、實作），用簡短詞彙。
- effortLevel 依作業/報告數量、考試頻率、專題份量，推論修這門課大概要花多少精力（低/中/高）。
- effortReason 用一句話講為什麼給這個精力等級，例如「僅期中期末考試，無額外報告」。
- 只根據課綱文字內容判斷，不要編造課綱沒提到的資訊。

課程代碼：{course_code}

課綱原始文字：
{text}
"""


def call_gemini(prompt, api_key, timeout=30, retries=3):
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }).encode("utf-8")
    url = f"{GEMINI_URL}?key={api_key}"
    last_error = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            text = payload["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='ignore')}"
            if exc.code == 429:
                time.sleep(2 ** attempt)
                continue
            break
        except Exception as exc:
            last_error = str(exc)
            time.sleep(1)
    raise RuntimeError(f"Gemini 呼叫失敗（course={prompt[:0]}）：{last_error}")


def parse_one_with_llm(path, api_key):
    text, _fallback_grading = path_to_text_and_grading(path)
    course_code = course_code_from_path(path)
    if not text or len(text) < 20:
        return {
            "courseCode": course_code,
            "sourceFile": path.name,
            "parseStatus": "missing",
            "plainSummary": "課綱原始文字為空或無法讀取。",
            "grading": [],
            "gradingStatus": "not_found",
            "gradingMessage": "課綱頁面未成功解析到評分表格",
            "prerequisites": "課綱未列明學前科目或能力需求。",
            "courseOutputs": [],
            "effortLevel": None,
            "effortReason": "",
        }
    prompt = PROMPT_TEMPLATE.format(course_code=course_code, text=text[:6000])
    try:
        result = call_gemini(prompt, api_key)
    except Exception as exc:
        return {
            "courseCode": course_code,
            "sourceFile": path.name,
            "parseStatus": "llm_failed",
            "plainSummary": "AI 解析失敗，請改用人工 override 或檢查課綱來源。",
            "grading": [],
            "gradingStatus": "not_found",
            "gradingMessage": f"LLM 解析錯誤：{exc}",
            "prerequisites": "課綱未列明學前科目或能力需求。",
            "courseOutputs": [],
            "effortLevel": None,
            "effortReason": "",
        }
    grading = result.get("grading", [])
    return {
        "courseCode": course_code,
        "sourceFile": path.name,
        "parseStatus": "success",
        "plainSummary": clean_text(result.get("plainSummary", ""))[:200] or "課綱已取得，但 AI 未能歸納出摘要。",
        "grading": [
            {"item": clean_text(g.get("item", ""))[:60], "percent": g.get("percent"), "rawText": clean_text(g.get("item", ""))[:160]}
            for g in grading
            if g.get("item")
        ],
        "gradingStatus": "success" if grading else "not_found",
        "gradingMessage": "" if grading else "課綱頁面未成功解析到評分表格",
        "prerequisites": clean_text(result.get("prerequisites", ""))[:120] or "課綱未列明學前科目或能力需求。",
        "courseOutputs": list(dict.fromkeys(result.get("courseOutputs", []))),
        "effortLevel": result.get("effortLevel"),
        "effortReason": clean_text(result.get("effortReason", ""))[:100],
    }


def parse_dir(input_dir, output, api_key):
    files = sorted(set(Path(input_dir).glob("*.html")) | set(Path(input_dir).glob("*.pdf")))
    by_code = {}
    for path in files:
        by_code.setdefault(course_code_from_path(path), []).append(path)

    parsed = {}
    for code, paths in by_code.items():
        paths.sort(key=lambda p: p.suffix.lower() != ".pdf")
        item = None
        for path in paths:
            item = parse_one_with_llm(path, api_key)
            if item["parseStatus"] == "success":
                break
        parsed[code] = item
        print(f"{code}: {item['parseStatus']}")
    write_json(output, parsed)
    return parsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="tools/raw/syllabus_html")
    parser.add_argument("--output", default="tools/output/syllabus_parsed_llm.json")
    parser.add_argument("--api-key", default=None, help="未指定時讀環境變數 GEMINI_API_KEY 或 .env")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        env_path = Path(".env")
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        raise SystemExit("找不到 GEMINI_API_KEY，請在 .env 設定或用 --api-key 傳入")

    parsed = parse_dir(args.input_dir, args.output, api_key)
    success = sum(1 for item in parsed.values() if item["parseStatus"] == "success")
    print(f"已解析 {len(parsed)} 筆課綱，成功 {success} 筆，輸出到 {args.output}")


if __name__ == "__main__":
    main()
