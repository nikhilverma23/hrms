#Django Imports
from django.shortcuts import get_object_or_404, HttpResponseRedirect,\
render_to_response, render
from django.core.mail import EmailMessage
from django.template import RequestContext, loader, Context
from django.contrib.auth import authenticate, login

#HRMS Imports
from hrms import settings
from hrms.settings import BASE_URL
from hrms.registration.models import Company, UserProfile
from hrms.registration.views import register_user
from hrms.registration.forms import CompanyForm
from hrms.home.forms import LoginForm
# Create your views here.


def home(request):
    """
    Registration process of company
    """
    
    if request.method == "POST":
        if request.POST['formname'] == 'registration':
            company_detail_form = CompanyForm(request.POST)
            form_login = LoginForm()
            if company_detail_form.is_valid():
                cd = company_detail_form.cleaned_data
                user = register_user(cd)
                company_obj = Company.objects.get_or_create(
                                name = cd['title'],
                                
                                email = cd['email'],
                                website = cd['website'],
                                street1 = cd['street1'],
                                street2 = cd['street2'],
                                zip_code = cd['post_code'],
                                country = cd['country'],
                                phone_number = cd['phone_number'],
                                category = cd['industry_type'],
                                business_year_start = cd['business_year_start'],
                                business_year_end = cd['business_year_end'],
                                description = cd['description'],
                                )
                #userprofile_obj = UserProfile.objects.get(user=user)
                #userprofile_obj.is_supervisor = True
                #userprofile_obj.save()
                
                
                if user:
                    address = user.email
                    redirect_to = 'registration/registration_confirmation?email=%s' % \
                    address
                    
                    subject='[HRMSystems]'
                    message = """Hi %s,
                    
                    You have successfully registered with HRMSystems.
    
                    Please follow the link below to complete your registration:
                        
                    http://%s/registration/verify_registration/?key=%s&username=%s
                                        
                    Regards,
                    HRMSystems  Team
                     
                    """ % (user.username, BASE_URL, user.profile.key, 
                           user.username)
                    email = EmailMessage(subject, message, to=[address])
                    email.send()
                else:
                    redirect_to = 'registration/registration_failure'
                return HttpResponseRedirect(redirect_to)
            else:
                print "Form is not valid"
    
        if request.POST['formname'] == 'login':
            form_login = LoginForm(request.POST)
            company_detail_form = CompanyForm()
            if form_login.is_valid():
                data = form_login.cleaned_data
                user = authenticate(username=data['username'], 
                                   password=data['password'])
                login(request, user)
                if user.is_staff == True:
                    return HttpResponseRedirect('/registration/summary/?user=company&active=summary')
                elif user.userprofile_set.values('is_supervisor')[0].get('is_supervisor') == True:
                    return HttpResponseRedirect('/registration/supervisor_detail/')
                else:
                    return HttpResponseRedirect('/registration/employee_homepage/')

    else:
        company_detail_form = CompanyForm()
        form_login = LoginForm()
    return render_to_response(
                              'home/home_page.html',
                              {
                                'company_detail_form':company_detail_form,
                               'form_login' : form_login,
                               'request':request,
                               'base_url':BASE_URL
                               },
                              context_instance = RequestContext(request)
                              )