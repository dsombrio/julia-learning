// CRM Frontend App
const API = 'http://localhost:3000/api';
let token = localStorage.getItem('crm_token');
let currentUser = null;
let currentFilter = {};
let allContacts = [];
let allDeals = [];
let allTasks = [];
let allNotes = [];

// Auth tabs
document.querySelectorAll('.auth-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const isLogin = tab.dataset.tab === 'login';
    document.getElementById('login-form').style.display = isLogin ? 'block' : 'none';
    document.getElementById('register-form').style.display = isLogin ? 'none' : 'block';
  });
});

// Auth forms
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  if (res.ok) {
    token = data.token;
    currentUser = data.user;
    localStorage.setItem('crm_token', token);
    showApp();
  } else {
    toast(data.error);
  }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = document.getElementById('register-name').value;
  const email = document.getElementById('register-email').value;
  const password = document.getElementById('register-password').value;
  const res = await fetch(`${API}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  });
  const data = await res.json();
  if (res.ok) {
    token = data.token;
    currentUser = data.user;
    localStorage.setItem('crm_token', token);
    showApp();
  } else {
    toast(data.error);
  }
});

document.getElementById('logout-btn').addEventListener('click', () => {
  token = null;
  currentUser = null;
  localStorage.removeItem('crm_token');
  document.getElementById('auth-screen').style.display = 'flex';
  document.getElementById('app').style.display = 'none';
});

async function showApp() {
  const res = await fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) { logout(); return; }
  currentUser = await res.json();
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('app').style.display = 'flex';
  lucide.createIcons();
  loadDashboard();
}

// Navigation
document.querySelectorAll('.nav-item[data-page]').forEach(item => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    item.classList.add('active');
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${item.dataset.page}`).classList.add('active');
    if (item.dataset.page === 'dashboard') loadDashboard();
    if (item.dataset.page === 'contacts') loadContacts();
    if (item.dataset.page === 'deals') loadDeals();
    if (item.dataset.page === 'tasks') loadTasks();
    if (item.dataset.page === 'notes') loadNotes();
  });
});

// API helper
async function api(endpoint, options = {}) {
  const res = await fetch(`${API}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers
    }
  });
  return res.json();
}

// Dashboard
async function loadDashboard() {
  const data = await api('/dashboard');
  document.getElementById('stat-tasks').textContent = data.tasks?.length || 0;
  document.getElementById('stat-deals').textContent = data.activeDeals?.count || 0;
  document.getElementById('stat-value').textContent = `$${(data.activeDeals?.total || 0).toLocaleString()}`;
  renderDashboardTasks(data.tasks || []);
}

function renderDashboardTasks(tasks) {
  const el = document.getElementById('dashboard-tasks');
  if (tasks.length === 0) {
    el.innerHTML = '<div class="empty-state"><i data-lucide="check-square"></i><h3>No tasks yet</h3><p>Add your first task</p></div>';
    lucide.createIcons();
    return;
  }
  el.innerHTML = tasks.map(t => renderTaskItem(t)).join('');
  lucide.createIcons();
}

// Contacts
async function loadContacts() {
  allContacts = await api('/contacts');
  renderContacts(allContacts);
}

function renderContacts(contacts) {
  const el = document.getElementById('contacts-grid');
  if (contacts.length === 0) {
    el.innerHTML = '<div class="empty-state"><i data-lucide="users"></i><h3>No contacts</h3><p>Add your first contact</p></div>';
    return;
  }
  el.innerHTML = contacts.map(c => `
    <div class="contact-card" onclick="openContactModal(${c.id})">
      <div style="display:flex;justify-content:space-between;align-items:start">
        <div>
          <div class="name">${c.first_name} ${c.last_name || ''}</div>
          <div class="company">${c.company || 'No company'}</div>
        </div>
        <span class="badge badge-${c.type}">${c.type}</span>
      </div>
      <div class="contact-info">
        ${c.email ? `<div>${c.email}</div>` : ''}
        ${c.phone ? `<div>${c.phone}</div>` : ''}
      </div>
    </div>
  `).join('');
}

function filterContacts() {
  const q = document.getElementById('contact-search').value.toLowerCase();
  const filtered = allContacts.filter(c => 
    (c.first_name + ' ' + (c.last_name || '')).toLowerCase().includes(q) ||
    (c.company || '').toLowerCase().includes(q) ||
    (c.email || '').toLowerCase().includes(q)
  );
  renderContacts(filtered);
}

function filterContactsByType(type) {
  document.querySelectorAll('#page-contacts .filter-tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`#page-contacts .filter-tab[data-filter="${type}"]`).classList.add('active');
  const filtered = type === 'all' ? allContacts : allContacts.filter(c => c.type === type);
  renderContacts(filtered);
}

// Deals
async function loadDeals() {
  allDeals = await api('/deals');
  renderDeals(allDeals);
}

function renderDeals(deals) {
  const el = document.getElementById('deals-grid');
  if (deals.length === 0) {
    el.innerHTML = '<div class="empty-state"><i data-lucide="trending-up"></i><h3>No deals</h3><p>Add your first deal</p></div>';
    return;
  }
  el.innerHTML = deals.map(d => `
    <div class="deal-card" onclick="openDealModal(${d.id})">
      <div style="display:flex;justify-content:space-between;align-items:start">
        <div class="title">${d.title}</div>
        <span class="badge badge-${d.stage}">${d.stage}</span>
      </div>
      <div class="contact">${d.first_name ? d.first_name + ' ' + (d.last_name || '') : ''} ${d.company ? '@ ' + d.company : ''}</div>
      <div class="value">$${(d.value || 0).toLocaleString()}</div>
    </div>
  `).join('');
}

function filterDealsByStage(stage) {
  document.querySelectorAll('#page-deals .filter-tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`#page-deals .filter-tab[data-filter="${stage}"]`).classList.add('active');
  const filtered = stage === 'all' ? allDeals : allDeals.filter(d => d.stage === stage);
  renderDeals(filtered);
}

// Tasks
async function loadTasks(status = 'pending') {
  allTasks = await api('/tasks');
  currentFilter.tasks = status;
  const filtered = status === 'all' ? allTasks : allTasks.filter(t => t.status === status);
  renderTasks(filtered);
}

function renderTasks(tasks) {
  const el = document.getElementById('tasks-list');
  if (tasks.length === 0) {
    el.innerHTML = '<div class="empty-state"><i data-lucide="check-square"></i><h3>No tasks</h3><p>Add your first task</p></div>';
    lucide.createIcons();
    return;
  }
  el.innerHTML = tasks.map(t => renderTaskItem(t, true)).join('');
  lucide.createIcons();
}

// Time elapsed logic
function getTimeClass(created_at, timeframe_minutes, status) {
  if (status === 'completed') return { class: '', text: 'Completed' };
  
  const created = new Date(created_at);
  const now = new Date();
  const elapsed = now - created;
  const hours = Math.floor(elapsed / 3600000);
  const days = Math.floor(elapsed / 86400000);
  const timeframeMs = (timeframe_minutes || 0) * 60000;
  
  if (timeframeMs > 0 && elapsed > timeframeMs) {
    return { class: 'overdue-soft', text: formatElapsed(elapsed) };
  } else if (days >= 1) {
    return { class: 'overdue-1day', text: formatElapsed(elapsed) };
  }
  return { class: '', text: formatElapsed(elapsed) };
}

function formatElapsed(ms) {
  const hours = Math.floor(ms / 3600000);
  const days = Math.floor(ms / 86400000);
  if (days > 0) return `${days}d ${hours % 24}h ago`;
  if (hours > 0) return `${hours}h ago`;
  return 'Just now';
}

function renderTaskItem(t, showActions = false) {
  const time = getTimeClass(t.created_at, t.timeframe_minutes, t.status);
  
  return `
    <div class="task-item ${t.status === 'completed' ? 'completed' : ''} ${time.class}">
      <div class="task-checkbox ${t.status === 'completed' ? 'checked' : ''}" onclick="toggleTask(${t.id})">
        ${t.status === 'completed' ? '<i data-lucide="check" style="width:12px;height:12px;color:white"></i>' : ''}
      </div>
      <div class="task-content">
        <div class="task-title" style="${t.status === 'completed' ? 'text-decoration:line-through' : ''}">${t.title}</div>
        <div class="task-meta">
          ${t.company ? `<span>${t.first_name || ''} ${t.last_name || ''} @ ${t.company}</span>` : ''}
          ${t.source === 'plaud' ? '<span class="badge badge-plaud">Plaud</span>' : ''}
        </div>
      </div>
      <div class="task-time ${time.class}">${time.text}</div>
      ${showActions ? `
        <div class="task-actions">
          <button class="btn btn-ghost" onclick="deleteTask(${t.id})" style="padding:4px">
            <i data-lucide="trash-2" style="width:16px;height:16px"></i>
          </button>
        </div>
      ` : ''}
    </div>
  `;
}

function filterTasksByStatus(status) {
  document.querySelectorAll('#page-tasks .filter-tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`#page-tasks .filter-tab[data-filter="${status}"]`).classList.add('active');
  const filtered = status === 'all' ? allTasks : allTasks.filter(t => t.status === status);
  renderTasks(filtered);
}

async function toggleTask(id) {
  await api(`/tasks/${id}/complete`, { method: 'PATCH' });
  loadTasks(currentFilter.tasks || 'pending');
  loadDashboard();
  toast('Task completed');
}

async function deleteTask(id) {
  if (!confirm('Delete this task?')) return;
  await api(`/tasks/${id}`, { method: 'DELETE' });
  loadTasks(currentFilter.tasks || 'pending');
  loadDashboard();
  toast('Task deleted');
}

// Notes
async function loadNotes() {
  allNotes = await api('/notes');
  renderNotes(allNotes);
}

function renderNotes(notes) {
  const el = document.getElementById('notes-list');
  if (notes.length === 0) {
    el.innerHTML = '<div class="empty-state"><i data-lucide="file-text"></i><h3>No notes</h3><p>Add your first note</p></div>';
    lucide.createIcons();
    return;
  }
  el.innerHTML = `<div class="card">${notes.map(n => `
    <div class="note-item">
      <div class="note-content">${n.content}</div>
      <div class="note-meta">
        ${n.first_name ? `${n.first_name} ${n.last_name || ''}` : ''} 
        ${n.company ? `@ ${n.company}` : ''} 
        · ${new Date(n.created_at).toLocaleDateString()}
      </div>
    </div>
  `).join('')}</div>`;
  lucide.createIcons();
}

// Modals
let currentModalType = '';
let currentModalId = null;

function closeModal(e) {
  if (e && e.target !== e.currentTarget) return;
  document.getElementById('modal-overlay').classList.remove('active');
}

function openContactModal(id = null) {
  currentModalType = 'contact';
  currentModalId = id;
  const isEdit = !!id;
  const contact = id ? allContacts.find(c => c.id === id) : null;
  
  document.getElementById('modal-title').textContent = isEdit ? 'Edit Contact' : 'Add Contact';
  document.getElementById('modal-body').innerHTML = `
    <input type="hidden" id="contact-id" value="${id || ''}">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label>First Name</label>
        <input type="text" id="contact-first_name" value="${contact?.first_name || ''}">
      </div>
      <div class="form-group">
        <label>Last Name</label>
        <input type="text" id="contact-last_name" value="${contact?.last_name || ''}">
      </div>
    </div>
    <div class="form-group">
      <label>Company</label>
      <input type="text" id="contact-company" value="${contact?.company || ''}">
    </div>
    <div class="form-group">
      <label>Email</label>
      <input type="email" id="contact-email" value="${contact?.email || ''}">
    </div>
    <div class="form-group">
      <label>Phone</label>
      <input type="text" id="contact-phone" value="${contact?.phone || ''}">
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label>Type</label>
        <select id="contact-type">
          <option value="customer" ${contact?.type === 'customer' ? 'selected' : ''}>Customer</option>
          <option value="vendor" ${contact?.type === 'vendor' ? 'selected' : ''}>Vendor</option>
          <option value="prospect" ${contact?.type === 'prospect' || !contact ? 'selected' : ''}>Prospect</option>
        </select>
      </div>
      <div class="form-group">
        <label>Metro</label>
        <select id="contact-metro">
          <option value="">--</option>
          <option value="austin" ${contact?.metro === 'austin' ? 'selected' : ''}>Austin</option>
          <option value="dallas" ${contact?.metro === 'dallas' ? 'selected' : ''}>Dallas</option>
          <option value="houston" ${contact?.metro === 'houston' ? 'selected' : ''}>Houston</option>
          <option value="san antonio" ${contact?.metro === 'san antonio' ? 'selected' : ''}>San Antonio</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label>Notes</label>
      <textarea id="contact-notes" rows="3">${contact?.notes || ''}</textarea>
    </div>
  `;
  document.getElementById('modal-overlay').classList.add('active');
}

function openDealModal(id = null) {
  currentModalType = 'deal';
  currentModalId = id;
  const isEdit = !!id;
  const deal = id ? allDeals.find(d => d.id === id) : null;
  
  document.getElementById('modal-title').textContent = isEdit ? 'Edit Deal' : 'Add Deal';
  document.getElementById('modal-body').innerHTML = `
    <input type="hidden" id="deal-id" value="${id || ''}">
    <div class="form-group">
      <label>Title</label>
      <input type="text" id="deal-title" value="${deal?.title || ''}">
    </div>
    <div class="form-group">
      <label>Contact</label>
      <select id="deal-contact_id">
        <option value="">-- None --</option>
        ${allContacts.map(c => `<option value="${c.id}" ${deal?.contact_id == c.id ? 'selected' : ''}>${c.first_name} ${c.last_name || ''} ${c.company ? '(' + c.company + ')' : ''}</option>`).join('')}
      </select>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label>Value ($)</label>
        <input type="number" id="deal-value" value="${deal?.value || ''}">
      </div>
      <div class="form-group">
        <label>Stage</label>
        <select id="deal-stage">
          <option value="lead" ${deal?.stage === 'lead' ? 'selected' : ''}>Lead</option>
          <option value="prospect" ${deal?.stage === 'prospect' ? 'selected' : ''}>Prospect</option>
          <option value="proposal" ${deal?.stage === 'proposal' ? 'selected' : ''}>Proposal</option>
          <option value="negotiation" ${deal?.stage === 'negotiation' ? 'selected' : ''}>Negotiation</option>
          <option value="won" ${deal?.stage === 'won' ? 'selected' : ''}>Won</option>
          <option value="lost" ${deal?.stage === 'lost' ? 'selected' : ''}>Lost</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label>Notes</label>
      <textarea id="deal-notes" rows="3">${deal?.notes || ''}</textarea>
    </div>
  `;
  document.getElementById('modal-overlay').classList.add('active');
}

function openTaskModal(id = null) {
  currentModalType = 'task';
  currentModalId = id;
  const isEdit = !!id;
  const task = id ? allTasks.find(t => t.id === id) : null;
  
  document.getElementById('modal-title').textContent = isEdit ? 'Edit Task' : 'Add Task';
  document.getElementById('modal-body').innerHTML = `
    <input type="hidden" id="task-id" value="${id || ''}">
    <div class="form-group">
      <label>Title</label>
      <input type="text" id="task-title" value="${task?.title || ''}">
    </div>
    <div class="form-group">
      <label>Contact (optional)</label>
      <select id="task-contact_id">
        <option value="">-- None --</option>
        ${allContacts.map(c => `<option value="${c.id}" ${task?.contact_id == c.id ? 'selected' : ''}>${c.first_name} ${c.last_name || ''} ${c.company ? '(' + c.company + ')' : ''}</option>`).join('')}
      </select>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label>Due Date (optional)</label>
        <input type="date" id="task-due_date" value="${task?.due_date || ''}">
      </div>
      <div class="form-group">
        <label>Timeframe (minutes)</label>
        <input type="number" id="task-timeframe_minutes" value="${task?.timeframe_minutes || ''}" placeholder="e.g. 480 for 8h">
      </div>
    </div>
    <div class="form-group">
      <label>Source</label>
      <select id="task-source">
        <option value="manual" ${task?.source === 'manual' || !task ? 'selected' : ''}>Manual</option>
        <option value="plaud" ${task?.source === 'plaud' ? 'selected' : ''}>Plaud</option>
      </select>
    </div>
    <div class="form-group">
      <label>Description</label>
      <textarea id="task-description" rows="3">${task?.description || ''}</textarea>
    </div>
  `;
  document.getElementById('modal-overlay').classList.add('active');
}

function openNoteModal(id = null) {
  currentModalType = 'note';
  currentModalId = id;
  
  document.getElementById('modal-title').textContent = 'Add Note';
  document.getElementById('modal-body').innerHTML = `
    <input type="hidden" id="note-id" value="${id || ''}">
    <div class="form-group">
      <label>Contact (optional)</label>
      <select id="note-contact_id">
        <option value="">-- None --</option>
        ${allContacts.map(c => `<option value="${c.id}">${c.first_name} ${c.last_name || ''} ${c.company ? '(' + c.company + ')' : ''}</option>`).join('')}
      </select>
    </div>
    <div class="form-group">
      <label>Note</label>
      <textarea id="note-content" rows="5" placeholder="Write your note..."></textarea>
    </div>
  `;
  document.getElementById('modal-overlay').classList.add('active');
}

async function saveModal() {
  let endpoint = '';
  let method = 'POST';
  let body = {};

  if (currentModalType === 'contact') {
    const id = document.getElementById('contact-id').value;
    endpoint = id ? `/contacts/${id}` : '/contacts';
    method = id ? 'PUT' : 'POST';
    body = {
      first_name: document.getElementById('contact-first_name').value,
      last_name: document.getElementById('contact-last_name').value,
      company: document.getElementById('contact-company').value,
      email: document.getElementById('contact-email').value,
      phone: document.getElementById('contact-phone').value,
      type: document.getElementById('contact-type').value,
      metro: document.getElementById('contact-metro').value,
      notes: document.getElementById('contact-notes').value
    };
  } else if (currentModalType === 'deal') {
    const id = document.getElementById('deal-id').value;
    endpoint = id ? `/deals/${id}` : '/deals';
    method = id ? 'PUT' : 'POST';
    body = {
      title: document.getElementById('deal-title').value,
      contact_id: document.getElementById('deal-contact_id').value || null,
      value: parseFloat(document.getElementById('deal-value').value) || 0,
      stage: document.getElementById('deal-stage').value,
      notes: document.getElementById('deal-notes').value
    };
  } else if (currentModalType === 'task') {
    const id = document.getElementById('task-id').value;
    endpoint = id ? `/tasks/${id}` : '/tasks';
    method = id ? 'PUT' : 'POST';
    body = {
      title: document.getElementById('task-title').value,
      contact_id: document.getElementById('task-contact_id').value || null,
      due_date: document.getElementById('task-due_date').value || null,
      timeframe_minutes: parseInt(document.getElementById('task-timeframe_minutes').value) || null,
      source: document.getElementById('task-source').value,
      description: document.getElementById('task-description').value,
      status: 'pending'
    };
  } else if (currentModalType === 'note') {
    endpoint = '/notes';
    body = {
      contact_id: document.getElementById('note-contact_id').value || null,
      content: document.getElementById('note-content').value
    };
  }

  await api(endpoint, { method, body: JSON.stringify(body) });
  closeModal();
  toast('Saved');

  if (currentModalType === 'contact') loadContacts();
  if (currentModalType === 'deal') loadDeals();
  if (currentModalType === 'task') { loadTasks(currentFilter.tasks || 'pending'); loadDashboard(); }
  if (currentModalType === 'note') loadNotes();
}

// Toast
function toast(msg) {
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = msg;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

// Auto-refresh task times every minute
setInterval(() => {
  if (document.getElementById('app').style.display !== 'none') {
    const activePage = document.querySelector('.page.active');
    if (activePage) {
      const pageId = activePage.id;
      if (pageId === 'page-dashboard') loadDashboard();
      if (pageId === 'page-tasks') loadTasks(currentFilter.tasks || 'pending');
    }
  }
}, 60000);

// Init
if (token) {
  showApp();
} else {
  document.getElementById('auth-screen').style.display = 'flex';
}
