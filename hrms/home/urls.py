from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    'hrms.home.views',
    
    url(r'^$', 'home', name='home'),
    #url(r'^$','edit_company_details',name='edit_company_details'),
    url(r'^registration_update/','registration_update',name='registration_update'),
)
