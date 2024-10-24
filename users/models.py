from django.db import models
from adminapp.models import BaseModel,IUMaster
from django.contrib.auth.models import AbstractUser
from django.db import models
from adminapp.models import *
from users.models import *
# Create your models here.
class CustomUser(AbstractUser,BaseModel):
    username = None
    # email = models.EmailField(_('email address'), unique=True)
    mobile_number = models.CharField(max_length=32)

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []
    email=models.EmailField(unique=True)#email-unique
    temp_code=models.CharField(max_length=10, null=True, blank=True)#temp-code for otp
    is_approval=models.BooleanField(default=False)
    last_login_role = models.CharField(max_length=30,blank=True,null=True)
    approved_by=models.CharField(max_length=10, null=True, blank=True)
    iu_id=models.ForeignKey(IUMaster,related_name='CustomUser_iu_id',on_delete=models.CASCADE)

    class Meta:
        unique_together = (('mobile_number', 'iu_id'),)

        db_table = 'customuser'
        ordering = ['created_at']
    
    def __str__(self):
        return self.mobile_number

class UserPersonalProfile(BaseModel):  
    """details of user"""
    firstname=models.CharField(max_length=30,null=True,blank=True)#name of user
    lastname=models.CharField(max_length=30,null=True,blank=True)
    user=models.ForeignKey(CustomUser,related_name='userdetails',on_delete=models.CASCADE)#refer the custom user
    profilephoto=JSONField(null=True,blank=True,default=dict)#image field
    gender=models.CharField(max_length=20,null=True,blank=True)#for gender
    age=models.IntegerField(blank=True,null=True)#to specified the age
    language=models.TextField(blank=True,null=True)#to specified the language
    primary_address=models.TextField(blank=True,null=True)#address of user
    secondary_address=models.TextField(blank=True,null=True)#address of user
    iu_id = models.ForeignKey(IUMaster, on_delete=models.CASCADE, related_name='user_personal_profile_iu')

    class Meta:
        db_table = 'user_profile_details'
        ordering = ['created_at']



class RoleMaster(BaseModel):
    name = models.CharField(max_length=50, unique=True)#name of the role
    description = models.TextField(blank=True, null=True)#description about the role
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer the iu_id

    class Meta:
        db_table="role_master"
        ordering = ["created_at"]



class RoleMapping(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='custom_user')#refer the user_id
    role = models.ForeignKey(RoleMaster, on_delete=models.CASCADE,related_name='role_master')#refer the role 
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer the iu_id

    class Meta:
        db_table="role_mapping"
        


