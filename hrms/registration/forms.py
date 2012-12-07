from django import forms
from hrms.registration.models import Category, Country


class CompanyForm(forms.Form):
    """
    Describing the company fields 
    """
    # Primary Info For company
    email = forms.EmailField(required=True, initial = "info@xyz.com")
    title = forms.CharField(label="Company's Name", max_length=1024,required=True, initial="XYZ PVT. LTD")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    indutry_type = forms.ModelChoiceField(queryset=Category.objects.all()\
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
    
    name = forms.CharField(label= "Department Name", max_length=255,required=True)
    #employee = forms.CharField(label="Employee", max_length=255,required=False)
    #employee_email = forms.EmailField(required=True, initial = "nikhilverma55@gmail.com")
    #supervisor_username = forms.CharField(label= "Supervisor Username",max_length=255, required=False)
    supervisor_first_name = forms.CharField(label= "Supervisor First Name",max_length=255, required=False)
    supervisor_last_name = forms.CharField(label= "Supervisor Last Name",max_length=255, required=False)
    supervisor_email = forms.EmailField(required=True, initial = "nikhilverma55@gmail.com")
    
    
class EmployeeForm(forms.Form):
    """
    Decsribing the Employee
    """
    first_name = forms.CharField(label= "Employee First Name", max_length=255,required=True)
    last_name = forms.CharField(label= "Employee Last Name", max_length=255,required=True)
    employee_email = forms.EmailField(required=True, initial = "nikhilverma55@gmail.com")
    
       
    
    
    
    