from django.urls import path
from .views import SellerApplicationDetailsAPI,ManagerApprovalView,SellerUpdateProfileAPI,ManagerApproveUpdateAPI
from django.conf.urls import url


app_name = 'seller'


urlpatterns = [
    path('application/',SellerApplicationDetailsAPI.as_view(),name='seller-application'),
    path('manager_approval/',ManagerApprovalView.as_view(),name='manager-approval'),
    path('seller_profile_update/',SellerUpdateProfileAPI.as_view(),name='seller-update-profile'),
    path('manager_profile_update/',ManagerApproveUpdateAPI.as_view(),name='seller-update-profile'),
]
