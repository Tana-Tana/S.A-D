from django.urls import path
from .views import (CategoryListView, ProductListView, ProductDetailView,
                    ProductSearchView, ProductStockCheckView, BehaviorEventCreateView)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('products/stock-check/', ProductStockCheckView.as_view(), name='stock-check'),
    path('events/', BehaviorEventCreateView.as_view(), name='behavior-event-create'),
]
