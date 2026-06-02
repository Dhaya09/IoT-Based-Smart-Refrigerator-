// ─── Toast Notifications ──────────────────────────────────────────────────────
let toastContainer = null;
function getToastContainer() {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }
  return toastContainer;
}

function showToast(title, body, severity = 'info', duration = 4000) {
  const icons = { info: 'ℹ️', warning: '⚠️', critical: '🚨', success: '✅' };
  const el = document.createElement('div');
  el.className = `toast ${severity}`;
  el.innerHTML = `
    <span class="toast-icon">${icons[severity] || icons.info}</span>
    <div><div class="toast-title">${title}</div><div class="toast-body">${body}</div></div>
  `;
  getToastContainer().appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transform = 'translateX(30px)'; el.style.transition = '.3s'; setTimeout(() => el.remove(), 300); }, duration);
}

// ─── API Helpers ──────────────────────────────────────────────────────────────
async function apiFetch(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(url, opts);
  return r.json();
}

// ─── Status badge updater ─────────────────────────────────────────────────────
function updateStatusPill(status) {
  const pill = document.getElementById('overall-status');
  if (!pill) return;
  pill.textContent = status;
  pill.className = `status-pill ${status}`;
}

// ─── Alert badge in nav ───────────────────────────────────────────────────────
function updateNavBadge(count) {
  const badges = document.querySelectorAll('.alert-nav-badge');
  badges.forEach(b => {
    b.textContent = count;
    b.style.display = count > 0 ? 'inline' : 'none';
  });
}

// ─── Mark active nav link ─────────────────────────────────────────────────────
function markActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === path);
  });
}

// ─── Severity class helper ────────────────────────────────────────────────────
function severityClass(sev) {
  if (sev === 'Critical') return 'critical';
  if (sev === 'Warning') return 'warning';
  return 'normal';
}

// ─── Format relative time ─────────────────────────────────────────────────────
function relTime(ts) {
  const d = new Date(ts);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  return d.toLocaleTimeString();
}

// ─── Poll status for nav badge ────────────────────────────────────────────────
async function pollGlobalStatus() {
  try {
    const d = await apiFetch('/api/status');
    updateStatusPill(d.overall_status);
    updateNavBadge(d.alert_count);
  } catch {}
}

document.addEventListener('DOMContentLoaded', () => {
  markActiveNav();
  pollGlobalStatus();
  setInterval(pollGlobalStatus, 5000);
});
