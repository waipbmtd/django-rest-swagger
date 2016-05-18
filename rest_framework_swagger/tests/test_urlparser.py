import datetime
from importlib import import_module
from unittest.mock import patch

from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth.models import User
from django.test import TestCase
from django.views.generic import View
from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet

from ..urlparser import UrlParser


class MockApiView(APIView):
    """
    A Test View

    This is more commenting
    """
    def get(self, request):
        """
        Get method specific comments
        """
        return Response("mock me maybe")


class NonApiView(View):
    pass


class MockUrlconfModule:
    """ A mock of an `app.urls`-like module. """
    def __init__(self, urlpatterns):
        self.urlpatterns = urlpatterns


class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField(default=datetime.datetime.now)


class UrlParserTest(TestCase):
    def setUp(self):
        self.url_patterns = [
            url(r'a-view/?$', MockApiView.as_view(), name='a test view'),
            url(r'b-view$', MockApiView.as_view(), name='a test view'),
            url(r'c-view/$', MockApiView.as_view(), name='a test view'),
            url(r'a-view/child/?$', MockApiView.as_view()),
            url(r'a-view/child2/?$', MockApiView.as_view()),
            url(r'another-view/?$', MockApiView.as_view(),
                name='another test view'),
            url(r'view-with-param/(:?<ID>\d+)/?$', MockApiView.as_view(),
                name='another test view'),
            url(r'a-view-honky/?$', MockApiView.as_view(), name='a test view'),
        ]

    def test_get_apis(self):
        urlparser = UrlParser()
        urls = import_module(settings.ROOT_URLCONF)
        # Overwrite settings with test patterns
        urls.urlpatterns = self.url_patterns
        apis = urlparser.get_apis()
        self.assertEqual(self.url_patterns[0], apis[0]['pattern'])
        self.assertEqual('/a-view/', apis[0]['path'])
        self.assertEqual(self.url_patterns[1], apis[1]['pattern'])
        self.assertEqual('/b-view', apis[1]['path'])
        self.assertEqual(self.url_patterns[2], apis[2]['pattern'])
        self.assertEqual('/c-view/', apis[2]['path'])
        self.assertEqual(self.url_patterns[3], apis[3]['pattern'])
        self.assertEqual('/a-view/child/', apis[3]['path'])
        self.assertEqual(self.url_patterns[4], apis[4]['pattern'])
        self.assertEqual('/a-view/child2/', apis[4]['path'])
        self.assertEqual(self.url_patterns[5], apis[5]['pattern'])
        self.assertEqual('/another-view/', apis[5]['path'])
        self.assertEqual(self.url_patterns[6], apis[6]['pattern'])
        self.assertEqual('/view-with-param/{var}/', apis[6]['path'])
        self.assertEqual(self.url_patterns[7], apis[7]['pattern'])
        self.assertEqual('/a-view-honky/', apis[7]['path'])

    def test_get_apis_urlconf_import(self):
        urlparser = UrlParser()
        urlconf = MockUrlconfModule(self.url_patterns)
        with patch.dict('sys.modules', {'mock_urls': urlconf}):
            apis = urlparser.get_apis(urlconf='mock_urls')
            for api in apis:
                self.assertIn(api['pattern'], self.url_patterns)

    def test_get_apis_urlconf_module(self):
        urlparser = UrlParser()
        urlconf = MockUrlconfModule(self.url_patterns)
        apis = urlparser.get_apis(urlconf=urlconf)
        for api in apis:
            self.assertIn(api['pattern'], self.url_patterns)

    def test_flatten_url_tree(self):
        urlparser = UrlParser()
        apis = urlparser.get_apis(self.url_patterns)

        self.assertEqual(len(self.url_patterns), len(apis))

    def test_flatten_url_tree_url_import(self):
        urls = [url(r'api/base/path/', include(self.url_patterns))]
        urlparser = UrlParser()
        apis = urlparser.get_apis(urls)

        self.assertEqual(len(self.url_patterns), len(apis))

    def test_resources_starting_with_letters_from_base_path(self):
        base_path = r'api/'
        url_patterns = [
            url(r'test', MockApiView.as_view(), name='a test view'),
            url(r'pai_test', MockApiView.as_view(),
                name='start with letters a, p, i'),
        ]
        urls = [url(base_path, include(url_patterns))]
        urlparser = UrlParser()
        apis = urlparser.get_apis(urls)
        resources = urlparser.get_top_level_apis(apis)
        self.assertEqual(set(resources),
                         set([base_path + url_pattern.regex.pattern
                              for url_pattern in url_patterns]))

    def test_flatten_url_tree_with_filter(self):
        urlparser = UrlParser()
        apis = urlparser.get_apis(self.url_patterns, filter_path="a-view")

        paths = [api['path'] for api in apis]

        self.assertIn("/a-view/", paths)
        self.assertIn("/a-view/child/", paths)
        self.assertIn("/a-view/child2/", paths)
        self.assertNotIn("/a-view-honky/", paths)

        self.assertEqual(3, len(apis))

    def test_filter_custom(self):
        urlparser = UrlParser()
        apis = [{'path': '/api/custom'}]
        apis2 = urlparser.get_filtered_apis(apis, 'api/custom')
        self.assertEqual(apis, apis2)

    def test_flatten_url_tree_excluded_namesapce(self):
        urls = [
            url(r'api/base/path/',
                include(self.url_patterns, namespace='exclude'))
        ]
        urlparser = UrlParser()
        apis = urlparser.__flatten_patterns_tree__(
            patterns=urls, exclude_namespaces='exclude')

        self.assertEqual([], apis)

    def test_flatten_url_tree_url_import_with_routers(self):

        class MockApiViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            model = User
            queryset = User.objects.all()

        router = DefaultRouter()
        router.register(r'other_views', MockApiViewSet)
        router.register(r'more_views', MockApiViewSet)

        urls_app = [url(r'^', include(router.urls))]
        urls = [
            url(r'api/', include(urls_app)),
            url(r'test/', include(urls_app))
        ]
        urlparser = UrlParser()
        apis = urlparser.get_apis(urls)

        self.assertEqual(
            4, sum(api['path'].find('api') != -1 for api in apis))
        self.assertEqual(
            4, sum(api['path'].find('test') != -1 for api in apis))

    def test_get_api_callback(self):
        urlparser = UrlParser()
        callback = urlparser.__get_pattern_api_callback__(self.url_patterns[0])

        self.assertTrue(issubclass(callback, MockApiView))

    def test_get_api_callback_not_rest_view(self):
        urlparser = UrlParser()
        non_api = [
            url(r'something', NonApiView.as_view())
        ]
        callback = urlparser.__get_pattern_api_callback__(non_api)

        self.assertIsNone(callback)

    def test_get_top_level_api(self):
        urlparser = UrlParser()
        apis = urlparser.get_top_level_apis(
            urlparser.get_apis(self.url_patterns))

        self.assertIn("a-view", apis)
        self.assertIn("b-view", apis)
        self.assertIn("c-view", apis)
        self.assertIn("another-view", apis)
        self.assertIn("view-with-param", apis)
        self.assertNotIn("a-view/child", apis)
        self.assertNotIn("a-view/child2", apis)

    def test_assemble_endpoint_data(self):
        """
        Tests that the endpoint data is correctly packaged
        """
        urlparser = UrlParser()
        pattern = self.url_patterns[0]

        data = urlparser.__assemble_endpoint_data__(pattern)

        self.assertEqual(data['path'], '/a-view/')
        self.assertEqual(data['callback'], MockApiView)
        self.assertEqual(data['pattern'], pattern)

    def test_assemble_data_with_non_api_callback(self):
        bad_pattern = [url(r'^some_view/', NonApiView.as_view())]

        urlparser = UrlParser()
        data = urlparser.__assemble_endpoint_data__(bad_pattern)

        self.assertIsNone(data)

    def test_exclude_router_api_root(self):
        class MyViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            queryset = User.objects.all()
            model = User

        router = DefaultRouter()
        router.register('test', MyViewSet)

        urls_created = len(router.urls)

        parser = UrlParser()
        apis = parser.get_apis(router.urls)

        self.assertEqual(4, urls_created - len(apis))

    def test_get_base_path_for_common_endpoints(self):
        parser = UrlParser()
        paths = ['api/endpoint1', 'api/endpoint2']
        base_path = parser.__get_base_path__(paths)

        self.assertEqual('api/', base_path)

    def test_get_base_path_for_root_level_endpoints(self):
        parser = UrlParser()
        paths = ['endpoint1', 'endpoint2', 'endpoint3']
        base_path = parser.__get_base_path__(paths)

        self.assertEqual('', base_path)


class NestedUrlParserTest(TestCase):
    def setUp(self):
        class FuzzyApiView(APIView):
            def get(self, request):
                pass

        class ShinyApiView(APIView):
            def get(self, request):
                pass

        api_fuzzy_url_patterns = [
            url(r'^item/$', FuzzyApiView.as_view(), name='find_me')
        ]
        api_shiny_url_patterns = [
            url(r'^item/$', ShinyApiView.as_view(), name='hide_me')
        ]

        fuzzy_app_urls = [
            url(r'^api/', include(api_fuzzy_url_patterns,
                                  namespace='api_fuzzy_app'))
        ]
        shiny_app_urls = [
            url(r'^api/', include(api_shiny_url_patterns,
                                  namespace='api_shiny_app'))
        ]

        self.project_urls = [
            url('my_fuzzy_app/', include(fuzzy_app_urls)),
            url('my_shiny_app/', include(shiny_app_urls)),
        ]

    def test_exclude_nested_urls(self):

        url_parser = UrlParser()
        # Overwrite settings with test patterns
        urlpatterns = self.project_urls
        apis = url_parser.get_apis(urlpatterns,
                                   exclude_namespaces=['api_shiny_app'])
        self.assertEqual(len(apis), 1)
        self.assertEqual(apis[0]['pattern'].name, 'find_me')
