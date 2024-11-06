from django.urls import path
from adminapp.views import *
from order.views import *


app_name = 'order'


urlpatterns = [
    path('category/',CategoryMasterAPI.as_view(),name='category-details'),
    path('category/<int:id>/', CategoryMasterAPI.as_view(), name='category'),
    path('variant/',VariantMasterAPI.as_view(),name='variant-details'),
    path('variant/<int:id>/', VariantMasterAPI.as_view(), name='variant-details'),
    path('payment-type-master/',PaymentTypeMasterView.as_view(),name='paymenttypemaster'),
]

