from unittest.mock import patch

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

    def test_path(self):
        self.assertEqual(self.path, self.sut.path)

    def test_pattern(self):
        self.assertEqual(self.pattern, self.sut.pattern)

    def test_callback(self):
        self.assertIsInstance(self.sut.callback, self.callback)

    @patch.object(PathIntrospector, 'get_allowed_methods',
                  return_value=['GET', 'PUT'])
    @patch('rest_framework_swagger.introspectors.ViewMethodIntrospector')
    def test_get_methods(self, introspector_mock, *args):
        # Mock the return value from the view method introspectors
        introspector_mock.factory.return_value.get_data.return_value = {
            'foo': 'bar',
        }
        with patch(
            'rest_framework_swagger.serializers.OperationSerializer'
        ) as serializer_mock:
            serializer_mock.return_value.is_valid.return_value = True
            serializer_mock.return_value.data = [{'fizz': 'buzz'}]
            result = self.sut.get_methods()

        allowed_methods = self.sut.get_allowed_methods()
        self.assertEqual(
            len(allowed_methods),
            introspector_mock.factory.call_count
        )

        for method in self.sut.get_allowed_methods():
            introspector_mock.factory.assert_any_call(
                method=method,
                top_level_path=self.sut.get_top_level_path(),
                view=self.sut.callback
            )

        self.assertCountEqual(result, serializer_mock.return_value.data)

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
