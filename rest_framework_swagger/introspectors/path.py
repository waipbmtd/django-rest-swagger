from rest_framework.viewsets import ViewSetMixin

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
                'responses': self.get_response_object_for_method(method)
            }
            for method in self.get_allowed_methods()
        ]

        serializer = serializers.OperationSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        return serializer.data

    def get_allowed_methods(self):
        if isinstance(self.callback, ViewSetMixin):
            return self.callback.http_method_names

        return self.callback.allowed_methods

    def get_response_object_for_method(self, method):
        data = []
        for status_code in STATUS_CODES.get(method, [200]):
            data.append({
                'status_code': status_code,
                'description': ''
            })
        serializer = serializers.ResponseSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        return serializer.data

    def get_tags(self):
        # TODO: something better
        urlparser = UrlParser()
        return urlparser.get_top_level_apis([{'path': self.path}])
