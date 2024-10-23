from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("3d/", include("cadinspector.urls", namespace="cadinspector")),
]
