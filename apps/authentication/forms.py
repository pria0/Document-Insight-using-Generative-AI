from django import forms
from authentication.models import Account
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class AccountCreationForm(forms.ModelForm): 
    """ 
    A form for creating new users. Includes all the required 
    fields, plus a repeated password. 
    """ 

    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta: 
        model = Account 
        fields = ('email',)

    def save(self, commit=True): 
        # Save the provided password in hashed format 
        user = super(AccountCreationForm, self).save(commit=False)
        user.username = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"]) 
        if commit: 
            user.save() 
        return user 


class AccountUpdateForm(forms.ModelForm): 
    """ 
    A form for updating users. Includes all the fields on 
    the user, but replaces the password field with admin's 
    password hash display field. 
    """ 
    password = ReadOnlyPasswordHashField() 

    class Meta: 
        model = Account
        fields = ('password',)

    def clean_password(self): 
        # Regardless of what the user provides, return the initial value. 
        # This is done here, rather than on the field, because the 
        # field does not have access to the initial value 
        return self.initial["password"] 


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget = forms.PasswordInput,)

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            "name":"email"})
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            "name":"password"})
    
    def clean(self, *args, **keyargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Email or Password not correct!")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect Password!")
            if not user.is_active:
                raise forms.ValidationError("User is no longer active!")
        return super(UserLoginForm, self).clean(*args, **keyargs)
