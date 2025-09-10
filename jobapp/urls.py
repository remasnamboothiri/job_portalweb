# jobapp/urls.py

from django.urls import path
from . import views
from .debug_dashboard import debug_dashboard_view 


urlpatterns = [
      # 🏠 Home
    path('', views.home_view, name='home'),
    # 🔐 Auth views - register redirects to login
    path('register/', views.register_view, name='register'),  # This now redirects to login
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # 👤 Profile
    path('profile/',views.update_profile, name='Profile_update'),
    # 💼 Job pages
    path('post-job/',views.post_job, name='post_job'),
    path('jobs/',views.job_list, name='job_list'),
    path('job/<int:job_id>/update-status/', views.update_job_status, name='update_job_status'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/add-candidates/', views.add_candidates, name='add_candidates'),
    
     # 📄 Apply to job
    path('apply/<int:job_id>/',views.apply_to_job, name='apply_to_job'),
    
     # 🧑‍💼 Dashboards
    path('dashboard/seeker/', views.jobseeker_dashboard, name='jobseeker_dashboard'),
    path('dashboard/recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    # 📅 Interview scheduling - existing (for registered candidates)
    path('schedule-interview/<int:job_id>/<int:applicant_id>/', views.schedule_interview, name='schedule_interview'),
    # Interview scheduling - simplified for added candidates
    path('schedule-interview/', views.schedule_interview_simple, name='schedule_interview_simple'),
    # Schedule interview with specific candidate
    path('schedule-interview/candidate/<int:candidate_id>/', views.schedule_interview_with_candidate, name='schedule_interview_with_candidate'),
    
    
    
    # interview ready page 
    path('interview/ready/<uuid:interview_uuid>/', views.interview_ready, name='interview_ready'),
     # 🗣️ Interview Start + AI Response
    path('interview/start/<uuid:interview_uuid>/', views.start_interview_by_uuid, name='start_interview'),
    # path('debug/media/', views.test_media_debug, name='test_debug_media'),
   
    
    
    
    # About
    path('about/', views.about_view, name='about'),
    
    
    # contact 
    path('contact/', views.contact_view, name='contact'),
    
    # testimonials 
    path('testimonials/', views.testimonials_view, name='testimonials'),
    
    # FAQ 
    path('faq/', views.faq_view, name='faq'),
    
    # Blog
    path('blog/', views.blog_view, name='blog'),
    # blog_single
    path('blog/single/', views.blog_single_view, name='blog_single'),
    
    # debugging
    path('debug/', views.debug_db, name='debug'),
    path('test-auth/', views.test_recruiter_auth, name='test_auth'),
    
    path('chat/', views.chat_view, name='chat'),
    path('debug-dashboard/', debug_dashboard_view, name='debug_dashboard'),
    
    # Recording and TTS endpoints
    path('save-interview-recording/', views.save_interview_recording, name='save_interview_recording'),
    path('test-tts/', views.test_tts, name='test_tts'),
    path('generate-audio/', views.generate_audio, name='generate_audio'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    
    # Add candidate from dashboard
    path('add-candidate-dashboard/', views.add_candidate_dashboard, name='add_candidate_dashboard'),
    
    # API endpoint for candidate email
    path('api/candidate/<int:candidate_id>/email/', views.get_candidate_email, name='get_candidate_email'),
    
    # Test interview results
    path('test-interview-results/', views.test_interview_results, name='test_interview_results'),
    
    
    # path('add_candidate/', views.add_candidate, name='add_candidate'),
    
    
    
    path('debug-db/', views.debug_database_structure, name='debug_db'),
    
    
    #visible of jobs 
    path('debug/job-posting/', views.debug_job_posting, name='debug_job_posting'),
    path('debug/test-job-save/', views.test_job_save, name='test_job_save'),
    path('debug/fix-database/', views.fix_database_issues, name='fix_database_issues'),
    
    
    
    #edit job , Job Management URLs
    path('jobs/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('jobs/<int:job_id>/duplicate/', views.duplicate_job, name='duplicate_job'),
    
]
