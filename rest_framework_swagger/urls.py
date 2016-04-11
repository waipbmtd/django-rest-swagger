from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.SwaggerUI.as_view(), name='main'),
    url(r'swagger.json', views.SwaggerJSON.as_view(), name='json')
]
