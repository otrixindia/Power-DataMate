from cProfile import label
from email.policy import default
from multiprocessing.sharedctypes import Value
from pydoc import render_doc
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from . import models
from django.apps import apps

class DatasetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False 
            if "date"  in name.lower():
                _class = "date-picker-single form-control"
            else:
                _class = "form-control"
            self.fields[name].widget.attrs.update({
                'class': _class,
                'placeholder':name.title()
            })
    class Meta:
        model = models.Dataset
        fields = ("__all__")

class DataFileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DataFileForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False 
            if "date"  in name.lower():
                _class = "date-picker-single form-control"
            else:
                _class = "form-control"
            self.fields[name].widget.attrs.update({
                'class': _class,
                'placeholder':name.title()
            })
    class Meta:
        model = models.DataFile
        fields = ("__all__")

class AttributeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttributeForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False 
            if "date"  in name.lower():
                _class = "date-picker-single form-control"
            else:
                _class = "form-control"
            self.fields[name].widget.attrs.update({
                'class': _class,
                'placeholder':name.title()
            })
    class Meta:
        model = models.Attribute
        fields = ("__all__")

class ConnectionForm(forms.Form):
    CHOICES = (('Option 1', 'Option 1'),('Option 2', 'Option 2'),)
    type = forms.ChoiceField(choices=(('MySql', 'MySql'), ('Postgres', 'Postgres')), initial="Postgres")
    host = forms.CharField(max_length=100, initial="localhost")
    database = forms.CharField(max_length=100, initial="djangodb")
    user = forms.CharField(max_length=100, initial="user")
    passwd = forms.CharField(max_length=100, initial="password", widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        super(ConnectionForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False 
            if "date"  in name.lower():
                _class = "date-picker-single form-control"
            else:
                _class = "form-control"
            self.fields[name].widget.attrs.update({
                'class': _class,
                'placeholder':name.title()
            })

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].required = False 
            if "date"  in name.lower():
                _class = "date-picker-single form-control"
            else:
                _class = "form-control"
            self.fields[name].widget.attrs.update({
                'class': _class,    
                'placeholder':name.replace("_", " ").title()
            })
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder':"Username"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class' : 'form-control', "placeholder":"Password"}))
    class Meta:
        model = User
        fields = ("username", "password")
