"""
Django management command: seed_data
Tạo dữ liệu mẫu cho product-service với ảnh Unsplash đúng cho từng sản phẩm.
"""
from django.core.management.base import BaseCommand
from products.models import Category, Product, Book, Electronics, Fashion


CATEGORIES = [
    {'name': 'Điện tử',    'slug': 'electronics'},
    {'name': 'Sách',       'slug': 'books'},
    {'name': 'Thời trang', 'slug': 'fashion'},
    {'name': 'Thể thao',   'slug': 'sports'},
    {'name': 'Làm đẹp',   'slug': 'beauty'},
    {'name': 'Thực phẩm',  'slug': 'food'},
    {'name': 'Nội thất',   'slug': 'furniture'},
]

# Ảnh Unsplash cụ thể cho từng sản phẩm
PRODUCTS_DATA = [
    # ID 1 — Electronics
    {'name': 'Laptop ASUS ROG G15 (2024)', 'price': 19500000, 'original_price': 22000000,
     'type': 'electronics', 'cat': 'electronics', 'stock': 25, 'rating': '4.90', 'sold': 312,
     'image': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=480&q=80',
     'brand': 'ASUS', 'warranty': 24, 'specs': {'CPU': 'AMD Ryzen 9', 'RAM': '16GB', 'GPU': 'RTX 4060', 'Màn hình': '15.6" FHD 144Hz'}},

    # ID 2
    {'name': 'iPhone 15 Pro Max 256GB', 'price': 34990000, 'original_price': None,
     'type': 'electronics', 'cat': 'electronics', 'stock': 40, 'rating': '4.80', 'sold': 524,
     'image': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=480&q=80',
     'brand': 'Apple', 'warranty': 12, 'specs': {'Chip': 'A17 Pro', 'Camera': '48MP', 'Pin': '4422mAh', 'Màn hình': '6.7" Super Retina XDR'}},

    # ID 3
    {'name': 'Samsung Galaxy S24 Ultra', 'price': 32990000, 'original_price': None,
     'type': 'electronics', 'cat': 'electronics', 'stock': 35, 'rating': '4.75', 'sold': 445,
     'image': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=480&q=80',
     'brand': 'Samsung', 'warranty': 12, 'specs': {'CPU': 'Snapdragon 8 Gen 3', 'RAM': '12GB', 'Camera': '200MP'}},

    # ID 4
    {'name': 'Tai nghe Sony WH-1000XM5', 'price': 8490000, 'original_price': 9990000,
     'type': 'electronics', 'cat': 'electronics', 'stock': 60, 'rating': '4.90', 'sold': 891,
     'image': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=480&q=80',
     'brand': 'Sony', 'warranty': 12, 'specs': {'ANC': 'Có', 'Pin': '30h', 'Kết nối': 'Bluetooth 5.2'}},

    # ID 5
    {'name': 'Màn hình LG UltraWide 34" 144Hz', 'price': 9990000, 'original_price': 12000000,
     'type': 'electronics', 'cat': 'electronics', 'stock': 18, 'rating': '4.80', 'sold': 267,
     'image': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=480&q=80',
     'brand': 'LG', 'warranty': 24, 'specs': {'Kích thước': '34"', 'Độ phân giải': '3440x1440', 'Hz': '144'}},

    # ID 6
    {'name': 'Apple Watch Series 9 GPS 45mm', 'price': 11990000, 'original_price': None,
     'type': 'electronics', 'cat': 'electronics', 'stock': 30, 'rating': '4.85', 'sold': 345,
     'image': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=480&q=80',
     'brand': 'Apple', 'warranty': 12, 'specs': {'Màn hình': 'OLED', 'Chip': 'S9', 'GPS': 'Có', 'Pin': '18h'}},

    # ID 7
    {'name': 'Bàn phím cơ Keychron K2 Pro', 'price': 2190000, 'original_price': None,
     'type': 'electronics', 'cat': 'electronics', 'stock': 80, 'rating': '4.90', 'sold': 1456,
     'image': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=480&q=80',
     'brand': 'Keychron', 'warranty': 12, 'specs': {'Layout': '75%', 'Switch': 'Gateron G Pro', 'Kết nối': 'BT/USB-C'}},

    # ID 8
    {'name': 'Chuột Razer DeathAdder V3', 'price': 1890000, 'original_price': 2200000,
     'type': 'electronics', 'cat': 'electronics', 'stock': 50, 'rating': '4.80', 'sold': 723,
     'image': 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=480&q=80',
     'brand': 'Razer', 'warranty': 12, 'specs': {'DPI': '30000', 'Nút': '6', 'Trọng lượng': '59g'}},

    # ID 9 — Books
    {'name': 'Clean Code - Robert C. Martin', 'price': 180000, 'original_price': 220000,
     'type': 'book', 'cat': 'books', 'stock': 200, 'rating': '4.90', 'sold': 2341,
     'image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=480&q=80',
     'author': 'Robert C. Martin', 'publisher': 'Prentice Hall', 'isbn': '9780132350884', 'pages': 464, 'lang': 'Tiếng Anh'},

    # ID 10
    {'name': 'Domain-Driven Design - Eric Evans', 'price': 350000, 'original_price': None,
     'type': 'book', 'cat': 'books', 'stock': 150, 'rating': '4.80', 'sold': 567,
     'image': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=480&q=80',
     'author': 'Eric Evans', 'publisher': 'Addison-Wesley', 'isbn': '9780321125217', 'pages': 560, 'lang': 'Tiếng Anh'},

    # ID 11
    {'name': 'Tư duy như Elon Musk', 'price': 159000, 'original_price': 199000,
     'type': 'book', 'cat': 'books', 'stock': 300, 'rating': '4.60', 'sold': 1205,
     'image': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=480&q=80',
     'author': 'Ashlee Vance', 'publisher': 'NXB Dân Trí', 'isbn': '9786049942259', 'pages': 392, 'lang': 'Tiếng Việt'},

    # ID 12
    {'name': 'The Psychology of Money', 'price': 145000, 'original_price': 185000,
     'type': 'book', 'cat': 'books', 'stock': 250, 'rating': '4.80', 'sold': 1876,
     'image': 'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=480&q=80',
     'author': 'Morgan Housel', 'publisher': 'Harriman House', 'isbn': '9780857197689', 'pages': 256, 'lang': 'Tiếng Anh'},

    # ID 13
    {'name': 'Atomic Habits - James Clear', 'price': 168000, 'original_price': 210000,
     'type': 'book', 'cat': 'books', 'stock': 280, 'rating': '4.90', 'sold': 3240,
     'image': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=480&q=80',
     'author': 'James Clear', 'publisher': 'Avery', 'isbn': '9780735211292', 'pages': 320, 'lang': 'Tiếng Anh'},

    # ID 14 — Fashion
    {'name': 'Áo Polo Lacoste Classic Fit', 'price': 1290000, 'original_price': 1800000,
     'type': 'fashion', 'cat': 'fashion', 'stock': 100, 'rating': '4.70', 'sold': 678,
     'image': 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=480&q=80',
     'brand': 'Lacoste', 'size': 'L', 'color': 'Trắng', 'material': 'Cotton Pique 100%'},

    # ID 15
    {'name': 'Giày Nike Air Force 1 White', 'price': 2490000, 'original_price': 2890000,
     'type': 'fashion', 'cat': 'fashion', 'stock': 75, 'rating': '4.80', 'sold': 934,
     'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=480&q=80',
     'brand': 'Nike', 'size': 'M', 'color': 'Trắng', 'material': 'Da tổng hợp cao cấp'},

    # ID 16
    {'name': 'Giày Adidas Ultraboost 22', 'price': 3290000, 'original_price': 3890000,
     'type': 'fashion', 'cat': 'fashion', 'stock': 60, 'rating': '4.70', 'sold': 512,
     'image': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=480&q=80',
     'brand': 'Adidas', 'size': 'M', 'color': 'Đen/Trắng', 'material': 'Primeknit+'},

    # ID 17
    {'name': 'Áo khoác The North Face Resolve', 'price': 3490000, 'original_price': 4500000,
     'type': 'fashion', 'cat': 'fashion', 'stock': 40, 'rating': '4.60', 'sold': 389,
     'image': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=480&q=80',
     'brand': 'The North Face', 'size': 'XL', 'color': 'Xanh Navy', 'material': 'Polyester chống nước'},
]


class Command(BaseCommand):
    help = 'Seed sample products into database'

    def handle(self, *args, **options):
        if Product.objects.count() > 0:
            self.stdout.write(self.style.WARNING(
                f'Database already has {Product.objects.count()} products. Skipping.'
            ))
            return

        cat_map = {}
        for c in CATEGORIES:
            obj, _ = Category.objects.get_or_create(slug=c['slug'], defaults={'name': c['name']})
            cat_map[c['slug']] = obj
        self.stdout.write(f'✓ Created {len(cat_map)} categories')

        for i, data in enumerate(PRODUCTS_DATA):
            cat = cat_map.get(data['cat'])
            product = Product.objects.create(
                id=i + 1,
                name=data['name'],
                price=data['price'],
                original_price=data.get('original_price'),
                stock=data['stock'],
                sold_count=data['sold'],
                product_type=data['type'],
                category=cat,
                rating=data['rating'],
                image_url=data['image'],      # ← ảnh đúng cho từng sản phẩm
                is_active=True,
                description=f"{data['name']} — sản phẩm chất lượng cao được nhiều khách hàng tin tưởng lựa chọn.",
            )

            if data['type'] == 'electronics':
                Electronics.objects.create(
                    product=product,
                    brand=data.get('brand', ''),
                    warranty_months=data.get('warranty', 12),
                    specifications=data.get('specs', {}),
                )
            elif data['type'] == 'book':
                Book.objects.create(
                    product=product,
                    author=data.get('author', ''),
                    publisher=data.get('publisher', ''),
                    isbn=data.get('isbn', ''),
                    pages=data.get('pages', 0),
                    language=data.get('lang', 'Tiếng Việt'),
                )
            elif data['type'] == 'fashion':
                Fashion.objects.create(
                    product=product,
                    brand=data.get('brand', ''),
                    size=data.get('size', 'M'),
                    color=data.get('color', ''),
                    material=data.get('material', ''),
                )

        self.stdout.write(self.style.SUCCESS(
            f'✓ Seeded {len(PRODUCTS_DATA)} products with correct images!'
        ))
