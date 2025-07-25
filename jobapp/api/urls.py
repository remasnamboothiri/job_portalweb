# API URL routes

from django.urls import path
from .views import RegisterView , JobListCreate , jobdetail , ApplicationCreate , ApplicationList ,InterviewList , schedule_interview_api
from rest_framework_simplejwt.views import TokenRefreshView , TokenObtainPairView


urlpatterns = [
    # 🔐 Auth & JWT
    path('register/', RegisterView.as_view(), name="api_register"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 💼 Jobs
    path('jobs/', JobListCreate.as_view(), name='job_list_create'),
    path('jobs/<int:pk>/', jobdetail.as_view(), name='api_job_detail'),
    
     # 📄 Apply
    path('apply/', ApplicationCreate.as_view(), name='apply_job'),
    path('my-applications/', ApplicationList.as_view(), name='my-applications'),
    
    # 📅 Interview
    path('interviews/', InterviewList.as_view(), name='interview_list'),
    path('schedule-interview/<int:job_id>/<int:applicant_id>/', schedule_interview_api, name='schedule_interview_api'),
    
]
