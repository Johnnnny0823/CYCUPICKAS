# AI 幫你監

中原選課系統課綱摘要輔助 Chrome Extension 原型。本作品不是選課系統，也不代選課；目前只在本機 FAKE HTML Demo 課程列表上注入「AI 幫你監」按鈕，讀取本地摘要 JSON 顯示課綱摘要卡。

## 解決的問題

學生選課時常要逐一點開課綱才能看到課程內容、評分方式、先備知識與可能產出。本工具把公開課綱中已存在的資訊整理到同一頁，減少來回點擊。

## 架構

`課程資料.xls` -> `course_seed.json` -> 驗證課綱 URL -> 抓取 HTML -> 本地解析 -> `course_summaries.json` -> Chrome Extension 注入摘要卡。

本版本不使用 Gemini、OpenAI 或任何 LLM API。

## 使用教學

給展示人員的逐步操作文件：docs/USER_GUIDE.md。

## 安裝 Chrome Extension

1. 開啟 Chrome `chrome://extensions/`。
2. 開啟「開發人員模式」。
3. 點「載入未封裝項目」。
4. 選擇本專案的 `extension/` 資料夾。

## 啟動 Demo

```bash
python -m http.server 8765
```

打開：

```text
http://localhost:8765/demo/fake_selection_system.html
```

頁面本身載入完整課程表格；摘要、比較與 AI 篩選由 Extension 注入。

## 放入課程資料

把 `課程資料.xls` 放到：

```text
tools/raw/excel/課程資料.xls
```

若 Python 沒有舊版 `.xls` 讀取引擎，可用 Excel 另存為 CSV，再執行：

```bash
python tools/excel_to_course_seed.py --input tools/raw/excel/課程資料.csv --year-term 1142 --output extension/data/course_seed.json
```

## 資料處理流程

`excel_to_course_seed.py` 會保留 `courseCode` 作為頁面比對代碼，並使用 Excel 的 `課程代碼` 產生 `opCode` 與課綱網址。

```bash
python tools/excel_to_course_seed.py --input tools/raw/excel/課程資料.csv --year-term 1142 --output extension/data/course_seed.json
python tools/verify_syllabus_urls.py --input extension/data/course_seed.json --output tools/output/syllabus_url_check.json
python tools/fetch_syllabus_html.py --input extension/data/course_seed.json --check tools/output/syllabus_url_check.json --output-dir tools/raw/syllabus_html
python tools/parse_syllabus_html.py --input-dir tools/raw/syllabus_html --output tools/output/syllabus_parsed.json
python tools/build_course_summaries.py --seed extension/data/course_seed.json --parsed tools/output/syllabus_parsed.json --overrides tools/manual_overrides.json --output extension/data/course_summaries.json
python tools/validate_course_summaries.py extension/data/course_summaries.json
```

## 人工修正

編輯 `tools/manual_overrides.json`：

```json
{
  "MI123H": {
    "plainSummary": "本課介紹資訊管理概念、企業流程與資訊系統應用。",
    "prerequisites": "課綱未明確要求。",
    "courseOutputs": ["期中報告", "期末報告"]
  }
}
```

重跑 `build_course_summaries.py` 與 `validate_course_summaries.py`。

## 隱私與限制

不要求帳密、不登入校方系統、不讀取個人課表、成績或點名資料。不爬 Dcard、PTT、歐趴糖評論，只產生 Google 搜尋連結。

目前公開課綱頁可能回應正常但不含可解析課綱內容，請以 `tools/output/syllabus_url_check.json` 為準。

## Demo 操作

1. 啟動本機伺服器。
2. 載入 Extension。
3. 打開 Demo 頁。
4. 點課程列旁「AI 幫你監」。
5. 展開摘要卡，查看摘要、評分方式、先備知識、課程產出與補充搜尋。

## 常見錯誤

- `無法讀取 .xls`：用 Excel 另存 CSV，或安裝 `xlrd`。
- 按鈕沒出現：確認 Extension 已載入，且 URL 是 `http://localhost:8765/demo/fake_selection_system.html`。
- 摘要為尚未解析：代表課綱 URL 未開放或 HTML 未包含關鍵字，可用 `manual_overrides.json` 補正。





