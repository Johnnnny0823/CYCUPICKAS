# Architecture

## 系統架構

```text
課程資料 -> course_seed*.json -> URL 驗證 -> PDF/HTML 抓取 -> 規則解析 -> course_summaries*.json -> Chrome Extension -> 本機 Demo
```

## 資料流
資料先在本機工具處理，瀏覽器端只讀取 Extension 內的 JSON；目前展示集中在本機 FAKE HTML Demo。

## Chrome Extension 模組
`manifest.json` 宣告 MV3；`content.js` 掃描列與注入卡片；`styles.css` 控制樣式；`popup.*` 顯示狀態與重新掃描。

## 課程資料處理流程
`excel_to_course_seed.py` 讀取 CSV/XLSX/XLS，欄位容錯映射並產生課綱 URL。

## 課綱網址驗證流程
`verify_syllabus_urls.py` 對每筆課程發 GET，記錄 HTTP 狀態、關鍵字與成功失敗。

## 課綱 PDF/HTML 抓取流程
`fetch_syllabus_html.py` 只抓 reachable 課程，間隔至少 0.5 秒。

## 課綱解析流程
`parse_syllabus_html.py` 用 BeautifulSoup 與關鍵字解析摘要、評分、先備與產出。

## Demo 展示流程
`demo/fake_selection_system.html` 載入 `course_seed_itouch.json` 產生完整資管課表；Extension 只在本機 Demo 注入摘要，不再處理 itouch 真實頁。

## 備援方案
`demo/integrated_backup.html` 在 Extension 無法載入時直接顯示同一批摘要資料。


