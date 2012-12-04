from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from hrms.settings import MEDIA_ROOT, STATIC_ROOT
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', "home.views.home", name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/',include('home.urls')),
    
      # Static content.
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)
