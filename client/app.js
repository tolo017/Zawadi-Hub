// ---------- State ----------
let token = localStorage.getItem('token') || null;
let customer = null;
let dashboard = { points: null, transactions: [], reward: null };
const cart = {};

const apiBase = '';

// ---------- Helpers ----------
async function api(method, url, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${apiBase}${url}`, { method, headers, body: body ? JSON.stringify(body) : null });
  if (!res.ok) {
    // Try to parse error, could be FastAPI validation (array) or plain object
    const errData = await res.json().catch(() => ({ detail: 'Request failed' }));
    const message = Array.isArray(errData.detail)
      ? errData.detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join('; ')
      : errData.detail || `HTTP ${res.status}`;
    throw new Error(message);
  }
  return res.json();
}

function el(id) { return document.getElementById(id); }

// ---------- Auth ----------
function showAuth() {
  el('auth-container').classList.remove('hidden');
  el('dashboard-container').classList.add('hidden');
}
function showDashboard() {
  el('auth-container').classList.add('hidden');
  el('dashboard-container').classList.remove('hidden');
  if (customer) el('user-name-display').textContent = customer.name;
}

// Login/Register toggle
el('show-register-btn').addEventListener('click', () => {
  el('login-form').classList.add('hidden');
  el('register-form').classList.remove('hidden');
});
el('show-login-btn').addEventListener('click', () => {
  el('register-form').classList.add('hidden');
  el('login-form').classList.remove('hidden');
});

// Login handler
el('login-form-element').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = el('login-email').value.trim();
  const password = el('login-password').value;
  const errEl = el('login-error');
  try {
    errEl.classList.add('hidden');
    const data = await api('POST', '/auth/login', { email, password });
    token = data.access_token;
    localStorage.setItem('token', token);
    await loadUser();
    showDashboard();
    console.log('User loaded:', customer);
    await loadDashboardData();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
});

// Register handler
el('register-form-element').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = el('reg-name').value.trim();
  const email = el('reg-email').value.trim();
  const password = el('reg-password').value;
  const errEl = el('register-error');
  try {
    errEl.classList.add('hidden');
    await api('POST', '/auth/register', { name, email, password });
    alert('Registration successful! You can now log in.');
    el('register-form').classList.add('hidden');
    el('login-form').classList.remove('hidden');
    el('reg-name').value = '';
    el('reg-email').value = '';
    el('reg-password').value = '';
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
});

// ---------- Delegated global click handler ----------
document.addEventListener('click', (e) => {
  // Logout
  if (e.target.id === 'logout-btn') {
    localStorage.removeItem('token');
    token = null;
    customer = null;
    for (const key of Object.keys(cart)) delete cart[key];
    showAuth();
  }
  // Toggle to register form
  if (e.target.id === 'show-register-btn') {
    el('login-form').classList.add('hidden');
    el('register-form').classList.remove('hidden');
  }
  // Toggle to login form
  if (e.target.id === 'show-login-btn') {
    el('register-form').classList.add('hidden');
    el('login-form').classList.remove('hidden');
  }
});

// ---------- User & Data ----------
async function loadUser() {
  customer = await api('GET', '/auth/me');
}
async function loadDashboardData() {
  try {
    const [pointsData, transactions, reward] = await Promise.all([
      api('GET', '/points'),
      api('GET', '/transactions'),
      api('GET', '/rewards/suggest'),
    ]);
    dashboard = { points: pointsData, transactions, reward };
    console.log('Dashboard data:', dashboard);
    renderAll();
  } catch (err) {
    console.error(err);
    el('dashboard-container').innerHTML = `
      <div class="dashboard-main" style="text-align:center;padding:40px;">
        <h2>⚠️ Failed to load dashboard</h2>
        <p>${err.message}</p>
        <button onclick="location.reload()" class="btn-primary" style="margin-top:16px;">Retry</button>
      </div>`;
  }
}

// ---------- Render functions ----------
function renderAll() {
  renderPoints();
  renderTier();
  renderTransactions();
  renderReward();
  renderMenu();
}

function renderPoints() {
  const p = dashboard.points;
  el('points-card').innerHTML = `
    <div class="points-header">
      <div>
        <div class="points-label">Available Points</div>
        <div class="points-value">${p.points_balance} pts</div>
      </div>
      <div style="text-align:right;">
        <div class="points-label">Loyalty Card</div>
        <div class="card-number">${customer.loyalty_card_number}</div>
      </div>
    </div>
    <div style="margin-top:16px;">${customer.name}</div>
  `;
}

function renderTier() {
  const info = dashboard.points.tier_info;
  const tierClass = `tier-${info.current_tier}`;
  el('tier-badge').innerHTML = `
    <div class="tier-badge ${tierClass}">${info.current_tier} tier</div>
    <p style="color:#4b5563;">Total spent: <strong>$${info.total_spent.toFixed(2)}</strong></p>
    ${info.next_tier ? `
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" style="width:${info.progress_pct}%"></div>
        </div>
        <div class="progress-text">$${(info.next_spend_goal - info.total_spent).toFixed(2)} to ${info.next_tier.toUpperCase()}</div>
      </div>
    ` : `<p style="color:#d97706;font-weight:600;margin-top:8px;">🎉 Max tier reached!</p>`}
  `;
}

function renderTransactions() {
  const tx = dashboard.transactions;
  let html = '<h2 style="font-size:1.3rem;margin-bottom:16px;">Recent Transactions</h2>';
  if (tx.length === 0) {
    html += '<p style="color:#9ca3af;">No transactions yet.</p>';
  } else {
    html += tx.map(t => `
      <div class="transaction-item">
        <div class="tx-details">
          <span class="tx-name">${t.items.join(', ')}</span>
          <span class="tx-meta">${new Date(t.created_at).toLocaleDateString()} · ${t.category}</span>
        </div>
        <div class="tx-points">+${t.points_earned} pts</div>
      </div>
    `).join('');
  }
  el('transactions-list').innerHTML = html;
}

function renderReward() {
  const r = dashboard.reward;
  if (!r) {
    el('reward-card').innerHTML = '<p>Loading reward...</p>';
    return;
  }
  el('reward-card').innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
      <div>
        <h2 style="font-size:1.3rem;color:#92400e;">${r.is_personalized ? '🎯 FlavorPrint Reward' : '🌟 Special Offer'}</h2>
        <p style="margin-top:8px;font-size:1.1rem;">${r.reward_description}</p>
        <p style="color:#6b7280;font-size:0.85rem;margin-top:4px;">
          ${r.discount_percent}% off · Expires ${new Date(r.expires_at).toLocaleDateString()}
        </p>
      </div>
      <button id="redeem-btn" class="btn-primary" ${r.redeemed ? 'disabled' : ''}>${r.redeemed ? 'Redeemed' : 'Redeem'}</button>
    </div>
    <p id="redeem-error" class="error-msg hidden"></p>
  `;
  if (!r.redeemed) {
    el('redeem-btn').addEventListener('click', async () => {
      try {
        await api('POST', `/rewards/redeem/${r.id}`);
        await loadDashboardData();
      } catch (err) {
        el('redeem-error').textContent = err.message;
        el('redeem-error').classList.remove('hidden');
      }
    });
  }
}

// ---------- Menu & Cart ----------
const menuItems = [
  { id: 'mango-smoothie', name: 'Mango Smoothie', price: 5, category: 'drink', emoji: '🥭' },
  { id: 'latte', name: 'Latte', price: 4.5, category: 'drink', emoji: '☕' },
  { id: 'croissant', name: 'Croissant', price: 4, category: 'food', emoji: '🥐' },
  { id: 'espresso', name: 'Espresso', price: 3, category: 'drink', emoji: '☕' },
  { id: 'banana-bread', name: 'Banana Bread', price: 4, category: 'food', emoji: '🍌' },
];

function getCartTotal() {
  return Object.entries(cart).reduce((sum, [id, qty]) => {
    const item = menuItems.find(i => i.id === id);
    return sum + item.price * qty;
  }, 0);
}

function updateCartCounter(id, delta) {
  if (!cart[id]) cart[id] = 0;
  cart[id] += delta;
  if (cart[id] <= 0) delete cart[id];
  renderMenu(); // re-render to update quantities and total
}

async function checkout() {
  if (Object.keys(cart).length === 0) return;
  const items = [];
  const categories = new Set();
  for (const [id, qty] of Object.entries(cart)) {
    const item = menuItems.find(i => i.id === id);
    for (let i = 0; i < qty; i++) {
      items.push(item.name);
      categories.add(item.category);
    }
  }
  const category = categories.size > 1 ? 'combo' : [...categories][0] || 'food';
  const total_amount = getCartTotal();
  try {
    await api('POST', '/transactions', { items, total_amount, category });
    // Clear cart and refresh data
    Object.keys(cart).forEach(id => delete cart[id]);
    await loadDashboardData();
  } catch (err) {
    alert(`Checkout failed: ${err.message}`);
  }
}

function renderMenu() {
  let html = '<h2 style="font-size:1.3rem;margin-bottom:12px;">Menu</h2>';
  html += '<div class="menu-grid">';
  menuItems.forEach(item => {
    const qty = cart[item.id] || 0;
    html += `
      <div class="menu-item">
        <div class="item-emoji">${item.emoji}</div>
        <div class="item-name">${item.name}</div>
        <span class="item-category">${item.category}</span>
        <div class="item-price">$${item.price.toFixed(2)}</div>
        <div class="quantity-control">
          <button class="qty-btn" data-action="minus" data-id="${item.id}">−</button>
          <span class="qty-value">${qty}</span>
          <button class="qty-btn" data-action="plus" data-id="${item.id}">+</button>
        </div>
      </div>`;
  });
  html += '</div>';
  const total = getCartTotal();
  if (total > 0) {
    html += `
      <div class="cart-summary">
        <span class="total-label">Order Total</span>
        <span class="total-price">$${total.toFixed(2)}</span>
        <button id="pay-btn" class="btn-primary">Pay & Earn Points</button>
      </div>`;
  }
  el('menu-order').innerHTML = html;

  // Attach quantity button listeners
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = e.currentTarget.dataset.id;
      const action = e.currentTarget.dataset.action;
      updateCartCounter(id, action === 'plus' ? 1 : -1);
    });
  });

  const payBtn = el('pay-btn');
  if (payBtn) payBtn.addEventListener('click', checkout);
}

// ---------- Init ----------
(async () => {
  if (token) {
    try {
      await loadUser();
      showDashboard();
      await loadDashboardData();
    } catch (e) {
      token = null;
      localStorage.removeItem('token');
      showAuth();
    }
  } else {
    showAuth();
  }
})();
