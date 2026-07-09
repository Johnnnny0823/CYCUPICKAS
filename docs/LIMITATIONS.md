# Limitations

- 目前課綱 URL 可能 HTTP 可讀但不含可解析課綱關鍵字。
- 同一課程代碼若在 Excel 出現多列，摘要資料以課程代碼共用。
- 舊版 `.xls` 在 Python 缺少 `xlrd` 時需用 Excel 另存 CSV。
- 自動摘要只使用本地規則，效果不足時請用 `manual_overrides.json` 修正。

