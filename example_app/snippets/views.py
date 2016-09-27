#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.views import APIView

from django_rest_schemas.coredoc import Field, Link, ScResponse, Tag
from django_rest_schemas.decorators import render_parmeters, render_link, \
    render_responses, rander_tag, render_serializer
from snippets.models import Snippet
from snippets.permissions import IsOwnerOrReadOnly
from snippets.serializers import SnippetSerializer, UserSerializer


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents code snippets.

    The `highlight` field presents a hyperlink to the highlighted HTML
    representation of the code snippet.

    The **owner** of the code snippet may update or delete instances
    of the code snippet.

    Try it yourself by logging in as one of these four users: **amy**, **max**,
    **jose** or **aziz**.  The passwords are the same as the usernames.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @detail_route(renderer_classes=(renderers.StaticHTMLRenderer,))
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the users in the system.

    As you can see, the collection of snippet instances owned by a user are
    serialized using a hyperlinked representation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


@rander_tag(Tag("snippet", '所有SnippetList'))
class SnippetListView(APIView):

    @render_parmeters(
        Field("pk", True, 'path', 'desc pk'),
        Field("test_b", False, 'query', "desc test b"),
        Field("test_c", False, 'query', "desc test c"),
    )
    @render_responses(
        ScResponse(200, "normal response", "schema", UserSerializer),
        ScResponse(403, u"权限不够")
    )
    @render_link(Link(u"这只是一个测试而已", u"测试获取"))
    def get(self, pk, request):
        query_dict = request.query_params.dict().copy()
        print "SnippetListView: get",query_dict
        snippet_list = Snippet.objects.all()
        serializer = SnippetSerializer(snippet_list, many=True)
        return Response(serializer.data)


@rander_tag(Tag("bbc", '单个Snippet'))
class SnippetView(APIView):

    @render_parmeters(
        Field("test_b", False, 'query', "desc test b"),
        Field("test_c", False, 'query', "desc test c"),
    )
    @render_responses(
        ScResponse(200, "normal response", "schema", UserSerializer),
        ScResponse(403, u"权限不够")
    )
    @render_link(Link(u"这只是一个测试而已", u"测试获取"))
    def get(self, request):
        query_dict = request.query_params.dict().copy()
        print "SnippetView: get",query_dict
        snippet_list = Snippet.objects.all()
        serializer = SnippetSerializer(snippet_list, many=True)
        return Response(serializer.data)
