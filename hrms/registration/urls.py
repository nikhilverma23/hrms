from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    'hrms.registration.views',
    
    
    url(r'^registration_confirmation/','registration_confirmation',name='registration-confirmation'),
    url(r'^registration_failure/','registration_failure',name='registration-failure'),
    url(r'^verify_registration/','verify_registration',name='registration-verify'),
    url(r'^department/' ,'create_department',name="create-department"),
    url(r'^employee/' ,'create_employee',name="create-employee"),
    
)
