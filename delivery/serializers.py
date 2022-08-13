from django.contrib.auth import get_user_model  
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {
            'password' : {'write_only': 'True'}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        UserModel = get_user_model()
        user = UserModel.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
