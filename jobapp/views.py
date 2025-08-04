from django.shortcuts import render,redirect, get_object_or_404 , HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, LoginForm , ProfileForm, JobForm, ApplicationForm
from .models import CustomUser , Profile, Job, Application , Interview, Candidate
from django.contrib.auth.decorators import login_required , user_passes_test 
from django.http import HttpResponseForbidden , JsonResponse
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
            print("❌ Form errors:", form.errors)  # Debugging
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


  
@login_required
def post_job(request):
    if not request.user.is_recruiter:
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('login')
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)  # Add request.FILES
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_list')
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
from django.contrib import messages


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









# interview starting view      
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
            print(f"Resume extraction error: {e}")
        
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
            user_text = request.POST.get("text", "")
            
            if not user_text.strip():
                return JsonResponse({
                    'error': 'Please provide a response.',
                    'response': 'I didn\'t receive your answer. Could you please respond?'
                })
            
            # Get context from session
            context = request.session.get('interview_context', {})
            question_count = context.get('question_count', 0) + 1
            
            # Update question count
            context['question_count'] = question_count
            request.session['interview_context'] = context
            
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
                print(f"AI API Error: {e}")
                ai_response = "Thank you for that response. Can you tell me more about your experience with similar challenges?"
            
            # Generate audio (keeping your existing TTS logic)
            audio_data = None
            if ai_response and ai_response.strip():
                try:
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    tts = gTTS(text=ai_response.strip(), lang='en', slow=False)
                    tts.save(temp_path)
                    
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                        with open(temp_path, 'rb') as audio_file:
                            audio_content = audio_file.read()
                            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                            audio_data = f"data:audio/mpeg;base64,{audio_base64}"
                    
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
                except Exception as e:
                    print(f"TTS Error: {e}")

            return JsonResponse({
                'response': ai_response,
                'audio': audio_data
            })

        # GET: Show interview UI with first question
        first_prompt = f"""
        

You are Alex interviewing {candidate_name} for {job_title} at {company_name}.

Resume highlights: {resume_text[:300]}

RULES:
- Only output what you say - no quotes, labels, or descriptions
- Maximum 2 sentences per response
- Sound natural and conversational
- Show interest in their answers

START: Say hello, ask "can you hear me clearly?" then ask why they want this role.
"""        


        
        try:
            ai_question = ask_ai_question(first_prompt, candidate_name, job_title, company_name)
        except Exception as e:
            print(f"AI API Error on initial question: {e}")
            ai_question = f"Hi {candidate_name}! Thanks for joining me today. Could you start by telling me a bit about yourself and what interests you about this {job_title} position?"
        
        # Generate initial audio
        audio_data = None
        if ai_question and ai_question.strip():
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                tts = gTTS(text=ai_question.strip(), lang='en', slow=False)
                tts.save(temp_path)
                
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    with open(temp_path, 'rb') as audio_file:
                        audio_content = audio_file.read()
                        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                        audio_data = f"data:audio/mpeg;base64,{audio_base64}"
                
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            except Exception as e:
                print(f"Initial TTS Error: {e}")

        return render(request, 'jobapp/interview_ai.html', {
            'interview': interview,
            'ai_question': ai_question,
            'audio_url': audio_data
        })
        
    except Exception as e:
        print(f"Interview Error: {e}")
        return HttpResponse(f'Interview could not be started. Error: {str(e)}', status=500)





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
           
        
        
    
