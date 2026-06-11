import django.db.models.deletion
from django.db import migrations, models


def copy_existing_data(apps, schema_editor):
    User = apps.get_model('users', 'User')
    FullName = apps.get_model('users', 'FullName')
    Address = apps.get_model('users', 'Address')

    for user in User.objects.all():
        FullName.objects.get_or_create(
            user=user,
            defaults={'first_name': user.first_name, 'last_name': user.last_name},
        )
        if user.address:
            Address.objects.get_or_create(
                user=user,
                address_line=user.address,
                defaults={'is_default': True},
            )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FullName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('first_name', models.CharField(blank=True, max_length=150)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='full_name', to='users.user')),
            ],
            options={
                'db_table': 'user_full_names',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line', models.TextField()),
                ('is_default', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='users.user')),
            ],
            options={
                'db_table': 'user_addresses',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
        migrations.RunPython(copy_existing_data, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='user',
            name='address',
        ),
    ]
