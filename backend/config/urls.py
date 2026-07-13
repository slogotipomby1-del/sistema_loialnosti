from django.contrib import admin
from django.urls import path
from apps.common.views import healthcheck


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck),
]
