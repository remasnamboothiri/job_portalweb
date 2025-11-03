"""
Email utilities for sending interview links to candidates
"""
import logging
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
import threading
import time

logger = logging.getLogger(__name__)

def send_interview_email_async(interview):
    """
    Send interview email in a separate thread to avoid blocking
    """
    def send_email():
        try:
            time.sleep(1)  # Small delay to ensure interview is saved
            send_interview_link_email(interview)
        except Exception as e:
            logger.error(f"Async email sending failed: {e}")
    
    thread = threading.Thread(target=send_email)
    thread.daemon = True
    thread.start()

def send_interview_link_email(interview):
    """
    Send interview link email to candidate with multiple fallback options
    """
    try:
        # Generate interview URL
        domain = getattr(settings, 'PRODUCTION_DOMAIN', 'job-portalweb-ga7b.onrender.com')
        if settings.DEBUG:
            domain = 'localhost:8000'
        
        protocol = 'https' if not settings.DEBUG else 'http'
        interview_url = f"{protocol}://{domain}/interview/ready/{interview.uuid}/"
        
        # Prepare email content
        context = {
            'candidate_name': interview.candidate_name,
            'job_title': interview.job.title,
            'company_name': interview.job.company,
            'interview_url': interview_url,
            'scheduled_date': interview.scheduled_at.strftime('%B %d, %Y at %I:%M %p') if interview.scheduled_at else 'To be confirmed',
            'interview_id': interview.interview_id,
        }
        
        # Create email subject and body
        subject = f"🎯 Interview Scheduled - {interview.job.title} at {interview.job.company}"
        
        # HTML email template
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                .interview-link {{ background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; font-weight: bold; }}
                .details {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Interview Scheduled!</h1>
                </div>
                <div class="content">
                    <h2>Hello {context['candidate_name']},</h2>
                    <p>Great news! Your interview has been scheduled for the <strong>{context['job_title']}</strong> position at <strong>{context['company_name']}</strong>.</p>
                    
                    <div class="details">
                        <h3>📋 Interview Details:</h3>
                        <ul>
                            <li><strong>Position:</strong> {context['job_title']}</li>
                            <li><strong>Company:</strong> {context['company_name']}</li>
                            <li><strong>Date & Time:</strong> {context['scheduled_date']}</li>
                            <li><strong>Interview ID:</strong> {context['interview_id']}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{context['interview_url']}" class="interview-link">
                            🚀 Start Your Interview
                        </a>
                    </div>
                    
                    <p><strong>Important Instructions:</strong></p>
                    <ul>
                        <li>Click the button above to access your interview</li>
                        <li>Make sure you have a stable internet connection</li>
                        <li>Test your microphone and camera beforehand</li>
                        <li>Find a quiet, well-lit space for the interview</li>
                        <li>Have your resume and any relevant documents ready</li>
                    </ul>
                    
                    <p>If you have any technical issues, please contact our support team.</p>
                    
                    <div class="footer">
                        <p>Best of luck with your interview!</p>
                        <p><strong>Job Portal Team</strong></p>
                        <hr>
                        <p style="font-size: 12px;">Interview Link: {context['interview_url']}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
Hello {context['candidate_name']},

🎉 Great news! Your interview has been scheduled.

📋 Interview Details:
• Position: {context['job_title']}
• Company: {context['company_name']}
• Date & Time: {context['scheduled_date']}
• Interview ID: {context['interview_id']}

🔗 Interview Link: {context['interview_url']}

👆 Click the link above to join your interview at the scheduled time.

Important Instructions:
- Make sure you have a stable internet connection
- Test your microphone and camera beforehand
- Find a quiet, well-lit space for the interview
- Have your resume and any relevant documents ready

If you have any technical issues, please contact our support team.

Best of luck with your interview!
Job Portal Team

=== INTERVIEW LINK ===
{context['interview_url']}
=== END LINK ===
        """
        
        # Try to send email with multiple methods
        email_sent = False
        
        # Method 1: Try HTML email
        try:
            msg = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[interview.candidate_email],
            )
            msg.content_subtype = "html"
            msg.send()
            email_sent = True
            logger.info(f"✅ HTML email sent successfully to {interview.candidate_email}")
        except Exception as e:
            logger.warning(f"HTML email failed: {e}")
        
        # Method 2: Fallback to plain text email
        if not email_sent:
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[interview.candidate_email],
                    fail_silently=False
                )
                email_sent = True
                logger.info(f"✅ Plain text email sent successfully to {interview.candidate_email}")
            except Exception as e:
                logger.warning(f"Plain text email failed: {e}")
        
        # Method 3: Console output (always works)
        logger.info(f"""
        ==========================================
        📧 EMAIL CONTENT FOR: {interview.candidate_email}
        ==========================================
        Subject: {subject}
        
        {plain_message}
        ==========================================
        🔗 COPY THIS LINK TO SEND MANUALLY:
        {context['interview_url']}
        ==========================================
        """)
        
        # Return result
        return {
            'success': email_sent,
            'interview_url': context['interview_url'],
            'email': interview.candidate_email,
            'method': 'email' if email_sent else 'console'
        }
        
    except Exception as e:
        logger.error(f"❌ Email sending completely failed for interview {interview.uuid}: {e}")
        
        # Emergency fallback - just log the link
        try:
            domain = getattr(settings, 'PRODUCTION_DOMAIN', 'job-portalweb-ga7b.onrender.com')
            if settings.DEBUG:
                domain = 'localhost:8000'
            protocol = 'https' if not settings.DEBUG else 'http'
            emergency_url = f"{protocol}://{domain}/interview/ready/{interview.uuid}/"
            
            logger.error(f"""
            ==========================================
            🚨 EMERGENCY INTERVIEW LINK
            ==========================================
            Candidate: {interview.candidate_email}
            Job: {interview.job.title}
            Link: {emergency_url}
            ==========================================
            """)
            
            return {
                'success': False,
                'interview_url': emergency_url,
                'email': interview.candidate_email,
                'method': 'emergency_log',
                'error': str(e)
            }
        except Exception as emergency_error:
            logger.error(f"Even emergency logging failed: {emergency_error}")
            return {
                'success': False,
                'error': str(e),
                'emergency_error': str(emergency_error)
            }

def send_bulk_interview_emails(interviews):
    """
    Send interview emails to multiple candidates
    """
    results = []
    for interview in interviews:
        result = send_interview_link_email(interview)
        results.append({
            'interview_id': interview.uuid,
            'candidate_email': interview.candidate_email,
            'result': result
        })
    return results

def test_email_configuration():
    """
    Test email configuration and return status
    """
    try:
        # Test basic email sending
        send_mail(
            subject='Test Email Configuration',
            message='This is a test email to verify email configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False
        )
        return {
            'success': True,
            'message': 'Email configuration is working',
            'backend': settings.EMAIL_BACKEND
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Email configuration error: {str(e)}',
            'backend': settings.EMAIL_BACKEND,
            'error': str(e)
        }

def get_email_settings_info():
    """
    Get current email settings information
    """
    return {
        'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', 'Not configured'),
        'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'Not configured'),
        'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 'Not configured'),
        'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', 'Not configured'),
        'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not configured'),
        'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'Not configured'),
        'EMAIL_HOST_PASSWORD': '***' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'Not configured',
    }