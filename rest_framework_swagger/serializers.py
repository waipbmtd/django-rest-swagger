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


class BaseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {key: val for key, val in instance.items() if val is not None}


class DictListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        responses = {}
        for response in data:
            obj = self.child.to_representation(response)
            responses.update(obj)

        return responses

    @property
    def data(self):
        return self.to_representation(self.validated_data)


class ContactSerializer(BaseSerializer):
    name = serializers.CharField(allow_blank=True, required=False)
    url = serializers.URLField(allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, required=False)


class LicenseSerializer(BaseSerializer):
    name = serializers.CharField()
    url = serializers.URLField(allow_blank=True, required=False)


class InfoSerializer(BaseSerializer):
    title = serializers.CharField(default='Django REST Swagger')
    description = serializers.CharField(allow_blank=True, required=False)
    termsOfService = serializers.CharField(allow_blank=True, required=False)
    contact = ContactSerializer(allow_null=True, required=False)
    license = LicenseSerializer(allow_null=True, required=False)
    version = serializers.CharField(default='2.0')


class PropertySerializer(BaseSerializer):
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
    default = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    multipleOf = serializers.FloatField(
        required=False,
        allow_null=True
    )
    maximum = serializers.FloatField(
        required=False,
        allow_null=True
    )
    exclusiveMaximum = serializers.FloatField(
        required=False,
        allow_null=True
    )
    minimum = serializers.FloatField(
        required=False,
        allow_null=True
    )
    exclusiveMinimum = serializers.FloatField(
        required=False,
        allow_null=True
    )
    maxLength = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    minLength = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    pattern = serializers.CharField(
        required=False,
        allow_null=True
    )
    maxItems = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    minItems = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    uniqueItems = serializers.BooleanField(
        default=False,
        required=False
    )
    maxProperties = serializers.IntegerField(required=False)
    minProperties = serializers.IntegerField(required=False)
    enum = serializers.ListField(
        required=False,
        allow_null=True,
        child=serializers.CharField(),
    )

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        return {
            instance.pop('name'): instance
        }


class SchemaObjectSerializer(BaseSerializer):
    title = serializers.CharField()
    description = serializers.CharField(
        allow_blank=True,
    )
    type = serializers.ChoiceField(
        default='object',
        choices=TYPES
    )
    properties = serializers.DictField(required=False)


class ReferenceSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['$ref'] = serializers.CharField(allow_blank=True)


class ResponseSerializer(BaseSerializer):
    status_code = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True)
    schema = ReferenceSerializer(allow_null=True, required=False)

    class Meta:
        list_serializer_class = DictListSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {data.pop('status_code'): data}


class ParameterSerializer(BaseSerializer):
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
    schema = ReferenceSerializer(allow_null=True, required=False)
    type = serializers.ChoiceField(choices=TYPES)


class OperationSerializer(BaseSerializer):
    method = serializers.CharField()
    tags = serializers.ListField(required=False, allow_null=True)
    summary = serializers.CharField(max_length=120, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
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
    responses = serializers.DictField()
    schemes = serializers.MultipleChoiceField(
        required=False,
        allow_null=True,
        choices=['http', 'https', 'ws', 'wss']
    )
    deprecated = serializers.BooleanField(default=False)
    # TODO: security object?

    class Meta:
        list_serializer_class = DictListSerializer

    def to_representation(self, obj):
        return {
            obj.pop('method'): obj
        }


class PathItemSerializer(BaseSerializer):
    parameters = ParameterSerializer(
        required=False, many=True, allow_null=True)
    get = OperationSerializer(required=False)


class SchemaSerializer(BaseSerializer):
    swagger = serializers.CharField(default='2.0')
    paths = serializers.DictField()
    info = InfoSerializer()
    definitions = serializers.JSONField(allow_null=True)
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
