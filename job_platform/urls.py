"""
URL configuration for job_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from jobapp.views import serve_media, get_csrf_token, test_tts, generate_audio
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('jobapp.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include('jobapp.api.urls')),
    path('media/<path:path>', serve_media, name='serve_media'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('test-tts/', test_tts, name='test_tts'),
    path('generate-audio/', generate_audio, name='generate_audio'),
    path('favicon.ico', serve, {'document_root': settings.STATIC_ROOT, 'path': 'favicon.ico'}),
    path('ftco-32x32.png', serve, {'document_root': settings.STATIC_ROOT, 'path': 'favicon.ico'}),
]

# Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Ensure media files are served in production too
if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   
    
    
    
# Add this for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    
    
