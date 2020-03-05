from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

from logs.api.serializers import AccessLogSerializer
from logs.models import AccessLog


class AccessLogListView(generics.ListAPIView):
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ip', 'method', 'path']
    filterset_fields = ['ip', 'method', 'path', 'date', 'response_code']
    permission_classes = [permissions.AllowAny]
    ordering_fields = '__all__'
