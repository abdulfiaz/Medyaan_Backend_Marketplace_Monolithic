from django.shortcuts import render
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.conf import settings
from adminapp.iudetail import get_iuobj
from users.auth import get_user_roles
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db import transaction
from order.serializers import *
from users.models import *
from order.models import *
from rest_framework.views import APIView,status


class CategoryMasterAPI(APIView):
    serializer_class = Categoryserializer

    def post(self,request):
           
        role = get_user_roles(request)
        if role != 'manager':
            return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        data = request.data
        data['created_by'] = request.user.id
        data['iu_id'] = iu_id.id

        existing_category = ProductCategoryMaster.objects.filter(name__iexact=data.get('name'), is_active=True,iu_id=iu_id).exists()
        if existing_category:
            return Response({"status":"error","message":'Category with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

       
        transaction.set_autocommit(False)  
        try:
            
            main_category_serializer = self.serializer_class(data=data)
            if not main_category_serializer.is_valid():
                return Response({"status": "error", "message": main_category_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            main_category = main_category_serializer.save()

            subcategories_data = data.get('sub_categories', [])
            for subcategory_data in subcategories_data:
                subcategory_data['created_by'] = request.user.id
                subcategory_data['iu_id'] = iu_id.id

                existing_subcategory = ProductCategoryMaster.objects.filter(name__iexact=subcategory_data.get('name'), is_active=True,iu_id=iu_id).exists()

                if existing_subcategory:
                    return Response({"status":"error","message":'SubCategory with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
                subcategory_serializer = SubCategorySerializer(data=subcategory_data)
                if not subcategory_serializer.is_valid():
                    return Response({"status": "error", "message": subcategory_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                subcategory = subcategory_serializer.save()
                main_category.sub_categories.add(subcategory)
                
            transaction.commit()  
            return Response({"status": "success", "message":"Created successfull","data":{"id": main_category.id}}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.rollback()  
            return Response({"status": "error", "message": "An unexpected error occurred" +str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def get_category_hierarchy(self,category, visited_ids=None,fields=None):
        if visited_ids is None:
            visited_ids = set()

        if category.id in visited_ids:
            return None

        visited_ids.add(category.id)
        
        hierarchy = Categoryserializer(category).data
        if fields:
            hierarchy = {field: hierarchy[field] for field in fields if field in hierarchy}

        hierarchy['sub_categories'] = []

        for sub_category in category.sub_categories.filter(is_active=True).exclude(id__in=visited_ids):
            sub_hierarchy = self.get_category_hierarchy(sub_category, visited_ids,fields=fields)
            if sub_hierarchy:
                hierarchy['sub_categories'].append(sub_hierarchy)

        return hierarchy
    

   
    def get(self, request, id=None):
        try:
            role = get_user_roles(request)
            if role != 'manager':
                return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
            
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
            iu_id = get_iuobj(current_site)
            data = request.data
            data['iu_id'] = iu_id.id
            fields = ['id', 'name', 'description']  

            categories_data = []
            
            if id:
                category = get_object_or_404(ProductCategoryMaster,pk=id,is_active=True,iu_id=iu_id)
                category_hierarchy = self.get_category_hierarchy(category, fields=fields)
                categories_data.append(category_hierarchy)
            else:
                categories = ProductCategoryMaster.objects.filter(is_active=True,iu_id=iu_id)
                visited_ids = set()
                for category in categories:
                        category_hierarchy = self.get_category_hierarchy(category, visited_ids, fields=fields)
                        if category_hierarchy:
                           categories_data.append(category_hierarchy)

                                     
            return Response({"status": "success", "message":"Data fetched successfully","data":categories_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": "An unexpected error occurred" +str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, id):
        role = get_user_roles(request)
        if role != 'manager':
            return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data['iu_id'] = iu_id.id
        data['modified_by'] = request.user.id
    
        category = get_object_or_404(ProductCategoryMaster, id=id,is_active=True,iu_id=iu_id)

        if category.can_be_deleted:  
            return Response({"status":"error","message":"This category cannot be modified"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SubCategorySerializer(category, data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success","message":"Updated successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request,id):
       
        role = get_user_roles(request)
        if role != 'manager':
            return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data['iu_id'] = iu_id.id
        
        category = get_object_or_404(ProductCategoryMaster, id=id, is_active=True,iu_id=iu_id)
      
        if  category.can_be_deleted:
            return Response({"status":"error","message":"This category cannot be deleted"}, status=status.HTTP_403_FORBIDDEN)
        
        if category:
            category.is_active = False
            category.modified_by = request.user.id
            category.save()
            return Response({"status":"success","message":"Deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":"Category not found"}, status=status.HTTP_404_NOT_FOUND)  
    
    


class VariantMasterAPI(APIView):
    serializer_class=VariantMasterSerializer

    def post(self,request):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data = request.data
        data['iu_id'] = iu_id.id
         


        category_id = request.data.get('category_id')
        category= get_object_or_404(ProductCategoryMaster, id=category_id, is_active=True,iu_id=iu_id)

      
       
        existing =VariantMaster.objects.filter(category_id=category_id,name__iexact=data.get('name'),is_active=True,iu_id=iu_id).exists()
        if existing:
            return Response({"status":"error","message":"variant with this category already exists"}, status=status.HTTP_400_BAD_REQUEST)
        data['created_by'] = request.user.id
        data['category'] = category.id 

       
        variantmaster_serializer = self.serializer_class(data=data)

        if variantmaster_serializer.is_valid():
            variantmaster_serializer.save()
            return Response({"status":"success","message":"created successfully","data":variantmaster_serializer.data['id']},status=status.HTTP_201_CREATED)
        return Response({"status":"error","message":variantmaster_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self,request,id=None):

        try:
            role = get_user_roles(request)
            if role != 'seller':
                return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
            
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
            iu_id = get_iuobj(current_site)

            data = request.data
            data['iu_id'] = iu_id.id

            fields=['id','category','name','description']

            variant_data=[]
            
            if id:
                Variant = get_object_or_404(VariantMaster, id=id, is_active=True,iu_id=iu_id)
                variants= self.serializer_class(Variant,fields=fields)
                variant_data.append(variants.data) 

            else:
                Variant= VariantMaster.objects.filter(is_active=True,iu_id=iu_id)
                variants= self.serializer_class(Variant, fields=fields, many=True)
                variant_data=variants.data


            return Response({"status": "success", "message":"Data fetched successfully","data":variant_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": "An unexpected error occurred" +str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            

    def put(self, request, id):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data=request.data
        data['iu_id']=iu_id.id
        
        variant= get_object_or_404(VariantMaster, id=id, is_active=True,iu_id=iu_id) 
        data['modified_by']=request.user.id
      
        id=data.get('category')
        categorys=ProductCategoryMaster.objects.get(id=id,iu_id=iu_id)
       
        if VariantMaster.objects.filter(name__iexact=data.get('name'),is_active=True,category=categorys,iu_id=iu_id).exists():
            return Response({"status":"error","message":"A variant name with this category already exists"}, status=status.HTTP_400_BAD_REQUEST)


        serializer=self.serializer_class(variant,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success","message":"Updated successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
       


    def delete(self,request,id):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data=request.data
        data['iu_id']=iu_id.id
        
        variant= get_object_or_404(VariantMaster, id=id,iu_id=iu_id)

        if variant:
            variant.is_active=False
            variant.modified_by = request.user.id
            variant.save()
            return Response({"status":"success","message": "Deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":"variant not found"}, status=status.HTTP_404_NOT_FOUND)  
    
    



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


        



