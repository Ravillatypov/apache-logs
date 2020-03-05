from django.urls import include, path

from logs.api.viewsets import AccessLogListView

urlpatterns = [
    path('logs', AccessLogListView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
