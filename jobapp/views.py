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
from jobapp.tts import generate_tts, generate_gtts_fallback,  check_tts_system
import json
from django.conf import settings
import logging
from .health import health_check, readiness_check



# At the top of your views.py file, add:






from django.views.decorators.http import require_POST

from django.http import JsonResponse
from django.db import connection

from django.core.exceptions import FieldError
from django.views.static import serve

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


#for Ai interview
try:
    from .utils.interview_ai_nvidia import ask_ai_question 
    from jobapp.utils.resume_reader import extract_resume_text
except ImportError as e:
    print(f"Import error: {e}")
    def ask_ai_question(prompt, candidate_name=None, job_title=None, company_name=None , timeout=None):
        return "AI service is currently unavailable. Please try again later."
    def extract_resume_text(resume_file):
        return "Resume processing is currently unavailable."

from gtts import gTTS

from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.middleware.csrf import CsrfViewMiddleware
import uuid










# Create your views here.

def home_view(request):
    return render(request, 'jobapp/home.html')


#register view - redirects to login (register.html no longer needed)
def register_view(request):
    return redirect('login')
    
    
    
#login view - handles both login and registration
def login_view(request):
    if request.method == 'POST':
        # Check if this is a registration or login request
        if 'username' in request.POST and 'password1' in request.POST:
            # This is a registration request
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                # ✅ Tell Django which backend to use
                backend = get_backends()[0]  # Use the first available backend (your default one)
                user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
                login(request, user)
                return redirect('Profile_update')  # Redirect to profile page
            else:
                # Registration form has errors, show them on login page
                login_form = LoginForm()
                return render(request, 'registration/login.html', {
                    'form': login_form, 
                    'registration_form': form,
                    'registration_errors': True
                })
        else:
            # This is a login request
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    # Redirect based on user type
                    if user.is_recruiter:
                        return redirect('recruiter_dashboard')
                    else:
                        return redirect('Profile_update')
                else:
                    form.add_error(None, 'invalid credentials')
            
            # Login form has errors, show them on login page
            registration_form = UserRegistrationForm()
            return render(request, 'registration/login.html', {
                'form': form, 
                'registration_form': registration_form,
                'login_errors': True
            })
                
    else:
        # GET request - show both forms
        form = LoginForm()
        registration_form = UserRegistrationForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'registration_form': registration_form
    })
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






def debug_job_posting(request):
    """Debug view to check job posting issues"""
    debug_info = {}
    
    try:
        # 1. Check if Job model can be imported
        from .models import Job
        debug_info['model_import'] = 'SUCCESS'
        
        # 2. Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            debug_info['db_connection'] = 'SUCCESS'
        
        # 3. Check if jobapp_job table exists
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'jobapp_job'
            """)
            result = cursor.fetchone()
            debug_info['table_exists'] = 'YES' if result else 'NO'
            
        # 4. Check table structure
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'jobapp_job'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            debug_info['table_columns'] = [f"{col[0]} ({col[1]})" for col in columns]
            
        # 5. Check current job count
        job_count = Job.objects.count()
        debug_info['current_job_count'] = job_count
        
        # 6. Check if user can create jobs
        if request.user.is_authenticated:
            debug_info['user_authenticated'] = True
            debug_info['user_is_recruiter'] = getattr(request.user, 'is_recruiter', False)
            debug_info['user_id'] = request.user.id
        else:
            debug_info['user_authenticated'] = False
            
        # 7. Try to create a test job (without saving)
        test_job = Job(
            title="Test Job",
            company="Test Company", 
            location="Test Location",
            description="Test Description for debugging purposes",
            posted_by=request.user if request.user.is_authenticated else None
        )
        debug_info['test_job_creation'] = 'SUCCESS'
        
    except Exception as e:
        debug_info['error'] = str(e)
        debug_info['error_type'] = type(e).__name__
        
    return JsonResponse(debug_info, indent=2)

@require_POST
def test_job_save(request):
    """Test saving a job to database"""
    if not request.user.is_authenticated or not request.user.is_recruiter:
        return JsonResponse({'error': 'Must be logged in as recruiter'}, status=403)
        
    try:
        with transaction.atomic():
            # Create test job
            test_job = Job.objects.create(
                title="DEBUG TEST JOB - DELETE ME",
                company="Test Company Debug",
                location="Test Location",
                description="This is a test job created for debugging. Please delete this job after testing.",
                posted_by=request.user
            )
            
            # Verify it was saved
            saved_job = Job.objects.filter(id=test_job.id).first()
            
            if saved_job:
                return JsonResponse({
                    'success': True,
                    'job_id': saved_job.id,
                    'job_title': saved_job.title,
                    'message': 'Test job created successfully!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Job was created but not found in database'
                })
                
    except Exception as e:
        logger.error(f"Test job save failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        })

def fix_database_issues(request):
    """Attempt to fix common database issues"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Only superusers can run database fixes'}, status=403)
    
    fixes_applied = []
    errors = []
    
    try:
        # 1. Run migrations
        try:
            call_command('makemigrations', 'jobapp')
            call_command('migrate', 'jobapp')
            fixes_applied.append('Migrations updated and applied')
        except Exception as e:
            errors.append(f'Migration error: {str(e)}')
        
        # 2. Check for missing columns and add them
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jobapp_job'
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            required_columns = [
                'title', 'company', 'location', 'description', 
                'posted_by_id', 'date_posted', 'status'
            ]
            
            missing_columns = []
            for col in required_columns:
                if col not in existing_columns:
                    missing_columns.append(col)
            
            if missing_columns:
                errors.append(f'Missing columns: {missing_columns}')
            else:
                fixes_applied.append('All required columns exist')
        
        return JsonResponse({
            'fixes_applied': fixes_applied,
            'errors': errors,
            'status': 'completed'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'fixes_applied': fixes_applied,
            'errors': errors
        })

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
                domain = 'job-portal-23qb.onrender.com' if not settings.DEBUG else 'localhost:8000'
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
                interview = form.save()
                logger.info(f"Interview created successfully: {interview.id}")
                
                # Send email to candidate
                try:
                    # Generate full interview URL
                    domain = 'job-portal-23qb.onrender.com' if not settings.DEBUG else 'localhost:8000'
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
                    
                    success_message = f'Interview scheduled successfully! Email sent to {interview.candidate_email}.'
                    logger.info(f"Email sent successfully to {interview.candidate_email}")
                    
                except Exception as e:
                    logger.warning(f'Email sending failed: {str(e)}')
                    success_message = 'Interview scheduled successfully! Email could not be sent, but candidate can see the interview link on dashboard.'
                
                # Return JSON response for AJAX (modal submission)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': success_message,
                        'interview_id': interview.id
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
                    domain = 'job-portal-23qb.onrender.com' if not settings.DEBUG else 'localhost:8000'
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
        
        return render(request, 'jobapp/interview_ready.html', {
            'interview': interview,
        })
        
    except Exception as e:
        logger.error(f"Interview Ready Error: {e}")
        return HttpResponse(f'Interview ready page could not be loaded. Error: {str(e)}', status=500)






            
            
            
            
# @csrf_exempt
# def start_interview_by_uuid(request, interview_uuid):
#     try:
#         # Get the interview record
#         interview = get_object_or_404(Interview, uuid=interview_uuid)
        
#         # Handle both registered and unregistered candidates
#         if interview.is_registered_candidate:
#             # For registered candidates, use the User model
#             candidate_name = interview.candidate.get_full_name() or interview.candidate.username
#             job_title = interview.job.title or "Software Developer"
            
#             # Get resume file from candidate's profile with error handling
#             profile = getattr(interview.candidate, 'profile', None)
#             resume_file = profile.resume if profile and profile.resume else None
#             resume_text = ""
            
#             if resume_file:
#                 try:
#                     resume_text = extract_resume_text(resume_file)
#                 except Exception as e:
#                     resume_text = "Resume could not be processed."
#                     logger.warning(f"Resume extraction error for interview {interview_uuid}: {e}")
#             else:
#                 # For registered users without resume, use basic info
#                 resume_text = f"Candidate: {candidate_name}, applying for {job_title} position."
                
#         else:
#             # For unregistered candidates, use the stored candidate information
#             candidate_name = interview.candidate_name or "the candidate"
#             job_title = interview.job.title if interview.job else "Software Developer"
            
#             # Handle resume file for unregistered candidates
#             if hasattr(interview, 'candidate_resume') and interview.candidate_resume:
#                 try:
#                     resume_text = extract_resume_text(interview.candidate_resume)
#                 except Exception as e:
#                     resume_text = f"Resume could not be processed for {candidate_name}."
#                     logger.warning(f"Resume extraction error for unregistered candidate in interview {interview_uuid}: {e}")
#             else:
#                 # Create basic resume text from available information
#                 resume_text = f"Candidate: {candidate_name}"
#                 if hasattr(interview, 'candidate_email') and interview.candidate_email:
#                     resume_text += f", Email: {interview.candidate_email}"
#                 if hasattr(interview, 'candidate_phone') and interview.candidate_phone:
#                     resume_text += f", Phone: {interview.candidate_phone}"
#                 resume_text += f", applying for {job_title} position."
        
#         # Handle company name safely (works for both registered and unregistered)
#         try:
#             company_name = interview.job.company if interview.job else "Our Company"
#         except AttributeError:
#             company_name = "Our Company"

#         # Validate that we have minimum required information
#         if not resume_text.strip():
#             return HttpResponse(
#                 "Resume information not found. Please ensure your resume is uploaded or contact support.", 
#                 status=400
#             )
        
#         # Store interview context in session for consistency
#         request.session['interview_context'] = {
#             'candidate_name': candidate_name,
#             'job_title': job_title,
#             'company_name': company_name,
#             'resume_text': resume_text,
#             'job_description': interview.job.description if interview.job else "",
#             'job_location': interview.job.location if interview.job else "",
#             'question_count': 0,
#             'is_registered_candidate': interview.is_registered_candidate
#         }
        
#         # Initialize conversation history
#         request.session['conversation_history'] = []
        
#         if request.method == "POST":
#             # Handle both AJAX and regular form submissions
#             try:
#                 if request.content_type == 'application/json':
#                     data = json.loads(request.body)
#                     user_text = data.get("text") or data.get("message")
#                 else:
#                     user_text = request.POST.get("text", "")
#             except json.JSONDecodeError as e:
#                 logger.error(f"JSON decode error in interview {interview_uuid}: {e}")
#                 user_text = request.POST.get("text", "")
#             except Exception as e:
#                 logger.error(f"Unexpected error parsing request data in interview {interview_uuid}: {e}")
#                 user_text = request.POST.get("text", "")
            
#             if not user_text.strip():
#                 return JsonResponse({
#                     'error': 'Please provide a response.',
#                     'response': 'I didn\'t receive your answer. Could you please respond?',
#                     'audio': '',
#                     'success': False
#                 })
            
#             logger.info(f"User input for interview {interview_uuid}: {user_text}")
            
#             # Check for duplicate requests (prevent double processing)
#             last_processed = request.session.get('last_processed_input', '')
#             if last_processed == user_text:
#                 logger.warning(f"Duplicate request detected for interview {interview_uuid}, ignoring")
#                 return JsonResponse({
#                     'error': 'Duplicate request detected',
#                     'response': 'Please wait for the previous response to complete.',
#                     'success': False
#                 })
            
#             # Store current input to prevent duplicates
#             request.session['last_processed_input'] = user_text
            
#             # Get context from session
#             context = request.session.get('interview_context', {})
#             question_count = context.get('question_count', 0) + 1
            
#             # Update question count
#             context['question_count'] = question_count
#             request.session['interview_context'] = context
            
#             logger.info(f"Question count for interview {interview_uuid}: {question_count}")
            
#             # Handle "I can't hear" responses specifically
#             user_text_lower = user_text.lower().strip()
#             if any(phrase in user_text_lower for phrase in ['cant hear', "can't hear", 'cannot hear', 'cant listen', "can't listen", 'no audio', 'no sound']):
#                 logger.info(f"User reported audio issues in interview {interview_uuid}, providing text-based response")
                
#                 if question_count == 1:
#                     ai_response = f"I understand you're having audio issues. No problem! Your microphone is still working fine for me to hear you. Let me ask you in text: Could you please tell me about yourself and why you're interested in this {job_title} position at {company_name}?"
#                 elif question_count <= 8:
#                     ai_response = "I understand you can't hear the audio. That's okay! I can still hear you clearly through your microphone. Here's my next question: Can you describe a challenging project you've worked on and how you overcame the obstacles?"
#                 else:
#                     ai_response = "Thank you for letting me know about the audio issues. Your microphone is working perfectly for our conversation. What questions do you have about this role or our company?"
                
#                 # Force text-only response (no audio generation)
#                 response_data = {
#                     'response': ai_response,
#                     'audio': '',  # No audio
#                     'success': True,
#                     'question_count': question_count,
#                     'is_final': question_count >= 8,
#                     'text_only': True,  # Flag for frontend
#                     'microphone_note': 'Your microphone is working fine - I can hear you clearly'
#                 }
                
#                 return JsonResponse(response_data)
            
           

            
#             # Create contextual prompt based on conversation flow
#             if question_count < 8:
#                 # Build conversation context from session
#                 conversation_history = request.session.get('conversation_history', [])
                
#                 # Add current response to history
#                 conversation_history.append({
#                     'speaker': 'candidate',
#                     'message': user_text,
#                     'question_number': question_count
#                 })
                
#                 # Keep only last 4 exchanges to avoid token limits
#                 if len(conversation_history) > 8:  # 4 exchanges = 8 messages
#                     conversation_history = conversation_history[-8:]
                
#                 # Update session
#                 request.session['conversation_history'] = conversation_history
                
#                 # Build context string
#                 context_str = ""
#                 for entry in conversation_history[-6:]:  # Last 3 exchanges
#                     speaker = "Interviewer" if entry['speaker'] == 'interviewer' else "Candidate"
#                     context_str += f"{speaker}: {entry['message']}\n"
                
#                 # Create different prompts based on question number for variety
#                 if question_count == 1:
#                     prompt = f"""
# You are Alex, a friendly HR interviewer at {company_name}. The candidate just responded to your opening question.

# Candidate's response: "{user_text}"

# Now ask about their technical experience or a specific skill relevant to {job_title}. Keep it natural and conversational (2-3 sentences max).
# """
#                 elif question_count == 2:
#                     prompt = f"""
# You are Alex continuing the interview. Based on their previous responses:

# {context_str}

# Candidate just said: "{user_text}"

# Now ask about a challenging project they've worked on or a problem they've solved. Keep it conversational (2-3 sentences max).
# """
#                 elif question_count == 3:
#                     prompt = f"""
# You are Alex. Previous conversation:

# {context_str}

# Candidate just said: "{user_text}"

# Now ask about their teamwork experience or how they handle collaboration. Keep it natural (2-3 sentences max).
# """
#                 elif question_count == 4:
#                     prompt = f"""
# You are Alex. Previous conversation:

# {context_str}

# Candidate just said: "{user_text}"

# Now ask about their career goals or where they see themselves in the future. Keep it conversational (2-3 sentences max).
# """
#                 elif question_count == 5:
#                     prompt = f"""
# You are Alex. Previous conversation:

# {context_str}

# Candidate just said: "{user_text}"

# Now ask about how they stay updated with technology or handle learning new skills. Keep it natural (2-3 sentences max).
# """
#                 elif question_count == 6:
#                     prompt = f"""
# You are Alex. Previous conversation:

# {context_str}

# Candidate just said: "{user_text}"

# Now ask about their experience with specific technologies relevant to {job_title} or ask about a time they had to learn something quickly. Keep it conversational (2-3 sentences max).
# """
#                 else:  # question_count == 7
#                     prompt = f"""
# You are Alex. Previous conversation:

# {context_str}

# Candidate just said: "{user_text}"

# This is the second-to-last question. Ask if they have any questions about the role, company, or team. Keep it welcoming (2-3 sentences max).
# """
#             else:
#                 # This is the final question - generate results
#                 prompt = f"""
# You are Alex wrapping up the interview with {candidate_name}.

# The candidate just said: "{user_text}"

# INSTRUCTIONS:
# - Briefly acknowledge their final response
# - Thank them for their time
# - Mention next steps will be communicated soon
# - Keep it warm and professional (2-3 sentences max)

# Respond as Alex would naturally speak:
# """
                
#                 # Generate interview results after final response
#                 try:
#                     conversation_history = request.session.get('conversation_history', [])
#                     # Add the final candidate response to history before generating results
#                     conversation_history.append({
#                         'speaker': 'candidate',
#                         'message': user_text,
#                         'question_number': question_count
#                     })
                    
#                     logger.info(f"Generating final interview results for {interview_uuid} with {len(conversation_history)} conversation entries")
#                     generate_interview_results(interview, conversation_history)
#                     logger.info(f"Interview results generation completed for {interview_uuid}")
#                 except Exception as e:
#                     logger.error(f"Failed to generate interview results for {interview_uuid}: {e}")
#                     import traceback
#                     logger.error(f"Full traceback: {traceback.format_exc()}")
            
#             try:
#                 # Use shorter, faster AI prompts for immediate responses
#                 if question_count <= 3:
#                     ai_response = ask_ai_question(prompt, candidate_name, job_title, company_name)
#                 else:
#                     # Use pre-generated quick responses for later questions to speed up
#                     quick_responses = [
#                         "That's interesting! Tell me about your experience with teamwork and collaboration.",
#                         "Great! What are your career goals and where do you see yourself in 3-5 years?",
#                         "Excellent! How do you stay updated with new technologies in your field?",
#                         "Perfect! What questions do you have about this role or our company?",
#                         "Thank you for sharing that. Do you have any final questions for me?"
#                     ]
#                     ai_response = quick_responses[min(question_count - 4, len(quick_responses) - 1)]
#             except Exception as e:
#                 logger.error(f"AI API Error for interview {interview_uuid}: {e}")
#                 ai_response = "Thank you for that response. Can you tell me more about your experience?"
            
#             logger.info(f"AI Response for interview {interview_uuid}: {ai_response}")
            
#             # Add AI response to conversation history (for all questions including final)
#             conversation_history = request.session.get('conversation_history', [])
#             conversation_history.append({
#                 'speaker': 'interviewer',
#                 'message': ai_response,
#                 'question_number': question_count
#             })
#             request.session['conversation_history'] = conversation_history
            
#             # Generate TTS instantly - Force RunPod first, then gTTS fallback
#             audio_path = None
#             audio_duration = None
#             audio_generation_error = None
#             try:
#                 # Try ElevenLabs with your preferred voice first
#                 audio_path = generate_tts(ai_response, model="female_natural")
#                 if not audio_path:
#                     # Quick gTTS fallback if RunPod fails
#                     audio_path = generate_gtts_fallback(ai_response)
                
#                 # Get audio duration for typewriter sync
#                 if audio_path:
#                     from jobapp.tts import estimate_audio_duration, get_audio_duration
                    
#                     # Try to get actual duration first
#                     full_audio_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
#                     actual_duration = get_audio_duration(full_audio_path)
                    
#                     if actual_duration and actual_duration > 0:
#                         audio_duration = actual_duration
#                         logger.info(f"Using actual audio duration: {audio_duration} seconds")
#                     else:
#                         # Fallback to estimation
#                         audio_duration = estimate_audio_duration(ai_response)
#                         logger.info(f"Using estimated audio duration: {audio_duration} seconds")
#                 else:
#                     # No audio, estimate duration for typewriter effect
#                     from jobapp.tts import estimate_audio_duration
#                     audio_duration = estimate_audio_duration(ai_response)
#                     logger.info(f"No audio - using estimated duration for typewriter: {audio_duration} seconds")
                    
#             except Exception as e:
#                 logger.error(f"TTS generation failed for interview {interview_uuid}: {e}")
#                 audio_generation_error = str(e)
#                 audio_path = None
                
#                 # Still estimate duration for typewriter effect
#                 from jobapp.tts import estimate_audio_duration
#                 audio_duration = estimate_audio_duration(ai_response)
            
#             # Return JSON response for AJAX requests
#             response_data = {
#                 'response': ai_response,
#                 'audio': audio_path if audio_path else '',
#                 'audio_duration': audio_duration,  # Duration in seconds for typewriter sync
#                 'success': True,
#                 'question_count': question_count,
#                 'is_final': question_count >= 8,
#                 'audio_error': audio_generation_error if audio_generation_error else None
#             }
            
#             logger.info(f"Sending response for interview {interview_uuid}: question_count={question_count}")
#             logger.info(f"Response data: {response_data}")
            
#             # Clear duplicate prevention after successful processing
#             if 'last_processed_input' in request.session:
#                 del request.session['last_processed_input']
            
#             # Add CORS headers for better compatibility
#             response = JsonResponse(response_data)
#             response['Access-Control-Allow-Origin'] = '*'
#             response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
#             response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
#             return response

#         # GET: Show interview UI with first question
#         first_prompt = f"""
# You are Alex, a friendly HR interviewer at {company_name}. You're starting an interview with {candidate_name} for the {job_title} position.

# Resume highlights: {resume_text[:300]}

# INSTRUCTIONS:
# - Give a warm, professional greeting
# - Ask them to tell you about themselves and what drew them to this role
# - Keep it natural and conversational (2-3 sentences max)
# - Sound like a real human interviewer, not a robot
# - Be welcoming and put them at ease

# Respond as Alex would naturally speak:
# """        
        
#         try:
#             ai_question = ask_ai_question(first_prompt, candidate_name, job_title, company_name)
#         except Exception as e:
#             logger.error(f"AI API Error on initial question for interview {interview_uuid}: {e}")
#             ai_question = f"Hi {candidate_name}! Thanks for joining me today. Could you start by telling me a bit about yourself and what interests you about this {job_title} position?"
        
#         logger.info(f"Initial AI Question for interview {interview_uuid}: {ai_question}")
        
#         # Add initial question to conversation history
#         conversation_history = request.session.get('conversation_history', [])
#         conversation_history.append({
#             'speaker': 'interviewer',
#             'message': ai_question,
#             'question_number': 0
#         })
#         request.session['conversation_history'] = conversation_history
        
#         # Generate initial TTS - Force RunPod first
#         audio_path = None
#         audio_duration = None
#         try:
#             # Try ElevenLabs with your preferred voice for initial question
#             audio_path = generate_tts(ai_question, model="female_natural")
#             if not audio_path:
#                 # Quick gTTS fallback
#                 audio_path = generate_gtts_fallback(ai_question)
            
#             # Get audio duration for typewriter sync
#             if audio_path:
#                 from jobapp.tts import estimate_audio_duration, get_audio_duration
                
#                 # Try to get actual duration first
#                 full_audio_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
#                 actual_duration = get_audio_duration(full_audio_path)
                
#                 if actual_duration and actual_duration > 0:
#                     audio_duration = actual_duration
#                     logger.info(f"Initial question - using actual audio duration: {audio_duration} seconds")
#                 else:
#                     # Fallback to estimation
#                     audio_duration = estimate_audio_duration(ai_question)
#                     logger.info(f"Initial question - using estimated audio duration: {audio_duration} seconds")
#             else:
#                 # No audio, estimate duration for typewriter effect
#                 from jobapp.tts import estimate_audio_duration
#                 audio_duration = estimate_audio_duration(ai_question)
#                 logger.info(f"Initial question - no audio, using estimated duration: {audio_duration} seconds")
                
#         except Exception as e:
#             logger.error(f"Initial TTS generation failed for interview {interview_uuid}: {e}")
#             audio_path = None
            
#             # Still estimate duration for typewriter effect
#             from jobapp.tts import estimate_audio_duration
#             audio_duration = estimate_audio_duration(ai_question)

#         # Template context with proper audio handling
#         context_data = {
#             'interview': interview,
#             'ai_question': ai_question,
#             'audio_url': audio_path if audio_path else '',
#             'audio_duration': audio_duration,  # Duration for typewriter sync
#             'candidate_name': candidate_name,
#             'job_title': job_title,
#             'company_name': company_name,
#             'has_audio': bool(audio_path),  # Helper flag for template
#             'csrf_token': get_token(request),  # Ensure fresh CSRF token
#             'is_registered_candidate': interview.is_registered_candidate,  # Add this for template logic
#         }
        
#         logger.info(f"Template context for interview {interview_uuid} - audio_url: '{context_data['audio_url']}', has_audio: {context_data['has_audio']}")
        
#         return render(request, 'jobapp/interview_simple.html', context_data)
        
#     # Improved error handling with specific exception types
#     except Http404:
#         logger.error(f"Interview not found: {interview_uuid}")
#         return HttpResponse('Interview not found.', status=404)
    
#     except PermissionDenied as e:
#         if 'CSRF' in str(e) or 'csrf' in str(e).lower():
#             logger.error(f"CSRF error for interview {interview_uuid}: {e}")
#             return JsonResponse({
#                 'error': 'Session expired. Please refresh the page.',
#                 'response': 'Your session has expired. Please refresh the page to continue.',
#                 'success': False,
#                 'csrf_error': True,
#                 'refresh_required': True
#             }, status=403)
#         else:
#             logger.error(f"Permission denied for interview: {interview_uuid}")
#             return HttpResponse('You do not have permission to access this interview.', status=403)
    
#     except ValidationError as e:
#         logger.error(f"Validation error for interview {interview_uuid}: {e}")
#         return HttpResponse(f'Invalid data: {str(e)}', status=400)
    
#     except ConnectionError as e:
#         logger.error(f"Connection error for interview {interview_uuid}: {e}")
#         return HttpResponse('Unable to connect to required services. Please try again later.', status=503)
    
#     except TimeoutError as e:
#         logger.error(f"Timeout error for interview {interview_uuid}: {e}")
#         return HttpResponse('Request timed out. Please try again.', status=504)
    
#     except Exception as e:
#         # Enhanced error logging with more context
#         import traceback
#         error_details = {
#             'interview_uuid': interview_uuid,
#             'error_type': type(e).__name__,
#             'error_message': str(e),
#             'traceback': traceback.format_exc(),
#             'request_method': request.method,
#             'user': getattr(request.user, 'id', 'Anonymous') if hasattr(request, 'user') else 'Unknown',
#             'session_key': request.session.session_key if hasattr(request, 'session') else 'Unknown'
#         }
        
#         logger.error(f"Interview Error Details: {error_details}")
        
#         # For development, show detailed error
#         if settings.DEBUG:
#             return HttpResponse(
#                 f'Interview could not be started.<br>'
#                 f'Error Type: {error_details["error_type"]}<br>'
#                 f'Error: {error_details["error_message"]}<br>'
#                 f'UUID: {interview_uuid}<br>'
#                 f'<pre>{error_details["traceback"]}</pre>',
#                 status=500
#             )
#         else:
#             # For production, show generic error
#             return HttpResponse(
#                 'Interview could not be started. Our team has been notified and is working to resolve the issue.',
#                 status=500
#             )            


# EMERGENCY FIX - Replace your start_interview_by_uuid function with this version
# This removes the AI API dependency that's causing timeouts



#this is the  secondly version of interview function .
# @csrf_exempt
# def start_interview_by_uuid(request, interview_uuid):
#     try:
#         # Get the interview record
#         interview = get_object_or_404(Interview, uuid=interview_uuid)
        
#         # Handle both registered and unregistered candidates
#         if interview.is_registered_candidate:
#             candidate_name = interview.candidate.get_full_name() or interview.candidate.username
#             job_title = interview.job.title or "Software Developer"
            
#             profile = getattr(interview.candidate, 'profile', None)
#             resume_file = profile.resume if profile and profile.resume else None
#             resume_text = ""
            
#             if resume_file:
#                 try:
#                     resume_text = extract_resume_text(resume_file)
#                 except Exception as e:
#                     resume_text = "Resume could not be processed."
#                     logger.warning(f"Resume extraction error for interview {interview_uuid}: {e}")
#             else:
#                 resume_text = f"Candidate: {candidate_name}, applying for {job_title} position."
                
#         else:
#             candidate_name = interview.candidate_name or "the candidate"
#             job_title = interview.job.title if interview.job else "Software Developer"
            
#             if hasattr(interview, 'candidate_resume') and interview.candidate_resume:
#                 try:
#                     resume_text = extract_resume_text(interview.candidate_resume)
#                 except Exception as e:
#                     resume_text = f"Resume could not be processed for {candidate_name}."
#                     logger.warning(f"Resume extraction error for unregistered candidate in interview {interview_uuid}: {e}")
#             else:
#                 resume_text = f"Candidate: {candidate_name}"
#                 if hasattr(interview, 'candidate_email') and interview.candidate_email:
#                     resume_text += f", Email: {interview.candidate_email}"
#                 if hasattr(interview, 'candidate_phone') and interview.candidate_phone:
#                     resume_text += f", Phone: {interview.candidate_phone}"
#                 resume_text += f", applying for {job_title} position."
        
#         try:
#             company_name = interview.job.company if interview.job else "Our Company"
#         except AttributeError:
#             company_name = "Our Company"

#         if not resume_text.strip():
#             return HttpResponse(
#                 "Resume information not found. Please ensure your resume is uploaded or contact support.", 
#                 status=400
#             )
        
#         # Store interview context in session
#         request.session['interview_context'] = {
#             'candidate_name': candidate_name,
#             'job_title': job_title,
#             'company_name': company_name,
#             'resume_text': resume_text,
#             'job_description': interview.job.description if interview.job else "",
#             'job_location': interview.job.location if interview.job else "",
#             'question_count': 0,
#             'is_registered_candidate': interview.is_registered_candidate
#         }
        
#         # Initialize conversation history
#         request.session['conversation_history'] = []
        
#         if request.method == "POST":
#             # Handle candidate response
#             try:
#                 if request.content_type == 'application/json':
#                     data = json.loads(request.body)
#                     user_text = data.get("text") or data.get("message")
#                 else:
#                     user_text = request.POST.get("text", "")
#             except json.JSONDecodeError as e:
#                 logger.error(f"JSON decode error in interview {interview_uuid}: {e}")
#                 user_text = request.POST.get("text", "")
#             except Exception as e:
#                 logger.error(f"Unexpected error parsing request data in interview {interview_uuid}: {e}")
#                 user_text = request.POST.get("text", "")
            
#             if not user_text.strip():
#                 return JsonResponse({
#                     'error': 'Please provide a response.',
#                     'response': 'I didn\'t receive your answer. Could you please respond?',
#                     'audio': '',
#                     'success': False
#                 })
            
#             logger.info(f"User input for interview {interview_uuid}: {user_text}")
            
#             # Prevent duplicate processing
#             last_processed = request.session.get('last_processed_input', '')
#             if last_processed == user_text:
#                 logger.warning(f"Duplicate request detected for interview {interview_uuid}, ignoring")
#                 return JsonResponse({
#                     'error': 'Duplicate request detected',
#                     'response': 'Please wait for the previous response to complete.',
#                     'success': False
#                 })
            
#             request.session['last_processed_input'] = user_text
            
#             # Get context from session
#             context = request.session.get('interview_context', {})
#             question_count = context.get('question_count', 0) + 1
            
#             # Update question count
#             context['question_count'] = question_count
#             request.session['interview_context'] = context
            
#             logger.info(f"Question count for interview {interview_uuid}: {question_count}")
            
#             # EMERGENCY FIX: Use pre-defined questions instead of AI API
#             predefined_questions = {
#                 1: f"That's great to hear! Can you tell me more about your technical experience with {job_title} technologies? What programming languages or tools have you been working with recently?",
#                 2: "Interesting! Can you walk me through a challenging project you've worked on recently? I'd love to hear about the obstacles you faced and how you overcame them.",
#                 3: "That sounds like a great approach to problem-solving! How do you typically work in a team environment? Can you give me an example of how you've collaborated with others on a project?",
#                 4: "Excellent teamwork skills! Where do you see yourself in the next 3-5 years? What are your career goals and how does this position fit into them?",
#                 5: "Those are great career aspirations! How do you stay updated with the latest technologies and trends in your field? Do you have any preferred learning methods?",
#                 6: f"That's a great way to stay current! Given this {job_title} role, do you have experience with any specific technologies or frameworks that would be relevant? How do you typically approach learning new tools or technologies?",
#                 7: f"Thank you for sharing that! Before we wrap up, do you have any questions about this {job_title} position, our company culture, or the team you'd be working with?",
#                 8: f"Thank you for those great questions, {candidate_name}! I really enjoyed our conversation today. We'll review everything we discussed and get back to you with next steps within the next few days."
#             }
            
#             # Get the appropriate question
#             if question_count <= 8:
#                 ai_response = predefined_questions.get(question_count, "Can you tell me more about that?")
#             else:
#                 ai_response = predefined_questions[8]  # Final question
            
#             logger.info(f"Using predefined question {question_count} for interview {interview_uuid}: {ai_response}")
            
#             # Build conversation history
#             conversation_history = request.session.get('conversation_history', [])
            
#             # Add current response to history
#             conversation_history.append({
#                 'speaker': 'candidate',
#                 'message': user_text,
#                 'question_number': question_count
#             })
            
#             # Add AI response to history
#             conversation_history.append({
#                 'speaker': 'interviewer',
#                 'message': ai_response,
#                 'question_number': question_count
#             })
            
#             # Keep only last 8 exchanges
#             if len(conversation_history) > 16:  # 8 exchanges = 16 messages
#                 conversation_history = conversation_history[-16:]
            
#             request.session['conversation_history'] = conversation_history
            
#             # Generate final results if this is the last question
#             if question_count >= 8:
#                 try:
#                     logger.info(f"Generating final interview results for {interview_uuid}")
#                     generate_interview_results(interview, conversation_history)
#                     logger.info(f"Interview results generation completed for {interview_uuid}")
#                 except Exception as e:
#                     logger.error(f"Failed to generate interview results for {interview_uuid}: {e}")
            
#             # Generate TTS audio
#             audio_path = None
#             audio_duration = None
#             try:
#                 logger.info(f"Starting TTS generation for interview {interview_uuid}")
#                 audio_path = generate_tts(ai_response, model="female_natural")
#                 if not audio_path:
#                     logger.info(f"ElevenLabs failed, trying gTTS fallback for interview {interview_uuid}")
#                     audio_path = generate_gtts_fallback(ai_response)
                
#                 if audio_path:
#                     from jobapp.tts import estimate_audio_duration, get_audio_duration
#                     full_audio_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
#                     actual_duration = get_audio_duration(full_audio_path)
                    
#                     if actual_duration and actual_duration > 0:
#                         audio_duration = actual_duration
#                         logger.info(f"Using actual audio duration: {audio_duration} seconds")
#                     else:
#                         audio_duration = estimate_audio_duration(ai_response)
#                         logger.info(f"Using estimated audio duration: {audio_duration} seconds")
#                 else:
#                     from jobapp.tts import estimate_audio_duration
#                     audio_duration = estimate_audio_duration(ai_response)
#                     logger.info(f"No audio - using estimated duration: {audio_duration} seconds")
                    
#             except Exception as e:
#                 logger.error(f"TTS generation failed for interview {interview_uuid}: {e}")
#                 audio_path = None
#                 try:
#                     from jobapp.tts import estimate_audio_duration
#                     audio_duration = estimate_audio_duration(ai_response)
#                 except:
#                     audio_duration = len(ai_response.split()) * 0.5
            
#             # Return response
#             response_data = {
#                 'response': ai_response,
#                 'audio': audio_path if audio_path else '',
#                 'audio_duration': audio_duration,
#                 'success': True,
#                 'question_count': question_count,
#                 'is_final': question_count >= 8,
#                 'using_predefined': True  # Flag to indicate we're using predefined questions
#             }
            
#             logger.info(f"Sending predefined response for interview {interview_uuid}: question_count={question_count}")
            
#             # Clear duplicate prevention
#             if 'last_processed_input' in request.session:
#                 del request.session['last_processed_input']
            
#             response = JsonResponse(response_data)
#             response['Access-Control-Allow-Origin'] = '*'
#             response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
#             response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
#             return response

#         # GET request - show interview UI with first question
#         # EMERGENCY FIX: Use predefined first question instead of AI API
#         ai_question = f"Hi {candidate_name}! Thanks for joining me today. Could you start by telling me a bit about yourself and what interests you about this {job_title} position at {company_name}?"
        
#         logger.info(f"Initial predefined question for interview {interview_uuid}: {ai_question}")
        
#         # Add initial question to conversation history
#         conversation_history = request.session.get('conversation_history', [])
#         conversation_history.append({
#             'speaker': 'interviewer',
#             'message': ai_question,
#             'question_number': 0
#         })
#         request.session['conversation_history'] = conversation_history
        
#         # Generate initial TTS
#         audio_path = None
#         audio_duration = None
#         try:
#             audio_path = generate_tts(ai_question, model="female_natural")
#             if not audio_path:
#                 audio_path = generate_gtts_fallback(ai_question)
            
#             if audio_path:
#                 from jobapp.tts import estimate_audio_duration, get_audio_duration
#                 full_audio_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
#                 actual_duration = get_audio_duration(full_audio_path)
                
#                 if actual_duration and actual_duration > 0:
#                     audio_duration = actual_duration
#                     logger.info(f"Initial question - using actual audio duration: {audio_duration} seconds")
#                 else:
#                     audio_duration = estimate_audio_duration(ai_question)
#                     logger.info(f"Initial question - using estimated audio duration: {audio_duration} seconds")
#             else:
#                 from jobapp.tts import estimate_audio_duration
#                 audio_duration = estimate_audio_duration(ai_question)
#                 logger.info(f"Initial question - no audio, using estimated duration: {audio_duration} seconds")
                
#         except Exception as e:
#             logger.error(f"Initial TTS generation failed for interview {interview_uuid}: {e}")
#             audio_path = None
#             from jobapp.tts import estimate_audio_duration
#             audio_duration = estimate_audio_duration(ai_question)

#         # Template context
#         context_data = {
#             'interview': interview,
#             'ai_question': ai_question,
#             'audio_url': audio_path if audio_path else '',
#             'audio_duration': audio_duration,
#             'candidate_name': candidate_name,
#             'job_title': job_title,
#             'company_name': company_name,
#             'has_audio': bool(audio_path),
#             'csrf_token': get_token(request),
#             'is_registered_candidate': interview.is_registered_candidate,
#         }
        
#         logger.info(f"Template context for interview {interview_uuid} - audio_url: '{context_data['audio_url']}', has_audio: {context_data['has_audio']}")
        
#         return render(request, 'jobapp/interview_simple.html', context_data)
        
#     except Http404:
#         logger.error(f"Interview not found: {interview_uuid}")
#         return HttpResponse('Interview not found.', status=404)
    
#     except Exception as e:
#         import traceback
#         error_details = {
#             'interview_uuid': interview_uuid,
#             'error_type': type(e).__name__,
#             'error_message': str(e),
#             'traceback': traceback.format_exc(),
#             'request_method': request.method,
#         }
        
#         logger.error(f"Interview Error Details: {error_details}")
        
#         if settings.DEBUG:
#             return HttpResponse(
#                 f'Interview error.<br>'
#                 f'Error: {error_details["error_message"]}<br>'
#                 f'<pre>{error_details["traceback"]}</pre>',
#                 status=500
#             )
#         else:
#             return HttpResponse(
#                 'Interview system temporarily unavailable. Please try again in a few minutes.',
#                 status=500
#             )



@csrf_exempt
def start_interview_by_uuid(request, interview_uuid):
    try:
        # Get the interview record
        interview = get_object_or_404(Interview, uuid=interview_uuid)
        
        # Handle both registered and unregistered candidates
        if interview.is_registered_candidate:
            candidate_name = interview.candidate.get_full_name() or interview.candidate.username
            job_title = interview.job.title or "Software Developer"
            
            profile = getattr(interview.candidate, 'profile', None)
            resume_file = profile.resume if profile and profile.resume else None
            resume_text = ""
            
            if resume_file:
                try:
                    resume_text = extract_resume_text(resume_file)
                except Exception as e:
                    resume_text = "Resume could not be processed."
                    logger.warning(f"Resume extraction error for interview {interview_uuid}: {e}")
            else:
                resume_text = f"Candidate: {candidate_name}, applying for {job_title} position."
                
        else:
            candidate_name = interview.candidate_name or "the candidate"
            job_title = interview.job.title if interview.job else "Software Developer"
            
            if hasattr(interview, 'candidate_resume') and interview.candidate_resume:
                try:
                    resume_text = extract_resume_text(interview.candidate_resume)
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
        
        if session_key not in request.session:
            logger.info(f"Created new session context for interview {interview_uuid}")
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
                'started_at': timezone.now().isoformat()
            }
        
        request.session.modified = True
        
        # HANDLE POST REQUEST
        if request.method == "POST":
            try:
                if request.content_type == 'application/json':
                    data = json.loads(request.body)
                    user_text = data.get("text") or data.get("message")
                else:
                    user_text = request.POST.get("text", "")
            except:
                user_text = request.POST.get("text", "")
    
            if not user_text.strip():
                return JsonResponse({
                    'error': 'Please provide a response.',
                    'response': 'I didn\'t receive your answer. Could you please respond?',
                    'audio': '',
                    'success': False
                })
    
            logger.info(f"User input for interview {interview_uuid}: {user_text}")
    
            # Prevent duplicate processing
            last_processed = request.session.get('last_processed_input', '')
            if last_processed == user_text:
                logger.warning(f"Duplicate request detected for interview {interview_uuid}, ignoring")
                return JsonResponse({
                    'error': 'Duplicate request detected',
                    'response': 'Please wait for the previous response to complete.',
                    'success': False
                })
    
            request.session['last_processed_input'] = user_text
    
            # Get current question count and increment properly
            context = request.session.get(session_key, {})
            current_count = context.get('question_count', 0)
            question_count = current_count + 1
    
            # Save incremented count back to session IMMEDIATELY
            context['question_count'] = question_count
            request.session[session_key] = context
            request.session.modified = True
    
            logger.info(f"Question count incremented from {current_count} to {question_count} for interview {interview_uuid}")
    
            # Build conversation history
            conversation_history = context.get('conversation_history', [])
            conversation_history.append({
                'speaker': 'candidate',
                'message': user_text,
                'question_number': question_count
            })
    
            # Check for audio issues in candidate response
            user_text_lower = user_text.lower().strip()
            audio_issue_phrases = [
                'can you hear me', 'cant hear', "can't hear", 'cannot hear', 
                'cant listen', "can't listen", 'no audio', 'no sound',
                'hello can you hear', 'audio problem', 'sound problem'
            ]
            
            is_audio_issue = any(phrase in user_text_lower for phrase in audio_issue_phrases)
            
            if is_audio_issue:
                logger.info(f"Audio issue detected for interview {interview_uuid}: {user_text}")
                
                if question_count == 1:
                    ai_response = f"Yes, I can hear you perfectly, {candidate_name}! Your microphone is working great. Let me ask you the first question: Can you tell me about yourself and your experience with {job_title} technologies?"
                elif question_count <= 4:
                    ai_response = f"I can hear you clearly, {candidate_name}! Your audio is working fine on my end. Let me continue with our interview questions."
                else:
                    ai_response = f"Yes, I can hear you well, {candidate_name}! Don't worry about the audio - our interview is going smoothly. Let me ask you another question."
                
                logger.info(f"Using audio issue response for question {question_count}")
            
            else:
                # Use predefined questions for reliability
                predefined_questions = {
                    1: f"That's great to hear! Can you tell me more about your technical experience with {job_title} technologies? What programming languages or tools have you been working with recently?",
                    2: "Interesting! Can you walk me through a challenging project you've worked on recently? I'd love to hear about the obstacles you faced and how you overcame them.",
                    3: "That sounds like a great approach to problem-solving! How do you typically work in a team environment? Can you give me an example of how you've collaborated with others on a project?",
                    4: "Excellent teamwork skills! Where do you see yourself in the next 3-5 years? What are your career goals and how does this position fit into them?",
                    5: "Those are great career aspirations! How do you stay updated with the latest technologies and trends in your field? Do you have any preferred learning methods?",
                    6: f"That's a great way to stay current! Given this {job_title} role, do you have experience with any specific technologies or frameworks that would be relevant? How do you typically approach learning new tools or technologies?",
                    7: f"Thank you for sharing that! Before we wrap up, do you have any questions about this {job_title} position, our company culture, or the team you'd be working with?",
                    8: f"Thank you for those great questions, {candidate_name}! I really enjoyed our conversation today. We'll review everything we discussed and get back to you with next steps within the next few days."
                }
        
                if question_count <= 8:
                    ai_response = predefined_questions.get(question_count, "Can you tell me more about that?")
                    logger.info(f"Using predefined question {question_count}: {ai_response[:50]}...")
                else:
                    ai_response = f"Thank you for the interview, {candidate_name}! We'll be in touch soon."
                    logger.info(f"Interview complete for {interview_uuid}")
    
            # Add AI response to history
            conversation_history.append({
                'speaker': 'interviewer',
                'message': ai_response,
                'question_number': question_count
            })
    
            # Keep conversation history manageable
            if len(conversation_history) > 16:
                conversation_history = conversation_history[-16:]
                
            context['conversation_history'] = conversation_history
            request.session[session_key] = context
            request.session.modified = True
    
            # Generate final results if interview is complete
            if question_count >= 8:
                try:
                    logger.info(f"Generating final interview results for {interview_uuid}")
                    generate_interview_results(interview, conversation_history)
                    logger.info(f"Interview results generation completed for {interview_uuid}")
                except Exception as e:
                    logger.error(f"Failed to generate interview results for {interview_uuid}: {e}")
        
            # Generate TTS audio
            audio_path = None
            audio_duration = None
            try:
                logger.info(f"Starting TTS generation for interview {interview_uuid}")
                logger.info(f"Using gTTS fallback due to ElevenLabs issues")
                
                from jobapp.tts import generate_tts                 
                audio_path = generate_tts(ai_response, model="female_interview")
                
                if audio_path:
                    from jobapp.tts import estimate_audio_duration, get_audio_duration
                    full_audio_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                    actual_duration = get_audio_duration(full_audio_path)
            
                    if actual_duration and actual_duration > 0:
                        audio_duration = actual_duration
                        logger.info(f"Initial question - using actual audio duration: {audio_duration} seconds")
                    else:
                        audio_duration = estimate_audio_duration(ai_response)
                        logger.info(f"Using estimated audio duration: {audio_duration} seconds")
                else:
                    from jobapp.tts import estimate_audio_duration
                    audio_duration = estimate_audio_duration(ai_response)
                    logger.info(f"No audio - using estimated duration: {audio_duration} seconds")
                    
            except Exception as e:
                logger.error(f"TTS generation failed for interview {interview_uuid}: {e}")
                audio_path = None
                try:
                    from jobapp.tts import estimate_audio_duration
                    audio_duration = estimate_audio_duration(ai_response)
                except:
                    audio_duration = 30.0
    
            # Return response data
            response_data = {
                'response': ai_response,
                'audio': audio_path if audio_path else '',
                'audio_duration': audio_duration,
                'success': True,
                'question_count': question_count,
                'is_final': question_count >= 8,
                'audio_issue_handled': is_audio_issue
            }
    
            logger.info(f"Sending response for interview {interview_uuid}: question_count={question_count}")
    
            # Clear duplicate prevention
            if 'last_processed_input' in request.session:
                del request.session['last_processed_input']
            
            response = JsonResponse(response_data)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
            return response
        
        # HANDLE GET REQUEST - Show interview UI with first question
        ai_question = f"Hi {candidate_name}, great to meet you and thanks for joining me today! I'm excited to learn more about you. Could you start by telling me a bit about yourself and what interests you about this {job_title} position at {company_name}?"
        
        logger.info(f"Generated AI initial question for interview {interview_uuid}")
        
        # Add initial question to context conversation history
        context = request.session.get(session_key, {})
        conversation_history = context.get('conversation_history', [])
        conversation_history.append({
            'speaker': 'interviewer',
            'message': ai_question,
            'question_number': 0
        })
        
        context['conversation_history'] = conversation_history
        request.session[session_key] = context
        request.session.modified = True
        
        # Generate initial TTS
        audio_path = None
        audio_duration = None
        try:
            logger.info(f"Starting initial TTS generation for interview {interview_uuid}")
            logger.info(f"Using gTTS fallback due to ElevenLabs issues")
            
            from jobapp.tts import generate_tts
            audio_path = generate_tts(ai_question, model="female_interview")
            
            if audio_path:
                from jobapp.tts import estimate_audio_duration, get_audio_duration
                full_audio_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                actual_duration = get_audio_duration(full_audio_path)
                
                if actual_duration and actual_duration > 0:
                    audio_duration = actual_duration
                    logger.info(f"Initial question - using actual audio duration: {audio_duration} seconds")
                else:
                    audio_duration = estimate_audio_duration(ai_question)
                    logger.info(f"Initial question - using estimated audio duration: {audio_duration} seconds")
            else:
                from jobapp.tts import estimate_audio_duration
                audio_duration = estimate_audio_duration(ai_question)
                logger.info(f"Initial question - no audio, using estimated duration: {audio_duration} seconds")
                
        except Exception as e:
            logger.error(f"Initial TTS generation failed for interview {interview_uuid}: {e}")
            audio_path = None
            try:
                from jobapp.tts import estimate_audio_duration
                audio_duration = estimate_audio_duration(ai_question)
            except:
                audio_duration = 30.0

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
        
        logger.info(f"Template context for interview {interview_uuid} - audio_url: '{context_data['audio_url']}', has_audio: {context_data['has_audio']}")
        
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
        
        logger.error(f"Interview Error Details: {error_details}")
        
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

def contact_view(request):
    return render(request, 'jobapp/contact.html')



# testimonials

def testimonials_view(request):
    return render(request, 'jobapp/testimonials.html')



# About View
def about_view(request):
    return render(request, 'jobapp/about.html')



# FAQ view
def faq_view(request):
    return render(request, 'jobapp/faq.html')


# Blog
def blog_view(request):
    return render(request, 'jobapp/blog.html')



# blog single
def blog_single_view(request):
    """Display single blog post"""
    return render(request, 'jobapp/blog_single.html')




        
            
def debug_db(request):
    try:
        db_url = os.environ.get('DATABASE_URL', 'Not found')
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "Database connection: OK"
        
        return HttpResponse(f'''
        DATABASE_URL: {db_url[:50]}...<br>
        {db_status}<br>
        Environment: {os.environ.get('RENDER', 'Local')}
        ''')
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}')           
           
        
        
# for tts checking   
def chat_view(request):
    if request.method == "POST":
        try:
            # Handle both form data and JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                user_input = data.get("message")
            else:
                user_input = request.POST.get("message")
            
            if not user_input:
                return JsonResponse({"error": "No message provided"}, status=400)
            
            print(f"🔵 User input: {user_input}")
            
            # Your AI/chatbot logic here
            response_text = f" {user_input}. "
            
            # Generate TTS audio
            print("🔵 Generating TTS...")
            audio_path = generate_tts(response_text)
            print(f"🔵 TTS result: {audio_path}")
            
            # Return JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if audio_path:
                    print(f"✅ Returning audio path: {audio_path}")
                else:
                    print("❌ No audio path generated")
                    
                return JsonResponse({
                    "response": response_text,
                    "audio_path": audio_path,
                    "success": True
                })
            
            # Return template for regular requests
            return render(request, "jobapp/chat.html", {
                "response": response_text,
                "audio_path": audio_path,
                "user_input": user_input
            })
            
        except Exception as e:
            print(f"❌ Error in chat_view: {str(e)}")
            return JsonResponse({"error": "Internal server error"}, status=500)
    
    return render(request, "jobapp/chat.html")


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

# TTS test endpoint
@csrf_exempt
def test_tts(request):
    """Test TTS generation system with ElevenLabs voice support"""
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                text = data.get('text', 'This is a test of the text to speech system')
                voice = data.get('voice', 'female_professional')
            else:
                text = request.POST.get('text', 'This is a test of the text to speech system')
                voice = request.POST.get('voice', 'female_professional')
            
            logger.info(f"TTS test requested with text: '{text}' and voice: '{voice}'")
            
            # Test TTS generation with specified voice
            from jobapp.tts import generate_tts, check_tts_system
            
            # Run system health check
            health_info = check_tts_system()
            logger.info(f"TTS system health: {health_info}")
            
            # Test generation with voice model
            audio_path = generate_tts(text, model=voice)
            
            # Determine which service was used
            service_used = 'Unknown'
            if audio_path:
                if 'elevenlabs' in audio_path:
                    service_used = 'ElevenLabs'
                elif 'gtts' in audio_path:
                    service_used = 'gTTS (Fallback)'
            
            response_data = {
                'success': bool(audio_path),
                'audio_url': audio_path if audio_path else None,
                'text': text,
                'voice': voice,
                'service_used': service_used,
                'health_check': health_info,
                'message': f'TTS test completed successfully using {service_used}' if audio_path else 'TTS test failed'
            }
            
            logger.info(f"TTS test result: {response_data}")
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"TTS test error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'TTS test failed with error'
            }, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

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

# Test authentication view
@login_required
def test_recruiter_auth(request):
    """Simple test view to check recruiter authentication"""
    user_info = {
        'user_id': request.user.id,
        'username': request.user.username,
        'is_authenticated': request.user.is_authenticated,
        'is_recruiter': getattr(request.user, 'is_recruiter', 'Field not found'),
        'user_type': type(request.user).__name__,
        'groups': list(request.user.groups.values_list('name', flat=True)) if hasattr(request.user, 'groups') else 'No groups'
    }
    
    return HttpResponse(f"""
    <h2>Authentication Test</h2>
    <pre>{user_info}</pre>
    <p><a href="/schedule-interview/1/2/">Test Schedule Interview Link</a></p>
    """)



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

# Test application form view
@login_required
def test_apply_form(request, job_id):
    """Test view for debugging application form"""
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        logger.info(f"TEST: Form submitted with POST: {request.POST}")
        logger.info(f"TEST: Files submitted: {request.FILES}")
        
        form = ApplicationForm(request.POST, request.FILES)
        logger.info(f"TEST: Form is bound: {form.is_bound}")
        logger.info(f"TEST: Form is valid: {form.is_valid()}")
        logger.info(f"TEST: Form errors: {form.errors}")
        
        if form.is_valid():
            messages.success(request, 'Form is valid!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ApplicationForm()
    
    return render(request, 'jobapp/test_apply.html', {'form': form, 'job': job})



def debug_database_structure(request):
    """Debug view to see exact database structure"""
    try:
        with connection.cursor() as cursor:
            # Get all jobapp tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name LIKE 'jobapp_%'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            table_details = {}
            
            for table in tables:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, [table])
                
                columns = []
                for col in cursor.fetchall():
                    columns.append({
                        'name': col[0],
                        'type': col[1],
                        'nullable': col[2],
                        'default': col[3]
                    })
                
                table_details[table] = columns
            
            return JsonResponse({
                'status': 'success',
                'tables': tables,
                'details': table_details
            }, indent=2)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
        

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



@login_required
@user_passes_test(lambda u: u.is_recruiter)
def test_interview_results(request):
    """Test view to create sample interview results"""
    try:
        # Get the first interview for this recruiter
        interview = Interview.objects.filter(
            job__posted_by=request.user
        ).first()
        
        if not interview:
            return JsonResponse({
                'success': False,
                'message': 'No interviews found for testing'
            })
        
        # Create sample conversation history with more realistic data
        sample_conversation = [
            {'speaker': 'interviewer', 'message': 'Hello! Thanks for joining me today. Could you start by telling me a bit about yourself and what interests you about this position?', 'question_number': 1},
            {'speaker': 'candidate', 'message': 'Hi! I am a software developer with 3 years of experience in full-stack development. I have worked extensively with Python, Django, JavaScript, and React. I am particularly interested in this position because it offers opportunities to work on challenging projects and grow my skills in cloud technologies.', 'question_number': 1},
            {'speaker': 'interviewer', 'message': 'That sounds great! Can you tell me about a challenging project you have worked on recently and how you approached solving the problems you encountered?', 'question_number': 2},
            {'speaker': 'candidate', 'message': 'Recently, I worked on a e-commerce platform where we had performance issues with the database queries. I identified the bottlenecks using profiling tools, optimized the queries by adding proper indexes, and implemented caching strategies using Redis. This reduced the page load time by 60%.', 'question_number': 2},
            {'speaker': 'interviewer', 'message': 'Excellent problem-solving approach! How do you handle working in a team environment, especially when there are conflicting opinions on technical decisions?', 'question_number': 3},
            {'speaker': 'candidate', 'message': 'I believe in open communication and data-driven decisions. When there are conflicting opinions, I try to understand different perspectives, present the pros and cons of each approach, and if needed, create small prototypes to test the solutions. I also value team consensus and am willing to compromise when it benefits the overall project.', 'question_number': 3},
        ]
        
        # Generate results
        generate_interview_results(interview, sample_conversation)
        
        return JsonResponse({
            'success': True,
            'message': f'Test results generated for interview {interview.uuid}',
            'interview_id': str(interview.uuid),
            'candidate_name': interview.candidate_name,
            'job_title': interview.job.title if interview.job else 'N/A'
        })
        
    except Exception as e:
        logger.error(f"Test interview results failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
        
        
        
     
     
     
# Add this function in your views.py file:
def generate_interview_results(interview, conversation_history):
    """Generate and save interview results"""
    try:
        logger.info(f"Interview completed for {interview.uuid} with {len(conversation_history)} exchanges")
        
        # Count responses
        candidate_responses = [entry for entry in conversation_history if entry['speaker'] == 'candidate']
        
        # Update interview status
        interview.status = 'completed'
        interview.completed_at = timezone.now()
        interview.save()
        
        logger.info(f"Interview results saved for interview {interview.uuid}")
        return True
    except Exception as e:
        logger.error(f"Error generating interview results: {e}")
        return False        
        
        
        
        
      