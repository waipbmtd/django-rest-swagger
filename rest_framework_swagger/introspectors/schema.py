from .. import serializers
from .property import PropertyIntrospector


class SchemaObjectIntrospector(object):
    """
    Converts Serializer into Swagger Schema Object.

    """
    def __init__(self, serializer_class, method=None):
        assert method in [None, 'read', 'write'], (
            'method must be either read or write'
        )
        self.serializer_class = serializer_class
        self.method = method

    def get_title(self):
        """Returns the class name."""
        return getattr(self.serializer_class, '__name__')

    def get_description(self):
        """Returns the Serializer docstring."""
        doc = getattr(self.serializer_class, '__doc__') or ''
        return doc.strip()

    def get_fields(self):
        fields = self.serializer_class().fields
        if self.method == 'read':
            return [field for field in fields if not field.write_only]
        if self.method == 'write':
            return [field for field in fields if not field.read_only]

        return fields

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
            generator = PropertyIntrospector(key, field)
            data.update(generator.get_data())

        return data
