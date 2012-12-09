#python imports
import os
import uuid
import datetime
import json
from datetime import timedelta
import sys, traceback
import os, random, string
import hashlib

#django imports
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import load_backend, login, logout
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.core.mail import send_mail
from django.template import RequestContext, loader, Context

#HRMS imports
from hrms.home.forms import LoginForm
from hrms.registration.forms import DepartmentForm, EmployeeForm,\
PasswordForm,LeaveForm
from hrms.registration.models import Department, UserProfile, Company
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
                # Taking out the companydetails for filling
                # department object
                company_obj = Company.objects.get(email=request.user.username)
                department_obj = Department.objects.get_or_create(
                                    name=department_name_list[department_counter],
                                    company = company_obj,
                                    supervisor= user_obj
                                )
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
                
            return HttpResponseRedirect('/registration/employee/')
            
    else:
        department_form = DepartmentForm()
    
    return render_to_response('registration/create_department.html',
                              {'request':request,
                               'department_form':department_form},
                              context_instance = RequestContext(request)
                              )
#---------------------------------------------------------------------------    
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
                
            return HttpResponseRedirect('/registration/summary/')
        
            
    else:
        
        employee_form = EmployeeForm()
        company_obj = Company.objects.get(email=request.user.username)
        # Listing the department created by the company itself
        department = company_obj.department_set.all()
            
    return render_to_response('registration/create_employee.html',
                              {'request':request,
                               'department':department,
                               'employee_form':employee_form},
                              context_instance = RequestContext(request)
                            )
#---------------------------------------------------------------------------
def summary(request):
    """
    This will tell the complete summary in a Table
    """
 
    company_obj = Company.objects.get(email=request.user)
    department_obj = Department.objects.filter(company=company_obj)
    
    return render_to_response('registration/summary.html',
                                {'request':request,
                                'company_obj':company_obj,
                                'department_obj':department_obj
                                },
                                context_instance = RequestContext(request)
                              )
#---------------------------------------------------------------------------
def password_reset(request):
    """
    Change password for logged in user
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
                return HttpResponseRedirect('/registration/supervisor_detail/')
            else:
                return HttpResponseRedirect('/registration/employee_detail/')
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
def supervisor_detail(request):
    """
    Describe the detail of leaves to employees.
    """

    return render_to_response('registration/supervisor_detail.html',
                                    {'request':request,'base_url':BASE_URL},
                                    context_instance = RequestContext(request)
                                )
#---------------------------------------------------------------------------
def employee_detail(request):
    """
    Leads to Leave application form because they will not have any rights.
    """
    form = LeaveForm(request)
    if request.method == "POST":
        leave_form = LeaveForm(request.POST)
        if leave_form.is_valid():
            cd = leave_form.cleaned_data
        else:
            print "Leave Application Form is invalid "
    data = dict(form=form,request=request,base_url=BASE_URL)
    return render_to_response('registration/employee_detail.html',
                                data,
                                context_instance = RequestContext(request)
                                )
#---------------------------------------------------------------------------