# Simple test view to debug authentication issues
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def test_recruiter_auth(request):
    """Simple test view to check recruiter authentication"""
    user_info = {
        'user_id': request.user.id,
        'username': request.user.username,
        'is_authenticated': request.user.is_authenticated,
        'is_recruiter': getattr(request.user, 'is_recruiter', 'Field not found'),
        'user_type': type(request.user).__name__,
        'groups': list(request.user.groups.values_list('name', flat=True)) if hasattr(request.user, 'groups') else 'No groups'
    }
    
    return HttpResponse(f"""
    <h2>Authentication Test</h2>
    <pre>{user_info}</pre>
    <p><a href="/schedule-interview/1/2/">Test Schedule Interview Link</a></p>
    """)