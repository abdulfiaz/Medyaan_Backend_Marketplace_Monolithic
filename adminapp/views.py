from django.shortcuts import render
from adminapp.models import *
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction
from adminapp.rolename import *

class IUMasterAPI(APIView):

    def get(self, request):
        iu_id = request.query_params.get('id')
        rolename = getrolename(request)

        try:
            if rolename != 'ADMIN':
                return Response({"status": "error", "message": "Only ADMIN can have the access!"}, status=status.HTTP_403_FORBIDDEN)

            if iu_id:
                try:
                    iumaster_obj = IUMaster.objects.filter(id=iu_id, is_active=True)
                    if not iumaster_obj.exists():
                        return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)
                except IUMaster.DoesNotExist:
                    return Response({"status": "error", "message": "IU not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                iumaster_obj = IUMaster.objects.filter(is_active=True)

            data = []
            for iu_obj in iumaster_obj:
                data.append({
                    "id": iu_obj.id,
                    "name": iu_obj.name,
                    "domain": iu_obj.domain,
                    "contact_mobile_no": iu_obj.contact_mobile_no,
                    "logo": iu_obj.logo,
                    "address": iu_obj.address,
                    "city": iu_obj.city,
                    "state": iu_obj.state
                } )
                
            
            return Response({"status": "success", "message": "IUMaster list retrieved successfully", "data": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def post(self,request):
        data = request.data
        name = data.get('name')
        domain = data.get('domain')
        contact_mobile_no = data.get('contact_mobile_no','')
        logo = data.get('logo',{})
        address = data.get('address','')
        city = data.get('city','')
        state = data.get('state','')
        created_by = request.user.id 

        rolename = getrolename(request)

        try:
            if rolename != "ADMIN":
                return Response({"status": "error", "message": "Only ADMIN can have the access!"}, status=status.HTTP_400_BAD_REQUEST)


            transaction.set_autocommit(False)
            
            iumaster = IUMaster(
                name = name,
                domain = domain,
                contact_mobile_no = contact_mobile_no,
                logo = logo,
                address = address,
                city = city,
                state =state,
                created_by = created_by
            )
            iumaster.save()
            transaction.commit()
            
            return Response({"status":"success","message":"Details created successfully"},status = status.HTTP_201_CREATED)
                
        except Exception as e :
            transaction.rollback()
            return Response({"status":"error","message":str(e)},status = status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        data = request.data
        iu_id = data.get('id')
        name = data.get('name')
        domain = data.get('domain')
        contact_mobile_no = data.get('contact_mobile_no')
        logo = data.get('logo',{})
        address = data.get('address')
        city = data.get('city')
        state = data.get('state')
        modified_by = request.user.id

        rolename = getrolename(request)

        try:

            if rolename != "ADMIN":
                return Response({"status": "error", "message": "Only ADMIN can access this!"}, status=status.HTTP_403_FORBIDDEN)

            try:
                iumaster_obj = IUMaster.objects.get(id=iu_id, is_active=True)
            except IUMaster.DoesNotExist:
                transaction.rollback()
                return Response({"status": "error", "message": "IU not found"}, status=status.HTTP_404_NOT_FOUND)
            
            transaction.set_autocommit(False)
            iumaster_obj.name = name if name else iumaster_obj.name
            iumaster_obj.domain = domain if domain else iumaster_obj.domain
            iumaster_obj.contact_mobile_no = contact_mobile_no if contact_mobile_no else iumaster_obj.contact_mobile_no
            iumaster_obj.logo = logo if logo else iumaster_obj.logo
            iumaster_obj.address = address if address else iumaster_obj.address
            iumaster_obj.city = city if city else iumaster_obj.city
            iumaster_obj.state = state if state else iumaster_obj.state
            iumaster_obj.modified_by = modified_by  

            iumaster_obj.save()
            transaction.commit()

            return Response({"status": "success", "message": "Details updated successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.rollback()
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    
    def delete(self, request):
        iu_id = request.data.get('id')
        rolename = getrolename(request)

        try:

            if rolename != "ADMIN":
                return Response({"status": "error", "message": "Only ADMIN can access this!"}, status=status.HTTP_403_FORBIDDEN)
            
            try:
                iumaster_obj = IUMaster.objects.get(id=iu_id, is_active=True)
            except IUMaster.DoesNotExist:
                return Response({"status": "error", "message": "IUMaster not found"}, status=status.HTTP_404_NOT_FOUND)
            
            iumaster_obj.is_active = False  
            iumaster_obj.save()

            return Response({"status": "success", "message": "IU Master deleted successfully"}, status=status.HTTP_201_CREATED)
    
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
            


                
                
    




