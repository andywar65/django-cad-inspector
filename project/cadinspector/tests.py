from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import Entity


@override_settings(MEDIA_ROOT=Path(settings.MEDIA_ROOT).joinpath("tests"))
class ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        obj_path = Path(settings.BASE_DIR).joinpath(
            "cadinspector/static/cadinspector/tests/blue.obj"
        )
        mtl_path = Path(settings.BASE_DIR).joinpath(
            "cadinspector/static/cadinspector/tests/blue_changed.mtl"
        )
        with open(obj_path, "rb") as fobj, open(mtl_path, "rb") as fmtl:
            obj_content = fobj.read()
            mtl_content = fmtl.read()
        Entity.objects.create(
            title="Foo",
            description="bar",
            obj_model=SimpleUploadedFile("blue.obj", obj_content, "text/plain"),
            mtl_model=SimpleUploadedFile("blue_changed.mtl", mtl_content, "text/plain"),
        )

    @classmethod
    def tearDownClass(cls):
        """Checks existing files, then removes them"""
        try:
            path = Path(settings.MEDIA_ROOT).joinpath("uploads/cadinspector/entity/")
            list = [e for e in path.iterdir() if e.is_file()]
            for file in list:
                Path(file).unlink()
        except FileNotFoundError:
            pass

    def test_entity_str_method(self):
        ent = Entity.objects.get(title="Foo")
        self.assertEqual(ent.__str__(), "Foo")

    def test_entity_check_material_file_name(self):
        ent = Entity.objects.get(title="Foo")
        ent.check_material_file_name()
        path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/cadinspector/entity/blue.obj"
        )
        with open(path, "r") as f:
            for line in f:
                self.assertEqual(line, "mtllib blue_changed.mtl\n")
                break
