from django.apps import AppConfig

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dav'
    DATE_INPUT_FORMATS = ('%d-%m-%Y','%Y-%m-%d')
