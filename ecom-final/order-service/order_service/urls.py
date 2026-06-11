from django.contrib import admin
from django.urls import path
from orders.views import OrderListView, OrderCreateView, OrderDetailView, OrderStatusUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status'),
]
