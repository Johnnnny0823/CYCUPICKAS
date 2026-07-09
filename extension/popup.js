fetch(chrome.runtime.getURL('data/course_summaries.json')).then(r => r.json()).then(data => {
  document.getElementById('term').textContent = data.metadata?.yearTerm || '1142';
  document.getElementById('count').textContent = Object.keys(data.courses || {}).length;
}).catch(() => document.getElementById('count').textContent = '無法讀取');

document.getElementById('rescan').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  if (tab?.id) chrome.tabs.sendMessage(tab.id, {type: 'AIWATCH_RESCAN'});
});

function renderKeyStatus(hasKey) {
  const el = document.getElementById('keyStatus');
  el.textContent = hasKey ? '狀態：已設定' : '狀態：尚未設定，AI 選課建議無法使用';
  el.className = hasKey ? 'row status-ok' : 'row status-missing';
}

chrome.runtime.sendMessage({type: 'AIWATCH_GET_API_KEY_STATUS'}).then(res => renderKeyStatus(res?.hasKey));

document.getElementById('saveKey').addEventListener('click', async () => {
  const apiKey = document.getElementById('apiKeyInput').value.trim();
  await chrome.runtime.sendMessage({type: 'AIWATCH_SET_API_KEY', apiKey});
  document.getElementById('apiKeyInput').value = '';
  renderKeyStatus(Boolean(apiKey));
});
