const GEMINI_MODEL = 'gemini-2.5-flash';
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

const ADVISOR_RESPONSE_SCHEMA = {
  type: 'object',
  properties: {
    conflicts: {
      type: 'array',
      items: { type: 'string' },
      description: '時間衝堂的課程配對描述，例如「資訊管理 與 軟體專案管理 週三第6-8節衝堂」；沒有衝堂就回傳空陣列',
    },
    creditTotal: { type: 'integer', description: '目前已選課程學分總和' },
    contentOverlap: {
      type: 'array',
      items: { type: 'string' },
      description: '根據課綱摘要、先備知識、課程產出判斷內容重疊或高度相關的課程配對，例如「資料庫管理 與 系統分析與設計 都涵蓋資料建模，內容有重疊」；沒有明顯重疊就回傳空陣列',
    },
    workloadWarning: { type: 'string', description: '綜合各課精力等級、評分方式、課程產出，判斷重要評量（期中/期末報告、專題、考試）是否集中在同一時期造成負荷過重；若不確定就回傳空字串，不要臆測' },
    priorityOrder: {
      type: 'array',
      items: { type: 'string' },
      description: '若時間或精力有限，依課綱內容判斷這些課的優先順序建議，只列課名，最值得先修或最該保留的排前面',
    },
    advice: { type: 'string', description: '給學生的整體選課建議，150字以內，需引用課綱內容（如評分方式、精力等級、課程產出）具體說明理由，不要空泛的話' },
  },
  required: ['conflicts', 'creditTotal', 'contentOverlap', 'workloadWarning', 'priorityOrder', 'advice'],
};

function buildPrompt(courses) {
  const lines = courses.map((c, i) => {
    const grading = (c.grading || []).map(g => `${g.item}${g.percent != null ? g.percent + '%' : ''}`).join('、') || '未知';
    const outputs = (c.courseOutputs || []).join('、') || '未列';
    return `${i + 1}. ${c.courseName}（${c.courseCode}）
   教師：${c.teacher || '未列'}｜學分：${c.credits || '未知'}｜時間：${c.timeText || '未列'}
   精力等級：${c.effortLevel || '未知'}（${c.effortReason || '無說明'}）
   評分方式：${grading}
   課程產出：${outputs}
   先備知識：${c.prerequisites || '未列'}
   課綱摘要：${c.plainSummary || '無摘要'}`;
  }).join('\n\n');
  return `你是大學選課顧問，以下是一個學生目前已選或正在考慮的課程清單（含課綱語義分析結果），請根據課綱實際內容（不只是時間表）幫他做深度選課分析。

課程清單：
${lines}

規則：
- conflicts 只根據「時間」欄位判斷是否有星期與節次重疊，時間格式是「星期-節次」，例如 3-678 代表週三第6、7、8節。
- contentOverlap 要根據課綱摘要、先備知識、課程產出判斷課程內容是否重疊或高度相關，不要只看課名字面相似。
- workloadWarning 綜合精力等級、評分方式、課程產出，判斷重要評量是否集中在同一時期；沒有明顯風險就回傳空字串，不要臆測課綱沒提到的資訊。
- priorityOrder 依課綱內容（如必修/選修性質、精力負荷、產出類型）給修課優先順序建議。
- advice 必須具體引用課綱內容作為理由，不要空泛的話。
- 只根據提供的課綱資料判斷，不要編造課綱沒提到的資訊。`;
}

async function getApiKey() {
  const stored = await chrome.storage.local.get('geminiApiKey');
  return stored.geminiApiKey || '';
}

async function callGemini(prompt, apiKey) {
  const response = await fetch(`${GEMINI_URL}?key=${encodeURIComponent(apiKey)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        responseMimeType: 'application/json',
        responseSchema: ADVISOR_RESPONSE_SCHEMA,
      },
    }),
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Gemini API 錯誤（${response.status}）：${errorText.slice(0, 300)}`);
  }
  const payload = await response.json();
  const text = payload?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('Gemini 回應格式異常，缺少內容');
  return JSON.parse(text);
}

async function getAdvice(courses) {
  const apiKey = await getApiKey();
  if (!apiKey) {
    return { error: 'missing_api_key' };
  }
  if (!courses || courses.length < 2) {
    return { error: 'not_enough_courses' };
  }
  try {
    const result = await callGemini(buildPrompt(courses), apiKey);
    return { data: result };
  } catch (error) {
    return { error: 'api_error', message: String(error?.message || error) };
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'AIWATCH_GET_ADVICE') {
    getAdvice(message.courses).then(sendResponse);
    return true;
  }
  if (message?.type === 'AIWATCH_SET_API_KEY') {
    chrome.storage.local.set({ geminiApiKey: message.apiKey || '' }).then(() => sendResponse({ ok: true }));
    return true;
  }
  if (message?.type === 'AIWATCH_GET_API_KEY_STATUS') {
    getApiKey().then(key => sendResponse({ hasKey: Boolean(key) }));
    return true;
  }
});
