"""My_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from App1 import views


admin.site.site_header = "ECL Admin"
admin.site.site_title = "ECL Admin Portal"
admin.site.index_title = "Welcome to ECL Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', views.login, name='login'),
    path('', views.login, name='login'),
    path('index', views.show_options, name='index'),
    path('selected',views.selected, name = 'select'),
    path('cal', views.cal),
    path('upload', views.upload, name='upload'),
    path('logout', views.logout, name = 'logout'),
    path('uploaded_success',views.uploaded_success,name='uploaded_success'),
    path('regre',views.regre, name='regre'),
    path('generate_report',views.generate_report,name ='generate_report'),
    path('reupload_file',views.reupload_file,name ='reupload_file'),
    path('flag_check', views.flag_check, name = 'flag_check'),
    path('reupload', views.reupload, name = 'reupload'),
    path('view_report', views.view_report, name = 'view_report'),
    path('cal_view', views.cal_view, name = 'cal_view'),
    path('download', views.download, name = 'download'),
    path('chart', views.chart, name= 'chart')


]
