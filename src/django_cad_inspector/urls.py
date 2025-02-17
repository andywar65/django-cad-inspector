from django.urls import path
from django.views.generic import RedirectView

from .views import EntityDetailView, EntityListView, SceneDetailView, SceneListView

app_name = "django_cad_inspector"
urlpatterns = [
    path(
        "",
        RedirectView.as_view(pattern_name="django_cad_inspector:scene_list"),
        name="home",
    ),
    path("entity/", EntityListView.as_view(), name="entity_list"),
    path("entity/<pk>/", EntityDetailView.as_view(), name="entity_detail"),
    path("scene/", SceneListView.as_view(), name="scene_list"),
    path("scene/<pk>/", SceneDetailView.as_view(), name="scene_detail"),
]
