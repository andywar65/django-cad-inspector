from pathlib import Path

import ezdxf
import numpy as np
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from django_cad_inspector.models import Entity, MaterialImage, Scene, Staging


@override_settings(MEDIA_ROOT=Path(settings.MEDIA_ROOT).joinpath("tests"))
@override_settings(CAD_LAYER_BLACKLIST=["Defpoints"])
@override_settings(CAD_BLOCK_BLACKLIST=["*Model_Space"])
class ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        obj_path = Path(settings.BASE_DIR).joinpath("tests/static/tests/blue.obj")
        mtl_path = Path(settings.BASE_DIR).joinpath(
            "tests/static/tests/blue_changed.mtl"
        )
        img_path = Path(settings.BASE_DIR).joinpath(
            "tests/static/tests/image_changed.jpg"
        )
        dxf_path = Path(settings.BASE_DIR).joinpath("tests/static/tests/sample.dxf")
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
        Entity.objects.create(
            title="Bar",
            description="baz",
        )

    @classmethod
    def tearDownClass(cls):
        """Checks existing files, then removes them"""
        try:
            path = Path(settings.MEDIA_ROOT).joinpath(
                "uploads/django_cad_inspector/entity/"
            )
            list = [e for e in path.iterdir() if e.is_file()]
            for file in list:
                Path(file).unlink()
        except FileNotFoundError:
            pass
        try:
            path = Path(settings.MEDIA_ROOT).joinpath(
                "uploads/django_cad_inspector/scene/"
            )
            list = [e for e in path.iterdir() if e.is_file()]
            for file in list:
                Path(file).unlink()
        except FileNotFoundError:
            pass

    def test_cad_inspector_group_exists(self):
        self.assertTrue(Group.objects.filter(name="Dj CAD Inspector").exists())

    def test_entity_str_method(self):
        ent = Entity.objects.get(title="Foo")
        self.assertEqual(ent.__str__(), "Foo")

    def test_metrial_image_str_method(self):
        ent = Entity.objects.get(title="Foo")
        mtlimg = ent.material_images.first()
        self.assertEqual(mtlimg.__str__(), "image_changed.jpg")

    def test_entity_check_material_file_name(self):
        ent = Entity.objects.get(title="Foo")
        ent.check_material_file_name()
        path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/django_cad_inspector/entity/blue.obj"
        )
        with open(path, "r") as f:
            self.assertEqual(f.readline(), "Foo\n")
            self.assertEqual(f.readline(), "mtllib blue_changed.mtl\n")
            self.assertEqual(f.readline(), "bar\n")

    def test_entity_check_image_file_name(self):
        ent = Entity.objects.get(title="Foo")
        ent.check_image_file_name()
        path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/django_cad_inspector/entity/blue_changed.mtl"
        )
        with open(path, "r") as f:
            self.assertEqual(f.readline(), "Foo\n")
            self.assertEqual(f.readline(), "before map_Ka image_changed.jpg\n")
            self.assertEqual(f.readline(), "before map_Kd image_changed.jpg\n")
            self.assertEqual(f.readline(), "bar\n")

    def test_action_check_file_names_status_code(self):
        ent = Entity.objects.get(title="Foo")
        data = {
            "action": "check_file_names",
            "_selected_action": [
                ent.id,
            ],
        }
        change_url = reverse("admin:django_cad_inspector_entity_changelist")
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
        change_url = reverse("admin:django_cad_inspector_entity_changelist")
        self.client.login(username="boss", password="p4s5w0r6")
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(f"Checked file: {ent.obj_model.name}", messages)
        self.assertIn(
            f"Checked images for file: {ent.mtl_model.name}",
            messages,
        )

    def test_action_delete_unstaged_entities_status_code(self):
        staged = Entity.objects.get(title="Foo")
        unstaged = Entity.objects.get(title="Bar")
        data = {
            "action": "delete_unstaged_entities",
            "_selected_action": [staged.id, unstaged.id],
        }
        change_url = reverse("admin:django_cad_inspector_entity_changelist")
        self.client.login(username="boss", password="p4s5w0r6")
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_action_delete_unstaged_entities_messages(self):
        staged = Entity.objects.get(title="Foo")
        unstaged = Entity.objects.get(title="Bar")
        data = {
            "action": "delete_unstaged_entities",
            "_selected_action": [staged.id, unstaged.id],
        }
        change_url = reverse("admin:django_cad_inspector_entity_changelist")
        self.client.login(username="boss", password="p4s5w0r6")
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(f"Deleted unstaged entity: {unstaged.title}", messages)
        self.assertNotIn(f"Deleted unstaged entity: {staged.title}", messages)

    def test_scene_str_method(self):
        scn = Scene.objects.get(title="Foo")
        self.assertEqual(scn.__str__(), "Foo")

    # def test_staging_str_method(self):
    # scn = Scene.objects.get(title="Foo")
    # stg = scn.staged_entities.first()
    # self.assertEqual(stg.__str__(), f"Staging-{stg.id}")

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

    def test_make_layer_dict_blacklist(self):
        scn = Scene.objects.get(title="Foo")
        doc = ezdxf.readfile(scn.dxf.path)
        layer_dict = scn.make_layer_dict(doc)
        self.assertFalse("Defpoints" in layer_dict)

    def test_scene_save_method(self):
        scn = Scene.objects.get(title="Foo")
        stg_before = scn.staged_entities.first()
        dxf_path = Path(settings.BASE_DIR).joinpath("tests/static/tests/sample.dxf")
        with open(dxf_path, "rb") as fdxf:
            dxf_content = fdxf.read()
        scn.dxf = SimpleUploadedFile("sample.dxf", dxf_content, "image/x-dxf")
        scn.save()
        self.assertIsNot(scn.dxf.name, "uploads/django_cad_inspector/scene/sample.dxf")
        stg_after = scn.staged_entities.first()
        self.assertIsNot(stg_before.id, stg_after.id)
        self.assertFalse(
            scn.staged_entities.filter(entity__title="Block *Model_Space").exists()
        )

    def test_entity_creation_process(self):
        scn = Scene.objects.get(title="Foo")
        doc = ezdxf.readfile(scn.dxf.path)
        msp = doc.modelspace()
        path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/django_cad_inspector/scene/temp.obj"
        )
        query = msp.query("MESH[layer=='red']")
        scn.record_vertex_number(path, query)
        with open(path, "r") as f:
            for line in f:
                if line.startswith("# total vertices="):
                    break
        self.assertEqual(line, "# total vertices=24\n")
        path2 = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/django_cad_inspector/scene/temp2.obj"
        )
        is_mesh = scn.offset_face_number(path, path2)
        self.assertTrue(is_mesh)
        scn.create_staged_entity(path2, "red", "#FF0000")
        stg = Staging.objects.last()
        self.assertEqual(stg.data, {"Layer": "red"})

    def test_block_creation_process(self):
        scn = Scene.objects.get(title="Foo")
        doc = ezdxf.readfile(scn.dxf.path)
        block = doc.blocks["sample"]
        path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/django_cad_inspector/scene/temp.obj"
        )
        query = block.query("MESH")
        scn.record_vertex_number(path, query)
        with open(path, "r") as f:
            for line in f:
                if line.startswith("# total vertices="):
                    break
        self.assertEqual(line, "# total vertices=24\n")
        path2 = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/django_cad_inspector/scene/temp2.obj"
        )
        is_mesh = scn.offset_face_number(path, path2)
        self.assertTrue(is_mesh)
        entity = scn.create_block_entity(path2, block)
        self.assertEqual(entity.title, "Block sample")
        msp = doc.modelspace()
        for ins in msp.query("INSERT[name=='sample']"):
            scn.create_block_insertion(ins, block.name, entity, "#FF0000")
            break
        stg = Staging.objects.last()
        self.assertEqual(stg.data["Block"], "sample")
        self.assertEqual(stg.data["Layer"], "0")
        self.assertEqual(stg.data["attribs"], {"FIRST": "pitch", "SECOND": "-30"})

    def test_rotation_matrix_to_euler_angles(self):
        scn = Scene.objects.get(title="Foo")
        doc = ezdxf.readfile(scn.dxf.path)
        msp = doc.modelspace()
        for ins in msp.query("INSERT[name=='sample']"):
            R = np.asarray([list(ins.ucs().ux), list(ins.ucs().uy), list(ins.ucs().uz)])
            yaw, roll, pitch, gimbal_lock = scn.rotation_matrix_to_euler_angles_zyx(R)
            break
        self.assertAlmostEqual(yaw, 1.2246467991473535e-16)
        self.assertAlmostEqual(roll, -0.0)
        self.assertAlmostEqual(pitch, 0.523598775598299)

    def test_scene_list_view_status_code(self):
        response = self.client.get(reverse("django_cad_inspector:scene_list"))
        self.assertEqual(response.status_code, 200)

    def test_entity_list_view_status_code(self):
        response = self.client.get(reverse("django_cad_inspector:entity_list"))
        self.assertEqual(response.status_code, 200)

    def test_scene_detail_view_status_code(self):
        scn = Scene.objects.get(title="Foo")
        response = self.client.get(
            reverse("django_cad_inspector:scene_detail", kwargs={"pk": scn.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_scene_detail_view_no_cursor(self):
        scn = Scene.objects.get(title="Foo")
        response = self.client.get(
            reverse("django_cad_inspector:scene_detail", kwargs={"pk": scn.id})
            + "?no-cursor=true"
        )
        self.assertTrue("no_cursor" in response.context)

    def test_entity_detail_view_status_code(self):
        ent = Entity.objects.get(title="Foo")
        response = self.client.get(
            reverse("django_cad_inspector:entity_detail", kwargs={"pk": ent.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_scene_list_view_status_template_used(self):
        response = self.client.get(reverse("django_cad_inspector:scene_list"))
        self.assertTemplateUsed(response, "django_cad_inspector/scene_list.html")

    def test_entity_list_view_status_template_used(self):
        response = self.client.get(reverse("django_cad_inspector:entity_list"))
        self.assertTemplateUsed(response, "django_cad_inspector/entity_list.html")

    def test_scene_detail_view_status_template_used(self):
        scn = Scene.objects.get(title="Foo")
        response = self.client.get(
            reverse("django_cad_inspector:scene_detail", kwargs={"pk": scn.id})
        )
        self.assertTemplateUsed(response, "django_cad_inspector/scene_detail.html")

    def test_entity_detail_view_status_template_used(self):
        ent = Entity.objects.get(title="Foo")
        response = self.client.get(
            reverse("django_cad_inspector:entity_detail", kwargs={"pk": ent.id})
        )
        self.assertTemplateUsed(response, "django_cad_inspector/entity_detail.html")

    def test_home_view_status_code(self):
        response = self.client.get(reverse("django_cad_inspector:home"))
        self.assertEqual(response.status_code, 302)

    def test_home_view_status_code_follow(self):
        response = self.client.get(reverse("django_cad_inspector:home"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home_view_status_template_used_follow(self):
        response = self.client.get(reverse("django_cad_inspector:home"), follow=True)
        self.assertTemplateUsed(response, "django_cad_inspector/scene_list.html")
