from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Application , Interview , Profile

User = get_user_model()


# 1 . Registration  Email

@receiver(post_save, sender = User)
def send_registration_email(sender , instance , created, **kwargs):
    if created:
        send_mail(
            subject="Welcome to Job Portal!",
            message="Hi {}, thanks for registering.".format(instance.username),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
        )
        
        
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
       
       
# 2. Application Submitted Email 

@receiver(post_save, sender = Application)
def send_application_email(sender , instance , created , **kwargs):
    if created:
        send_mail(
            subject="Your Application is Submitted",
            message="Hi {}, Your application to '{}' was submitted.".format(
                instance.applicant.username, instance.job.title),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.applicant.email],
            )
        
        
#3 . Shortlisted Email

@receiver(post_save, sender = Application)
def send_shortlisted_email(sender, instance , created , **kwargs):
    if instance.status == 'Shortlisted':
        send_mail(
            subject="You have been Shortlisted!",
            message="Hi {}, You have been Shortlisted for '{}'.".format(
                instance.applicant.username, instance.job.title),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.applicant.email],
            
            
        )  
        


# 4 . Interview Schedued Emil

@receiver(post_save, sender = Interview)
def send_interview_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject="Interview Scheduled",
            message="Hi {}, your Interview for '{}' is scheduled. \nlink: {}".format(
                instance.candidate.username, instance.job.title, instance.link),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.candidate.email],
        )              
            
              