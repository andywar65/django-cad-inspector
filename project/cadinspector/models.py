from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Entity(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)
    gltf_model = models.FileField(
        _("GLTF file"),
        help_text=_("Overrides all other entries"),
        max_length=200,
        upload_to="uploads/cadinspector/entity/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "gltf",
                    "glb",
                ]
            )
        ],
        null=True,
        blank=True,
    )
    obj_model = models.FileField(
        _("OBJ file"),
        max_length=200,
        upload_to="uploads/cadinspector/entity/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "obj",
                ]
            )
        ],
        null=True,
        blank=True,
    )
    mtl_model = models.FileField(
        _("MTL file"),
        max_length=200,
        upload_to="uploads/cadinspector/entity/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "mtl",
                ]
            )
        ],
        null=True,
        blank=True,
    )
    switch = models.BooleanField(default=False, help_text="Switch Z/Y axis")

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")

    def __str__(self):
        return self.title
