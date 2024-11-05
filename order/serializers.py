from rest_framework import serializers
from order.models import *

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryMaster
        fields = ['id', 'name', 'description','iu_id','created_by','modified_by']

    def update(self, obj, validated_data):
        
        for attr, value in validated_data.items():
            if value:  
                setattr(obj, attr, value)
        obj.save()
        return obj
 
 
class Categoryserializer(serializers.ModelSerializer):
    sub_categories = SubCategorySerializer(many=True, read_only=True)
 
    class Meta:
        model = ProductCategoryMaster
        fields = ['id', 'name', 'description', 'sub_categories','created_by','iu_id','modified_by']
 


class PaymentTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypeMaster
        fields = '__all__'

class GetPaymentTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypeMaster
        fields = ['id','name','description']
