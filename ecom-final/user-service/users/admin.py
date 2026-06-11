from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FullName, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('role', 'phone', 'avatar')}),
    )


@admin.register(FullName)
class FullNameAdmin(admin.ModelAdmin):
    list_display = ['user', 'last_name', 'first_name']
    search_fields = ['user__username', 'last_name', 'first_name']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_line', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['user__username', 'address_line']
