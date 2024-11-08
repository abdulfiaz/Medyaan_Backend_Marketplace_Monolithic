from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import TemplateMasterSerializer,EventMasterSerializer,NotificationSerializer
from .models import *
from adminapp.iudetail import *
from users.auth import *
from users.models import *
from rest_framework.response import Response
from rest_framework import status

class TemplateMasterView(APIView):
    serializer_class=TemplateMasterSerializer
    def get(self, request, id=None):
        roles = get_user_roles(request)
        if roles !="admin":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        if id:
            template = TemplateMaster.objects.get(id=id,is_active=True)
            serializer = self.serializer_class(template)

        else:
            templates = TemplateMaster.objects.filter(is_active=True)
            serializer = self.serializer_class(templates, many=True)
        
        return Response({'status': 'success', 'message': 'successfully receive data.','data':serializer.data},status=status.HTTP_200_OK)
    
    def post(self,request):
        roles = get_user_roles(request)
        if roles !="admin":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        data=request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer_data=serializer.save(created_by=request.user.id)
            return Response({'status': 'success', 'message': 'template created successfully',"data":serializer_data.id},status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'message': 'template not create',"data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, id):
        roles = get_user_roles(request)
        if roles !="admin":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        try:
            template = TemplateMaster.objects.get(id=id,is_active=True)
        except TemplateMaster.DoesNotExist:
            return Response({"error": "Template not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(template, data=request.data,partial=True)
        if serializer.is_valid():
            serializer_data=serializer.save(modified_by=request.user.id)
            return Response({'status': 'success', 'message': 'successfully update the template.','data':serializer_data.id},status=status.HTTP_200_OK)

        return Response({'status': 'error', 'message': 'template not found',"data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        roles = get_user_roles(request)
        if roles !="admin":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        try:
            template = TemplateMaster.objects.get(id=id,is_active=True)
            template.is_active=False
            serializer_data=template.save(modified_by=request.user.id)
            return Response({"status":"success","message":"deleted successfully","data":serializer_data.id},status=status.HTTP_200_OK)
        except TemplateMaster.DoesNotExist:
            return Response({'status': 'error', 'message': 'template not found'}, status=status.HTTP_400_BAD_REQUEST)


class EventMasterView(APIView):
    serializer_class=EventMasterSerializer
    def get(self, request, id=None):
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        if id:
            event = EventMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
            serializer = self.serializer_class(event)       
        else:
            events = EventMaster.objects.filter(is_active=True,iu_id=iu_id)
            serializer = self.serializer_class(events, many=True)
        return Response({'status': 'success', 'message': 'successfully receive data.','data':serializer.data},status=status.HTTP_200_OK)

    
    def post(self, request):
        data=request.data
        role=data.get('role') 
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        data['iu_id'] = iu_id.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer_data=serializer.save(role=role,created_by=request.user.id)
            
            return Response({'status': 'success', 'message': 'event created successfully.','data':serializer_data.id}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'message': 'event not created',"data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, id):
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            event = EventMaster.objects.get(id=id,iu_id=iu_id,is_active=True)
        except EventMaster.DoesNotExist:
            return Response({"error": "event not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(event, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=request.user.id)
            return Response({'status': 'success', 'message': 'successfully update the data.'},status=status.HTTP_200_OK)

        return Response({'status': 'error', 'message': 'data is not update',"data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        user=request.user
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            event = EventMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
            event.is_active=False
            event.save(modified_by=request.user.id)
            return Response({"status":"success","message":"deleted successfully"},status=status.HTTP_200_OK)
        except EventMaster.DoesNotExist:
            return Response({"status":"error","message":"data is not delete"},status=status.HTTP_400_BAD_REQUEST)
            
class NotificationView(APIView):
    serializer_class=NotificationSerializer
    def get(self, request, id=None):
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        if id:
            message = Notification.objects.get(id=id,is_active=True,iu_id=iu_id)
            serializer = self.serializer_class(message)       
        else:
            message = Notification.objects.filter(is_active=True)
            serializer = self.serializer_class(message, many=True)
        return Response({'status': 'success', 'message': 'successfully receive data.','data':serializer.data},status=status.HTTP_200_OK)
    
    # def post(self, request):
    #     data = request.data
    #     current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
    #     iu_id = get_iuobj(current_site)

    #     if not iu_id:
    #         return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)

    #     data['iu_id'] = iu_id.id

    #     receiver_id = data.get('receiver')
    #     event_id = data.get('event')

    #     if receiver_id:
    #         receiver_email = get_email(receiver_id)
    #         if receiver_email:
    #             data['email_id'] = receiver_email
    #         else:
    #             return Response({'status': 'error', 'message': 'Receiver email not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         return Response({'status': 'error', 'message': 'Receiver ID not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        
    #     if event_id:
    #         try:
    #             event = EventMaster.objects.get(id=event_id)
    #             data['role'] = event.role  
    #         except EventMaster.DoesNotExist:
    #             return Response({'status': 'error', 'message': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         return Response({'status': 'error', 'message': 'Event ID not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        
    #     if event_id:
    #         try:
    #             event = EventMaster.objects.get(id=event_id)
    #             template = TemplateMaster.objects.get(id=event.sms_templateid)

    #             formatted_message = template.content.format(data.get('notification_message', ''))

    #             data['notification_message'] = formatted_message

    #         except (EventMaster.DoesNotExist, TemplateMaster.DoesNotExist):
    #             return Response({'status': 'error', 'message': 'Event or Template not found.'}, status=status.HTTP_404_NOT_FOUND)

    #     serializer = self.serializer_class(data=data)

    #     if serializer.is_valid():
    #         serializer_data = serializer.save(created_by=request.user.id)
    #         return Response({'status': 'success', 'message': 'Notification created successfully.', 'data': serializer_data.id}, status=status.HTTP_201_CREATED)

    #     return Response({'status': 'error', 'message': 'Notification not created', "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            event = Notification.objects.get(id=id,iu_id=iu_id,is_active=True)
        except Notification.DoesNotExist:
            return Response({"error": "notification not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(event, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=request.user.id)
            return Response({'status': 'success', 'message': 'successfully update the data.','data':serializer.data},status=status.HTTP_200_OK)
        return Response({'status': 'error', 'message': 'data is not update.',"data":serializer.errors}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            event = Notification.objects.get(id=id,is_active=True,iu_id=iu_id)
            event.is_active=False
            event.save(modified_by=request.user.id)
            return Response({"status":"success","message":"deleted successfully"},status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'status': 'error', 'message': 'data is not delete.'}, status=status.HTTP_404_NOT_FOUND)
