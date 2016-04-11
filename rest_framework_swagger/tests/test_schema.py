from unittest.mock import patch

from django.test import TestCase
from rest_framework import serializers

from .. import schema


class MySerializer(serializers.Serializer):
    """
    Serializes important data blah.
    """
    name = serializers.CharField(
        help_text='The name of the cigar'
    )


class SerializerSchemaGeneratorTest(TestCase):
    def setUp(self):
        self.sut = schema.SerializerSchemaGenerator(MySerializer)

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
        self.assertIsNone(self.sut.get_description())

    def test_get_fields(self):
        expected = self.sut.serializer_class().fields
        self.assertCountEqual(
            expected,
            self.sut.get_fields()
        )

    @patch('rest_framework_swagger.schema.PropertyGenerator')
    def test_get_properties(self, property_mock):
        with patch.object(
            schema.SerializerSchemaGenerator,
            'get_fields',
            return_value={'myfield': serializers.IntegerField()}
        ) as field_mock:
            data = {'maximum': 1, 'something': 'darkside'}
            property_mock.return_value.get_data.return_value = data
            result = self.sut.get_properties()

        expected = {'myfield': data}
        self.assertEqual(expected, result)

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


class CharFieldPropertyGeneratorTest(TestCase):
    def setUp(self):
        field = serializers.Field(
            help_text='Some text',
            required=False,
            allow_null=True,
        )

        self.sut = schema.PropertyGenerator(name='peterman', field=field)

    def test_get_name(self):
        self.assertEqual(self.sut.name, self.sut.get_name())

    def test_get_description(self):
        expected = self.sut.field.help_text
        self.assertEqual(expected, self.sut.get_description())

    def test_get_type(self):
        self.assertEqual('string', self.sut.get_type())

    def test_get_default(self):
        self.assertEqual(self.sut.field.default, self.sut.get_default())

    def test_get_max_length_set(self):
        self.sut.field = serializers.CharField(max_length=10)
        self.assertEqual(self.sut.field.max_length, self.sut.get_max_length())

    def test_get_max_length_none(self):
        self.assertIsNone(self.sut.get_min_length())

    def test_get_min_length_set(self):
        self.sut.field = serializers.CharField(min_length=10)
        self.assertEqual(self.sut.field.min_length, self.sut.get_min_length())

    def test_get_min_length_none(self):
        self.assertIsNone(self.sut.get_min_length())

    def test_get_required_if_field_required(self):
        self.sut.field.required = True
        self.assertTrue(self.sut.get_required())

    def test_get_required_if_not_allow_blank(self):
        self.sut.field = serializers.CharField(
            allow_blank=True
        )
        self.assertTrue(self.sut.get_required())

    def test_get_required_if_not_allow_null(self):
        self.sut.field.allow_null = False
        self.assertTrue(self.sut.get_required())

    def test_get_required_if_optional(self):
        self.assertFalse(self.sut.get_required())

    def test_get_enum_if_none(self):
        self.assertIsNone(self.sut.get_enum())

    def test_get_enum_if_list(self):
        """
        Given a list (no tuple), the method should return the list
        as is.
        """
        choices = ['a', 'b', 'c']
        self.sut.field = serializers.ChoiceField(choices=choices)
        self.assertCountEqual(choices, self.sut.get_enum())

    def test_get_enum_if_choices_tuple(self):
        """
        Given a list of choices, the method should return a list of
        the choices first element (key).
        """
        choices = [('a', 'The letter A'), ('b', 'The letter B!')]
        expected = [x[0] for x in choices]
        self.sut.field = serializers.ChoiceField(choices=choices)
        self.assertCountEqual(expected, self.sut.get_enum())
