# cycu_pick_assit（AI 幫你監）

中原大學選課輔助 Chrome Extension＋本機 demo。全域工作守則見 `~/.claude/CLAUDE.md`（自動載入）。

## 事實

- 主產品：`extension/`（Chrome 未封裝擴充功能）；展示頁：`demo/fake_selection_system.html`，用 `python -m http.server 8765` 起本機伺服器開啟。
- 資料管線：`tools/` 內的 Python 腳本，流程與指令見 `docs/USER_GUIDE.md` 第三節（CSV → course_seed → 課綱下載解析 → course_summaries）。
- 資料檔改動後必跑：`python tools/validate_course_summaries.py extension/data/course_summaries.json`，看到「驗證通過」才算完成。
- 摘要不對時改 `tools/manual_overrides.json`，不要直接改輸出 json，然後重跑：
  `python tools/build_course_summaries.py --seed extension/data/course_seed.json --parsed tools/output/syllabus_parsed.json --overrides tools/manual_overrides.json --output extension/data/course_summaries.json`
- 展示前另跑 `python tools/verify_demo_contract.py` 檢查 demo 相依資料完整。

## 注意

- `docs/USER_GUIDE.md` 有已知腐化：殘留別台電腦路徑 `C:\Users\k9404\...`（本機實際路徑是 `C:\Users\xnikz\OneDrive\桌面\cycu_pick_assit-main`）、第二節有重複的步驟編號 8。引用該文件的指令前先驗證路徑。
- itouch 真實頁注入已停用，展示一律用本機 fake 頁；不要「順手」重新啟用。
