from django.urls import path
from adminapp.views import *
from django.conf.urls import url


app_name = 'adminapp'


urlpatterns = [
    path('iumaster/',IUMasterAPI.as_view(),name='iumaster'),
    path('iujson/',IUJsonMasterAPI.as_view(),name='iujson_master'),

]