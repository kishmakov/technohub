import settings
from django.conf.urls import patterns, include, url
from views import welcome
from vle.views import vle
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    ('^$', welcome),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    url(r'^admin/', include(admin.site.urls)),
    ('^vle/$', vle),
)
