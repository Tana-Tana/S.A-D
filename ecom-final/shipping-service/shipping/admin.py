from django.contrib import admin
from .models import Shipment, ShipmentHistory

class ShipmentHistoryInline(admin.TabularInline):
    model = ShipmentHistory
    extra = 0

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_id', 'tracking_code', 'carrier', 'status', 'created_at']
    list_filter = ['status', 'carrier']
    inlines = [ShipmentHistoryInline]
