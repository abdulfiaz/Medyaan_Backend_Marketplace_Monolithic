from django.urls import path
from adminapp.views import *
from order.views import *


app_name = 'order'


urlpatterns = [
    path('category/',CategoryMasterAPI.as_view(),name='category-details'),
    path('variant/',VariantMasterAPI.as_view(),name='variant-details'),
    path('variantoption/',VariantOptionAPI.as_view(),name='variant_options'),
    path('productvariation/',ProductVariationAPI.as_view(),name='product_variant'),
    path('manager/',ManagerAPI.as_view(), name='manager-details'),
    path('payment-type-master/',PaymentTypeMasterView.as_view(),name='paymenttypemaster'),
]



 
