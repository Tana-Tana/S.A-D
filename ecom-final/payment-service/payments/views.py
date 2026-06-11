import requests
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from .models import Payment
from .serializers import PaymentSerializer

ORDER_SERVICE_URL = "http://order-service:8003"
SHIPPING_SERVICE_URL = "http://shipping-service:8005"


class PaymentCreateView(APIView):
    """
    Khởi tạo thanh toán cho đơn hàng.
    COD: tự động success. Các gateway khác: mock success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        order_id = request.data.get('order_id')
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        method = request.data.get('method', 'cod')

        if Payment.objects.filter(order_id=order_id, status='success').exists():
            return Response({'error': 'Đơn hàng này đã được thanh toán.'}, status=400)

        payment = Payment.objects.create(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            method=method,
            status='processing'
        )

        payment_success = self._process_payment(payment)

        if payment_success:
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.gateway_response = {'code': '00', 'message': 'Thanh toán thành công'}
            payment.save()

            try:
                requests.patch(
                    f"{ORDER_SERVICE_URL}/orders/{order_id}/status/",
                    json={'status': 'paid'}, timeout=5
                )
                requests.post(
                    f"{SHIPPING_SERVICE_URL}/shipping/create/",
                    json={'order_id': order_id, 'user_id': user_id,
                          'address': request.data.get('shipping_address', '')},
                    timeout=5
                )
            except Exception:
                pass
        else:
            payment.status = 'failed'
            payment.gateway_response = {'code': '99', 'message': 'Thanh toán thất bại'}
            payment.save()

        return Response(PaymentSerializer(payment).data,
                        status=status.HTTP_201_CREATED if payment_success else status.HTTP_400_BAD_REQUEST)

    def _process_payment(self, payment):
        """Mock payment gateway. Trong thực tế gọi API của MoMo/VNPay."""
        return True


class PaymentStatusView(RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]
    lookup_field = 'order_id'


class PaymentListView(ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Payment.objects.filter(user_id=user_id)
        return Payment.objects.all()
