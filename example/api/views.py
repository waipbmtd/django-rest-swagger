"""API Views for example application."""
from rest_framework.decorators import detail_route
from rest_framework.generics import ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.views import Response, APIView
from rest_framework import viewsets

from .models import Cigar, Manufacturer, Country
from .serializers import CigarSerializer, ManufacturerSerializer, \
    CountrySerializer


class CigarViewSet(viewsets.ModelViewSet):
    """
    # Cigar resource.


    This is my description


    This is my other description
    """

    serializer_class = CigarSerializer
    model = Cigar
    queryset = Cigar.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Return a list of objects.
        """
        return super(CigarViewSet, self).list(request, *args, **kwargs)

    @detail_route(methods=['post'])
    def set_price(self, request, pk):
        """An example action to on the ViewSet."""
        return Response('20$')

    @detail_route
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

    @detail_route(methods=['post'])
    def set_price(self, request, pk):
        """An example action to on the ViewSet."""
        return Response('20$')

    @detail_route()
    def get_price(self, request, pk):
        """Return the price of a cigar."""
        return Response('20$')


class ManufacturerList(ListCreateAPIView):
    """
    Get the list of cigar manufacturers from the database.
    Excludes artisan manufacturers.
    """
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class ManufacturerDetails(RetrieveUpdateDestroyAPIView):
    """Return the details on a manufacturer."""
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class CountryList(ListCreateAPIView):
    """Gets a list of countries. Allows the creation of a new country."""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CountryDetails(RetrieveUpdateDestroyAPIView):
    """Detailed view of the country."""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


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
