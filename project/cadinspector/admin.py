from django.contrib import admin

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
