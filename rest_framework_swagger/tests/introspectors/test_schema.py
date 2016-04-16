from unittest.mock import patch

from django.test import TestCase
from rest_framework import serializers

from ...introspectors import schema


class MySerializer(serializers.Serializer):
    """
    Serializes important data blah.
    """
    name = serializers.CharField(
        help_text='The name of the cigar'
    )


class SerializerSchemaGeneratorTest(TestCase):
    def setUp(self):
        self.sut = schema.SchemaObjectIntrospector(MySerializer)

    def test_serializer_class_bound(self):
        self.assertEqual(
            self.sut.serializer_class,
            MySerializer
        )

    def test_get_title(self):
        expected = self.sut.serializer_class.__name__
        self.assertEqual(expected, self.sut.get_title())

    def test_get_description_when_docstring_present(self):
        expected = self.sut.serializer_class.__doc__.strip()
        self.assertEqual(expected, self.sut.get_description())

    def test_get_description_when_no_docstring(self):
        self.sut.serializer_class.__doc__ = None
        self.assertEqual('', self.sut.get_description())

    def test_get_fields(self):
        expected = self.sut.serializer_class().fields
        self.assertCountEqual(
            expected,
            self.sut.get_fields()
        )

    @patch('rest_framework_swagger.introspectors.schema.PropertyIntrospector')
    def test_get_properties(self, property_mock):
        with patch.object(
            schema.SchemaObjectIntrospector,
            'get_fields',
            return_value={'myfield': serializers.IntegerField()}
        ) as field_mock:
            data = {'maximum': 1, 'something': 'darkside'}
            property_mock.return_value.get_data.return_value = data
            result = self.sut.get_properties()

        self.assertEqual(data, result)

        for name, field in field_mock.return_value.items():
            property_mock.assert_called_once_with(name, field)

    def test_get_data(self):
        title = 'Vandelay Industries'
        description = 'Fine latex products'
        properties = {
            'name': {
                'description': 'Your name',
            },
            'age': {
                'description': 'Your age'
            }
        }

        with patch.multiple(
            self.sut,
            get_title=lambda: title,
            get_description=lambda: description,
            get_properties=lambda: properties
        ):
            result = self.sut.get_data()

        expected = {
            'title': title,
            'description': description,
            'type': 'object',
            'properties': properties
        }

        self.assertEqual(expected, result)
