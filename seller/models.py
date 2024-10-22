from django.db import models
from adminapp.models import BaseModel,IUMaster
from users.models import *
# Create your models here.

class SellerApplicationDetails(BaseModel):
    """seller approval"""
    user=models.ForeignKey(CustomUser,related_name='seller-details',on_delete=models.CASCADE)#refer the user id
    details=models.JSONField(default=dict, blank=True,null=True)#seller details
    application_status=models.CharField(max_length=30,blank=True,null=True,default='pending')#check the status
    is_rejected=models.BooleanField(default=False)#check the rejection
    reason=models.TextField(max_length=100,blank=True,null=True)#reason for rejection
    iu_id=models.ForeignKey(IUMaster,related_name='iu-id',on_delete=models.CASCADE)
    class Meta:
        db_table = 'seller_application_details'
        ordering = ['created_at']
class SellerProfile(BaseModel):
    """to create a seller registration"""
    user=models.ForeignKey(CustomUser,related_name='seller',on_delete=models.CASCADE)
    seller_application_id=models.ForeignKey(SellerApplicationDetails,related_name='seller-approval',on_delete=models.CASCADE)
    bussiness_name=models.CharField(max_length=150,null=True,blank=True)#name of the bussiness
    address=models.TextField(null=True,blank=True)#seller address
    email=models.EmailField(unique=True)#seller email -unique
    mobile_number=models.PositiveIntegerField(unique=True,blank=True)#seller mobile no
    gst_number=models.CharField(max_length=20)#get seller gst no
    pan_number=models.CharField(unique=True,max_length=15)#pan number for seller
    account_number=models.CharField(max_length=30)#bank account number
    ifsc_number=models.CharField(max_length=15)#ifsc number
    iu_id=models.ForeignKey(IUMaster,related_name='iu-id',on_delete=models.CASCADE)

    class Meta:
        db_table = 'seller_profile'
        ordering = ['created_at']

