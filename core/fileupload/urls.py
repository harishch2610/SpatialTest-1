from django.conf.urls import url
from django.urls import path

# from core.urls import *
# from . import views
# from .views import index
# from core.fileupload import views
from .views import index, success

app_name = "fileupload"

urlpatterns = [
    # path('', views.index, name='index'),   r'^aaa$

    path('harish', success, name='success'),
    path('', index, name='index'),


]
