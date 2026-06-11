/* ─── Ảnh thật theo loại sản phẩm (Unsplash) ─────────────────────────────── */
const TYPE_IMAGES = {
  electronics: [
    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=480&q=80', // laptop
    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=480&q=80', // phone
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=480&q=80', // headphones
    'https://images.unsplash.com/photo-1593640408182-31c228b523a9?w=480&q=80', // keyboard
    'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=480&q=80', // monitor
    'https://images.unsplash.com/photo-1601524909162-ae8725290836?w=480&q=80', // airpods
    'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=480&q=80', // smartwatch
    'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=480&q=80', // tablet
  ],
  book: [
    'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=480&q=80',
    'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=480&q=80',
    'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=480&q=80',
    'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=480&q=80',
    'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=480&q=80',
  ],
  fashion: [
    'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=480&q=80', // clothes
    'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=480&q=80',   // shoes
    'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=480&q=80', // shirt
    'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=480&q=80', // tshirt
    'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=480&q=80',   // sneakers
    'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=480&q=80', // jacket
  ],
  food: [
    'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=480&q=80',
    'https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=480&q=80',
    'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=480&q=80',
    'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=480&q=80',
  ],
  sports: [
    'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=480&q=80',
    'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=480&q=80',
    'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=480&q=80',
    'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=480&q=80',
  ],
  beauty: [
    'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=480&q=80',
    'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=480&q=80',
    'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=480&q=80',
  ],
  furniture: [
    'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=480&q=80',
    'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=480&q=80',
    'https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=480&q=80',
  ],
  toys: [
    'https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=480&q=80',
    'https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=480&q=80',
  ],
  automotive: [
    'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=480&q=80',
    'https://images.unsplash.com/photo-1502877338535-766e1452684a?w=480&q=80',
  ],
  other: [
    'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=480&q=80',
  ],
};

/* Lấy ảnh phù hợp theo loại và id sản phẩm */
function getTypeImage(type, id = 0) {
  const imgs = TYPE_IMAGES[type] || TYPE_IMAGES.other;
  return imgs[Math.abs(id) % imgs.length];
}

/* ─── Product visual helpers ───────────────────────────────────────────────── */
const PRODUCT_VISUAL = {
  electronics: { gradient: 'linear-gradient(135deg,#1e3a5f,#2563eb)', icon: '💻', color: '#2563eb' },
  book:        { gradient: 'linear-gradient(135deg,#3b1f6e,#7c3aed)', icon: '📚', color: '#7c3aed' },
  fashion:     { gradient: 'linear-gradient(135deg,#831843,#ec4899)', icon: '👗', color: '#ec4899' },
  food:        { gradient: 'linear-gradient(135deg,#7c2d12,#f97316)', icon: '🍜', color: '#f97316' },
  sports:      { gradient: 'linear-gradient(135deg,#14532d,#22c55e)', icon: '⚽', color: '#22c55e' },
  beauty:      { gradient: 'linear-gradient(135deg,#701a75,#d946ef)', icon: '💄', color: '#d946ef' },
  furniture:   { gradient: 'linear-gradient(135deg,#431407,#92400e)', icon: '🛋️', color: '#92400e' },
  toys:        { gradient: 'linear-gradient(135deg,#713f12,#eab308)', icon: '🧸', color: '#eab308' },
  automotive:  { gradient: 'linear-gradient(135deg,#1c1917,#44403c)', icon: '🚗', color: '#44403c' },
  other:       { gradient: 'linear-gradient(135deg,#1e293b,#475569)', icon: '📦', color: '#475569' },
};

function getVisual(type) {
  return PRODUCT_VISUAL[type] || PRODUCT_VISUAL.other;
}

/* Render ảnh sản phẩm — dùng ảnh thật Unsplash, fallback về emoji */
function productImageHtml(product, height = '220px') {
  const url = product.image_url || getTypeImage(product.product_type, product.id);
  const v   = getVisual(product.product_type);
  return `<img src="${url}" alt="${product.name}"
    style="width:100%;height:${height};object-fit:cover;transition:transform .4s ease"
    onerror="this.replaceWith(Object.assign(document.createElement('div'),{
      style:'width:100%;height:${height};background:${v.gradient};display:flex;align-items:center;justify-content:center;font-size:5rem',
      innerHTML:'${v.icon}'
    }))">`;
}

function productImgFallback(type, height = '220px') {
  const v = getVisual(type);
  return `<div style="width:100%;height:${height};background:${v.gradient};
    display:flex;align-items:center;justify-content:center;font-size:calc(${height} * 0.35)">${v.icon}</div>`;
}

/* ─── Mock products — ảnh khớp 100% với seed_data.py ─────────────────────── */
const MOCK_PRODUCTS = [
  { id:1,  name:'Laptop ASUS ROG G15 (2024)',        price:19500000, original_price:22000000, product_type:'electronics', rating:4.9, sold_count:312,  image_url:'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=480&q=80' },
  { id:2,  name:'iPhone 15 Pro Max 256GB',            price:34990000, original_price:null,     product_type:'electronics', rating:4.8, sold_count:524,  image_url:'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=480&q=80' },
  { id:3,  name:'Samsung Galaxy S24 Ultra',           price:32990000, original_price:null,     product_type:'electronics', rating:4.75,sold_count:445,  image_url:'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=480&q=80' },
  { id:4,  name:'Tai nghe Sony WH-1000XM5',           price:8490000,  original_price:9990000,  product_type:'electronics', rating:4.9, sold_count:891,  image_url:'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=480&q=80' },
  { id:5,  name:'Màn hình LG UltraWide 34" 144Hz',   price:9990000,  original_price:12000000, product_type:'electronics', rating:4.8, sold_count:267,  image_url:'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=480&q=80' },
  { id:6,  name:'Apple Watch Series 9 GPS 45mm',     price:11990000, original_price:null,     product_type:'electronics', rating:4.85,sold_count:345,  image_url:'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=480&q=80' },
  { id:7,  name:'Bàn phím cơ Keychron K2 Pro',       price:2190000,  original_price:null,     product_type:'electronics', rating:4.9, sold_count:1456, image_url:'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=480&q=80' },
  { id:8,  name:'Chuột Razer DeathAdder V3',          price:1890000,  original_price:2200000,  product_type:'electronics', rating:4.8, sold_count:723,  image_url:'https://images.unsplash.com/photo-1527814050087-3793815479db?w=480&q=80' },
  { id:9,  name:'Clean Code - Robert C. Martin',     price:180000,   original_price:220000,   product_type:'book',        rating:4.9, sold_count:2341, image_url:'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=480&q=80' },
  { id:10, name:'Domain-Driven Design - Eric Evans', price:350000,   original_price:null,     product_type:'book',        rating:4.8, sold_count:567,  image_url:'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=480&q=80' },
  { id:11, name:'Tư duy như Elon Musk',              price:159000,   original_price:199000,   product_type:'book',        rating:4.6, sold_count:1205, image_url:'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=480&q=80' },
  { id:12, name:'The Psychology of Money',           price:145000,   original_price:185000,   product_type:'book',        rating:4.8, sold_count:1876, image_url:'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=480&q=80' },
  { id:13, name:'Atomic Habits - James Clear',       price:168000,   original_price:210000,   product_type:'book',        rating:4.9, sold_count:3240, image_url:'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=480&q=80' },
  { id:14, name:'Áo Polo Lacoste Classic Fit',       price:1290000,  original_price:1800000,  product_type:'fashion',     rating:4.7, sold_count:678,  image_url:'https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=480&q=80' },
  { id:15, name:'Giày Nike Air Force 1 White',       price:2490000,  original_price:2890000,  product_type:'fashion',     rating:4.8, sold_count:934,  image_url:'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=480&q=80' },
  { id:16, name:'Giày Adidas Ultraboost 22',         price:3290000,  original_price:3890000,  product_type:'fashion',     rating:4.7, sold_count:512,  image_url:'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=480&q=80' },
  { id:17, name:'Áo khoác The North Face Resolve',   price:3490000,  original_price:4500000,  product_type:'fashion',     rating:4.6, sold_count:389,  image_url:'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=480&q=80' },
].map(p => ({
  ...p,
  discount_percent: p.original_price ? Math.round((1 - p.price/p.original_price)*100) : 0,
  description: `${p.name} — sản phẩm chất lượng cao được nhiều khách hàng tin tưởng.`,
  stock: 50,
}));
