from django.views.generic import DetailView, ListView

from .models import Entity, Scene


class EntityListView(ListView):
    model = Entity
    template_name = "cadinspector/entity_list.html"


class EntityDetailView(DetailView):
    model = Entity
    template_name = "cadinspector/entity_detail.html"


class SceneListView(ListView):
    model = Scene
    template_name = "cadinspector/scene_list.html"


class SceneDetailView(DetailView):
    model = Scene
    template_name = "cadinspector/scene_detail.html"
