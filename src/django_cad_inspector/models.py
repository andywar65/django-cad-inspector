from math import asin, atan2, copysign, cos, degrees, fabs, pi
from pathlib import Path
from shutil import copyfileobj

import ezdxf
import nh3
import numpy as np
from colorfield.fields import ColorField
from django.conf import settings
from django.core.files import File
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from ezdxf.addons import meshex
from ezdxf.math import Vec3
from ezdxf.render import MeshBuilder


class Entity(models.Model):

    title = models.CharField(_("Title"), max_length=50)
    description = models.TextField(
        _("Description"), max_length=500, null=True, blank=True
    )
    gltf_model = models.FileField(
        _("GLTF file"),
        help_text=_("Overrides OBJ/MTL entries"),
        max_length=200,
        upload_to="uploads/django_cad_inspector/entity/",
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
        upload_to="uploads/django_cad_inspector/entity/",
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
        upload_to="uploads/django_cad_inspector/entity/",
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
            "uploads/django_cad_inspector/entity/temp.obj"
        )
        obj_path = Path(self.obj_model.path)
        # copy helper from object file
        with open(obj_path, "r") as o_f, open(helper_path, "w") as h_f:
            for line in o_f:
                if line.startswith("mtllib"):
                    h_f.write(f"mtllib {mtl_name}\n")
                    # copy the rest of the object file
                    copyfileobj(o_f, h_f)
                    break
                else:
                    h_f.write(line)
        # copy object file back
        with open(obj_path, "w") as o_f, open(helper_path, "r") as h_f:
            copyfileobj(h_f, o_f)

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
            "uploads/django_cad_inspector/entity/temp.obj"
        )
        mtl_path = Path(self.mtl_model.path)
        # copy helper from material file
        with open(mtl_path, "r") as m_f, open(helper_path, "w") as h_f:
            for line in m_f:
                if "map_Ka " in line:
                    self.replace_filename(image_dict, line, "map_Ka ", h_f)
                elif "map_Kd " in line:
                    self.replace_filename(image_dict, line, "map_Kd ", h_f)
                else:
                    h_f.write(line)
        # copy material file back
        with open(mtl_path, "w") as m_f, open(helper_path, "r") as h_f:
            copyfileobj(h_f, m_f)

    def replace_filename(self, image_dict, line, str, h_f):
        start = line.split(str)[0]
        rest = line.split(str)[-1]
        name = rest.split(".")[0]
        for key, value in image_dict.items():
            if name == key:
                h_f.write(line)
            elif name in key:
                h_f.write(f"{start}{str}{key}.{value}\n")


class MaterialImage(models.Model):
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="material_images",
        verbose_name=_("Material image"),
    )
    image = models.ImageField(
        _("Image"), upload_to="uploads/django_cad_inspector/entity/"
    )

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
        upload_to="uploads/django_cad_inspector/scene/",
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
        upload_to="uploads/django_cad_inspector/scene/",
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
        doc = ezdxf.readfile(self.dxf.path)
        layer_dict = self.make_layer_dict(doc)
        # get model space
        msp = doc.modelspace()
        # prepare two helper files
        path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/django_cad_inspector/scene/temp.obj"
        )
        path2 = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/django_cad_inspector/scene/temp2.obj"
        )
        # iterate over layers
        for name, color in layer_dict.items():
            query = msp.query(f"MESH[layer=='{name}']")
            self.record_vertex_number(path, query)
            is_mesh = self.offset_face_number(path, path2)
            if not is_mesh:
                continue
            self.create_staged_entity(path2, name, color)
        # iterate over blocks
        for block in doc.blocks:
            # filter blacklisted blocks
            if block.name in settings.CAD_BLOCK_BLACKLIST:
                continue
            query = block.query("MESH")
            self.record_vertex_number(path, query)
            is_mesh = self.offset_face_number(path, path2)
            if not is_mesh:
                continue
            entity = self.create_block_entity(path2, block)
            # we look for insertions of the block
            for ins in msp.query(f"INSERT[name=='{block.name}']"):
                color = layer_dict[ins.dxf.layer]
                self.create_block_insertion(ins, block.name, entity, color)

    def make_layer_dict(self, doc):
        layer_dict = {}
        for layer in doc.layers:
            # filter blacklisted layers
            if layer.dxf.name in settings.CAD_LAYER_BLACKLIST:
                continue
            if layer.rgb:
                color = self.cad2hex(layer.rgb)
            else:
                color = self.cad2hex(layer.color)
            layer_dict[layer.dxf.name] = color
        return layer_dict

    def cad2hex(self, color):
        if isinstance(color, tuple):
            return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
        rgb24 = ezdxf.colors.DXF_DEFAULT_COLORS[color]
        return "#{:06X}".format(rgb24)

    def record_vertex_number(self, path, query):
        with open(path, "w") as f:
            for m in query:
                mb = MeshBuilder()
                mb.vertices = Vec3.list(m.vertices)
                mb.faces = m.faces
                f.write(meshex.obj_dumps(mb))
                f.write(f"# total vertices={len(m.vertices)}\n")

    def offset_face_number(self, path, path2):
        with open(path, "r") as f, open(path2, "w") as f2:
            # if file is empty, pass
            if len(f.readlines()) == 0:
                is_mesh = False
            else:
                # rewind file!
                f.seek(0)
                f2.write("# Generated by django-cad-inspector\n")
                # offset face number by total vertex number
                n = 0
                for line in f:
                    if line.startswith("v"):
                        f2.write(line)
                    elif line.startswith("# total vertices="):
                        n += int(line.split("=")[1])
                    elif line.startswith("f"):
                        fc = line.split(" ")
                        f2.write(f"f {int(fc[1])+n} {int(fc[2])+n} {int(fc[3])+n}\n")
                is_mesh = True
        return is_mesh

    def create_staged_entity(self, path2, name, color):
        with open(path2, "r") as f:
            entity = Entity.objects.create(
                title=_("Layer %(name)s") % {"name": name},
                description=_("Generated by django-cad-inspector"),
                switch=True,
                obj_model=File(f, name="object.obj"),
            )
            Staging.objects.create(
                scene=self,
                entity=entity,
                color=color,
                data={"Layer": name},
            )

    def create_block_entity(self, path2, block):
        with open(path2, "r") as f:
            # we create the block entity
            entity = Entity.objects.create(
                title=f"Block {block.name}",
                description="Generated by django-a-frame",
                switch=True,
                obj_model=File(f, name="object.obj"),
            )
        return entity

    def create_block_insertion(self, ins, block_name, entity, color):
        # extract attributes
        attrib_dict = {}
        if ins.attribs:
            for attr in ins.attribs:
                attrib_dict[attr.dxf.tag] = attr.dxf.text
        # for 3D rotated insertions we need origin of local coords
        origin = ins.ucs().origin
        # and vectors of local coords...
        R = np.asarray([list(ins.ucs().ux), list(ins.ucs().uy), list(ins.ucs().uz)])
        # ...to extract 3D rotation of insertion
        yaw, roll, pitch, gimbal_lock = self.rotation_matrix_to_euler_angles_zyx(R)
        Staging.objects.create(
            scene=self,
            entity=entity,
            color=color,
            position=(f"{origin[0]} {origin[2]} {-origin[1]}"),
            rotation=f"{degrees(-pitch)} {degrees(-yaw)} {degrees(roll)}",
            scale=f"{ins.dxf.xscale} {ins.dxf.zscale} {ins.dxf.yscale}",
            data={
                "Block": block_name,
                "Layer": ins.dxf.layer,
                "attribs": attrib_dict,
            },
        )

    def rotation_matrix_to_euler_angles_zyx(self, R):
        """
        From https://github.com/duolu/pyrotation

        Converting a rotation matrix representation to
        a rotation represented by three Euler angles (z-y'-x").

        CAUTION: Euler angles have a singularity when pitch = pi / 2 or - pi / 2,
        i.e., gimbal lock. In this case, yaw and roll angles can not be determined
        uniquely, and this function always return a zero yaw angle.

        """
        # This is the floating point error tolerance.
        EPSILON = 1e-6
        if fabs(fabs(R[2, 0]) - 1) < EPSILON:
            # cos(y) != 0, gimbal lock
            # CAUTION: y is always pi/2, and z is always 0
            y = copysign(pi / 2, -R[2, 0])
            x = 0
            z = atan2(R[0, 1], R[0, 2])
            gimbal_lock = True
            # print('gimbal lock!!!')
        else:
            # cos(y) == 0, normal situation
            # CAUTION: y is always in [-pi/2, pi/2]
            y = -asin(R[2, 0])
            cy = cos(y)
            x = atan2(R[2, 1] / cy, R[2, 2] / cy)
            z = atan2(R[1, 0] / cy, R[0, 0] / cy)
            gimbal_lock = False
        return z, y, x, gimbal_lock


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
        max_length=100,
        help_text="Left/Right - Up/Down - In/Out",
    )
    rotation = models.CharField(
        _("Rotation"),
        default="0 0 0",
        max_length=100,
        help_text="Pitch - Yaw - Roll",
    )
    scale = models.CharField(
        _("Scale"),
        default="1 1 1",
        max_length=100,
        help_text="Width - Heigth - Depth",
    )
    color = ColorField(_("Color"), default="#FFFFFF")
    data = models.JSONField(
        _("Data sheet"),
        null=True,
        blank=True,
    )
    wireframe = models.BooleanField(
        _("Wireframe"),
        default=False,
    )

    class Meta:
        verbose_name = _("Staging")
        verbose_name_plural = _("Stagings")

    # def __str__(self):
    # return _("Staging-%(id)d") % {"id": self.id}

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
