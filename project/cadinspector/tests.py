from pathlib import Path

import ezdxf
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Entity, MaterialImage, Scene, Staging


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
        img_path = Path(settings.BASE_DIR).joinpath(
            "cadinspector/static/cadinspector/tests/image_changed.jpg"
        )
        dxf_path = Path(settings.BASE_DIR).joinpath(
            "cadinspector/static/cadinspector/tests/sample.dxf"
        )
        with open(obj_path, "rb") as fobj:
            obj_content = fobj.read()
        with open(mtl_path, "rb") as fmtl:
            mtl_content = fmtl.read()
        with open(img_path, "rb") as fimg:
            img_content = fimg.read()
        with open(dxf_path, "rb") as fdxf:
            dxf_content = fdxf.read()
        ent = Entity.objects.create(
            title="Foo",
            description="bar",
            obj_model=SimpleUploadedFile("blue.obj", obj_content, "text/plain"),
            mtl_model=SimpleUploadedFile("blue_changed.mtl", mtl_content, "text/plain"),
        )
        MaterialImage.objects.create(
            entity=ent,
            image=SimpleUploadedFile("image_changed.jpg", img_content, "image/jpeg"),
        )
        User.objects.create_superuser("boss", "test@example.com", "p4s5w0r6")
        scn = Scene.objects.create(
            title="Foo",
            description="baz",
            dxf=SimpleUploadedFile("sample.dxf", dxf_content, "image/x-dxf"),
        )
        Staging.objects.create(
            scene=scn,
            entity=ent,
            data={
                "Key": "<script>alert('Foo')</script>",
            },
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
        try:
            path = Path(settings.MEDIA_ROOT).joinpath("uploads/cadinspector/scene/")
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

    def test_entity_check_image_file_name(self):
        ent = Entity.objects.get(title="Foo")
        ent.check_image_file_name()
        path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/cadinspector/entity/blue_changed.mtl"
        )
        with open(path, "r") as f:
            for line in f:
                self.assertEqual(line, "before map_Ka image_changed.jpg\n")
                break

    def test_action_check_file_names_status_code(self):
        ent = Entity.objects.get(title="Foo")
        data = {
            "action": "check_file_names",
            "_selected_action": [
                ent.id,
            ],
        }
        change_url = reverse("admin:cadinspector_entity_changelist")
        self.client.login(username="boss", password="p4s5w0r6")
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_action_check_file_names_messages(self):
        ent = Entity.objects.get(title="Foo")
        data = {
            "action": "check_file_names",
            "_selected_action": [
                ent.id,
            ],
        }
        change_url = reverse("admin:cadinspector_entity_changelist")
        self.client.login(username="boss", password="p4s5w0r6")
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(f"Checked file: {ent.obj_model.name}", messages)
        self.assertIn(
            f"Checked images for file: {ent.mtl_model.name}",
            messages,
        )

    def test_scene_str_method(self):
        scn = Scene.objects.get(title="Foo")
        self.assertEqual(scn.__str__(), "Foo")

    def test_staging_str_method(self):
        scn = Scene.objects.get(title="Foo")
        stg = scn.staged_entities.first()
        self.assertEqual(stg.__str__(), f"Staging-{stg.id}")

    def test_staging_popupcontent_method_bleached(self):
        scn = Scene.objects.get(title="Foo")
        stg = scn.staged_entities.first()
        self.assertEqual(stg.popupContent(), "Key: \n")

    def test_staging_popupcontent_method(self):
        scn = Scene.objects.get(title="Foo")
        stg = scn.staged_entities.first()
        stg.data = {"Key": "Foo"}
        stg.save()
        self.assertEqual(stg.popupContent(), "Key: Foo\n")

    def test_staging_popupcontent_method_attribs(self):
        scn = Scene.objects.get(title="Foo")
        stg = scn.staged_entities.first()
        stg.data = {"attribs": {"Key": "Foo"}}
        stg.save()
        self.assertEqual(stg.popupContent(), "Attributes:\n--Key: Foo\n")

    def test_cad2hex_tuple(self):
        scn = Scene.objects.get(title="Foo")
        color = (128, 128, 128)
        self.assertEqual(scn.cad2hex(color), "#808080")

    def test_cad2hex_default(self):
        scn = Scene.objects.get(title="Foo")
        color = 128
        self.assertEqual(scn.cad2hex(color), "#00261C")

    def test_make_layer_dict(self):
        scn = Scene.objects.get(title="Foo")
        doc = ezdxf.readfile(scn.dxf.path)
        layer_dict = scn.make_layer_dict(doc)
        self.assertEqual(layer_dict["0"], "#FFFFFF")

    def test_entity_creation_process(self):
        scn = Scene.objects.get(title="Foo")
        doc = ezdxf.readfile(scn.dxf.path)
        msp = doc.modelspace()
        path = Path(settings.MEDIA_ROOT).joinpath("uploads/cadinspector/scene/temp.obj")
        scn.record_vertex_number(path, msp, "red")
        with open(path, "r") as f:
            for line in f:
                if line.startswith("# total vertices="):
                    break
        self.assertEqual(line, "# total vertices=24\n")
        path2 = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/cadinspector/scene/temp2.obj"
        )
        is_mesh = scn.offset_face_number(path, path2)
        self.assertTrue(is_mesh)
        scn.create_staged_entity(path2, "red", "#FF0000")
        stg = Staging.objects.last()
        self.assertEqual(stg.data, {"Layer": "red"})
