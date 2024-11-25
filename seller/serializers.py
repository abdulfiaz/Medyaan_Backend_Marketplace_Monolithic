from django.conf import settings
from requests import Response
from rest_framework import serializers
from users.models import CustomUser
from .models import SellerProfile,SellerApplicationDetails
from adminapp.models import IUJsonMaster
from adminapp.iudetail import *
from rest_framework.views import APIView,status


class SellerApplicationDetailsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model=SellerApplicationDetails
        fields=['id','user','details','application_status','is_rejected','reason','iu_id']
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
class SellerProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model=SellerProfile
        fields=['id','user','seller_application_id','bussiness_name','address','email','mobile_number','gst_number','pan_number','account_number','ifsc_number','return_amount','iu_id']