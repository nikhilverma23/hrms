from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    'hrms.home.views',
    
    url(r'^$', 'home', name='home')
)
