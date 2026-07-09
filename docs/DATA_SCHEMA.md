# Data Schema

## course_seed.json
陣列。每筆包含 `courseCode`, `opCode`, `courseName`, `teacher`, `credits`, `timeText`, `classroom`, `department`, `courseCategory`, `className`, `requiredOrElective`, `language`, `quota`, `note`, `yearTerm`, `syllabusUrl`。`courseCode` 用於列表比對，`opCode` 目前等於課程代碼並用於課綱 PDF URL 參數；缺值保留空字串。

## syllabus_url_check.json
包含 `checkedAt`, `yearTerm`, `total`, `success`, `failed`, `results`。每個 result 記錄 URL、HTTP 狀態、是否 reachable、是否有 useful content、命中的課綱關鍵字與訊息。

## syllabus_parsed.json
以課程代碼為 key。欄位包含 `plainSummary`, `grading`, `gradingStatus`, `gradingMessage`, `prerequisites`, `courseOutputs`, `parseStatus`。

## course_summaries.json
Extension 使用的正式資料。包含 `metadata` 與 `courses`。`courses` 以課程代碼為 key，合併 seed、parsed 與人工覆蓋。

## manual_overrides.json
以課程代碼為 key，只填需要覆蓋的欄位。存在覆蓋時 `manualReviewed` 為 true。

## 缺值處理
缺少摘要時顯示尚未解析；缺少先備時顯示「課綱未明確要求。」；評分找不到時 `grading` 為空陣列。

## 錯誤狀態
URL 無法取得或無關鍵字時寫入 `syllabus_url_check.json`，流程不中斷。


