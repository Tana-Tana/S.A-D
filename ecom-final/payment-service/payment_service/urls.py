from django.contrib import admin
from django.urls import path
from payments.views import PaymentCreateView, PaymentStatusView, PaymentListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payment/pay/', PaymentCreateView.as_view(), name='payment-create'),
    path('payment/status/<int:order_id>/', PaymentStatusView.as_view(), name='payment-status'),
    path('payment/', PaymentListView.as_view(), name='payment-list'),
]
