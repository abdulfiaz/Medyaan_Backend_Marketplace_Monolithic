from django.urls import path
from .views import *
from django.conf.urls import url
from .utils import create_notification

app_name = 'notification'


urlpatterns = [
    path('template/',TemplateMasterView.as_view(),name='template'), 
    path('template/<int:id>/',TemplateMasterView.as_view(),name='get_template'), 
    path('event/',EventMasterView.as_view(),name='event'), 
    path('event/<int:id>/',EventMasterView.as_view(),name='get_event'),
    path('notification/',NotificationView.as_view(),name='notification'),    
]