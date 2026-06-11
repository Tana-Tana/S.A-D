from django.db import models


class Cart(models.Model):
    """Giỏ hàng của một user. Mỗi user có đúng 1 giỏ hàng."""
    user_id = models.IntegerField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart(user_id={self.user_id})"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Một dòng sản phẩm trong giỏ hàng."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField(db_index=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    product_image = models.URLField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'product_id']

    def __str__(self):
        return f"CartItem(product={self.product_id}, qty={self.quantity})"

    @property
    def subtotal(self):
        return self.product_price * self.quantity
