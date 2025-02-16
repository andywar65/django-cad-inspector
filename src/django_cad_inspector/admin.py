from django.contrib import admin, messages
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from .models import Entity, MaterialImage, Scene, Staging


class MaterialImageInline(admin.TabularInline):
    model = MaterialImage
    extra = 0


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    inlines = [
        MaterialImageInline,
    ]
    actions = ["check_file_names", "delete_unstaged_entities"]

    @admin.action(description=_("Check material and image file names"))
    def check_file_names(self, request, queryset):
        for ent in queryset:
            if ent.obj_model and ent.mtl_model:
                ent.check_material_file_name()
                self.message_user(
                    request,
                    _("Checked file: %(name)s") % {"name": ent.obj_model.name},
                    messages.SUCCESS,
                )
            if ent.mtl_model and ent.material_images.exists():
                ent.check_image_file_name()
                self.message_user(
                    request,
                    _("Checked images for file: %(name)s")
                    % {"name": ent.mtl_model.name},
                    messages.SUCCESS,
                )

    @admin.action(description=_("Delete unstaged entities"))
    def delete_unstaged_entities(self, request, queryset):
        staged = Staging.objects.values_list("entity", flat=True)
        for ent in queryset:
            if ent.id not in staged:
                self.message_user(
                    request,
                    _("Deleted unstaged entity: %(title)s") % {"title": ent.title},
                    messages.WARNING,
                )
                ent.delete()


class StagingInline(admin.TabularInline):
    model = Staging
    extra = 0
    fields = [
        "entity",
        "color",
        "wireframe",
    ]


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    readonly_fields = ["admin_link_stagings"]
    inlines = [
        StagingInline,
    ]

    @admin.display(description=_("Stagings (edit all fields)"))
    def admin_link_stagings(self, obj):
        """Learned this trick here:
        https://406.ch/writing/django-admin-tip-adding-links-to-related-objects-in-change-forms/
        """
        return render_to_string(
            "django_cad_inspector/admin_stagings.html",
            {"stagings": obj.staged_entities.all()},
        )


@admin.register(Staging)
class StagingAdmin(admin.ModelAdmin):
    list_display = ("id", "scene", "entity")
