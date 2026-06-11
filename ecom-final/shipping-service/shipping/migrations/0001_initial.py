from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('order_id', models.IntegerField(db_index=True, unique=True)),
                ('user_id', models.IntegerField(db_index=True)),
                ('tracking_code', models.CharField(blank=True, max_length=50, unique=True)),
                ('address', models.TextField()),
                ('carrier', models.CharField(default='GHN Express', max_length=100)),
                ('status', models.CharField(
                    choices=[('processing','Đang chuẩn bị hàng'),('picked_up','Đã lấy hàng'),
                             ('in_transit','Đang vận chuyển'),('out_for_delivery','Đang giao hàng'),
                             ('delivered','Đã giao hàng'),('failed','Giao hàng thất bại'),
                             ('returned','Đã hoàn hàng')],
                    default='processing', max_length=30)),
                ('estimated_delivery', models.DateField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'shipments', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ShipmentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=255)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='history', to='shipping.shipment')),
            ],
            options={'db_table': 'shipment_history', 'ordering': ['-timestamp']},
        ),
    ]
