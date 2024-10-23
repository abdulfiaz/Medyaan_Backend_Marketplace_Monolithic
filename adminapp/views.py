from django.shortcuts import render
from adminapp.models import *
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction
from adminapp.rolename import *
from adminapp.serializers import IUMasterSerializer



class IUMasterAPI(APIView):
    serializer_class=IUMasterSerializer()
    def get(self, request):
        iu_id = request.query_params.get('id')
        rolename = getrolename(request)

        if rolename != 'ADMIN':
            return Response({"status": "error", "message": "Only ADMIN can have the access!"}, status=status.HTTP_403_FORBIDDEN)

        try:
            if iu_id:
                iumaster = IUMaster.objects.filter(id=iu_id, is_active=True)
                if not iumaster:
                    return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)
                serializer = self.serializer_class(iumaster)
            else:
                iumaster = IUMaster.objects.filter(is_active=True)
                serializer = IUMasterSerializer(iumaster, many=True)
            
            return Response({"status": "success", "message": "IUMaster list retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        rolename = getrolename(request)
        if rolename != "ADMIN":
            return Response({"status": "error", "message": "Only ADMIN can access this!"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                serializer = IUMasterSerializer(data=request.data)
                if serializer.is_valid():
                    iumaster = serializer.save(created_by=request.user)
                    return Response({"status": "success", "message": "Details created successfully"}, status=status.HTTP_201_CREATED)
                return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        iu_id = request.data.get('id')
        rolename = getrolename(request)

        if rolename != "ADMIN":
            return Response({"status": "error", "message": "Only ADMIN can access this!"}, status=status.HTTP_403_FORBIDDEN)

        try:
            iumaster = IUMaster.objects.filter(id=iu_id, is_active=True)
            if not iumaster:
                return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                serializer = IUMasterSerializer(iumaster, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user)
                    return Response({"status": "success", "message": "Details updated successfully"}, status=status.HTTP_200_OK)
                return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        iu_id = request.data.get('id')
        rolename = getrolename(request)

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