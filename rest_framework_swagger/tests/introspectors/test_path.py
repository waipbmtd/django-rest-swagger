from django.conf.urls import url
from django.test import TestCase
from rest_framework import serializers, generics, views

from ...introspectors.path import PathIntrospector


class MySerializer(serializers.Serializer):
    pass


class FooListCreate(generics.ListCreateAPIView):
    serializer_class = MySerializer


class PathIntrospectorTest(TestCase):
    def setUp(self):
        self.path = r'/api/foo/{pk}'
        self.pattern = url(self.path, FooListCreate.as_view())
        self.callback = FooListCreate

        self.sut = PathIntrospector(
            path=self.path,
            callback=self.callback,
            pattern=self.pattern
        )

    def test_get_tags(self):
        result = self.sut.get_tags()
        expected = ['api/foo']

        self.assertEqual(expected, result)

    def test_path(self):
        self.assertEqual(self.path, self.sut.path)

    def test_pattern(self):
        self.assertEqual(self.pattern, self.sut.pattern)

    def test_callback(self):
        self.assertIsInstance(self.sut.callback, self.callback)

    def test_get_methods(self):
        result = self.sut.get_methods()
        expected = [
            method.lower() for
            method in self.sut.callback.allowed_methods
        ]

        self.assertCountEqual(expected, result.keys())

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

    def test_get_path_parameters_with_pk_parameter(self):
        result = self.sut.get_path_parameters()
        self.assertCountEqual(result, [{
            'name': 'pk',
            'required': True,
            'in': 'path',
            'type': 'string'
        }])

    def test_get_allowed_methods_for_api_view(self):
        """
        Given that the callback is an APIView, the allowed_methods
        list should be returned.
        """
        self.assertIsInstance(self.sut.callback, views.APIView)
        expected = self.sut.callback.allowed_methods
        result = self.sut.get_allowed_methods()

        self.assertCountEqual(expected, result)

    def test_get_allowed_methods_for_viewset_list(self):
        viewset = viewsets.GenericViewset.as_view({'get': 'list'})
        viewset.suffix = 'List'
        expected = ['get', 'post']




class PathIntrospectorOverridesView(generics.ListCreateAPIView):
    serializer_class = MySerializer

    class Swagger:
        GET = {
            'tags': ['my tags'],
            'summary': 'This is my summary',
            'description': 'This is my description of sorts.'
        }


class PathIntrospectorOverridesTest(TestCase):
    def setUp(self):
        self.path = r'/api/fizz'
        self.pattern = url(self.path, PathIntrospectorOverridesView.as_view())
        self.callback = PathIntrospectorOverridesView

        self.sut = PathIntrospector(
            path=self.path,
            pattern=self.pattern,
            callback=self.callback
        )

    def test_get_method_data_returns_declared_overrides(self):
        expected = self.callback.Swagger.GET
        result = self.sut.get_method_data('GET')

        self.assertDictContainsSubset(expected, result)
