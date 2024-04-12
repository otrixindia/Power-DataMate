"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangofile.com/en/4.1/topics/http/urls/
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
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),

    path('datasets/', views.datasets, name='index'),
    path('datasets/<id>', views.datasets, name='dataset'),

    path('datasets/<project_id>/datafiles/<id>', views.datafiles, name='datafile'),
    path('datasets/<project_id>/datafiles', views.datafiles, name='datafile'),

    path('projects/', views.index, name='projects'),
    # path('projects/<id>', views.projects, name='projects'),
    path('projects/<id>', views.project_detail, name='projects'),
    path('generate_erd/<id>', views.generate_erd, name='projects'),
    path('analyze_dataset/<id>', views.analyze_dataset, name='projects'),
    path('visualize_dataset/<id>', views.visualize_dataset, name='projects'),
    # path('files/<id>', views.files, name='files'),
    path('files/<id>', views.file_detail_js, name='files'),
    path('analyze_files/<id>', views.file_detail_js, name='files'),

    path('connectdb/<id>', views.connect_db, name='projects'),
    path('connectdb/<id>/<table_name>', views.connect_db, name='projects'),

    # path('files/<id>', views.file_detail, name='files'),
    # path('files/', views.files, name='files'),
    # path('files/<id>', views.files, name='files'),
    # path('files/<id>/validate', views.validate_excel_file, name='files'),
    # path('files/<file_id>/attributes/<id>', views.fields, name='validate_excel_file'),
]
