from django.contrib import admin
from django.urls import path
from cart.views import CartView, CartAddView, CartRemoveView, CartClearView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddView.as_view(), name='cart-add'),
    path('cart/remove/', CartRemoveView.as_view(), name='cart-remove'),
    path('cart/clear/<int:user_id>/', CartClearView.as_view(), name='cart-clear'),
]
