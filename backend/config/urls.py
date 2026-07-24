from django.contrib import admin
from django.urls import path
from apps.adminpanel.views import owner_report_csv
from apps.common.views import healthcheck


urlpatterns = [
    path("admin/owner-report.csv", owner_report_csv),
    path("admin/", admin.site.urls),
    path("health/", healthcheck),
]
