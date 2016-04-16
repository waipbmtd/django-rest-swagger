import re

from .. import serializers
from ..urlparser import UrlParser

STATUS_CODES = {
    'OPTIONS': [200, 404],
    'GET': [200, 404],
    'POST': [201, 400],
    'PUT': [200, 404, 400],
    'PATCH': [200, 404, 400],
    'DELETE': [204, 404],
}


class PathIntrospector(object):
    def __init__(self, path, pattern, callback):
        self.path = path
        self.pattern = pattern
        self.callback = callback()

    def get_data(self):
        return self.get_methods()

    def get_methods(self):
        data = [
            {
                'tags': self.get_tags(),
                'method': method.lower(),
                'summary': self.callback.get_view_name(),
                'description': self.callback.get_view_description(),
                'responses': self.get_response_object_for_method(method),
                'parameters': self.get_parameters(method)
            }
            for method in self.get_allowed_methods()
        ]

        serializer = serializers.OperationSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        return serializer.data

    def get_allowed_methods(self):
        return self.callback.allowed_methods

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
        urlparser = UrlParser()
        return urlparser.get_top_level_apis([{'path': self.path}])

    def get_path_parameters(self):
        """
        Gets the parameters from the URL
        """
        url_params = re.findall('/{([^}]*)}', self.path)
        data = []

        for param in url_params:
            data.append({
                'in': 'path',
                'name': param,
                'type': 'string',
                'required': True
            })

        serializer = serializers.ParameterSerializer(data=data, many=True)
        serializer.is_valid()

        return serializer.data

    def get_schema(self, status_code):
        if 203 >= status_code >= 200:
            return self.get_success_schema()

    def get_success_schema(self):
        """
        Returns schema for successful responses.
        """
        if not hasattr(self.callback, 'get_serializer_class'):
            return

        serializer = self.callback.get_serializer_class()
        name = getattr(serializer, '__name__')
        if not name:
            return

        return {'$ref': '#/definitions/%s' % name}

    def get_parameters(self, method):
        data = []
        data += self.get_path_parameters()
        if method in ['POST', 'PUT', 'PATCH']:
            body = serializers.ParameterSerializer(data={
                'in': 'body',
                'name': 'body',
                'type': 'object',
                'schema': self.get_success_schema()
            })
            body.is_valid(raise_exception=True)
            data.append(body.data)

        return data
