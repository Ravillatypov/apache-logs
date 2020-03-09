from django_filters import rest_framework as filters

from logs.models import AccessLog


class AccessLogFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = AccessLog
        fields = ['ip', 'method', 'path', 'date_from', 'date_to', 'response_code']
