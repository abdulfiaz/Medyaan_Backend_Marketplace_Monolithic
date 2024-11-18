from django.urls import path
from adminapp.views import *
from order.views import *


app_name = 'order'


urlpatterns = [
    path('category/',CategoryMasterAPI.as_view(),name='category-details'),
    path('variant/',VariantMasterAPI.as_view(),name='variant-details'),
    path('variantoption/',VariantOptionAPI.as_view(),name='variant_options'),
    path('productvariation/',ProductVariationAPI.as_view(),name='product_variant'),
    path('manager/',ManagerdetailsAPI.as_view(), name='manager-details'),
    path('Buyer/',BuyerView.as_view(), name='manager-details'),
    path('payment-type-master/',PaymentTypeMasterView.as_view(),name='paymenttypemaster'),
    path('product/',ProductMasterView.as_view(),name='productmaster'),
    path('order_invoice/',OrderInvoiceAPI.as_view(),name='order_invoice'),
    path('Product_name/',ProductFetchAPI.as_view(), name='product_name'),
    path('payment_detail/',PaymentDetailsAPIView.as_view(), name='payment_detail'),
    path('wishlistitems/',WishListAPI.as_view()),
    path('cartitems/',CartItemAPI.as_view()),
    path('feedback/',FeedbackAPI.as_view()),
    path('upload_image/',UploadImagesAPI.as_view(),name='upload_image'),

]

 