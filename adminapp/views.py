from django.conf import settings
from django.shortcuts import render
from adminapp.models import *
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction
from users.auth import get_user_roles
from adminapp.serializers import IUMasterSerializer,IUJsonMasterSerializers
from adminapp.iudetail import *


class IUMasterAPI(APIView):
    def get(self, request):
        iu_id = request.query_params.get('id')
        rolename = get_user_roles(request)

        if rolename != 'admin':
            return Response({"status": "error", "message": "Only admin can have the access!"}, status=status.HTTP_403_FORBIDDEN)

        try:
            if iu_id:
                try:
                    iumaster = IUMaster.objects.get(id=iu_id, is_active=True)
                except IUMaster.DoesNotExist:
                    return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)
                serializer = IUMasterSerializer(iumaster)
            else:
                iumaster = IUMaster.objects.filter(is_active=True)
                serializer = IUMasterSerializer(iumaster, many=True)
            
            return Response({"status": "success", "message": "IUMaster list retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        rolename = get_user_roles(request)
        if rolename != "admin":
            return Response({"status": "error", "message": "Only admin can access this!"}, status=status.HTTP_403_FORBIDDEN)

        transaction.set_autocommit(False)
        data=request.data
        data['created_by']=request.user.id
        serializer = IUMasterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            transaction.commit()
            return Response({"status": "success", "message": "Details created successfully"}, status=status.HTTP_201_CREATED)
        else :
            transaction.rollback()
            return Response({"status": "error", "message":  serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        iu_id = request.data.get('id')
        rolename = get_user_roles(request)

        if rolename != "admin":
            return Response({"status": "error", "message": "Only admin can access this!"}, status=status.HTTP_403_FORBIDDEN)

        if not iu_id:
            return Response({"status":"error","message":"iu_id is required"})
        
        try:
            iumaster = IUMaster.objects.get(id=iu_id, is_active=True)
        except IUMaster.DoesNotExist:
            return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)
        
        transaction.set_autocommit(False)
        data=request.data
        data['modified_by']=request.user.id
        print("modify---->",data['modified_by'])
        serializer = IUMasterSerializer(iumaster, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            transaction.commit()
            return Response({"status": "success", "message": "Details updated successfully"}, status=status.HTTP_200_OK)
            
        else:
            transaction.rollback()
            return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        iu_id = request.data.get('id')
        rolename = get_user_roles(request)

        if rolename != "admin":
            return Response({"status": "error", "message": "Only admin can access this!"}, status=status.HTTP_403_FORBIDDEN)
        if not iu_id:
            return Response({"status":"error","message":"iu_id is required"})
        
        try:
            iumaster = IUMaster.objects.get(id=iu_id, is_active=True)
        except IUMaster.DoesNotExist:
            return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            transaction.set_autocommit(False)
            iumaster.is_active = False
            iumaster.modified_by=request.user.id
            iumaster.save()
            transaction.commit()
            return Response({"status": "success", "message": "IU Master deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            transaction.rollback()
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class IUJsonMasterAPI(APIView):
    serializer_class=IUJsonMasterSerializers
    def get(self,request,id=None):
        roles = get_user_roles(request)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if roles !="admin":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        
        if id:
            iujsonmaster=IUJsonMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
            serializer=self.serializer_class(iujsonmaster).data
        else:
            iujsonmaster=IUJsonMaster.objects.filter(is_active=True,iu_id=iu_id)
            serializer = self.serializer_class(iujsonmaster, many=True)

        return Response({"status":"success","message":"successfully received data","data":serializer.data},status=status.HTTP_200_OK)

    def post(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="admin":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'failure', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        data['iu_id'] = iu_id.id

        iujsonmaster=self.serializer_class(data=data)
        if iujsonmaster.is_valid():
            serializer_iu=iujsonmaster.save(created_by=request.user.id)

            return Response({"status":"success","message":"Successfully created","data":serializer_iu.id},status=status.HTTP_201_CREATED)
        else:
            return Response({"status":"error","message":"data is not created","data":serializer_iu.errors},status=status.HTTP_400_BAD_REQUEST)
            
    def put(self,request,id=None):
        roles = get_user_roles(request)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if roles !="admin":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
    
        iujsonmaster=IUJsonMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
       
        serializer=self.serializer_class(iujsonmaster,data=request.data,partial=True)
        if serializer.is_valid():
            serializer_data=serializer.save(modified_by=request.user.id)
            return Response({"status":"success","message":"successfully update the data","data":serializer_data.id},status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id=None):
        roles = get_user_roles(request)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if roles !="admin":
            return Response({ "status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        
        iujsonmaster=IUJsonMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
        if iujsonmaster:            
            iujsonmaster.is_active = False
            serializer_data=iujsonmaster.save()
            return Response({"status": "success", "message": "IUJson deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","message":"iujson  is not delete"},status=status.HTTP_400_BAD_REQUEST)