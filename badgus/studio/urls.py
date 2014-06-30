from django.conf.urls.defaults import *

from .views import create

urlpatterns = patterns('',
    url(r'^create/?$', create,),
)
