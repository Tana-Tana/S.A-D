from django.db import models


class Shipment(models.Model):
    """Thông tin vận chuyển cho một đơn hàng."""
    STATUS_CHOICES = (
        ('processing', 'Đang chuẩn bị hàng'),
        ('picked_up', 'Đã lấy hàng'),
        ('in_transit', 'Đang vận chuyển'),
        ('out_for_delivery', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('failed', 'Giao hàng thất bại'),
        ('returned', 'Đã hoàn hàng'),
    )

    order_id = models.IntegerField(unique=True, db_index=True)
    user_id = models.IntegerField(db_index=True)
    tracking_code = models.CharField(max_length=50, unique=True, blank=True)
    address = models.TextField()
    carrier = models.CharField(max_length=100, default='GHN Express')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='processing')
    estimated_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shipments'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            import random
            import string
            self.tracking_code = 'GHN' + ''.join(random.choices(string.digits, k=10))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shipment(order={self.order_id}, tracking={self.tracking_code})"


class ShipmentHistory(models.Model):
    """Lịch sử cập nhật trạng thái vận chuyển."""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=30)
    description = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipment_history'
        ordering = ['-timestamp']
