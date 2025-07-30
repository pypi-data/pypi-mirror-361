// ==================================================================================
// Theme Handling
// ==================================================================================
function initThemeToggle() {
  const themeToggleBtn = document.getElementById('theme-toggle');
  const darkIcon = document.getElementById('dark-icon');
  const lightIcon = document.getElementById('light-icon');

  function applyTheme(theme) {
    // Set both data-theme (for our CSS) and data-bs-theme (for Bootstrap 5)
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-bs-theme', theme);
    
    const isDark = theme === 'dark';

    // Update icons
    darkIcon.classList.toggle('d-none', isDark);
    lightIcon.classList.toggle('d-none', !isDark);

    // Update body classes
    document.body.classList.toggle('theme-dark', isDark);
    document.body.classList.toggle('theme-light', !isDark);
    
    // Apply dark mode to calendar container
    const calendarContainer = document.querySelector('.calendar-container');
    if (calendarContainer) {
      calendarContainer.classList.toggle('bg-white', !isDark);
      calendarContainer.classList.toggle('bg-dark', isDark);
    }

    // Update loading overlay
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
      loadingOverlay.style.backgroundColor = isDark ? 'rgba(26, 27, 38, 0.8)' : 'rgba(255, 255, 255, 0.8)';
    }

    // Apply dark mode to no-due-date-list
    const noDueDateList = document.getElementById('no-due-date-list');
    if (noDueDateList) {
      noDueDateList.classList.toggle('bg-white', !isDark);
      noDueDateList.classList.toggle('bg-dark', isDark);
    }
    
    // FullCalendar should automatically pick up theme changes
    if (calendar) {
      calendar.render(); // Re-render to ensure all elements update
    }
  }

  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
  applyTheme(initialTheme);

  themeToggleBtn.addEventListener('click', () => {
    const newTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  });
}

// ==================================================================================
// Global State & App Initialization
// ==================================================================================
let calendar;

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initCalendar();
  initApp();
});

function initCalendar() {
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) {
    console.error('Calendar element not found!');
    return;
  }
  calendar = new FullCalendar.Calendar(calendarEl, {
    themeSystem: 'bootstrap5',
    initialView: 'dayGridMonth',
    height: '100%',
    expandRows: true,
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,listMonth'
    },
    eventClick: handleEventClick,
  });
  calendar.render();
}

async function initApp() {
  try {
    showLoading(true);
    const [teams, projects] = await Promise.all([fetchData('/api/teams'), fetchData('/api/projects')]);

    populateDropdown('team-filter', teams, 'All Teams');
    populateDropdown('project-filter', projects, null, true);

    if (teams.length > 0) {
      const states = await fetchData(`/api/states?teamId=${teams[0].id}`);
      populateDropdown('state-filter', states, 'All States');
    }

    await fetchEvents();
    setupEventListeners();
  } catch (error) {
    showError('Failed to initialize application', error);
  } finally {
    showLoading(false);
  }
}

// ==================================================================================
// Data Fetching & UI Population
// ==================================================================================
async function fetchData(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(`API request to ${url} failed: ${JSON.stringify(errorData)}`);
  }
  return response.json();
}

function populateDropdown(elementId, items, defaultOptionText, isMultiSelect = false) {
  const selectEl = document.getElementById(elementId);
  selectEl.innerHTML = '';

  if (!isMultiSelect && defaultOptionText) {
    selectEl.add(new Option(defaultOptionText, 'all'));
  }

  items.forEach(item => {
    selectEl.add(new Option(item.name, item.id));
  });
}

async function fetchEvents() {
  try {
    showLoading(true);
    const params = new URLSearchParams();
    
    const teamId = document.getElementById('team-filter').value;
    if (teamId !== 'all') params.append('teamId', teamId);

    const stateId = document.getElementById('state-filter').value;
    if (stateId !== 'all') params.append('stateId', stateId);

    const selectedProjects = [...document.getElementById('project-filter').selectedOptions].map(opt => opt.value);
    selectedProjects.forEach(id => params.append('projectId', id));

    const isNoDueDateChecked = document.getElementById('no-due-date-toggle').checked;
    if (isNoDueDateChecked) {
      params.append('noDueDate', 'true');
    }

    const issues = await fetchData(`/api/issues?${params.toString()}`);

    if (isNoDueDateChecked) {
      displayNoDueDateIssues(issues);
    } else {
      const events = issues.map(issue => ({
        id: issue.id,
        title: issue.title,
        start: issue.dueDate,
        allDay: true,
        backgroundColor: issue.state.color,
        borderColor: issue.state.color,
        textColor: getContrastColor(issue.state.color),
        extendedProps: issue
      }));
      calendar.removeAllEvents();
      calendar.addEventSource(events);
    }
  } catch (error) {
    showError('Failed to fetch issues', error);
  } finally {
    showLoading(false);
  }
}

// ==================================================================================
// Event Listeners & Handlers
// ==================================================================================
function setupEventListeners() {
  const issueDetailsOffcanvas = new bootstrap.Offcanvas(document.getElementById('issueDetailsOffcanvas'));
  window.issueDetailsOffcanvas = issueDetailsOffcanvas;

  document.getElementById('team-filter').addEventListener('change', async () => {
    const teamId = document.getElementById('team-filter').value;
    const stateFilterEl = document.getElementById('state-filter');
    if (teamId && teamId !== 'all') {
      const states = await fetchData(`/api/states?teamId=${teamId}`);
      populateDropdown('state-filter', states, 'All States');
    } else {
      populateDropdown('state-filter', [], 'All States');
    }
    fetchEvents();
  });

  document.getElementById('project-filter').addEventListener('change', fetchEvents);
  document.getElementById('state-filter').addEventListener('change', fetchEvents);

  document.getElementById('no-due-date-toggle').addEventListener('change', () => {
    const isNoDueDateChecked = document.getElementById('no-due-date-toggle').checked;
    switchView(isNoDueDateChecked);
    fetchEvents();
  });
  document.getElementById('close-sidebar').addEventListener('click', () => issueDetailsOffcanvas.hide());
}

function handleEventClick({ event }) {
  const props = event.extendedProps;
  document.getElementById('issue-title').textContent = event.title;
  document.getElementById('issue-description').innerHTML = props.description ? props.description.replace(/\n/g, '<br>') : '<em>No description</em>';
  document.getElementById('issue-team').textContent = props.team.name;
  
  const stateEl = document.getElementById('issue-state');
  stateEl.textContent = props.state.name;
  stateEl.style.backgroundColor = props.state.color;
  stateEl.style.color = getContrastColor(props.state.color);

  document.getElementById('issue-assignee').innerHTML = props.assignee ? `<i class="bi bi-person"></i> ${props.assignee.name}` : '<i>Unassigned</i>';
  
  const labelsContainer = document.getElementById('issue-labels');
  labelsContainer.innerHTML = '';
  if (props.labels && props.labels.length > 0) {
    props.labels.forEach(label => {
      const el = document.createElement('span');
      el.className = 'badge me-1';
      el.textContent = label.name;
      el.style.backgroundColor = label.color;
      el.style.color = getContrastColor(label.color);
      labelsContainer.appendChild(el);
    });
  }

  document.getElementById('view-in-linear').href = `https://linear.app/issue/${props.id}`;
  window.issueDetailsOffcanvas.show();
}

// ==================================================================================
// UI Utility Functions
// ==================================================================================
function switchView(showNoDueDateList) {
  document.getElementById('calendar').classList.toggle('d-none', showNoDueDateList);
  document.getElementById('no-due-date-list').classList.toggle('d-none', !showNoDueDateList);
}

function displayNoDueDateIssues(issues) {
  const listEl = document.getElementById('no-due-date-list');
  listEl.innerHTML = (issues.length === 0) 
    ? '<div class="text-center p-4 text-muted">No issues found without a due date.</div>'
    : '';
  if (issues.length === 0) return;

  const ul = document.createElement('ul');
  ul.className = 'list-group';
  issues.forEach(issue => {
    const li = document.createElement('li');
    li.className = 'list-group-item';
    li.innerHTML = `
      <div class="d-flex w-100 justify-content-between">
        <h6 class="mb-1">${issue.title}</h6>
        <small class="text-muted">${issue.team.name}</small>
      </div>
      <p class="mb-1 small text-muted">${issue.description || 'No description'}</p>
      <span class="badge" style="background-color: ${issue.state.color}; color: ${getContrastColor(issue.state.color)}">${issue.state.name}</span>
    `;
    ul.appendChild(li);
  });
  listEl.appendChild(ul);
}

function showLoading(isLoading) {
  document.getElementById('loading-overlay').classList.toggle('d-none', !isLoading);
}

function showError(message, error) {
  console.error(message, error);
  const errorOverlay = document.getElementById('error-overlay');
  if(errorOverlay) {
      errorOverlay.classList.remove('d-none');
      document.getElementById('error-message').textContent = `${message}: ${error.message}`;
  }
}

function getContrastColor(hex) {
  if (!hex) return '#000';
  const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
  return ((r * 299) + (g * 587) + (b * 114)) / 1000 >= 128 ? '#000' : '#fff';
}
