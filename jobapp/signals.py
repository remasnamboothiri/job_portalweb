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
        try:
            send_mail(
                subject="Welcome to Job Portal!",
                message="Hi {}, thanks for registering.".format(instance.username),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send registration email to {instance.email}: {str(e)}")
        
        
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name or '',
            last_name=instance.last_name or '',
            email=instance.email or ''
        )
       
       
# 2. Application Submitted Email 

@receiver(post_save, sender = Application)
def send_application_email(sender , instance , created , **kwargs):
    if created:
        try:
            send_mail(
                subject="Your Application is Submitted",
                message="Hi {}, Your application to '{}' was submitted.".format(
                    instance.applicant.username, instance.job.title),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.applicant.email],
                fail_silently=True
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send application email to {instance.applicant.email}: {str(e)}")
        
        
#3 . Shortlisted Email

@receiver(post_save, sender = Application)
def send_shortlisted_email(sender, instance , created , **kwargs):
    if instance.status == 'Shortlisted':
        try:
            send_mail(
                subject="You have been Shortlisted!",
                message="Hi {}, You have been Shortlisted for '{}'.".format(
                    instance.applicant.username, instance.job.title),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.applicant.email],
                fail_silently=True
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send shortlisted email to {instance.applicant.email}: {str(e)}")
        


# 4 . Interview Scheduled Email

@receiver(post_save, sender = Interview)
def send_interview_email(sender, instance, created, **kwargs):
    if created:
        try:
            send_mail(
                subject="Interview Scheduled",
                message="Hi {}, your Interview for '{}' is scheduled. \nlink: {}".format(
                    instance.candidate_name, instance.job.title, instance.link),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.candidate_email],
                fail_silently=True  # Don't crash if email fails
            )
        except Exception as e:
            # Log the error but don't crash the interview scheduling
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send interview email to {instance.candidate_email}: {str(e)}")
            # Interview scheduling continues even if email fails