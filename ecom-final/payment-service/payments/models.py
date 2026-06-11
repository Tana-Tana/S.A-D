from django.db import models
import uuid


class Payment(models.Model):
    """Giao dịch thanh toán. Mỗi đơn hàng có tối đa 1 thanh toán thành công."""
    METHOD_CHOICES = (
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('momo', 'Ví MoMo'),
        ('vnpay', 'VNPay'),
        ('zalopay', 'ZaloPay'),
    )

    STATUS_CHOICES = (
        ('pending', 'Chờ thanh toán'),
        ('processing', 'Đang xử lý'),
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
        ('refunded', 'Đã hoàn tiền'),
    )

    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_id = models.IntegerField(db_index=True)
    user_id = models.IntegerField(db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cod')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment#{self.transaction_id} - Order#{self.order_id} - {self.status}"
