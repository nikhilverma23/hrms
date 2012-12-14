#python imports
import os
import uuid
import datetime
import json
from datetime import timedelta
import sys, traceback
import random, string
import hashlib
import csv

#django imports
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import load_backend, login, logout
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.core.mail import send_mail
from django.template import RequestContext, loader, Context

#HRMS imports
from hrms.home.forms import LoginForm
from hrms.registration.forms import DepartmentForm, EmployeeForm,\
PasswordForm ,LeaveForm ,UserProfileForm, LeaveTypeForm
from hrms.registration.models import Department, UserProfile,\
Company, Leave, LeaveType
from hrms.settings import BASE_URL


#------------------------------------------------------------------------------
def registration_confirmation(request):
    try:
        email = request.GET.get('email')
    except:
        email = ''
    return render_to_response('registration/registration_confirmation.html',
                              {'email' : email})

#------------------------------------------------------------------------------
def registration_failure(request):
    return render_to_response('registration/registration_failure.html')
#------------------------------------------------------------------------------
def verification_error(request):
    try:
        reason = request.GET.get('reason')
    except:
        reason = 'Invalid Key'
    return render_to_response('registration/verification_error.html',
                              {'reason' : reason})
#------------------------------------------------------------------------------
def verify_registration(request):
    verified = False
    reason = 'Invalid Key'
    try:
        key = request.GET.get('key')
        username = request.GET.get('username')
        user = User.objects.get(username=username)
        user_key = user.profile.key
        key_validity = int(user.profile.key_expires.strftime('%f'))
        now = int(datetime.datetime.now().strftime('%f'))
        if not user.profile.key == key:
            verified = False
            reason = 'Unknown Key'
        if not key_validity > now:
            user.profile.delete()
            user.delete()
            verified = False
            reason = 'Key Expired'
        verified = True
    except Exception as e:
        verified = False
    if not verified:
        return HttpResponseRedirect('/registration/verification_error?reason=%s' % reason)
    else:
        user.is_locked = False
        user.save()
        user.profile.key = uuid.uuid4().__str__()
        user.profile.save()
        login_user(request, user)
        user.save()
        return HttpResponseRedirect('/registration/department/')
#------------------------------------------------------------------------------
def login_user(request, user):
    """
    Log in a user without requiring credentials (using ``login`` from
    ``django.contrib.auth``, first finding a matching backend).

    """
    from django.contrib.auth import load_backend, login
    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        return login(request, user)
    
#------------------------------------------------------------------------------
def register_user(data):
    """
    This method is used to register a new user and create a user profile.
    """
    password = hashlib.sha1(data['confirm_password']).hexdigest()
    new_user = User(username=data['email'], email=data['email'], 
                    is_staff=True
                    )
    new_user.set_password(data['confirm_password'])
    new_user.save()
    
    new_user.first_name = data['title']
    new_user.email = data['email']
    new_user.is_locked = True
    new_user.save()
    #saving into User Profile Table
    new_profile = new_user.profile
    profile = new_user.profile
    key = uuid.uuid4().__str__()
    profile.key = key
    profile.is_supervisor = True
    profile.save()
    if new_user and profile:
        return new_user
    else:
        return False
    
#-------------------------------------------------------------------------------
def login(request):
    """
    Login Form
    """
    login_form = LoginForm()
    return render_to_response('registration/login.html',
                              {'login_form' : login_form},
                              context_instance = RequestContext(request)
                              )

#-------------------------------------------------------------------------------
def logout_view(request):
    """
    Logout from browser
    """
    logout(request)
    return HttpResponseRedirect('/')
#-------------------------------------------------------------------------------
def login_error(request):
    """
    In case some verification failed
    """
    return HttpResponseRedirect('registration/login_error.html')
#-------------------------------------------------------------------------------
def create_department(request):
    """
    Adding Department
    """
    userprofile_obj = UserProfile.objects.get(user=request.user)
    if request.method =="POST":
        department_form = DepartmentForm(request.POST)
        if department_form.is_valid():
            cd = department_form.cleaned_data
            print "department form is invalid"
        else:
            department_counter = 0
            
            department_name_list = request.POST.getlist('name[]')
            supervisor_first_name_list = request.POST.getlist('supervisor_first_name[]')
            supervisor_last_name_list = request.POST.getlist('supervisor_last_name[]')
            supervisor_email_list = request.POST.getlist('supervisor_email[]')
            for department_name in request.POST.getlist('name[]'):
                # generating random username
                N = 8
                random_username = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
                random_username =  str(random_username)
                # generating random password
                chars = string.ascii_letters + string.digits + '!@#$%^&*()'
                random.seed = (os.urandom(1024))
                random_password = ''.join(random.choice(chars) for i in range(N))
                random_password = str(random_password)
                #Saving supervisor as a user
                user_obj = User(
                            username = random_username,
                            first_name = supervisor_first_name_list[department_counter],
                            last_name = supervisor_last_name_list[department_counter],
                            email = supervisor_email_list[department_counter],
                            )
                user_obj.set_password(random_password)
                user_obj.save()
                
                # Taking out the companydetails for filling
                # department object
                company_obj = Company.objects.get(email=request.user.username)
                department_obj = Department.objects.get_or_create(
                                    name=department_name_list[department_counter],
                                    company = company_obj,
                                    supervisor= user_obj
                                )
                #saving in UserProfile object
                new_profile = user_obj.profile
                profile = user_obj.profile
                key = uuid.uuid4().__str__()
                profile.key = key
                profile.first_name = user_obj.first_name
                profile.last_name = user_obj.last_name
                profile.email = user_obj.email
                profile.is_supervisor = True
                profile.save()
               
                # Now Send them the email
                subject = "Supervisor of %s department" % department_obj[0].name
                 # Send them an email.
                t = loader.get_template('registration/new_department.txt')
                full_name = user_obj.first_name + " " + user_obj.last_name
                c = Context({
                    'id':user_obj.id,
                    'department_name':department_obj[0].name,
                    'name':full_name,
                    'username':user_obj.username,
                    'password':random_password,
                    'base_url':BASE_URL,
                })
                msg = t.render(c)
                send_mail(
                    subject,
                    msg,
                    'HRMS <noreply@hrms.com>',
                    [supervisor_email_list[department_counter]],
                    fail_silently=True
                )
                department_counter += 1
            # Making sure that all department are from the current logged
            # in company and then using userprofile object adding these
            #departments so that we can edit the department form.
            #I was not able to find  any other way . 
            get_department_obj = Department.objects.filter(company=company_obj)
            for department in get_department_obj:
                userprofile_obj.department.add(department)
            # redirecting it to employee form
            return HttpResponseRedirect('/registration/employee/')
            
    else:
        department_form = DepartmentForm()
        
    
    return render_to_response('registration/create_department.html',
                              {'request':request,
                               'department_form':department_form,
                               'active':'department',
                               'userprofile_obj':userprofile_obj
                               },
                              context_instance = RequestContext(request)
                              )
#---------------------------Create Department End-----------------------

#--------------------------- Update Department Starts-------------------------

def update_department(request):
    """
    updates the selected department.
    """
    
    if request.method == "GET":
        if request.GET['id']:
            id = request.GET['id']
            department_obj = Department.objects.get(id=id)
            department_form = DepartmentForm()
            department_form.fields['name'].initial = department_obj.supervisor.username
            department_form.fields['supervisor_first_name'].initial = department_obj.supervisor.first_name
            department_form.fields['supervisor_last_name'].initial = department_obj.supervisor.last_name
            department_form.fields['supervisor_email'].initial = department_obj.supervisor.email
    else:
        # It will be a POST
        department_form = DepartmentForm(request.POST)
        if department_form.is_valid():
            cd = department_form.cleaned_data
            department_obj = Department.objects.get(id=request.GET['id'])
            department_obj.name = cd['name']
            department_obj.save()
            user_id = department_obj.supervisor.id
            user_obj =  User.objects.get(id=user_id)
            user_obj.email = cd['supervisor_email']
            user_obj.first_name = cd['supervisor_first_name']
            user_obj.last_name = cd['supervisor_last_name']
            user_obj.save()
            return HttpResponseRedirect('/registration/department/')
        
    return render_to_response('registration/update_department.html',
                              {'request':request,
                               'department_form':department_form,
                               'active':'department',
                               },
                              context_instance = RequestContext(request)
                              )
#--------------------------- Company updates Department -------------------------

#------------------------Company decides to delete department-----------------------
def leads_to_delete_page(request):
    """
    leads to delete confirmation page for department
    """
    department_id = request.GET.get('id')
    department_obj = Department.objects.get(id=department_id)
    return render_to_response('registration/delete_department.html',
                              {'request':request,
                               'department_obj':department_obj,
                               'active':'department',
                               },
                              context_instance = RequestContext(request)
                              )
#------------------------Company decides to delete department-----------------------    

def delete_department(request):
    """
    allows the company to delete the department
    """
    id = request.GET.get('id')
    department_obj = Department.objects.get(id=id)
    department_obj.delete()
    
    return HttpResponseRedirect('/registration/department/')

#------------------------Company has deleted the  department--------------------

#--------------------------- Company creating employee -------------------------  
def create_employee(request):
    """
    Adding employees
    """
    if request.method == "POST":
        employee_form = EmployeeForm(request.POST)
        
        if employee_form.is_valid():
            cd = employee_form.cleaned_data
            print "Employee Form is invalid"
        else:
            employment_counter = 0
            first_name_list = request.POST.getlist('first_name[]')
            last_name_list = request.POST.getlist('last_name[]')
            employee_email_list = request.POST.getlist('employee_email[]')
            employee_department_list = request.POST.getlist('employee_department[]')
            for employee_name in request.POST.getlist('first_name[]'):
                # generating random username because user will login
                # and go to change password page.
                N = 8
                random_username = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
                random_username =  str(random_username)
                # generating random password because user will login
                # and go to change password
                chars = string.ascii_letters + string.digits + '!@#$%^&*()'
                random.seed = (os.urandom(1024))
                random_password = ''.join(random.choice(chars) for i in range(N))
                random_password = str(random_password)
                # Adding in User Table
                user_obj =  User(
                                username = random_username,
                                first_name = first_name_list[employment_counter],
                                last_name = last_name_list[employment_counter],
                                email = employee_email_list[employment_counter],
                            )
                user_obj.set_password(random_password)
                user_obj.save()
                #saving in UserProfile object to make sure
                #department gets saved there !
                new_profile = user_obj.profile
                profile = user_obj.profile
                profile.department.add(employee_department_list[employment_counter])
                profile.save()
                
                #Adding into department 
                
                department_obj = Department.objects.get(id=employee_department_list[employment_counter])
                department_obj.employee.add(user_obj.id)
                    
                # Send them an email.
                t = loader.get_template('registration/new_employee.txt')
                full_name = user_obj.first_name + " " + user_obj.last_name
                c = Context({
                    'id':user_obj.id,
                    'department_name':department_obj.name,
                    'name':full_name,
                    'username':user_obj.username,
                    'password':random_password,
                    'base_url':BASE_URL,
                })
                msg = t.render(c)
                subject = "Employer of %s department" % department_obj.name
                send_mail(
                    subject,
                    msg,
                    'HRMS <noreplyhr@hrms.com>',
                    [employee_email_list[employment_counter]],
                    fail_silently=True
                )
                
                employment_counter += 1    
            return HttpResponseRedirect('/registration/summary/?active=leave_requests')
        
            
    else:
        
        employee_form = EmployeeForm()
        company_obj = Company.objects.get(email=request.user.username)
        # Listing the department created by the company itself
        department = company_obj.department_set.all()
            
    return render_to_response('registration/create_employee.html',
                              {'request':request,
                               'department':department,
                               'employee_form':employee_form,
                               'active':'employee'
                               },
                              context_instance = RequestContext(request)
                            )
#-------------------------Company has created Employee------------------

#---------------Company's can update their employees -------------------
def update_employee(request):
    """
    updates the selected employee.
    """
    id = request.GET.get('id')
    if request.method == "GET":
        
        user_obj = User.objects.get(id=id)
        userprofile_obj = UserProfile.objects.get(user=user_obj)
        employee_form = EmployeeForm()
        employee_form.fields['department'].initial = userprofile_obj.department
        employee_form.fields['first_name'].initial = user_obj.first_name
        employee_form.fields['last_name'].initial = user_obj.last_name
        employee_form.fields['employee_email'].initial = user_obj.email
    else:
        # It will be a POST
        employee_form = EmployeeForm(request.POST)
        if employee_form.is_valid():
            user_obj = User.objects.get(id=id)
            userprofile_obj = UserProfile.objects.get(user=user_obj)
            cd = employee_form.cleaned_data
            user_obj.first_name = cd['first_name']
            user_obj.last_name = cd['last_name']
            user_obj.email = cd['employee_email']
            user_obj.save()
            
            userprofile_obj.first_name = cd['first_name']
            userprofile_obj.last_name = cd['last_name']
            userprofile_obj.email = cd['employee_email']
            userprofile_obj.save()
            userprofile_obj.department.add(cd['department'])
            return HttpResponseRedirect('/registration/employee/')
        
    return render_to_response('registration/update_employee.html',
                              {'request':request,
                               'employee_form':employee_form,
                               'active':'employee',
                               },
                              context_instance = RequestContext(request)
    
                            )
#---------------Company's has updated their employees ------------------

#---------------Company is confirming to delete the employee------------
def leads_to_delete_employeepage(request):
    """
    leads to delete confirmation page for department
    """
    id = request.GET.get('id')
    user_obj = User.objects.get(id=id)
    return render_to_response('registration/delete_employee.html',
                              {'request':request,
                               'user_obj':user_obj,
                               'active':'employee',
                               },
                              context_instance = RequestContext(request)
                              )
#---------------Company is confirming to delete the employee------------

#---------------Company is confirming to delete the employee------------
def delete_employee(request):
    """
    allows the company to delete the department
    """
    id = request.GET.get('id')
    user_obj = User.objects.get(id=id)
    user_obj.delete()
    
    return HttpResponseRedirect('/registration/employee/')
#---------------Company is confirming to delete the employee------------

#---------------Company is creating type of leave-------------
from django.forms.formsets import formset_factory


def create_type_of_leave(request):
    if request.method == "POST":
        type_of_leave_form = LeaveTypeForm(request.POST)
        if type_of_leave_form.is_valid():
            cd = type_of_leave_form.cleaned_data
            type_of_leave = LeaveType.objects.get_or_create(
                            type_of_leave = cd['type_of_leave']    
                            )
        else:
            print "LeaveTypeForm is invalid"
    else:
        type_of_leave_form = LeaveTypeForm()
    return render_to_response('registration/company_leave_summary.html',
                                    {'request':request,
                                    #'company_obj':company_obj,
                                    #'department_obj':department_obj,
                                    #'leave_obj':leave_obj,
                                    'base_url':BASE_URL,
                                    'active':'leave_requests'
                                    },
                                    context_instance = RequestContext(request)
                                  )

#---------------Company has created type of leaves------------


#---------------Company's Summary of department and employees-----------
def summary(request):
    """
    This will tell the complete summary in a Table
    """
    leave_user = []
    company_obj = Company.objects.get(email=request.user)
    department_obj = Department.objects.filter(company=company_obj)
    for department in department_obj:
        all_emp = department.employee.all()
        supervisor = department.supervisor
        for emp in all_emp:
            leave_user.append(emp)
        leave_user.append(supervisor)
    leave_obj = Leave.objects.filter(supervisor=request.user,status=False)
    if request.GET.get('active') == "summary":
        # calling the summary page
        return render_to_response('registration/summary.html',
                                    {'request':request,
                                    'company_obj':company_obj,
                                    'department_obj':department_obj,
                                    'leave_obj':leave_obj,
                                    'base_url':BASE_URL,
                                    'active':'summary'
                                    },
                                    context_instance = RequestContext(request)
                                  )
    elif request.GET.get('active') == "leave_requests":
        # Here we can see all the leaves
        if request.method == "POST":
            type_of_leave_form = LeaveTypeForm(request.POST)
            if type_of_leave_form.is_valid():
                cd = type_of_leave_form.cleaned_data
                type_of_leave = LeaveType.objects.get_or_create(
                                type_of_leave = cd['type_of_leave']    
                                )
            else:
                print "LeaveTypeForm is invalid"
        else:
            type_of_leave_form = LeaveTypeForm()
            try:
                type_of_leave_obj = LeaveType.objects.get(id=id)
                type_of_leave_form.fields['type_of_leave'].initial = type_of_leave_obj.type_of_leave
            except:
                pass
        return render_to_response('registration/company_leave_summary.html',
                                    {'request':request,
                                    'company_obj':company_obj,
                                    'department_obj':department_obj,
                                    'type_of_leave_form':type_of_leave_form,
                                    'leave_obj':leave_obj,
                                    'base_url':BASE_URL,
                                    'active':'leave_requests',
                                    },
                                    context_instance = RequestContext(request)
                                  )
    elif request.GET.get('active') == 'export':
        # Here we can see the summary and go to export button
        return render_to_response('registration/summary.html',
                                    {'request':request,
                                    'company_obj':company_obj,
                                    'department_obj':department_obj,
                                    'leave_obj':leave_obj,
                                    'base_url':BASE_URL,
                                    'active':'export'
                                    },
                                    context_instance = RequestContext(request)
                                  )
        
        
#---------------Company's Summary of department and employees------------


#--------------------Company's data in csv file--------------------------
def export_company_data(request):
    company_obj = Company.objects.get(email=request.user)
    department_obj = Department.objects.filter(company=company_obj)
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=\
    %s-%s.csv' % ( company_obj.name, datetime.datetime.now().date())
    writer = csv.writer(response)
    row_header_values = [
                        'Company Name',
                        'Department Name',
                        'Supervisor',
                        'Employee',
                        ]
    # Output the headers first
    writer.writerow(row_header_values)
    
    for department_details in department_obj:
        
        row_data =  [
                        company_obj.name,
                        department_details.name,
                        department_details.supervisor.username,
                        [employee.username for employee in department_details.employee.all()]
                        
                    ]
    # preparing the export    
    export_dict = dict(zip(row_header_values,row_data))
    # Matching the values with headers
    final_row_data = [export_dict[key] for key in row_header_values]     
    writer.writerow(final_row_data)
    return response
#--------------------Company's data in csv file------------------------------

#---------------------Company Section Ends-----------------------------------


#---------------------Supervisor section-------------------------------------
def supervisor_detail(request):
    """
    Describe the detail of leaves to employees.
    """

    employee_list = []
    if request.GET.get('id'):
        user_obj = User.objects.get(id=request.GET['id'])
        department_obj = Department.objects.filter(supervisor=user_obj)
        
    else:
        department_obj = Department.objects.filter(supervisor=request.user)
    for d_obj in department_obj:
        employee_obj_list  = d_obj.employee.all()
    if employee_obj_list:
        for employee_name in employee_obj_list:
            leave_obj = Leave.objects.filter(user=employee_name,status=False)
    else:
        leave_obj = ""
        
    return render_to_response(
                                'registration/supervisor_detail.html',
                                {
                                    'request':request,'base_url':BASE_URL,
                                    'leave_obj':leave_obj
                                },
                                
                                context_instance = RequestContext(request)
                                )
#---------------------------------------------------------------------------
def supervisor_profile(request):
    """
    Leads to edit and update the supervisor profile.
    """
    
    department_obj = Department.objects.get(supervisor=request.user)
    if request.method == "POST":
        
        userprofile_form = UserProfileForm(request.POST)
        if userprofile_form.is_valid():
            cd = userprofile_form.cleaned_data
            userprofile_obj = UserProfile.objects.get(user=request.user)
            userprofile_obj.first_name = cd['first_name']
            userprofile_obj.last_name = cd['last_name']
            userprofile_obj.email = cd['email']
            userprofile_obj.street1 = cd['street1']
            userprofile_obj.street2 = cd['street2']
            userprofile_obj.zip_code = cd['post_code']
            userprofile_obj.country = cd['country']
            userprofile_obj.company = department_obj.company
            userprofile_obj.save()
            user_obj = User.objects.get(id=request.user.id)
            user_obj.first_name = userprofile_obj.first_name
            user_obj.last_name = userprofile_obj.last_name
            user_obj.email = userprofile_obj.email 
            return HttpResponseRedirect('/registration/supervisor_leave/')
        else:
            print "UserProfileForm is invalid"
    else:
        userprofile_form = UserProfileForm()
        try:
            userprofile_obj = UserProfile.objects.get(user=request.user)
            userprofile_form.fields['first_name'].initial = userprofile_obj.first_name
            userprofile_form.fields['last_name'].initial = userprofile_obj.last_name
            userprofile_form.fields['email'].initial = userprofile_obj.email
            userprofile_form.fields['street1'].initial = userprofile_obj.street1
            userprofile_form.fields['street2'].initial = userprofile_obj.street2
            userprofile_form.fields['post_code'].initial = userprofile_obj.zip_code
            userprofile_form.fields['country'].initial = userprofile_obj.country
            
        except:
            pass
    return render_to_response(
                                'registration/supervisor_profile.html',
                                {
                                    'request':request,
                                    'department_obj':department_obj,
                                    'userprofile_form':userprofile_form
                                 },
                                context_instance = RequestContext(request)
                               ) 
#---------------------------------------------------------------------------
def supervisor_leave(request):
    """
    Supervisor is applying leave and this will directly
    go to company owner email who created the department.
    """

    if request.method == "POST":
        leave_form = LeaveForm(request.POST)
        if leave_form.is_valid():
            cd = leave_form.cleaned_data
            # Picking all department of user
            userprofile_obj = UserProfile.objects.get(user=request.user)
            department_list = userprofile_obj.department.all()
            supervisor = User.objects.get(id=cd['supervisor'])
            leave_obj = Leave(
                        type_of_leave = cd['type_of_leave'],
                        start_date = cd['start_date'],
                        end_date = cd['end_date'],
                        user = request.user,
                        reason = cd['reason'],
                        supervisor=supervisor
                        )
            leave_obj.save()
            
            # finally adding those departments to leave_obj
            for department in department_list:
                leave_obj.department.add(department)
            ## Send email to supervisor
            supervisor = User.objects.get(id=cd['supervisor'])
            t = loader.get_template('registration/supervisor_leave.txt')
            username = request.user.username
            c = Context({
                'id':request.user.id,
                #'department_name':department_list[0].name,
                'username':username,
                'supervisor':leave_obj.supervisor,
                'reason':cd['reason'],
                'start_date':cd['start_date'],
                'end_date':cd['end_date'],
                'type_of_leave':cd['type_of_leave']
                
            })
            msg = t.render(c)
            subject = "Leave Application"
            
            send_mail(
                subject,
                msg,
                request.user.email,
                [supervisor.email],
                fail_silently=True
            )
            return render_to_response(
                                        'registration/leave_approval.html',
                                        {'request':request},
                                        context_instance = RequestContext(request)
                                       )
                
        else:
            print "Leave Application Form is invalid "
    else:
        leave_form = LeaveForm()
    return render_to_response('registration/supervisor_leave.html',
                                {
                                 'leave_form':leave_form,
                                 'request':request,
                                 'base_url':BASE_URL,
                                 'active':'leave'
                                },
                                context_instance = RequestContext(request)
                            )
#-------------------Supervisor Section Ends------------------------------------

#-------------------Employer Section Start------------------------------------
def employee_homepage(request):
    """
    displays the employer first page
    """
    department_obj = Department.objects.get(employee=request.user)
    return render_to_response(
                                'registration/emp_homepage.html',
                                {
                                    'request':request,
                                    'department_obj':department_obj
                                 },
                                context_instance = RequestContext(request)
                               ) 
#---------------------------------------------------------------------------
def employee_profile(request):
    """
    Displays the profile page
    """
    if request.method == "POST":
        department_obj = Department.objects.get(employee=request.user)
        userprofile_form = UserProfileForm(request.POST)
        if userprofile_form.is_valid():
            cd = userprofile_form.cleaned_data
            userprofile_obj = UserProfile.objects.get(user=request.user)
            userprofile_obj.first_name = cd['first_name']
            userprofile_obj.last_name = cd['last_name']
            userprofile_obj.email = cd['email']
            userprofile_obj.street1 = cd['street1']
            userprofile_obj.street2 = cd['street2']
            userprofile_obj.zip_code = cd['post_code']
            userprofile_obj.country = cd['country']
            userprofile_obj.company = department_obj.company
            userprofile_obj.save()
            user_obj = User.objects.get(id=request.user.id)
            user_obj.first_name = userprofile_obj.first_name
            user_obj.last_name = userprofile_obj.last_name
            user_obj.email = userprofile_obj.email 
            return HttpResponseRedirect('/registration/employee_leave/')
        else:
            print "UserProfileForm is invalid"
    else:
        userprofile_form = UserProfileForm()
        try:
            userprofile_obj = UserProfile.objects.get(user=request.user)
            userprofile_form.fields['first_name'].initial = userprofile_obj.first_name
            userprofile_form.fields['last_name'].initial = userprofile_obj.last_name
            userprofile_form.fields['email'].initial = userprofile_obj.email
            userprofile_form.fields['street1'].initial = userprofile_obj.street1
            userprofile_form.fields['street2'].initial = userprofile_obj.street2
            userprofile_form.fields['post_code'].initial = userprofile_obj.zip_code
            userprofile_form.fields['country'].initial = userprofile_obj.country
            
        except:
            pass
        
    return render_to_response(
                                'registration/emp_profile.html',
                                {
                                    'userprofile_form':userprofile_form,
                                    'request':request,
                                    'active':'profile'
                                 },
                                context_instance = RequestContext(request)
                            )
#---------------------------------------------------------------------------
def employee_leave(request):
    """
    Leads to Leave application form because they will not have any rights.
    """

    if request.method == "POST":
        leave_form = LeaveForm(request.POST)
        if leave_form.is_valid():
            cd = leave_form.cleaned_data
            # Picking all department of user
            userprofile_obj = UserProfile.objects.get(user=request.user)
            department_list = userprofile_obj.department.all()
            supervisor = User.objects.get(id=cd['supervisor'])
            leave_obj = Leave(
                        type_of_leave = cd['type_of_leave'],
                        start_date = cd['start_date'],
                        end_date = cd['end_date'],
                        user = request.user,
                        reason = cd['reason'],
                        supervisor = supervisor
                        )
            leave_obj.save()
            
            # finally adding those departments to leave_obj
            for department in department_list:
                leave_obj.department.add(department)
            
            # Send email to supervisor
            
            t = loader.get_template('registration/employee_leave.txt')
            username = request.user.username
            c = Context({
                'id':request.user.id,
                'department_name':department_list[0].name,
                'username':username,
                'supervisor':leave_obj.supervisor,
                'reason':cd['reason'],
                'start_date':cd['start_date'],
                'end_date':cd['end_date'],
                'type_of_leave':cd['type_of_leave']
                
            })
            msg = t.render(c)
            subject = "Leave Application from %s department" % userprofile_obj.department.all()[0].name

            send_mail(
                subject,
                msg,
                request.user.email,
                [userprofile_obj.department.all()[0].supervisor.email],
                fail_silently=True
            )
            return render_to_response(
                                        'registration/leave_approval.html',
                                        {'request':request},
                                        context_instance = RequestContext(request)
                                       )
                
        else:
            print "Leave Application Form is invalid "
    else:
        leave_form = LeaveForm()
    return render_to_response('registration/emp_leave.html',
                                {
                                 'leave_form':leave_form,
                                 'request':request,
                                 'base_url':BASE_URL,
                                 'active':'leave'
                                },
                                context_instance = RequestContext(request)
                                )
#------------------------Employer Section Ends------------------------------------

#-----------------------Common Functions/methods----------------------------------

def leave_detail(request):
    """
    deccribe the detail for a particular leave
    """
    leave_obj = Leave.objects.get(id=request.GET['id'])
    return render_to_response(
                                'registration/leave_detail.html',
                                {
                                    'request':request,
                                    'leave_obj':leave_obj
                                },
                                context_instance = RequestContext(request)
                                )
    
#---------------------------------------------------------------------------
def leave_approval(request):
    """
    leave approval process makes the status field true or false
    """
   
    leave_obj = Leave.objects.get(id=request.GET['id'])
    if request.GET['name'] == "accept":
        leave_obj.status = True
        approve_variable = "Approved"
    else:
        leave_obj.status = False
        approve_variable = "Disapproved"
    leave_obj.save()
        
    # Send email to employer
    
    t = loader.get_template('registration/leave_status_email.txt')
    c = Context({
        'employee':leave_obj.user.username,
        'start_date':leave_obj.start_date,
        'end_date':leave_obj.end_date,
        'type_of_leave':leave_obj.type_of_leave,
        'length':leave_obj.leave_count,
        'approve_variable':approve_variable
    })
    msg = t.render(c)
    subject = "Leave Application %s" % approve_variable

    send_mail(
        subject,
        msg,
        # All these emails will be ofcourse from company id.
        request.user.email,
        [leave_obj.user.email],
        fail_silently=True
    )
    return render_to_response(
                                'registration/leave_status.html',
                                {
                                    'request':request,
                                    'leave_obj':leave_obj,
                                    'approve_variable':approve_variable
                                },
                                context_instance = RequestContext(request)
                                )
#---------------------------------------------------------------------------
def password_reset(request):
    """
    Change password for logged in user
    whether it is supervisor or it is an employee
    """

    if request.method == "POST":
        password_form = PasswordForm(request.POST)
        if password_form.is_valid():
            cd = password_form.cleaned_data
            user_obj = User.objects.get(id=request.GET['id'])
            user_obj.username = cd['username']
            user_obj.set_password(cd['password'])
            user_obj.save()
            new_profile = user_obj.profile
            profile = user_obj.profile
            key = uuid.uuid4().__str__()
            profile.key = key
            profile.first_name = user_obj.first_name
            profile.last_name = user_obj.last_name
            profile.email = user_obj.email
            profile.save()
            userprofile_obj = UserProfile.objects.get(user=user_obj)
            if userprofile_obj.is_supervisor == True:
                return HttpResponseRedirect('/registration/supervisor_detail/?id=%s' % user_obj.id)
            else:
                return HttpResponseRedirect('/registration/employee_leave/')
        else:
            print "Default password Form is invalid !"
            
    else:
        password_form = PasswordForm()
            
    return render_to_response('registration/password_reset_form.html',
                                {
                                'request':request,
                                'password_form':password_form,
                                },
                                context_instance = RequestContext(request)
                              )
#---------------------------------------------------------------------------