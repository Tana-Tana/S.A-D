from django.contrib import admin
from django.urls import path
from shipping.views import ShipmentCreateView, ShipmentStatusView, ShipmentUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shipping/create/', ShipmentCreateView.as_view(), name='shipment-create'),
    path('shipping/status/', ShipmentStatusView.as_view(), name='shipment-status'),
    path('shipping/<int:pk>/update/', ShipmentUpdateView.as_view(), name='shipment-update'),
]
