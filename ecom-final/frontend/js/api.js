/* ═══════════════════════════════════════════════
   EcomAI — API Module
   Base URL: /api (proxied by nginx to services)
   ═══════════════════════════════════════════════ */

const API = {
  base: '',  // relative — cả port 3000 và 80 đều proxy qua gateway

  // ─── Auth ─────────────────────────────────────
  async login(username, password) {
    return this._post('/auth/login/', { username, password });
  },
  async register(data) {
    return this._post('/auth/register/', data);
  },
  async verifyToken() {
    return this._get('/auth/verify/');
  },

  // ─── Products ─────────────────────────────────
  async getProducts(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this._get(`/products/${qs ? '?' + qs : ''}`);
  },
  async getProduct(id) {
    return this._get(`/products/${id}/`);
  },
  async getCategories() {
    return this._get('/categories/');
  },
  async searchProducts(q) {
    return this._get(`/products/search/?q=${encodeURIComponent(q)}`);
  },

  // ─── Cart ─────────────────────────────────────
  async getCart() {
    const userId = Auth.getUserId();
    return this._get(`/cart/?user_id=${userId}`);
  },
  async addToCart(productId, quantity = 1) {
    return this._post('/cart/add/', { user_id: Auth.getUserId(), product_id: productId, quantity });
  },
  async removeFromCart(productId) {
    return this._delete('/cart/remove/', { user_id: Auth.getUserId(), product_id: productId });
  },

  // ─── Orders ───────────────────────────────────
  async createOrder(shippingAddress, note = '') {
    return this._post('/orders/create/', { user_id: Auth.getUserId(), shipping_address: shippingAddress, note });
  },
  async getOrders() {
    return this._get(`/orders/?user_id=${Auth.getUserId()}`);
  },

  // ─── Payment ──────────────────────────────────
  async pay(orderId, amount, method = 'cod') {
    return this._post('/payment/pay/', { order_id: orderId, user_id: Auth.getUserId(), amount, method });
  },

  // ─── AI ───────────────────────────────────────
  async recommend(sequence = []) {
    const userId = Auth.getUserId() || 1;
    const qs = sequence.length
      ? `?user_id=${userId}&behavior_sequence=${sequence.join(',')}&top_k=6`
      : `?user_id=${userId}&behavior_sequence=10,12,15,20&top_k=6`;
    return this._get(`/recommend${qs}`);
  },
  async chat(message, history = []) {
    return this._post('/chatbot', { user_id: Auth.getUserId() || 1, message, chat_history: history });
  },

  // ─── Behavior tracking (cho AI service) ───────
  // Fire-and-forget: không chặn UI, không throw nếu lỗi.
  logEvent(productId, action) {
    if (!productId) return;
    this._post('/events/', {
      user_id: Auth.getUserId() || 1,
      product_id: productId,
      action,
    }).catch(() => {});
  },

  // ─── HTTP helpers ─────────────────────────────
  async _get(path) {
    const res = await fetch(this.base + path, { headers: this._headers() });
    return res.json();
  },
  async _post(path, body) {
    const res = await fetch(this.base + path, {
      method: 'POST',
      headers: { ...this._headers(), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return res.json();
  },
  async _delete(path, body) {
    const res = await fetch(this.base + path, {
      method: 'DELETE',
      headers: { ...this._headers(), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return res.json();
  },
  _headers() {
    const token = Auth.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  },
};

/* ═══════════════════════════════════════════════
   Auth Manager
   ═══════════════════════════════════════════════ */
const Auth = {
  getToken()  { return localStorage.getItem('access_token'); },
  getUser()   { try { return JSON.parse(localStorage.getItem('user')); } catch { return null; } },
  getUserId() { return this.getUser()?.id; },
  isLoggedIn(){ return !!this.getToken(); },

  save(data) {
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
  },

  logout() {
    // Xóa cart của user hiện tại trước khi logout
    const uid = this.getUserId();
    if (uid) localStorage.removeItem(`cart_user_${uid}`);
    ChatStore.clear();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/auth.html';
  },
};

/* ═══════════════════════════════════════════════
   Cart State (localStorage)
   ═══════════════════════════════════════════════ */
const Cart = {
  // Key riêng theo user — giỏ hàng không dùng chung giữa các tài khoản
  get _key() {
    const uid = Auth.getUserId();
    return uid ? `cart_user_${uid}` : 'cart_guest';
  },

  get() {
    try { return JSON.parse(localStorage.getItem(this._key)) || []; } catch { return []; }
  },

  count() { return this.get().reduce((s, i) => s + i.quantity, 0); },

  add(product, qty = 1) {
    const items = this.get();
    const idx = items.findIndex(i => i.product_id === product.id);
    if (idx > -1) items[idx].quantity += qty;
    else items.push({
      product_id:    product.id,
      product_name:  product.name,
      product_price: product.price,
      product_image: product.image_url,
      quantity: qty,
    });
    localStorage.setItem(this._key, JSON.stringify(items));
    this._updateBadge();
    API.logEvent(product.id, 'add_to_cart');
  },

  remove(productId) {
    const items = this.get().filter(i => i.product_id !== productId);
    localStorage.setItem(this._key, JSON.stringify(items));
    this._updateBadge();
  },

  updateQty(productId, qty) {
    const items = this.get().map(i => i.product_id === productId ? { ...i, quantity: qty } : i);
    localStorage.setItem(this._key, JSON.stringify(items.filter(i => i.quantity > 0)));
    this._updateBadge();
  },

  total() { return this.get().reduce((s, i) => s + (parseFloat(i.product_price) * i.quantity), 0); },

  clear() { localStorage.removeItem(this._key); this._updateBadge(); },

  _updateBadge() {
    const badges = document.querySelectorAll('.cart-count');
    const count = this.count();
    badges.forEach(b => { b.textContent = count; b.classList.toggle('hidden', count === 0); });
  },
};

/* ═══════════════════════════════════════════════
   Chatbot History — lưu vào localStorage
   ═══════════════════════════════════════════════ */
const ChatStore = {
  _API_KEY:  'chatbot_api_history',   // [{role, content}] — gửi lên API
  _MSG_KEY:  'chatbot_messages',      // [{role, text}]    — hiển thị lại

  getApiHistory()  { try { return JSON.parse(localStorage.getItem(this._API_KEY)) || []; } catch { return []; } },
  getMessages()    { try { return JSON.parse(localStorage.getItem(this._MSG_KEY)) || []; } catch { return []; } },

  saveApiHistory(h) { localStorage.setItem(this._API_KEY, JSON.stringify(h.slice(-20))); },
  saveMessages(m)   { localStorage.setItem(this._MSG_KEY, JSON.stringify(m.slice(-40))); },

  pushMessage(role, text) {
    const msgs = this.getMessages();
    msgs.push({ role, text, ts: Date.now() });
    this.saveMessages(msgs);
  },

  clear() {
    localStorage.removeItem(this._API_KEY);
    localStorage.removeItem(this._MSG_KEY);
  },
};

/* ═══════════════════════════════════════════════
   Toast Notifications
   ═══════════════════════════════════════════════ */
const Toast = {
  show(msg, type = 'success') {
    let container = document.querySelector('.toast-container-custom');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container-custom';
      document.body.appendChild(container);
    }
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast-custom ${type !== 'success' ? type : ''}`;
    toast.innerHTML = `<span>${icons[type] || '✅'}</span><span>${msg}</span>`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .3s'; setTimeout(() => toast.remove(), 300); }, 3000);
  },
};

/* ═══════════════════════════════════════════════
   Helpers
   ═══════════════════════════════════════════════ */
const fmt = {
  price: (n) => new Intl.NumberFormat('vi-VN').format(n) + ' ₫',
  stars: (r) => '★'.repeat(Math.round(r)) + '☆'.repeat(5 - Math.round(r)),
  typeIcon: (t) => ({ book: '📚', electronics: '💻', fashion: '👗', food: '🍜', sports: '⚽', beauty: '💄', toys: '🧸', furniture: '🛋️', automotive: '🚗', other: '📦' }[t] || '📦'),
  typeLabel: (t) => ({ book: 'Sách', electronics: 'Điện tử', fashion: 'Thời trang', food: 'Thực phẩm', sports: 'Thể thao', beauty: 'Làm đẹp', toys: 'Đồ chơi', furniture: 'Nội thất', automotive: 'Ô tô - Xe máy', other: 'Khác' }[t] || t),
};

// Update navbar on load
document.addEventListener('DOMContentLoaded', () => {
  Cart._updateBadge();
  const user = Auth.getUser();
  const authArea = document.getElementById('auth-area');
  if (authArea) {
    if (user) {
      const avatar = (user.first_name || user.username || 'U')[0].toUpperCase();
      authArea.innerHTML = `
        <div class="d-flex align-items-center gap-2">
          <div style="width:32px;height:32px;background:var(--primary);border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;flex-shrink:0">${avatar}</div>
          <span style="color:var(--gray-700);font-size:.875rem;font-weight:600;max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${user.first_name || user.username}</span>
          <button onclick="Auth.logout()"
            style="background:none;border:1.5px solid var(--gray-200);border-radius:8px;padding:.3rem .75rem;font-size:.8rem;font-weight:600;color:var(--gray-600);cursor:pointer;transition:all .2s;white-space:nowrap"
            onmouseover="this.style.borderColor='var(--danger)';this.style.color='var(--danger)'"
            onmouseout="this.style.borderColor='var(--gray-200)';this.style.color='var(--gray-600)'">
            <i class="fas fa-sign-out-alt me-1"></i>Đăng xuất
          </button>
        </div>`;
    } else {
      authArea.innerHTML = `
        <a href="/auth.html"
          style="background:var(--primary);color:#fff;border-radius:8px;padding:.4rem 1rem;font-size:.875rem;font-weight:600;text-decoration:none;display:inline-flex;align-items:center;gap:.4rem;transition:all .2s"
          onmouseover="this.style.background='var(--primary-dark)'"
          onmouseout="this.style.background='var(--primary)'">
          <i class="fas fa-user"></i> Đăng nhập
        </a>`;
    }
  }
});
