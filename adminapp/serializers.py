from rest_framework import serializers
from adminapp.models import IUMaster

class IUMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = IUMaster
        fields = ['id', 'name', 'domain', 'contact_mobile_no', 'logo', 'address', 'city', 'state']
        