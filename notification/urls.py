from django.urls import path
from .views import *
from django.conf.urls import url

app_name = 'notification'


urlpatterns = [
    path('template/',TemplateMasterView.as_view(),name='template'), 
    path('event/',EventMasterView.as_view(),name='event'), 
    path('notification/',NotificationView.as_view(),name='notification'),    
]