from django.urls import path
from adminapp.views import *
from django.conf.urls import url
from order.views import PaymentTypeMasterView


app_name = 'order'


urlpatterns = [
    path('payment-type-master/',PaymentTypeMasterView.as_view(),name='paymenttypemaster'),
]