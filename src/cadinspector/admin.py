from django.contrib import admin, messages
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


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    inlines = [
        StagingInline,
    ]