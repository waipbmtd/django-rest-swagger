from django.test import TestCase
from rest_framework import generics, serializers

from ...introspectors import method as introspectors


class MySerializer(serializers.Serializer):
    pass


class FooListCreate(generics.ListCreateAPIView):
    serializer_class = MySerializer


class ViewMethodIntrospectorTest(TestCase):
    def setUp(self):
        self.method = 'GET'
        self.view = FooListCreate()
        self.top_level_path = 'foo'

        self.sut = introspectors.ViewMethodIntrospector(
            method=self.method,
            view=self.view,
            top_level_path=self.top_level_path
        )

    def test_get_tags(self):
        result = self.sut.get_tags()
        expected = 'foo'

        self.assertEqual(expected, result)

    def test_get_description(self):
        self.assertEqual(
            FooListCreate().get_view_description(),
            self.sut.get_description()
        )

    def test_get_summary(self):
        self.assertEqual(
            FooListCreate().get_view_name(),
            self.sut.get_summary()
        )


class PathIntrospectorOverridesView(generics.ListCreateAPIView):
    serializer_class = MySerializer

    class Swagger:
        GET = {
            'tags': 'mytags',
            'summary': 'This is my summary',
            'description': 'This is my description of sorts.'
        }


class PathIntrospectorOverridesTest(TestCase):
    def setUp(self):
        self.method = 'GET'
        self.view = PathIntrospectorOverridesView()
        self.top_level_path = 'foo'

        self.sut = introspectors.ViewMethodIntrospector(
            method=self.method,
            view=self.view,
            top_level_path=self.top_level_path
        )

    def test_get_method_data_returns_declared_overrides(self):
        expected = self.view.Swagger.GET
        result = self.sut.get_method_data('GET')

        self.assertDictContainsSubset(expected, result)
