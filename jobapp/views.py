from django.shortcuts import render,redirect, get_object_or_404 , HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, LoginForm , ProfileForm, JobForm, ApplicationForm
from .models import CustomUser , Profile, Job, Application , Interview, Candidate
from django.contrib.auth.decorators import login_required , user_passes_test 
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden , JsonResponse, Http404, FileResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.middleware.csrf import CsrfViewMiddleware
from django.db.models import Q
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
from jobapp.tts import generate_tts, generate_gtts_fallback
import json
from django.conf import settings
import logging

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
    def ask_ai_question(prompt, candidate_name=None, job_title=None, company_name=None):
        return "AI service is currently unavailable. Please try again later."
    def extract_resume_text(resume_file):
        return "Resume processing is currently unavailable."

from gtts import gTTS

from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
import uuid










# Create your views here.

def home_view(request):
    return render(request, 'jobapp/home.html')



def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # ✅ Tell Django which backend to use
            backend = get_backends()[0]  # Use the first available backend (your default one)
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user)
            return redirect('Profile_update')  # Redirect to profile page
        else:
            pass  # Form errors
    else:
        form = UserRegistrationForm() # Show empty form on GET request
    return render(request, 'registration/register.html', {'form': form}) # ✅ Always return something
    
    
    

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # Redirect based on user type
                if user.is_recruiter:
                    return redirect('recruiter_dashboard')  # or create a recruiter dashboard
                else:
                    return redirect('Profile_update')
            else:
                form.add_error(None, 'invalid credentials')
                
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  #or any page you want to go after logout     



@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('jobseeker_dashboard') #or anywhere you want so  -to dashboard
    else:
        form = ProfileForm(instance=profile)
        
    return render(request, 'jobapp/profile_update.html', {'form': form})    


  

# post job view for recruiter only 
@login_required
def post_job(request):
    if not request.user.is_recruiter:
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('login')
        
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_list')
        else:
            # If form is not valid, show errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobForm()
        
    return render(request, 'jobapp/post_job.html', {'form': form})

# Job List view
def job_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = Job.objects.filter(title__icontains=search_query)
        no_results = not jobs.exists()
    else:
        jobs = Job.objects.all()
        no_results = False

    return render(request, 'jobapp/job_list.html', {
        'jobs': jobs,
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



#is loged in as a recruiter only 



def add_candidates(request, job_id):
    # Ensure only recruiters can access this page
    if not request.user.is_authenticated or not request.user.is_recruiter:
        messages.error(request, 'Only recruiters can access this page.')
        return redirect('login')
    
    # Get the job and ensure the recruiter owns it
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        # Handle candidate addition form submission
        candidate_name = request.POST.get('candidate_name')
        candidate_email = request.POST.get('candidate_email')
        candidate_phone = request.POST.get('candidate_phone')
        candidate_resume = request.FILES.get('candidate_resume')
        
        # Create and save the candidate
        candidate = Candidate.objects.create(
            job=job,
            name=candidate_name,
            email=candidate_email,
            phone=candidate_phone,
            resume=candidate_resume,
            added_by=request.user
        )
        
        messages.success(request, f'Candidate {candidate_name} added successfully!')
        return redirect('add_candidates', job_id=job_id)
    
    # Get all candidates for this job to display
    candidates = Candidate.objects.filter(job=job)
    
    return render(request, 'jobapp/add_candidates.html', {
        'job': job,
        'candidates': candidates
    })



@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # prevent duplicate application
    
    if Application.objects.filter(applicant=request.user, job=job).exists():
        return render(request, 'jobapp/already_applied.html', {'job': job})
    
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job = job
            application.save()
            return redirect('job_list')  # or to 'my_applications'
    
    else:
        form = ApplicationForm()
   
    return render(request, 'jobapp/apply_job.html', {'form': form, 'job': job})   




#job seeker Dashboard
@login_required
def jobseeker_dashboard(request):
    applications = Application.objects.filter(applicant=request.user)
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'jobapp/jobseeker_dashboard.html', {'applications': applications, 'profile': profile})        

#recruiter dashboard
@login_required
@user_passes_test(lambda u: u.is_recruiter)
def recruiter_dashboard(request):
    applications = Application.objects.filter(job__posted_by=request.user)  
    # jobs = Job.objects.filter(posted_by=request.user)
    # return render(request, 'jobapp/recruiter_dashboard.html', {'jobs': jobs})
    return render(request, 'jobapp/recruiter_dashboard.html', {
        'applications': applications
    })


# schedule interview view for recruiter only
@login_required
@user_passes_test(lambda u: u.is_recruiter)
def schedule_interview(request, job_id, applicant_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    candidate = get_object_or_404(User, id=applicant_id)

    if request.method == 'POST':
        link = request.POST.get('link')
        date = request.POST.get('date')
        time = request.POST.get('time')
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Create Interview
        Interview.objects.create(
            job=job,
            candidate=candidate,
            # link=link,
            scheduled_at=dt,
        )
        
        
        
        return redirect('recruiter_dashboard')

    return render(request, 'jobapp/schedule_interview.html', {'job': job, 'candidate': candidate})




# interview_ready function view
def interview_ready(request, interview_uuid):
    """
    Display the interview ready page before starting the actual AI interview
    """
    try:
        # Get the interview record
        interview = get_object_or_404(Interview, uuid=interview_uuid)
        
        # Check if the user is authorized (optional security check)
        if hasattr(request.user, 'profile'):
            if interview.candidate != request.user:
                return HttpResponse('Unauthorized access to this interview.', status=403)
        
        return render(request, 'jobapp/interview_ready.html', {
            'interview': interview,
        })
        
    except Exception as e:
        print(f"Interview Ready Error: {e}")
        return HttpResponse(f'Interview ready page could not be loaded. Error: {str(e)}', status=500)





def start_interview_by_uuid(request, interview_uuid):
    try:
        # Get the interview record
        interview = get_object_or_404(Interview, uuid=interview_uuid)
        
        candidate_name = interview.candidate.get_full_name() or "the candidate"
        job_title = interview.job.title or "Software Developer"
        
        # Handle company name safely
        try:
            company_name = interview.job.company
        except AttributeError:
            company_name = "Our Company"
        
        # Get resume file from candidate's profile with error handling
        profile = getattr(interview.candidate, 'profile', None)
        resume_file = profile.resume if profile and profile.resume else None

        if not resume_file:
            return HttpResponse("Resume file not found. Please upload your resume in your profile.", status=400)

        try:
            resume_text = extract_resume_text(resume_file)
        except Exception as e:
            resume_text = "Resume could not be processed."
            logger.warning(f"Resume extraction error for interview {interview_uuid}: {e}")
        
        # Store interview context in session for consistency
        request.session['interview_context'] = {
            'candidate_name': candidate_name,
            'job_title': job_title,
            'company_name': company_name,
            'resume_text': resume_text,
            'job_description': interview.job.description,
            'job_location': interview.job.location,
            'question_count': 0
        }
        
        if request.method == "POST":
            # Handle both AJAX and regular form submissions
            try:
                if request.content_type == 'application/json':
                    data = json.loads(request.body)
                    user_text = data.get("text") or data.get("message")
                else:
                    user_text = request.POST.get("text", "")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in interview {interview_uuid}: {e}")
                user_text = request.POST.get("text", "")
            except Exception as e:
                logger.error(f"Unexpected error parsing request data in interview {interview_uuid}: {e}")
                user_text = request.POST.get("text", "")
            
            if not user_text.strip():
                return JsonResponse({
                    'error': 'Please provide a response.',
                    'response': 'I didn\'t receive your answer. Could you please respond?',
                    'audio': '',
                    'success': False
                })
            
            logger.info(f"User input for interview {interview_uuid}: {user_text}")
            
            # Get context from session
            context = request.session.get('interview_context', {})
            question_count = context.get('question_count', 0) + 1
            
            # Update question count
            context['question_count'] = question_count
            request.session['interview_context'] = context
            
            # Handle "I can't hear" responses specifically
            user_text_lower = user_text.lower().strip()
            if any(phrase in user_text_lower for phrase in ['cant hear', "can't hear", 'cannot hear', 'cant listen', "can't listen", 'no audio', 'no sound']):
                logger.info(f"User reported audio issues in interview {interview_uuid}, providing text-based response")
                
                if question_count == 1:
                    ai_response = f"I understand you're having audio issues. No problem! Let me ask you in text: Could you please tell me about yourself and why you're interested in this {job_title} position at {company_name}?"
                elif question_count <= 8:
                    ai_response = "I understand you can't hear the audio. That's okay! Here's my next question: Can you describe a challenging project you've worked on and how you overcame the obstacles?"
                else:
                    ai_response = "Thank you for letting me know about the audio issues. We can continue with text-based questions. What questions do you have about this role or our company?"
                
                # Force text-only response (no audio generation)
                response_data = {
                    'response': ai_response,
                    'audio': '',  # No audio
                    'success': True,
                    'question_count': question_count,
                    'is_final': question_count > 8,
                    'text_only': True  # Flag for frontend
                }
                
                return JsonResponse(response_data)
            
            # Create contextual prompt based on question number
            if question_count <= 8:
                prompt = f"""
You are Alex, a friendly HR interviewer. Keep your responses natural and conversational.

CONTEXT:
- Candidate: {context.get('candidate_name', 'the candidate')}
- Position: {context.get('job_title')} at {context.get('company_name')}
- Job Description: {context.get('job_description', '')}
- Resume Summary: {context.get('resume_text', '')[:500]}...

The candidate just said: "{user_text}"

INSTRUCTIONS:
- Give a brief, natural acknowledgment of their answer (1 sentence max)
- Ask ONE follow-up question related to their response OR move to the next interview topic
- Keep it conversational - use "That's interesting," "I see," etc.
- Maximum 2-3 sentences total
- Don't give lengthy explanations or multiple questions

Current question #{question_count} of 8.
"""
            else:
                prompt = f"""
You are Alex, a friendly HR interviewer wrapping up the interview.

The candidate just said: "{user_text}"

INSTRUCTIONS:
- Briefly acknowledge their final answer
- Thank them for their time
- Let them know next steps will be communicated soon
- Keep it warm but concise (2-3 sentences max)
- End the interview naturally

This was the final question.
"""
            
            try:
                ai_response = ask_ai_question(prompt, candidate_name, job_title, company_name)
            except Exception as e:
                logger.error(f"AI API Error for interview {interview_uuid}: {e}")
                ai_response = "Thank you for that response. Can you tell me more about your experience with similar challenges?"
            
            logger.info(f"AI Response for interview {interview_uuid}: {ai_response}")
            
            # Generate TTS for response with enhanced error handling and fallback
            audio_path = None
            audio_generation_error = None
            
            try:
                logger.info(f"Generating response TTS for interview {interview_uuid}: '{ai_response[:50]}...'")
                
                # Try primary TTS first
                audio_path = generate_tts(ai_response)
                
                if audio_path:
                    # Verify the file actually exists
                    full_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                    if os.path.exists(full_path):
                        file_size = os.path.getsize(full_path)
                        logger.info(f"Response TTS verified for interview {interview_uuid}: {full_path} ({file_size} bytes)")
                        
                        # Additional validation for audio files
                        if file_size < 100:  # Too small to be valid audio
                            logger.warning(f"Generated audio file too small for interview {interview_uuid}, trying fallback")
                            audio_path = None
                        
                    else:
                        logger.error(f"Response TTS file not found for interview {interview_uuid}: {full_path}")
                        audio_path = None
                else:
                    logger.warning(f"Response TTS generation returned None for interview {interview_uuid}")
                    
            except Exception as e:
                logger.error(f"Response TTS generation failed for interview {interview_uuid}: {e}")
                audio_generation_error = str(e)
                audio_path = None
            
            # If primary TTS failed, try gTTS specifically
            if not audio_path:
                try:
                    logger.info(f"Trying gTTS fallback for interview {interview_uuid}...")
                    audio_path = generate_gtts_fallback(ai_response)
                    if audio_path:
                        full_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                        if os.path.exists(full_path) and os.path.getsize(full_path) > 100:
                            logger.info(f"gTTS fallback successful for interview {interview_uuid}")
                        else:
                            logger.warning(f"gTTS fallback file invalid for interview {interview_uuid}")
                            audio_path = None
                except Exception as e:
                    logger.error(f"gTTS fallback also failed for interview {interview_uuid}: {e}")
                    audio_path = None
            
            # Return JSON response for AJAX requests
            response_data = {
                'response': ai_response,
                'audio': audio_path if audio_path else '',
                'success': True,
                'question_count': question_count,
                'is_final': question_count > 8,
                'audio_error': audio_generation_error if audio_generation_error else None
            }
            
            logger.info(f"Sending response for interview {interview_uuid}: {response_data}")
            
            return JsonResponse(response_data)
            
    # Handle CSRF errors specifically
    except PermissionDenied as e:
        if 'CSRF' in str(e) or 'csrf' in str(e).lower():
            logger.error(f"CSRF error for interview {interview_uuid}: {e}")
            return JsonResponse({
                'error': 'Session expired. Please refresh the page.',
                'response': 'Your session has expired. Please refresh the page to continue.',
                'success': False,
                'csrf_error': True,
                'refresh_required': True
            }, status=403)
        else:
            raise  # Re-raise if not CSRF related

        # GET: Show interview UI with first question
        first_prompt = f"""
You are Alex interviewing {candidate_name} for {job_title} at {company_name}.

Resume highlights: {resume_text[:300]}

RULES:
- Only output what you say - no quotes, labels, or descriptions
- Maximum 2 sentences per response
- Sound natural and conversational
- Show interest in their answers

START: Say hello, mention you can communicate via text if they have audio issues, then ask why they want this role.
"""        
        
        try:
            ai_question = ask_ai_question(first_prompt, candidate_name, job_title, company_name)
        except Exception as e:
            logger.error(f"AI API Error on initial question for interview {interview_uuid}: {e}")
            ai_question = f"Hi {candidate_name}! Thanks for joining me today. If you have any audio issues, we can communicate via text. Could you start by telling me a bit about yourself and what interests you about this {job_title} position?"
        
        logger.info(f"Initial AI Question for interview {interview_uuid}: {ai_question}")
        
        # Generate initial TTS with enhanced error handling
        audio_path = None
        try:
            logger.info(f"Generating initial TTS for interview {interview_uuid}: '{ai_question[:50]}...'")
            
            # Skip TTS health check for now
            # health_check = check_tts_system()
            # if not health_check.get('gtts_available', False):
            #     logger.error(f"gTTS not available for interview {interview_uuid}, cannot generate audio")
            
            # Try to generate initial audio
            audio_path = generate_tts(ai_question)
            
            if audio_path:
                # Verify the file actually exists
                full_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    logger.info(f"Initial TTS verified for interview {interview_uuid}: {full_path} ({file_size} bytes)")
                    
                    # Validate file size
                    if file_size < 100:
                        logger.warning(f"Initial TTS file too small for interview {interview_uuid}")
                        audio_path = None
                        
                else:
                    logger.error(f"Initial TTS file not found for interview {interview_uuid}: {full_path}")
                    audio_path = None
            else:
                logger.warning(f"Initial TTS generation returned None for interview {interview_uuid}")
                
        except Exception as e:
            logger.error(f"Initial TTS generation failed for interview {interview_uuid}: {e}")
            audio_path = None

        # If no audio generated, try gTTS specifically
        if not audio_path:
            try:
                logger.info(f"Trying gTTS for initial question in interview {interview_uuid}...")
                audio_path = generate_gtts_fallback(ai_question)
                if audio_path:
                    full_path = os.path.join(settings.BASE_DIR, audio_path.lstrip('/'))
                    if os.path.exists(full_path) and os.path.getsize(full_path) > 100:
                        logger.info(f"Initial gTTS successful for interview {interview_uuid}")
                    else:
                        logger.warning(f"Initial gTTS file invalid for interview {interview_uuid}")
                        audio_path = None
            except Exception as e:
                logger.error(f"Initial gTTS also failed for interview {interview_uuid}: {e}")
                audio_path = None

        # Template context with proper audio handling
        context_data = {
            'interview': interview,
            'ai_question': ai_question,
            'audio_url': audio_path if audio_path else '',
            'candidate_name': candidate_name,
            'job_title': job_title,
            'company_name': company_name,
            'has_audio': bool(audio_path),  # Helper flag for template
            'csrf_token': get_token(request),  # Ensure fresh CSRF token
        }
        
        logger.info(f"Template context for interview {interview_uuid} - audio_url: '{context_data['audio_url']}', has_audio: {context_data['has_audio']}")
        
        return render(request, 'jobapp/interview_ai.html', context_data)
        
    # Improved error handling with specific exception types
    except Http404:
        logger.error(f"Interview not found: {interview_uuid}")
        return HttpResponse('Interview not found.', status=404)
    
    except PermissionDenied:
        logger.error(f"Permission denied for interview: {interview_uuid}")
        return HttpResponse('You do not have permission to access this interview.', status=403)
    
    except ValidationError as e:
        logger.error(f"Validation error for interview {interview_uuid}: {e}")
        return HttpResponse(f'Invalid data: {str(e)}', status=400)
    
    except ConnectionError as e:
        logger.error(f"Connection error for interview {interview_uuid}: {e}")
        return HttpResponse('Unable to connect to required services. Please try again later.', status=503)
    
    except TimeoutError as e:
        logger.error(f"Timeout error for interview {interview_uuid}: {e}")
        return HttpResponse('Request timed out. Please try again.', status=504)
    
    except Exception as e:
        # Enhanced error logging with more context
        import traceback
        error_details = {
            'interview_uuid': interview_uuid,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc(),
            'request_method': request.method,
            'user': getattr(request.user, 'id', 'Anonymous') if hasattr(request, 'user') else 'Unknown',
            'session_key': request.session.session_key if hasattr(request, 'session') else 'Unknown'
        }
        
        logger.error(f"Interview Error Details: {error_details}")
        
        # For development, show detailed error
        if settings.DEBUG:
            return HttpResponse(
                f'Interview could not be started.<br>'
                f'Error Type: {error_details["error_type"]}<br>'
                f'Error: {error_details["error_message"]}<br>'
                f'UUID: {interview_uuid}<br>'
                f'<pre>{error_details["traceback"]}</pre>',
                status=500
            )
        else:
            # For production, show generic error
            return HttpResponse(
                'Interview could not be started. Our team has been notified and is working to resolve the issue.',
                status=500
            )


# Additional helper function for better error context
def log_interview_error(interview_uuid, error, context=None):
    """
    Centralized error logging for interview-related errors
    """
    import traceback
    
    error_info = {
        'timestamp': datetime.now().isoformat(),
        'interview_uuid': interview_uuid,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
    }
    
    if context:
        error_info['context'] = context
    
    logger.error(f"Interview System Error: {error_info}")
    
    # Optional: Send to external monitoring service
    # send_to_monitoring_service(error_info)
    
    return error_info
    
     
# def start_interview_by_uuid(request, interview_uuid):
#     try:
#         # Get the interview record
#         interview = get_object_or_404(Interview, uuid=interview_uuid)
        
#         candidate_name = interview.candidate.get_full_name() or "the candidate"
#         job_title = interview.job.title or "Software Developer"
        
#         # Handle company name safely
#         try:
#             company_name = interview.job.company
#         except AttributeError:
#             company_name = "Our Company"
        
#         # Get resume file from candidate's profile with error handling
#         profile = getattr(interview.candidate, 'profile', None)
#         resume_file = profile.resume if profile and profile.resume else None

#         if not resume_file:
#             return HttpResponse("Resume file not found. Please upload your resume in your profile.", status=400)

#         try:
#             resume_text = extract_resume_text(resume_file)
#         except Exception as e:
#             resume_text = "Resume could not be processed."
#             pass  # Resume extraction error
        
#         # Store interview context in session for consistency
#         request.session['interview_context'] = {
#             'candidate_name': candidate_name,
#             'job_title': job_title,
#             'company_name': company_name,
#             'resume_text': resume_text,
#             'job_description': interview.job.description,
#             'job_location': interview.job.location,
#             'question_count': 0
#         }
        
#         if request.method == "POST":
#             user_text = request.POST.get("text", "")
            
#             if not user_text.strip():
#                 return JsonResponse({
#                     'error': 'Please provide a response.',
#                     'response': 'I didn\'t receive your answer. Could you please respond?'
#                 })
            
#             # Get context from session
#             context = request.session.get('interview_context', {})
#             question_count = context.get('question_count', 0) + 1
            
#             # Update question count
#             context['question_count'] = question_count
#             request.session['interview_context'] = context
            
#             # Create contextual prompt based on question number
#             if question_count <= 8:
#                 prompt = f"""
# You are Alex, a friendly HR interviewer. Keep your responses natural and conversational.

# CONTEXT:
# - Candidate: {context.get('candidate_name', 'the candidate')}
# - Position: {context.get('job_title')} at {context.get('company_name')}
# - Job Description: {context.get('job_description', '')}
# - Resume Summary: {context.get('resume_text', '')[:500]}...

# The candidate just said: "{user_text}"

# INSTRUCTIONS:
# - Give a brief, natural acknowledgment of their answer (1 sentence max)
# - Ask ONE follow-up question related to their response OR move to the next interview topic
# - Keep it conversational - use "That's interesting," "I see," etc.
# - Maximum 2-3 sentences total
# - Don't give lengthy explanations or multiple questions

# Current question #{question_count} of 8.
# """
#             else:
#                 prompt = f"""
# You are Alex, a friendly HR interviewer wrapping up the interview.

# The candidate just said: "{user_text}"

# INSTRUCTIONS:
# - Briefly acknowledge their final answer
# - Thank them for their time
# - Let them know next steps will be communicated soon
# - Keep it warm but concise (2-3 sentences max)
# - End the interview naturally

# This was the final question.
# """
            
#             try:
#                 ai_response = ask_ai_question(prompt, candidate_name, job_title, company_name)
#             except Exception as e:
#                 pass  # AI API Error
#                 ai_response = "Thank you for that response. Can you tell me more about your experience with similar challenges?"
            
#             # Generate audio (keeping your existing TTS logic)
#             audio_data = None
#             if ai_response and ai_response.strip():
#                 try:
#                     with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
#                         temp_path = temp_file.name
                    
#                     tts = gTTS(text=ai_response.strip(), lang='en', slow=False)
#                     tts.save(temp_path)
                    
#                     if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
#                         with open(temp_path, 'rb') as audio_file:
#                             audio_content = audio_file.read()
#                             audio_base64 = base64.b64encode(audio_content).decode('utf-8')
#                             audio_data = f"data:audio/mpeg;base64,{audio_base64}"
                    
#                     try:
#                         os.unlink(temp_path)
#                     except:
#                         pass
                        
#                 except Exception as e:
#                     pass  # TTS Error

#             return JsonResponse({
#                 'response': ai_response,
#                 'audio': audio_data
#             })

#         # GET: Show interview UI with first question
#         first_prompt = f"""
        

# You are Alex interviewing {candidate_name} for {job_title} at {company_name}.

# Resume highlights: {resume_text[:300]}

# RULES:
# - Only output what you say - no quotes, labels, or descriptions
# - Maximum 2 sentences per response
# - Sound natural and conversational
# - Show interest in their answers

# START: Say hello, ask "can you hear me clearly?" then ask why they want this role.
# """        


        
#         try:
#             ai_question = ask_ai_question(first_prompt, candidate_name, job_title, company_name)
#         except Exception as e:
#             pass  # AI API Error on initial question
#             ai_question = f"Hi {candidate_name}! Thanks for joining me today. Could you start by telling me a bit about yourself and what interests you about this {job_title} position?"
        
#         # Generate initial audio
#         audio_data = None
#         if ai_question and ai_question.strip():
#             try:
#                 with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
#                     temp_path = temp_file.name
                
#                 tts = gTTS(text=ai_question.strip(), lang='en', slow=False)
#                 tts.save(temp_path)
                
#                 if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
#                     with open(temp_path, 'rb') as audio_file:
#                         audio_content = audio_file.read()
#                         audio_base64 = base64.b64encode(audio_content).decode('utf-8')
#                         audio_data = f"data:audio/mpeg;base64,{audio_base64}"
                
#                 try:
#                     os.unlink(temp_path)
#                 except:
#                     pass
                    
#             except Exception as e:
#                 pass  # Initial TTS Error

#         return render(request, 'jobapp/interview_ai.html', {
#             'interview': interview,
#             'ai_question': ai_question,
#             'audio_url': audio_data
#         })
        
#     except Exception as e:
#         pass  # Interview Error
#         return HttpResponse(f'Interview could not be started. Error: {str(e)}', status=500)





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

# Media file serving view for production
def serve_media(request, path):
    """Serve media files in production"""
    import mimetypes
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    if os.path.exists(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    else:
        raise Http404("Media file not found")

# CSRF token endpoint
def get_csrf_token(request):
    """Return fresh CSRF token for AJAX requests"""
    return JsonResponse({
        'csrf_token': get_token(request)
    })