from django.contrib import admin
from . import models
from django.apps import apps
# Register your models here.

app_models = apps.get_app_config('dav').get_models()

admin.site.site_header = "Power DataMate"
admin.site.index_title = "Power DataMate"

class DataFileInline(admin.TabularInline):
    model = models.DataFile
    exclude = ["type"]

class DatasetAdmin(admin.ModelAdmin):
    inlines = [
        DataFileInline,
    ]

class AttributeInline(admin.TabularInline):
    model = models.Attribute

class DataFileAdmin(admin.ModelAdmin):
    inlines = [
        AttributeInline,
    ]


class AttributeReferenceInline(admin.TabularInline):
    model = models.AttributeReference
    fk_name = 'field'

class AttributeAdmin(admin.ModelAdmin):
    inlines = [
        AttributeReferenceInline,
    ]

admin.site.register(models.Dataset, DatasetAdmin)
admin.site.register(models.DataFile, DataFileAdmin)
admin.site.register(models.Attribute, AttributeAdmin)
# admin.site.register(models.Attribute, AttributeReferenceAdmin)

for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

