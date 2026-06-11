from rest_framework import serializers
from .models import Shipment, ShipmentHistory


class ShipmentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentHistory
        fields = ['status', 'description', 'location', 'timestamp']


class ShipmentSerializer(serializers.ModelSerializer):
    history = ShipmentHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Shipment
        fields = ['id', 'order_id', 'user_id', 'tracking_code', 'address',
                  'carrier', 'status', 'status_display', 'estimated_delivery',
                  'delivered_at', 'history', 'created_at', 'updated_at']
