#django imports
import datetime
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate

#-------------------------------------------------------------------------------
class LoginForm(forms.Form):
    """
    Login form for users
    """
    
    username = forms.CharField(label="Username:",max_length=80,\
                                 required=True,
                                 widget=forms.TextInput(attrs=\
                                                           {'class':'span2','placeholder':'Username'})
                                 )
    password = forms.CharField(label="Password:",\
                                widget=forms.PasswordInput(attrs=\
                                                           {'class':'span2','placeholder':'Password'}),\
                                required=True,
                                )
    
    #---------------------------------------------------------------------------
    def clean_username(self):
        """
        Validating username
        """
        username = self.data.get('username')
        password = self.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username or password.")
        else:
            if not user.is_active:
                raise forms.ValidationError("This account is locked")
        return self.data.get('username')
#-------------------------------------------------------------------------------