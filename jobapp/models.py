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
    
    ('active', 'Active'),
    ('closed', 'Closed'),
    ('expired', 'Expired'),
    ('filled', 'Position Filled'),
]

class Job(models.Model):
    # Basic Information
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(max_length=20000)
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
            ('5', '5 minutes'),
            ('10', '10 minutes'),
            ('15', '15 minutes'),
            ('20', '20 minutes'),
            ('30', '30 minutes'),
        ],
        default='15',
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
    
    # Add created_at and updated_at fields here
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    



  
    


class Interview(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # job_position = models.ForeignKey('Job', on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    
    # Make candidate optional - for registered users only
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    # These fields will store info for unregistered candidates
    candidate_name = models.CharField(max_length=255, default='Unknown Candidate')
    candidate_email = models.EmailField(default='unknown@example.com')
    candidate_phone = models.CharField(max_length=20, blank=True, null=True)  # Add phone field
    
    
    # Interview details
    interview_id = models.CharField(max_length=11, unique=True, blank=True)
    link = models.URLField(max_length=500, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    
    # Add status to track interview state
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Recording fields
    transcript = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    recording_data = models.TextField(blank=True, null=True, help_text="JSON data for recording information")
    recording_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to the recorded interview file")
    recording_duration = models.FloatField(blank=True, null=True, help_text="Duration of recording in seconds")
    is_recorded = models.BooleanField(default=False, help_text="Whether this interview was recorded")
    
    # Interview Results Fields
    questions_asked = models.TextField(blank=True, null=True, help_text="JSON data of questions asked during interview")
    answers_given = models.TextField(blank=True, null=True, help_text="JSON data of candidate answers")
    overall_score = models.FloatField(blank=True, null=True, help_text="Overall interview score out of 10")
    technical_score = models.FloatField(blank=True, null=True, help_text="Technical skills score out of 10")
    communication_score = models.FloatField(blank=True, null=True, help_text="Communication skills score out of 10")
    problem_solving_score = models.FloatField(blank=True, null=True, help_text="Problem solving score out of 10")
    ai_feedback = models.TextField(blank=True, null=True, help_text="AI-generated feedback about the candidate")
    recommendation = models.CharField(
        max_length=20,
        choices=[
            ('highly_recommended', 'Highly Recommended'),
            ('recommended', 'Recommended'),
            ('maybe', 'Maybe'),
            ('not_recommended', 'Not Recommended'),
        ],
        blank=True,
        null=True,
        help_text="AI recommendation for hiring"
    )
    completed_at = models.DateTimeField(blank=True, null=True, help_text="When the interview was completed")
    results_generated_at = models.DateTimeField(blank=True, null=True, help_text="When AI results were generated")
    started_at = models.DateTimeField(blank=True, null=True, help_text="When the interview session actually started")
    interview_duration_minutes = models.IntegerField(
        choices=[
            (5, '5 minutes'),
            (10, '10 minutes'),
            (15, '15 minutes'),
            (20, '20 minutes'),
            (30, '30 minutes'),
        ],
        default=15,
        help_text="Duration set by recruiter for this specific interview"
    )

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
            
        if not self.interview_id:
            self.interview_id = self.generate_unique_id()
            
        if not self.link:
            self.link = f"/interview/ready/{self.uuid}/"
                
        super().save(*args, **kwargs)

    def generate_unique_id(self):
        job_name = self.job.title.strip().lower()
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
    
    @property
    def get_uuid(self):
        """Get UUID safely"""
        return self.uuid
    
    
    @property
    def is_registered_candidate(self):
        """Check if candidate is a registered user"""
        return self.candidate is not None
    
    # @property
    # def has_results(self):
    #     """Check if interview has results generated"""
    #     return bool(self.overall_score or self.ai_feedback or self.recommendation)
    
    
    @property
    def has_results(self):
        """Check if interview has results generated"""
        # Check if ANY result field is present (not just truthy)
        return (
            self.overall_score is not None or 
            self.ai_feedback is not None and self.ai_feedback.strip() != '' or
            self.recommendation is not None and self.recommendation.strip() != '' or
            self.questions_asked is not None and self.questions_asked.strip() != '' or
            self.answers_given is not None and self.answers_given.strip() != ''
        )
    
    @property
    def is_completed(self):
        """Check if interview is completed"""
        return self.status == 'completed' and self.completed_at is not None
    
    def get_recommendation_display_color(self):
        """Get color class for recommendation display"""
        colors = {
            'highly_recommended': 'success',
            'recommended': 'info', 
            'maybe': 'warning',
            'not_recommended': 'danger'
        }
        return colors.get(self.recommendation, 'secondary')
    
    def mark_completed(self):
        """Mark interview as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    @property
    def is_expired(self):
        """Check if interview deadline has passed"""
        if not self.scheduled_at:
            return False
        return timezone.now() > self.scheduled_at
    
    @property
    def is_accessible(self):
        """Check if interview can still be accessed by candidate"""
        # Interview is not accessible if:
        # 1. It's already completed, OR
        # 2. The deadline has passed
        return not (self.is_completed or self.is_expired)
    
    def get_status_for_recruiter(self):
        """Get status display for recruiter dashboard"""
        if self.is_completed:
            return 'Completed'
        elif self.is_expired:
            return 'Expired'
        else:
            return 'Active'
    
    def get_status_color_class(self):
        """Get Bootstrap color class for status badge"""
        if self.is_completed:
            return 'bg-success'  # Green for completed
        elif self.is_expired:
            return 'bg-danger'   # Red for expired
        else:
            return 'bg-primary'  # Blue for active
    
    def __str__(self):
        return f"Interview for {self.job.title} - {self.candidate_name}"


    


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='candidate_resumes/', blank=True, null=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['email', 'added_by']  # Prevent duplicate candidates per recruiter
    
    def __str__(self):
        return f"{self.name} ({self.email})"        
 
        
    
    
# class Profile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=100)
#     contact = models.CharField(max_length=20)
#     resume = models.FileField(upload_to='resumes/')
#     profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    
#     def __str__(self):
#         return f"{self.user.username}'s Profile"


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
    