/**
 * Ordinace Na Vyhlídce – Frontend Application Logic
 */

const API_BASE = '/api/v1';

// Application State
const state = {
  token: localStorage.getItem('token') || null,
  currentUser: null,
  users: [],
  editingUserId: null,
};

// DOM Elements
const views = {
  login: document.getElementById('login-view'),
  dashboard: document.getElementById('dashboard-view'),
};

const userNav = document.getElementById('user-nav-badge');
const navAvatar = document.getElementById('nav-user-avatar');
const navName = document.getElementById('nav-user-name');
const navRole = document.getElementById('nav-user-role');
const navLogoutBtn = document.getElementById('nav-logout-btn');

const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const demoFillBtn = document.getElementById('demo-fill-btn');

const usersTableBody = document.getElementById('users-table-body');
const searchInput = document.getElementById('search-input');
const roleFilter = document.getElementById('role-filter');
const openCreateModalBtn = document.getElementById('open-create-modal-btn');

// Modal Elements
const userModal = document.getElementById('user-modal');
const modalTitle = document.getElementById('modal-title');
const userForm = document.getElementById('user-form');
const closeModalBtn = document.getElementById('close-modal-btn');
const cancelModalBtn = document.getElementById('cancel-modal-btn');
const formUsername = document.getElementById('form-username');
const formFullname = document.getElementById('form-fullname');
const formEmail = document.getElementById('form-email');
const formRole = document.getElementById('form-role');
const formPassword = document.getElementById('form-password');
const formPasswordHelp = document.getElementById('form-password-help');
const formActiveGroup = document.getElementById('form-active-group');
const formActive = document.getElementById('form-active');

// Stats Elements
const statTotalUsers = document.getElementById('stat-total-users');
const statDoctors = document.getElementById('stat-doctors');
const statReception = document.getElementById('stat-reception');

// Toast Container
const toastContainer = document.getElementById('toast-container');

// ==========================================================================
// Toast Notifications
// ==========================================================================
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : '⚠'}</span>
    <div>${message}</div>
  `;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ==========================================================================
// Authentication Handlers
// ==========================================================================
async function handleLogin(e) {
  e.preventDefault();
  loginError.style.display = 'none';

  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;

  try {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Přihlášení se nezdařilo.');
    }

    state.token = data.access_token;
    localStorage.setItem('token', state.token);
    showToast('Úspěšně přihlášeno.', 'success');
    await initApp();
  } catch (err) {
    loginError.innerText = err.message;
    loginError.style.display = 'block';
  }
}

function handleLogout() {
  state.token = null;
  state.currentUser = null;
  state.users = [];
  localStorage.removeItem('token');
  showLoginView();
  showToast('Byli jste odhlášeni.', 'success');
}

async function fetchCurrentUser() {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: {
        Authorization: `Bearer ${state.token}`,
      },
    });

    if (res.status === 401) {
      handleLogout();
      return null;
    }

    if (!res.ok) throw new Error('Chyba při načtení profilu.');
    return await res.json();
  } catch (err) {
    handleLogout();
    return null;
  }
}

// ==========================================================================
// User Management
// ==========================================================================
async function fetchUsers() {
  if (state.currentUser.role !== 'ADMIN') {
    state.users = [state.currentUser];
    renderUsers();
    updateStats();
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/users/`, {
      headers: {
        Authorization: `Bearer ${state.token}`,
      },
    });
    if (!res.ok) throw new Error('Nepodařilo se načíst seznam uživatelů.');
    state.users = await res.json();
    renderUsers();
    updateStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function updateStats() {
  const total = state.users.length;
  const doctors = state.users.filter(u => u.role === 'LEKAR').length;
  const reception = state.users.filter(u => u.role === 'RECEPCNI').length;

  if (statTotalUsers) statTotalUsers.innerText = total;
  if (statDoctors) statDoctors.innerText = doctors;
  if (statReception) statReception.innerText = reception;
}

function renderUsers() {
  const searchTerm = searchInput.value.toLowerCase().trim();
  const selectedRole = roleFilter.value;

  const filtered = state.users.filter(u => {
    const matchesSearch =
      u.full_name.toLowerCase().includes(searchTerm) ||
      u.username.toLowerCase().includes(searchTerm) ||
      (u.email && u.email.toLowerCase().includes(searchTerm));
    const matchesRole = !selectedRole || u.role === selectedRole;
    return matchesSearch && matchesRole;
  });

  if (filtered.length === 0) {
    usersTableBody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
          Žádní uživatelé neodpovídají zadaným kritériím.
        </td>
      </tr>
    `;
    return;
  }

  usersTableBody.innerHTML = filtered
    .map(user => {
      const initials = user.full_name
        .split(' ')
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase();

      const roleBadgeClass =
        user.role === 'ADMIN'
          ? 'badge-admin'
          : user.role === 'LEKAR'
          ? 'badge-lekar'
          : 'badge-recepcni';

      const roleName =
        user.role === 'ADMIN'
          ? 'Administrátor'
          : user.role === 'LEKAR'
          ? 'Lékař'
          : 'Recepční';

      const statusBadge = user.is_active
        ? '<span class="badge badge-active">Aktivní</span>'
        : '<span class="badge badge-inactive">Deaktivován</span>';

      const canEdit = state.currentUser.role === 'ADMIN';
      const isSelf = state.currentUser.id === user.id;

      return `
        <tr>
          <td>
            <div class="user-cell">
              <div class="user-avatar-sm">${initials}</div>
              <div>
                <strong>${escapeHtml(user.full_name)}</strong>
                <div style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(user.username)}</div>
              </div>
            </div>
          </td>
          <td>${user.email ? escapeHtml(user.email) : '<em>Neuveden</em>'}</td>
          <td><span class="badge ${roleBadgeClass}">${roleName}</span></td>
          <td>${statusBadge}</td>
          <td style="color: var(--text-secondary); font-size: 0.85rem;">
            ${new Date(user.created_at).toLocaleDateString('cs-CZ')}
          </td>
          <td>
            <div class="actions-cell">
              ${
                canEdit
                  ? `
                <button class="btn btn-secondary btn-sm" onclick="openEditModal(${user.id})" title="Upravit uživatele">
                  Upravit
                </button>
                ${
                  !isSelf
                    ? `
                  <button class="btn btn-danger-outline btn-sm" onclick="toggleUserStatus(${user.id}, ${user.is_active})" title="${user.is_active ? 'Deaktivovat' : 'Aktivovat'}">
                    ${user.is_active ? 'Deaktivovat' : 'Aktivovat'}
                  </button>
                `
                    : ''
                }
              `
                  : ''
              }
            </div>
          </td>
        </tr>
      `;
    })
    .join('');
}

// Modal Handlers
function openCreateModal() {
  state.editingUserId = null;
  modalTitle.innerText = 'Přidat člena personálu';
  userForm.reset();
  formUsername.disabled = false;
  formPassword.required = true;
  formPasswordHelp.innerText = 'Zadejte minimálně 6 znaků.';
  formActiveGroup.style.display = 'none';
  userModal.classList.add('active');
}

window.openEditModal = function (userId) {
  const user = state.users.find(u => u.id === userId);
  if (!user) return;

  state.editingUserId = userId;
  modalTitle.innerText = `Upravit uživatele: ${user.full_name}`;
  formUsername.value = user.username;
  formUsername.disabled = true; // Username is immutable
  formFullname.value = user.full_name;
  formEmail.value = user.email || '';
  formRole.value = user.role;
  formPassword.value = '';
  formPassword.required = false;
  formPasswordHelp.innerText = 'Ponechte prázdné, pokud heslo nechcete měnit.';
  formActive.checked = user.is_active;
  formActiveGroup.style.display = 'block';

  userModal.classList.add('active');
};

function closeModal() {
  userModal.classList.remove('active');
}

async function handleSaveUser(e) {
  e.preventDefault();

  const payload = {
    full_name: formFullname.value.trim(),
    email: formEmail.value.trim() || null,
    role: formRole.value,
  };

  if (formPassword.value) {
    payload.password = formPassword.value;
  }

  try {
    if (state.editingUserId) {
      // Update
      payload.is_active = formActive.checked;
      const res = await fetch(`${API_BASE}/users/${state.editingUserId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Chyba při úpravě uživatele.');
      showToast('Uživatel byl úspěšně upraven.');
    } else {
      // Create
      payload.username = formUsername.value.trim();
      payload.password = formPassword.value;
      payload.is_active = true;

      const res = await fetch(`${API_BASE}/users/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Chyba při zakládání uživatele.');
      showToast('Nový uživatel byl úspěšně založen.');
    }

    closeModal();
    await fetchUsers();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

window.toggleUserStatus = async function (userId, currentStatus) {
  const user = state.users.find(u => u.id === userId);
  if (!user) return;

  const actionText = currentStatus ? 'deaktivovat' : 'znovu aktivovat';
  if (!confirm(`Opravdu si přejete ${actionText} uživatele ${user.full_name}?`)) {
    return;
  }

  try {
    if (currentStatus) {
      // Soft-delete
      const res = await fetch(`${API_BASE}/users/${userId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${state.token}`,
        },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Chyba při deaktivaci účtu.');
      showToast(`Uživatel ${user.full_name} byl deaktivován.`);
    } else {
      // Re-activate via PUT
      const res = await fetch(`${API_BASE}/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify({ is_active: true }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Chyba při aktivaci účtu.');
      showToast(`Uživatel ${user.full_name} byl opět aktivován.`);
    }
    await fetchUsers();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

// ==========================================================================
// View Transitions
// ==========================================================================
function showLoginView() {
  views.login.style.display = 'flex';
  views.dashboard.style.display = 'none';
  userNav.style.display = 'none';
  navLogoutBtn.style.display = 'none';
}

function showDashboardView() {
  views.login.style.display = 'none';
  views.dashboard.style.display = 'block';
  userNav.style.display = 'flex';
  navLogoutBtn.style.display = 'inline-flex';

  const initials = state.currentUser.full_name
    .split(' ')
    .map(n => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  navAvatar.innerText = initials;
  navName.innerText = state.currentUser.full_name;
  navRole.innerText = state.currentUser.role;

  // Toggle admin features
  if (state.currentUser.role !== 'ADMIN') {
    openCreateModalBtn.style.display = 'none';
  } else {
    openCreateModalBtn.style.display = 'inline-flex';
  }
}

// Utility
function escapeHtml(text) {
  if (!text) return '';
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// Quick Demo Fill
if (demoFillBtn) {
  demoFillBtn.addEventListener('click', () => {
    document.getElementById('login-username').value = 'admin';
    document.getElementById('login-password').value = 'admin123';
  });
}

// Listeners
loginForm.addEventListener('submit', handleLogin);
navLogoutBtn.addEventListener('click', handleLogout);
searchInput.addEventListener('input', renderUsers);
roleFilter.addEventListener('change', renderUsers);
openCreateModalBtn.addEventListener('click', openCreateModal);
closeModalBtn.addEventListener('click', closeModal);
cancelModalBtn.addEventListener('click', closeModal);
userForm.addEventListener('submit', handleSaveUser);

// Close modal on click outside
userModal.addEventListener('click', e => {
  if (e.target === userModal) closeModal();
});

// App Initialization
async function initApp() {
  if (state.token) {
    const user = await fetchCurrentUser();
    if (user) {
      state.currentUser = user;
      showDashboardView();
      await fetchUsers();
      return;
    }
  }
  showLoginView();
}

// Start
initApp();
