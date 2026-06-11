from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, FullName, Address


class FullNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = FullName
        fields = ['last_name', 'first_name']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address_line', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    full_name = FullNameSerializer(required=False)
    addresses = AddressSerializer(many=True, read_only=True)
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'phone', 'avatar', 'is_active', 'full_name',
                  'addresses', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_first_name(self, obj):
        full_name = getattr(obj, 'full_name', None)
        return full_name.first_name if full_name else ''

    def get_last_name(self, obj):
        full_name = getattr(obj, 'full_name', None)
        return full_name.last_name if full_name else ''

    def update(self, instance, validated_data):
        full_name_data = validated_data.pop('full_name', None)
        instance = super().update(instance, validated_data)
        if full_name_data is not None:
            full_name, _ = FullName.objects.get_or_create(user=instance)
            for attr, value in full_name_data.items():
                setattr(full_name, attr, value)
            full_name.save()
            instance.full_name = full_name
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'address', 'phone', 'role']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Mật khẩu xác nhận không khớp.")
        return data

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        address = validated_data.pop('address', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', 'customer'),
        )
        FullName.objects.create(user=user, first_name=first_name, last_name=last_name)
        if address:
            Address.objects.create(user=user, address_line=address, is_default=True)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Sai tên đăng nhập hoặc mật khẩu.")
        if not user.is_active:
            raise serializers.ValidationError("Tài khoản đã bị vô hiệu hóa.")
        refresh = RefreshToken.for_user(user)
        return {
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
