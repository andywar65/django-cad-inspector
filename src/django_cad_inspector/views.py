from typing import Any

from django.views.generic import DetailView, ListView

from .models import Entity, Scene


class EntityListView(ListView):
    model = Entity
    template_name = "django_cad_inspector/entity_list.html"


class EntityDetailView(DetailView):
    model = Entity
    template_name = "django_cad_inspector/entity_detail.html"


class SceneListView(ListView):
    model = Scene
    template_name = "django_cad_inspector/scene_list.html"


class SceneDetailView(DetailView):
    model = Scene
    template_name = "django_cad_inspector/scene_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if "no-cursor" in self.request.GET:
            context["no_cursor"] = True
        if "lights" in self.request.GET:
            context["no_cursor"] = True
            context["lights"] = True
        return context
