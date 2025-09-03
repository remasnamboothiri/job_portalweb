from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Interview, Job, Candidate
from django.db import connection
import logging

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: u.is_recruiter)
def debug_dashboard_view(request):
    """Debug view to check interview scheduling issues"""
    debug_info = {}
    
    try:
        # Check Interview model fields
        interview_fields = [field.name for field in Interview._meta.get_fields()]
        debug_info['interview_fields'] = interview_fields
        
        # Check if job_position field exists (it shouldn't)
        debug_info['has_job_position_field'] = 'job_position' in interview_fields
        debug_info['has_job_field'] = 'job' in interview_fields
        
        # Check database table structure
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jobapp_interview'
                ORDER BY ordinal_position
            """)
            db_columns = [row[0] for row in cursor.fetchall()]
            debug_info['db_columns'] = db_columns
            debug_info['db_has_job_position'] = 'job_position_id' in db_columns
            debug_info['db_has_job'] = 'job_id' in db_columns
        
        # Try to create a test interview object (without saving)
        try:
            test_job = Job.objects.filter(posted_by=request.user).first()
            if test_job:
                test_interview = Interview(
                    job=test_job,
                    candidate_name="Test Candidate",
                    candidate_email="test@example.com"
                )
                # Try to access the generate_unique_id method
                test_id = test_interview.generate_unique_id()
                debug_info['test_interview_creation'] = 'SUCCESS'
                debug_info['test_unique_id'] = test_id
            else:
                debug_info['test_interview_creation'] = 'NO_JOBS_FOUND'
        except Exception as e:
            debug_info['test_interview_creation'] = f'ERROR: {str(e)}'
        
        # Check recent interviews
        try:
            recent_interviews = Interview.objects.filter(
                job__posted_by=request.user
            ).order_by('-created_at')[:5]
            
            debug_info['recent_interviews'] = []
            for interview in recent_interviews:
                debug_info['recent_interviews'].append({
                    'id': interview.id,
                    'job_title': interview.job.title,
                    'candidate_name': interview.candidate_name,
                    'created_at': str(interview.created_at)
                })
        except Exception as e:
            debug_info['recent_interviews_error'] = str(e)
        
    except Exception as e:
        debug_info['error'] = str(e)
    
    return JsonResponse(debug_info, indent=2)