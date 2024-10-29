from django.shortcuts import render
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.db import transaction, IntegrityError
from users.models import *
from order.models import PaymentTypeMaster
from rest_framework.response import Response
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from django.conf import settings
from order.serializers import PaymentTypeMasterSerializer,GetPaymentTypeMasterSerializer
from adminapp.iudetail import get_iuobj
from users.auth import get_user_roles
from rest_framework.exceptions import AuthenticationFailed


# paymenttypemaster crud i.e mode of payment cards,cash on delivery,upi etc
class PaymentTypeMasterView(APIView):
    def get(self, request):
        payment_type_id = request.query_params.get('payment_type_id', None)
        role_name = get_user_roles(request)
        domain = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)

        if role_name != 'admin':
            return Response({"status": "error", "message": "only admin can view payment type master details"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            if payment_type_id:
                payment_type_master = PaymentTypeMaster.objects.get(id=payment_type_id, iu_id=iu_id, is_active=True)
                serializer = GetPaymentTypeMasterSerializer(payment_type_master)  
            else:
                
                payment_type_master = PaymentTypeMaster.objects.filter(iu_id=iu_id, is_active=True)
                serializer = GetPaymentTypeMasterSerializer(payment_type_master, many=True)  

            return Response({"status": "success", "message": "data retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        except PaymentTypeMaster.DoesNotExist:
            return Response({"status": "error", "message": "PaymentType not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)

        role_name = get_user_roles(request)

        if role_name != 'admin':
            return Response({"status":"error","message":"only admin can create PaymentTypeMaster"},status=status.HTTP_401_UNAUTHORIZED)
        
        transaction.set_autocommit(False)
        data = request.data
        data['created_by'] = request.user.id
        data['iu_id'] = iu_id.id

        serializer = PaymentTypeMasterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            transaction.commit()
            return Response({"status":"success","message":"paymenttype created successfully"},status=status.HTTP_201_CREATED)
        else:
            transaction.rollback()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def put(self,request):
        domain = request.META.get('HTTP_ORIGIN',settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)
        role_name = get_user_roles(request)
        payment_type_master_id = request.data.get('id')

        if not payment_type_master_id :
            return Response({"status":"error","message":"payment_type_master id is required"},status=status.HTTP_400_BAD_REQUEST)

        if role_name != 'admin':
            return Response({"status":"error","message":"only admin can update this"},status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            payment_type_obj = PaymentTypeMaster.objects.get(id=payment_type_master_id,iu_id=iu_id,is_active=True)
        except PaymentTypeMaster.DoesNotExist:
            return Response({"status": "error", "message": "PaymentTypeMaster not found"}, status=status.HTTP_404_NOT_FOUND)
        
        transaction.set_autocommit(False)
        data = request.data
        data['modified_by']=request.user.id
        data['iu_id']=iu_id.id

        serializer = PaymentTypeMasterSerializer(payment_type_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            transaction.commit()
            return Response({"status": "success", "message": "PaymentType updated successfully"}, status=status.HTTP_200_OK)
        else:
            transaction.rollback()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request):
        payment_type_master_id = request.data.get('id')
        role_name = get_user_roles(request)
        domain = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_master = get_iuobj(domain)

        if not payment_type_master_id:
            return Response({'status':'error','message':"id is required"},status=status.HTTP_404_NOT_FOUND)
        
        if role_name != 'admin':
            return Response({"status":"error","message":"only admin can delete this"},status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            payment_type_obj = PaymentTypeMaster.objects.get(id=payment_type_master_id, iu_id=iu_master,is_active=True)
        except PaymentTypeMaster.DoesNotExist:
            return Response({"status": "error", "message": "id not found"}, status=status.HTTP_404_NOT_FOUND)
        
        transaction.set_autocommit(False)
        serializer = PaymentTypeMasterSerializer(payment_type_obj, data={'is_active': False,'modified_by':request.user.id}, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            transaction.commit()
            return Response({"status": "success", "message": "payment_type deleted successfully"}, status=status.HTTP_200_OK)

        else:
            transaction.rollback()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        



