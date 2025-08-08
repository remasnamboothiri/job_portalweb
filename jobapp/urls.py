# jobapp/urls.py

from django.urls import path
from . import views 

urlpatterns = [
      # 🏠 Home
    path('', views.home_view, name='home'),
    # 🔐 Auth views
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # 👤 Profile
    path('profile/',views.update_profile, name='Profile_update'),
    # 💼 Job pages
    path('post-job/',views.post_job, name='post_job'),
    path('jobs/',views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/add-candidates/', views.add_candidates, name='add_candidates'),
    
     # 📄 Apply to job
    path('apply/<int:job_id>/',views.apply_to_job, name='apply_to_job'),
    
     # 🧑‍💼 Dashboards
    path('dashboard/seeker/', views.jobseeker_dashboard, name='jobseeker_dashboard'),
    path('dashboard/recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    # 📅 Interview scheduling
    path('schedule-interview/<int:job_id>/<int:applicant_id>/', views.schedule_interview, name='schedule_interview'),
    
    
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
    
    path('chat/', views.chat_view, name='chat'),
]
