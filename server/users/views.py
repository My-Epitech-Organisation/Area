from rest_framework import viewsets
from .models import AppUser
from .serializers import AppUserSerializer


class AppUserViewSet(viewsets.ModelViewSet):
	queryset = AppUser.objects.all().order_by('-created_at')
	serializer_class = AppUserSerializer
