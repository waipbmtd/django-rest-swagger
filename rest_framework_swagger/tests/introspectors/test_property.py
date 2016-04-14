from django.test import TestCase
from rest_framework import fields

from ...introspectors.property import PropertyIntrospector


class CommonPropertyTest(TestCase):
    def setUp(self):
        field = fields.Field(
            help_text='Some text',
            required=False,
            allow_null=True,
        )

        self.sut = PropertyIntrospector(name='peterman', field=field)

    def test_get_name(self):
        self.assertEqual(self.sut.name, self.sut.get_name())

    def test_get_description(self):
        expected = self.sut.field.help_text
        self.assertEqual(expected, self.sut.get_description())

    def test_get_type(self):
        self.sut.field = fields.CharField()
        self.assertEqual('string', self.sut.get_type())

    def test_get_format(self):
        self.assertIsNone(self.sut.get_format())

    def test_get_default(self):
        self.assertEqual(self.sut.field.default, self.sut.get_default())

    def test_get_max_length_none(self):
        self.assertIsNone(self.sut.get_min_length())

    def test_get_min_length_none(self):
        self.assertIsNone(self.sut.get_min_length())

    def test_get_required_if_field_required(self):
        self.sut.field.required = True
        self.assertTrue(self.sut.get_required())

    def test_get_required_if_not_allow_null(self):
        self.sut.field.allow_null = False
        self.assertTrue(self.sut.get_required())

    def test_get_required_if_optional(self):
        self.assertFalse(self.sut.get_required())

    def test_get_enum_if_none(self):
        self.assertIsNone(self.sut.get_enum())


class CharFieldTest(TestCase):
    def setUp(self):
        self.field = fields.CharField(
            help_text='Some text',
            max_length=100,
            min_length=10
        )

        self.sut = PropertyIntrospector(name='peterman', field=self.field)

    def test_get_type(self):
        self.assertEqual('string', self.sut.get_type())

    def test_get_max_length_set(self):
        self.assertEqual(self.field.max_length, self.sut.get_max_length())

    def test_get_min_length_set(self):
        self.sut.field = fields.CharField(min_length=10)
        self.assertEqual(self.field.min_length, self.sut.get_min_length())

    def test_get_required_if_not_allow_blank(self):
        self.sut.field = fields.CharField(
            allow_blank=True
        )
        self.assertTrue(self.sut.get_required())


class ChoiceFieldTest(TestCase):
    def setUp(self):
        field = fields.ChoiceField(
            choices=[]
        )

        self.sut = PropertyIntrospector(name='peterman', field=field)

    def test_get_enum_if_list(self):
        """
        Given a list (no tuple), the method should return the list
        as is.
        """
        choices = ['a', 'b', 'c']
        self.sut.field = fields.ChoiceField(choices=choices)
        self.assertCountEqual(choices, self.sut.get_enum())

    def test_get_enum_if_choices_tuple(self):
        """
        Given a list of choices, the method should return a list of
        the choices first element (key).
        """
        choices = [('a', 'The letter A'), ('b', 'The letter B!')]
        expected = [x[0] for x in choices]
        self.sut.field = fields.ChoiceField(choices=choices)
        self.assertCountEqual(expected, self.sut.get_enum())


class DecimalFieldTest(TestCase):
    def setUp(self):
        self.field = fields.DecimalField(
            max_digits=10,
            decimal_places=2,
            max_value=1000,
            min_value=0
        )
        self.sut = PropertyIntrospector(name='vandelay', field=self.field)

    def test_get_type(self):
        self.assertEqual('number', self.sut.get_type())

    def test_get_maximum(self):
        self.assertEqual(self.field.max_value, self.sut.get_maximum())

    def test_get_minimum(self):
        self.assertEqual(self.field.min_value, self.sut.get_minimum())


class DictFieldTest(TestCase):
    def setUp(self):
        self.field = fields.DictField()
        self.sut = PropertyIntrospector(name='vandelay', field=self.field)

    def test_get_type(self):
        self.assertEqual('object', self.sut.get_type())


class JSONFieldTest(TestCase):
    def setUp(self):
        self.field = fields.JSONField()
        self.sut = PropertyIntrospector(name='kramerica', field=self.field)

    def test_get_type(self):
        self.assertEqual('object', self.sut.get_type())


class IntegerFieldTest(TestCase):
    def setUp(self):
        self.field = fields.IntegerField()
        self.sut = PropertyIntrospector(name='seven', field=self.field)

    def test_get_type(self):
        self.assertEqual('integer', self.sut.get_type())


class FloatFieldTest(TestCase):
    def setUp(self):
        self.field = fields.FloatField()
        self.sut = PropertyIntrospector(name='seven', field=self.field)

    def test_get_type(self):
        self.assertEqual('number', self.sut.get_type())


class EmailFieldTest(TestCase):
    def setUp(self):
        self.field = fields.EmailField()
        self.sut = PropertyIntrospector(name='email', field=self.field)

    def test_get_type(self):
        self.assertEqual('string', self.sut.get_type())

    def test_get_format(self):
        self.assertEqual('email', self.sut.get_format())


class DateFieldTest(TestCase):
    def setUp(self):
        self.field = fields.DateField()
        self.sut = PropertyIntrospector(name='date', field=self.field)

    def test_get_format(self):
        self.assertEqual('date', self.sut.get_format())


class DateTimeFieldTest(TestCase):
    def setUp(self):
        self.field = fields.DateTimeField()
        self.sut = PropertyIntrospector(name='datetime', field=self.field)

    def test_get_format(self):
        self.assertEqual('date-time', self.sut.get_format())
