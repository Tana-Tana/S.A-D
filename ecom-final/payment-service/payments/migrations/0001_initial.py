import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('transaction_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('order_id', models.IntegerField(db_index=True)),
                ('user_id', models.IntegerField(db_index=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('method', models.CharField(
                    choices=[('cod','Thanh toán khi nhận hàng'),('bank_transfer','Chuyển khoản'),
                             ('momo','Ví MoMo'),('vnpay','VNPay'),('zalopay','ZaloPay')],
                    default='cod', max_length=20)),
                ('status', models.CharField(
                    choices=[('pending','Chờ thanh toán'),('processing','Đang xử lý'),
                             ('success','Thành công'),('failed','Thất bại'),('refunded','Đã hoàn tiền')],
                    default='pending', max_length=20)),
                ('gateway_response', models.JSONField(blank=True, default=dict)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'payments', 'ordering': ['-created_at']},
        ),
    ]
