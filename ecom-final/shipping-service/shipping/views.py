import requests
from django.utils import timezone
from datetime import date, timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from .models import Shipment, ShipmentHistory
from .serializers import ShipmentSerializer

ORDER_SERVICE_URL = "http://order-service:8003"


class ShipmentCreateView(APIView):
    """Tạo bản ghi vận chuyển sau khi thanh toán thành công."""
    permission_classes = [AllowAny]

    def post(self, request):
        order_id = request.data.get('order_id')
        user_id = request.data.get('user_id')
        address = request.data.get('address')

        if Shipment.objects.filter(order_id=order_id).exists():
            return Response({'error': 'Đơn hàng này đã có thông tin vận chuyển.'}, status=400)

        shipment = Shipment.objects.create(
            order_id=order_id,
            user_id=user_id,
            address=address,
            estimated_delivery=date.today() + timedelta(days=3)
        )

        ShipmentHistory.objects.create(
            shipment=shipment,
            status='processing',
            description='Đơn hàng đã được xác nhận và đang chuẩn bị hàng.',
            location='Kho Hà Nội'
        )

        try:
            requests.patch(
                f"{ORDER_SERVICE_URL}/orders/{order_id}/status/",
                json={'status': 'shipping'}, timeout=5
            )
        except Exception:
            pass

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)


class ShipmentStatusView(APIView):
    """Tra cứu trạng thái vận chuyển theo order_id hoặc tracking_code."""
    permission_classes = [AllowAny]

    def get(self, request):
        order_id = request.query_params.get('order_id')
        tracking_code = request.query_params.get('tracking_code')

        try:
            if order_id:
                shipment = Shipment.objects.get(order_id=order_id)
            elif tracking_code:
                shipment = Shipment.objects.get(tracking_code=tracking_code)
            else:
                return Response({'error': 'Vui lòng cung cấp order_id hoặc tracking_code.'}, status=400)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy thông tin vận chuyển.'}, status=404)

        return Response(ShipmentSerializer(shipment).data)


class ShipmentUpdateView(APIView):
    """Cập nhật trạng thái vận chuyển (webhook từ đối tác GHN)."""
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        try:
            shipment = Shipment.objects.get(pk=pk)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn vận chuyển.'}, status=404)

        new_status = request.data.get('status')
        description = request.data.get('description', '')
        location = request.data.get('location', '')

        shipment.status = new_status
        if new_status == 'delivered':
            shipment.delivered_at = timezone.now()
            try:
                requests.patch(
                    f"{ORDER_SERVICE_URL}/orders/{shipment.order_id}/status/",
                    json={'status': 'delivered'}, timeout=5
                )
            except Exception:
                pass
        shipment.save()

        ShipmentHistory.objects.create(
            shipment=shipment, status=new_status,
            description=description, location=location
        )

        return Response(ShipmentSerializer(shipment).data)
