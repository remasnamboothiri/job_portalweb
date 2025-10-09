from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Application, Interview, Profile

# AUTOMATIC EMAIL SENDING WITH GMAIL SMTP
# Using threading and timeouts to prevent worker crashes

User = get_user_model()


# 1 . Registration  Email - TEMPORARILY DISABLED

# @receiver(post_save, sender = User)
# def send_registration_email(sender , instance , created, **kwargs):
#     if created:
#         try:
#             send_mail(
#                 subject="Welcome to Job Portal!",
#                 message="Hi {}, thanks for registering.".format(instance.username),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[instance.email],
#                 fail_silently=True
#             )
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Failed to send registration email to {instance.email}: {str(e)}")
        
        
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name or '',
            last_name=instance.last_name or '',
            email=instance.email or ''
        )
       
       
# 2. Application Submitted Email - TEMPORARILY DISABLED

# @receiver(post_save, sender = Application)
# def send_application_email(sender , instance , created , **kwargs):
#     if created:
#         try:
#             send_mail(
#                 subject="Your Application is Submitted",
#                 message="Hi {}, Your application to '{}' was submitted.".format(
#                     instance.applicant.username, instance.job.title),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[instance.applicant.email],
#                 fail_silently=True
#             )
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Failed to send application email to {instance.applicant.email}: {str(e)}")
        
        
#3 . Shortlisted Email - TEMPORARILY DISABLED

# @receiver(post_save, sender = Application)
# def send_shortlisted_email(sender, instance , created , **kwargs):
#     if instance.status == 'Shortlisted':
#         try:
#             send_mail(
#                 subject="You have been Shortlisted!",
#                 message="Hi {}, You have been Shortlisted for '{}'.".format(
#                     instance.applicant.username, instance.job.title),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[instance.applicant.email],
#                 fail_silently=True
#             )
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.warning(f"Failed to send shortlisted email to {instance.applicant.email}: {str(e)}")
        


# 4. Interview Scheduled Email - ENHANCED WITH MULTIPLE METHODS

@receiver(post_save, sender=Interview)
def send_interview_email(sender, instance, created, **kwargs):
    """Send interview email when interview is created"""
    if created:
        try:
            from .email_utils import send_interview_email_async
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info(f"📧 Sending interview email for {instance.candidate_email}")
            
            # Send email asynchronously to avoid blocking
            send_interview_email_async(instance)
            
            logger.info(f"✅ Interview email process initiated for {instance.candidate_email}")
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Interview email signal failed: {str(e)}")
            
            # Emergency fallback - generate link manually
            try:
                from django.conf import settings
                domain = getattr(settings, 'PRODUCTION_DOMAIN', 'job-portal-23qb.onrender.com')
                if settings.DEBUG:
                    domain = 'localhost:8000'
                protocol = 'https' if not settings.DEBUG else 'http'
                emergency_url = f"{protocol}://{domain}/interview/ready/{instance.uuid}/"
                
                logger.error(f"🚨 EMERGENCY LINK for {instance.candidate_email}: {emergency_url}")
            except Exception as emergency_error:
                logger.error(f"Even emergency link generation failed: {emergency_error}")