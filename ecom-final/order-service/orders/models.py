from django.db import models


class Order(models.Model):
    """Đơn hàng. Mỗi đơn hàng thuộc về 1 user."""
    STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('paid', 'Đã thanh toán'),
        ('shipping', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
        ('refunded', 'Đã hoàn tiền'),
    )

    user_id = models.IntegerField(db_index=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_address = models.TextField()
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order#{self.id} - User#{self.user_id} - {self.status}"


class OrderItem(models.Model):
    """Chi tiết sản phẩm trong đơn hàng. Snapshot giá tại thời điểm đặt."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = 'order_items'

    @property
    def subtotal(self):
        return self.product_price * self.quantity
