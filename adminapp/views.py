from django.shortcuts import render
from adminapp.models import *
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction
from users.auth import get_user_roles
from adminapp.serializers import IUMasterSerializer



class IUMasterAPI(APIView):
    def get(self, request):
        iu_id = request.query_params.get('id')
        rolename = get_user_roles(request)

        if rolename != 'ADMIN':
            return Response({"status": "error", "message": "Only ADMIN can have the access!"}, status=status.HTTP_403_FORBIDDEN)

        try:
            if iu_id:
                iumaster = IUMaster.objects.filter(id=iu_id, is_active=True)
                if not iumaster:
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
        if rolename != "ADMIN":
            return Response({"status": "error", "message": "Only ADMIN can access this!"}, status=status.HTTP_403_FORBIDDEN)

        transaction.set_autocommit(False)
        data=request.data
        data['created_by']=request.user.id
        serializer = IUMasterSerializer(data=data)
        try:
            if serializer.is_valid():
                serializer.save()
                transaction.commit()
                return Response({"status": "success", "message": "Details created successfully"}, status=status.HTTP_201_CREATED)
        except :
            transaction.rollback()
            return Response({"status": "error", "message":  serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        iu_id = request.data.get('id')
        rolename = get_user_roles(request)

        if rolename != "ADMIN":
            return Response({"status": "error", "message": "Only ADMIN can access this!"}, status=status.HTTP_403_FORBIDDEN)

        
        iumaster = IUMaster.objects.filter(id=iu_id, is_active=True)
        if not iumaster:
            return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)

        transaction.set_autocommit(False)
        serializer = IUMasterSerializer(iumaster, data=request.data, partial=True)
        try:
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return Response({"status": "success", "message": "Details updated successfully"}, status=status.HTTP_200_OK)
            transaction.commit()
        
        except Exception as e:
            transaction.rollback()
            return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        iu_id = request.data.get('id')
        rolename = get_user_roles(request)

        if rolename != "ADMIN":
            return Response({"status": "error", "message": "Only ADMIN can access this!"}, status=status.HTTP_403_FORBIDDEN)

        try:
            iumaster = IUMaster.objects.filter(id=iu_id, is_active=True).first()
            if not iumaster:
                return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                iumaster.is_active = False
                iumaster.save()
                return Response({"status": "success", "message": "IU Master deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)