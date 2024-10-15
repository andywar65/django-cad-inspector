from django.contrib import admin, messages

from .models import Entity, MaterialImage


class MaterialImageInline(admin.TabularInline):
    model = MaterialImage
    extra = 0


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    inlines = [
        MaterialImageInline,
    ]
    actions = ["check_file_names"]

    @admin.action(description="Check material and image file names")
    def check_file_names(self, request, queryset):
        for ent in queryset:
            if ent.obj_model and ent.mtl_model:
                ent.check_material_file_name()
                self.message_user(
                    request,
                    f"Checked file: {ent.mtl_model.name}",
                    messages.SUCCESS,
                )
            if ent.mtl_model and ent.material_images.exists():
                ent.check_image_file_name()
                self.message_user(
                    request,
                    f"Checked images for file: {ent.mtl_model.name}",
                    messages.SUCCESS,
                )
