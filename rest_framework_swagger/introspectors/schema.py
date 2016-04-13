from .. import serializers
from .property import PropertyIntrospector


class SchemaObjectIntrospector(object):
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
            generator = PropertyIntrospector(key, field)
            data[key] = generator.get_data()

        return data
