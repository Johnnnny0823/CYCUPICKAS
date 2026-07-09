# AI 幫你監使用教學

這份文件給展示人員使用。照順序做即可，不需要理解程式架構。

## 一、你需要先確認的東西

1. 電腦有 Chrome。
2. 電腦有 Python。
3. 專案資料夾在：

```text
C:\Users\k9404\Desktop\未來問題AI幫你監\ai-course-watch
```

4. 課程資料放在：

```text
tools/raw/excel/課程資料.csv
```

目前專案已經有轉好的資料，可以直接展示。

## 二、最快展示方式

### 1. 開啟命令列

在專案資料夾空白處按右鍵，開啟 PowerShell，或在 PowerShell 執行：

```powershell
cd C:\Users\k9404\Desktop\未來問題AI幫你監\ai-course-watch
```

### 2. 啟動本機展示頁

```powershell
python -m http.server 8765
```

看到類似下面文字就不要關掉視窗：

```text
Serving HTTP on :: port 8765
```

### 3. 打開 Demo 頁

用 Chrome 開啟：

```text
http://localhost:8765/demo/fake_selection_system.html
```

這頁是仿中原選課頁，課程列表由本機全資管資料載入，摘要由 Extension 注入。

### 4. 載入 Chrome Extension

1. Chrome 打開：

```text
chrome://extensions/
```

2. 右上角打開「開發人員模式」。
3. 點「載入未封裝項目」。
4. 選擇：

```text
C:\Users\k9404\Desktop\未來問題AI幫你監\ai-course-watch\extension
```

5. 回到 Demo 頁，重新整理。
6. 課程列右側會出現「AI 幫你監」按鈕。
7. 點「AI 幫你監」展開摘要卡，再點一次收合。
8. 點「加入比較」可選 2 到 3 門課，右下會出現「比較清單」小按鈕；點開後以彈窗顯示比較表。
9. 點 AI 篩選可切換「沒報告」、「沒考試」、「沒作業」或「課綱已解析」的課。
8. 點「開啟課綱」會開新分頁到校方課綱頁；插件不會在課綱頁做任何摘要注入，只處理選課列表頁。
8. 點「開啟課綱」會在瀏覽器新分頁開啟校方 CoursePreview 課綱頁，不走會直接下載的 PDF action。

## 三、正式資料重跑流程

只有課程資料更新時才需要做這段。

### 1. 如果拿到的是 xls

目前最穩方式是用 Excel 開啟 `課程資料.xls`，另存成 CSV：

```text
tools/raw/excel/課程資料.csv
```

### 2. 轉成課程 seed

```powershell
python tools/excel_to_course_seed.py --input tools/raw/excel/課程資料.csv --year-term 1142 --output extension/data/course_seed.json
```

### 3. 驗證課綱 URL

```powershell
python tools/verify_syllabus_urls.py --input extension/data/course_seed.json --output tools/output/syllabus_url_check.json
```

成功時會看到：

```text
成功：7 筆；失敗：0 筆
```

### 4. 下載課綱 PDF 供本地解析

```powershell
python tools/fetch_syllabus_html.py --input extension/data/course_seed.json --check tools/output/syllabus_url_check.json --output-dir tools/raw/syllabus_html
```

下載後會出現在：

```text
tools/raw/syllabus_html/
```

### 5. 解析課綱 PDF 供摘要產生

```powershell
python tools/parse_syllabus_html.py --input-dir tools/raw/syllabus_html --output tools/output/syllabus_parsed.json
```

### 6. 產生 Extension 使用的摘要資料

```powershell
python tools/build_course_summaries.py --seed extension/data/course_seed.json --parsed tools/output/syllabus_parsed.json --overrides tools/manual_overrides.json --output extension/data/course_summaries.json
```

### 7. 檢查資料格式

```powershell
python tools/validate_course_summaries.py extension/data/course_summaries.json
```

看到下面文字代表可展示：

```text
course_summaries.json 驗證通過
```

若出現 `WARNING`，通常是評分比例加總不是 100，需要人工確認，但不會擋展示。

## 四、人工修正摘要

如果自動解析出來的摘要不順，改這個檔案：

```text
tools/manual_overrides.json
```

範例：

```json
{
  "MI373J": {
    "plainSummary": "本課以商業英語會話為主，訓練學生在商務情境中進行英文表達與互動。",
    "prerequisites": "建議具備基礎英文溝通能力。",
    "courseOutputs": ["課堂討論", "口頭報告", "期末評量"]
  }
}
```

改完後重跑：

```powershell
python tools/build_course_summaries.py --seed extension/data/course_seed.json --parsed tools/output/syllabus_parsed.json --overrides tools/manual_overrides.json --output extension/data/course_summaries.json
python tools/validate_course_summaries.py extension/data/course_summaries.json
```

再回 Chrome Demo 頁重新整理。

## 五、現場備援頁

如果 Chrome Extension 現場載入失敗，打開備援頁：

```text
http://localhost:8765/demo/integrated_backup.html
```

備援頁會直接顯示摘要卡。報告與口頭說明仍要說明主產品是 Chrome Extension。

## 六、常見問題

### 課綱頁仍看到「AI 幫你監」

1. 到 chrome://extensions/ 重新載入 Extension。
2. 關掉已開著的課綱分頁，再重新從 Demo 頁點「開啟課綱」。
3. 新版只處理本機 FAKE HTML Demo，課綱頁與 itouch 真實頁都不會再注入。

### 看不到「AI 幫你監」按鈕

1. 確認 Extension 有載入。
2. 確認網址是 `http://localhost:8765/demo/fake_selection_system.html`。
3. 重新整理頁面。
4. 到 `chrome://extensions/` 關掉再打開 Extension。

### PowerShell 顯示 port 被占用

改用另一個 port：

```powershell
python -m http.server 8766
```

然後打開：

```text
http://localhost:8766/demo/fake_selection_system.html
```

### 驗證出現 WARNING

例如：

```text
WARNING: MI373H grading 比例合計為 200，請人工確認
```

這代表 PDF 文字解析抓到重複比例。展示仍可用，但正式報告前建議用 `manual_overrides.json` 修正。

### 課綱頁打不開

先檢查 `tools/output/syllabus_url_check.json`，看該課程是否成功。若失敗，可能是課綱尚未開放或校方網站暫時無回應。若瀏覽器直接下載，通常是 Chrome 或校方伺服器的 PDF 處理設定，連結本身沒有加 `download`。

## 七、展示講法

可以照這段說：

```text
這個作品不是替代校方選課系統，也不登入帳號或讀取個資。它用 Chrome Extension 疊加在課程列表上，根據課程代碼讀取預先處理好的公開課綱摘要。學生點「AI 幫你監」後，可以直接看到課程內容、評分方式、先備知識與課程產出，減少逐一打開課綱比較的時間。
```






## 八、目前展示版本

目前只保留本機仿選課頁：

```text
http://localhost:8765/demo/fake_selection_system.html
```

這個版本的課程列表讀取：

```text
extension/data/course_seed_itouch.json
```

摘要資料讀取：

```text
extension/data/course_summaries.json
extension/data/course_summaries_itouch.json
```

`itouch` 真實課程查詢頁注入已停用。展示時不要開真實 itouch 頁面，所有課程都在本機 FAKE HTML Demo 中操作。


