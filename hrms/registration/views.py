#python imports
import os
import uuid
import datetime
import json
import urllib2 
from urllib2 import urlopen
from datetime import timedelta
import sys, traceback

#django imports
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import load_backend, login, logout
from django.conf import settings
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission

#HRMS imports
from hrms.home.forms import LoginForm

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
def set_password(raw_password):
    import random
    algo = 'sha1'
    salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    hsh = get_hexdigest(algo, salt, raw_password)
    self.password = '%s$%s$%s' % (algo, salt, hsh)
#------------------------------------------------------------------------------    
import hashlib

def register_user(data):
    """
    This method is used to register a new user and create a user profile.
    """
    password = hashlib.sha1(data['confirm_password']).hexdigest()
    #password = set_password(data['confirm_password'])
    new_user = User(username=data['email'], email=data['email'], 
                    is_staff=True
                    )
    new_user.set_password(data['confirm_password'])
    new_user.save()
    
    new_user.first_name = data['title']
    new_user.email = data['email']
    new_user.is_locked = True
    new_user.save()
    #
    #somemodel_ct = ContentType.objects.get(app_label='auth', model='user')
    #
    #can_view = Permission(name='Can View', codename='can_view_something',
    #                       content_type=somemodel_ct)
    #can_view.save()
    #
    #can_modify = Permission(name='Can Modify', codename='can_modify_something',
    #                       content_type=somemodel_ct)
    #can_modify.save()
    
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
    login_form = LoginForm()
    return render_to_response('registration/login.html',
                              {'login_form' : login_form},
                              context_instance = RequestContext(request)
                              )

#-------------------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
#-------------------------------------------------------------------------------
def login_error(request):
    return HttpResponseRedirect('registration/login_error.html')
#-------------------------------------------------------------------------------

def create_department(request):
    return render_to_response('registration/after_registration.html',
                              {'request':request},
                              context_instance = RequestContext(request)
                              )
    
    

