"""
Debug script to test schedule interview functionality
Run this to check if the authentication and URL routing is working correctly
"""

# Test data
test_cases = [
    {
        'description': 'Test URL pattern',
        'url': '/schedule-interview/1/2/',
        'expected': 'Should work if user is authenticated and is_recruiter=True'
    },
    {
        'description': 'Test authentication',
        'url': '/test-auth/',
        'expected': 'Should show user authentication details'
    }
]

print("Schedule Interview Debug Information:")
print("=" * 50)

for i, test in enumerate(test_cases, 1):
    print(f"{i}. {test['description']}")
    print(f"   URL: {test['url']}")
    print(f"   Expected: {test['expected']}")
    print()

print("Common Issues and Solutions:")
print("-" * 30)
print("1. User not authenticated -> Redirects to login")
print("2. User.is_recruiter = False -> Shows error message")
print("3. Job doesn't exist -> 404 error")
print("4. Job not owned by user -> 404 error")
print("5. Applicant doesn't exist -> 404 error")
print()

print("To test:")
print("1. Login as a recruiter user")
print("2. Visit /test-auth/ to verify authentication")
print("3. Visit /schedule-interview/1/2/ (replace with valid IDs)")
print("4. Check server logs for detailed error messages")