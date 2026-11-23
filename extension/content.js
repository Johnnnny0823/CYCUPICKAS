let aiwatchSummaries = null;
const aiwatchCompare = new Map();

function isDemoCoursePage() {
  return location.pathname.endsWith('/fake_selection_system.html');
}

function shouldProcessPage() {
  return isDemoCoursePage();
}

async function loadCourseSummaries() {
  if (aiwatchSummaries) return aiwatchSummaries;
  const files = ['data/course_summaries.json', 'data/course_summaries_itouch.json'];
  const loaded = await Promise.all(
    files.map(file => fetch(chrome.runtime.getURL(file)).then(response => response.json()).catch(() => ({courses: {}})))
  );
  aiwatchSummaries = {
    metadata: loaded[loaded.length - 1]?.metadata || loaded[0]?.metadata || {},
    courses: Object.assign({}, ...loaded.map(data => data.courses || {})),
  };
  return aiwatchSummaries;
}

function normalizeCourseCode(value) {
  return String(value || '').trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
}

function findCourseRows() {
  return Array.from(document.querySelectorAll('tr[data-course-code]')).filter(row => !row.classList.contains('aiwatch-summary-row'));
}

function extractCourseCodeFromRow(row) {
  return normalizeCourseCode(row.getAttribute('data-course-code'));
}

function matchCourseSummary(courseCode, summaries) {
  return summaries?.courses?.[normalizeCourseCode(courseCode)] || null;
}

function buildPreviewUrl(courseCode) {
  return `https://cmap.cycu.edu.tw:8443/Syllabus/CoursePreview.html?yearTerm=1142&opCode=${encodeURIComponent(courseCode)}`;
}

function syllabusLink(summary) {
  for (const candidate of [summary.previewUrl, summary.syllabusUrl]) {
    if (typeof candidate !== 'string') continue;
    try {
      const url = new URL(candidate);
      if (url.origin === 'https://cmap.cycu.edu.tw:8443' && !url.username && !url.password) {
        return url.href;
      }
    } catch {
      // Fall back to the official course preview.
    }
  }
  return buildPreviewUrl(summary.courseCode);
}

function fallbackSummaryFromRow(courseCode, row) {
  const nameCell = row.children[5];
  return {
    courseCode,
    courseName: nameCell?.textContent?.replace(courseCode, '').trim() || courseCode,
    teacher: row.children[6]?.textContent?.trim() || '',
    timeText: row.children[7]?.textContent?.trim() || '',
    classroom: row.children[8]?.textContent?.trim() || '',
    yearTerm: '1142',
    previewUrl: buildPreviewUrl(courseCode),
    plainSummary: '這門課目前不在本機摘要資料庫中。可先開啟課綱確認內容；若要顯示完整摘要，請將此課加入 Excel 後重跑資料處理流程。',
    grading: [],
    gradingMessage: '目前沒有本地預處理後的評分表格。',
    prerequisites: '尚未納入本機課綱資料庫。',
    courseOutputs: [],
    parseStatus: 'missing',
    manualReviewed: false,
    fallbackOnly: true,
  };
}

function createAiWatchButton(courseCode) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'aiwatch-button';
  button.textContent = 'AI 幫你監';
  button.dataset.courseCode = courseCode;
  return button;
}

function createCompareButton(courseCode, summary) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'aiwatch-compare-button';
  button.textContent = '加入比較';
  button.disabled = !summary;
  button.addEventListener('click', () => toggleCompare(courseCode, summary));
  return button;
}

function createSummaryCard(summary) {
  const card = document.createElement('div');
  card.className = 'aiwatch-card';
  const gradingRows = (summary.grading || [])
    .map(item => `<tr><td>${escapeHtml(item.item || item.rawText || '')}</td><td>${item.percent == null ? '依課綱原文' : escapeHtml(item.percent + '%')}</td></tr>`)
    .join('');
  const outputs = (summary.courseOutputs || []).map(item => `<span class="aiwatch-chip">${escapeHtml(item)}</span>`).join('');
  const openUrl = syllabusLink(summary);
  card.innerHTML = `
    <div class="aiwatch-card-header">
      <div><div class="aiwatch-kicker">AI 幫你監</div><div class="aiwatch-title">${escapeHtml(summary.courseName || summary.courseCode)}</div></div>
      <div class="aiwatch-meta">${escapeHtml(summary.teacher || '')}</div>
    </div>
    <section class="aiwatch-modern-section aiwatch-summary-block"><h4>這堂課在幹嘛</h4><p>${escapeHtml(summary.plainSummary || '課綱尚未成功解析。')}</p></section>
    <div class="aiwatch-grid">
      <section class="aiwatch-modern-section"><h4>評分方式</h4>${gradingRows ? `<table class="aiwatch-grading-table"><tbody>${gradingRows}</tbody></table>` : `<p>${escapeHtml(summary.gradingMessage || '課綱頁面未成功解析到評分表格。')}</p>`}</section>
      <section class="aiwatch-modern-section"><h4>先備知識</h4><p>${escapeHtml(displayPrerequisites(summary))}</p>${outputs ? `<h4 class="aiwatch-output-title">課程產出</h4><div class="aiwatch-chips">${outputs}</div>` : ''}</section>
    </div>
    <div class="aiwatch-status">${summary.fallbackOnly ? '資料狀態：此課尚未納入本機摘要資料庫｜可開啟課綱人工確認' : `資料來源：${escapeHtml(summary.yearTerm || '1142')} 課綱頁面｜課綱狀態：可讀取｜已完成本地預處理`}</div>
    <div class="aiwatch-links"><a class="aiwatch-link-button" target="_blank" rel="noopener noreferrer" href="${escapeHtml(openUrl)}">開啟課綱</a><a class="aiwatch-muted-link" target="_blank" rel="noopener noreferrer" href="${buildGoogleSearchUrl(summary.courseName, summary.teacher)}">補充搜尋</a></div>
  `;
  return card;
}

function injectButtonAndCard(row, button, compareButton, card) {
  if (row.dataset.aiwatchInjected === 'true') return;
  row.dataset.aiwatchInjected = 'true';
  const actionCell = row.insertCell(-1);
  actionCell.className = 'aiwatch-action-cell';
  actionCell.append(button, compareButton);
  const detailRow = document.createElement('tr');
  detailRow.className = 'aiwatch-summary-row';
  detailRow.hidden = true;
  const detailCell = document.createElement('td');
  detailCell.colSpan = row.children.length;
  detailCell.appendChild(card);
  detailRow.appendChild(detailCell);
  row.after(detailRow);
  button.addEventListener('click', () => {
    detailRow.hidden = !detailRow.hidden;
    button.classList.toggle('is-open', !detailRow.hidden);
  });
}

function toggleCompare(courseCode, summary) {
  if (aiwatchCompare.has(courseCode)) {
    aiwatchCompare.delete(courseCode);
  } else {
    if (aiwatchCompare.size >= 3) return alert('最多比較 3 門課。');
    aiwatchCompare.set(courseCode, summary);
  }
  refreshCompareButtons();
  renderCompareLauncher();
}

function refreshCompareButtons() {
  document.querySelectorAll('.aiwatch-compare-button').forEach(button => {
    const code = button.closest('tr')?.dataset.courseCode;
    const selected = aiwatchCompare.has(code);
    button.classList.toggle('is-selected', selected);
    button.textContent = selected ? '已加入' : '加入比較';
  });
}

function gradingText(summary) {
  return (summary.grading || [])
    .map(item => (item.item || item.rawText || '') + (item.percent == null ? '' : ' ' + item.percent + '%'))
    .join('\n') || '未解析';
}

function displayPrerequisites(summary) {
  const value = String(summary?.prerequisites || '').trim();
  if (!value || value.includes('未列明') || value.includes('未明確')) return '課綱未列明，建議依課名與教師要求確認。';
  return value;
}

function displayCourseTime(course) {
  const fixed = [course.timeText, course.classroom].filter(Boolean).join(' / ');
  if (fixed) return fixed;
  const note = (course.note || '') + ' ' + (course.courseName || '');
  if (note.includes('非同步遠距')) return '非同步遠距 / 無固定實體時段';
  if (note.includes('企業實習') || note.includes('依實習單位指定')) return '依實習單位指定';
  if (note.includes('專題課程') || note.includes('指導老師')) return '依指導老師排定';
  return '未列明';
}

function compareRows() {
  const courses = Array.from(aiwatchCompare.values());
  return [
    ['課名', ...courses.map(course => course.courseName || course.courseCode)],
    ['教師', ...courses.map(course => course.teacher || '')],
    ['時間', ...courses.map(displayCourseTime)],
    ['評分方式', ...courses.map(gradingText)],
    ['先備知識', ...courses.map(displayPrerequisites)],
    ['課程產出', ...courses.map(course => (course.courseOutputs || []).join('、') || '未列明')],
  ];
}

function renderCompareLauncher() {
  document.querySelector('.aiwatch-compare-launcher')?.remove();
  document.querySelector('.aiwatch-compare-modal')?.remove();
  if (!aiwatchCompare.size) return;
  const launcher = document.createElement('button');
  launcher.type = 'button';
  launcher.className = 'aiwatch-compare-launcher';
  launcher.textContent = `比較清單 ${aiwatchCompare.size}/3`;
  launcher.addEventListener('click', openCompareModal);
  document.body.appendChild(launcher);
}

function renderCompareCell(label, cell) {
  const value = escapeHtml(cell);
  return label === '評分方式' ? '<div class="aiwatch-compare-grading">' + value + '</div>' : value;
}

function openCompareModal() {
  document.querySelector('.aiwatch-compare-modal')?.remove();
  const modal = document.createElement('section');
  modal.className = 'aiwatch-compare-modal';
  modal.innerHTML = `
    <div class="aiwatch-compare-dialog">
      <div class="aiwatch-compare-head"><div><strong>課程比較</strong><span>已選 ${aiwatchCompare.size}/3 門</span></div><div><button type="button" class="aiwatch-clear-compare">清除</button><button type="button" class="aiwatch-close-compare">關閉</button></div></div>
      <div class="aiwatch-compare-scroll"><table>${compareRows().map(row => `<tr>${row.map((cell, index) => `<${index ? 'td' : 'th'}>${index ? renderCompareCell(row[0], cell) : escapeHtml(cell)}</${index ? 'td' : 'th'}>`).join('')}</tr>`).join('')}</table></div>
    </div>
  `;
  modal.querySelector('.aiwatch-close-compare').addEventListener('click', () => modal.remove());
  modal.querySelector('.aiwatch-clear-compare').addEventListener('click', () => {
    aiwatchCompare.clear();
    refreshCompareButtons();
    renderCompareLauncher();
  });
  modal.addEventListener('click', event => {
    if (event.target === modal) modal.remove();
  });
  document.body.appendChild(modal);
}

function ensureFilterBar(summaries) {
  if (document.querySelector('.aiwatch-filterbar')) return;
  const table = document.querySelector('tr[data-course-code]')?.closest('table');
  if (!table) return;
  const bar = document.createElement('div');
  bar.className = 'aiwatch-filterbar';
  bar.innerHTML = '<b>AI 篩選</b><button class="is-active" data-filter="all">全部</button><button data-filter="no-report">沒報告</button><button data-filter="no-exam">沒考試</button><button data-filter="no-homework">沒作業</button>';
  bar.addEventListener('click', event => {
    const filter = event.target.dataset.filter;
    if (!filter) return;
    bar.querySelectorAll('button').forEach(button => button.classList.toggle('is-active', button.dataset.filter === filter));
    applyFilter(filter, summaries);
  });
  table.before(bar);
}

function summaryMatchesFilter(summary, filter) {
  if (filter === 'all') return true;
  if (!summary || summary.fallbackOnly) return false;
  const text = `${gradingText(summary)} ${(summary.courseOutputs || []).join('、')}`;
  if (filter === 'no-report') return !text.includes('報告');
  if (filter === 'no-exam') return !(text.includes('考') || text.includes('測驗'));
  if (filter === 'no-homework') return !text.includes('作業');
  return true;
}

function applyFilter(filter, summaries) {
  for (const row of findCourseRows()) {
    const code = extractCourseCodeFromRow(row);
    const summary = matchCourseSummary(code, summaries) || fallbackSummaryFromRow(code, row);
    const show = summaryMatchesFilter(summary, filter);
    row.hidden = !show;
    if (row.nextElementSibling?.classList.contains('aiwatch-summary-row')) row.nextElementSibling.hidden = true;
  }
}

function buildGoogleSearchUrl(courseName, teacher) {
  const query = `中原大學 ${courseName || ''} ${teacher || ''} 評價 Dcard 歐趴糖`;
  return `https://www.google.com/search?q=${encodeURIComponent(query)}`;
}

function observePageChanges() {
  let timer = null;
  new MutationObserver(() => {
    clearTimeout(timer);
    timer = setTimeout(scanAndInject, 200);
  }).observe(document.body, {childList: true, subtree: true});
}

function escapeHtml(value) {
  const div = document.createElement('div');
  div.textContent = value == null ? '' : String(value);
  return div.innerHTML;
}

async function scanAndInject() {
  if (!shouldProcessPage()) return;
  const summaries = await loadCourseSummaries();
  ensureFilterBar(summaries);
  for (const row of findCourseRows()) {
    const code = extractCourseCodeFromRow(row);
    if (!code) continue;
    const summary = matchCourseSummary(code, summaries) || fallbackSummaryFromRow(code, row);
    injectButtonAndCard(row, createAiWatchButton(code), createCompareButton(code, summary), createSummaryCard(summary));
  }
}

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === 'AIWATCH_RESCAN') scanAndInject();
});

if (shouldProcessPage()) {
  scanAndInject().catch(error => console.error('AI 幫你監載入失敗', error));
  observePageChanges();
}
