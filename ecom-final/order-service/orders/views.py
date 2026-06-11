import requests
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer

CART_SERVICE_URL = "http://cart-service:8002"
PAYMENT_SERVICE_URL = "http://payment-service:8004"


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Order.objects.filter(user_id=user_id).prefetch_related('items')
        return Order.objects.all().prefetch_related('items')


class OrderCreateView(APIView):
    """
    Tạo đơn hàng từ giỏ hàng.
    Flow: Lấy cart → Tạo Order + OrderItems → Xóa cart → Trả về order
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        shipping_address = request.data.get('shipping_address')
        note = request.data.get('note', '')

        try:
            cart_resp = requests.get(
                f"{CART_SERVICE_URL}/cart/",
                params={'user_id': user_id}, timeout=5
            )
            cart = cart_resp.json()
        except Exception:
            return Response({'error': 'Không thể lấy thông tin giỏ hàng.'}, status=503)

        if not cart.get('items'):
            return Response({'error': 'Giỏ hàng trống.'}, status=400)

        order = Order.objects.create(
            user_id=user_id,
            total_price=cart['total_price'],
            shipping_address=shipping_address,
            shipping_fee=30000,
            note=note,
            status='pending'
        )

        for item in cart['items']:
            OrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                product_name=item['product_name'],
                product_price=item['product_price'],
                quantity=item['quantity'],
            )

        try:
            requests.delete(
                f"{CART_SERVICE_URL}/cart/clear/{user_id}/", timeout=5
            )
        except Exception:
            pass

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]


class OrderStatusUpdateView(APIView):
    """Cập nhật trạng thái đơn hàng (dùng bởi payment/shipping service)."""
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Đơn hàng không tồn tại.'}, status=404)

        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Trạng thái không hợp lệ.'}, status=400)

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)
