from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Danh mục sản phẩm (Book, Electronics, Fashion, ...)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Base Product model - chứa thông tin chung cho tất cả loại sản phẩm"""
    PRODUCT_TYPE_CHOICES = (
        ('book', 'Sách'),
        ('electronics', 'Điện tử'),
        ('fashion', 'Thời trang'),
        ('furniture', 'Nội thất'),
        ('food', 'Thực phẩm'),
        ('sports', 'Thể thao'),
        ('beauty', 'Làm đẹp'),
        ('toys', 'Đồ chơi'),
        ('automotive', 'Ô tô - Xe máy'),
        ('other', 'Khác'),
    )

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    sold_count = models.IntegerField(default=0)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    image_url = models.URLField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product_type', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0


class Book(models.Model):
    """Thông tin chi tiết dành riêng cho sản phẩm loại Sách"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='book_detail')
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    publication_year = models.IntegerField(null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default='Tiếng Việt')
    genre = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'books'

    def __str__(self):
        return f"Book: {self.product.name} - {self.author}"


class Electronics(models.Model):
    """Thông tin chi tiết dành riêng cho sản phẩm Điện tử"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='electronics_detail')
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100, blank=True)
    warranty_months = models.IntegerField(default=12)
    specifications = models.JSONField(default=dict, blank=True)
    color = models.CharField(max_length=50, blank=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'electronics'

    def __str__(self):
        return f"Electronics: {self.product.name} - {self.brand}"


class Fashion(models.Model):
    """Thông tin chi tiết dành riêng cho sản phẩm Thời trang"""
    SIZE_CHOICES = (('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'))

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='fashion_detail')
    brand = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    material = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, choices=(('male', 'Nam'), ('female', 'Nữ'), ('unisex', 'Unisex')), default='unisex')
    season = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'fashion'

    def __str__(self):
        return f"Fashion: {self.product.name} - Size {self.size}"


class UserBehaviorEvent(models.Model):
    """Log hanh vi nguoi dung (view/click/add_to_cart) tren san pham,
    dung lam du lieu huan luyen cho AI service (RNN/LSTM/BiLSTM + KB_Graph)."""
    ACTION_CHOICES = (
        ('view', 'Xem'),
        ('click', 'Click'),
        ('add_to_cart', 'Thêm vào giỏ hàng'),
    )

    user_id = models.IntegerField(db_index=True)
    product_id = models.IntegerField(db_index=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'user_behavior_events'
        ordering = ['user_id', 'created_at']

    def __str__(self):
        return f"UserBehaviorEvent(user={self.user_id}, product={self.product_id}, action={self.action})"
