from django.shortcuts import render,redirect, get_object_or_404 , HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, LoginForm , ProfileForm, JobForm, ApplicationForm, ScheduleInterviewForm , AddCandidateForm, ScheduleInterviewWithCandidateForm
from .models import CustomUser , Profile, Job, Application , Interview, Candidate
from django.contrib.auth.decorators import login_required , user_passes_test 
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden , JsonResponse, Http404, FileResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.middleware.csrf import CsrfViewMiddleware
from django.db.models import Q
from django.db import models
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
User = get_user_model()
from datetime import datetime
from django.contrib.auth import get_backends
from django.urls import reverse
import os
import uuid
import base64
import tempfile
from gtts import gTTS
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from jobapp.tts import generate_tts, generate_google_tts
import json
from django.conf import settings
import logging
from .health import health_check, readiness_check



# At the top of your views.py file, add:


import hashlib

 




from django.views.decorators.http import require_POST

from django.http import JsonResponse
from django.db import connection

from django.core.exceptions import FieldError
from django.views.static import serve

from django.core.mail import send_mail
from .email_utils import send_interview_link_email, test_email_configuration, get_email_settings_info
from django.core.mail import send_mail


from django.db import connection, transaction
from django.core.management import call_command
import json

# Configure logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def send_interview_status_email(interview, status_type):
    """Send email notification for interview status changes"""
    try:
        if status_type == 'expired':
            subject = f'Interview Deadline Passed - {interview.job.title}'
            message = f"""Dear {interview.candidate_name},

The deadline for your interview for the position of {interview.job.title} at {interview.job.company} has passed.

If you still wish to be considered for this position, please contact our HR team directly:

Email: hr@{interview.job.company.lower().replace(' ', '')}.com
Phone: +1-555-0123

Thank you for your interest in our company.

Best regards,
HR Team
{interview.job.company}"""
        
        elif status_type == 'completed':
            subject = f'Interview Completed - {interview.job.title}'
            message = f"""Dear {interview.candidate_name},

Thank you for completing your interview for the position of {interview.job.title} at {interview.job.company}.

Your interview has been successfully recorded and our team will review your responses. We will contact you with the next steps within 3-5 business days.

For any questions, please contact our HR team:

Email: hr@{interview.job.company.lower().replace(' ', '')}.com
Phone: +1-555-0123

Thank you for your time and interest in our company.

Best regards,
HR Team
{interview.job.company}"""
        
        else:
            return False
        
        # Send the email
        try:
            # Check if we're using console backend
            from django.conf import settings
            is_console_backend = 'console' in settings.EMAIL_BACKEND.lower()
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [interview.candidate_email],
                fail_silently=False  # Show email errors for debugging
            )
            
            if is_console_backend:
                logger.info(f"📧 Status email logged to console for {interview.candidate_email} (interview {interview.uuid}) - Type: {status_type}")
                logger.info(f"""
                ==========================================
                📧 EMAIL CONTENT (CONSOLE OUTPUT):
                ==========================================
                To: {interview.candidate_email}
                Subject: {subject}
                
                {message}
                ==========================================
                💡 NOTE: Email was sent to console. To send real emails, configure SMTP settings.
                """)
            else:
                logger.info(f"✅ Status email sent successfully to {interview.candidate_email} for interview {interview.uuid} - Type: {status_type}")
            
            return True
            
        except Exception as email_error:
            logger.error(f"❌ Email sending failed for {interview.candidate_email}: {email_error}")
            # Log the email content for manual sending if needed
            logger.info(f"""
            ==========================================
            📧 EMAIL CONTENT (FAILED TO SEND):
            ==========================================
            To: {interview.candidate_email}
            Subject: {subject}
            
            {message}
            ==========================================
            """)
            return False
        
    except Exception as e:
        logger.error(f"Failed to send status email for interview {interview.uuid}: {e}")
        return False


#for Ai interview
try:
    from .utils.interview_ai_nvidia import ask_ai_question 
    from jobapp.utils.resume_reader import extract_resume_text
    from .asr import transcribe_audio
except ImportError as e:
    print(f"Import error: {e}")
    def ask_ai_question(prompt, candidate_name=None, job_title=None, company_name=None , timeout=None):
        return "AI service is currently unavailable. Please try again later."
    def extract_resume_text(resume_file):
        return "Resume processing is currently unavailable."
    def transcribe_audio(audio_file):
        return {'success': False, 'text': '', 'error': 'ASR not available'}

from gtts import gTTS

from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.middleware.csrf import CsrfViewMiddleware
import uuid










# Create your views here.

def home_view(request):
    return render(request, 'jobapp/home.html')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user)
            return redirect('Profile_update')
        else:
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_recruiter:
                    return redirect('recruiter_dashboard')
                else:
                    return redirect('Profile_update')
            else:
                form.add_error(None, 'Invalid credentials')
        return render(request, 'registration/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})
# logout view 
def logout_view(request):
    logout(request)
    return redirect('login')  #redirect to login page after logout     


# profile update view
@login_required
def update_profile(request):
    try:
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'first_name': request.user.first_name or '',
                'last_name': request.user.last_name or '',
                'email': request.user.email or '',
                'phone': '',
                'location': '',
                'bio': '',
                'skills': ''
            }
        )
    except Exception as e:
        # Handle database schema mismatch
        messages.error(request, 'Profile system is being updated. Please try again later.')
        return redirect('jobseeker_dashboard')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('jobseeker_dashboard')
    else:
        form = ProfileForm(instance=profile)
        
    return render(request, 'jobapp/profile_update.html', {'form': form})
    


  


# post job view for recruiter only 
@login_required
def post_job(request):
    
    # Enhanced logging to track the job posting process
    logger.info(f"Post job accessed by user {request.user.id} (is_recruiter: {request.user.is_recruiter})")
    
    if not request.user.is_recruiter:
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('login')
        
    if request.method == 'POST':
        
        logger.info(f"POST request received for job posting by user {request.user.id}")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        logger.info(f"FILES data keys: {list(request.FILES.keys())}")
        
        form = JobForm(request.POST, request.FILES)
        
        # Log form data for debugging
        logger.info(f"Form data - title: {request.POST.get('title', 'Not provided')}")
        logger.info(f"Form data - company: {request.POST.get('company', 'Not provided')}")
        logger.info(f"Form data - location: {request.POST.get('location', 'Not provided')}")
        
        if form.is_valid():
            logger.info("Form is valid, attempting to save job...")
            try:
                job = form.save(commit=False)
                job.posted_by = request.user
            
            
            
                # Log job details before saving
                logger.info(f"Job details before save - Title: {job.title}, Company: {job.company}, Location: {job.location}")
                
                job.save()
            
                 # Verify the job was actually saved
                saved_job = Job.objects.filter(id=job.id).first()
                if saved_job:
                    logger.info(f"SUCCESS: Job saved successfully with ID {job.id}")
                    messages.success(request, f'Job "{job.title}" posted successfully!')
                    return redirect('job_list')
                else:
                    logger.error("ERROR: Job was not found in database after save attempt")
                    messages.error(request, 'Job was not saved properly. Please try again.')
            except Exception as e:
                logger.error(f"ERROR saving job: {str(e)}")
                logger.error(f"Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                messages.error(request, f'Error saving job: {str(e)}')       
        else:
            logger.error(f"Form validation failed: {form.errors}")
            # Display specific form errors to user
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form.fields[field].label if field in form.fields else field.title()
                        messages.error(request, f'{field_name}: {error}')    
            
            # If form is not valid, show errors
            messages.error(request, 'Please correct the errors below.')
    else:
        logger.info("GET request - showing empty job form") 
        form = JobForm()
        
    return render(request, 'jobapp/post_job.html', {'form': form})











# Job List view
def job_list(request):
    from django.core.paginator import Paginator
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    job_type_filter = request.GET.get('job_type', '')
    
    # Start with all jobs
    jobs = Job.objects.all().order_by('-date_posted')
    
    # Apply search filter
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)
    
    # Apply status filter
    if status_filter:
        if status_filter == 'open':
            jobs = jobs.filter(status='active')  # 'active' status means open jobs
        elif status_filter == 'closed':
            jobs = jobs.filter(status='closed')
    
    # Apply job type filter
    if job_type_filter:
        jobs = jobs.filter(employment_type=job_type_filter)
    
    # Pagination - 5 jobs per page
    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    no_results = not jobs.exists()

    return render(request, 'jobapp/job_list.html', {
        'jobs': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'no_results': no_results
    })

 



# Job Detail view
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if the logged-in user is a recruiter and owns this job
    is_recruiter = request.user.is_recruiter if request.user.is_authenticated else False
    is_job_owner = request.user.is_authenticated and job.posted_by == request.user
    
    context = {
        'job': job,
        'is_recruiter': is_recruiter,
        'is_job_owner': is_job_owner
    }
    return render(request, 'jobapp/job_detail.html', context)










@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Prevent duplicate application
    if Application.objects.filter(applicant=request.user, job=job).exists():
        return render(request, 'jobapp/already_applied.html', {'job': job})
    
    if request.method == 'POST' and request.POST.get('form_submitted'):
        logger.info(f"Application form submitted for job {job_id} by user {request.user.id}")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        logger.info(f"FILES data keys: {list(request.FILES.keys())}")
        logger.info(f"Resume file present: {'resume' in request.FILES}")
        
        if 'resume' in request.FILES:
            resume_file = request.FILES['resume']
            logger.info(f"Resume file details: name={resume_file.name}, size={resume_file.size}, content_type={resume_file.content_type}")
        
        form = ApplicationForm(request.POST, request.FILES)
        logger.info(f"Form data after initialization: {form.data}")
        logger.info(f"Form files after initialization: {form.files}")
        
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.applicant = request.user
                application.job = job
                application.save()
                
                logger.info(f"Application saved successfully for job {job_id} by user {request.user.id}")
                messages.success(request, f'Your application for {job.title} has been submitted successfully!')
                return redirect('jobseeker_dashboard')
                
            except Exception as e:
                logger.error(f"Error saving application for job {job_id}: {e}")
                messages.error(request, 'There was an error submitting your application. Please try again.')
        else:
            logger.error(f"Form validation failed for job {job_id}: {form.errors}")
            # Display form errors to user
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = 'Resume' if field == 'resume' else field.title()
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = ApplicationForm()
        
    # Handle case where form is submitted without the hidden field (shouldn't happen with proper form)
    if request.method == 'POST' and not request.POST.get('form_submitted'):
        logger.warning(f"Form submitted without form_submitted flag for job {job_id}")
        messages.warning(request, 'Please use the form below to submit your application.')
   
    return render(request, 'jobapp/apply_job.html', {'form': form, 'job': job})   




#job seeker Dashboard
@login_required
def jobseeker_dashboard(request):
    applications = Application.objects.filter(applicant=request.user)
    try:
        profile = Profile.objects.filter(user=request.user).first()
    except Exception:
        profile = None
    
    # Get scheduled interviews for this candidate
    scheduled_interviews = []
    try:
        # Try the primary query first
        scheduled_interviews = list(Interview.objects.filter(
            candidate=request.user
        ).select_related('job').order_by('-created_at'))
        
        logger.info(f"Found {len(scheduled_interviews)} interviews for user {request.user.username}")
        
    except Exception as e:
        logger.warning(f"Could not fetch interviews for user {request.user.id}: {e}")
        # Try alternative query method
        try:
            scheduled_interviews = list(Interview.objects.filter(
                candidate_id=request.user.id
            ).select_related('job').order_by('-created_at'))
            logger.info(f"Alternative query successful: {len(scheduled_interviews)} interviews")
        except Exception as e2:
            logger.warning(f"Alternative interview query also failed for user {request.user.id}: {e2}")
            scheduled_interviews = []
    
    # Debug logging
    logger.info(f"Dashboard for {request.user.username}: {len(applications)} applications, {len(scheduled_interviews)} interviews")
    
    return render(request, 'jobapp/jobseeker_dashboard.html', {
        'applications': applications, 
        'profile': profile,
        'scheduled_interviews': scheduled_interviews
    })        

# The old recruiter_dashboard function has been replaced with the cleaner version below

    
    
    
@require_POST
@login_required
@user_passes_test(lambda u: u.is_recruiter)
def update_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    status = request.POST.get('status')
    
    # Get valid status choices from the model
    valid_statuses = [choice[0] for choice in job._meta.get_field('status').choices]
    
    if status in valid_statuses:
        job.status = status
        job.save()
        messages.success(request, f"Job status updated to {status.replace('_', ' ').title()}.")
        logger.info(f"Job {job.id} status updated to {status} by user {request.user.username}")
    else:
        messages.error(request, "Invalid status selected.")
        logger.warning(f"Invalid status '{status}' attempted for job {job.id} by user {request.user.username}")
    
    return redirect('recruiter_dashboard')    




@login_required
def schedule_interview(request, job_id, applicant_id):
    from django.core.mail import send_mail
    from django.conf import settings
    
    logger.info(f"Schedule interview accessed by user {request.user.id} (is_recruiter: {request.user.is_recruiter}) for job {job_id}, applicant {applicant_id}")
    
    # Check if user is recruiter
    if not request.user.is_recruiter:
        logger.warning(f"Non-recruiter user {request.user.id} attempted to access schedule interview")
        messages.error(request, 'Only recruiters can schedule interviews.')
        return redirect('login')
    
    # Get the job and ensure the recruiter owns it
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    # Get the applicant
    applicant = get_object_or_404(User, id=applicant_id)
    
    if request.method == 'POST':
        form = ScheduleInterviewForm(request.POST, user=request.user)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.job = job
            interview.candidate = applicant  # Link the actual user
            interview.candidate_id = applicant.id  # Ensure candidate_id is set
            interview.save()
            
            # Send email to candidate with interview link
            try:
                email_subject = f'Interview Scheduled - {interview.job.title}'
                # Generate full interview URL
                from django.urls import reverse
                
                # Use production domain or localhost
                #domain = 'job-portal-23qb.onrender.com' if not settings.DEBUG else 'localhost:8000'
                domain = getattr(settings, 'PRODUCTION_DOMAIN', 'localhost:8000') if not settings.DEBUG else 'localhost:8000'
                protocol = 'https' if not settings.DEBUG else 'http'
                
                # Use get_uuid property for safe UUID access
                interview_uuid = interview.get_uuid
                interview_url = f"{protocol}://{domain}{reverse('interview_ready', args=[interview_uuid])}"
                
                email_body = f"""Hello {interview.candidate_name},

Your interview for the position of {interview.job.title} has been scheduled.

Interview Details:
- Date & Time: {interview.interview_date.strftime('%B %d, %Y at %I:%M %p')}
- Position: {interview.job.title}
- Company: {interview.job.company}
- Interview Link: {interview_url}

Please click the link above to start your interview at the scheduled time.
You can also find this link on your dashboard.

Best regards,
HR Team
{interview.job.company}"""
                
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [interview.candidate_email],
                    fail_silently=False  # Show email errors for debugging
                )
                messages.success(request, f'Interview scheduled successfully! Email sent to {interview.candidate_email} with interview link.')
            except Exception as e:
                logger.warning(f'Email sending failed for interview {interview.uuid}: {str(e)}')
                messages.warning(request, f'Interview scheduled successfully! Email could not be sent, but the candidate can see the interview link on their dashboard.')
            
            return redirect('recruiter_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate form with job and applicant data
        initial_data = {
            'job': job,
            'candidate_name': applicant.get_full_name() or applicant.username,
            'candidate_email': applicant.email,
        }
        form = ScheduleInterviewForm(initial=initial_data, user=request.user)
    
    return render(request, 'jobapp/schedule_interview.html', {
        'form': form,
        'job': job,
        'applicant': applicant
    })
    
    
    
    
#handle un registered users trying to access interview link 
@login_required
@user_passes_test(lambda u: u.is_recruiter)
def schedule_interview_simple(request):
    """Simple schedule interview for candidates added by recruiters"""
    from django.core.mail import send_mail
    from django.conf import settings
    from django.urls import reverse
    
    if request.method == 'POST':
        logger.info(f"Schedule interview form submitted by {request.user.username}")
        logger.info(f"POST data: {request.POST}")
        
        form = ScheduleInterviewForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                # Save the interview with additional error handling
                interview = form.save(commit=False)
                
                # Ensure all required fields are set
                if not interview.candidate_name:
                    interview.candidate_name = "Unknown Candidate"
                if not interview.candidate_email:
                    interview.candidate_email = "unknown@example.com"
                
                # Save the interview
                interview.save()
                logger.info(f"Interview created successfully: {interview.id}")
                
                # Email will be sent automatically (or check logs if using console backend)
                #interview_link = f'https://job-portal-23qb.onrender.com/interview/ready/{interview.uuid}/'
                domain = getattr(settings, 'PRODUCTION_DOMAIN', 'localhost:8000')
                protocol = 'https' if not settings.DEBUG else 'http'
                interview_link = f'{protocol}://{domain}/interview/ready/{interview.uuid}/'
                success_message = f'✅ Interview scheduled successfully! 📧 Email sent to {interview.candidate_email}. 🔗 Interview Link: {interview_link}'
                logger.info(f"✅ Interview scheduled for {interview.candidate_email}")
                logger.info(f"🔗 Interview Link: {interview_link}")
                logger.info(f"📧 Email sent to: {interview.candidate_email}")
                
                # Email will be sent via signal (printed to console/logs)
                # Interview link will also be displayed on dashboard for manual sharing
                
                # Return JSON response for AJAX (modal submission)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Interview scheduled successfully! Email sent to {interview.candidate_email}.',
                        'interview_id': interview.id,
                        'interview_link': interview_link,
                        'candidate_email': interview.candidate_email,
                        'candidate_name': interview.candidate_name,
                        'job_title': interview.job.title,
                        'scheduled_date': interview.scheduled_at.strftime('%B %d, %Y at %I:%M %p') if interview.scheduled_at else 'TBD'
                    })
                
                messages.success(request, success_message)
                return redirect('recruiter_dashboard')
                
            except Exception as e:
                logger.error(f"Error saving interview: {str(e)}")
                error_message = f'Error scheduling interview: {str(e)}'
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    })
                
                messages.error(request, error_message)
        else:
            logger.error(f"Form validation failed: {form.errors}")
            
            # Handle AJAX form submission (modal)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            error_messages.append(error)
                        else:
                            field_name = form.fields[field].label if field in form.fields else field.title()
                            error_messages.append(f'{field_name}: {error}')
                
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Please fix the following errors: ' + '; '.join(error_messages)
                })
            
            # Handle regular form submission
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form.fields[field].label if field in form.fields else field.title()
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = ScheduleInterviewForm(user=request.user)
    
    return render(request, 'jobapp/schedule_interview_simple.html', {
        'form': form
    })

@login_required
@user_passes_test(lambda u: u.is_recruiter) 
def schedule_interview_with_candidate(request, candidate_id):
    """Schedule interview with a specific candidate"""
    from django.core.mail import send_mail
    from django.conf import settings
    from django.urls import reverse
    
    # Get the candidate
    candidate = get_object_or_404(Candidate, id=candidate_id, added_by=request.user)
    
    if request.method == 'POST':
        logger.info(f"POST data received: {request.POST}")
        form = ScheduleInterviewWithCandidateForm(request.POST, user=request.user, candidate=candidate)
        
        logger.info(f"Form is bound: {form.is_bound}")
        logger.info(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            logger.error(f"Form errors: {form.errors}")
        
        if form.is_valid():
            try:
                logger.info(f"Form cleaned data: {form.cleaned_data}")
                interview = form.save(request.user)
                logger.info(f"Interview created successfully: {interview.id}")
                
                # Send email to candidate
                try:
                    #domain = 'job-portal-23qb.onrender.com' if not settings.DEBUG else 'localhost:8000'
                    domain = getattr(settings, 'PRODUCTION_DOMAIN', 'localhost:8000') if not settings.DEBUG else 'localhost:8000'
                    protocol = 'https' if not settings.DEBUG else 'http'
                    interview_url = f"{protocol}://{domain}{reverse('interview_ready', args=[interview.uuid])}"
                    
                    email_subject = f'Interview Scheduled - {interview.job.title}'
                    email_body = f"""Hello {interview.candidate_name},

Your interview for the position of {interview.job.title} has been scheduled.

Interview Details:
- Date & Time: {interview.scheduled_at.strftime('%B %d, %Y at %I:%M %p')}
- Position: {interview.job.title}
- Company: {interview.job.company}
- Interview Link: {interview_url}

Please click the link above to join your interview at the scheduled time.

Best regards,
{request.user.get_full_name() or request.user.username}
{interview.job.company}"""
                    
                    send_mail(
                        email_subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [interview.candidate_email],
                        fail_silently=False
                    )
                    
                    messages.success(request, f'Interview scheduled successfully! Email sent to {interview.candidate_email}.')
                    logger.info(f"Email sent successfully to {interview.candidate_email}")
                    
                except Exception as e:
                    logger.warning(f'Email sending failed: {str(e)}')
                    messages.warning(request, 'Interview scheduled successfully! Email could not be sent.')
                
                return redirect('recruiter_dashboard')
                
            except Exception as e:
                logger.error(f"Error saving interview: {str(e)}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                messages.error(request, f'Error scheduling interview: {str(e)}')
        else:
            logger.error(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ScheduleInterviewWithCandidateForm(user=request.user, candidate=candidate)
    
    return render(request, 'jobapp/schedule_interview_with_candidate.html', {
        'form': form,
        'candidate': candidate
    })    
    




# interview_ready function view
def interview_ready(request, interview_uuid):
    """
    Display the interview ready page before starting the actual AI interview
    """
    try:
        # Get the interview record
        interview = get_object_or_404(Interview, uuid=interview_uuid)
        
        # Check if interview is completed
        if interview.is_completed:
            # Send completion email if not sent already
            send_interview_status_email(interview, 'completed')
            return HttpResponse(
                f'<div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">'
                f'<h2>Interview Already Completed</h2>'
                f'<p>Dear {interview.candidate_name},</p>'
                f'<p>You have already completed your interview for <strong>{interview.job.title}</strong> at <strong>{interview.job.company}</strong>.</p>'
                f'<p>Our team will review your responses and contact you with the next steps within 3-5 business days.</p>'
                f'<p>An email confirmation has been sent to <strong>{interview.candidate_email}</strong>.</p>'
                f'<p>Thank you for your time and interest in our company.</p>'
                f'</div>'
            )
        
        # Check if interview deadline has passed
        if interview.is_expired:
            # Send expiration email
            send_interview_status_email(interview, 'expired')
            return HttpResponse(
                f'<div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">'
                f'<h2>Interview Deadline Passed</h2>'
                f'<p>Dear {interview.candidate_name},</p>'
                f'<p>The deadline for your interview for <strong>{interview.job.title}</strong> at <strong>{interview.job.company}</strong> has passed.</p>'
                f'<p>The interview was scheduled to be completed by: <strong>{interview.scheduled_at.strftime("%B %d, %Y at %I:%M %p")}</strong></p>'
                f'<p>If you still wish to be considered for this position, please contact our HR team directly.</p>'
                f'<p>An email with contact information has been sent to <strong>{interview.candidate_email}</strong>.</p>'
                f'</div>'
            )
        
        # Interview is accessible - show normal ready page
        return render(request, 'jobapp/interview_ready.html', {
            'interview': interview,
        })
        
    except Exception as e:
        logger.error(f"Interview Ready Error: {e}")
        return HttpResponse(f'Interview ready page could not be loaded. Error: {str(e)}', status=500)






            
            
            
            
#interview function
@csrf_exempt
def start_interview_by_uuid(request, interview_uuid):
    try:
        # Get the interview record
        interview = get_object_or_404(Interview, uuid=interview_uuid)
        
        # Check if interview is accessible (not expired or completed)
        if not interview.is_accessible:
            if interview.is_completed:
                send_interview_status_email(interview, 'completed')
                return JsonResponse({
                    'error': 'Interview already completed',
                    'message': 'This interview has already been completed. An email confirmation has been sent.',
                    'redirect': True
                })
            elif interview.is_expired:
                send_interview_status_email(interview, 'expired')
                return JsonResponse({
                    'error': 'Interview deadline passed',
                    'message': 'The deadline for this interview has passed. Please contact HR for further assistance.',
                    'redirect': True
                })
        
        
        # Interview is accessible - proceed with normal flow
        # Handle both registered and unregistered candidates
        if interview.is_registered_candidate:
            candidate_name = interview.candidate.get_full_name() or interview.candidate.username
            job_title = interview.job.title or "Software Developer"
            
            profile = getattr(interview.candidate, 'profile', None)
            resume_file = profile.resume if profile and profile.resume else None
            resume_text = ""
            
            if resume_file:
                try:
                    # Open the file properly before passing to extract_resume_text
                    with resume_file.open('rb') as file_obj:
                        resume_text = extract_resume_text(file_obj)
                except Exception as e:
                    resume_text = "Resume could not be processed."
                    logger.warning(f"Resume extraction error for interview {interview_uuid}: {e}")
            else:
                resume_text = f"Candidate: {candidate_name}, applying for {job_title} position."
                
        else:
            candidate_name = interview.candidate_name or "the candidate"
            job_title = interview.job.title if interview.job else "Software Developer"
            
            # Try to find the candidate resume from the Candidate model
            candidate_resume = None
            try:
                # Find the candidate by email and recruiter
                from .models import Candidate
                candidate_obj = Candidate.objects.filter(
                    email=interview.candidate_email,
                    added_by=interview.job.posted_by
                ).first()
                
                if candidate_obj and candidate_obj.resume:
                    candidate_resume = candidate_obj.resume
                    logger.info(f"Found resume for unregistered candidate {candidate_name}")
            except Exception as e:
                logger.warning(f"Could not find candidate resume: {e}")
            
            if candidate_resume:
                try:
                    # Open the file properly before passing to extract_resume_text
                    with candidate_resume.open('rb') as resume_file:
                        resume_text = extract_resume_text(resume_file)
                    logger.info(f"Successfully extracted resume text for {candidate_name}")
                except Exception as e:
                    resume_text = f"Resume could not be processed for {candidate_name}."
                    logger.warning(f"Resume extraction error for unregistered candidate in interview {interview_uuid}: {e}")
            else:
                resume_text = f"Candidate: {candidate_name}"
                if hasattr(interview, 'candidate_email') and interview.candidate_email:
                    resume_text += f", Email: {interview.candidate_email}"
                if hasattr(interview, 'candidate_phone') and interview.candidate_phone:
                    resume_text += f", Phone: {interview.candidate_phone}"
                resume_text += f", applying for {job_title} position."
        # job detail extraction
        try:
            company_name = interview.job.company if interview.job else "Our Company"
        except AttributeError:
            company_name = "Our Company"

        if not resume_text.strip():
            return HttpResponse(
                "Resume information not found. Please ensure your resume is uploaded or contact support.", 
                status=400
            )
        
        # Use unique session key per interview
        session_key = f'interview_context_{interview_uuid}'
        
        # CRITICAL FIX: Only initialize session if it doesn't exist (don't reset on every request)
        if session_key not in request.session:
            logger.info(f"Creating new session context for interview {interview_uuid}")
            # Set the actual start time in the database when interview begins
            if not interview.started_at:
                interview.started_at = timezone.now()
                interview.save(update_fields=['started_at'])
                logger.info(f"Interview {interview_uuid} started at {interview.started_at}")
            
            request.session[session_key] = {
                'candidate_name': candidate_name,
                'job_title': job_title,
                'company_name': company_name,
                'resume_text': resume_text,
                'job_description': interview.job.description if interview.job else "",
                'job_location': interview.job.location if interview.job else "",
                'question_count': 0,
                'is_registered_candidate': interview.is_registered_candidate,
                'conversation_history': [],
                'started_at': timezone.now().isoformat(),
                'interview_completed': False,
                'interview_duration_minutes': interview.interview_duration_minutes or 15  # Use actual duration or default to 15
            }
            request.session.modified = True
        else:
            logger.info(f"Using existing session context for interview {interview_uuid}")
        
        # HANDLE POST REQUEST - Process candidate responses
        if request.method == "POST":
            try:
                user_text = ""
                time_remaining = 900
                
                # Check if audio file was uploaded (Whisper ASR mode)
                if 'audio' in request.FILES:
                    audio_file = request.FILES['audio']
                    logger.info(f"🎤 Audio file received: {audio_file.name} ({audio_file.size} bytes)")
                    
                    # Transcribe audio to text using Whisper
                    transcription_result = transcribe_audio(audio_file)
                    
                    if transcription_result['success']:
                        user_text = transcription_result['text']
                        logger.info(f"✅ Whisper transcription: {user_text}")
                        
                        # Get time_remaining from form data
                        try:
                            time_remaining = int(request.POST.get("time_remaining", 900))
                        except (ValueError, TypeError):
                            time_remaining = 900
                    else:
                        logger.error(f"❌ Whisper transcription failed: {transcription_result['error']}")
                        return JsonResponse({
                            'error': 'Server-side speech recognition not available. Please use Chrome or Edge browser.',
                            'response': 'Please use Chrome or Edge browser for speech recognition, or type your response.',
                            'audio': '',
                            'audio_duration': 3.0,
                            'success': False,
                            'transcription_error': transcription_result['error']
                        })
                
                # Handle text input (existing Web Speech API mode)
                elif request.content_type == 'application/json':
                    data = json.loads(request.body)
                    user_text = data.get("text") or data.get("message")
                    time_remaining = int(data.get("time_remaining", 900))
                else:
                    user_text = request.POST.get("text", "")
                    try:
                        time_remaining = int(request.POST.get("time_remaining", 900))
                    except (ValueError, TypeError):
                        time_remaining = 900
                        
            except Exception as e:
                logger.error(f"Error parsing request data: {e}")
                user_text = request.POST.get("text", "")
                time_remaining = 900  # Default 15 minutes
                
            # LOG for debugging
            logger.info(f"Parsed time_remaining: {time_remaining} seconds ({time_remaining/60:.1f} minutes)")
    
            if not user_text.strip():
                return JsonResponse({
                    'error': 'Please provide a response.',
                    'response': 'I didn\'t receive your answer. Could you please respond?',
                    'audio': '',
                    'audio_duration': 3.0,
                    'success': False
                })
    
            logger.info(f"User input for interview {interview_uuid}: {user_text[:100]}... (Time remaining: {time_remaining}s)")
    
            # Get current context
            context = request.session.get(session_key, {})
            logger.info(f"Retrieved session context: {context.keys() if context else 'None'}")
            logger.info(f"Current question count in context: {context.get('question_count', 'Not found')}")
            logger.info(f"Interview completed flag: {context.get('interview_completed', 'Not found')}")
            
            # Check if interview is already completed
            if context.get('interview_completed', False):
                logger.warning(f"Interview {interview_uuid} already marked as completed, returning completion message")
                return JsonResponse({
                    'error': 'Interview already completed',
                    'response': 'Thank you! Your interview has been completed.',
                    'audio': '',
                    'audio_duration': 2.0,
                    'is_final': True,
                    'success': True
                })
    
            # Prevent duplicate processing - but be more lenient
            last_processed = context.get('last_processed_input', '')
            current_input_hash = hashlib.md5(user_text.encode()).hexdigest()
            
            # Only block if it's EXACTLY the same AND was processed within last 5 seconds
            last_processed_time = context.get('last_processed_time', 0)
            current_time = timezone.now().timestamp()
            time_since_last = current_time - last_processed_time
            
            if last_processed == current_input_hash and time_since_last < 5:
                logger.warning(f"Duplicate request detected for interview {interview_uuid} (within 5s), ignoring")
                return JsonResponse({
                    'error': 'Duplicate request detected',
                    'response': 'Please wait for the previous response to complete.',
                    'audio': '',
                    'audio_duration': 2.0,
                    'success': False
                })
    
            context['last_processed_input'] = current_input_hash
            context['last_processed_time'] = current_time
            
            logger.info(f"Processing new response (hash: {current_input_hash[:8]}...)")
    
            # Get current question count and increment
            current_count = context.get('question_count', 0)
            question_count = current_count + 1
    
            # Save incremented count back to session IMMEDIATELY
            context['question_count'] = question_count
            request.session[session_key] = context
            request.session.modified = True
    
            logger.info(f"Question count incremented from {current_count} to {question_count} for interview {interview_uuid}")
    
            # Check if this should be the last question (2 minutes or less remaining)
            is_last_question = time_remaining <= 120  # 2 minutes = 120 seconds
            is_time_up = time_remaining <= 30  # 30 seconds or less
            
            # LOG the decision logic
            logger.info(f"Interview timing check - Time: {time_remaining}s, Last Question: {is_last_question}, Time Up: {is_time_up}")
    
            # FIXED: Better audio issue detection
            user_text_lower = user_text.lower().strip()
            
            simple_audio_phrases = [
                'can you hear me', 'can you hear me can you hear me',
                'hello can you hear me', 'can you hear', 'audio test', 'hello hello',
                'testing testing', 'test test', 'hello', 'testing', 'test',
                'i am can you hear me', 'hello hello hello', 'hello mam can you hear me',
                'can you hear me mam', 'hello mam', 'mam can you hear me'
            ]
            
            # More precise audio issue detection - must be exact match and short
            is_simple_audio_issue = (
                any(phrase == user_text_lower for phrase in simple_audio_phrases) and 
                len(user_text_lower) <= 30  # Must be short
            )
            
            # Build conversation history
            conversation_history = context.get('conversation_history', [])
            
            # Only add to conversation history if it's not a simple audio test
            if not is_simple_audio_issue:
                conversation_history.append({
                    'speaker': 'candidate',
                    'message': user_text,
                    'question_number': question_count,
                    'timestamp': timezone.now().isoformat(),
                    'time_remaining': time_remaining
                })
            else:
                logger.info(f"Skipping conversation history for audio test: {user_text}")
                # For audio tests, don't increment question count
                context['question_count'] = max(0, context.get('question_count', 0) - 1)
                question_count = context['question_count']
            
            logger.info(f"Content analysis - Audio issue: {is_simple_audio_issue}, User text: '{user_text_lower}'")
            
            # Generate AI response - WRAP IN TRY-CATCH
            logger.info(f"About to generate AI response - Audio issue: {is_simple_audio_issue}, Time up: {is_time_up}, Last question: {is_last_question}")
            try:
                if is_time_up:
                    # Time is up - end the interview
                    ai_response = f"Thank you so much for your time today, {candidate_name}! We've covered a lot of ground in our conversation. I really enjoyed learning about your background, skills, and experiences. Your insights have been valuable, and we appreciate your interest in the {job_title} position at {company_name}. Our team will review everything we discussed and get back to you with next steps within 2-3 business days. Have a wonderful day!"
                    
                    context['interview_completed'] = True
                    # Mark interview as completed in database
                    interview.status = 'completed'
                    interview.completed_at = timezone.now()
                    # Ensure started_at is set if not already
                    if not interview.started_at:
                        interview.started_at = timezone.now() - timezone.timedelta(minutes=15)  # Estimate 15 minutes ago
                    interview.save()
                    logger.info(f"Interview time completed for {interview_uuid}")
                    
                    # Generate interview results immediately
                    try:
                        generate_interview_results(interview, conversation_history)
                        logger.info(f"Interview results generated for {interview_uuid}")
                    except Exception as e:
                        logger.error(f"Failed to generate interview results: {e}")
                    
                elif is_last_question:
                    # 2 minutes or less - notify this is the last question
                    follow_up_questions = [
                        f"We're coming to the end of our time together, {candidate_name}. For my final question: Is there anything important about your skills, experience, or qualifications that we haven't discussed yet that you'd like me to know about?",
                        
                        f"This will be our last question today, {candidate_name}. Before we wrap up: What makes you particularly excited about this {job_title} opportunity, and why do you think you'd be a great fit for our team at {company_name}?",
                        
                        f"We have just a couple of minutes left, {candidate_name}. As a final question: If you were to start in this role next week, what would be your top priority in your first 30 days?",
                        
                        f"For our final question today, {candidate_name}: What's one professional achievement you're most proud of, and what did you learn from that experience?",
                    ]
                    
                    import random
                    ai_response = random.choice(follow_up_questions)
                    logger.info(f"Last question triggered for interview {interview_uuid} with {time_remaining}s remaining")
                    
                elif is_simple_audio_issue:
                    # Audio test response - DON'T increment question count for audio tests
                    ai_response = f"Yes, I can hear you perfectly, {candidate_name}! Your audio is crystal clear and you sound great. I'm Sarah, and I'm so excited to get to know you better today! Let's dive in - could you tell me about your background, your experience with {job_title} work, and what specifically drew you to apply for this position with {company_name}?"
                    
                    # CRITICAL FIX: Reset question count for audio issues to prevent premature completion
                    context['question_count'] = 0  # Reset to 0 for audio tests
                    question_count = 0
                    logger.info(f"Audio test detected - resetting question count to {question_count}")
                    
                else:
                    # Generate intelligent follow-up questions based on candidate's response and conversation flow
                    logger.info(f"Generating conversational response for question {question_count}")
                    
                    try:
                        # Get conversation context and candidate's responses
                        candidate_last_response = ""
                        previous_topics = []
                        candidate_responses = []
                        
                        if conversation_history:
                            for entry in conversation_history:
                                if entry['speaker'] == 'candidate':
                                    candidate_responses.append(entry['message'])
                                    candidate_last_response = entry['message']  # Keep updating to get the latest
                                elif entry['speaker'] == 'interviewer':
                                    # Extract topics already covered
                                    msg_lower = entry['message'].lower()
                                    if any(word in msg_lower for word in ['technical', 'technology', 'programming', 'language']):
                                        previous_topics.append('technical_skills')
                                    if any(word in msg_lower for word in ['project', 'built', 'developed']):
                                        previous_topics.append('projects')
                                    if any(word in msg_lower for word in ['team', 'collaborate', 'work together']):
                                        previous_topics.append('teamwork')
                                    if any(word in msg_lower for word in ['goal', 'future', 'career']):
                                        previous_topics.append('career_goals')
                        
                        # Build comprehensive context for AI conversation
                        conversation_summary = "\n".join([f"- {resp[:150]}..." for resp in candidate_responses[-3:]]) if candidate_responses else "No previous responses"
                        
                        conversation_context = f"""
INTERVIEW CONTEXT:
Candidate: {candidate_name}
Position: {job_title} at {company_name}
Question #{question_count}
Topics covered: {', '.join(set(previous_topics)) if previous_topics else 'None yet'}

CANDIDATE'S RECENT RESPONSES:
{conversation_summary}

LATEST RESPONSE: "{candidate_last_response}"

As Sarah, respond to what they just shared. Acknowledge their answer, show genuine interest, and ask a follow-up question that builds naturally on what they said. Focus on their experience, skills, and fit for the {job_title} role.
"""
                        
                        # Use AI to generate contextual response
                        try:
                            ai_response = ask_ai_question(
                                conversation_context,
                                candidate_name=candidate_name,
                                job_title=job_title,
                                company_name=company_name,
                                timeout=15
                            )
                            
                            # Clean and validate the AI response
                            if ai_response:
                                # Remove any quotes or formatting that might have slipped through
                                ai_response = ai_response.replace('"', '').replace("'", "").strip()
                                
                                # Ensure it's not too long
                                if len(ai_response) > 350:
                                    sentences = ai_response.split('. ')
                                    if len(sentences) > 1:
                                        ai_response = sentences[0] + '. ' + sentences[1] + '.'
                                    else:
                                        ai_response = ai_response[:347] + "..."
                                
                                # Ensure it ends properly
                                if not ai_response.endswith(('?', '.', '!')):
                                    ai_response += "?"
                                
                                logger.info(f"Generated AI conversational response: {ai_response[:100]}...")
                            else:
                                raise Exception("AI returned empty response")
                            
                        except Exception as ai_error:
                            logger.warning(f"AI response generation failed: {ai_error}, using fallback")
                            
                            # Enhanced fallback responses that acknowledge candidate's input
                            response_lower = candidate_last_response.lower()
                            
                            
                            # This logic ONLY runs when the AI fails (as a fallback)
                            
                            # Analyze candidate's response for emotional tone and content
                            if any(word in response_lower for word in ['nervous', 'anxious', 'worried', 'scared']):
                                ai_response = f"I completely understand, {candidate_name}. Interviews can feel nerve-wracking, but you're doing fantastic! Let's keep this conversational and relaxed. "
                            elif any(word in response_lower for word in ['excited', 'passionate', 'love', 'enjoy', 'enthusiastic']):
                                ai_response = f"I can really hear the passion in your voice, {candidate_name}! That enthusiasm is exactly what we love to see. "
                            elif any(word in response_lower for word in ['challenge', 'difficult', 'problem', 'struggle']):
                                ai_response = f"That sounds like a great learning experience, {candidate_name}. I appreciate you sharing that challenge with me. "
                            else:
                                ai_response = f"Thank you for sharing that, {candidate_name}. That's really insightful! "
                            
                            # Add contextual follow-up based on question progression and content
                            if question_count <= 3:
                                # ICE-BREAKING QUESTIONS (First 3 questions to make candidate comfortable)
                                if question_count == 1:
                                    ai_response += f"Nice to meet you! How are you feeling today?"
                                elif question_count == 2:
                                    ai_response += f"Great! Now that we're getting to know each other, are you ready to start our interview for the {job_title} position at {company_name}?"
                                else:  # question_count == 3
                                    ai_response += f"Perfect! Let's begin. Could you tell me a bit about yourself and what drew you to apply for this {job_title} role?"
                            
                            elif question_count <= 4:
                                if any(word in response_lower for word in ['python', 'javascript', 'java', 'react', 'django', 'node', 'html', 'css', 'sql']):
                                    ai_response += "Excellent technical foundation! Can you walk me through a specific project where you used these technologies? I'm particularly interested in any challenges you faced and how you overcame them."
                                elif any(word in response_lower for word in ['project', 'built', 'created', 'developed', 'application', 'website']):
                                    ai_response += "That sounds like a fascinating project! What was the most challenging technical problem you encountered while building it, and how did you approach solving it?"
                                elif any(word in response_lower for word in ['framework', 'library', 'tool', 'database']):
                                    ai_response += "Great choice of technologies! Can you describe a specific project where you implemented these tools? What made you choose them for that particular solution?"
                                else:
                                    ai_response += "I'd love to hear about a project you've worked on that you're particularly proud of. Can you walk me through the technical challenges and how you solved them?"
                            #Techniacal questions
                            elif question_count <= 6:
                                if any(word in response_lower for word in ['team', 'collaborate', 'group', 'together', 'pair']):
                                    ai_response += "Collaboration is so crucial in development! Can you give me an example of a time when you had to work through a technical disagreement with a team member? How did you handle it?"
                                elif any(word in response_lower for word in ['problem', 'challenge', 'difficult', 'bug', 'issue', 'debug']):
                                    ai_response += "Great problem-solving approach! How do you typically approach debugging complex issues, especially when working with a team? Do you have a systematic process?"
                                elif any(word in response_lower for word in ['agile', 'scrum', 'methodology', 'process']):
                                    ai_response += "Excellent experience with development methodologies! How do you handle changing requirements or tight deadlines while maintaining code quality?"
                                else:
                                    ai_response += "How do you approach working in team environments, especially when collaborating on complex technical projects? Can you share an example?"
                            #Advanced
                            else:
                                if any(word in response_lower for word in ['goal', 'future', 'career', 'grow', 'learn', 'aspiration']):
                                    ai_response += f"I love hearing about career aspirations! What specifically excites you about this {job_title} role at {company_name}, and how does it align with your professional goals?"
                                elif any(word in response_lower for word in ['company', 'role', 'position', 'opportunity', 'culture']):
                                    ai_response += "That's exactly the kind of thinking we value! Do you have any questions about the day-to-day responsibilities, our team dynamics, or the company culture?"
                                elif any(word in response_lower for word in ['technology', 'innovation', 'cutting-edge', 'latest']):
                                    ai_response += f"Your interest in technology trends is great! How do you stay updated with the latest developments in {job_title}, and what emerging technologies are you most excited about?"
                                else:
                                    ai_response += f"What draws you most to this {job_title} position at {company_name}? What aspects of the role or our company culture interest you the most?"
                        
                    except Exception as qgen_error:
                        logger.error(f"Error generating conversational response: {qgen_error}")
                        # Enhanced fallback that's more engaging and job-focused
                        ai_response = f"Thank you for sharing that, {candidate_name}. That's really valuable insight! I'd love to learn more about your passion for {job_title} work. What aspects of technology and development motivate you most, and how do you see yourself contributing to our team?"
            
            except Exception as response_gen_error:
                logger.error(f"CRITICAL: Error generating AI response: {response_gen_error}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                ai_response = f"Thank you for that response, {candidate_name}. Could you tell me more about your background and experience?"
                # Mark as completion error to prevent interview from ending
                context['interview_completed'] = False
            
            logger.info(f"AI response generated successfully ({len(ai_response)} chars)")

    
            # Add AI response to history (skip for audio tests)
            if not is_simple_audio_issue:
                conversation_history.append({
                    'speaker': 'interviewer', 
                    'message': ai_response,
                    'question_number': question_count,
                    'timestamp': timezone.now().isoformat(),
                    'time_remaining': time_remaining
                })
            else:
                logger.info(f"Skipping AI response history for audio test response")
    
            # Keep conversation history manageable
            if len(conversation_history) > 40:
                conversation_history = conversation_history[-40:]
                
            context['conversation_history'] = conversation_history
            
            # Generate interview results if completed (but not already generated)
            if context.get('interview_completed', False) and not interview.has_results:
                try:
                    generate_interview_results(interview, conversation_history)
                    logger.info(f"Interview results generation completed for {interview_uuid}")
                except Exception as e:
                    logger.error(f"Failed to generate interview results for {interview_uuid}: {e}")
            
            # CRITICAL FIX: Don't complete interview unless time is actually up or we have substantial conversation
            elif question_count >= 15 and time_remaining > 60:  # Only complete if we have many questions AND time is running out
                logger.info(f"Interview has {question_count} questions but {time_remaining}s remaining - continuing interview")
                # Don't complete yet, let time run out naturally
            
            # Save updated context
            request.session[session_key] = context
            request.session.modified = True
        
            # Generate TTS audio for the response
            audio_path = None
            audio_duration = None
            try:
                logger.info(f"Starting TTS generation for interview {interview_uuid}")
                
                from jobapp.tts import generate_tts, estimate_audio_duration, get_audio_duration
                
                # Always try Daisy TTS first
                audio_path = generate_tts(ai_response, "female_interview")
                
                if audio_path and audio_path != 'None':
                    try:
                        full_audio_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                        if os.path.exists(full_audio_path):
                            actual_duration = get_audio_duration(full_audio_path)
                            
                            if actual_duration and actual_duration > 0:
                                audio_duration = actual_duration
                                logger.info(f"Using actual audio duration: {audio_duration:.2f} seconds")
                            else:
                                audio_duration = estimate_audio_duration(ai_response)
                                logger.info(f"Using estimated audio duration: {audio_duration:.2f} seconds")
                        else:
                            logger.warning(f"Audio file not found: {full_audio_path}")
                            audio_path = None
                            audio_duration = estimate_audio_duration(ai_response)
                    except Exception as duration_error:
                        logger.error(f"Error getting audio duration: {duration_error}")
                        audio_duration = estimate_audio_duration(ai_response)
                else:
                    logger.info("No audio path returned from TTS generation")
                    audio_path = None
                    audio_duration = estimate_audio_duration(ai_response)
                    
            except Exception as e:
                logger.error(f"TTS generation failed for interview {interview_uuid}: {e}")
                audio_path = None
                try:
                    from jobapp.tts import estimate_audio_duration
                    audio_duration = estimate_audio_duration(ai_response)
                except:
                    audio_duration = max(6.0, len(ai_response) * 0.05)
    
            # Ensure we have a valid duration
            if not audio_duration or audio_duration <= 0:
                audio_duration = max(3.0, len(ai_response) * 0.05)
    
            # Return response data
            response_data = {
                'response': ai_response,
                'audio': audio_path if audio_path else '',
                'audio_duration': audio_duration,
                'success': True,
                'question_count': question_count,
                'is_final': context.get('interview_completed', False),
                'has_audio': bool(audio_path),
                'interview_completed': context.get('interview_completed', False),
                'time_remaining': time_remaining
            }
    
            logger.info(f"Sending response for interview {interview_uuid}: question_count={question_count}, time_remaining={time_remaining}s, is_final={response_data['is_final']}")
            logger.info(f"Response data keys: {list(response_data.keys())}")
            logger.info(f"AI response length: {len(ai_response)} characters")
    
            # Save updated context to session
            request.session[session_key] = context
            request.session.modified = True
            
            # Update interview start time if not already set
            if not interview.started_at:
                interview.started_at = timezone.now()
                interview.save(update_fields=['started_at'])
                logger.info(f"Interview {interview_uuid} start time updated to {interview.started_at}")
            
            # Clear duplicate prevention after a delay
            if 'last_processed_input' in context:
                context['last_processed_input'] = ''
                request.session[session_key] = context
                request.session.modified = True
            
            logger.info(f"About to return JsonResponse for interview {interview_uuid}")
            return JsonResponse(response_data)
        
        # HANDLE GET REQUEST - Show interview UI with first question
        ai_question = f"Hi there! I'm Sarah. Before we begin, could you please tell me your name?"
        
        logger.info(f"Generated AI initial question for interview {interview_uuid}")
        
        # Add initial question to context conversation history
        context = request.session.get(session_key, {})
        conversation_history = context.get('conversation_history', [])
        conversation_history.append({
            'speaker': 'interviewer',
            'message': ai_question,
            'question_number': 0,
            'timestamp': timezone.now().isoformat(),
            'response_type': 'initial_greeting',
            'response_length': len(ai_question)
        })
        
        context['conversation_history'] = conversation_history
        context['interview_started_at'] = timezone.now().isoformat()
        context['interviewer_name'] = 'Sarah'
        request.session[session_key] = context
        request.session.modified = True
        
        # Generate initial TTS
        audio_path = None
        audio_duration = None
        try:
            logger.info(f"Starting initial TTS generation for interview {interview_uuid}")
            
            from jobapp.tts import generate_tts, estimate_audio_duration, get_audio_duration
            
            audio_path = generate_tts(ai_question, "female_interview")
            
            if audio_path and audio_path != 'None':
                try:
                    full_audio_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                    if os.path.exists(full_audio_path):
                        actual_duration = get_audio_duration(full_audio_path)
                        
                        if actual_duration and actual_duration > 0:
                            audio_duration = actual_duration
                            logger.info(f"Initial question - using actual audio duration: {audio_duration:.2f} seconds")
                        else:
                            audio_duration = estimate_audio_duration(ai_question)
                            logger.info(f"Initial question - using estimated audio duration: {audio_duration:.2f} seconds")
                    else:
                        logger.warning(f"Initial audio file not found: {full_audio_path}")
                        audio_path = None
                        audio_duration = estimate_audio_duration(ai_question)
                except Exception as duration_error:
                    logger.error(f"Error getting initial audio duration: {duration_error}")
                    audio_duration = estimate_audio_duration(ai_question)
            else:
                logger.info("No initial audio path returned from TTS generation")
                audio_path = None
                audio_duration = estimate_audio_duration(ai_question)
                
        except Exception as e:
            logger.error(f"Initial TTS generation failed for interview {interview_uuid}: {e}")
            audio_path = None
            try:
                from jobapp.tts import estimate_audio_duration
                audio_duration = estimate_audio_duration(ai_question)
            except:
                audio_duration = max(6.0, len(ai_question) * 0.05)

        if not audio_duration or audio_duration <= 0:
            audio_duration = max(5.0, len(ai_question) * 0.05)

        # Template context
        context_data = {
            'interview': interview,
            'ai_question': ai_question,
            'audio_url': audio_path if audio_path else '',
            'audio_duration': audio_duration,
            'candidate_name': candidate_name,
            'job_title': job_title,
            'company_name': company_name,
            'has_audio': bool(audio_path),
            'csrf_token': get_token(request),
            'is_registered_candidate': interview.is_registered_candidate,
        }
        
        logger.info(f"Template context for interview {interview_uuid} - has_audio: {context_data['has_audio']}, duration: {audio_duration:.2f}s")
        
        return render(request, 'jobapp/interview_simple.html', context_data)
        
    except Http404:
        logger.error(f"Interview not found: {interview_uuid}")
        return HttpResponse('Interview not found.', status=404)
    
    except Exception as e:
        import traceback
        error_details = {
            'interview_uuid': interview_uuid,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc(),
            'request_method': request.method,
        }
        
        logger.error(f"CRITICAL INTERVIEW ERROR: {error_details}")
        
        # If this is a POST request (user response), return JSON error instead of completing interview
        if request.method == "POST":
            logger.error(f"POST request failed for interview {interview_uuid}, returning error response")
            return JsonResponse({
                'success': False,
                'error': 'Interview processing error',
                'response': 'I apologize, there was a technical issue. Could you please repeat your response?',
                'audio': '',
                'audio_duration': 3.0,
                'interview_completed': False,
                'is_final': False
            })
        
        if settings.DEBUG:
            return HttpResponse(
                f'Interview error.<br>'
                f'Error: {error_details["error_message"]}<br>'
                f'<pre>{error_details["traceback"]}</pre>',
                status=500
            )
        else:
            return HttpResponse(
                'Interview system temporarily unavailable. Please try again in a few minutes.',
                status=500
            )


            






# contact view
# def contact_view(request):
#     return render(request, 'jobapp/contact.html')



# testimonials

# def testimonials_view(request):
#     return render(request, 'jobapp/testimonials.html')



# About View
# def about_view(request):
#     return render(request, 'jobapp/about.html')



# FAQ view
# def faq_view(request):
#     return render(request, 'jobapp/faq.html')


# Blog
# def blog_view(request):
#     return render(request, 'jobapp/blog.html')



# blog single
# def blog_single_view(request):
#     """Display single blog post"""
#     return render(request, 'jobapp/blog_single.html')




        
            
      
           
        
        



def serve_media(request, path):
    """
    Serve media files in production with better error handling
    """
    try:
        # Try to serve the file
        media_root = settings.MEDIA_ROOT
        full_path = os.path.join(media_root, path)
        
        logger.info(f"Attempting to serve media file: {path}")
        logger.info(f"Full path: {full_path}")
        logger.info(f"File exists: {os.path.exists(full_path)}")
        
        if not os.path.exists(full_path):
            logger.error(f"Media file not found: {full_path}")
            raise Http404(f"Media file not found: {path}")
        
        # Get file info
        file_size = os.path.getsize(full_path)
        logger.info(f"File size: {file_size} bytes")
        
        # For PDF files, ensure proper content type
        response = serve(request, path, document_root=media_root)
        if path.lower().endswith('.pdf'):
            response['Content-Type'] = 'application/pdf'
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(path)}"'
            
        return response
    except Exception as e:
        logger.error(f"Error serving media file {path}: {e}")
        raise Http404(f"Media file not found: {path}")

# CSRF token endpoint
def get_csrf_token(request):
    """Return fresh CSRF token for AJAX requests"""
    return JsonResponse({
        'csrf_token': get_token(request)
    })




# Audio generation endpoint
@csrf_exempt
def generate_audio(request):
    """Generate audio for given text"""
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                text = data.get('text', '')
            else:
                text = request.POST.get('text', '')
            
            if not text.strip():
                return JsonResponse({'error': 'No text provided'}, status=400)
            
            logger.info(f"Audio generation requested for: '{text[:50]}...'")
            
            # Generate audio
            audio_path = generate_tts(text)
            
            if audio_path:
                # Verify file exists
                full_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    logger.info(f"Audio generated successfully: {audio_path} ({file_size} bytes)")
                    
                    return JsonResponse({
                        'success': True,
                        'audio_url': audio_path,
                        'file_size': file_size,
                        'message': 'Audio generated successfully'
                    })
                else:
                    logger.error(f"Generated audio file not found: {full_path}")
                    return JsonResponse({
                        'success': False,
                        'error': 'Audio file was not created',
                        'message': 'Audio generation failed'
                    }, status=500)
            else:
                logger.error("Audio generation returned None")
                return JsonResponse({
                    'success': False,
                    'error': 'Audio generation failed',
                    'message': 'TTS system returned no audio'
                }, status=500)
                
        except Exception as e:
            logger.error(f"Audio generation error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Audio generation failed with error'
            }, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

# Save interview recording
@csrf_exempt
def save_interview_recording(request):
    """Save interview recording file"""
    if request.method == 'POST':
        try:
            # Get the recording file
            recording_file = request.FILES.get('recording')
            interview_uuid = request.POST.get('interview_uuid')
            duration = request.POST.get('duration', 0)
            
            if not recording_file:
                return JsonResponse({'error': 'No recording file provided'}, status=400)
            
            if not interview_uuid:
                return JsonResponse({'error': 'No interview UUID provided'}, status=400)
            
            logger.info(f"Saving recording for interview {interview_uuid}: {recording_file.name} ({recording_file.size} bytes)")
            
            # Get the interview record
            try:
                interview = Interview.objects.get(uuid=interview_uuid)
            except Interview.DoesNotExist:
                return JsonResponse({'error': 'Interview not found'}, status=404)
            
            # Create recordings directory if it doesn't exist
            recordings_dir = os.path.join(settings.MEDIA_ROOT, 'interview_recordings')
            try:
                os.makedirs(recordings_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create recordings directory: {e}")
                return JsonResponse({'error': 'Failed to create storage directory'}, status=500)
            
            # Generate unique filename
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            file_extension = os.path.splitext(recording_file.name)[1] or '.webm'
            filename = f"interview_{interview_uuid}_{timestamp}{file_extension}"
            file_path = os.path.join(recordings_dir, filename)
            
            # Save the file
            with open(file_path, 'wb') as f:
                for chunk in recording_file.chunks():
                    f.write(chunk)
            
            # Update interview record with recording info
            relative_path = os.path.join('interview_recordings', filename)
            
            # Add recording info to interview (you might want to create a separate Recording model)
            # For now, we'll store it in the transcript field or create a new field
            recording_info = {
                'recording_path': relative_path,
                'duration': float(duration),
                'file_size': recording_file.size,
                'recorded_at': timezone.now().isoformat(),
                'filename': filename
            }
            
            # Store recording info in interview record
            interview.recording_data = json.dumps(recording_info)
            interview.recording_path = relative_path
            interview.recording_duration = float(duration)
            interview.is_recorded = True
            
            # Also update transcript with recording info
            current_transcript = interview.transcript or ''
            interview.transcript = current_transcript + f"\n\nRecording saved: {json.dumps(recording_info)}"
            
            interview.save()
            
            logger.info(f"Recording saved successfully: {file_path}")
            
            return JsonResponse({
                'success': True,
                'message': 'Recording saved successfully',
                'filename': filename,
                'file_size': recording_file.size,
                'duration': duration,
                'path': relative_path
            })
            
        except Exception as e:
            logger.error(f"Error saving interview recording: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Failed to save recording'
            }, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)




@login_required
@user_passes_test(lambda u: u.is_recruiter)
def add_candidates(request, job_id):
    """Add candidates to a specific job - fixed version"""
    # Get the job and ensure the recruiter owns it
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        # Handle candidate addition form submission
        candidate_name = request.POST.get('candidate_name', '').strip()
        candidate_email = request.POST.get('candidate_email', '').strip()
        candidate_phone = request.POST.get('candidate_phone', '').strip()
        candidate_resume = request.FILES.get('candidate_resume')
        
        # Validation
        if not candidate_name:
            messages.error(request, 'Candidate name is required.')
            return redirect('add_candidates', job_id=job_id)
        
        if not candidate_email:
            messages.error(request, 'Candidate email is required.')
            return redirect('add_candidates', job_id=job_id)
        
        if not candidate_phone:
            messages.error(request, 'Candidate phone is required.')
            return redirect('add_candidates', job_id=job_id)
        
        # Check if candidate already exists for this recruiter (since Candidate model doesn't have job field)
        existing_candidate = Candidate.objects.filter(
            email=candidate_email,
            added_by=request.user
        ).first()
        
        if existing_candidate:
            messages.warning(request, f'Candidate with email {candidate_email} already exists in your candidates list.')
            return redirect('add_candidates', job_id=job_id)
        
        try:
            # Create and save the candidate (without job field since it doesn't exist in the model)
            candidate = Candidate.objects.create(
                name=candidate_name,
                email=candidate_email,
                phone=candidate_phone,
                resume=candidate_resume,
                added_by=request.user
            )
            
            messages.success(request, f'Candidate {candidate_name} added successfully!')
            logger.info(f'Candidate {candidate_name} added by user {request.user.username}')
            
        except Exception as e:
            logger.error(f'Error adding candidate: {e}')
            messages.error(request, f'Error adding candidate: {str(e)}')
        
        return redirect('add_candidates', job_id=job_id)
    
    # Get all candidates added by this recruiter (since there's no job relationship)
    candidates = Candidate.objects.filter(added_by=request.user).order_by('-added_at')
    
    return render(request, 'jobapp/add_candidates.html', {
        'job': job,
        'candidates': candidates
    })


@login_required
@user_passes_test(lambda u: u.is_recruiter)
def add_candidate_dashboard(request):
    """Add candidate directly from recruiter dashboard"""
    if request.method == 'POST':
        form = AddCandidateForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Check if candidate already exists for this recruiter
                candidate_email = form.cleaned_data['email']
                existing_candidate = Candidate.objects.filter(
                    email=candidate_email,
                    added_by=request.user
                ).first()
                
                if existing_candidate:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'message': f'Candidate with email {candidate_email} already exists in your candidates list.'
                        })
                    messages.warning(request, f'Candidate with email {candidate_email} already exists in your candidates list.')
                    return redirect('recruiter_dashboard')
                
                # Create candidate
                candidate = form.save(commit=False)
                candidate.added_by = request.user
                candidate.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Candidate {candidate.name} added successfully!',
                        'candidate_id': candidate.id
                    })
                
                messages.success(request, f'Candidate {candidate.name} added successfully!')
                logger.info(f'Candidate {candidate.name} added by user {request.user.username} via dashboard')
                
            except Exception as e:
                logger.error(f'Error adding candidate via dashboard: {e}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Error adding candidate: {str(e)}'
                    })
                
                messages.error(request, f'Error adding candidate: {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('recruiter_dashboard')


@login_required
@user_passes_test(lambda u: u.is_recruiter)
def recruiter_dashboard(request):
    """Updated recruiter dashboard with proper candidate handling"""
    # Initialize all variables as empty
    applications = []
    jobs = []
    scheduled_interviews = []
    all_candidates = []
    
    try:
        # Get jobs posted by this recruiter
        jobs = Job.objects.filter(posted_by=request.user).order_by('-date_posted')
        logger.info(f"Successfully loaded {len(jobs)} jobs for recruiter {request.user.username}")
    except Exception as e:
        logger.error(f"Job query failed for recruiter {request.user.username}: {e}")
        jobs = []
    
    # Try to get applications for recruiter's jobs
    try:
        applications = Application.objects.filter(
            job__posted_by=request.user
        ).select_related('job', 'applicant').order_by('-applied_at')
        logger.info(f"Successfully loaded {len(applications)} applications for recruiter {request.user.username}")
    except Exception as e:
        logger.warning(f"Application query failed for recruiter {request.user.username}: {e}")
        applications = []
    
    # Try to get interviews for recruiter's jobs
    try:
        scheduled_interviews = Interview.objects.filter(
            job__posted_by=request.user
        ).select_related('job', 'candidate').order_by('-scheduled_at')
        logger.info(f"Successfully loaded {len(scheduled_interviews)} interviews for recruiter {request.user.username}")
    except Exception as e:
        logger.warning(f"Interview query failed for recruiter {request.user.username}: {e}")
        scheduled_interviews = []
    
    # Get completed interviews with results for the results section
    try:
        completed_interviews = Interview.objects.filter(
            job__posted_by=request.user,
            status='completed'
        ).select_related('job', 'candidate').order_by('-completed_at')
        logger.info(f"Successfully loaded {len(completed_interviews)} completed interviews for recruiter {request.user.username}")
    except Exception as e:
        logger.warning(f"Completed interview query failed for recruiter {request.user.username}: {e}")
        completed_interviews = []
    
    # Get all candidates added by this recruiter
    try:
        all_candidates = Candidate.objects.filter(
            added_by=request.user
        ).order_by('-added_at')
        logger.info(f"Successfully loaded {len(all_candidates)} candidates for recruiter {request.user.username}")
    except Exception as e:
        logger.warning(f"Candidate query failed for recruiter {request.user.username}: {e}")
        all_candidates = []
    
    # Get user's jobs for the modal dropdown
    try:
        user_jobs = Job.objects.filter(posted_by=request.user).values('id', 'title', 'company', 'status')
        user_jobs_list = list(user_jobs)
        logger.info(f"Successfully loaded {len(user_jobs_list)} jobs for modal dropdown")
    except Exception as e:
        logger.warning(f"Could not fetch user jobs for modal: {e}")
        user_jobs_list = []
    
    # Prepare context
    context = {
        'applications': applications,
        'scheduled_interviews': scheduled_interviews,
        'completed_interviews': completed_interviews,
        'all_candidates': all_candidates,
        'jobs': jobs,
        'user_jobs': user_jobs_list,
        'user': request.user,
        'debug_info': {
            'jobs_count': len(jobs),
            'applications_count': len(applications),
            'interviews_count': len(scheduled_interviews),
            'completed_interviews_count': len(completed_interviews),
            'candidates_count': len(all_candidates)
        }
    }
    
    logger.info(f"Recruiter dashboard loaded for {request.user.username}: {len(jobs)} jobs, {len(applications)} applications, {len(all_candidates)} candidates")
    
    return render(request, 'jobapp/recruiter_dashboard.html', context)



        

# specific crud operation for  updating job structure           
@login_required
@user_passes_test(lambda u: u.is_recruiter)
def edit_job(request, job_id):
    """Edit job view - shows form in modal or separate page"""
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        logger.info(f"Edit job POST request for job {job_id} by user {request.user.id}")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        logger.info(f"FILES data keys: {list(request.FILES.keys())}")
        
        # Log current image before update
        logger.info(f"Current job image before update: {job.featured_image}")
        
        form = JobForm(request.POST, request.FILES, instance=job)
        
        if form.is_valid():
            logger.info("Edit job form is valid, saving...")
            updated_job = form.save(commit=False)
            updated_job.posted_by = request.user  # Ensure ownership stays same
            updated_job.save()
            form.save_m2m()  # For tags
            
            # Log image after update
            logger.info(f"Job image after update: {updated_job.featured_image}")
            
            messages.success(request, f'Job "{updated_job.title}" updated successfully!')
            
            # Return JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Job updated successfully!',
                    'job_title': updated_job.title,
                    'image_url': updated_job.featured_image.url if updated_job.featured_image else None
                })
            
            return redirect('recruiter_dashboard')
        else:
            logger.error(f"Edit job form validation failed: {form.errors}")
            # Return form errors for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Form validation failed'
                })
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
        'is_editing': True
    }
    
    # For AJAX requests, return only the form HTML
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'jobapp/edit_job_modal_content.html', context)
    
    return render(request, 'jobapp/edit_job.html', context)

@login_required
@user_passes_test(lambda u: u.is_recruiter)
@require_POST
def delete_job(request, job_id):
    """Delete a job posting"""
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    job_title = job.title
    
    try:
        job.delete()
        messages.success(request, f'Job "{job_title}" deleted successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Job "{job_title}" deleted successfully!'})
            
    except Exception as e:
        messages.error(request, f'Error deleting job: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'Error deleting job: {str(e)}'})
    
    return redirect('recruiter_dashboard')

@login_required
@user_passes_test(lambda u: u.is_recruiter)
def duplicate_job(request, job_id):
    """Duplicate a job posting"""
    original_job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    try:
        # Create a copy
        new_job = Job.objects.get(pk=original_job.pk)
        new_job.pk = None  # This will create a new instance
        new_job.id = None
        new_job.title = f"{original_job.title} (Copy)"
        new_job.status = 'draft'  # Set as draft
        new_job.save()
        
        # Copy tags
        for tag in original_job.tags.all():
            new_job.tags.add(tag)
        
        messages.success(request, f'Job duplicated successfully as "{new_job.title}"')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'Job duplicated successfully!',
                'new_job_id': new_job.id
            })
            
    except Exception as e:
        messages.error(request, f'Error duplicating job: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'Error duplicating job: {str(e)}'})
    
    return redirect('recruiter_dashboard')

@login_required
@user_passes_test(lambda u: u.is_recruiter)
def get_candidate_email(request, candidate_id):
    """API endpoint to get candidate email"""
    try:
        candidate = get_object_or_404(Candidate, id=candidate_id, added_by=request.user)
        return JsonResponse({
            'success': True,
            'email': candidate.email,
            'name': candidate.name
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })




        
        
     
     
     




def generate_interview_results(interview, conversation_history):
    """Generate and save interview results from live conversation - FIXED VERSION"""
    try:
        logger.info(f"🔄 Starting results generation for interview {interview.uuid}")
        logger.info(f"📊 Conversation history has {len(conversation_history)} exchanges")
        
        # Extract questions and answers from conversation history
        #Collect the Conversation - Takes all questions asked by AI interviewer,Takes all answers given by candidate,
        #Counts how many questions were asked , Measures how detailed the answers were
        questions_asked = []
        answers_given = []
        candidate_responses = []
        interviewer_questions = []
        
        for entry in conversation_history:
            if entry['speaker'] == 'candidate':
                candidate_responses.append(entry['message'])
                answers_given.append({
                    'question_number': entry.get('question_number', 0),
                    'answer': entry['message'],
                    'timestamp': entry.get('timestamp', timezone.now().isoformat())
                })
            elif entry['speaker'] == 'interviewer':
                interviewer_questions.append(entry['message'])
                questions_asked.append({
                    'question_number': entry.get('question_number', 0),
                    'question': entry['message'],
                    'timestamp': entry.get('timestamp', timezone.now().isoformat())
                })
                
                
                
        
        logger.info(f"📝 Extracted {len(questions_asked)} questions and {len(answers_given)} answers")
        
        # CRITICAL FIX: Handle edge case where no responses were recorded
        if len(candidate_responses) == 0:
            logger.warning(f"⚠️ No candidate responses found for interview {interview.uuid}")
            # Still save partial results
            interview.questions_asked = json.dumps(questions_asked)
            interview.answers_given = json.dumps([])
            interview.overall_score = 1.0
            interview.technical_score = 1.0
            interview.communication_score = 1.0
            interview.problem_solving_score = 1.0
            interview.ai_feedback = "Interview was completed but no candidate responses were recorded. This may indicate a technical issue during the interview."
            interview.recommendation = 'not_recommended'
            interview.status = 'completed'
            interview.completed_at = timezone.now()
            interview.results_generated_at = timezone.now()
            interview.transcript = "No conversation data available."
            interview.save()
            logger.info(f"✅ Saved partial results for interview {interview.uuid}")
            return True
        
        # Generate basic scores based on conversation quality
        # Calculate Scores -Technical Score: How well they know technology (1-10)
        #-Communication Score: How clearly they speak (1-10)
        #-Problem-Solving Score: How they think through problems (1-10)
        #-Overall Score: Average of all scores
        
        total_responses = len(candidate_responses)
        avg_response_length = sum(len(response) for response in candidate_responses) / max(total_responses, 1)
        
        logger.info(f"📈 Calculating scores - Responses: {total_responses}, Avg length: {avg_response_length:.1f}")
        
        # Simple scoring algorithm based on response quality
        technical_score = min(10.0, max(1.0, (avg_response_length / 50) * 5))  # Based on response depth
        communication_score = min(10.0, max(1.0, total_responses * 1.5))  # Based on engagement
        problem_solving_score = min(10.0, max(1.0, 6.0))  # Default middle score
        overall_score = (technical_score + communication_score + problem_solving_score) / 3
        
        
        
        # Generate detailed AI feedback using actual conversation analysis
        try:
            # Build full conversation for AI analysis
            #Generate AI Feedback
            
            
            full_conversation = "\n\n".join([
                f"{entry['speaker'].title()}: {entry['message']}"
                for entry in conversation_history
            ])
            
            # Create comprehensive analysis prompt
            analysis_prompt = f"""
Analyze this job interview conversation and provide a detailed professional assessment:

CANDIDATE: {interview.candidate_name}
POSITION: {interview.job.title if interview.job else 'Software Developer'}
COMPANY: {interview.job.company if interview.job else 'Our Company'}

FULL INTERVIEW CONVERSATION:
{full_conversation}

Provide a comprehensive analysis in this exact format:

Overall Assessment:
[Detailed paragraph analyzing the candidate's technical capabilities, communication skills, professional demeanor, problem-solving approach, and team collaboration potential. Be specific about strengths and concerns based on their actual responses.]

Decision: [Recommended for Hire / Not Recommended for Hire / Requires Further Evaluation]

Feedback for the Candidate:
[Specific advice for improvement, areas to focus on, and strengths to build upon based on the interview performance.]

Focus your analysis on: technical competency demonstrated, communication clarity, professional presentation, problem-solving methodology, and cultural fit indicators.
"""
            
            # Get AI analysis using existing function
            detailed_analysis = ask_ai_question(
                analysis_prompt,
                candidate_name=interview.candidate_name,
                job_title=interview.job.title if interview.job else 'Software Developer',
                company_name=interview.job.company if interview.job else 'Our Company',
                timeout=30
            )
            
            
            
            #Make Hiring Recommendation
            if detailed_analysis and len(detailed_analysis) > 100:
                ai_feedback = detailed_analysis
                # Extract recommendation from AI response
                if 'not recommended' in detailed_analysis.lower():
                    recommendation = 'not_recommended'
                elif 'highly recommended' in detailed_analysis.lower():
                    recommendation = 'highly_recommended'
                elif 'recommended' in detailed_analysis.lower():
                    recommendation = 'recommended'
                else:
                    recommendation = 'maybe'
            else:
                # Fallback to enhanced basic analysis
                ai_feedback = f"""Overall Assessment:
The candidate participated in a {total_responses}-question interview with an average response length of {int(avg_response_length)} characters. Based on their engagement level and response quality, they demonstrated {'strong' if avg_response_length > 100 else 'moderate' if avg_response_length > 50 else 'basic'} communication skills. {'The detailed responses suggest good technical understanding and articulation abilities.' if avg_response_length > 100 else 'The responses indicate room for improvement in providing more comprehensive explanations and technical depth.'}

Decision: {'Recommended for Hire' if avg_response_length > 100 else 'Requires Further Evaluation'}

Feedback for the Candidate:
{'Continue leveraging your strong communication skills and technical knowledge. Focus on maintaining this level of detail in future interviews.' if avg_response_length > 100 else 'To strengthen future opportunities, focus on providing more detailed responses that showcase your technical expertise and problem-solving approach. Practice articulating your experience with specific examples and technical implementations.'}"""
                recommendation = 'recommended' if avg_response_length > 100 else 'maybe'
                
        except Exception as ai_error:
            logger.error(f"AI analysis failed: {ai_error}")
            # Enhanced fallback analysis
            ai_feedback = f"""Overall Assessment:
The candidate completed the interview with {total_responses} responses averaging {int(avg_response_length)} characters each. {'Their detailed responses demonstrate strong communication skills and technical engagement.' if avg_response_length > 100 else 'Their responses show basic engagement but could benefit from more comprehensive technical explanations.'} The interview duration and response quality suggest {'good' if total_responses >= 5 else 'limited'} interaction with the interviewer.

Decision: {'Recommended for Hire' if avg_response_length > 100 and total_responses >= 5 else 'Requires Further Evaluation'}

Feedback for the Candidate:
{'Your communication style and technical responses were well-received. Continue to build on these strengths in future opportunities.' if avg_response_length > 100 else 'To improve future interview performance, focus on providing more detailed technical explanations, specific examples from your experience, and comprehensive answers that demonstrate your problem-solving approach.'}"""
            recommendation = 'recommended' if avg_response_length > 100 and total_responses >= 5 else 'maybe'
        else:
            ai_feedback = f"""Overall Assessment:
The interview was brief with only {total_responses} responses recorded. Limited interaction makes it challenging to provide a comprehensive evaluation of the candidate's technical capabilities and communication skills. More extensive dialogue would be needed to assess their problem-solving approach and cultural fit.

Decision: Requires Further Evaluation

Feedback for the Candidate:
Due to the brief nature of this interview, we recommend scheduling a follow-up session to better showcase your technical expertise and experience. Prepare to discuss specific projects, challenges you've overcome, and your approach to problem-solving in more detail."""
            recommendation = 'maybe'
        
        logger.info(f"🎯 Scores calculated - Overall: {overall_score:.1f}, Technical: {technical_score:.1f}, Communication: {communication_score:.1f}")
        logger.info(f"💡 Recommendation: {recommendation}")
        
        # CRITICAL FIX: Save to database with explicit field assignment
        #Save Everything to Database
        try:
            interview.questions_asked = json.dumps(questions_asked)
            interview.answers_given = json.dumps(answers_given)
            interview.overall_score = round(overall_score, 1)
            interview.technical_score = round(technical_score, 1)
            interview.communication_score = round(communication_score, 1)
            interview.problem_solving_score = round(problem_solving_score, 1)
            interview.ai_feedback = ai_feedback
            interview.recommendation = recommendation
            interview.status = 'completed'
            interview.completed_at = timezone.now()
            interview.results_generated_at = timezone.now()
            
            # Save the full conversation in transcript field
            full_transcript = "\n\n".join([
                f"{entry['speaker'].title()}: {entry['message']}"
                for entry in conversation_history
            ])
            interview.transcript = full_transcript
            
            # CRITICAL: Force save to database
            interview.save(update_fields=[
                'questions_asked', 'answers_given', 'overall_score', 
                'technical_score', 'communication_score', 'problem_solving_score',
                'ai_feedback', 'recommendation', 'status', 'completed_at',
                'results_generated_at', 'transcript', 'started_at'
            ])
            
            
            
            logger.info(f"✅ Interview results saved successfully for {interview.uuid}")
            logger.info(f"📊 Final scores - Overall: {interview.overall_score}/10, Technical: {interview.technical_score}/10")
            logger.info(f"💼 Recommendation: {interview.recommendation}")
            logger.info(f"❓ Questions: {len(questions_asked)}, 💬 Responses: {len(answers_given)}")
            
            # VERIFICATION: Check if data was actually saved
            interview.refresh_from_db()
            if interview.overall_score is not None:
                logger.info(f"✅ VERIFICATION PASSED: Results confirmed in database")
                
                # Send completion email automatically
                # Email Confirmation code
                try:
                    send_interview_status_email(interview, 'completed')
                    logger.info(f"✅ Completion email sent for interview {interview.uuid}")
                except Exception as email_error:
                    logger.error(f"❌ Failed to send completion email: {email_error}")
                
                return True
            else:
                logger.error(f"❌ VERIFICATION FAILED: Results not found in database after save")
                return False
            
        except Exception as save_error:
            logger.error(f"❌ Database save error for interview {interview.uuid}: {save_error}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR generating interview results for {interview.uuid}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Try to save error state
        try:
            interview.status = 'completed'
            interview.completed_at = timezone.now()
            interview.ai_feedback = f"Error generating results: {str(e)}"
            interview.overall_score = 1.0
            interview.save()
        except:
            pass
            
        return False
    
    
#interview results view 
@login_required
@user_passes_test(lambda u: u.is_recruiter)
def interview_results(request, interview_uuid):
    """Display interview results for completed interviews - FIXED VERSION"""
    try:
        logger.info(f"📊 Results page accessed for interview {interview_uuid}")
        
        # Get the interview and ensure the recruiter owns it
        interview = get_object_or_404(Interview, uuid=interview_uuid)
        
        logger.info(f"✅ Interview found: {interview.candidate_name} for {interview.job.title}")
        logger.info(f"📝 Interview status: {interview.status}")
        logger.info(f"🎯 Has results: {interview.has_results}")
        logger.info(f"💯 Overall score: {interview.overall_score}")
        logger.info(f"💬 AI feedback length: {len(interview.ai_feedback) if interview.ai_feedback else 0}")
        
        if interview.job.posted_by != request.user:
            logger.warning(f"⚠️ Permission denied - wrong recruiter")
            messages.error(request, 'You do not have permission to view this interview.')
            return redirect('recruiter_dashboard')
        
        
        # Check if results exist
        if not interview.has_results:
            logger.warning(f"⚠️ No results available for interview {interview_uuid}")
            logger.info(f"Debug info - Status: {interview.status}, Completed: {interview.completed_at}")
            logger.info(f"Debug info - Questions: {bool(interview.questions_asked)}, Answers: {bool(interview.answers_given)}")
            
            # Try to regenerate results if interview is completed but has no results
            if interview.status == 'completed' and interview.completed_at:
                logger.info(f"🔄 Attempting to regenerate results...")
                messages.info(request, 'Results are being generated for this interview. Please refresh in a moment.')
            else:
                messages.warning(request, 'This interview is not yet completed or has no results.')
            
            return redirect('recruiter_dashboard')
        
        # Parse the questions and answers from JSON
        questions_asked = []
        answers_given = []
        
        try:
            if interview.questions_asked:
                questions_asked = json.loads(interview.questions_asked)
                logger.info(f"✅ Parsed {len(questions_asked)} questions")
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"❌ Could not parse questions_asked: {e}")
        
        try:
            if interview.answers_given:
                answers_given = json.loads(interview.answers_given)
                logger.info(f"✅ Parsed {len(answers_given)} answers")
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"❌ Could not parse answers_given: {e}")
        
        # Combine questions and answers for display 
        qa_pairs = []
        for i in range(max(len(questions_asked), len(answers_given))):
            question = questions_asked[i] if i < len(questions_asked) else None
            answer = answers_given[i] if i < len(answers_given) else None
            
            qa_pairs.append({
                'question_number': i + 1,
                'question': question['question'] if question else 'Question not recorded',
                'answer': answer['answer'] if answer else 'Answer not recorded',
                'question_timestamp': question.get('timestamp') if question else None,
                'answer_timestamp': answer.get('timestamp') if answer else None
            })
        
        logger.info(f"✅ Created {len(qa_pairs)} Q&A pairs for display")
        
        # Calculate interview duration if available -  actual start time
        interview_duration = None
        if interview.completed_at and interview.started_at:
            duration_seconds = (interview.completed_at - interview.started_at).total_seconds()
            # Ensure duration is positive and reasonable (max 60 minutes for interviews)
            if duration_seconds > 0 and duration_seconds <= 3600:  # Max 1 hour
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                interview_duration = f"{minutes}m {seconds}s"
            elif duration_seconds > 3600:
                # If duration seems too long, use the scheduled duration instead
                scheduled_duration = getattr(interview, 'interview_duration_minutes', 15)
                interview_duration = f"{scheduled_duration}m (scheduled duration)"
            else:
                interview_duration = "Less than 1 minute"
        elif interview.completed_at and interview.created_at:
            # Fallback to created_at if started_at is not available (for old interviews)
            duration_seconds = (interview.completed_at - interview.created_at).total_seconds()
            if duration_seconds > 0 and duration_seconds <= 3600:  # Max 1 hour
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                interview_duration = f"{minutes}m {seconds}s (estimated)"
            elif duration_seconds > 3600:
                # If duration seems too long, use the scheduled duration instead
                scheduled_duration = getattr(interview, 'interview_duration_minutes', 15)
                interview_duration = f"{scheduled_duration}m (scheduled duration)"
            else:
                interview_duration = "Duration unavailable"
        
        logger.info(f"⏱️ Interview duration calculated: {interview_duration}")
        if interview.started_at and interview.completed_at:
            actual_duration = (interview.completed_at - interview.started_at).total_seconds()
            logger.info(f"📅 Started: {interview.started_at}, Completed: {interview.completed_at}")
            logger.info(f"⏱️ Actual duration: {actual_duration:.0f} seconds ({actual_duration/60:.1f} minutes)")
            logger.info(f"🎯 Scheduled duration: {getattr(interview, 'interview_duration_minutes', 15)} minutes")
        else:
            logger.info(f"⚠️ Missing timestamps - Started: {interview.started_at}, Completed: {interview.completed_at}")
        
        
        
        # Prepare Data for Template - Packages all data into a dictionary called context
        #-Sends data to HTML template (interview_results.html)
        #-Template uses this data to create the beautiful results page
        context = {
            'interview': interview,
            'qa_pairs': qa_pairs,
            'interview_duration': interview_duration,
            'total_questions': len(questions_asked),
            'total_answers': len(answers_given),
        }
        
        logger.info(f"✅ Rendering results page with {len(qa_pairs)} Q&A pairs")
        return render(request, 'jobapp/interview_results.html', context)
    #Error Handling   
    except Exception as e:
        logger.error(f"❌ Error displaying interview results for {interview_uuid}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        messages.error(request, 'Could not load interview results. Please try again.')
        return redirect('recruiter_dashboard')    


# EMAIL MANAGEMENT VIEWS

@login_required
@user_passes_test(lambda u: u.is_recruiter)
def send_interview_email_manual(request, interview_uuid):
    """Manually send interview email to candidate"""
    try:
        interview = get_object_or_404(Interview, uuid=interview_uuid)
        
        # Check if recruiter owns this interview
        if interview.job.posted_by != request.user:
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to send this interview email.'
            }, status=403)
        
        # Send the email
        result = send_interview_link_email(interview)
        
        if result['success']:
            messages.success(request, f'Interview email sent successfully to {interview.candidate_email}!')
        else:
            messages.warning(request, f'Email could not be sent, but interview link is available: {result["interview_url"]}')
        
        return JsonResponse({
            'success': True,
            'message': f'Email process completed for {interview.candidate_email}',
            'interview_url': result['interview_url'],
            'email_sent': result['success']
        })
        
    except Exception as e:
        logger.error(f"Manual email sending failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }, status=500)


#This function is like the "Copy Meeting Link" feature like in zoom meeting 
@login_required
@user_passes_test(lambda u: u.is_recruiter)
def get_interview_link(request, interview_uuid):
    """Get interview link for manual sharing"""
    try:
        interview = get_object_or_404(Interview, uuid=interview_uuid)
        
        # Check if recruiter owns this interview
        if interview.job.posted_by != request.user:
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to access this interview.'
            }, status=403)
        
        # Generate interview URL
        domain = getattr(settings, 'PRODUCTION_DOMAIN', 'localhost:8000')
        if settings.DEBUG:
            domain = 'localhost:8000'
        protocol = 'https' if not settings.DEBUG else 'http'
        interview_url = f"{protocol}://{domain}/interview/ready/{interview.uuid}/"
        
        return JsonResponse({
            'success': True,
            'interview_url': interview_url,
            'candidate_name': interview.candidate_name,
            'candidate_email': interview.candidate_email,
            'job_title': interview.job.title,
            'company_name': interview.job.company,
            'interview_id': interview.interview_id,
            'scheduled_date': interview.scheduled_at.strftime('%B %d, %Y at %I:%M %p') if interview.scheduled_at else 'TBD'
        })
        
    except Exception as e:
        logger.error(f"Get interview link failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Failed to get interview link: {str(e)}'
        }, status=500)







