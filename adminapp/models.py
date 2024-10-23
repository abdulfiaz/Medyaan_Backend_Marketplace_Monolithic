from django.db import models
from django.contrib.postgres.fields import JSONField

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)  # auto_now=True for updates
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

# to store host names to differentiate the user based on the host 
class IUMaster(BaseModel):
    name=models.CharField(max_length=50)
    domain=models.CharField(max_length=50) #host name 
    contact_mobile_no=models.CharField(max_length=15)
    logo=JSONField(default=dict, blank=True) # logo image stored as json 
    address=models.CharField(max_length=250,null=True,blank=True)
    city=models.CharField(max_length=50,null=True,blank=True)
    state=models.CharField(max_length=50,null=True,blank=True)
    

    class Meta:
        db_table = 'iu_master'
        ordering = ['created_at']


class IUJsonMaster(BaseModel):
    channel_name=models.CharField(max_length=100,null=True,blank=True)#channel name of the seller register
    document_type=models.CharField(max_length=50,null=True,blank=True)#type of document
    document_name=models.CharField(max_length=30,null=True,blank=True)#document name
    details=JSONField(default=dict, blank=True)#additional details 
    version=models.CharField(max_length=5,default=1)
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE,related_name='iu_jsonmaster')
    class Meta:
        db_table = 'iujsonmaster'
        ordering = ['created_at']
