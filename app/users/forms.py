from django import forms
from django.contrib.auth.models import User  # uses the auth_user table
from django.contrib.auth.forms import UserCreationForm  # will automatically use auth_user table
from . models import Profile
# the table will be auth_user which was already created in the initial migration
class UserRegisterForm(UserCreationForm):  # the table will be auth_user, same as
    email = forms.EmailField()  # in norder to add email to the form

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # which fields to show in the form

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
