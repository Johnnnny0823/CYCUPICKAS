# AI 幫你監完整驗證計畫

## 目標

確認本機 FAKE HTML Demo 可以完整展示：課程載入、AI 摘要卡、評分方式、先備知識、比較功能、AI 篩選、課綱新分頁，以及文件與實作一致。

目前驗證範圍只包含：

```text
http://localhost:8765/demo/fake_selection_system.html
```

不驗證真實 itouch 頁面，因為新版已停用真實頁注入。

## 目前狀態

已通過自動檢查：`npm run verify-demo`、JS 語法檢查、`manifest.json` JSON 檢查、單元測試、摘要資料驗證。

尚未完成：第三節的手動 Chrome 擴充功能驗證。`@chrome` 與 `@電腦` plugin 目前會遇到 `sandboxPolicy` 工具層錯誤，headless Chrome 也不能可靠證明 unpacked extension 已注入頁面；因此完整驗證不能標記為通過。

## 一、環境準備

在 PowerShell 執行：

```powershell
cd C:\Users\k9404\Desktop\未來問題AI幫你監\ai-course-watch
python -m http.server 8765
```

用 Chrome 開啟：

```text
http://localhost:8765/demo/fake_selection_system.html
```

到 Chrome 擴充功能頁：

```text
chrome://extensions/
```

確認：

1. 開發人員模式已開啟。
2. 已載入 `extension/`。
3. Extension 版本為 `1.1.2`。
4. 修改檔案後有按「重新載入」。

## 二、自動驗證

### 1. Demo 合約驗證

```powershell
npm run verify-demo
```

通過標準：

- `seed_rows` 是 58。
- `summary_matches` 是 58。
- 大一、大二、大三、大四都有課。
- `manifest_matches` 只包含：

```text
http://localhost:*/*
http://127.0.0.1:*/*
file:///*
```

### 2. JS 語法驗證

```powershell
node --check extension\content.js
node --check demo\fake_selection_system.js
```

通過標準：沒有輸出錯誤。

### 3. Manifest 驗證

```powershell
python -m json.tool extension\manifest.json
```

通過標準：可以正常輸出 JSON。

### 4. 單元測試

```powershell
python -m unittest discover -s tests
```

通過標準：顯示 `OK`。

### 5. 摘要資料驗證

```powershell
python tools\validate_course_summaries.py extension\data\course_summaries_itouch.json
```

通過標準：最後顯示：

```text
course_summaries.json 驗證通過
```

若出現 `WARNING: ... grading 比例合計為 ...`，代表評分表格可能需要人工確認，但不阻擋展示。

## 三、手動 Chrome 功能驗證

### 1. 課程列表載入

操作：打開 Demo 頁。

通過標準：

- 頁面上方顯示「目前 58 門」。
- 表格中有資管一、資管二、資管三、資管四課程。
- 備註長文字可以折疊，不會把表格撐爆。

### 2. 年級篩選

操作：依序點：

```text
全部 / 大一 / 大二 / 大三 / 大四
```

通過標準：

- `全部` 顯示 58 門。
- `大一` 顯示 15 門。
- `大二` 顯示 16 門。
- `大三` 顯示 20 門。
- `大四` 顯示 7 門。
- 表格不水平爆版。

### 3. AI 摘要卡

操作：點任一課程右側 `AI 幫你監`。

通過標準：

- 摘要卡展開。
- 再點一次可以收合。
- 卡片包含：
  - 這堂課在幹嘛
  - 評分方式
  - 先備知識
  - 課程產出
  - 資料來源狀態
  - 開啟課綱
  - 補充搜尋

### 4. 評分方式

操作：展開有摘要的課程。

通過標準：

- 評分方式以表格呈現。
- 左欄是評分項目。
- 右欄是比例或課綱原文。
- 表格文字會換行，不撐開整頁。

### 5. 比較功能

操作：

1. 點 2 到 3 門課的 `加入比較`。
2. 點右下角 `比較清單 n/3`。

通過標準：

- 右下只出現小按鈕，不直接佔住畫面。
- 點開後出現置中的比較彈窗。
- 比較表包含：
  - 課名
  - 教師
  - 時間
  - 評分方式
  - 先備知識
  - 課程產出
- 長文字可折疊或換行。
- `清除` 可以清空比較清單。
- `關閉` 可以關閉彈窗。
- 超過 3 門時會阻擋。

### 6. AI 篩選

操作：依序點：

```text
全部 / 沒報告 / 沒考試 / 沒作業
```

通過標準：

- 點擊後表格列會更新。
- 被篩掉的課程不顯示。
- 已展開的摘要列會自動收起。
- 篩選按鈕 active 狀態明顯。

### 7. 開啟課綱

操作：在摘要卡點 `開啟課綱`，或表格中點 `課綱`。

通過標準：

- 會開新分頁。
- URL 格式為：

```text
https://cmap.cycu.edu.tw:8443/Syllabus/CoursePreview.html?yearTerm=1142&opCode=課程代碼
```

- 新分頁不會出現 `AI 幫你監` 注入卡片。

### 8. 補充搜尋

操作：在摘要卡點 `補充搜尋`。

通過標準：

- 開新分頁到 Google 搜尋。
- 關鍵字包含：

```text
中原大學 課名 老師 評價 Dcard 歐趴糖
```

- 系統沒有自行蒐集或呈現外部評論。

### 9. 側欄收合

操作：點左側收合按鈕。

通過標準：

- 左側欄位可收合。
- 主表格可用寬度增加。
- 再點一次可展開。

## 四、文件一致性驗證

執行：

```powershell
rg -n --glob "!docs/VERIFICATION_PLAN.md" "5173|5174|版本 B|courseQuery|有報告、有考試、有作業|畫面下方會出現比較表|授權網域" README.md docs package.json extension\manifest.json
```

通過標準：沒有輸出。

允許保留的文字：

```text
itouch 真實課程查詢頁注入已停用
```

## 五、失敗處理

### 看不到 AI 幫你監

1. 到 `chrome://extensions/` 重新載入 Extension。
2. 重新整理 Demo 頁。
3. 確認網址是 `http://localhost:8765/demo/fake_selection_system.html`。
4. 執行 `npm run verify-demo`。

### 課程沒有 58 門

1. 確認本機伺服器從專案根目錄啟動。
2. 確認 `demo/fake_selection_system.js` 讀取：

```text
../extension/data/course_seed_itouch.json
```

3. 執行 `npm run verify-demo`。

### 摘要找不到

1. 確認 `extension/data/course_summaries_itouch.json` 存在。
2. 執行：

```powershell
python tools\validate_course_summaries.py extension\data\course_summaries_itouch.json
```

3. 若某課真的沒有摘要，加入資料後重跑資料處理流程。

### Port 被占用

改用：

```powershell
python -m http.server 8766
```

並開啟：

```text
http://localhost:8766/demo/fake_selection_system.html
```

## 六、展示前最小 Checklist

展示前只要跑這些：

```powershell
npm run verify-demo
python -m unittest discover -s tests
python -m http.server 8765
```

Chrome 手動確認：

- Demo 頁有 58 門。
- `AI 幫你監` 可展開。
- `加入比較` 可開比較彈窗。
- `沒報告 / 沒考試 / 沒作業` 可篩選。
- 課綱開新分頁且不注入摘要。

## 七、目前自動化限制

`@chrome` 與 `@電腦` plugin 在目前 Codex session 會失敗：

```text
Mcp error: -32602: js: codex/sandbox-state-meta: missing field sandboxPolicy
```

因此目前真瀏覽器點擊驗證需要手動執行。若新開 Codex thread 或重啟 Codex Desktop 後 plugin 恢復，可再補截圖式驗證。
