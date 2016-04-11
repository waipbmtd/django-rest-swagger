from . import serializers


class PropertyGenerator(object):
    """
    Converts Serializer Field into Swagger Property Object.
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
        return 'string'

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

    #format = serializers.ChoiceField(
    #    required=False,
    #    choices=FORMATS
    #)
    #multipleOf = serializers.FloatField(required=False)
    #maximum = serializers.FloatField(required=False)
    #exclusiveMaximum = serializers.FloatField(required=False)
    #minimum = serializers.FloatField(required=False)
    #exclusiveMinimum = serializers.FloatField(required=False)
    #maxLength = serializers.IntegerField(required=False)
    #minLength = serializers.IntegerField(required=False)
    #pattern = serializers.CharField(required=False)
    #maxItems = serializers.IntegerField(required=False)
    #minItems = serializers.IntegerField(required=False)
    #uniqueItems = serializers.BooleanField(default=False, required=False)
    #maxProperties = serializers.IntegerField(required=False)
    #minProperties = serializers.IntegerField(required=False)
    #enum = serializers.ListField(
    #    required=False,
    #    child=serializers.CharField(),
    #)


class SerializerSchemaGenerator(object):
    """
    Converts Serializer into Swagger Schema Object.
    """
    def __init__(self, serializer_class):
        self.serializer_class = serializer_class

    def get_title(self):
        """Returns the class name."""
        return self.serializer_class.__name__

    def get_description(self):
        """Returns the Serializer docstring."""
        doc = self.serializer_class.__doc__
        if not doc:
            return

        return doc.strip()

    def get_fields(self):
        return self.serializer_class().fields

    def get_data(self):
        serializer = serializers.SchemaObjectSerializer(data={
            'title': self.get_title(),
            'description': self.get_description(),
            'properties': self.get_properties()
        })
        serializer.is_valid(raise_exception=True)

        return serializer.data

    def get_properties(self):
        data = {}
        for key, field in self.get_fields().items():
            generator = PropertyGenerator(key, field)
            data[key] = generator.get_data()

        return data
