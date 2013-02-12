from django.conf.urls import patterns, include, url
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.generic.simple import redirect_to
from rest_framework.renderers import JSONRenderer

# Enable the admin site
from django.contrib import admin
admin.autodiscover()

# Import the API
from app import api


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders it's content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# define the catch all
def index(request):
    user_json = {}
    if request.user.is_authenticated():
        serialized = api.user.UserSerializer(request.user)
        user_json = serialized.data

    return render_to_response('index.html', {
      'user': request.user,
      'user_json': JSONRenderer().render(user_json)
    })


def auth(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        uname, passwd = request.META['HTTP_AUTHORIZATION'].split(':')
        user = authenticate(username=uname, password=passwd)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.user = user

                # Once we have logged the user in return the serialized response
                serializer = api.user.UserSerializer(request.user)
                return JSONResponse(serializer.data)

    # They did not provide basic authentication
    response = HttpResponse()
    response.status_code = 401
    return response


def vlogout(request):
    logout(request)
    return redirect('/')

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    url(r'^admin/?', include(admin.site.urls)),
    url(r'^favicon.ico$', redirect_to, {'url': '/static/favicon.ico'}),

    url(r'^api', include(api.urls)),

    # log in, log out routes.
    url(r'^auth/?', auth, name='auth'),
    url(r'^logout/?', vlogout, name='logout'),

    # Catch all, for history API routing
    url(r'^.*', index, name='index')
)