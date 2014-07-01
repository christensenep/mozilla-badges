from django.conf.urls.defaults import *

from .views import create, edit_meta, edit_design

urlpatterns = patterns('',
    url(r'^create/?$', create,),
    url(r'^badge/(?P<slug>[^/]+)/edit/?$', edit_meta, name='edit_badge_meta',),
    url(r'^badge/(?P<slug>[^/]+)/edit/design/?$', edit_design, name='edit_badge_design',),
)
