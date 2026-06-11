from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model với Role-Based Access Control (RBAC).
    Extends AbstractUser để tận dụng authentication có sẵn của Django.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
        db_index=True
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff_member(self):
        return self.role == 'staff'

    @property
    def is_customer(self):
        return self.role == 'customer'


class FullName(models.Model):
    """
    Value Object - Ho va ten day du cua nguoi dung.
    Quan he aggregation 1-1 voi User (User la Aggregate Root).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='full_name')
    last_name = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'user_full_names'

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip()


class Address(models.Model):
    """
    Entity - Dia chi cua nguoi dung.
    Quan he aggregation 1-N voi User (mot User co the co nhieu Address).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line = models.TextField()
    is_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return self.address_line[:50]
