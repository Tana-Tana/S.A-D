from rest_framework import serializers
from .models import Category, Product, Book, Electronics, Fashion, UserBehaviorEvent


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'parent']


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['author', 'publisher', 'isbn', 'publication_year', 'pages', 'language', 'genre']


class ElectronicsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electronics
        fields = ['brand', 'model_number', 'warranty_months', 'specifications', 'color', 'weight_kg']


class FashionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fashion
        fields = ['brand', 'size', 'color', 'material', 'gender', 'season']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percent = serializers.ReadOnlyField()
    book_detail = BookDetailSerializer(read_only=True)
    electronics_detail = ElectronicsDetailSerializer(read_only=True)
    fashion_detail = FashionDetailSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'original_price',
            'stock', 'sold_count', 'product_type', 'category', 'category_name',
            'image_url', 'rating', 'discount_percent', 'is_active',
            'book_detail', 'electronics_detail', 'fashion_detail',
            'created_at', 'updated_at'
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'original_price',
                  'stock', 'product_type', 'category', 'image_url']

    def create(self, validated_data):
        return Product.objects.create(**validated_data)


class UserBehaviorEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehaviorEvent
        fields = ['id', 'user_id', 'product_id', 'action', 'created_at']
        read_only_fields = ['id', 'created_at']
