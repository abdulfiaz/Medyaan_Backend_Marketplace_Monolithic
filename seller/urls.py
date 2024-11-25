from django.urls import path
from .views import SellerApplicationDetailsAPI,ManagerApprovalView
from django.conf.urls import url


app_name = 'seller'


urlpatterns = [
    path('application/',SellerApplicationDetailsAPI.as_view(),name='seller-application'),
    path('manager_approval/',ManagerApprovalView.as_view(),name='manager-approval'),
]