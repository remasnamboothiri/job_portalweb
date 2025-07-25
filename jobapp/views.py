from django.shortcuts import render,redirect, get_object_or_404 , HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, LoginForm , ProfileForm, JobForm, ApplicationForm
from .models import CustomUser , Profile, Job, Application , Interview 
from django.contrib.auth.decorators import login_required , user_passes_test 
from django.http import HttpResponseForbidden , JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()
from datetime import datetime
from django.contrib.auth import get_backends
from django.urls import reverse
import os

#for Ai interview
from .utils.interview_ai_nvidia import ask_ai_question 
from jobapp.utils.resume_reader import extract_resume_text

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
        return render(request, 'jobapp/post_job.html')  # Better UX
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid:
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('job_list')   # redirect to job listings
    else:
        form = JobForm()
        
    return render(request, 'jobapp/post_job.html', {'form': form})   



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

 



def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobapp/job_detail.html', {'job': job})




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
        
        # ✅ Auto-generate interview URL with UUID
        
        # generated_link = request.build_absolute_uri(
        #     reverse('start_interview', args=[Interview.uuid])
        # )
        # Interview.link = generated_link
        # Interview.save()
        
        return redirect('recruiter_dashboard')

    return render(request, 'jobapp/schedule_interview.html', {'job': job, 'candidate': candidate})








def start_interview_by_uuid(request, interview_uuid):
    # Get the interview record
    interview = get_object_or_404(Interview, uuid = interview_uuid)
    
    
    candidate_name = interview.candidate.get_full_name() or "the candidate"
    interview.job.title or "Software Developer"
    # company_name = company_name or "Our Company"
    
    # Handle if company object or name is missing
    try:
        company_name = interview.job.company.name
    except AttributeError:
        company_name = "Our Company"
    
    
    # Get resume file from candidate's profile
    # resume_file = interview.candidate.profile.resume
    profile = getattr(interview.candidate, 'profile', None)
    resume_file = profile.resume if profile and profile.resume else None

    if not resume_file:
        return HttpResponse("Resume file not found in user profile.", status=400)


    resume_text = extract_resume_text(resume_file)
    # job_description = interview.job.description
    
    
    if request.method == "POST":
        user_text = request.POST.get("text")
        prompt = f"""
        candidate Resume:
        {resume_text}
    
        Job Role: {interview.job.title}
        job_description: {interview.job.description}
        Location : {interview.job.location}
        
        The candidate replied: "{user_text}"
        Please give the next question.
        """
        
        ai_response = ask_ai_question(prompt)
        
        
        # Safe audio generation
        if ai_response and ai_response.strip():
            audio_path = 'media/tts/ai_reply.mp3'
            tts = gTTS(ai_response.strip())
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            tts.save(audio_path)
        else:
            ai_response = "Sorry, I could not generate a response. Please try again."
            audio_path = 'media/tts/ai_reply.mp3'
            tts = gTTS(ai_response)
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            tts.save(audio_path)

        # Convert to voice
        audio_path = 'media/tts/ai_reply.mp3'
        tts = gTTS(ai_response)
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        tts.save(audio_path)

        return JsonResponse({
            'response': ai_response,
            'audio': f'/media/tts/ai_reply.mp3'
        })

    # GET: show interview UI
    first_prompt = f"""
    Candidate Resume: {resume_text}
    Job Title: {interview.job.title}
    Job Description: {interview.job.description}

    Ask the first interview question.
    """
    ai_question = ask_ai_question(first_prompt)
    tts = gTTS(ai_question)
    tts_path = 'media/tts/audio.mp3'
    os.makedirs(os.path.dirname(tts_path), exist_ok=True)
    tts.save(tts_path)

    return render(request, 'jobapp/interview_ai.html', {
        'interview': interview,
        'ai_question': ai_question
    })
        
        
    
    
   
    
#    # Call NVIDIA AI model
#     ai_question = ask_ai_question(prompt)
#     print("AI Question:", ai_question)
    
#      # ✅ Convert question to voice using gTTS
#     if ai_question:
#         tts = gTTS(ai_question)
#         tts_path = 'media/tts/audio.mp3'
#         os.makedirs(os.path.dirname(tts_path), exist_ok=True)
#         tts.save(tts_path)
        
#     else:
#         ai_question = "Sorry, something went wrong."

    
    
#     return render(request, 'jobapp/interview_ai.html', {
#         'interview': interview,
#         'ai_question': ai_question
#     })
    
@csrf_exempt
def ai_chat_response(request):
    if request.method == 'POST':
        user_text = request.POST.get('text')
        
        # Get question count from session, default to 1
        question_count = request.session.get('question_count', 1)

           # Set prompt based on question number
        if question_count <= 10:
            prompt = f"""
            The candidate said: "{user_text}"
            
            Now ask only the next interview question.
            Do NOT give any feedback, summary, or evaluation.
            Only ask one question at a time.
            """
        else:
            prompt = f"""
            The interview is complete.

            Based on the candidate’s full responses, provide overall feedback and selection status.
            Keep it short: max 2-3 sentences.
            """
        

        ai_reply = ask_ai_question(prompt)

        # Save voice file
        tts = gTTS(ai_reply)
        tts_path = f"media/tts/{uuid.uuid4()}.mp3"
        os.makedirs(os.path.dirname(tts_path), exist_ok=True)
        tts.save(tts_path)
        
         # Increment question count for next round
        request.session['question_count'] = question_count + 1

        return JsonResponse({
            'response': ai_reply,
            'audio': f'/{tts_path}'
            # 'audio': '/media/tts/audio.mp3'
        })    
    


# contact view

def contact_view(request):
    return render(request, 'jobapp/contact.html')

        
            
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
           
        
        
    
