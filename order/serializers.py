from rest_framework import serializers
from order.models import PaymentDetails,PaymentTypeMaster

class PaymentTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypeMaster
        fields = '__all__'

class GetPaymentTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypeMaster
        fields = ['id','name','description']
