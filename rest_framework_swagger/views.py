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
            'paths': self.get_path_data()
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
                pattern=api['pattern']
            )
            data[api['path']] = introspector.get_data()

        return data


class SwaggerJSON2(APIView):
    def get(self, request):
        info = serializers.InfoSerializer(data={
            'title': 'hello',
            'description': '## This is my example',
            'termsOfService': 'your mother',
            'version': 'infinty'
        })
        info.is_valid(raise_exception=True)

        properties = serializers.PropertySerializer(
            many=True,
            data=[{
                'name': 'foo',
                'description': 'foo bizz',
                'type': 'string',
            }, {
                'name': 'email',
                'description': 'The email sent by x',
                'type': 'string',
                'format': 'email'
            }]
        )
        properties.is_valid(raise_exception=True)
        properties_data = {k: v for d in properties.data for k, v in d.items()}

        schema = serializers.SchemaObjectSerializer(data={
            'title': 'Foo object',
            'description': 'The very important foo object',
            'properties': properties_data
        })
        schema.is_valid(raise_exception=True)
        responses = serializers.ResponseSerializer(
            many=True,
            data=[{
                'status_code': '200',
                'description': 'All Good',
                'schema': schema.data
            }, {
                'status_code': '404',
                'description': 'Not Found',
            }]
        )
        responses.is_valid(raise_exception=True)
        responses_data = {k: v for d in responses.data for k, v in d.items()}

        operation = serializers.OperationSerializer(data={
            'tags': ['foo'],
            'responses': responses_data,
            'deprecated': True
        })
        operation.is_valid(raise_exception=True)

        parameters = serializers.ParameterSerializer(data=[{
            'name': 'foo',
            'in': 'query'
        }], many=True)
        parameters.is_valid(raise_exception=True)

        getPath = serializers.PathItemSerializer(data={
            #'parameters': parameters.data,
            'get': operation.data
        })
        getPath.is_valid(raise_exception=True)
        paths = {
            '/mypath': getPath.data,
            '/mypath2': getPath.data
        }

        serializer = serializers.SchemaSerializer(data={
            'swagger': '2.0',
            'info': info.data,
            'host': request.get_host(),
            'basePath': '/my-api/',
            'schemes': ['http', 'https'],
            'consumes': ['application/json'],
            'produces': ['application/json'],
        })
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        data['paths'] = paths

        return Response(data)
