from django.contrib import admin
from .models import CustomUser , Profile, Job, Application , Interview
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model


User = get_user_model()

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model=CustomUser
    list_display = ['username', 'email', 'is_recruiter', 'is_staff', 'is_active']
    list_filter = ['is_recruiter', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_recruiter',)}),
    )
    
    
admin.site.register(CustomUser, CustomUserAdmin)   
admin.site.register(Profile)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Interview) 





admin.site.site_header = "Online Job Platform Admin"
admin.site.site_title = "Job Admin"
admin.site.index_title = "Welcome to the Job Admin Dashboard"
