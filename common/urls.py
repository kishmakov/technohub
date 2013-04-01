from django.conf.urls import patterns
from views import welcome
# from vle.views import fluids

import settings

from django.contrib importx admin
admin.autodiscover()

urlpatterns = patterns('',
   ('^$', welcome),
   # ('^vle/fluids$', fluids),
   (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
