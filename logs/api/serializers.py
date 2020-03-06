from rest_framework import serializers
from logs.models import AccessLog


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        exclude = ('id',)
