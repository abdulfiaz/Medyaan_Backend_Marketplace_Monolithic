from rest_framework import serializers
from adminapp.models import IUMaster,IUJsonMaster

class IUMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = IUMaster
        fields = ['id', 'name', 'domain', 'contact_mobile_no', 'logo', 'address', 'city', 'state','modified_by','created_by']
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def update(self, obj, validated_data):
        for attr, value in validated_data.items():
            if value:  
                setattr(obj, attr, value)
        obj.save()
        return obj
        
class IUJsonMasterSerializers(serializers.ModelSerializer):
    class Meta:
        model=IUJsonMaster
        fields=['id','channel_name','document_type','document_name','details','version','iu_id','created_at_timestamp']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def update(self, obj, validated_data):
        for attr, value in validated_data.items():
            if value:  
                setattr(obj, attr, value)
        obj.save()
        return obj