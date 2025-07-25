# All API views (using DRF)

from rest_framework import generics , permissions
from jobapp.models import Job , Application , Interview , CustomUser
from .serializers import RegisterSerializer , JobSerializer , ApplicationSerializer , InterviewSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from rest_framework import status
from rest_framework.response import Response

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    
    
    
class JobListCreate(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
class jobdetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]
    
    
class ApplicationCreate(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
class ApplicationList(generics.ListAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user)
    
    
    
    
class InterviewList(generics.ListAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        return Interview.objects.filter(candidate=self.request.user)    
    
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_interview_api(request, job_id, applicant_id):
    try:
        job = Job.objects.get(id=job_id)
        candidate = CustomUser.objects.get(id=applicant_id)
        link = request.data.get('link')
        date = request.data.get('date')
        time = request.data.get('time')
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        Interview.objects.create(job=job, candidate=candidate, link=link, scheduled_at=dt)
        return Response({"message": "Interview scheduled successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
                        
 