from rest_framework import serializers
from adminapp.models import IUMaster,IUJsonMaster

class IUMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = IUMaster
        fields = ['id', 'name', 'domain', 'contact_mobile_no', 'logo', 'address', 'city', 'state','modified_by','created_by']
        
class IUJsonMasterSerializers(serializers.ModelSerializer):
    class Meta:
        model=IUJsonMaster
        fields=['id','channel_name','document_type','document_name','details','version','iu_id','created_at_timestamp']