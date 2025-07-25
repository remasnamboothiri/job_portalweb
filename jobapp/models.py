from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from taggit.managers import TaggableManager
# from django.contrib.auth import get_user_model
# User = get_user_model()
import uuid



# Create your models here.

class CustomUser(AbstractUser):
    is_recruiter=models.BooleanField(default=False) # True = Recruiter, False = Job Seeker
    
    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    
class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()
    
    def __str__(self):
        return self.title
    

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Shortlisted', 'Shortlisted'),
    ('Rejected', 'Rejected'),
    ('Hired', 'Hiered'),
]



class Application(models.Model):
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='applications/resumes/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at =models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"
    
    
    
class Interview(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    link = models.URLField(blank=True, null=True)
    scheduled_at = models.DateTimeField()
    transcript = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Interview for {self.candidate.username} - {self.job.title} "
    

        
 
        
    