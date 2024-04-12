import os
from distutils.command.upload import upload
from email.policy import default
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User
from .apps import AppConfig as app
import pandas as pd 
from django.utils.translation import gettext_lazy as _

class Dataset(models.Model):
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.title
    class Meta:
        verbose_name = _('Project')

class DataFile(models.Model):
    project = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=100, null = 'Uploaded')
    content = models.FileField(upload_to = "dav/datafile/")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.title+" - "+os.path.basename(self.content.name)

    def field_df(self) -> pd.DataFrame:
        list = Attribute.objects.filter(file=self).values()
        return pd.DataFrame.from_records(list)

class Attribute(models.Model):
    file = models.ForeignKey(DataFile, on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    attribute_name = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)
    # not_nulls = models.CharField(max_length=100)
    # count = models.PositiveIntegerField(null=True)
    # unique = models.PositiveIntegerField(null=True)
    # freq = models.PositiveIntegerField(null=True)
    # top = models.CharField(max_length=100, null=True)
    is_unique = models.BooleanField(default=False)
    pk_reference = models.ForeignKey('self', on_delete=models.CASCADE, related_name="field_pk_reference", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_pk = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.file.title+" - "+self.title

class AttributeReference(models.Model):
    field = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="field")
    reference = models.ForeignKey(Attribute, related_name="reference_field", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.field.file.title+" - "+self.field.title+" reference "

