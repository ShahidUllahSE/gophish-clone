from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from apps.home.models import Group  # Assuming you have a Group model

# Existing EmailForm
class EmailForm(forms.Form):
    to = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


# User Registration Form
class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


# User Login Form
class LoginUserForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


# Group Assignment Form
class AssignGroupForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)

    class Meta:
        fields = ['user', 'group']
