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
    
     # 📄 Apply to job
    path('apply/<int:job_id>/',views.apply_to_job, name='apply_to_job'),
    
     # 🧑‍💼 Dashboards
    path('dashboard/seeker/', views.jobseeker_dashboard, name='jobseeker_dashboard'),
    path('dashboard/recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    # 📅 Interview scheduling
    path('schedule-interview/<int:job_id>/<int:applicant_id>/', views.schedule_interview, name='schedule_interview'),
    
     # 🗣️ Interview Start + AI Response
    path('interview/start/<uuid:interview_uuid>/', views.start_interview_by_uuid, name='start_interview'),
    path('interview/response/', views.ai_chat_response, name='ai_chat_response'),
    
    
    # contact 
    path('contact/', views.contact_view, name='contact'),
    # debugging
    path('debug/', views.debug_db, name='debug'),
]
