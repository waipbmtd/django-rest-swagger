from django.conf.urls import url, include
from rest_framework import renderers, response
from django_rest_schemas import schemas
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

from snippets import views


@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def schema_view(request):
    generator = schemas.CoreApiSchemaGenerator(title='Pastebin API')
    # generator = schemas.SchemaGenerator(title='Pastebin API')
    return response.Response(generator.get_schema())
    # return response.Response(generator.get_schema(request=request))



router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    url('^$', schema_view),
    # url(r'^', include(router.urls)),
    url(r'snippets_list/(?P<pk>[0-9]+)/$', views.SnippetListView.as_view()),
    url(r'snippets/$', views.SnippetView.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
