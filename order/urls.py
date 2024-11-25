from django.urls import path
from adminapp.views import *
from order.views import *


app_name = 'order'


urlpatterns = [
    path('create/category/',CategoryMasterAPI.as_view(),name='category-details'),
    path('create/variant/',VariantMasterAPI.as_view(),name='variant-details'),
    path('create/variantoption/',VariantOptionAPI.as_view(),name='variant_options'),
    path('create/productvariation/',ProductVariationAPI.as_view(),name='product_variant'),
    path('manageraccess/',ManagerdetailsAPI.as_view()),
    path('buyer/',BuyerView.as_view()),
    path('orderseller/',SellerOrderStatus.as_view()),
    path('buyerorder/',BuyerOrderDetailsAPI.as_view()),
    path('payment-type-master/',PaymentTypeMasterView.as_view(),name='paymenttypemaster'),
    path('product/',ProductMasterView.as_view(),name='productmaster'),
    path('order_invoice/',OrderInvoiceAPI.as_view(),name='order_invoice'),
    path('Product_name/',ProductFetchAPI.as_view(), name='product_name'),
    path('payment_detail/',PaymentDetailsAPIView.as_view(), name='payment_detail'),
    path('wishlistitems/',WishListAPI.as_view()),
    path('cartitems/',CartItemAPI.as_view()),
    path('feedback/',FeedbackAPI.as_view()),
    path('upload_image/',UploadImagesAPI.as_view(),name='upload_image'),
    path('order_type_master/',OrderTypeAPI.as_view(),name='order_type_master'),
    path('invoice_model/',InvoiceModelAPI.as_view(),name='invoice_model'),


]
