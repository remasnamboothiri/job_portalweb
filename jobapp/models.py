from django.db import models
from django.contrib.auth.models import AbstractUser , User
from django.conf import settings
from taggit.managers import TaggableManager

import uuid

# for integrating timestamp 
import hashlib
import time
from django.utils import timezone



# Create your models here.

class CustomUser(AbstractUser):
    is_recruiter=models.BooleanField(default=False) # True = Recruiter, False = Job Seeker
    
    def __str__(self):
        return self.username

# class Profile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=100)
#     contact = models.CharField(max_length=20)
#     resume = models.FileField(upload_to='resumes/')
#     profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    
#     def __str__(self):
#         return f"{self.user.username}'s Profile"



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    skills = models.CharField(max_length=300, blank=True, help_text="Separate skills with commas")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
               
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    

DEPARTMENT_CHOICES = [
    ('engineering', 'Engineering'),
    ('marketing', 'Marketing'),
    ('sales', 'Sales'),
    ('hr', 'Human Resources'),
    ('finance', 'Finance'),
    ('operations', 'Operations'),
    ('design', 'Design'),
    ('product', 'Product'),
    ('customer_support', 'Customer Support'),
    ('other', 'Other'),
]






EMPLOYMENT_TYPE_CHOICES = [
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
    ('internship', 'Internship'),
    ('freelance', 'Freelance'),
]

EXPERIENCE_LEVEL_CHOICES = [
    ('entry', 'Entry Level'),
    ('mid', 'Mid Level'),
    ('senior', 'Senior Level'),
    ('lead', 'Lead/Manager'),
    ('executive', 'Executive'),
]
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('paused', 'Paused'),
    ('closed', 'Closed'),
    ('expired', 'Expired'),
    ('filled', 'Position Filled'),
]

class Job(models.Model):
    # Basic Information
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    featured_image = models.ImageField(upload_to='job_images/', blank=True, null=True)
    
    # New fields based on the images
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='other')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='mid')
    salary_min = models.IntegerField(help_text="Minimum salary in your currency", default=50000)
    salary_max = models.IntegerField(help_text="Maximum salary in your currency", default=80000)
    required_skills = models.TextField(max_length=500, help_text="Comma separated skills", default='Not specified')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # AI Interview Settings
    enable_ai_interview = models.BooleanField(default=False)
    interview_duration = models.CharField(
        max_length=20,
        choices=[
            ('15', '15 minutes'),
            ('30', '30 minutes'),
            ('45', '45 minutes'),
            ('60', '60 minutes'),
        ],
        default='30',
        blank=True,
        null=True
    )
    interview_question_count = models.IntegerField(
        choices=[
            (5, '5 questions'),
            (8, '8 questions'),
            (10, '10 questions'),
            (12, '12 questions'),
            (15, '15 questions'),
        ],
        default=8,
        blank=True,
        null=True
    )
    
    # Existing fields
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    def __str__(self):
        return self.title



class Application(models.Model):
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume = models.FileField(
        upload_to='applications/resumes/',
        help_text='Upload your resume in PDF, DOC, or DOCX format (max 5MB)',
        blank=False,
        null=False
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"
    



  
    
# class Interview(models.Model):
#     id = models.AutoField(primary_key=True)
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     job = models.ForeignKey(Job, on_delete=models.CASCADE)
#     candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     link = models.URLField(blank=True, null=True)
#     scheduled_at = models.DateTimeField()
#     transcript = models.TextField(blank=True, null=True)
#     summary = models.TextField(blank=True, null=True)
    
#     def __str__(self):
#         return f"Interview for {self.candidate.username} - {self.job.title} "

class Interview(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    job_position = models.ForeignKey('Job', on_delete=models.CASCADE)
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    candidate_name = models.CharField(max_length=255, default='Unknown Candidate')
    candidate_email = models.EmailField(default='unknown@example.com')
    interview_id = models.CharField(max_length=11, unique=True, blank=True)
    interview_link = models.URLField(max_length=500, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        if not self.interview_id:
            self.interview_id = self.generate_unique_id()
        if not self.interview_link:
            # Generate proper interview link using UUID
            self.interview_link = f"/interview/ready/{self.uuid}/"
        super().save(*args, **kwargs)

    def generate_unique_id(self):
        job_name = self.job_position.title.strip().lower()
        candidate = self.candidate_name.strip().lower()
        timestamp = str(int(time.time() * 1000000))  # microseconds
        raw_string = f"{job_name}{candidate}{timestamp}"
        hash_value = hashlib.md5(raw_string.encode()).hexdigest()
        hex_9 = hash_value[:9]
        formatted_id = f"{hex_9[:3]}-{hex_9[3:6]}-{hex_9[6:9]}"

        while Interview.objects.filter(interview_id=formatted_id).exists():
            timestamp = str(int(time.time() * 1000000))
            raw_string = f"{job_name}{candidate}{timestamp}"
            hash_value = hashlib.md5(raw_string.encode()).hexdigest()
            hex_9 = hash_value[:9]
            formatted_id = f"{hex_9[:3]}-{hex_9[3:6]}-{hex_9[6:9]}"
        return formatted_id
    

    


class Candidate(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='candidate_resumes/', blank=True, null=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.job.title}"        
 
        
    