import re

from .. import introspectors, serializers
from ..urlparser import UrlParser


class PathIntrospector(object):
    def __init__(self, path, pattern, callback):
        self.path = path
        self.pattern = pattern
        self.callback = callback()
        self.override = getattr(self.callback, 'Swagger', None)

    def get_data(self):
        parameters = self.get_path_parameters()
        data = self.get_methods()
        data.update({'parameters': parameters})

        return data

    def get_methods(self):
        data = []
        top_level_path = self.get_top_level_path()
        for method in self.get_allowed_methods():
            introspector = introspectors.ViewMethodIntrospector.factory(
                method=method,
                view=self.callback,
                top_level_path=top_level_path
            )
            data.append(introspector.get_data())

        serializer = serializers.OperationSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        return serializer.data

    def get_allowed_methods(self):
        # TODO: check view vs. viewset
        return self.callback.allowed_methods

    def get_top_level_path(self):
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
