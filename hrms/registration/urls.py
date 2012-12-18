from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    'hrms.registration.views',
    
    
    url(r'^registration_confirmation/','registration_confirmation',name='registration-confirmation'),
    url(r'^registration_failure/','registration_failure',name='registration-failure'),
    url(r'^verify_registration/','verify_registration',name='registration-verify'),
    url(r'^department/' ,'create_department',name="create-department"),
    url(r'^employee/' ,'create_employee',name="create-employee"),
    url(r'^summary/$' ,'summary',name="summary"),
    url(r'^password_reset/$', 'password_reset',name='password_reset'),
    url(r'^supervisor_detail/$', 'supervisor_detail',name='supervisor_detail'),
    url(r'^employee_leave/$', 'employee_leave',name='employee_leave'),
    url(r'^export_company_data/$', 'export_company_data',name='export_company_data'),
    url(r'^leave_detail/$', 'leave_detail',name='leave_detail'),
    url(r'^leave_approval/$', 'leave_approval',name='leave_approval'),
    url(r'^employee_profile/$', 'employee_profile',name='employee_profile'),
    url(r'^employee_homepage/$', 'employee_homepage',name='employee_homepage'),
    url(r'^supervisor_profile/$', 'supervisor_profile',name='supervisor_profile'),
    url(r'^supervisor_leave/$', 'supervisor_leave',name='supervisor_leave'),
    url(r'^update_department/$', 'update_department',name='update_department'),
    url(r'^leads_to_delete_page/$', 'leads_to_delete_page',name='leads_to_delete_page'),
    url(r'^delete_department/$', 'delete_department',name='delete_department'),
    url(r'^update_employee/$', 'update_employee',name='update_employee'),
    url(r'^leads_to_delete_employeepage/$', 'leads_to_delete_employeepage',name='leads_to_delete_employeepage'),
    url(r'^delete_employee/$', 'delete_employee',name='delete_employee'),
    url(r'^create_type_of_leave/$', 'create_type_of_leave',name='create_type_of_leave'),
    url(r'^update_leavetype/$', 'update_leavetype',name='update_leavetype'),
    url(r'^delete_leavetype/$', 'delete_leavetype',name='delete_leavetype')
    
)
