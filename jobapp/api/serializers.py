# DRF serializers

from rest_framework import serializers
from jobapp.models import CustomUser , Job , Application , Interview
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password' , 'is_recruiter']
        
        
        
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_recruiter=validated_data.get('is_recruiter', False)
        )
        return user   
    
    
    
class JobSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Job
        fields = '__all__'
        
        
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['status', 'applied_at']
        
        
        
class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = '__all__'        
                
