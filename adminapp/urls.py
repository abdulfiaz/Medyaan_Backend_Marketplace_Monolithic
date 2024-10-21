from django.urls import path
from adminapp.views import *

urlpatterns = [
    path('iumaster/',IUMasterAPI.as_view(),name='iumaster'),

]