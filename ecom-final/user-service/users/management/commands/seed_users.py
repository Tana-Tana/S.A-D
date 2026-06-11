from django.core.management.base import BaseCommand
from users.models import User, FullName, Address


class Command(BaseCommand):
    help = 'Tạo tài khoản mẫu để demo'

    def handle(self, *args, **options):
        accounts = [
            {'username': 'admin',    'password': 'Admin@123',    'role': 'admin',    'email': 'admin@ecomai.vn',
             'last_name': '', 'first_name': 'Admin', 'address': ''},
            {'username': 'staff01',  'password': 'Staff@123',    'role': 'staff',    'email': 'staff@ecomai.vn',
             'last_name': 'Nguyễn Văn', 'first_name': 'Nhân viên', 'address': '12 Láng Hạ, Đống Đa, Hà Nội'},
            {'username': 'customer', 'password': 'Customer@123', 'role': 'customer', 'email': 'customer@ecomai.vn',
             'last_name': 'Trần Thị', 'first_name': 'Khách Hàng', 'address': '123 Nguyễn Trãi, Thanh Xuân, Hà Nội'},
        ]
        for acc in accounts:
            if not User.objects.filter(username=acc['username']).exists():
                user = User.objects.create_user(
                    username=acc['username'],
                    password=acc['password'],
                    email=acc['email'],
                    role=acc['role'],
                )
                FullName.objects.create(
                    user=user,
                    last_name=acc['last_name'],
                    first_name=acc['first_name'],
                )
                if acc['address']:
                    Address.objects.create(user=user, address_line=acc['address'], is_default=True)
                self.stdout.write(self.style.SUCCESS(f"✓ Created user: {acc['username']} / {acc['password']}"))
            else:
                self.stdout.write(f"  Skip: {acc['username']} already exists")
