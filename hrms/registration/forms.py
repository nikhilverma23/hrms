from django import forms
from hrms.registration.models import Category, Country, Department,\
UserProfile, LeaveType


class CompanyForm(forms.Form):
    """
    Describing the company fields 
    """
    # Primary Info For company
    email = forms.EmailField(required=True, initial = "info@xyz.com")
    title = forms.CharField(label="Company's Name", max_length=1024,required=True, initial="XYZ PVT. LTD")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    industry_type = forms.ModelChoiceField(queryset=Category.objects.all()\
                                          ,required=False)
    website = forms.URLField(required=True)
    description = forms.CharField(widget=forms.Textarea, initial='Describe omething about the company')
    #Address Fields
    street1 = forms.CharField(label= "Address", max_length=255,required=True)
    street2 = forms.CharField(max_length=255,required=True)
    post_code = forms.IntegerField(required=True)
    country = forms.ModelChoiceField(queryset=Country.objects.all(),required=True)
    # Phone Number
    phone_number = forms.CharField(max_length=20,required=True)
    # Business Years
    business_year_start = forms.DateField(initial="2012-04-02")
    business_year_end = forms.DateField(initial="2012-04-03")
    # Terms and Conditions
    toc = forms.BooleanField(label="I agree the terms & conditions",initial=True)
    
    
    
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("A user with that username already exists.")

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")        
        return self.cleaned_data
    
class DepartmentForm(forms.Form):
    """
    company will create these departments
    """
    
    name = forms.CharField(max_length=255,required=True)
    supervisor_first_name = forms.CharField(max_length=255, required=False)
    supervisor_last_name = forms.CharField(max_length=255, required=False)
    supervisor_email = forms.EmailField(required=True)
    
    
class EmployeeForm(forms.Form):
    """
    Decsribing the Employee
    """
    
    department = forms.ModelChoiceField(queryset=Department.objects.all(),empty_label=u'Select Department',required=True)
    first_name = forms.CharField(label= "Employee First Name", max_length=255,required=True)
    last_name = forms.CharField(label= "Employee Last Name", max_length=255,required=True)
    employee_email = forms.EmailField(required=True, initial = "nikhilverma55@gmail.com")
    
       

class PasswordForm(forms.Form):
    """
    This form changes the default username and password
    """
    
    username = forms.CharField(max_length=80,required=True)
    password = forms.CharField(widget=forms.PasswordInput,required=True)
    
    
class LeaveForm(forms.Form):
    """
    Describing the leave application process
    """
    
    def __init__(self, *args, **kwargs):
        super(LeaveForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs['class'] = "datepicker"
        self.fields['end_date'].widget.attrs['class'] = "datepicker"
        

    EXTRA_CHOICES = (
                        ('0','Select Leave length'),
                        ('1','Half Day'),
                        ('2','Full Day'),
                    )
    
    
    qs=UserProfile.objects.filter(is_supervisor=True)
    SUPERVISOR_CHOICES = [(supervisor.user.id, unicode(supervisor.user.username)) for supervisor in qs]
    start_date = forms.DateField()
    end_date = forms.DateField()
    type_of_leave = forms.ModelChoiceField(
                                    queryset = LeaveType.objects.all(),
                                    empty_label="Select Leave Type",
                                    required=True
                                    )
    leave_count = forms.ChoiceField(
                                    label="Leave Count",
                                    choices=EXTRA_CHOICES,
                                    widget=forms.Select(),
                                    required=True
                                    )
    reason = forms.CharField(
                            widget=forms.Textarea,
                            initial='Valid Reason For Leave',
                            required=True
                            )
    supervisor = forms.ChoiceField(label="Supervisor",
                                    choices=SUPERVISOR_CHOICES,
                                    required = True,
                                    widget=forms.Select()
                                    )
    
class UserProfileForm(forms.Form):
    """
    adding user profile details
    """
    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=80)
    email = forms.EmailField()
    street1 = forms.CharField(max_length=255,required=False)
    street2 = forms.CharField(max_length=255,required=False)
    post_code = forms.CharField(max_length=255,required=False)
    country = forms.ModelChoiceField(queryset=Country.objects.all(),
                                     required=True)



    
    
    