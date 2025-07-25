from django.apps import AppConfig


class JobappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobapp'
    
    def ready(self):
        import jobapp.signals  #This runs the signals at startup
        
        
        
def ready(self):
        import jobapp.signals  # ✅ Import the signals here        
    
    
    
