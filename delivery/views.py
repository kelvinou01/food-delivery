
from django.contrib.auth import get_user_model
from rest_framework import generics

class BaseRegister(generics.CreateAPIView):
    permission_classes = []
    queryset = get_user_model()._default_manager.all()
