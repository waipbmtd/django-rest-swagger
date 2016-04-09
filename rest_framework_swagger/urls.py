from django.conf.urls import url

from . import views


urlpatterns = [
    url('', views.SwaggerUI.as_view(), name='main'),
]
