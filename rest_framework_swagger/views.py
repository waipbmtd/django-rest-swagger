from django.conf import settings
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.response import Response

from . import introspectors
from . import serializers, urlparser


class SwaggerUI(TemplateView):
    template_name = 'rest_framework_swagger/index.html'


class SwaggerJSON(APIView):
    contact = None
    info = None
    license = None

    def get(self, request):
        return Response(self.get_schema_data())

    def get_patterns(self):
        parser = urlparser.UrlParser()
        return parser.get_apis()

    def get_schema_data(self):
        serializer = serializers.SchemaSerializer(data={
            'info': self.get_info_data(),
            'paths': self.get_path_data(),
            'definitions': self.get_definitions()
        })
        serializer.is_valid(raise_exception=True)
        return serializer.data

    def get_info_data(self):
        data = self.get_setting('info') or {}
        data.update({
            'contact': self.get_setting('contact'),
            'license': self.get_setting('license'),
        })
        info = serializers.InfoSerializer(data=data)
        info.is_valid(raise_exception=True)

        return info.data

    def get_setting(self, key):
        setting = getattr(settings, 'SWAGGER_SETTINGS', {}) or {}
        return setting.get(key)

    def get_path_data(self):
        parser = urlparser.UrlParser()
        apis = parser.get_apis()

        data = {}
        for api in apis:
            introspector = introspectors.PathIntrospector(
                path=api['path'],
                callback=api['callback'],
                pattern=api['pattern'],
            )
            data[api['path']] = introspector.get_data()

        return data

    def get_definitions(self):
        definitions = {}
        for pattern in self.get_patterns():
            if not hasattr(pattern['callback'], 'get_serializer_class'):
                continue
            serializer_class = pattern['callback']().get_serializer_class()
            introspector = introspectors.SchemaObjectIntrospector(
                serializer_class
            )
            data = introspector.get_data()
            definitions[data['title']] = data

        return definitions
