from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'transaction_id', 'order_id', 'user_id', 'amount',
                  'method', 'method_display', 'status', 'status_display',
                  'gateway_response', 'paid_at', 'created_at']
