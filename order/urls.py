from django.urls import path
from adminapp.views import *
from order.views import *


app_name = 'order'


urlpatterns = [
    path('category/',CategoryMasterAPI.as_view(),name='category-details'),
    path('category/<int:id>/', CategoryMasterAPI.as_view(), name='category'),
    path('payment-type-master/',PaymentTypeMasterView.as_view(),name='paymenttypemaster'),
]
