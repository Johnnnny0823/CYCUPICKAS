fetch(chrome.runtime.getURL('data/course_summaries.json')).then(r => r.json()).then(data => {
  document.getElementById('term').textContent = data.metadata?.yearTerm || '1142';
  document.getElementById('count').textContent = Object.keys(data.courses || {}).length;
}).catch(() => document.getElementById('count').textContent = '無法讀取');

document.getElementById('rescan').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  if (tab?.id) chrome.tabs.sendMessage(tab.id, {type: 'AIWATCH_RESCAN'});
});
