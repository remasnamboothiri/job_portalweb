from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile, Job, Application , Interview , Candidate


    


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
            'title', 'company', 'location', 'department', 'employment_type', 
            'experience_level', 'description', 'required_skills', 
            'salary_min', 'salary_max', 'status', 'featured_image',
            'enable_ai_interview', 'interview_duration', 'interview_question_count'
            
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Senior Frontend Developer',
                'class': 'form-control',
                'required': True,
            }),
            'company': forms.TextInput(attrs={
                'placeholder': 'e.g. Tech Company Inc.',
                'class': 'form-control',
                'required': True,
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g. San Francisco, CA',
                'class': 'form-control',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': 'Describe the role, responsibilities, and what you\'re looking for...',
                'class': 'form-control',
                'required': True,
            }),
            'required_skills': forms.TextInput(attrs={
                'placeholder': 'React, JavaScript, TypeScript (comma separated)',
                'class': 'form-control',
            }),
            'salary_min': forms.NumberInput(attrs={
                'placeholder': '80000',
                'class': 'form-control',
                'min': '0',
            }),
            'salary_max': forms.NumberInput(attrs={
                'placeholder': '120000',
                'class': 'form-control',
                'min': '0',
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
             'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'enable_ai_interview': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'interview_duration': forms.Select(attrs={
                'class': 'form-control',
            }),
            'interview_question_count': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'title': 'Job Title *',
            'company': 'Company Name *',
            'department': 'Department',
            'location': 'Location *',
            'employment_type': 'Employment Type',
            'experience_level': 'Experience Level',
            'salary_min': 'Salary Min ($)',
            'salary_max': 'Salary Max ($)',
            'description': 'Job Description *',
            'required_skills': 'Required Skills',
            'status': 'Job Status',
            'enable_ai_interview': 'Enable AI Interview for this position',
            'interview_duration': 'Default Duration',
            'interview_question_count': 'Question Count',
            'featured_image': 'Upload Featured Image',
        }
        
        help_texts = {
            'title': 'Enter a clear, descriptive job title',
            'company': 'Enter the company or organization name',
            'location': 'Enter the job location (city, state/country)',
            'description': 'Provide detailed job description, responsibilities, and requirements',
            'required_skills': 'List key skills separated by commas',
            'salary_min': 'Minimum salary offered',
            'salary_max': 'Maximum salary offered',
            'featured_image': 'Upload an image to represent this job posting (optional)',
        }
        
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError('Job title is required.')
        return title.strip()

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if not company or not company.strip():
            raise forms.ValidationError('Company name is required.')
        return company.strip()

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location or not location.strip():
            raise forms.ValidationError('Location is required.')
        return location.strip()

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise forms.ValidationError('Job description is required.')
        if len(description.strip()) < 50:
            raise forms.ValidationError('Job description must be at least 50 characters long.')
        return description.strip()

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        if salary_min is not None and salary_max is not None:
            if salary_min > salary_max:
                raise forms.ValidationError('Minimum salary cannot be greater than maximum salary.')
        
        return cleaned_data   
        
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'required': True
            })
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume:
            raise forms.ValidationError('Please select a resume file to upload.')
            
        # Check file size (5MB limit)
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File size must be less than 5MB.')
        
        # Check file extension
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_name = resume.name.lower()
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError('Please upload a PDF, DOC, or DOCX file.')
        
        return resume       
        
        
        
        
#interview form
# class ScheduleInterviewForm(forms.ModelForm):
#     interview_link = forms.URLField(
#         required=False,
#         help_text='Enter Google Meet, Zoom, or any video call link',
#         widget=forms.URLInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'https://meet.google.com/abc-defg-hij or https://zoom.us/j/123456789'
#         })
#     )
    
#     class Meta:
#         model = Interview
#         fields = [ 'job', 'candidate_name', 'candidate_email', 'scheduled_at', 'link']
#         widgets = {
#             'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
#             'job': forms.Select(attrs={'class': 'form-control'}),
#             'candidate_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter candidate full name'}),
#             'candidate_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'candidate@example.com'}),
#         }
#         labels = {
#             'job': 'Job Position',
#             'candidate_name': 'Candidate Name',
#             'candidate_email': 'Candidate Email',
#             'scheduled_at': 'Interview Date & Time',
#             'link': 'Interview Link',
#         }
    
#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)
        
#         # If user is provided, filter job_position to only show jobs posted by this user
#         if user and hasattr(user, 'is_recruiter') and user.is_recruiter:
#             self.fields['job'].queryset = Job.objects.filter(posted_by=user)
        
#         # Make job_position field read-only if it's already set in initial data
#         if self.initial.get('job'):
#             self.fields['job'].widget.attrs['readonly'] = True
    
#     def save(self, commit=True):
#         interview = super().save(commit=False)
        
#         # If no custom link provided, generate a default one
#         if not interview.link:
#             interview.link = f"https://meet.google.com/{interview.interview_id or 'generated-link'}"
        
#         if commit:
#             interview.save()
#         return interview
        
        
        
        
class ScheduleInterviewForm(forms.ModelForm):
    candidate = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Candidate',
        help_text='Choose from candidates you have added',
        empty_label='Select a candidate...'
    )
    
    class Meta:
        model = Interview
        fields = ['job', 'scheduled_at', 'interview_duration_minutes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'job': forms.Select(attrs={'class': 'form-control'}),
            'interview_duration_minutes': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'job': 'Which job is it?',
            'scheduled_at': 'Interview Date & Time',
            'interview_duration_minutes': 'Interview Duration',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'is_recruiter') and user.is_recruiter:
            # Filter jobs for this recruiter
            self.fields['job'].queryset = Job.objects.filter(posted_by=user)
            self.fields['job'].empty_label = 'Select a job...'
            # Filter candidates added by this recruiter
            self.fields['candidate'].queryset = Candidate.objects.filter(added_by=user)
        else:
            # If no user provided, set empty querysets
            self.fields['job'].queryset = Job.objects.none()
            self.fields['candidate'].queryset = Candidate.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        job = cleaned_data.get('job')
        candidate = cleaned_data.get('candidate')
        scheduled_at = cleaned_data.get('scheduled_at')
        
        if not job:
            raise forms.ValidationError('Please select a job position.')
        
        if not candidate:
            raise forms.ValidationError('Please select a candidate.')
            
        if not scheduled_at:
            raise forms.ValidationError('Please select interview date and time.')
        
        return cleaned_data
    
    def save(self, commit=True):
        interview = super().save(commit=False)
        
        # Get candidate info from selected candidate
        candidate = self.cleaned_data.get('candidate')
        if candidate:
            interview.candidate_name = candidate.name
            interview.candidate_email = candidate.email
            interview.candidate_phone = getattr(candidate, 'phone', '')
            # Don't set interview.candidate as it expects CustomUser, not Candidate
        
        # Generate unique interview link
        if not interview.link:
            interview.link = f"/interview/ready/{interview.uuid}/"
        
        # Ensure UUID is generated
        if not interview.uuid:
            import uuid
            interview.uuid = uuid.uuid4()
        
        if commit:
            interview.save()
        return interview        
        
        
        
class ScheduleInterviewWithCandidateForm(forms.Form):
    job = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Which job is it?',
        empty_label='Select a job...',
        required=True
    )
    scheduled_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local', 
            'class': 'form-control',
            'required': True
        }),
        label='Interview Date & Time',
        required=True,
        help_text='Select the date and time for the interview'
    )
    interview_duration_minutes = forms.ChoiceField(
        choices=[
            (5, '5 minutes'),
            (10, '10 minutes'),
            (15, '15 minutes'),
            (20, '20 minutes'),
            (30, '30 minutes'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Interview Duration',
        initial=15,
        required=True,
        help_text='Select how long this interview should be'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'is_recruiter') and user.is_recruiter:
            self.fields['job'].queryset = Job.objects.filter(posted_by=user)
        else:
            self.fields['job'].queryset = Job.objects.none()
        
        self.candidate = candidate
    
    def clean(self):
        cleaned_data = super().clean()
        job = cleaned_data.get('job')
        scheduled_at = cleaned_data.get('scheduled_at')
        
        if not job:
            raise forms.ValidationError('Please select a job position.')
            
        if not scheduled_at:
            raise forms.ValidationError('Please select interview date and time.')
        
        return cleaned_data
    
    def save(self, user):
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        User = get_user_model()
        
        job = self.cleaned_data['job']
        scheduled_at = self.cleaned_data['scheduled_at']
        
        # Ensure scheduled_at is not None
        if not scheduled_at:
            scheduled_at = timezone.now() + timezone.timedelta(days=1)  # Default to tomorrow
        
        # Create or get a dummy user for unregistered candidates
        dummy_user, created = User.objects.get_or_create(
            username=f"candidate_{self.candidate.email}",
            defaults={
                'email': self.candidate.email,
                'first_name': self.candidate.name,
                'is_active': False,  # Mark as inactive
                'is_recruiter': False
            }
        )
        
        interview = Interview(
            job=job,
            candidate=dummy_user,  # Use dummy user to satisfy constraint
            candidate_name=self.candidate.name,
            candidate_email=self.candidate.email,
            candidate_phone=self.candidate.phone,
            scheduled_at=scheduled_at,
            interview_duration_minutes=self.cleaned_data['interview_duration_minutes']
        )
        interview.save()
        return interview

class AddCandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ('name', 'email', 'phone', 'resume')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter candidate full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'candidate@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }
        labels = {
            'name': 'Candidate Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'resume': 'Resume (Optional)',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email is required.')
        return email.lower().strip()
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError('Name is required.')
        return name.strip()
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone or not phone.strip():
            raise forms.ValidationError('Phone number is required.')
        return phone.strip()        