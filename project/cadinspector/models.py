from pathlib import Path

import nh3
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Entity(models.Model):

    title = models.CharField(_("Title"), max_length=50)
    description = models.TextField(
        _("Description"), max_length=500, null=True, blank=True
    )
    gltf_model = models.FileField(
        _("GLTF file"),
        help_text=_("Overrides OBJ/MTL entries"),
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
    switch = models.BooleanField(
        _("Switch Z/Y axis"),
        help_text=_("Select if coming from CAD environments"),
        default=False,
    )

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

    def check_image_file_name(self):
        # this function should be called only if
        # images and mtl_model exist

        # get image names as a dictionary
        image_dict = {}
        for img in self.material_images.all():
            img_name = img.image.name.split("/")[-1]
            image_dict[img_name.split(".")[0]] = img_name.split(".")[1]
        # get file paths for material file and helper file
        helper_path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/cadinspector/entity/temp.obj"
        )
        mtl_path = Path(self.mtl_model.path)
        # copy helper from material file
        with open(mtl_path, "r") as m_f, open(helper_path, "w") as h_f:
            for line in m_f:
                if "map_Ka " in line:
                    start = line.split("map_Ka ")[0]
                    rest = line.split("map_Ka ")[-1]
                    name = rest.split(".")[0]
                    for key, value in image_dict.items():
                        if name == key:
                            h_f.write(line)
                        elif name in key:
                            h_f.write(f"{start}map_Ka {key}.{value}\n")
                elif "map_Kd " in line:
                    start = line.split("map_Kd ")[0]
                    rest = line.split("map_Kd ")[-1]
                    name = rest.split(".")[0]
                    for key, value in image_dict.items():
                        if name == key:
                            h_f.write(line)
                        elif name in key:
                            h_f.write(f"{start}map_Kd {key}.{value}\n")
                else:
                    h_f.write(line)
        # copy material file back
        with open(mtl_path, "w") as m_f, open(helper_path, "r") as h_f:
            for line in h_f:
                m_f.write(line)


class MaterialImage(models.Model):
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="material_images",
        verbose_name=_("Material image"),
    )
    image = models.ImageField(_("Image"), upload_to="uploads/cadinspector/entity/")

    def __str__(self):
        return Path(self.image.url).name


class Scene(models.Model):

    title = models.CharField(_("Title"), max_length=50)
    description = models.TextField(
        _("Description"), max_length=500, null=True, blank=True
    )
    dxf = models.FileField(
        _("DXF file"),
        help_text=_("Please, transform 3DSolids into Meshes before upload"),
        max_length=200,
        upload_to="uploads/cadinspector/scene/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "dxf",
                ]
            )
        ],
    )
    image = models.ImageField(
        _("Background image"),
        help_text=_("Please provide an equirectangular image"),
        upload_to="uploads/cadinspector/scene/",
        null=True,
        blank=True,
    )
    __original_dxf = None

    class Meta:
        verbose_name = _("Scene")
        verbose_name_plural = _("Scenes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_dxf = self.dxf

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # save and eventually upload DXF
        super().save(*args, **kwargs)
        if self.__original_dxf != self.dxf:
            all_objects = self.staged_entities.all()
            if all_objects.exists():
                all_objects.delete()
            self.create_objs_from_dxf()

    def create_objs_from_dxf(self):
        pass


class Staging(models.Model):
    scene = models.ForeignKey(
        Scene,
        on_delete=models.CASCADE,
        related_name="staged_entities",
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="scenes",
    )
    position = models.CharField(
        _("Position"),
        default="0 0 0",
        max_length=50,
        help_text="Left/Right - Up/Down - In/Out",
    )
    rotation = models.CharField(
        _("Rotation"),
        default="0 0 0",
        max_length=50,
        help_text="Pitch - Yaw - Roll",
    )
    scale = models.CharField(
        _("Scale"),
        default="1 1 1",
        max_length=50,
        help_text="Width - Heigth - Depth",
    )
    color = models.CharField(_("Color"), default="#FFFFFF", max_length=7)
    data = models.JSONField(
        _("Data sheet"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Staging")
        verbose_name_plural = _("Stagings")

    def __str__(self):
        return _("Staging-%(id)d") % {"id": self.id}

    def popupContent(self):
        if not self.data:
            return
        else:
            out = ""
            for key, value in self.data.items():
                if key == "attribs":
                    out += _("Attributes:\n")
                    for t, v in value.items():
                        out += f"--{nh3.clean(t)}: {nh3.clean(v)}\n"
                else:
                    out += f"{nh3.clean(key)}: {nh3.clean(value)}\n"
            return out
