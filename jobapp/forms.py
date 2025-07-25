from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile, Job, Application
    


class UserRegistrationForm(UserCreationForm):
    is_recruiter=forms.BooleanField(required=False,label="Register as Recruiter")
    
    class Meta:
        model = CustomUser
        fields = ['username','email','password1','password2','is_recruiter']
        
class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)        
    
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'contact', 'resume', 'profile_picture']  
        

class JobForm(forms.ModelForm):
    
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'description']          
        
class ApplicationForm(forms.ModelForm):
    
    class Meta:
        model = Application
        fields = ['resume']        