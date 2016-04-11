from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializers


class SwaggerUI(TemplateView):
    template_name = 'rest_framework_swagger/index.html'


class SwaggerJSON(APIView):
    def get(self, request):
        contact = serializers.ContactSerializer(data={
            'name': 'Marc Gibbons',
            'url': 'http://marcgibbons.com',
            'email': 'marc_gibbons@rogers.com'
        })
        contact.is_valid(raise_exception=True)

        license = serializers.LicenseSerializer(data={
            'name': 'MIT',
            'url': 'http://google.com'
        })
        license.is_valid(raise_exception=True)

        info = serializers.InfoSerializer(data={
            'title': 'hello',
            'description': '## This is my example',
            'termsOfService': 'your mother',
            'contact': contact.data,
            'license': license.data,
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
