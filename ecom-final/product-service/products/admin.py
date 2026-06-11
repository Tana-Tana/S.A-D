from django.contrib import admin
from .models import Category, Product, Book, Electronics, Fashion, UserBehaviorEvent


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}


class BookInline(admin.StackedInline):
    model = Book
    extra = 0


class ElectronicsInline(admin.StackedInline):
    model = Electronics
    extra = 0


class FashionInline(admin.StackedInline):
    model = Fashion
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'price', 'stock', 'rating', 'is_active']
    list_filter = ['product_type', 'is_active', 'category']
    search_fields = ['name', 'description']
    inlines = [BookInline, ElectronicsInline, FashionInline]


@admin.register(UserBehaviorEvent)
class UserBehaviorEventAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'product_id', 'action', 'created_at']
    list_filter = ['action']
    search_fields = ['user_id', 'product_id']
