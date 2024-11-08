from django.urls import path
from adminapp.views import *
from django.conf.urls import url


app_name = 'adminapp'


urlpatterns = [
    path('iumaster/',IUMasterAPI.as_view(),name='iumaster'),
    path('get_iudetails/<int:id>/',IUJsonMasterAPI.as_view(),name='iujsonmaster'),
    path('create_iujson/',IUJsonMasterAPI.as_view(),name='create_iujsonmaster'),

]