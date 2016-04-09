from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^docs/', include('rest_framework_swagger.urls', namespace='swagger')),
    url(r'^admin/', admin.site.urls),
]
