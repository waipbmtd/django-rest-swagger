from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'cigars', views.CigarViewSet)
router.register(r'artisan_cigars', views.ArtisanCigarViewSet)

urlpatterns = [
    url(r'^custom$', views.MyCustomView.as_view()),
    url(r'^manufacturers/?$', views.ManufacturerList.as_view(), name='list_of_manufacturers'),
    url(r'^manufacturers/(?P<pk>\d+)/?$', views.ManufacturerDetails.as_view(), name='manufacturer_details'),

    url(r'^countries/?$', views.CountryList.as_view(), name='list_of_countries'),
    url(r'^countries/(?P<pk>\d+)/?$', views.CountryDetails.as_view(), name='countries_details'),
]
urlpatterns += router.urls
