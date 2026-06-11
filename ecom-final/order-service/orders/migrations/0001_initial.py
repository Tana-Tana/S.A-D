from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(db_index=True)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('shipping_address', models.TextField()),
                ('shipping_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(
                    choices=[('pending','Chờ xác nhận'),('confirmed','Đã xác nhận'),
                             ('processing','Đang xử lý'),('paid','Đã thanh toán'),
                             ('shipping','Đang giao hàng'),('delivered','Đã giao hàng'),
                             ('cancelled','Đã hủy'),('refunded','Đã hoàn tiền')],
                    db_index=True, default='pending', max_length=20)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'orders', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('product_id', models.IntegerField()),
                ('product_name', models.CharField(max_length=255)),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='items', to='orders.order')),
            ],
            options={'db_table': 'order_items'},
        ),
    ]
