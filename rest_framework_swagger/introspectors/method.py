from rest_framework import parsers
from .. import serializers


STATUS_CODES = {
    'OPTIONS': [200, 404],
    'GET': [200, 404],
    'POST': [201, 400],
    'PUT': [200, 404, 400],
    'PATCH': [200, 404, 400],
    'DELETE': [204, 404],
}


class SchemaType(object):
    READ = 'Read'
    WRITE = 'Write'


class ViewMethodIntrospector(object):
    SCHEMA_TYPE = None

    @classmethod
    def factory(cls, method, view, top_level_path):
        # TODO: handle OPTIONS, TRACE, CONNECT, HEAD
        mapping = {
            'GET': GetListIntrospector,
            'POST': PostIntrospector,
            'PUT': PutIntrospector,
            'PATCH': PatchIntrospector,
            'DELETE': DeleteIntrospector
        }
        klass = mapping.get(method) or mapping['GET']  # default for now
        return klass(method, view, top_level_path)

    def __init__(self, method, view, top_level_path):
        self.method = method
        self.view = view
        self.top_level_path = top_level_path
        self.override = getattr(self.view, 'Swagger', None)

        assert self.SCHEMA_TYPE in [SchemaType.READ, SchemaType.WRITE, None]

    def get_data(self):
        return self.get_method_data(self.method)

    def get_method_data(self, method):
        data = {
            'tags': self.get_tags(),
            'method': method.lower(),
            'summary': self.get_summary(),
            'description': self.get_description(),
            'responses': self.get_response_object_for_method(method),
            'parameters': self.get_parameters()
        }
        # Overwrite introspected data using definitions found in Swagger class
        data.update(getattr(self.override, method, {}))

        return data

    def get_description(self):
        return self.view.get_view_description()

    def get_summary(self):
        return self.view.get_view_name()

    def get_response_object_for_method(self, method):
        data = []
        for status_code in STATUS_CODES.get(method, [200]):
            data.append({
                'status_code': status_code,
                'description': '',
                'schema': self.get_schema(status_code)
            })
        serializer = serializers.ResponseSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        return serializer.data

    def get_tags(self):
        return self.top_level_path

    def get_schema(self, status_code):
        if 203 >= status_code >= 200:
            return self.get_success_schema()

    def get_success_schema(self, method='read'):
        """
        Returns schema for successful responses.
        """
        if not hasattr(self.view, 'get_serializer_class'):
            return
        if self.SCHEMA_TYPE is None:
            return

        serializer = self.view.get_serializer_class()
        name = getattr(serializer, '__name__')
        if not name:
            return

        return {
            '$ref': '#/definitions/{name}{schema_type}'.format(
                name=name,
                schema_type=self.SCHEMA_TYPE
            )
        }

    def get_parameters(self):
        return []


class ReadMixin(object):
    SCHEMA_TYPE = SchemaType.READ


class WriteMixin(object):
    SCHEMA_TYPE = SchemaType.WRITE

    def accepts_form_data(self):
        """
        Returns True if the APIView accepts form data.

        These include:
            - application/x-www-form-urlencoded
            - multipart/form-data
        """
        for parser in self.view.get_parsers():
            if isinstance(parser, parsers.FormParser):
                return True
            if isinstance(parser, parsers.MultiPartParser):
                return True

        return False

    def get_parameters(self):
        parameters = super().get_parameters()
        # TODO: determine which type of parameters to return based
        # on the parser classes
        body = serializers.ParameterSerializer(data={
            'in': 'body',
            'name': 'body',
            'type': 'object',
            'schema': self.get_success_schema(method='write')
        })
        body.is_valid(raise_exception=True)

        parameters.append(body.data)


class GetListIntrospector(ReadMixin, ViewMethodIntrospector):
    """
        - filters
        - serializer / model schema
    """
    pass


class GetInstanceIntrospector(ReadMixin, ViewMethodIntrospector):
    """
        - no filters
        - model schema
        - URL parameter (self.lookup_kwarg?)
    """
    pass


class PostIntrospector(WriteMixin, ViewMethodIntrospector):
    """
        - everything from retrieve
        - if form-data: form parameters, else body
    """


class PutIntrospector(WriteMixin, ViewMethodIntrospector):
    """
        = form-data / JSON whatevs
    """
    pass


class PatchIntrospector(WriteMixin, ViewMethodIntrospector):
    """
    Make every form data field optional
    """
    pass


class DeleteIntrospector(ViewMethodIntrospector):
    """
        - retrieve
        - no model schema
    """
    SCHEMA_TYPE = None
