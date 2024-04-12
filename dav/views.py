from pyflowchart import *
import uuid
# import schemdraw as sd
# from schemdraw.flow import *
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import urllib
import base64
import io
from django.db.models import Q
from django.db.models.functions import TruncMonth
from email import contentmanager
from django.db.models import Avg, Max, Min, Count
from pyexpat import model
from django.core import serializers
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from . import forms
from . import models
from django.contrib.auth import login, logout, authenticate
from django.forms import modelformset_factory
from .apps import AppConfig as app
from django.http import HttpResponse
from myproject import utils

def index(request):
    if request.user.is_authenticated:
        pass
    else:
        return redirect("/"+app.name+'/login')

    summary = {}
    summary['datasets'] = models.Dataset.objects.count()
    summary['datafiles'] = models.DataFile.objects.count()
    summary['attributes'] = models.Attribute.objects.count()
    
    list = models.Dataset.objects.all()
    table = list_to_table(list)
    context = {
        "list":list, 
        "table":table, 
        "summary":summary,

    }
    return render(request,app.name+'/index.html', context=context)

def login_request(request):
    loginForm = forms.LoginForm(data=request.POST or None)
    if request.method == "POST":
        if loginForm.is_valid():
            print("Post Method without Username")
            new_user = loginForm.get_user()
            login(request, new_user)
            return redirect('/'+app.name,)
        else:
            print(loginForm.errors)
    # elif username != None:
    #     print("Usenarm ", username)
    #     new_user = authenticate(username=username, password=password)
    #     login(request, new_user)
    context = {
        "form":loginForm
    }
    return render(request,app.name+'/login.html', context=context)

def logout_request(request):
    logout(request)
    return redirect("/"+app.name+'/login')



def datasets(request, id=None):
    title = "Datasets"
    dataset = models.Dataset.objects.filter(id=id).first()
    datasetForm = forms.DatasetForm(request.POST or None)
    list = models.Dataset.objects.all().order_by("-id")
    if request.method == "POST":
        print("metehod is post")
        if datasetForm.is_valid():
            print("Form is valid")
        else:
            print("datasetForm.errors", datasetForm.errors)
    if request.method == "POST":
        print("Form is valid")
        if datasetForm.is_valid():
            if id == None:
                pass
            elif int(id) > 0 :
                instance = models.Dataset.objects.get(id = id)
                datasetForm = forms.DatasetForm(request.POST or None, instance=instance)
            try:
                datasetForm.save()
                utils.show_message(request, title+' saved successfully.')
                return redirect("/dav/datasets")
            except Exception as e:
                utils.show_message(request, str(e), 'error')
        else:
            pass
    elif id == None:
        datasetForm = None
    elif id == 0:
        if datasetForm == None:
            datasetForm = forms.DatasetForm()
    else:
        datasetForm = forms.DatasetForm(instance = dataset)
    context = {
        "list":list, 
        "title":title, 
        "dataset":dataset,
        "form":datasetForm, 
    }
    return render(request,app.name+'/datasets.html', context=context)

def list_to_table(list):
    df = pd.DataFrame.from_records(list.values())
    table = df.to_html(index=False, classes='table table-stripped')
    return table


def add_or_update_project(request, id=None):
    form = forms.DatasetForm(request.POST or None)
    if form.is_valid():
        if id != None:
            instance = models.Dataset.objects.get(id = id)
            form = forms.DatasetForm(request.POST or None, instance=instance)
        form.save()
        return form
    else:
        return form;

def projects(request, id=None):
    project = models.Dataset.objects.filter(id=id).first()
    files = models.DataFile.objects.filter(project=project)
    for file in files:
        validate_excel_file(file.id)
    projectForm = forms.DatasetForm(request.POST or None)
    list = models.Dataset.objects.all()
    if request.method == "POST":
        projectForm = add_or_update_project(request, id)
    elif id == None or id == 0:
        projectForm = forms.DatasetForm()
    else:
        projectForm = forms.DatasetForm(instance = project)
    context = {
        "list":list, 
        "project":project,
        "project_form":projectForm, 
        "files":files
    }
    return render(request,app.name+'/projects.html', context=context)

def df_join_files(left_file, right_file, field):
    if left_file.type != 'Denormalized' and right_file.type != 'Denormalized':
        left_df = pd.read_csv(left_file.content.path, encoding='latin-1')
        right_df = pd.read_csv(right_file.content.path, encoding='latin-1')
        print(field.title)
        print(left_df.head())
        print(right_df.head())
        df = left_df.merge(right_df, on=field.title.lower(), how='left')
        file = models.DataFile.objects.filter(project=left_file.project and type == 'Denormalized').first()
        if file == None:
            csv_file = df.to_csv('media/dav/datafile/'+left_file.project.title+'-Denormalized.csv', index=False)
            print(csv_file)
            datafile = models.DataFile.objects.filter(type = 'Denormalized',project=left_file.project).first()
            if datafile == None:
                models.DataFile.objects.create(content='dav/datafile/'+left_file.project.title+'-Denormalized.csv', 
                title  = left_file.project.title+'-Denormalized.csv',
                type = 'Denormalized',
                project=left_file.project)
            else:
                datafile.content = 'dav/datafile/'+left_file.project.title+'-Denormalized.csv'
                datafile.title  = left_file.project.title+'-Denormalized.csv'
                datafile.save()
        print(file)
        return df.head();
    else:
        return None

def project_detail(request, id):
    project = models.Dataset.objects.filter(id=id).first()
    files = models.DataFile.objects.filter(project=project)
    list = models.Attribute.objects.filter(file__in=files).values('file').annotate(total=Count('file')).values('file', 'file__title', 'file__type', 'file__content', 'total')
    erd_list = []
    parent_fields = None
    child_fields = None
    is_ref = False
    fk_field = None
    for file in files:
        if file.type == 'Denormalized':
            continue
        is_ref = False
        validate_excel_file(file.id) 
        fields = models.Attribute.objects.filter(file=file)
        for field in fields:
            erd_list.append(field)
            if field.pk_reference != None:
                is_ref = True
            if field.pk_reference:
                fk_field = field

        if parent_fields == None and is_ref == False:
            parent_fields = fields
        if child_fields == None and is_ref == True:
            child_fields = fields
    joined_table = None
    try:
        if parent_fields != None and child_fields != None and fk_field != None and parent_fields[0].file.type != 'Denormalized' and child_fields[0].file.type != 'Denormalized':
            joined_list = df_join_files(parent_fields[0].file, child_fields[0].file, fk_field)
            if joined_list.empty == False:
                joined_table = joined_list.to_html(index=False, classes='table table-stripped')
    except:
        pass
    # print(joined_table)
    context = {
        "files":files,
        "list":list,
        "erd_list":erd_list,
        "parent_fields":parent_fields,
        "child_fields":child_fields,
        "joined_table":joined_table, 
        "project":project,
    }
    return render(request,app.name+'/project_detail.html', context=context)

import mysql.connector as mysql_con
import pandas as pd
import sqlite3
from myproject import settings
import os

def get_conn(form, type):
    print(type)
    if type == "MySql" and 1==2:
        host = form.cleaned_data['localhost']
        database  = form.cleaned_data['petdb']
        user = form.cleaned_data['user']
        passwd = form.cleaned_data['password']
        mydb = mysql_con.connect(host="localhost", database = 'petdb',user="root", passwd="password",use_pure=True)
        return mydb;
    elif type == "Postgres" and 1==2:
        pass
    else:
        db_path = os.path.abspath(settings.DATABASES['default']['NAME'])
        print(db_path)
        mydb = sqlite3.connect(db_path)
        return mydb

def get_all_tables(mydb, type):
    cursor=mydb.cursor()
    query = "SHOW TABLES;"
    if type == "Sqllite":
        query = "tables"
    query = "SELECT name FROM sqlite_master  WHERE type='table';"
    cursor.execute(query)
    print(cursor)
    list = []
    i = 1
    for table in cursor:
        list.append({"id":i, "table_name":table[0]})
        i = i+1
    print("list", list)
    return list

def select_table(table_name, mydb, project):
    if table_name != None:
        df = pd.read_sql("select * from "+table_name,mydb)
        file_path = 'dav/datafile/'+table_name+'.csv'
        csv_file = df.to_csv("media/"+file_path, index=False)
        datafile = models.DataFile.objects.filter(title=table_name, type = 'Database',project=project).first()
        if datafile == None:
            models.DataFile.objects.create(content=file_path, 
            title  = table_name,
            type = 'Database',
            project=project)
        else:
            datafile.content = file_path
            datafile.title  = table_name
            datafile.save()

def connect_db(request, id, table_name=None):
    project = models.Dataset.objects.filter(id=id).first()
    form = forms.ConnectionForm(request.POST or None)
    mydb = None
    type = "Sqllite"
    # if request.method == "POST" and form.is_valid():
        # type = form.cleaned_data['type']
    print("posst")
    mydb = get_conn(form, type)
    print("Connection", mydb)
    tables = get_all_tables(mydb, type)
    print(tables)
    select_table(table_name, mydb, project)
    if table_name == None and request.method == "GET":
        tables = None
    if table_name != None:
        df = pd.read_sql("select * from "+table_name,mydb)
        file_path = 'dav/datafile/'+table_name+'.csv'
        csv_file = df.to_csv("media/"+file_path, index=False)
        datafile = models.DataFile.objects.filter(title=table_name, type = 'Database',project=project).first()
        if datafile == None:
            models.DataFile.objects.create(content=file_path, 
            title  = table_name,
            type = 'Database',
            project=project)
        else:
            datafile.content = file_path
            datafile.title  = table_name
            datafile.save()
    if form == None:
        form = forms.ConnectionForm(initial={"host":"localhost", "database" : 'petdb',"user":"root", "passwd":"password"})
    selected = models.DataFile.objects.filter(project=id, type="Database")
    context = {
        "project":project,
        "tables":tables, 
        "selected":selected,
        "form":form
    }
    # mydb.close()
    return render(request,app.name+'/connect_db.html', context=context)


def generate_erd(request, id):
    project = models.Dataset.objects.filter(id=id).first()
    files = models.DataFile.objects.filter(project=project)
    erd_list = []
    parent_fields = None
    child_fields = None
    is_ref = False
    fk_field = None
    for file in files:
        is_ref = False
        validate_excel_file(file.id) 
        fields = models.Attribute.objects.filter(file=file)
        for field in fields:
            erd_list.append(field)
            if field.pk_reference != None:
                is_ref = True
            if field.pk_reference:
                fk_field = field

        if parent_fields == None and is_ref == False:
            parent_fields = fields
        if child_fields == None and is_ref == True:
            child_fields = fields
    joined_table = None
    try:
        if parent_fields != None and child_fields != None and fk_field != None:
            joined_list = df_join_files(parent_fields[0].file, child_fields[0].file, fk_field)
            if joined_list.empty == False:
                joined_table = joined_list.to_html(index=False, classes='table table-stripped')
    except:
        pass
    # print(joined_table)
    context = {
        "files":files,
        "erd_list":erd_list,
        "parent_fields":parent_fields,
        "child_fields":child_fields,
        "joined_table":joined_table
    }
    return render(request,app.name+'/generate_erd.html', context=context)


def add_or_update_file(request, id=None):
    form = forms.DataFileForm(request.POST or None)
    if form.is_valid():
        print("FOrm is valid    ")
        if id != None and id != "0":
            instance = models.DataFile.objects.get(id = id)
            form = forms.DataFileForm(request.POST or None, instance=instance)
        file = form.save(commit=True)
        print("Befor file validat ", file.id)
        # validate_excel_file(file.id)
        return form
    else:
        print("form.errors", form.errors)
        return form;

def files(request, id=None):
    file = models.DataFile.objects.filter(id=id).first()
    fields = models.Attribute.objects.filter(file=file)
    fileForm = forms.DataFileForm(request.POST or None)
    data = None
    print("ID ", id)
    if request.method == "POST":
        fileForm = add_or_update_file(request, id)
    elif id == None or id == 0:
        fileForm = forms.DataFileForm()
    else:
        fileForm = forms.DataFileForm(instance = file)
        # data = pd.read_csv(file.file.path).to_html().replace("dataframe", "table table-striped", encoding='latin-1')

    context = {
        "file":file,
        "file_form":fileForm, 
        "fields":fields, 
        "data":data
    }
    return render(request,app.name+'/datafiles.html', context=context)


def datafiles(request, project_id, id=None):
    title = "DataFiles"
    project = models.Dataset.objects.get(id=project_id)
    datafile = models.DataFile.objects.filter(id=id).first()
    datafileForm = forms.DataFileForm(request.POST or None, request.FILES)
    list = models.Dataset.objects.all().order_by("-id")
    if request.method == "POST":
        print("Form is valid")
        if datafileForm.is_valid():
            if id == None:
                pass
            elif int(id) > 0 :
                instance = models.Dataset.objects.get(id = id)
                datafileForm = forms.DataFileForm(request.POST or None, instance=instance)
            try:
                datafileForm.save()
                utils.show_message(request, title+' saved successfully.')
                return redirect("/dav/datafiles")
            except Exception as e:
                utils.show_message(request, str(e), 'error')
        else:
            pass
    elif id == None:
        datafileForm = None
    elif id == 0:
        if datafileForm == None:
            datafileForm = forms.DataFileForm(initial={"project":project})
    else:
        datafileForm = forms.DataFileForm(instance = datafile)
    context = {
        "list":list, 
        "title":title, 
        "object":datafile,
        "project":project,
        "form":datafileForm, 
    }
    return render(request,app.name+'/datafiles.html', context=context)


# def get_entity_chart():
#     with sd.Drawing() as d:
#         d+= Start().label("Start")
#         d+= Arrow().down(d.unit/2)

#         d+= (decision := Decision(w = 5, h= 5,
#                         S = "True",
#                             E = "False").label("Is \n string\n == \nreverse_string?"))
#         d+= Arrow().length(d.unit/2)
#         d+= Arrow().length(d.unit/2)
#         d+= Arrow().right(d.unit).at(decision.E)
        

#         buf = io.BytesIO()
#         d.save(buf, dpi = 300)
#         buf.seek(0)
#         string = base64.b64encode(buf.read())
#         data = urllib.parse.quote(string)
#         return data


def get_pie_chart(df, name, value):
    df_grouped = df.groupby(name)[name].count()
    # print(df_grouped)
    pie_plot = df_grouped.plot.pie()
    pie_plot.legend(bbox_to_anchor=(1.0, 1.0))
    pie_fig = pie_plot.get_figure()
    pie_fig.legend(loc=7)
    pie_fig.tight_layout()
    pie_fig.subplots_adjust(right=0.75)
    pie_buf = io.BytesIO()
    pie_fig.savefig(pie_buf, format="png")
    pie_buf.seek(0)
    pie_string = base64.b64encode(pie_buf.read())
    pie_data = urllib.parse.quote(pie_string)
    return pie_data

def get_timeseries_chart(df, name, value):
    df[name]= pd.to_datetime(df[name])
    grouped_df = df.groupby(df[name].dt.to_period("M"))[value].count()
    # print(grouped_df)
    plot = grouped_df.plot(x=name, y=value)
    # plot.plot(range(10))
    fig = plot.get_figure()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    string = base64.b64encode(buf.read())
    data = urllib.parse.quote(string)
    return data

def get_bar_chart(df, name, value):
    df_grouped = df.groupby(name)[name].count()
    # print(df_grouped)
    bar_plot = df_grouped.plot.bar()
    bar_plot.legend(bbox_to_anchor=(1.0, 1.0))
    bar_fig = bar_plot.get_figure()
    bar_fig.legend(loc=7)
    bar_fig.tight_layout()
    bar_fig.subplots_adjust(right=0.75)
    bar_buf = io.BytesIO()
    bar_fig.savefig(bar_buf, format="png")
    bar_buf.seek(0)
    bar_string = base64.b64encode(bar_buf.read())
    bar_data = urllib.parse.quote(bar_string)
    return bar_data


def file_detail(request, id):
    validate_excel_file(id)
    file = models.DataFile.objects.filter(id=id).first()
    fields = models.Attribute.objects.filter(file=file)
    df = pd.read_csv(file.content.path, encoding='latin-1')
    print(type(df.info()), type(df.describe()))
    data = df.head().to_html(classes='table table-stripped')
    df_desc = df.describe()
    stats = df_desc.to_html(classes='table table-stripped')
    info = df.dtypes.to_frame().to_html(classes='table table-stripped')
    field_df = pd.DataFrame.from_records(fields.values())
    filed_html = field_df.to_html(classes='table table-stripped')

    charts = []
    # charts.append(get_pie_chart(df, "Commit Type", "Message"))
    # chart = {"title":"Commited Date Time Series", "data":get_timeseries_chart(df, "Commited Date", "Message")}
    # charts.append(chart)

    # print(df.describe())
    for item in df_desc:
        # field = type(item)
        # uniqe_value = df_desc[item]["unique"]
        if "date" in item.lower():
            chart = {"title":"Visualize Attribute : "+item.title()+" Time Series", "data":get_timeseries_chart(df, item, item)}
            charts.append(chart)
        try:
            uniqe_value = df_desc[item]["unique"]
        except:
            uniqe_value = len(pd.unique(df[item]))
        print(item, uniqe_value)
        if uniqe_value > 1 and uniqe_value <= 5:
            print(uniqe_value, item)
            chart = {"title":"Visualize Attribute : "+item.title(), "data":get_pie_chart(df, item, item)}
            charts.append(chart)
        if uniqe_value > 5 and uniqe_value <= 15:
            print(uniqe_value, item)
            chart = {"title":"Visualize Attribute : "+item.title(), "data":get_bar_chart(df, item, item)}
            charts.append(chart)
    
    context = {
        "file":file,
        "fields":filed_html, 
        "desc":stats, 
        "info":info, 
        "data":data,
        "charts":charts
    }
    return render(request,app.name+'/datafile_detail.html', context=context)

def get_chart_data(df, name):
    labels = []
    values = []
    df_grouped = df.groupby(name)[name].count()
    for key, value in df_grouped.iteritems():
        print(key, value)
        labels.append(key)
        values.append(value)
    data = {"labels":labels, "values":values}
    # print(data)
    return data

def get_timeseries_data(df, name):
    df[name]= pd.to_datetime(df[name])
    labels = []
    values = []
    # df_grouped = df.groupby(name)[name].count()
    df_grouped = df.groupby(df[name].dt.strftime('%Y-%m'))[name].count()
    for key, value in df_grouped.iteritems():
        print(key, value)
        labels.append(key)
        values.append(value)
    data = {"labels":labels, "values":values}
    # print(data)
    return data
    
    # df[name]= pd.to_datetime(df[name])
    # grouped_df = df.groupby(df[name].dt.to_period("M"))[value].count()
    # # print(grouped_df)
    # plot = grouped_df.plot(x=name, y=value)
    # # plot.plot(range(10))
    # fig = plot.get_figure()
    # buf = io.BytesIO()
    # fig.savefig(buf, format="png")
    # buf.seek(0)
    # string = base64.b64encode(buf.read())
    # data = urllib.parse.quote(string)
    # return data
def analyze_dataset(request, id):
    project = models.Dataset.objects.filter(id=id).first()
    files = models.DataFile.objects.filter(project=project)
    list = models.Attribute.objects.filter(file__in=files).values('file').annotate(total=Count('file')).values('file', 'file__title', 'file__type', 'file__content', 'total')
    file = models.DataFile.objects.filter(project=project, type="Denormalized").first()
    if file == None:
        file = models.DataFile.objects.filter(project=project).first()
    fields = models.Attribute.objects.filter(file=file, is_active=True)
    df = pd.read_csv(file.content.path, encoding='latin-1')
    try:
        df = df.drop("Unnamed: 0",axis=1)
    except:
        pass

    df_desc = df.describe(include = 'all')
    stats = df_desc.to_html(classes='table table-stripped')
    field_titles = []
    for item in fields:
        field_titles.append(item.title)
    print(df.head())
    print(fields)
    print(field_titles)
    group_summary_fields = []
    for item in df_desc:
        item_type = str(df[item].dtypes)
        try:
            uniqe_value = df_desc[item]["unique"]
        except:
            uniqe_value = len(pd.unique(df[item]))
        if "object" in item_type and uniqe_value <= 8:
            group_summary_fields.append(item)
    group_summary_count = df.groupby(group_summary_fields).count().to_html(classes='table table-stripped')
    context = {
        "project":project,
        "list":list,
        "desc":stats, 
        "group_summary_count":group_summary_count
    }
    return render(request,app.name+'/analyze_dataset.html', context=context)

def visualize_dataset(request, id):
    project = models.Dataset.objects.filter(id=id).first()
    file = models.DataFile.objects.filter(project=project, type="Denormalized").first()
    if file == None:
        file = models.DataFile.objects.filter(project=project).first()

    fields = models.Attribute.objects.filter(file=file)
    field_titles = []
    for item in fields:
        if item.is_active == True:
            field_titles.append(item.title.lower())
    df = pd.read_csv(file.content.path, encoding='latin-1')
    try:
        df = df.drop("Unnamed: 0",axis=1)
    except:
        pass
    data = df.head().to_html(classes='table table-stripped')
    df_desc = df.describe(include = 'all')
    stats = df_desc.to_html(classes='table table-stripped')
    info = df.dtypes.to_frame().to_html(classes='table table-stripped')
    field_df = pd.DataFrame.from_records(fields.values())
    filed_html = field_df.to_html(classes='table table-stripped')

    charts = []
    group_summary_fields = []
    group_summary_values = []
    print(field_titles)
    for item in df_desc:
        item_type = str(df[item].dtypes)
        print(item,  item_type)
        chart_id =  uuid.uuid4()
        print("----------", item)
        if item.lower() == "id":
            continue
        elif item.lower() not in field_titles:
            continue
        if "date" in item.lower():
            chart = {"id":chart_id, "type":"line", "title":"Visualize Attribute : "+item.title()+" Time Series", "data":get_timeseries_data(df, item)}
            charts.append(chart)
        try:
            uniqe_value = df_desc[item]["unique"]
        except:
            uniqe_value = len(pd.unique(df[item]))
        # print(item, uniqe_value)
        if uniqe_value > 1 and uniqe_value <= 5:
            chart = {"id":chart_id, "type":"pie", "title":"Visualize Attribute : "+item.title(), "data":get_chart_data(df, item)}
            charts.append(chart)
            print("item_type", item_type)
        if uniqe_value > 5 and uniqe_value <= 100:
            # print(uniqe_value, item)
            chart = {"id":chart_id, "type":"bar", "title":"Visualize Attribute : "+item.title(), "data":get_chart_data(df, item)}
            charts.append(chart)
        if "object" in item_type and uniqe_value <= 10:
            group_summary_fields.append(item)
    # print(df.dtypes)
    print(group_summary_fields)
    if len(group_summary_fields) == 0:
        group_summary_fields = field_titles
    print(group_summary_fields, group_summary_values)
    group_summary_mean = None
    group_summary_count = None
    try:
        group_summary_mean = df.groupby(group_summary_fields).mean().to_html(classes='table table-stripped')
    except:
        pass
    group_summary_count = df.groupby(group_summary_fields).count().to_html(classes='table table-stripped')

    
    context = {
        "project":project,
        "file":file,
        "fields":filed_html, 
        "desc":stats, 
        "info":info, 
        "data":data,
        "charts":charts,
        "group_summary_mean":group_summary_mean,
        "group_summary_count":group_summary_count,
    }
    return render(request,app.name+'/visualize_dataset.html', context=context)


def file_detail_js(request, id):
    validate_excel_file(id)
    file = models.DataFile.objects.filter(id=id).first()
    fields = models.Attribute.objects.filter(file=file)
    field_titles = []
    for item in fields:
        if item.is_active == True:
            field_titles.append(item.title.lower())
    df = pd.read_csv(file.content.path, encoding='latin-1')
    try:
        df = df.drop("Unnamed: 0",axis=1)
    except:
        pass
    data = df.head().to_html(classes='table table-stripped')
    df_desc = df.describe(include = 'all')
    stats = df_desc.to_html(classes='table table-stripped')
    info = df.dtypes.to_frame().to_html(classes='table table-stripped')
    field_df = pd.DataFrame.from_records(fields.values())
    filed_html = field_df.to_html(classes='table table-stripped')

    charts = []
    group_summary_fields = []
    group_summary_values = []
    print(field_titles)
    for item in df_desc:
        item_type = str(df[item].dtypes)
        print(item,  item_type)
        chart_id =  uuid.uuid4()
        print("----------", item)
        if item.lower() == "id":
            continue
        elif item.lower() not in field_titles:
            continue
        if "date" in item.lower():
            chart = {"id":chart_id, "type":"line", "title":"Visualize Attribute : "+item.title()+" Time Series", "data":get_timeseries_data(df, item)}
            charts.append(chart)
        try:
            uniqe_value = df_desc[item]["unique"]
        except:
            uniqe_value = len(pd.unique(df[item]))
        # print(item, uniqe_value)
        if uniqe_value > 1 and uniqe_value <= 5:
            chart = {"id":chart_id, "type":"pie", "title":"Visualize Attribute : "+item.title(), "data":get_chart_data(df, item)}
            charts.append(chart)
            print("item_type", item_type)
        if uniqe_value > 5 and uniqe_value <= 100:
            # print(uniqe_value, item)
            chart = {"id":chart_id, "type":"bar", "title":"Visualize Attribute : "+item.title(), "data":get_chart_data(df, item)}
            charts.append(chart)
        if "object" in item_type and uniqe_value <= 10:
            group_summary_fields.append(item)
    # print(df.dtypes)
    print(group_summary_fields)
    if len(group_summary_fields) == 0:
        group_summary_fields = field_titles
    print(group_summary_fields, group_summary_values)
    group_summary_mean = None
    group_summary_count = None
    try:
        group_summary_mean = df.groupby(group_summary_fields).mean().to_html(classes='table table-stripped')
    except:
        pass
    group_summary_count = df.groupby(group_summary_fields).count().to_html(classes='table table-stripped')

    
    context = {
        "file":file,
        "fields":filed_html, 
        "desc":stats, 
        "info":info, 
        "data":data,
        "charts":charts,
        "group_summary_mean":group_summary_mean,
        "group_summary_count":group_summary_count,
    }
    return render(request,app.name+'/datafile_detail_js.html', context=context)

def get_list_columns(list):
    list_columns = []
    for object in list:
        for field in object._meta.fields:
            list_columns.append(field.name)
        break
    return list_columns

def fields(request, project_id, file_id, id=None):
    fieldForm = forms.AttributeForm(request.POST or None)
    list = models.Attribute.objects.filter(file = id)
    if fieldForm == None:
        fieldForm = forms.AttributeForm(initital={"file":id})
    context = {
        "list":list, 
        "field_form":fieldForm
    }
    return render(request,app.name+'/attributes.html', context=context)

def validate_excel_file(id):
    print("Validation Start --------------------------------")
    validate_field_references(id)
    file = models.DataFile.objects.get(id =id)
    df = pd.read_csv(file.content.path, encoding='latin-1')
    try:
        df = df.drop("Unnamed: 0",axis=1)
    except:
        pass
    meta_data = df.describe(include="all").to_dict('dict')
    i = 0
    for key in meta_data:
        is_unique = False
        pk_reference = None
        type = df.dtypes[key]
        is_pk = False
        if df[key].nunique() == len(df):
            is_unique = True
            print("dtypes", str(type))
            if "64" in str(type):
                is_pk = True
                print("It Pk")
            else:
                print("Not an Pk")
        if is_unique == False:
            pk_reference = models.Attribute.objects.filter(title=key.upper(), is_unique=True, is_pk = True).first()
        field = models.Attribute.objects.filter(file=id, title=key.upper()).first()
        if field != None:
            field.title=key.upper()
            field.index=i
            field.file=file
            field.type = type
            field.is_unique = is_unique
            field.pk_reference = pk_reference
            field.is_pk = is_pk
            field.save()
        else:
            models.Attribute.objects.create(title=key.upper(), index=i, file=file, 
            # count=meta_data[key]['count'], 
            is_unique = is_unique, type = type, pk_reference=pk_reference
            # unique = meta_data[key]['unique'], freq = meta_data[key]['freq'], top = meta_data[key]['top'], 
            )
        i = i+1

def validate_field_references(id):
    fields = models.Attribute.objects.filter(file=id)
    # print("fields", fields)
    for field in fields:
        references = None
        if field.title == "ID":
            references = models.Attribute.objects.filter(Q(title=field.title)|Q(title = field.file.title+"_"+field.title))
        else:
            models.Attribute.objects.filter(title=field.title)
        # print("references", references)
        if references:
            for refAttribute in references:
                if field.id != refAttribute.id:
                    result = models.AttributeReference.objects.filter(field=field, reference = refAttribute).first()
                    if result != None:
                        print("Attribute Found")
                    else:
                        print("OBject Creation ")
                        models.AttributeReference.objects.create(field=field, reference=refAttribute)

