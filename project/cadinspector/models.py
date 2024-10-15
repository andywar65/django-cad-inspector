from pathlib import Path

from django.conf import settings
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

    def check_material_file_name(self):
        # this function should be called only if
        # obj_model and mtl_model exist

        # get the material file name
        mtl_name = self.mtl_model.name.split("/")[-1]
        # get file paths for object file and helper file
        helper_path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/cadinspector/entity/temp.obj"
        )
        obj_path = Path(self.obj_model.path)
        # copy helper from object file
        with open(obj_path, "r") as o_f, open(helper_path, "w") as h_f:
            for line in o_f:
                if line.startswith("mtllib"):
                    h_f.write(f"mtllib {mtl_name}\n")
                else:
                    h_f.write(line)
        # copy object file back
        with open(obj_path, "w") as o_f, open(helper_path, "r") as h_f:
            for line in h_f:
                o_f.write(line)


class MaterialImage(models.Model):
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="material_images",
        verbose_name="Material image",
    )
    image = models.ImageField(upload_to="uploads/cadinspector/entity/")

    def __str__(self):
        return Path(self.image.url).name
