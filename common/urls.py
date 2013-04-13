import settings
from django.conf.urls import patterns, include, url
from common.views import welcome
from django.contrib import admin
from vle.application import vle_urls


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', welcome),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += vle_urls()