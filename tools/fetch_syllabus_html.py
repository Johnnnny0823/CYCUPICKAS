from __future__ import annotations

import argparse
import time
from pathlib import Path

import requests

try:
    from common import read_json
except ImportError:
    from .common import read_json


def file_suffix(response):
    content_type = response.headers.get("content-type", "").lower()
    if response.content.startswith(b"%PDF") or "pdf" in content_type:
        return ".pdf"
    return ".html"


def fetch(input_path, check_path, output_dir):
    courses = {course["courseCode"]: course for course in read_json(input_path, [])}
    checks = read_json(check_path, {}).get("results", [])
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    saved = []
    for index, check in enumerate(checks, start=1):
        if not check.get("reachable"):
            continue
        code = check["courseCode"]
        op_code = check.get("opCode") or courses.get(code, {}).get("opCode") or code
        url = check.get("syllabusUrl") or courses.get(code, {}).get("syllabusUrl")
        try:
            response = requests.get(url, timeout=12, headers={"User-Agent": "AI-Course-Watch/1.1"})
            response.raise_for_status()
            suffix = file_suffix(response)
            filename = f"{code}_{op_code}_{index}{suffix}"
            target = output / filename
            if suffix == ".pdf":
                target.write_bytes(response.content)
            else:
                target.write_text(response.text, encoding="utf-8")
            saved.append(filename)
            print(f"已儲存 {filename}")
        except requests.RequestException as exc:
            print(f"抓取失敗 {code}: {exc}")
        time.sleep(0.5)
    return saved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--check", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    saved = fetch(args.input, args.check, args.output_dir)
    print(f"完成，儲存 {len(saved)} 個課綱檔案")


if __name__ == "__main__":
    main()
