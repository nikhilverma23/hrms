# Django Imports
from django.db import models
from django.contrib.auth.models import User


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
    zip_code = models.IntegerField(max_length=7)
    country = models.ForeignKey(Country)
    phone_number = models.CharField(max_length=80,null=True,blank=True)
    decription = models.TextField(blank=True,null=True)
    category = models.ForeignKey(Category)
    business_year_start = models.DateField()
    business_year_end = models.DateField()
    toc = models.BooleanField(default=True, help_text="Terms and Conditions")
    
    
    def __unicode__(self):
        return self.name
    

class Supervisor(models.Model):
    """
    String the REporting Manager info
    """
    
    name = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.name.username
    

class Department(models.Model):
    """
    Department of a company
    """
    
    name = models.CharField(
                            max_length=1024,help_text="Department's Name"
                            )
    employee = models.ForeignKey(User, null=True, blank=True)
    company = models.ForeignKey(Company)
    supervisor = models.ForeignKey(Supervisor)
    
    
    def __unicode__(self):
        return self.name
    
class UserProfile(models.Model):
    """
    Extending the User Model
    """
    
    user = models.OneToOneField(User, unique=True, editable=False)
    employee_id = models.CharField(max_length=255)
    department = models.ManyToManyField(Department)
    first_name = models.CharField(max_length=80, blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    street1 = models.CharField(max_length=1024, null=True, blank=True)
    street2 = models.CharField(max_length=1024, null=True, blank=True)
    state = models.CharField(max_length=1024, null=True, blank=True)
    zip_code = models.IntegerField(max_length=7)
    country = models.ForeignKey(Country)
    company = models.ForeignKey(Company)
    is_supervisor = models.BooleanField(default=False)
    
    
    def __unicode__(self):
        return self.user.get_full_name()
    
    
class Leave(models.Model):
    """
    When the employee is applying for leave
    """
    
    type_of_leave = models.CharField(max_length=255,help_text="Type of Leave")
    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey(User)
    department = models.ForeignKey(Department)
    supervisor = models.ForeignKey(Supervisor)
    leave_count = models.CharField(max_length=5,null=True,blank=True)
    
    def __unicode__(self):
        return self.type_of_leave
    
    
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
    
    