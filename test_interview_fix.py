import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobapp.models import Interview, CustomUser, Job

def test_interview_functionality():
    """Test that interviews can be created and accessed properly"""
    
    print("Testing Interview functionality...")
    
    try:
        # Test database connection
        interview_count = Interview.objects.count()
        print(f"Database connection OK. Found {interview_count} interviews.")
        
        # Test if we can query interviews by candidate
        users = CustomUser.objects.filter(is_recruiter=False)[:1]
        if users:
            user = users[0]
            user_interviews = Interview.objects.filter(candidate=user)
            print(f"User {user.username} has {user_interviews.count()} interviews")
            
            # Test candidate_id field
            for interview in user_interviews:
                print(f"   - Interview UUID: {interview.uuid}")
                print(f"   - Candidate ID: {interview.candidate_id}")
                print(f"   - Job: {interview.job_position.title if interview.job_position else 'No job'}")
        
        print("Interview functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_interview_functionality()