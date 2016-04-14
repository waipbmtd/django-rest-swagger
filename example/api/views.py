# coding=utf-8
"""API Views for example application."""
from rest_framework.views import Response, APIView
from rest_framework import viewsets, status
import rest_framework

from rest_framework.generics import ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView

from .models import Cigar, Manufacturer, Country, Jambalaya
from .serializers import CigarSerializer, ManufacturerSerializer, \
    CountrySerializer, JambalayaSerializer, JambalayaQuerySerializer, \
    CigarJambalayaSerializer, JambalayaCigarsSerializer, CigarSerializerMinimal

if rest_framework.VERSION < '3.0.0':
    from rest_framework.decorators import action, link, api_view
else:
    from rest_framework.decorators import detail_route, api_view

    def action():
        return lambda func: detail_route(methods=['post'])(func)

    def link():
        return lambda func: detail_route()(func)


class CigarViewSet(viewsets.ModelViewSet):
    """ Cigar resource. """

    serializer_class = CigarSerializer
    model = Cigar
    queryset = Cigar.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Return a list of objects.
        """
        return super(CigarViewSet, self).list(request, *args, **kwargs)

    @action()
    def set_price(self, request, pk):
        """An example action to on the ViewSet."""
        return Response('20$')

    @link()
    def get_price(self, request, pk):
        """Return the price of a cigar."""
        return Response('20$')


class ArtisanCigarViewSet(viewsets.ModelViewSet):

    """
    Cigar resource.
    ---
    get_price:
        omit_serializer: true
    set_price:
        omit_serializer: true
        parameters_strategy:
            form: replace
        parameters:
            - name: price
              type: number
    """

    serializer_class = CigarSerializer
    model = Cigar
    queryset = Cigar.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Return a list of objects.
        """
        return super(ArtisanCigarViewSet, self).list(request, *args, **kwargs)

    @action()
    def set_price(self, request, pk):
        """An example action to on the ViewSet."""
        return Response('20$')

    @link()
    def get_price(self, request, pk):
        """Return the price of a cigar."""
        return Response('20$')


class ManufacturerList(ListCreateAPIView):
    """
    Get the list of cigar manufacturers from the database.
    Excludes artisan manufacturers.
    """

    model = Manufacturer
    serializer_class = ManufacturerSerializer


class ManufacturerDetails(RetrieveUpdateDestroyAPIView):

    """Return the details on a manufacturer."""

    model = Manufacturer
    serializer_class = ManufacturerSerializer


class CountryList(ListCreateAPIView):

    """Gets a list of countries. Allows the creation of a new country."""

    model = Country
    serializer_class = CountrySerializer


class CountryDetails(RetrieveUpdateDestroyAPIView):

    """Detailed view of the country."""

    model = Country
    serializer_class = CountrySerializer

    def get_serializer_class(self):
        self.serializer_class.context = {'request': self.request}
        return self.serializer_class


class MyCustomView(APIView):

    """
    This is a custom view that can be anything at all.
    It's not using a serializer class, but I can define my own parameters.
    Cet exemple démontre l'utilisation de caractères unicode
    """

    def get(self, *args, **kwargs):
        """
        Get the single object.
        param1 -- my param
        """
        return Response({'foo': 'bar'})

    def post(self, request, *args, **kwargs):
        """
        Post to see your horse's name.
        horse -- the name of your horse
        """
        return Response({'horse': request.GET.get('horse')})
