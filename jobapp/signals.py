from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Application , Interview , Profile

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
        


# 4 . Interview Scheduled Email - AUTOMATIC GMAIL SENDING

@receiver(post_save, sender = Interview)
def send_interview_email(sender, instance, created, **kwargs):
    if created:
        import threading
        import logging
        logger = logging.getLogger(__name__)
        
        def send_email_with_timeout():
            try:
                from django.conf import settings
                import socket
                
                # Set socket timeout to prevent hanging
                socket.setdefaulttimeout(10)
                
                # Generate full interview URL
                domain = 'job-portal-23qb.onrender.com' if not settings.DEBUG else 'localhost:8000'
                protocol = 'https' if not settings.DEBUG else 'http'
                interview_url = f"{protocol}://{domain}/interview/ready/{instance.uuid}/"
                
                email_subject = f'🎯 Interview Scheduled - {instance.job.title}'
                email_body = f"""Hello {instance.candidate_name},

🎉 Great news! Your interview has been scheduled.

📋 Interview Details:
• Date & Time: {instance.scheduled_at.strftime('%B %d, %Y at %I:%M %p') if instance.scheduled_at else 'TBD'}
• Position: {instance.job.title}
• Company: {instance.job.company}

🔗 Interview Link: {interview_url}

👆 Click the link above to join your interview at the scheduled time.

Best of luck!
Job Portal Team"""
                
                # Send email with timeout
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.candidate_email],
                    fail_silently=False,
                    timeout=10
                )
                
                logger.info(f"✅ EMAIL SENT SUCCESSFULLY to {instance.candidate_email}")
                logger.info(f"🔗 Interview link: {interview_url}")
                
            except Exception as e:
                logger.error(f"❌ Email failed: {str(e)}")
                logger.info(f"🔗 Manual link for {instance.candidate_email}: {interview_url}")
        
        # Send email in background thread with timeout
        email_thread = threading.Thread(target=send_email_with_timeout)
        email_thread.daemon = True
        email_thread.start()