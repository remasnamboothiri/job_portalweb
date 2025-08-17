# SIMPLE FIX FOR INTERVIEW LINKS

## The Problem
Interview links are not showing in the jobseeker dashboard.

## Root Cause
The URL is `/dashboard/seeker/` not `/dashboard/jobseeker/`

## Quick Fix Steps

### 1. Login as testcandidate
- Username: `testcandidate`
- Password: `testpass123`

### 2. Go to correct URL
- Visit: `http://localhost:8000/dashboard/seeker/`
- NOT: `http://localhost:8000/dashboard/jobseeker/`

### 3. You should see:
- "Your Scheduled Interviews" section
- 2 interviews: "Frontend Developer" and "Test Developer"
- Copyable interview links
- "Start Interview" buttons

## If still not working, run this:

```python
python create_test_interview.py
```

This creates fresh test data with proper interviews.

## Test the complete flow:
1. Login as `testcandidate`
2. Go to `/dashboard/seeker/`
3. Copy interview link
4. Click "Start Interview"
5. Click "Start AI Interview"

The interviews ARE there - just need to use the correct URL!