from django.urls import path
from .views import SellerApplicationDetailsAPI,ManagerApprovalView
from django.conf.urls import url


app_name = 'seller'


urlpatterns = [
    path('approval/',SellerApplicationDetailsAPI.as_view(),name='seller-details'),
    path('approval/<int:id>/',SellerApplicationDetailsAPI.as_view(),name='get-seller-details'),
    path('get_seller/',ManagerApprovalView.as_view(),name='get_all_seller_details'),
    path('get_seller/<int:id>/',ManagerApprovalView.as_view(),name='get_seller_status_details'),
    


]