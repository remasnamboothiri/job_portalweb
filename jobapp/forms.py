from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile, Job, Application , Interview
    


class UserRegistrationForm(UserCreationForm):
    is_recruiter=forms.BooleanField(required=False,label="Register as Recruiter")
    
    class Meta:
        model = CustomUser
        fields = ['username','email','password1','password2','is_recruiter']
        
class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)        
    
    
# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['full_name', 'contact', 'resume', 'profile_picture']  
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone', 'location', 'bio', 'skills', 'resume', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'skills': forms.TextInput(attrs={'placeholder': 'React, JavaScript, Python, Django...'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, State'}),
        }        

   

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'featured_image', 'title', 'department', 'location', 
            'employment_type', 'experience_level', 'salary_min', 
            'salary_max', 'description', 'required_skills', 'status',
            'enable_ai_interview', 'interview_duration', 'interview_question_count'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Senior Frontend Developer',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g. San Francisco, CA',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe the role, responsibilities, and what you\'re looking for...',
                'class': 'form-control'
            }),
            'required_skills': forms.TextInput(attrs={
                'placeholder': 'React, JavaScript, TypeScript (comma separated)',
                'class': 'form-control'
            }),
            'salary_min': forms.NumberInput(attrs={
                'placeholder': '80000',
                'class': 'form-control'
            }),
            'salary_max': forms.NumberInput(attrs={
                'placeholder': '120000',
                'class': 'form-control'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'enable_ai_interview': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'interview_duration': forms.Select(attrs={
                'class': 'form-control'
            }),
            'interview_question_count': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Job Title',
            'department': 'Department',
            'location': 'Location',
            'employment_type': 'Employment Type',
            'experience_level': 'Experience Level',
            'salary_min': 'Salary Min ($)',
            'salary_max': 'Salary Max ($)',
            'description': 'Job Description',
            'required_skills': 'Required Skills',
            'status': 'Job Status',
            'enable_ai_interview': 'Enable AI Interview for this position',
            'interview_duration': 'Default Duration',
            'interview_question_count': 'Question Count',
            'featured_image': 'Upload Featured Image',
        }
        
class ApplicationForm(forms.ModelForm):
    
    class Meta:
        model = Application
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={
                'id': 'resume-file',
                'accept': '.pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'class': 'file-upload-input'
            })
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Check file size (5MB limit)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 5MB.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = resume.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError('Please upload a PDF, DOC, or DOCX file.')
        
        return resume       
        
        
        
        
#interview form
class ScheduleInterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['job_position', 'candidate_name', 'candidate_email', 'interview_date']
        widgets = {
            'interview_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'job_position': forms.Select(attrs={'class': 'form-control'}),
            'candidate_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter candidate full name'}),
            'candidate_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'candidate@example.com'}),
        }
        labels = {
            'job_position': 'Job Position',
            'candidate_name': 'Candidate Name',
            'candidate_email': 'Candidate Email',
            'interview_date': 'Interview Date & Time',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is provided, filter job_position to only show jobs posted by this user
        if user and hasattr(user, 'is_recruiter') and user.is_recruiter:
            self.fields['job_position'].queryset = Job.objects.filter(posted_by=user)
        
        # Make job_position field read-only if it's already set in initial data
        if self.initial.get('job_position'):
            self.fields['job_position'].widget.attrs['readonly'] = True
        