let allCourses = [];
let currentGrade = 'all';

function escapeHtml(value) {
  const div = document.createElement('div');
  div.textContent = value == null ? '' : String(value);
  return div.innerHTML;
}

function foldText(text, limit = 24) {
  const value = String(text || '');
  if (value.length <= limit) return escapeHtml(value);
  return `<details class="note-fold"><summary>${escapeHtml(value.slice(0, limit))}...</summary><div>${escapeHtml(value)}</div></details>`;
}

function matchGrade(course) {
  if (currentGrade === 'all') return true;
  return String(course.className || '').includes(`資管${currentGrade}`);
}

function renderCourses() {
  const courses = allCourses.filter(matchGrade);
  const tbody = document.getElementById('courseRows');
  tbody.innerHTML = courses.map(course => `
    <tr data-course-code="${escapeHtml(course.courseCode)}">
      <td></td>
      <td><a href="${escapeHtml(course.previewUrl || course.syllabusUrl)}" target="_blank" rel="noopener noreferrer">課綱</a></td>
      <td>${escapeHtml(course.language || '')}</td>
      <td>${escapeHtml(course.courseCategory || '')}</td>
      <td>${escapeHtml(course.className || '')}</td>
      <td><div class="course-code">${escapeHtml(course.courseCode)}</div><div>${escapeHtml(course.courseName || '')}</div></td>
      <td>${escapeHtml(course.teacher || '')}</td>
      <td>${escapeHtml(course.timeText || '')}</td>
      <td>${escapeHtml(course.classroom || '')}</td>
      <td>0</td>
      <td>${escapeHtml(course.quota || '')}</td>
      <td class="note-cell">${foldText(course.note || '')}</td>
      <td>否</td>
    </tr>`).join('');
  document.getElementById('resultCount').textContent = courses.length;
}

fetch('../extension/data/course_seed_itouch.json').then(r => r.json()).then(courses => {
  allCourses = courses;
  renderCourses();
});

document.querySelectorAll('.grade-filter').forEach(button => {
  button.addEventListener('click', () => {
    currentGrade = button.dataset.grade;
    document.querySelectorAll('.grade-filter').forEach(item => item.classList.toggle('active', item === button));
    renderCourses();
  });
});

document.querySelector('.collapse-handle').addEventListener('click', () => {
  document.body.classList.toggle('sidebar-collapsed');
  document.querySelector('.collapse-handle').textContent = document.body.classList.contains('sidebar-collapsed') ? '❯❯' : '❮❮';
});
