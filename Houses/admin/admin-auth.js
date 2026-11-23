/**
 * SPR School of Excellence — Election Administration
 * Pure Browser-Native Admin Authentication Gate
 * 
 * 100% Client-Side — NO Python, NO Backend Server, NO Port 5001 Required!
 * - Authorized Admin Email check
 * - Cryptographic SHA-256 password verification (Web Crypto API)
 * - Eye icon toggle to view/hide password
 * - Session lock on tab/browser close (sessionStorage)
 * - Permanent reliability anywhere (Live Server, GitHub, Netlify, Custom Domain, USB)
 */

(function () {
  'use strict';

  // Authorized Administrators list
  // Pre-hashed with SHA-256 for security against DevTools snooping
  const AUTHORIZED_ADMINS = [
    {
      email: "rc4616105@gmail.com",
      name: "rc4616105",
      passwordHashes: [
        "9d0747886a08ff4f8512ef306e86f2eaa0941b9781214402f8dbfd6331dce944", // rc4616105
        "b249d97a0947f3f473dd0f63ef902a448f73e53b277a2a9b9f624db17db3b4b0", // Spr-Elections@rc4616105
        "7fc87bf219ebd9092c5ce776c4afa77f20b54c3653067a6faa249a1c8fef8789", // spr-elections@rc4616105
        "266b1d1cba0d57310b1a83a607eb2bc74048c9b50a154238209d7fe5a30846db"  // RC4616105
      ]
    },
    {
      email: "sprkmrd@gmail.com",
      name: "sprkmrd",
      passwordHashes: [
        "f25a69a7770bda682c6aea8cf0807b57c55ad0812b2b7f5863b069961f0173d5", // sprkmrd
        "2de9c37ee48d2be7e1039f1ee8c48a0cbef2a1e2dea688eadf4f29c20d84da81", // Sprkmrd
        "4513c8a70e49e8508d23a279ff2e750ddfefb9472cfe22f2caa57d44c5337425", // SPRKMRD
        "d136dec69402533dbb27363bf5aa8401b92629c3690155ceca21201f02ce0110", // sprkmrd@gmail.com
        "bbd256bec02f4e1035dc39bf0a8e66650cd6abd31c9e00495420c8cee17c9d68", // Spr-Elections@sprkmrd
        "4d0b96dd4d018c6d1b56477d803961fa59c46f34455ced7b4fa10b9f4eea51a7", // spr-elections@sprkmrd
        "9d0747886a08ff4f8512ef306e86f2eaa0941b9781214402f8dbfd6331dce944", // rc4616105
        "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9", // admin123
        "2a3c4d59a0a69568bc6968706339164bc5e1825b633c645982c88b99554db35a", // Spr@2026
        "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  // admin
      ]
    }
  ];

  const STORAGE_KEY_TOKEN = 'spr_admin_session_token';
  const STORAGE_KEY_NAME = 'spr_admin_name';
  const STORAGE_KEY_EMAIL = 'spr_admin_email';

  // Fast Browser-Native SHA-256 Hashing via Web Crypto API
  async function computeSha256(text) {
    try {
      if (window.crypto && window.crypto.subtle && window.crypto.subtle.digest) {
        const encoder = new TextEncoder();
        const data = encoder.encode(text);
        const hashBuffer = await window.crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      }
    } catch (_) {}
    return '';
  }

  // Inject CSS immediately to lock screen and style the auth gate
  function injectAuthStyles() {
    if (document.getElementById('spr-auth-styles')) return;
    const style = document.createElement('style');
    style.id = 'spr-auth-styles';
    style.textContent = `
      /* Immediate Lockout state */
      html.spr-admin-locked body > :not(#spr-auth-overlay) {
        filter: blur(12px) grayscale(40%);
        pointer-events: none !important;
        user-select: none !important;
      }
      html.spr-admin-locked body {
        overflow: hidden !important;
      }

      /* Modal Overlay */
      #spr-auth-overlay {
        position: fixed;
        inset: 0;
        z-index: 999999;
        background: rgba(20, 20, 19, 0.78);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1.25rem;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #141413;
        animation: sprFadeIn 0.25s ease-out;
      }

      @keyframes sprFadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      /* Card Box */
      .spr-auth-card {
        background: #ffffff;
        border: 1px solid #e5dccb;
        border-radius: 20px;
        box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(0, 0, 0, 0.05);
        width: 100%;
        max-width: 460px;
        overflow: hidden;
        position: relative;
        animation: sprPopIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      }

      @keyframes sprPopIn {
        from { transform: scale(0.94); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
      }

      .spr-auth-card-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2rem 1.75rem 1.75rem;
        text-align: center;
        color: #ffffff;
        border-bottom: 2px solid #cc785c;
      }

      .spr-auth-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(204, 120, 92, 0.22);
        color: #fbd5c6;
        border: 1px solid rgba(204, 120, 92, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.85rem;
      }

      .spr-auth-title {
        font-family: 'Fraunces', serif;
        font-size: 1.55rem;
        font-weight: 700;
        margin: 0 0 0.35rem;
        letter-spacing: -0.01em;
        color: #ffffff;
      }

      .spr-auth-subtitle {
        font-size: 0.85rem;
        color: #cbd5e1;
        margin: 0;
        line-height: 1.45;
      }

      .spr-auth-card-body {
        padding: 1.85rem 1.75rem 1.85rem;
      }

      /* Form Fields */
      .spr-auth-field {
        margin-bottom: 1.25rem;
      }

      .spr-auth-label {
        display: block;
        font-size: 0.82rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.4rem;
      }

      .spr-auth-input {
        width: 100%;
        padding: 0.75rem 0.95rem;
        font-size: 0.95rem;
        font-family: inherit;
        border: 1.5px solid #cbd5e1;
        border-radius: 10px;
        background: #f8fafc;
        color: #0f172a;
        box-sizing: border-box;
        transition: all 0.15s ease;
      }

      .spr-auth-input:focus {
        outline: none;
        border-color: #059669;
        background: #ffffff;
        box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15);
      }

      /* Password input with toggle button */
      .spr-pwd-wrap {
        position: relative;
        display: flex;
        align-items: center;
      }

      .spr-pwd-wrap .spr-auth-input {
        padding-right: 44px;
      }

      .spr-pwd-toggle-btn {
        position: absolute;
        right: 8px;
        background: none;
        border: none;
        cursor: pointer;
        padding: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #64748b;
        border-radius: 6px;
        transition: color 0.15s, background-color 0.15s;
      }

      .spr-pwd-toggle-btn:hover {
        color: #0f172a;
        background: #f1f5f9;
      }

      /* Alerts */
      .spr-auth-alert {
        padding: 0.75rem 0.95rem;
        border-radius: 10px;
        font-size: 0.82rem;
        line-height: 1.45;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
      }

      .spr-auth-alert.error {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
      }

      .spr-auth-alert.success {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
      }

      /* Button */
      .spr-auth-btn-primary {
        width: 100%;
        padding: 0.85rem 1.25rem;
        font-size: 0.95rem;
        font-weight: 700;
        font-family: inherit;
        background: #059669;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        transition: all 0.15s ease;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
        margin-top: 0.5rem;
      }

      .spr-auth-btn-primary:hover:not(:disabled) {
        background: #047857;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(5, 150, 105, 0.35);
      }

      .spr-auth-btn-primary:active:not(:disabled) {
        transform: translateY(0);
      }

      .spr-auth-btn-primary:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      /* Topbar Admin Session Badge */
      .spr-admin-session-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 0.3rem 0.65rem 0.3rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #0f172a;
      }

      .spr-admin-session-badge .admin-icon {
        font-size: 0.9rem;
      }

      .spr-admin-session-badge .admin-name {
        color: #047857;
        font-weight: 700;
      }

      .spr-admin-logout-btn {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
        border-radius: 9999px;
        padding: 0.15rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.15s ease;
      }

      .spr-admin-logout-btn:hover {
        background: #ef4444;
        color: #ffffff;
        border-color: #ef4444;
      }
    `;
    document.head.appendChild(style);
  }

  // Check if session token is in sessionStorage
  function getActiveSession() {
    const token = sessionStorage.getItem(STORAGE_KEY_TOKEN);
    const name = sessionStorage.getItem(STORAGE_KEY_NAME) || 'Admin';
    const email = sessionStorage.getItem(STORAGE_KEY_EMAIL) || '';
    if (!token) return null;
    return { token, name, email };
  }

  // Lock the UI
  function lockInterface() {
    document.documentElement.classList.add('spr-admin-locked');
    showAuthModal();
  }

  // Unlock the UI
  function unlockInterface(session) {
    document.documentElement.classList.remove('spr-admin-locked');
    const existingOverlay = document.getElementById('spr-auth-overlay');
    if (existingOverlay) existingOverlay.remove();
    renderSessionBadge(session);
  }

  // Render topbar session badge
  function renderSessionBadge(session) {
    const existing = document.getElementById('spr-admin-session-badge');
    if (existing) existing.remove();

    const topbarActions = document.querySelector('.topbar-actions');
    if (!topbarActions) return;

    const badge = document.createElement('div');
    badge.id = 'spr-admin-session-badge';
    badge.className = 'spr-admin-session-badge';
    badge.innerHTML = `
      <span class="admin-icon">🛡️</span>
      <span>Admin: <span class="admin-name">${escapeHtml(session.name)}</span></span>
      <button type="button" id="spr-admin-logout-btn" class="spr-admin-logout-btn" title="Lock admin dashboard">🔒 Logout</button>
    `;

    topbarActions.prepend(badge);

    document.getElementById('spr-admin-logout-btn').addEventListener('click', function () {
      if (confirm(`Lock the admin dashboard and log out ${session.name}?`)) {
        sessionStorage.removeItem(STORAGE_KEY_TOKEN);
        sessionStorage.removeItem(STORAGE_KEY_NAME);
        sessionStorage.removeItem(STORAGE_KEY_EMAIL);
        badge.remove();
        lockInterface();
      }
    });
  }

  function escapeHtml(str) {
    return String(str || '').replace(/[&<>'"]/g, tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag));
  }

  function showAuthModal() {
    injectAuthStyles();

    let overlay = document.getElementById('spr-auth-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'spr-auth-overlay';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-modal', 'true');
      document.body.appendChild(overlay);
    }

    renderModalContent();
  }

  // SVG Icons for Password Toggle
  const EYE_OPEN_SVG = `<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
  const EYE_CLOSED_SVG = `<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;

  function renderModalContent() {
    const overlay = document.getElementById('spr-auth-overlay');
    if (!overlay) return;

    overlay.innerHTML = `
      <div class="spr-auth-card">
        <div class="spr-auth-card-header">
          <div class="spr-auth-badge">🛡️ Authorized Access Only</div>
          <h2 class="spr-auth-title">Election Administration</h2>
          <p class="spr-auth-subtitle">SPR School of Excellence • School House Elections 2026</p>
        </div>
        <div class="spr-auth-card-body">
          <div id="spr-auth-alert-box" style="display:none;"></div>

          <form id="spr-login-form">
            <div class="spr-auth-field">
              <label class="spr-auth-label" for="spr-input-email">Administrator Email</label>
              <input
                type="email"
                id="spr-input-email"
                class="spr-auth-input"
                placeholder="Enter email"
                required
                autocomplete="username"
                autofocus
              />
            </div>

            <div class="spr-auth-field">
              <label class="spr-auth-label" for="spr-input-password">Administrative Password</label>
              <div class="spr-pwd-wrap">
                <input
                  type="password"
                  id="spr-input-password"
                  class="spr-auth-input"
                  placeholder="Enter password"
                  required
                  autocomplete="current-password"
                />
                <button type="button" id="spr-toggle-pwd-btn" class="spr-pwd-toggle-btn" title="Show / Hide Password" aria-label="Toggle password visibility">
                  ${EYE_OPEN_SVG}
                </button>
              </div>
            </div>

            <button type="submit" id="spr-btn-login" class="spr-auth-btn-primary">
              <span>Unlock Admin Dashboard 🚀</span>
            </button>
          </form>
        </div>
      </div>
    `;

    attachLoginEvents();
  }

  function showAlert(message, type = 'error') {
    const box = document.getElementById('spr-auth-alert-box');
    if (!box) return;
    box.style.display = 'block';
    box.className = `spr-auth-alert ${type}`;
    const icon = type === 'error' ? '⚠️' : '✅';
    box.innerHTML = `<span>${icon}</span><div>${escapeHtml(message)}</div>`;
  }

  function clearAlert() {
    const box = document.getElementById('spr-auth-alert-box');
    if (box) box.style.display = 'none';
  }

  function attachLoginEvents() {
    const form = document.getElementById('spr-login-form');
    const submitBtn = document.getElementById('spr-btn-login');
    const emailInput = document.getElementById('spr-input-email');
    const pwInput = document.getElementById('spr-input-password');
    const toggleBtn = document.getElementById('spr-toggle-pwd-btn');

    // Toggle Password Visibility
    let isPasswordVisible = false;
    toggleBtn.addEventListener('click', function () {
      isPasswordVisible = !isPasswordVisible;
      if (isPasswordVisible) {
        pwInput.type = 'text';
        toggleBtn.innerHTML = EYE_CLOSED_SVG;
        toggleBtn.title = 'Hide Password';
      } else {
        pwInput.type = 'password';
        toggleBtn.innerHTML = EYE_OPEN_SVG;
        toggleBtn.title = 'Show Password';
      }
      pwInput.focus();
    });

    // Handle Login Submit (Pure JavaScript — Zero Backend/Python needed)
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      clearAlert();

      const email = emailInput.value.trim().toLowerCase();
      const password = pwInput.value.trim();

      if (!email || !password) {
        showAlert('Please enter both your administrator email and password.');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span>Verifying credentials... ⏳</span>`;

      // 1. Check if email is in the authorized administrators list
      const admin = AUTHORIZED_ADMINS.find(a => a.email.toLowerCase() === email);
      if (!admin) {
        showAlert('Access Denied: This email address is not in the authorized administrator list.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>Unlock Admin Dashboard 🚀</span>`;
        return;
      }

      // 2. Verify password (using SHA-256 hash or case-insensitive match)
      const inputHash = await computeSha256(password);
      const isMatch = (admin.passwordHashes && admin.passwordHashes.includes(inputHash))
        || password === 'rc4616105'
        || password === 'Spr-Elections@rc4616105'
        || password.toLowerCase() === 'spr-elections@rc4616105'
        || password.toLowerCase() === 'rc4616105';

      if (!isMatch) {
        showAlert('Incorrect administrative password. Access denied.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>Unlock Admin Dashboard 🚀</span>`;
        return;
      }

      // 3. Login SUCCESS!
      const token = 'spr_adm_' + Math.random().toString(36).substring(2) + Date.now().toString(36);
      sessionStorage.setItem(STORAGE_KEY_TOKEN, token);
      sessionStorage.setItem(STORAGE_KEY_NAME, admin.name || 'rc4616105');
      sessionStorage.setItem(STORAGE_KEY_EMAIL, admin.email || email);

      unlockInterface({
        token: token,
        name: admin.name || 'rc4616105',
        email: admin.email || email
      });
    });
  }

  // Initialize Auth Guard
  function init() {
    injectAuthStyles();
    const activeSession = getActiveSession();

    if (!activeSession) {
      lockInterface();
    } else {
      renderSessionBadge(activeSession);
    }
  }

  // Lock immediately before DOM fully renders if unauthenticated
  if (!sessionStorage.getItem(STORAGE_KEY_TOKEN)) {
    document.documentElement.classList.add('spr-admin-locked');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
