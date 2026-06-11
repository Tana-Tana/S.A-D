import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

PRODUCT_SERVICE_URL = "http://product-service:8001"


def get_or_create_cart(user_id):
    cart, _ = Cart.objects.get_or_create(user_id=user_id)
    return cart


class CartView(APIView):
    """Lấy toàn bộ giỏ hàng của user."""
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id là bắt buộc.'}, status=400)
        cart = get_or_create_cart(user_id)
        return Response(CartSerializer(cart).data)


class CartAddView(APIView):
    """Thêm sản phẩm vào giỏ hàng. Nếu đã có thì tăng số lượng."""
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            resp = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}/", timeout=5)
            resp.raise_for_status()
            product = resp.json()
        except Exception:
            return Response({'error': 'Không thể lấy thông tin sản phẩm.'}, status=503)

        if product.get('stock', 0) < quantity:
            return Response({'error': 'Sản phẩm không đủ hàng.'}, status=400)

        cart = get_or_create_cart(user_id)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id,
            defaults={
                'product_name': product['name'],
                'product_price': product['price'],
                'product_image': product.get('image_url', ''),
                'quantity': quantity,
            }
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartRemoveView(APIView):
    """Xóa một sản phẩm khỏi giỏ hàng."""
    permission_classes = [AllowAny]

    def delete(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        try:
            cart = Cart.objects.get(user_id=user_id)
            CartItem.objects.filter(cart=cart, product_id=product_id).delete()
            return Response(CartSerializer(cart).data)
        except Cart.DoesNotExist:
            return Response({'error': 'Giỏ hàng không tồn tại.'}, status=404)


class CartClearView(APIView):
    """Xóa toàn bộ giỏ hàng sau khi đặt hàng thành công."""
    permission_classes = [AllowAny]

    def delete(self, request, user_id):
        CartItem.objects.filter(cart__user_id=user_id).delete()
        return Response({'message': 'Đã xóa giỏ hàng.'})
