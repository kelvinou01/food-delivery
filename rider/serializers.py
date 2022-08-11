from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from client.serializers import OrderItemListSerializer
from merchant.models import Order
from rider.models import Session


class SessionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = ['id', 'start_datetime', 'end_datetime']


class SessionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = ['id', 'start_datetime', 'end_datetime']
        extra_kwargs = {
            'id': {'read_only': 'True'},
            'start_datetime': {'read_only': 'True'}, 
        }
    
    def validate(self, attrs):
        overlapping_sessions = Session.objects.filter(
            start_datetime__lt=attrs['end_datetime'], 
            end_datetime__gt=timezone.now()
        )
        if overlapping_sessions.exists():
            raise ValidationError('Cannot save overlapping sessions')
        return super().validate(attrs)
    
    def create(self, validated_data):
        return Session.objects.create(
            rider=self.context.get('request').user.rider,
            start_datetime=timezone.now(),
            end_datetime=validated_data['end_datetime'],
        )


class SessionExtendSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Session
        fields = ['end_datetime']
    
    def validate_end_datetime(self, value):
        if value <= timezone.now():
            raise ValidationError('end_datetime must be greater than current time')
        return value


class OrderListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'created', 'completed', 'status']
        extra_kwargs = {
            'id': {'read_only': True},
            'completed': {'read_only': True},
            'status': {'read_only': True},
        }


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemListSerializer(many=True)
    estimated_completion_datetime = serializers.SerializerMethodField(method_name='get_estimated_completion_datetime')

    class Meta:
        model = Order
        fields = ['id', 'restaurant', 'items', 'created', 'status', 'price', 'estimated_completion_datetime']
    
    def get_estimated_completion_datetime(self, obj):
        return obj.delivery.estimated_delivery_datetime

