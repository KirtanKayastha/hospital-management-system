from django.apps import AppConfig

class PatientsConfig(AppConfig):  # Or whatever class name you have
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient_roshan'  # ✅ Must match the folder name, NOT 'patients'