from django.db import models
from django.contrib.postgres.fields import JSONField

# to store host names to differentiate the user based on the host 
class IUMaster(models.Model):
    name=models.CharField(max_length=50)
    domain=models.CharField(max_length=50) #host name 
    contact_mobile_no=models.CharField(max_length=15)
    logo=JSONField(default=dict) # logo image stored as json 
    address=models.CharField(max_length=250,null=True,blank=True)
    city=models.CharField(max_length=50,null=True,blank=True)
    state=models.CharField(max_length=50,null=True,blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)

    class Meta:
        db_table = 'iumaster'
        ordering = ['-created_at']


