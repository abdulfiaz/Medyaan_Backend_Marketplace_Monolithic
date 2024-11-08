from django.shortcuts import render
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction
from.models import SellerApplicationDetails,SellerProfile
from .serializers import SellerApplicationDetailsSerializer,SellerProfileSerializer
from adminapp.iudetail import *
from adminapp.models import IUJsonMaster
from adminapp.utils import overallnotification
from users.auth import *
from users.models import CustomUser,RoleMapping,RoleMaster
from notification.models import EventMaster,TemplateMaster


class SellerApplicationDetailsAPI(APIView):
    serializer_class=SellerApplicationDetailsSerializer
    
    def get(self, request, id=None):
        roles = get_user_roles(request)
        application_status=request.data.get('application_status')

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if roles == "seller":
            try:
                seller_application = SellerApplicationDetails.objects.get(user=request.user, is_active=True)
                serializer = self.serializer_class(seller_application)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except SellerApplicationDetails.DoesNotExist:
                return Response({"status": "error", "message": "Seller details not found"}, status=status.HTTP_404_NOT_FOUND)

        elif roles == "manager":
            if application_status=='pending':   
                if id:
                
                    try:
                        seller_application = SellerApplicationDetails.objects.get(id=id, is_active=True,application_status='pending')
                        serializer = self.serializer_class(seller_application)
                    except SellerApplicationDetails.DoesNotExist:
                        return Response({"status": "error", "message": "Seller application not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    pending_applications = SellerApplicationDetails.objects.filter(is_active=True,application_status='pending')
                    serializer = self.serializer_class(pending_applications, many=True)
                    
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            
            elif application_status=='approved':
                if id:
                
                    try:
                        seller_application = SellerApplicationDetails.objects.get(id=id, is_active=True,application_status='approved')
                        serializer = self.serializer_class(seller_application)
                    except SellerApplicationDetails.DoesNotExist:
                        return Response({"status": "error", "message": "Seller application not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    pending_applications = SellerApplicationDetails.objects.filter(is_active=True,application_status='approved')
                    serializer = self.serializer_class(pending_applications, many=True)
                    
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                pending_applications = SellerApplicationDetails.objects.filter(is_active=True)
                serializer = self.serializer_class(pending_applications, many=True)                 
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)

        
    def post(self, request):
        roles = get_user_roles(request)
        if roles != "consumer":
            return Response({"status": "error", "message": "Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        data['user'] = request.user.id

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        if not iu_id:
            return Response({'status': 'failure', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)

        data['iu_id'] = iu_id.id

        try:
            iujsonmaster_data = IUJsonMaster.objects.get(iu_id_id=iu_id.id,document_name='answer_json',document_type='seller_registration',channel_name='ORDER')
        except IUJsonMaster.DoesNotExist:
            return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        answer_data = iujsonmaster_data.details

        if not answer_data:
            return Response({'status': 'error', 'message': 'No answer_json found in details'}, status=status.HTTP_400_BAD_REQUEST)

        errors = {}
        validated_data = {}

        for key, fielddata in answer_data.items():
            fieldname = key 
            submitted_value = request.data.get(fieldname)  
            if fielddata.get('mandatory') and not submitted_value:
                errors[fieldname] = f"{fielddata.get('lablename', fieldname)} is required"

            validated_data[fieldname] = submitted_value
        created_by=request.user.id

        if errors:
            return Response({'status': 'error', 'message': errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer_data=serializer.save(created_by=request.user.id, details=validated_data)
        
        try:
            template = TemplateMaster.objects.get(template_name="seller_application_submitted")
        except TemplateMaster.DoesNotExist:
            return Response({"status": "error", "message": "Template not found"}, status=status.HTTP_400_BAD_REQUEST)
        manager_role = RoleMaster.objects.filter(name='manager').first()
        if not manager_role:
            return Response({"status": "error", "message": "Manager role not found"}, status=status.HTTP_400_BAD_REQUEST)
        event, created = EventMaster.objects.get_or_create(
            name=template.template_name,
            iu_id=iu_id,
            sms_templateid=template.id,
            defaults={'role': manager_role, 'created_by': request.user.id}
        )
        event_id=event.id
        event.email=True
        event.save()

        notification_message = template.content.format(serializer_data.id,)
        manager_ids = RoleMapping.objects.filter(role=manager_role).values_list('user_id', flat=True)
        sender_id = request.user.id
        for manager_id in manager_ids:
            notification = overallnotification(
                sender_id=sender_id,
                receiver_id=manager_id,
                event=event_id, 
                subject='New seller application submitted',
                message=f"A new seller application has been created.",
                notification_message=notification_message,
                iu_id=iu_id.id,
                request_user=request.user.id
            )
        return Response({"status": "success", "message": "Application created successfully"}, status=status.HTTP_201_CREATED)


    def put(self, request, id=None):
        user_role = get_user_roles(request)
        if user_role != "seller":
            return Response({"status": "error", "message": "Unauthorized user"}, status=status.HTTP_404_NOT_FOUND)
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            application = SellerApplicationDetails.objects.get(id=id, is_active=True,iu_id=iu_id)
        except SellerApplicationDetails.DoesNotExist:
            return Response({"status": "error", "message": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
            
        updated_data = request.data        
        if "business_name" in updated_data:
            return Response({"status": "error", "message": "You cannot update the business name."}, status=status.HTTP_403_FORBIDDEN)
        
        non_empty_data = {key: value for key, value in updated_data.items() if value not in ["", None]}

        if not non_empty_data:
            return Response({"status": "error", "message": "field is empty."}, status=status.HTTP_403_FORBIDDEN)
        serializer = SellerApplicationDetailsSerializer(application, data=non_empty_data, partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=request.user.id)
            return Response({"status": "success", "message": "Application updated successfully."}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request,id=None):
        roles=get_user_roles(request)
        if roles !="seller":
            return Response({ "status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        iujsonmaster=SellerApplicationDetails.objects.get(id=id,is_active=True,iu_id=iu_id)
        if iujsonmaster:            
            iujsonmaster.is_active = False
            iujsonmaster.save()
            return Response({"status": "success", "message": "IUJson master deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","message":"data  is not delete"},status=status.HTTP_400_BAD_REQUEST)
        

       
class ManagerApprovalView(APIView):
    serializer_class=SellerApplicationDetailsSerializer
    def get(self, request, id=None):
        roles = get_user_roles(request)
        if roles != "manager":
            return Response({"status": "error", "message": "Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        if not iu_id:
            return Response({'status': 'failure', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)

        response_data = []
        
        try:
            
            if id:
                seller_application = SellerApplicationDetails.objects.get(id=id, is_active=True, iu_id=iu_id)
                formatted_data = self.format_for_seller_application(seller_application)
                if formatted_data:
                    response_data.append(formatted_data)
                else:
                    return Response({"status": "error", "message": "No pending details"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                seller_applications = SellerApplicationDetails.objects.filter(is_active=True)
                for seller_application in seller_applications:
                    formatted_data = self.format_for_seller_application(seller_application)
                    if formatted_data:
                        response_data.append(formatted_data)

                if not response_data:
                    return Response({"status": "error", "message": "No pending details"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": "success", "message": "Successfully received data", "data": response_data}, status=status.HTTP_200_OK)

        except SellerApplicationDetails.DoesNotExist:
            return Response({"status": "error", "message": "Seller application not found"}, status=status.HTTP_404_NOT_FOUND)
        except IUJsonMaster.DoesNotExist:
            return Response({"status": "error", "message": "IUJsonMaster entry not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def format_for_seller_application(self, seller_application):
        serializer = self.serializer_class(seller_application)
        try:
            question_format = IUJsonMaster.objects.get(iu_id_id=seller_application.iu_id.id, document_name='question_json')
            formatted_data = {
                "id": serializer.data['id'],
                "user": serializer.data['user'],
                "application_details": serializer.data['application_status'],
                "details": {"list": {}}
            }

            if formatted_data['application_details'] == 'pending':
                questions = question_format.details.get('list', {})
                for key, question in questions.items():
                    field_name = question.get("fieldname")
                    formatted_data["details"]["list"][key] = {
                        "value": seller_application.details.get(field_name, ""),
                        "comment": "",
                        "sequence": question.get("sequence"),
                        "fieldname": field_name,
                        "fieldtype": question.get("fieldtype"),
                        "lablename": question.get("lablename"),
                        "mandatory": question.get("mandatory"),
                        "validation": question.get("validation"),
                        "fieldstatus": question.get("fieldstatus"),
                    }
                return formatted_data
            else:
                return None
        except IUJsonMaster.DoesNotExist:
            return None

    def approve_application(self, application, request,role):
        seller_data = application.details
        business_name = seller_data.get("business_name", "")

        if not business_name:
            return Response({"status": "error", "message": {"business_name": ["Business name cannot be empty."]}}, status=status.HTTP_400_BAD_REQUEST)
        profile_data = {
            "user": application.user.id,
            "seller_application_id": application.id,
            "bussiness_name": business_name,
            "address": seller_data.get("address", ""),
            "email": seller_data.get("email", ""),
            "mobile_number": seller_data.get("mobilenumber", ""),
            "gst_number": seller_data.get("gst_number", ""),
            "pan_number": seller_data.get("pan_number", ""),
            "account_number": seller_data.get("account_number", ""),
            "ifsc_number": seller_data.get("ifsc_number", ""),
            "return_amount": seller_data.get("return_amount", 0.0),
            "iu_id": application.iu_id.id
        }
  
        profile_serializer = SellerProfileSerializer(data=profile_data)
        if profile_serializer.is_valid():
            profile_serializer.created_by=application.user.id
            profile_serializer.save()
            application.application_status = "approved"
            application.modified_by=request.user.id
            application.save()
            try:
                template = TemplateMaster.objects.get(template_name="manager_approval_seller")
            except TemplateMaster.DoesNotExist:
                return Response({"status": "error", "message": "Template not found"}, status=status.HTTP_400_BAD_REQUEST)

            event, created = EventMaster.objects.get_or_create(
                name=template.template_name,
                iu_id=application.iu_id,
                sms_templateid=template.id,

                defaults={'role': role.role.name, 'created_by': request.user.id}
            )
            event_id = event.id
            event.email=True
            event.save()

            notification_message = template.content.format(application.id, request.user.id)
            sender_id = request.user.id
            receiver_id=application.user.id
            notification = overallnotification(
                sender_id=sender_id,
                receiver_id=receiver_id,
                event=event_id, 
                subject='manager approval seller ',
                message=f"manager is approved to be a seller",
                notification_message=notification_message,
                iu_id=application.iu_id.id,
                request_user=request.user.id
            )
            return Response({"status": "success", "message": "Application approved and profile created"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "message": profile_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def reject_application(self, application, request):
        application.application_status = "rejected"
        application.is_rejected=True
        application.reason = request.data.get("reason", "")
        application.modified_by=request.user.id
        application.save()
        try:
                template = TemplateMaster.objects.get(template_name="manager_rejected_seller")
        except TemplateMaster.DoesNotExist:
            return Response({"status": "error", "message": "Template not found"}, status=status.HTTP_400_BAD_REQUEST)

        event, created = EventMaster.objects.get_or_create(
            name=template.template_name,
            iu_id=application.iu_id,
            sms_templateid=template.id,
            defaults={'created_by': request.user.id}
        )
        event_id = event.id
        event.email=True
        event.save()

        notification_message = template.content.format(application.id, request.user.id)
        sender_id = request.user.id
        receiver_id=application.user.id
        notification = overallnotification(
            sender_id=sender_id,
            receiver_id=receiver_id,
            event=event_id, 
            subject='manager reject seller ',
            message=application.reason,
            notification_message=notification_message,
            iu_id=application.iu_id.id,
            request_user=request.user.id
        )
        return Response({"status": "success", "message": "Application rejected"}, status=status.HTTP_200_OK)

    def put(self, request, id=None):       
        user_role = get_user_roles(request)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        if not iu_id:
            return Response({'status': 'failure', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
              
        try:
            application = SellerApplicationDetails.objects.get(id=id, is_active=True,iu_id=iu_id)
        except SellerApplicationDetails.DoesNotExist:
            return Response({"status": "error", "message": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
        if user_role != "manager":
            return Response({"status": "error", "message": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)   
        application_status = request.data.get("application_status")

        if application_status == "approved":
            user=CustomUser.objects.get(id=application.user.id)
            user.is_approval=True
            user.approved_by=request.user.id
            user.modified_by=request.user.id
            user.save()
            try:
                seller_role = RoleMaster.objects.get(name="seller")
            except RoleMaster.DoesNotExist:
                return Response({"status":"error","message":"not found"},status=status.HTTP_400_BAD_REQUEST)
            role=RoleMapping.objects.create(user=user,role=seller_role,iu_id=iu_id)
            return self.approve_application(application, request,role)
        elif application_status == "rejected":
            return self.reject_application(application, request)
        else: 
            return Response({"status": "error", "message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    

    