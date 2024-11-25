from rest_framework.views import APIView,status
from rest_framework.response import Response
from.models import SellerApplicationDetails
from .serializers import SellerApplicationDetailsSerializer,SellerProfileSerializer
from adminapp.iudetail import *
from adminapp.models import IUJsonMaster
from adminapp.utils import overallnotification
from users.auth import *
from users.models import CustomUser,RoleMapping,RoleMaster,UserPersonalProfile
from notification.models import EventMaster,TemplateMaster
from django.template.loader import render_to_string

class SellerApplicationDetailsAPI(APIView):
    serializer_class=SellerApplicationDetailsSerializer
    
    def get(self, request):
        id = request.query_params.get('id')
        roles = get_user_roles(request)
        application_status=request.query_params.get('application_status')

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if roles == "seller":
            fields=['id','user','application_status','details','is_rejected','reason']
            try:
                seller_application = SellerApplicationDetails.objects.filter(user=request.user, is_active=True,iu_id=iu_id)
                serializer = self.serializer_class(seller_application,many=True,fields=fields)
                return Response({"status": "success","message":"seller details", "data": serializer.data}, status=status.HTTP_200_OK)
            except SellerApplicationDetails.DoesNotExist:
                return Response({"status": "error", "message": "Seller details not found"}, status=status.HTTP_404_NOT_FOUND)

        elif roles == "manager":
            fields=['id','user','application_status','details']
            if application_status:   
                if id:
                
                    try:
                        seller_application = SellerApplicationDetails.objects.get(id=id, is_active=True,application_status=application_status,iu_id=iu_id)
                        serializer = self.serializer_class(seller_application,fields=fields)
                    except SellerApplicationDetails.DoesNotExist:
                        return Response({"status": "error", "message": "Seller application not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    pending_applications = SellerApplicationDetails.objects.filter(is_active=True,application_status=application_status,iu_id=iu_id)
                    serializer = self.serializer_class(pending_applications, many=True,fields=fields)
                    
                return Response({"status": "success", "message":"seller pending details","data": serializer.data}, status=status.HTTP_200_OK)
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
        event= EventMaster.objects.get(name=template.template_name,iu_id=iu_id)
        
        event_id=event.id
        role=event.role
        subject="New Seller Application Submitted"
        message="A new seller application has been created. Please review the details below."
        notification_message = template.content.format(serializer_data.id)
        email_context = {
            "subject": subject,
            "message": message,
            "application_id": serializer_data.id,
            "details": notification_message, 
        }
        email_content = render_to_string('email/seller_notification_email.html', email_context)
        manager_ids = RoleMapping.objects.filter(role=manager_role).values_list('user_id', flat=True)
        managers = CustomUser.objects.filter(id__in=manager_ids)
        sender_id = request.user.id
        for manager in managers:
            notification = overallnotification(
                sender_id=sender_id,
                receiver_id=manager.id,
                event=event_id, 
                subject=subject,
                message=message,
                notification_message=notification_message,
                email_content=email_content,
                iu_id=iu_id.id,
                request_user=request.user.id,
                role=role,
                email_id=manager.email
    
            )
        return Response({"status": "success", "message": "Application created successfully","data":serializer_data.id}, status=status.HTTP_201_CREATED)

    def put(self, request):
        id=request.data.get('id')
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
        if "bussiness_name" in updated_data:
            return Response({"status": "error", "message": "You cannot update the bussiness name."}, status=status.HTTP_403_FORBIDDEN)
        
        non_empty_data = {key: value for key, value in updated_data.items() if value not in ["", None]}

        if not non_empty_data:
            return Response({"status": "error", "message": "field is empty."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(application, data=non_empty_data, partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=request.user.id)
            return Response({"status": "success", "message": "Application updated successfully."}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request):
        id=request.data.get('id')
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
    def format_for_seller_application(self, seller_application):
        serializer = self.serializer_class(seller_application)
        try:
            question_format = IUJsonMaster.objects.get(iu_id_id=seller_application.iu_id, document_name='question_json')
            answer_format=seller_application.details
            if serializer.data['application_status'] == 'pending':
                questions = question_format.details.get('list', {})
                
                formatted_details = {}
                for key, question in questions.items():
                    fieldname = question.get("fieldname")
                    value = answer_format.get(fieldname, "")
                    formatted_details[key] = {
                        "value": value,
                        "comment": "", 
                        "sequence": question.get("sequence", key),
                        "fieldname": fieldname,
                        "fieldtype": question.get("fieldtype", ""),
                        "lablename": question.get("lablename", ""),
                        "mandatory": question.get("mandatory", False),
                        "validation": question.get("validation", []),
                        "fieldstatus": question.get("fieldstatus", "Inactive"),
                    }
            
                return {
                    "id": serializer.data['id'],
                    "user": serializer.data['user'],
                    "application_details": serializer.data['application_status'],
                    "details":formatted_details,
                }

            return None
        except IUJsonMaster.DoesNotExist:
            return None

    def get(self, request):
        id = request.query_params.get('id')
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
                seller_applications = SellerApplicationDetails.objects.filter(is_active=True,iu_id=iu_id)
                for seller_application in seller_applications:
                    formatted_data = self.format_for_seller_application(seller_application)
                    if formatted_data:
                        response_data.append(formatted_data)

                if not response_data:
                    return Response({"status": "error", "message": "No pending details"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": "success", "message": "Successfully received data", "data": response_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def approve_application(self, application, request,role):
        seller_data = application.details
        bussiness_name = seller_data.get("bussiness_name", "")

        if not bussiness_name:
            return Response({"status": "error", "message": {"business_name": ["Bussiness name cannot be empty."]}}, status=status.HTTP_400_BAD_REQUEST)
        profile_data = {
            "user": application.user.id,
            "seller_application_id": application.id,
            "bussiness_name": bussiness_name,
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
            created_by=application.user.id
            profile_serializer.save(created_by=created_by)
            application.application_status = "approved"
            application.modified_by=request.user.id
            application.save()
            try:
                template = TemplateMaster.objects.get(template_name="manager_approval_seller")
            except TemplateMaster.DoesNotExist:
                return Response({"status": "error", "message": "Template not found"}, status=status.HTTP_400_BAD_REQUEST)

            event = EventMaster.objects.get(name=template.template_name,iu_id=application.iu_id)
            event_id = event.id
            role=event.role
            receiver_email=application.user.email
            user_profile = UserPersonalProfile.objects.get(user=application.user)
            user_name = f"{user_profile.firstname} {user_profile.lastname}"
            subject='Manager Approval Notification'
            message="Your application has been approved."
            notification = template.content.format(application.id, request.user.id)
            email_context = {
                "subject": subject,
                "message": message,
                "user_name": user_name,
                "application_id": application.id,
                "details":notification,
                "reason":None,
            }
            email_content = render_to_string('email/manager_approval_reject.html', email_context)

            sender_id = request.user.id
            receiver_id=application.user.id        
            notification = overallnotification(
            sender_id=sender_id,
            receiver_id=receiver_id,
            event=event_id,
            subject=subject,
            message=message,
            notification_message=notification,
            iu_id=application.iu_id.id,
            request_user=request.user.id,
            email_content=email_content,
            role=role,
            email_id=receiver_email
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

        event= EventMaster.objects.get(name=template.template_name,iu_id=application.iu_id)
        event_id = event.id
        role=event.role
        user_profile = UserPersonalProfile.objects.get(user=application.user)
        user_name = f"{user_profile.firstname} {user_profile.lastname}"
    
        subject='Manager Rejection Notification'
        message="Your application has been not approved."
        notification = template.content.format(application.id, request.user.id)
        email_context = {
            "subject": subject,
            "message": message,
            "user_name":user_name,
            "application_id": application.id,
            "details":notification,
            "reason":application.reason
        }
        email_content = render_to_string('email/manager_approval_reject.html', email_context)

        sender_id = request.user.id
        receiver_id=application.user.id  
        receiver_email=application.user.email     
        notification = overallnotification(
            sender_id=sender_id,
            receiver_id=receiver_id,
            event=event_id,
            subject=subject,
            message=message,
            notification_message=notification,
            iu_id=application.iu_id.id,
            request_user=request.user.id,
            email_content=email_content,
            email_id=receiver_email,
            role=role
        )
        return Response({"status": "success", "message": "Application rejected"}, status=status.HTTP_200_OK)

    def put(self, request):
        id=request.data.get('id')       
        user_role = get_user_roles(request)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
              
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
            return self.approve_application(application, request,role,user)
        elif application_status == "rejected":
            user=CustomUser.objects.get(id=application.user.id)
            return self.reject_application(application, request,user)
        else: 
            return Response({"status": "error", "message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    

    