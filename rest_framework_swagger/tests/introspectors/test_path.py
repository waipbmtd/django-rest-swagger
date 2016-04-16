from django.conf.urls import url
from django.test import TestCase
from rest_framework import serializers, generics

from ...introspectors.path import PathIntrospector


class MySerializer(serializers.Serializer):
    pass


class FooListCreate(generics.ListCreateAPIView):
    serializer_class = MySerializer


class PathIntrospectorTest(TestCase):
    def setUp(self):
        self.path = r'/api/foo'
        self.pattern = url(self.path, FooListCreate.as_view())
        self.callback = FooListCreate

        self.sut = PathIntrospector(
            path=self.path,
            callback=self.callback,
            pattern=self.pattern
        )

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

    def test_get_path_parameters_without_any_parameters(self):
        self.assertEqual([], self.sut.get_path_parameters())

    def test_get_path_parameters_with_pk_parameter(self):
        self.sut.path = r'/api/foo/{pk}'
        result = self.sut.get_path_parameters()

        self.assertCountEqual(result, [{
            'name': 'pk',
            'required': True,
            'in': 'path'
        }])
