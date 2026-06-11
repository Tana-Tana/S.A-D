/* ═══════════════════════════════════════════════════════════════
   EcomAI Chatbot Widget
   - Lưu lịch sử vào localStorage (không mất khi đóng/mở)
   - Hiển thị product cards với ảnh, giá, nút Xem + Giỏ
   ═══════════════════════════════════════════════════════════════ */

const Chatbot = {
  isOpen: false,

  init() {
    this._restoreMessages();
    // Đóng bằng ESC
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && this.isOpen) this.toggle(); });
  },

  toggle() {
    this.isOpen = !this.isOpen;
    document.getElementById('chatbot-panel').classList.toggle('hidden', !this.isOpen);
    document.getElementById('chatbot-icon').className = this.isOpen ? 'fas fa-times' : 'fas fa-robot';
    if (this.isOpen) {
      this._scrollBottom();
      setTimeout(() => document.getElementById('chatbot-input')?.focus(), 100);
    }
  },

  async send() {
    const input = document.getElementById('chatbot-input');
    const msg   = input.value.trim();
    if (!msg) return;
    input.value = '';

    this._appendText(msg, 'user');
    ChatStore.pushMessage('user', msg);

    const typing = this._appendTyping();

    try {
      const history = ChatStore.getApiHistory();
      const res     = await API.chat(msg, history);
      typing.remove();

      const answer = res.answer || 'Xin lỗi, tôi chưa hiểu. Bạn thử hỏi lại nhé!';
      this._appendText(answer, 'bot');
      ChatStore.pushMessage('bot', answer);

      // Lưu API history
      history.push({ role: 'user', content: msg }, { role: 'assistant', content: answer });
      ChatStore.saveApiHistory(history);

      // Hiển thị product cards
      if (res.recommended_products?.length) {
        this._appendProducts(res.recommended_products.slice(0, 3));
      }
    } catch {
      typing.remove();
      const errMsg = 'Không kết nối được AI service. Vui lòng thử lại!';
      this._appendText(errMsg, 'bot');
      ChatStore.pushMessage('bot', errMsg);
    }
  },

  clear() {
    ChatStore.clear();
    const box = document.getElementById('chatbot-messages');
    box.innerHTML = `
      <div class="message bot">Xin chào! 👋 Tôi là trợ lý mua sắm AI.</div>
      <div class="message bot">Thử hỏi: <em>"laptop gaming dưới 20 triệu"</em> hoặc <em>"áo thun nam"</em> 😊</div>`;
  },

  _appendText(text, role) {
    const box = document.getElementById('chatbot-messages');
    const el  = document.createElement('div');
    el.className = `message ${role}`;
    el.textContent = text;
    box.appendChild(el);
    this._scrollBottom();
    return el;
  },

  _appendTyping() {
    const box = document.getElementById('chatbot-messages');
    const el  = document.createElement('div');
    el.className = 'message bot';
    el.innerHTML = '<span style="opacity:.6">Đang tư vấn</span> <span class="typing-dots">...</span>';
    box.appendChild(el);
    this._scrollBottom();
    return el;
  },

  _appendProducts(products, save = true) {
    const box  = document.getElementById('chatbot-messages');
    const wrap = document.createElement('div');
    wrap.className = 'chatbot-products';
    wrap.style.cssText = 'display:flex;flex-direction:column;gap:.5rem;width:100%;animation:fadeInUp .3s ease';

    products.forEach(p => {
      const pid   = parseInt(p.product_id || p.id || 1);
      const name  = p.name || 'Sản phẩm';
      const price = parseFloat(p.price) || 0;
      const type  = p.product_type || p.type || 'other';
      // Ưu tiên: image_url từ API → ảnh đúng trong MOCK_PRODUCTS theo ID → fallback getTypeImage
      const mockMatch = typeof MOCK_PRODUCTS !== 'undefined' ? MOCK_PRODUCTS.find(m => m.id === pid) : null;
      const img   = p.image_url || mockMatch?.image_url || (typeof getTypeImage !== 'undefined' ? getTypeImage(type, pid) : '');
      const v     = typeof getVisual !== 'undefined' ? getVisual(type) : { gradient:'linear-gradient(135deg,#4f46e5,#7c3aed)', icon:'📦' };
      const priceStr = typeof fmt !== 'undefined' ? fmt.price(price) : price.toLocaleString('vi-VN') + ' ₫';

      const card = document.createElement('div');
      card.style.cssText = 'background:#fff;border-radius:12px;display:flex;gap:.7rem;padding:.7rem;box-shadow:0 2px 8px rgba(0,0,0,.08);border:1px solid #f1f5f9;cursor:pointer;transition:box-shadow .2s';
      card.onmouseover = () => card.style.boxShadow = '0 4px 16px rgba(0,0,0,.15)';
      card.onmouseout  = () => card.style.boxShadow = '0 2px 8px rgba(0,0,0,.08)';
      card.onclick = () => location.href = `product-detail.html?id=${pid}`;
      card.innerHTML = `
        <div style="width:64px;height:64px;border-radius:8px;overflow:hidden;flex-shrink:0;background:${v.gradient};display:flex;align-items:center;justify-content:center">
          <img src="${img}" style="width:100%;height:100%;object-fit:cover"
            onerror="this.style.display='none';this.parentElement.innerHTML='<span style=font-size:1.8rem>${v.icon}</span>'">
        </div>
        <div style="flex:1;min-width:0">
          <div style="font-size:.78rem;font-weight:700;color:#1e293b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${name}">${name}</div>
          <div style="font-size:.82rem;font-weight:800;color:#4f46e5;margin:.2rem 0">${priceStr}</div>
          <div style="display:flex;gap:.35rem;flex-wrap:wrap">
            <a href="product-detail.html?id=${pid}"
               style="font-size:.7rem;background:#f1f5f9;color:#475569;border-radius:5px;padding:.2rem .5rem;text-decoration:none;font-weight:600"
               onclick="event.stopPropagation()">👁 Xem</a>
            <button
               onclick="event.stopPropagation();Cart.add({id:${pid},name:${JSON.stringify(name)},price:${price},product_type:${JSON.stringify(type)},image_url:${JSON.stringify(img)}});Toast.show('Đã thêm vào giỏ!')"
               style="font-size:.7rem;background:#4f46e5;color:#fff;border:none;border-radius:5px;padding:.2rem .5rem;font-weight:600;cursor:pointer">🛒 Giỏ</button>
          </div>
        </div>`;
      wrap.appendChild(card);
    });

    box.appendChild(wrap);
    this._scrollBottom();

    // Lưu products vào localStorage để restore sau
    if (save) {
      const msgs = ChatStore.getMessages();
      msgs.push({ role: 'products', products, ts: Date.now() });
      ChatStore.saveMessages(msgs);
    }
  },

  _restoreMessages() {
    const msgs = ChatStore.getMessages();
    const box  = document.getElementById('chatbot-messages');
    if (!box) return;

    if (!msgs.length) {
      box.innerHTML = `
        <div class="message bot">Xin chào! 👋 Tôi là trợ lý mua sắm AI.</div>
        <div class="message bot">Thử hỏi: <em>"laptop gaming"</em>, <em>"sách hay"</em> hoặc <em>"giày thể thao"</em> 😊</div>`;
      return;
    }

    box.innerHTML = '';
    msgs.forEach(m => {
      if (m.role === 'products') {
        // Render lại product cards từ dữ liệu đã lưu
        this._appendProducts(m.products, false);
      } else {
        const el = document.createElement('div');
        el.className = `message ${m.role}`;
        el.textContent = m.text;
        box.appendChild(el);
      }
    });

    const notice = document.createElement('div');
    notice.style.cssText = 'text-align:center;font-size:.72rem;color:#94a3b8;padding:.4rem;';
    notice.innerHTML = `<i class="fas fa-history"></i> Đã khôi phục lịch sử
      &nbsp;<button onclick="Chatbot.clear()" style="background:none;border:none;color:#4f46e5;font-size:.72rem;cursor:pointer;text-decoration:underline">Xóa</button>`;
    box.appendChild(notice);
    this._scrollBottom();
  },

  _scrollBottom() {
    const box = document.getElementById('chatbot-messages');
    if (box) setTimeout(() => box.scrollTop = box.scrollHeight, 50);
  },
};

// Gắn vào global functions để HTML có thể gọi
function toggleChatbot() { Chatbot.toggle(); }
function sendChat()      { Chatbot.send();  }

// Khởi tạo — xử lý cả trường hợp DOM đã ready hoặc chưa
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Chatbot.init());
} else {
  Chatbot.init(); // Script load sau DOMContentLoaded — gọi thẳng
}

// Cho phép Enter gửi tin
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.activeElement?.id === 'chatbot-input') {
    e.preventDefault();
    Chatbot.send();
  }
});
