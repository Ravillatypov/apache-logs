from collections import defaultdict
from itertools import groupby

from django.db.models import QuerySet, F, Count, Sum, Window
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, response

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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        statistics = self.get_statistics(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({'data': serializer.data, 'statistics': statistics})

        serializer = self.get_serializer(queryset, many=True)
        return response.Response({'data': serializer.data, 'statistics': statistics})

    @staticmethod
    def get_statistics(queryset: QuerySet) -> dict:
        result = queryset.aggregate(
            unique_ip=Count('ip', distinct=True),
        )
        result['top10'] = []

        top10_qs = queryset.filter(
            ip__in=queryset.values('ip').annotate(count=Count('ip')).order_by('-count')[:10].values_list('ip')
        ).annotate(
            count=Window(
                expression=Count('ip'),
                partition_by=[F('ip'), F('method')],
                order_by=[F('ip')]
            ),
            size=Window(
                expression=Sum('response_size'),
                partition_by=[F('ip'), F('method')],
                order_by=[F('ip')]
            ),
        ).values('ip', 'method', 'size', 'count').order_by('ip', 'method')
        for ip, by_ip in groupby(top10_qs, lambda x: x.get('ip')):
            methods = defaultdict(lambda : {'count': 0, 'size': 0})
            for method, by_method in groupby(by_ip, lambda x: x.get('method')):
                for stats in by_method:
                    methods[method]['count'] += stats.get('count', 0)
                    methods[method]['size'] += stats.get('size', 0)
            result['top10'].append({
                'ip': ip,
                **methods
            })

        return result
