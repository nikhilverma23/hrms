# Django Imports
from django.db import models
from django.contrib.auth.models import User
#hrms Imports
from hrms.settings import USER_KEY_EXPIRATION_DAYS
#Python Import
import datetime
from datetime import timedelta

class Category(models.Model):
    """
    Describes the type of company
    """
    
    industry_type = models.CharField(max_length=1024, null=True,blank=True)
    
    def __unicode__(self):
        return self.industry_type
    
class Country(models.Model):
    """
    List of maximum  possible countries
    """
    
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    

    

    
class Company(models.Model):
    """
    Describing the company attributes
    """
    
    name = models.CharField(
                            max_length=1024,null=False,blank=False,\
                            help_text="Company's Name"
                            )
    email = models.EmailField(null=True,blank=True)
    website = models.URLField(null=True,blank=True)
    street1 = models.CharField(max_length=1024)
    street2 = models.CharField(max_length=1024, null=True, blank=True)
    state = models.CharField(max_length=1024, null=True, blank=True)
    zip_code = models.IntegerField(max_length=7,null=True, blank=True)
    country = models.ForeignKey(Country,null=True, blank=True)
    phone_number = models.CharField(max_length=80,null=True,blank=True)
    description = models.TextField(blank=True,null=True)
    category = models.ForeignKey(Category)
    business_year_start = models.DateField()
    business_year_end = models.DateField()
    toc = models.BooleanField(default=True, help_text="Terms and Conditions")
    
    
    def __unicode__(self):
        return self.name
    

class Department(models.Model):
    """
    Department of a company
    """
    
    supervisor = models.ForeignKey(User, related_name="supervisor",null=True,blank=True)
    employee = models.ManyToManyField(User, null=True, blank=True)
    name = models.CharField(
                            max_length=1024,help_text="Department's Name"
                            )
    company = models.ForeignKey(Company)
    
    
    
    
    def __unicode__(self):
        return self.name
User.new_employee_profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
    

    
class UserProfile(models.Model):
    """
    Extending the User Model
    """
    
    user = models.ForeignKey(User, unique=True)
    key = models.CharField(max_length=1024)
    key_expires = models.DateTimeField(default=\
                                       datetime.datetime.now() + \
                                       timedelta(days=USER_KEY_EXPIRATION_DAYS))
    employee_id = models.CharField(max_length=255)
    department = models.ManyToManyField(Department)
    first_name = models.CharField(max_length=80, blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    street1 = models.CharField(max_length=1024, null=True, blank=True)
    street2 = models.CharField(max_length=1024, null=True, blank=True)
    state = models.CharField(max_length=1024, null=True, blank=True)
    zip_code = models.CharField(max_length=7,null=True, blank=True)
    country = models.ForeignKey(Country,null=True, blank=True)
    company = models.ForeignKey(Company,null=True, blank=True)
    is_supervisor = models.BooleanField(default=False)
    
    
    def __unicode__(self):
        return self.user.username
    

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])    



class LeaveType(models.Model):
    """
    Specify the leave type.
    """
    type_of_leave = models.CharField(max_length=255,help_text="Type of Leave") 
    
    def __unicode__(self):
        return self.type_of_leave
    


class Leave(models.Model):
    """
    When the employee is applying for leave
    """
    
    type_of_leave = models.ForeignKey(LeaveType,null=True,blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey(User,help_text="Employer who wants leave")
    department = models.ManyToManyField(Department,null=True,blank=True)
    leave_count = models.CharField(max_length=5,null=True,blank=True)
    reason = models.TextField(null=True,blank=True)
    status = models.BooleanField(default=False)
    supervisor = models.ForeignKey(
                                    User,related_name="supervisor_leave",
                                    help_text = "who is supervisor",
                                    null=True,blank=True,
                                   )
    
    def __unicode__(self):
        leave_count = str(self.leave_count)
        return leave_count
    
    
class RestrictedDay(models.Model):
    """
    Describes the condtional days whether you can take off or not
    """
    
    title = models.CharField(max_length=80, blank=True, null=True)
    restriction_day_date = models.DateField()
    
    def __unicode__(self):
        return self.date
    
class Allowances(models.Model):
    """
    Describing the allowances
    """
    
    title = models.CharField(max_length=80)
    employee = models.ForeignKey(User)
    department = models.ForeignKey(Department)
    description = models.TextField(null=True,blank=True)
    status = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.title
    
    