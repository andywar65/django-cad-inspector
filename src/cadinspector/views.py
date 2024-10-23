from typing import Any

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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if "no-cursor" in self.request.GET:
            context["no_cursor"] = True
        return context
