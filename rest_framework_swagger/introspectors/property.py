from rest_framework import fields
from .. import serializers


TYPE_MAP = {
    fields.BooleanField: 'boolean',
    fields.CharField: 'string',
    fields.ChoiceField: 'string',
    fields.DecimalField: 'number',
    fields.DictField: 'object',
    fields.Field: 'string',
    fields.FileField: 'string',
    fields.FloatField: 'number',
    fields.JSONField: 'object',
    fields.ImageField: 'string',
    fields.IntegerField: 'integer',
    fields.ModelField: 'string',
    fields.RegexField: 'string',
    fields.SerializerMethodField: 'string',
    fields.SlugField: 'string',
    fields.TimeField: 'string',
    fields.NullBooleanField: 'boolean'
}

FORMAT_MAP = {
    fields.EmailField: 'email',
    fields.DateField: 'date',
    fields.DateTimeField: 'date-time',
    fields.URLField: 'uri',
}


class PropertyIntrospector(object):
    """
    Converts DRF Serializer Field into Swagger Property Object.
    """
    def __init__(self, name, field):
        self.name = name
        self.field = field

    def get_data(self):
        serializer = serializers.PropertySerializer(data={
            'name': self.name,
            'description': self.get_description(),
            'type': self.get_type(),
            'default': self.get_default(),
            'maxLength': self.get_max_length(),
            'minLength': self.get_min_length(),
            'required': self.get_required(),
            'maximum': self.get_maximum(),
            'minimum': self.get_minimum(),
            'enum': self.get_enum(),
        })
        serializer.is_valid(raise_exception=True)

        return serializer.data

    def get_name(self):
        return self.name

    def get_description(self):
        return getattr(self.field, 'help_text', None)

    def get_type(self):
        return TYPE_MAP.get(self.field.__class__, 'string')

    def get_format(self):
        return FORMAT_MAP.get(self.field.__class__, None)

    def get_default(self):
        return getattr(self.field, 'default', None)

    def get_max_length(self):
        return getattr(self.field, 'max_length', None)

    def get_min_length(self):
        return getattr(self.field, 'min_length', None)

    def get_required(self):
        if self.field.required:
            return True
        if not self.field.allow_null:
            return True
        if not getattr(self.field, 'allow_blank', True):
            return True

        return False

    def get_maximum(self):
        return getattr(self.field, 'max_value', None)

    def get_minimum(self):
        return getattr(self.field, 'min_value', None)

    def get_enum(self):
        choices = getattr(self.field, 'choices', None)
        if not choices:
            return
        enums = []
        for choice in choices:
            if isinstance(choice, list) or isinstance(choice, tuple):
                if not len(choice):
                    continue
                enum = choice[0]
            else:
                enum = choice
            enums.append(enum)

        return enums



