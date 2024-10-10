from django.test import TestCase

from .models import Entity


class ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Entity.objects.create(
            title="Foo",
            description="bar",
        )

    def test_entity_str_method(self):
        draw = Entity.objects.get(title="Foo")
        self.assertEqual(draw.__str__(), "Foo")
