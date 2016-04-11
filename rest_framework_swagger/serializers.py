from rest_framework import serializers

TYPES = [
    'array',
    'boolean',
    'integer',
    'number',
    'null',
    'object',
    'string'
]


FORMATS = [
    'int32',
    'int64',
    'float',
    'double',
    'byte',
    'binary',
    'date',
    'date-time',
    'password',
    'email',
    'hostname',
    'ipv4',
    'ipv6',
    'uri'
]


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True, required=False)
    url = serializers.URLField(allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, required=False)


class LicenseSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.URLField(allow_blank=True, required=False)


class InfoSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    termsOfService = serializers.CharField(allow_blank=True, required=False)
    contact = ContactSerializer(required=False)
    license = LicenseSerializer(required=False)
    version = serializers.CharField(allow_blank=True, required=False)


class PropertySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(
        allow_blank=True,
        required=False,
        allow_null=True,
    )
    format = serializers.ChoiceField(
        required=False,
        choices=FORMATS
    )
    type = serializers.ChoiceField(
        default='object',
        choices=TYPES
    )
    default = serializers.CharField(allow_blank=True, required=False)
    multipleOf = serializers.FloatField(required=False)
    maximum = serializers.FloatField(required=False)
    exclusiveMaximum = serializers.FloatField(required=False)
    minimum = serializers.FloatField(required=False)
    exclusiveMinimum = serializers.FloatField(required=False)
    maxLength = serializers.IntegerField(required=False)
    minLength = serializers.IntegerField(required=False)
    pattern = serializers.CharField(required=False)
    maxItems = serializers.IntegerField(required=False)
    minItems = serializers.IntegerField(required=False)
    uniqueItems = serializers.BooleanField(default=False, required=False)
    maxProperties = serializers.IntegerField(required=False)
    minProperties = serializers.IntegerField(required=False)
    enum = serializers.ListField(
        required=False,
        child=serializers.CharField(),
    )

    def to_representation(self, obj):
        return {
            obj.pop('name'): obj
        }


class SchemaObjectSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False
    )
    type = serializers.ChoiceField(
        default='object',
        choices=TYPES
    )
    properties = serializers.JSONField(required=False)


class ResponseSerializer(serializers.Serializer):
    status_code = serializers.IntegerField()
    description = serializers.CharField()
    schema = SchemaObjectSerializer(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {data.pop('status_code'): data}


class ParameterSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['in'] = serializers.ChoiceField(choices=[
            'query',
            'header',
            'path',
            'formData',
            'body'
        ])
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    required = serializers.BooleanField(default=False)


class OperationSerializer(serializers.Serializer):
    tags = serializers.ListField(required=False, allow_null=True)
    summary = serializers.CharField(max_length=120, required=False)
    description = serializers.CharField(required=False)
    operationId = serializers.CharField(required=False)
    consumes = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    produces = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    parameters = ParameterSerializer(
        many=True, required=False, allow_null=True)
    responses = serializers.JSONField()
    schemes = serializers.MultipleChoiceField(
        required=False,
        allow_null=True,
        choices=['http', 'https', 'ws', 'wss']
    )
    deprecated = serializers.BooleanField(default=False)
    # TODO: security?


class PathItemSerializer(serializers.Serializer):
    parameters = ParameterSerializer(
        required=False, many=True, allow_null=True)
    get = OperationSerializer(required=False)


class SchemaSerializer(serializers.Serializer):
    swagger = serializers.CharField(default='2.0')
    info = InfoSerializer()
    host = serializers.CharField(allow_blank=True, required=False)
    basePath = serializers.CharField(allow_blank=True, required=False)
    schemes = serializers.MultipleChoiceField(
        required=False,
        allow_null=True,
        choices=['http', 'https', 'ws', 'wss']
    )
    consumes = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    produces = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
