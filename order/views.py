from decimal import Decimal
from django.conf import settings
from adminapp.iudetail import get_iuobj
from users.auth import get_user_roles
from django.shortcuts import get_object_or_404
from django.db import transaction
from order.serializers import *
from users.models import *
from order.models import *
from notification.models import *
from adminapp.utils import *
from adminapp.models import *
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from order.utils import *
from django.utils import timezone
from sdd_marketplace import settings
import boto3
from botocore.config import Config
from django.conf import settings
from adminapp.iudetail import get_iuobj
from users.auth import get_user_roles
from django.shortcuts import get_object_or_404
from django.db import transaction
from order.serializers import *
from users.models import *
from order.models import *
from notification.models import *
from adminapp.utils import *
from adminapp.models import *
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.shortcuts import render
from django.template.loader import render_to_string
from order.utils import *


class CategoryMasterAPI(APIView):
    serializer_class = Categoryserializer

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

   
    def get(self, request):
        try:
            role = get_user_roles(request)
            if role != 'manager':
                return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
            
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
            iu_id = get_iuobj(current_site)
            data = request.data
            data['iu_id'] = iu_id.id

            id = request.query_params.get('id')
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
    
    def post(self,request):
           
        role = get_user_roles(request)
        if role != 'manager':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        data = request.data
        data['created_by'] = request.user.id
        data['iu_id'] = iu_id.id

        image = request.FILES.getlist('image', None)
        image_urls = []
        if  not image:
            return Response({"status":"error","message":'image not found'}, status=status.HTTP_400_BAD_REQUEST)
        for image_file in image:
            file_name = image_file.name
            image_url = upload_image_s3(image_file, file_name)
            if image_url:
                image_urls.append(image_url)
        data.setlist('image',image_urls)
        

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
            return Response({"status": "success", "message":"Category created successfully","data":{"id": main_category.id}}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.rollback()  
            return Response({"status": "error", "message": "An unexpected error occurred" +str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request):
        role = get_user_roles(request)
        if role != 'manager':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data['iu_id'] = iu_id.id
        data['modified_by'] = request.user.id
        id = data.get('category_id')
        if not id:
            return Response({"status": "error", "message": "category ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
        category = get_object_or_404(ProductCategoryMaster, id=id,is_active=True,iu_id=iu_id)

        if category.can_be_deleted:  
            return Response({"status":"error","message":"This category cannot be modified"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SubCategorySerializer(category, data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success","message":"Updated successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request):
       
        role = get_user_roles(request)
        if role != 'manager':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        id = data.get('category _id')
        
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

    def get(self,request):

        try:
            role = get_user_roles(request)
            if role != 'seller':
                return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
            
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
            iu_id = get_iuobj(current_site)

            data = request.data
            data['iu_id'] = iu_id.id
            seller_id=request.user.id
            id = request.query_params.get('id')

            fields=['id','category','name','description']

            variant_data=[]
            
            if id:
                Variant = get_object_or_404(VariantMaster, id=id, is_active=True,iu_id=iu_id,created_by=seller_id)
                variants= self.serializer_class(Variant,fields=fields)
                variant_data.append(variants.data) 

            else:
                Variant= VariantMaster.objects.filter(is_active=True,iu_id=iu_id,created_by=seller_id)
                variants= self.serializer_class(Variant, fields=fields, many=True)
                variant_data=variants.data


            return Response({"status": "success", "message":"Data fetched successfully","data":variant_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": "An unexpected error occurred" +str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

    def post(self,request):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
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
            return Response({"status":"success","message":"Variant Master created successfully","data":variantmaster_serializer.data['id']},status=status.HTTP_201_CREATED)
        return Response({"status":"error","message":variantmaster_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data=request.data
        data['iu_id']=iu_id.id
        id = data.get('variant_id')  
        if not id:
            return Response({"status": "error", "message": "Variant ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        
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
       

    def delete(self,request):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data=request.data
        data['iu_id']=iu_id.id
        id = data.get('variantmaster_id')
        
        variant= get_object_or_404(VariantMaster, id=id,iu_id=iu_id)

        if variant:
            variant.is_active=False
            variant.modified_by = request.user.id
            variant.save()
            return Response({"status":"success","message": "Deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":"variant not found"}, status=status.HTTP_404_NOT_FOUND)  
    

class VariantOptionAPI(APIView):
    serializer_class=VariantOptionSerializer

    def get(self,request):

        try:
            role = get_user_roles(request)
            if role != 'seller':
                return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
            
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
            iu_id = get_iuobj(current_site)

            data = request.data
            data['iu_id'] = iu_id.id
            id = request.query_params.get('id')
            seller_id=request.user.id

            fields=['id','variation','name','description']

            variant_choice=[]
            
            if id:
                Variantoption = get_object_or_404(VariantOption, id=id, is_active=True,iu_id=iu_id,created_by=seller_id)
                variants= self.serializer_class(Variantoption,fields=fields)
                variant_choice.append(variants.data) 

            else:
                Variantoption= VariantOption.objects.filter(is_active=True,iu_id=iu_id,created_by=seller_id)
                variants= self.serializer_class(Variantoption, fields=fields, many=True)
                variant_choice=variants.data


            return Response({"status": "success", "message":"Data fetched successfully","data":variant_choice}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": "An unexpected error occurred" +str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    def post(self,request):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data = request.data
        data['iu_id'] = iu_id.id

        variation_id = request.data.get('variation')
        image = request.FILES.getlist('image', None)
        
                                         
        variant_option= get_object_or_404(VariantMaster, id=variation_id, is_active=True,iu_id=iu_id)

      
       
        existing =VariantOption.objects.filter(variation_id=variation_id,name__iexact=data.get('name'),is_active=True,iu_id=iu_id).exists()
        if existing:
            return Response({"status":"error","message":"variant with this category already exists"}, status=status.HTTP_400_BAD_REQUEST)
        data['created_by'] = request.user.id
        data['variation'] = variant_option.id 
        
        image_urls = []
        if  not image:
            return Response({"status":"error","message":'image not found'}, status=status.HTTP_400_BAD_REQUEST)
        for image_file in image:
            file_name = image_file.name
            image_url = upload_image_s3(image_file, file_name)
            if image_url:
                image_urls.append(image_url)
        data.setlist('image',image_urls)
       
        variantoption_serializer = self.serializer_class(data=data)

        if variantoption_serializer.is_valid():
            variantoption_serializer.save()
            return Response({"status":"success","message":"VariantOption created successfully","data":variantoption_serializer.data['id']},status=status.HTTP_201_CREATED)
        return Response({"status":"error","message":variantoption_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data=request.data
        data['iu_id']=iu_id.id

        id = data.get('variant_option_id')  
        if not id:
            return Response({"status": "error", "message": "Variant ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        
        variant_options= get_object_or_404(VariantOption, id=id, is_active=True,iu_id=iu_id) 
        
        id=data.get('variation')
        variant_master=VariantMaster.objects.get(id=id,iu_id=iu_id)
        
        if VariantOption.objects.filter(name__iexact=data.get('name'),is_active=True,variation=variant_master,iu_id=iu_id).exists():
            return Response({"status":"error","message":"A variantoption  with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)

        data['modified_by']=request.user.id
        

        serializer=self.serializer_class(variant_options,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success","message":"Updated successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self,request):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data=request.data
        data['iu_id']=iu_id.id
        
        id = data.get('variant_option_id')
        variant= get_object_or_404(VariantOption, id=id,iu_id=iu_id)

        if variant:
            variant.is_active=False
            variant.modified_by = request.user.id
            variant.save()
            return Response({"status":"success","message": "Deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":"variantoption not found"}, status=status.HTTP_404_NOT_FOUND)


class ProductVariationAPI(APIView):
    serializer_class=ProductVariationSerializer

    def get(self,request):

        try:
            role = get_user_roles(request)
            if role != 'seller':
                return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
            
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
            iu_id = get_iuobj(current_site)

            data = request.data
            data['iu_id'] = iu_id.id

            seller_id=request.user.id

            id = request.query_params.get('id')

            fields=['id', 'product', 'variation', 'total_price', 'selling_price', 'stock','tax_rate','tax_amount']

            product_variant_data=[]
            
            if id:
                Product_variant = get_object_or_404(ProductVariation, id=id, is_active=True,iu_id=iu_id,created_by=seller_id)
                product= self.serializer_class(Product_variant,fields=fields)
                product_variant_data.append(product.data) 

            else:
                Product_variant= ProductVariation.objects.filter(is_active=True,iu_id=iu_id,created_by=seller_id)
                product= self.serializer_class(Product_variant,fields=fields, many=True)
                product_variant_data=product.data


            return Response({"status": "success", "message":"Data fetched successfully","data":product_variant_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": "An unexpected error occurred" +str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self,request):
        role = get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)

        product_id = request.data.get('product_id')
        image = request.FILES.getlist('image', None)
        product = get_object_or_404(ProductMaster, id=product_id, is_active=True)
        
        if product.seller.id != request.user.id:
            return Response({"status": "error", "message": "You are not authorized to add variants for this product"}, status=status.HTTP_403_FORBIDDEN)
        
        variantoption_id = request.data.get('option_id')
        variantoption = get_object_or_404(VariantOption, id=variantoption_id, is_active=True)

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_obj = get_iuobj(current_site)

        data = request.data
        data['iu_id'] = iu_obj.id
        data['created_by'] = request.user.id
        data['product'] = product.id
        data['variation'] = variantoption.id
            
        if ProductVariation.objects.filter(product=product.id, variation=variantoption.id, iu_id=iu_obj.id,is_active=True).exists():
            return Response({"status": "error", "message": "A product with the same variant already exists."}, status=status.HTTP_400_BAD_REQUEST)


        selling_price = float(data.get('selling_price'))
       
        tax_rate = data.get('tax_rate')
        tax_amount = data.get('tax_amount')

        
        if tax_rate and tax_amount:
            return Response({"status": "error", "message": "Provide only one: either 'tax_rate' or 'tax_amount', not both."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if tax_rate:
                tax_rate = float(tax_rate)
                tax_amount = round((tax_rate / 100) * float(selling_price), 5)
            elif tax_amount:
                tax_amount = float(tax_amount)
                tax_rate = round((tax_amount / float(selling_price)) * 100, 3)
            else:
                tax_rate = None
                tax_amount = None

        except ValueError:
            return Response({"status": "error", "message": "Invalid tax rate or tax amount value."}, status=status.HTTP_400_BAD_REQUEST)

        data['tax_amount'] = tax_amount
        data['tax_rate'] = tax_rate

        
        image_urls = []
        if  not image:
            return Response({"status":"error","message":'image not found'}, status=status.HTTP_400_BAD_REQUEST)
        for image_file in image:
            file_name = image_file.name
            image_url = upload_image_s3(image_file, file_name)
            if image_url:
                image_urls.append(image_url)
        data.setlist('image',image_urls)

        
        product_variation_serializer = self.serializer_class(data=data)
        if not product_variation_serializer.is_valid():
            return Response({"status": "error", "message": product_variation_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        data=product_variation_serializer.save()


        try:
            seller_profile = SellerProfile.objects.get(user=request.user.id)
        except SellerProfile.DoesNotExist:
            return Response({"status": "error", "message": "Seller profile not found"}, status=status.HTTP_404_NOT_FOUND)

      
        
        try:
            template = TemplateMaster.objects.get(template_name="product creation alert")
        except TemplateMaster.DoesNotExist:
            return Response({"status": "error", "message": "Notification template not found"}, status=status.HTTP_400_BAD_REQUEST)
       
        manager_role = RoleMaster.objects.filter(name='manager').first()
        if not manager_role:
            return Response({"status": "error", "message": "Manager role not found"}, status=status.HTTP_400_BAD_REQUEST)

        event = EventMaster.objects.get(
            name=template.template_name,  
            iu_id=iu_obj.id, 
            sms_templateid=template.id,
           
        ) 
       

        if event:
            product_name = data.product.name 
            business_name=seller_profile.bussiness_name 
            product_id = data.product.id
            variant_name = variantoption.name  
            product_variant_id = data.id  
            seller_id = request.user.id  
           
            manager_ids = RoleMapping.objects.filter(role=manager_role).values_list('user_id', flat=True)
           
            
            if manager_ids:
                sender_id = request.user.id
                for manager_id in manager_ids:
                    manager = UserPersonalProfile.objects.filter(user_id=manager_id).first()
                    manager_first_name = manager.firstname if manager else ()

                    content={
                        'business_name': business_name,
                        'seller_id':seller_id,
                        'product_id':product_id,
                        'product_name': product_name,
                        'product_variant_id': product_variant_id,
                        'variant_name':variant_name,
                        'manager_name': manager_first_name
                        }
                    
                    rendered_html_message = render_to_string('order/product_creation_notification.html',content)

                    message=template.content.format(business_name=business_name,
                    seller_id=seller_id,
                    product_id=product_id,
                    product_name=product_name,
                    product_variant_id=product_variant_id,
                    variant_name=variant_name,
                    manager_name=manager_first_name
                    )

                  
                    overallnotification(
                        sender_id=sender_id,
                        receiver_id=manager_id,
                        event=event.id,
                        subject='New Product was Created',
                        message="A new product has been created.",
                        notification_message=message,
                        email_content=rendered_html_message,
                        iu_id=iu_obj.id,
                        request_user=request.user.id
                    )
                   
            return Response({"status": "success", "message": "Product was created and notifications sent successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "message": "Event not found or conditions not met"}, status=status.HTTP_404_NOT_FOUND)

            
    def put(self, request):
        role = get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data = request.data
        data['iu_id'] = iu_id.id

        
        product_variant_id = request.data.get('product_variant_id')
        product_variant = get_object_or_404(ProductVariation, id=product_variant_id, iu_id=iu_id, is_active=True)
        data['modified_by'] = request.user.id

       
        tax_rate = data.get('tax_rate')
        tax_amount = data.get('tax_amount')
        selling_price = float(product_variant.selling_price)  

        
        if tax_rate is not None and tax_amount is not None:
            return Response({"status": "error", "message": "Provide only one: either 'tax_rate' or 'tax_amount'"},status=status.HTTP_400_BAD_REQUEST)

        try:
            if tax_rate is not None:
                tax_rate = float(tax_rate)
                data['tax_amount'] = round((tax_rate / 100) * selling_price, 5)

            elif tax_amount is not None:
                tax_amount = float(tax_amount)
                data['tax_rate'] = round((tax_amount / selling_price) * 100, 3)

        except ValueError:
            return Response(
                {"status": "error", "message": "Invalid value for 'tax_rate' or 'tax_amount'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(product_variant, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "Updated successfully"}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request):
        role=get_user_roles(request)
        if role != 'seller':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data=request.data
        data['iu_id']=iu_id.id
        
        id = data.get('product_variantion_id')
        Product_variation= get_object_or_404(ProductVariation,id=id,iu_id=iu_id)

        if  Product_variation:
            Product_variation.is_active=False
            Product_variation.modified_by = request.user.id
            Product_variation.save()
            return Response({"status":"success","message": "Deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"status":"error","message":"variantoption not found"}, status=status.HTTP_404_NOT_FOUND)


        
class ManagerdetailsAPI(APIView):
    serializer_class=ProductMasterSerializer

    def fetch_user_ids(self,role_name): 
        role_id = RoleMaster.objects.filter(name=role_name).values_list('id', flat=True).first()
        return set(RoleMapping.objects.filter(role_id=role_id).values_list('user_id', flat=True)) if role_id else set()

    def fetch_user_data(self,user_ids, include_seller_data=False):
        users = CustomUser.objects.filter(id__in=user_ids).values('id', 'email', 'mobile_number')
        first_names = {profile['user_id']: profile['firstname'] for profile in UserPersonalProfile.objects.filter(user_id__in=user_ids).values('user_id', 'firstname')}
        seller_data = {seller['user_id']: seller for seller in SellerProfile.objects.filter(user_id__in=user_ids).values('user_id','id', 'bussiness_name')} if include_seller_data else {}

        return [
            {**user, 'name': first_names.get(user['id']), **(seller_data.get(user['id'], {}))}
            for user in users
        ]

    def get_user_data(self,role=None): 
        if role:
            user_ids = self.fetch_user_ids(role) 
            if not user_ids:
                return Response({"status": "error", "message": "No users found"}, status=status.HTTP_400_BAD_REQUEST)
            data = self.fetch_user_data(user_ids, include_seller_data=(role == 'seller')) 
            return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)
        
        buyers =self.fetch_user_ids('consumer') - self.fetch_user_ids('seller') #no role provided
        return Response({"status": "success","buyers": self.fetch_user_data(buyers),"sellers":self. fetch_user_data(self.fetch_user_ids('seller'), include_seller_data=True)}, status=status.HTTP_200_OK)


    def get(self, request):
        try:
            role = get_user_roles(request)
            if role != 'manager':
                return Response({"status": "error", "message": "Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
            
            
            status_filter = request.query_params.get('status', None)
            if status_filter: 
                if status_filter in ['pending', 'approved', 'rejected']:
                    product = ProductMaster.objects.filter(product_status=status_filter, is_active=True)
                    product_list = self.serializer_class(product, fields=['id', 'seller', 'subcategory', 'name', 'product_status'], many=True).data
                    return Response({
                        "status": "success",
                        "message": f"Products fetched with status: {status_filter}",
                        "products": product_list
                    }, status=status.HTTP_200_OK)
                return Response({"status": "error", "message": "Invalid status provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            return self.get_user_data(request.query_params.get('role')) 

        except Exception as e:
            return Response({"status": "error", "message": "An unexpected error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                
    def put(self, request):
        role = get_user_roles(request)
        if role != 'manager':
            return Response({"status":"error","message":"Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)
        data = request.data
        data['iu_id'] = iu_id.id

        product_id = data.get('product_id')
        if not product_id:
            return Response({"status": "error", "message": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
       
        try:
            productmaster = get_object_or_404(ProductMaster, id=product_id, is_active=True, iu_id=iu_id)
        except:
            return Response({"status": "error", "message": "Product not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        product_variations = ProductVariation.objects.filter(product=product_id, is_active=True, iu_id=iu_id)
        if not product_variations.exists():
            return Response({"status": "error", "message": "Product cannot be approved as it has no associated variants"}, status=status.HTTP_400_BAD_REQUEST)
        
        product_status = data.get('status')

        if product_status == 'approved':
            data['product_status'] = product_status
            data['is_approved'] = True
            data['approved_by'] = request.user.id
            
        elif product_status == 'rejected':
            data['product_status'] = product_status
            data['modified_by'] = request.user.id
            
        else:
            return Response({"status": "error", "message": "Invalid status name"}, status=status.HTTP_400_BAD_REQUEST)
        

        serializer = self.serializer_class(productmaster, data=data, partial=True)
        if not serializer.is_valid(): 
            return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        data=serializer.save()
         
        try:
            template = TemplateMaster.objects.get(template_name="product approved/rejected alert")
        except TemplateMaster.DoesNotExist:
            return Response({"status": "error", "message": "Notification template not found"}, status=status.HTTP_400_BAD_REQUEST)
       
        product = get_object_or_404(ProductMaster, id=product_id)
        seller_id = product.seller.id
        
        
        try:
            template = TemplateMaster.objects.get(template_name="product approved/rejected alert")
        except TemplateMaster.DoesNotExist:
            return Response({"status": "error", "message": "Notification template not found"}, status=status.HTTP_400_BAD_REQUEST)

        event = EventMaster.objects.get(
            name=template.template_name,
            iu_id=iu_id.id,
            sms_templateid=template.id,
        )

        if event:
            product_name=product.name,
            product_status=data.product_status,

            mail_content={
                'product_name': product_name[0] if isinstance(product_name, (list, tuple)) and product_name else "Unknown Product",
                'product_status': product_status[0] if isinstance(product_status, (list, tuple)) and product_status else "Unknown Status"
                }
           
        
            rendered_html_message = render_to_string('order/product_status_notification.html',mail_content)
            message=template.content.format(product_name=mail_content['product_name'],product_status=mail_content['product_status'])

            sender_id = request.user.id

            overallnotification(
                sender_id=sender_id,
                receiver_id=seller_id,
                event=event.id,
                subject='Product Status detail',
                message="Notification for seller",
                notification_message=message,
                email_content=rendered_html_message,
                iu_id=iu_id.id,
                request_user=request.user.id
            )
           

            return Response({"status": "success", "message": "Product status updated and notification sent to the seller"}, status=status.HTTP_201_CREATED)
        else:
             return Response({"status": "error", "message": "Event not found or conditions not met"}, status=status.HTTP_404_NOT_FOUND)


class BuyerView(APIView):
    serializer_class=ProductVariationSerializer

    def get(self, request):
        try:
           
            role = get_user_roles(request)
            if role != 'consumer':
                return Response({"status": "error", "message": "Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)

            
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
            iu_id = get_iuobj(current_site)
            
            product_id = request.query_params.get('id')
            fields = ['id', 'variation', 'total_price', 'selling_price', 'stock', 'tax_rate', 'tax_amount']

            product_variant_data = []

            if product_id:
                
                product = ProductMaster.objects.filter(id=product_id, is_published=True, iu_id=iu_id, is_active=True, is_approved=True).first()

                if not product:
                    return Response({"status": "error", "message": "Product is not published"}, status=status.HTTP_400_BAD_REQUEST)

               
                product_variants = ProductVariation.objects.filter(product=product_id, is_active=True, iu_id=iu_id)
                if product_variants.exists():
                    
                    serializer = self.serializer_class(product_variants, fields=fields, many=True)
                    variant_data = serializer.data

                    product_variant_data.append({"product_id": product.id,"product_name": product.name,"variants": variant_data})

                    for variant in variant_data:
                       
                        variation_name = VariantOption.objects.filter(id=variant['variation']).first()
                        if variation_name:
                            variant["variation"] = variation_name.name  
                        else:
                            variant["variation"] = []          
                       
                else:
                   
                    product_variant_data.append({
                        "product_id": product.id,
                        "product_name": product.name,
                        "variants": []
                    })

            else:
                
                products = ProductMaster.objects.filter(is_published=True, iu_id=iu_id, is_active=True, is_approved=True)

                for product in products:
                    product_data = {
                        "product_id": product.id,
                        "product_name": product.name,
                        "variants": []
                    }

                    
                    product_variants = ProductVariation.objects.filter(product=product.id, is_active=True, iu_id=iu_id)
                    if product_variants.exists():
                        
                        serializer = self.serializer_class(product_variants, fields=fields, many=True)
                        for variant in serializer.data:
                           
                            variation_name = VariantOption.objects.filter(id=variant['variation']).first()
                            if variation_name:
                                variant["variation"] = variation_name.name  
                            else:
                                variant["variation"] = []
                           
                        product_data["variants"] = serializer.data
                    product_variant_data.append(product_data)
            return Response({"status": "success", "message": "Data fetched successfully", "data": product_variant_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": "An unexpected error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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



class ProductMasterView(APIView):
    serializer_class=ProductMasterSerializer
    def get(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="seller":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        if id:
            product=ProductMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
            serializer=self.serializer_class(product)
        else:
            product=ProductMaster.objects.filter(is_active=True)
            serializer = self.serializer_class(product, many=True)

        return Response({"status":"success","message":"successfully received data","data":serializer.data},status=status.HTTP_200_OK)

    def post(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="seller":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        data['seller']=request.user.id

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'failure', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        data['iu_id'] = iu_id.id

        product=self.serializer_class(data=data)
        if product.is_valid():
            serializer_iu=product.save(created_by=request.user.id)

            return Response({"status":"success","message":"Successfully created","data":serializer_iu.id},status=status.HTTP_201_CREATED)
        else:
            return Response({"status":"error","message":"product is not create","data":product.errors},status=status.HTTP_400_BAD_REQUEST)
            
    def put(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="seller":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        product=ProductMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
       
        serializer=self.serializer_class(product,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=request.user.id)
            return Response({"status":"success","message":"successfully update the data"},status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="seller":
            return Response({ "status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        product=ProductMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
        if product:            
            product.is_active = False
            product.save()
            return Response({"status": "success", "message": "Product deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","message":"data  is not delete"},status=status.HTTP_400_BAD_REQUEST)



              
class UploadImagesAPI(APIView):
    def post(self,request):
        try:
            data=request.data
            image = request.FILES.getlist('images', None)  
            image_urls = []
            if  not image: 
                return Response({"status":"error","message":'image not found'}, status=status.HTTP_400_BAD_REQUEST)       
            for image_file in image:
                file_name = image_file.name
                image_url = upload_image_s3(image_file, file_name)
                if image_url:
                  image_urls.append(image_url)
            return Response({"status": "success", "message":"images url created","data":image_urls}, status=status.HTTP_200_OK)
        except Exception as e:
            transaction.rollback()  
            return Response({"status": "error", "message": "An unexpected error occurred" +str(e)}, status=status.HTTP_400_BAD_REQUEST)




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



class ProductMasterView(APIView):
    serializer_class=ProductMasterSerializer
    def get(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="seller":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        if id:
            product=ProductMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
            serializer=self.serializer_class(product)
        else:
            product=ProductMaster.objects.filter(is_active=True)
            serializer = self.serializer_class(product, many=True)

        return Response({"status":"success","message":"successfully received data","data":serializer.data},status=status.HTTP_200_OK)

    def post(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="seller":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        data['seller']=request.user.id

        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'failure', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        data['iu_id'] = iu_id.id

        product=self.serializer_class(data=data)
        if product.is_valid():
            serializer_iu=product.save(created_by=request.user.id)

            return Response({"status":"success","message":"Successfully created","data":serializer_iu.id},status=status.HTTP_201_CREATED)
        else:
            return Response({"status":"error","message":"product is not create","data":product.errors},status=status.HTTP_400_BAD_REQUEST)
            
    def put(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="seller":
            return Response({"status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        product=ProductMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
       
        serializer=self.serializer_class(product,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=request.user.id)
            return Response({"status":"success","message":"successfully update the data"},status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id=None):
        roles = get_user_roles(request)
        if roles !="seller":
            return Response({ "status":"error","message":"Unauthorized user"},status=status.HTTP_401_UNAUTHORIZED)
        current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        iu_id = get_iuobj(current_site)

        if not iu_id:
            return Response({'status': 'error', 'message': 'IU domain not found.'}, status=status.HTTP_404_NOT_FOUND)
        product=ProductMaster.objects.get(id=id,is_active=True,iu_id=iu_id)
        if product:            
            product.is_active = False
            product.save()
            return Response({"status": "success", "message": "Product deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","message":"data  is not delete"},status=status.HTTP_400_BAD_REQUEST)
        
        
class OrderInvoiceAPI(APIView):
    def get(self, request):
        user= request.user
        print(user)
        try:
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST) 
            iu_id = get_iuobj(current_site)
            order_details = OrderDetails.objects.get(user=user,iu_id=iu_id ,is_active=True)
        except OrderDetails.DoesNotExist:
                return Response({"status":"error","message":"data not found"},status=status.HTTP_404_NOT_FOUND)
            
        try:
            order_items = OrderItems.objects.filter(order=order_details,iu_id=iu_id)     
            serializers = OrderItemsSerializer(order_items, many=True,fields=["delivered_location",'order_status'])
            
            return Response({"status": "success","message": "Data successfully retrieved", "data":serializers.data}, status=status.HTTP_200_OK)

        
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST) 
 
    def post(self, request):
        try:
            data = request.data
            users =request.user 
            current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST) 
            iu_id = get_iuobj(current_site)

            user = CustomUser.objects.get(id=users.id,iu_id=iu_id, is_active=True)

            transaction.set_autocommit(False)
            order_details_data = {
                'user': user.id,
                'iu_id': iu_id.id,
                'created_by': user.id,
            }
            order_details_serializer = OrderDetailsSerializer(data=order_details_data)
            if order_details_serializer.is_valid():
                order_details = order_details_serializer.save()
            else:
                return Response({"status": "error","message":order_details_serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            invoice_model_data={
                    'user': user.id,
                    'iu_id': iu_id.id,
                    'order_detail':order_details.id,
                    'created_by': user.id,
                    }
            invoice_model_serializer=InvoiceModelSerializer(data=invoice_model_data)
            
            if invoice_model_serializer.is_valid():
                invoice_model = invoice_model_serializer.save()
            else:
                return Response({"status": "error","message":invoice_model_serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            total_price = 0
            total=0 
            tax_amount = 0
            discount_amount = 0
            overall_total = 0
            for product in data['products']:
                product_detail = ProductVariation.objects.get(id=product['product_id'],iu_id=iu_id, is_active=True)
                
                if product_detail.stock < product['product_quantity']:
                    return Response({"status": "error", "message": f"Insufficient stock for product {product_detail.product.name}"},status=status.HTTP_400_BAD_REQUEST)

                product_detail.stock -= product['product_quantity']
                product_detail.save()
                
                variant_option = VariantOption.objects.get(id=product_detail.variation.id,iu_id=iu_id, is_active=True)
                seller = SellerProfile.objects.get(user=product_detail.product.seller,iu_id=iu_id, is_active=True)

                order_item_data = {
                    'order': order_details.id,
                    'user': user.id,
                    'product': product_detail.id,
                    'variation': variant_option.id,
                    'seller': seller.id,
                    'iu_id': iu_id.id,
                    'quantity': product['product_quantity'],
                    'price': product_detail.selling_price*product['product_quantity'],
                    'delivered_location': data['delivery_location'],
                    "created_by":user.id
                }
                order_item_serializer = OrderItemsSerializer(data=order_item_data)
                if order_item_serializer.is_valid():
                    order_item_serializer.save()
                    total_price +=Decimal(order_item_serializer.data['price'])
                else:
                    return Response({"status": "error","message":order_item_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
               
                proc_dis_amt = Decimal(product.get('discount_amount') or 0)
                proc_dis_per = Decimal(product.get('discount_percentage') or 0)

                if proc_dis_amt > 0 and product_detail.selling_price:
                    product_discount_percentage = (proc_dis_amt / Decimal(product_detail.selling_price)) * 100

                elif proc_dis_per > 0 and product_detail.selling_price:
                    product_discount_amount = (proc_dis_per / 100) * Decimal(product_detail.selling_price)
                    product_total_price = Decimal(product_detail.selling_price) - product_discount_amount
              

                try:
                    invoice_item_data={
                        'product': product_detail.id,
                        'invoice':invoice_model.id,
                        'quantity': product['product_quantity'],
                        'unit_price': product_detail.selling_price,
                        'iu_id': iu_id.id,
                        'tax_rate':product_detail.tax_rate,
                        'tax_amount':product_detail.tax_amount*product['product_quantity'] if product_detail.tax_amount else 0 ,
                        'discount_percentage':product_discount_percentage if  proc_dis_amt else proc_dis_per,
                        'discount_amount':product_discount_amount*product['product_quantity'] if  proc_dis_per else proc_dis_amt*product['product_quantity'],
                        "total":product_detail.selling_price*product['product_quantity'],
                        "created_by":user.id
                        }
                except Exception as e:
                    return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST) 
                   
                invoice_item_serializer = InvoiceItemsSerializer(data=invoice_item_data)
                if invoice_item_serializer.is_valid():
                    invoice_item_serializer.save()
                    tax_amount += Decimal(invoice_item_serializer.data['tax_amount']  or 0)
                    discount_amount +=Decimal(invoice_item_serializer.data['discount_amount']  or 0)
                    total=Decimal(invoice_item_serializer.data['total'])+Decimal(invoice_item_serializer.data['tax_amount']or 0)-Decimal(invoice_item_serializer.data['discount_amount'] or 0)
                    overall_total+=Decimal(total)
                else:
                    return Response({"status": "error","message":invoice_item_serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            
            total_discount_amount = data.get('total_discount_amount') or 0
            total_discount_percentage =data.get('total_discount_percentage') or 0
            overall_total_amount=0   
            if total_discount_percentage>0:
                total_discount_amount=overall_total*total_discount_percentage/ 100
                overall_total_amount=(overall_total-total_discount_amount)
        
            elif total_discount_amount>0:
                total_discount_percentage = (total_discount_amount /overall_total ) *100
                overall_total_amount = overall_total- total_discount_amount
            
            invoice_model.tax_amount=tax_amount
            invoice_model.total_discount_percentage=total_discount_percentage if total_discount_percentage>0 else None
            invoice_model.total_discount_amount=total_discount_amount if  total_discount_amount>0 else discount_amount
            invoice_model.total_amount=total_price
            invoice_model.overall_total=overall_total_amount if overall_total_amount>0 else overall_total
            order_details.total_price = overall_total_amount if overall_total_amount>0 else overall_total
            order_details.save()
            invoice_model.save()
            
            transaction.commit()
    
            return Response({"status": "success","message":"data created successfully",'data':invoice_model.id},status=status.HTTP_201_CREATED)    
        except ProductVariation.DoesNotExist or VariantOption.DoesNotExist or SellerProfile.DoesNotExist:
            return Response({"status": "error", "message": "Invalid data - product, variant, or seller not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.rollback()
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST) 
          
    def put(self, request):
        user = request.user
        order_item_id = request.data.get("order_id")
        data=request.data
        
        if user.role_name != 'buyer':
            return Response({"status": "failed", "message": "unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            order = OrderItems.objects.get(pk=order_item_id, order_status="pending", is_active=True)
            print(order.price)
        
            serializer = OrderItemsSerializer(order, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "message": "data updated successfully"}, status=status.HTTP_200_OK)

        except OrderItems.DoesNotExist:
            return Response({"status": "error", "message": "data not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
       
class PaymentDetailsAPIView(APIView):
    
    def post(self, request):
        domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)
        
        try:
            transaction.set_autocommit(False)
            data = request.data
            data['created_by'] = request.user.id
            data['iu_id'] = iu_id.id
            try:
                order_details = OrderDetails.objects.get(id=data['order_details_id'],iu_id=iu_id,is_active=True)
                data['order']=order_details.id
            except OrderDetails.DoesNotExist:
                return Response({"status":"error","message":"data not found"},status=status.HTTP_404_NOT_FOUND)
            try:  
                payment_type = PaymentTypeMaster.objects.get(id=data['payment_type_id'],iu_id=iu_id,is_active=True)
                data['payment_type']=payment_type.id
                if payment_type.name==CASH_ON_DELIVERY:
                    data['return_amount']=data['paid_ammount']-order_details.total_price
                  
                data['paid_amount']=order_details.total_price
                
            except PaymentTypeMaster.DoesNotExist:
                return Response({"status": "error", "message": "PaymentTypeMaster not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                OrderItems.objects.filter(order=order_details, iu_id=iu_id, is_active=True).update(order_status=ORDER_CONFIRMED)
                
                InvoiceModel.objects.filter(order_detail=order_details, iu_id=iu_id, is_active=True).update(status=ORDER_CONFIRMED)
                
            except OrderItems.DoesNotExist or InvoiceModel.DoesNotExist:
                return Response({"status": "error", "message": "data not found"}, status=status.HTTP_404_NOT_FOUND) 
               
            serializer = PaymentDetailsSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                transaction.commit()
                return Response({"status":"success","message":"paymenttype created successfully"},status=status.HTTP_201_CREATED)
            
            else:
                return Response({"status":"error","message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"status": "error", "messages": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductFetchAPI(APIView):

    def get(self,request):
        try:
            domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
            iu_id = get_iuobj(domain)
            product_name = request.query_params.get("name")
            product_type = request.query_params.get("type",None)
            id = request.query_params.get("id")
            min_price = request.query_params.get("min_price")
            max_price = request.query_params.get("max_price")
            
            products = None 
            if product_type is not None:
                if product_type == VARIANT and id:
                    variant = VariantOption.objects.filter(pk=id,iu_id=iu_id, is_active=True)
                    if variant:
                        products = ProductVariation.objects.filter(variation_id=id,iu_id=iu_id, is_active=True)

                elif product_type == PRODUCT and id:
                    products = ProductVariation.objects.filter(pk=id,iu_id=iu_id, is_active=True)

            elif product_name:
                print(product_name)
                products = ProductMaster.objects.filter(name__istartswith=product_name,iu_id=iu_id, is_active=True)
            if products is not None:
                if min_price:
                    products = products.filter(selling_price__gte=min_price)
                if max_price:
                    products = products.filter(selling_price__lte=max_price)

            if not products:
                return Response({"status": "success","message": "No products found","data": []})

            if product_type in [VARIANT, PRODUCT]:
                serializer = ProductVariationSerializer(products, many=True)
            else:
                serializer = ProductMasterSerializer(products, many=True)

            return Response({"status": "success","message": "Data successfully retrieved","data": serializer.data})

        except Exception as e:
            return Response({"status": "failed","message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WishListAPI(APIView):
    serializer_class=WishlistItemSerializers
    def get_object(self,wishlist_id,user,iu_id):
        try:
            wishlist=WishlistItem.objects.get(id=wishlist_id,User=user,is_active=True,is_removed=False,iu_id=iu_id)
            return wishlist
        except WishlistItem.DoesNotExist:
            return None

    def get(self,request):
        user=request.user
        role_name = get_user_roles(request)
        if not role_name in ['consumer']:
            return Response({"status":"error","message":"unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
        domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)
        wishlist=WishlistItem.objects.filter(User=user,is_active=True,is_removed=False,iu_id=iu_id)
        wishlist_count=wishlist.count()
        serializer_wishlist=self.serializer_class(wishlist,many=True,fields=['id','Product','product_variant'])
        return Response({"status":"success","message":"User wishlist","data":serializer_wishlist.data,"wishlist_count":wishlist_count},status=status.HTTP_200_OK)
    
    def post(self,request):
        user=request.user
        role_name = get_user_roles(request)
        # if not role_name in ['consumer']:
        #     return Response({"status":"error","message":"unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
        data=request.data
        if not data:
            return Response({"status":"error","message":"no data found"},status=status.HTTP_400_BAD_REQUEST)
        
        # current_site = request.META.get('HTTP_ORIGIN', settings.APPLICATION_HOST)
        domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)
        
        data['User']=user.id
        data['iu_id']=iu_id.id
        data['created_by']=user.id
        print(data)
        wishlist=self.serializer_class(data=data)
        if not wishlist.is_valid():
            return Response({"status":"error","message":wishlist.errors},status=status.HTTP_400_BAD_REQUEST)
        wishlist.save()
        return Response({"status":"Success","message":"Product Successfully Added to Wishlist"},status=status.HTTP_200_OK)
    
    def delete(self,request):
        user=request.user
        role_name = get_user_roles(request)
        if not role_name in ['consumer']:
            return Response({"status":"error","message":"unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
        wishlist_id=request.data.get('wishlist_id')
        domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)
        wishlist=self.get_object(wishlist_id,user.id,iu_id)
        if wishlist is None:
            return Response({"status":"error","message":"no wishlist is found"},status=status.HTTP_404_NOT_FOUND)
        wishlist.is_active=False
        wishlist.is_removed=True
        wishlist.modified_by=user.id
        wishlist.save()
        return Response({"status":"success","message":"product removed from wishlist"},status=status.HTTP_200_OK)
    
class CartItemAPI(APIView):
    serializer_class=CartItemSerializer
    def get_object(self,cart_id,user,iu_id):
        try:
            cartitem=CartItem.objects.get(id=cart_id,User=user,is_active=True,iu_id=iu_id,is_removed=False)
            return cartitem
        except CartItem.DoesNotExist:
            return None
        
    def get(self,request):
        user=request.user
        role_name = get_user_roles(request)
        if not role_name in ['consumer']:
            return Response({"status":"error","message":"unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
        domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)
        carts=CartItem.objects.filter(User=user,is_active=True,is_removed=False,iu_id=iu_id)
        carts_count=carts.count()
        cart_serialize=self.serializer_class(carts,many=True,fields=['id','quantity'])
        return Response({"status":"success","message":"User Carts","data":cart_serialize.data,"carts_count":carts_count},status=status.HTTP_200_OK)
    
    def post(self,request):
        user=request.user
        role_name = get_user_roles(request)
        if not role_name in ['consumer']:
            return Response({"status":"error","message":"unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
        data=request.data
        domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
        iu_id = get_iuobj(domain)

        data['iu_id']=iu_id.id
        data['created_by']=user.id
        data['User']=user.id
        carts=self.serializer_class(data=data)
        if not carts.is_valid():
            return Response({"status":"error","message":carts.errors},status=status.HTTP_400_BAD_REQUEST)
        carts.save()
        return Response({"status":"success","message":"item added to cart successfully"},status=status.HTTP_200_OK)
    
    def put(self,request):
        try:
            user=request.user
            role_name = get_user_roles(request)
            if not role_name in ['consumer']:
                return Response({"status":"error","message":"unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
            user_id=request.user.id
            cart_id=request.data.get('cart_id')
            if not cart_id:
                return Response({"status":"error","message":"cart_id required"},status=status.HTTP_400_BAD_REQUEST)
            domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
            iu_id = get_iuobj(domain)
            user_cart=self.get_object(cart_id,user,iu_id)
            if not user_cart:
                return Response({"status":"error","message":"cart does not exist"},status=status.HTTP_404_NOT_FOUND)
            data=request.data
            print(data)
            data['modified_by']=user_id
            carts=self.serializer_class(user_cart,data=data,partial=True)
            if not carts.is_valid():
                return Response({"status":"error","message":carts.errors},status=status.HTTP_400_BAD_REQUEST)
            carts.save()
            return Response({"status":"success","mesaage":"cart updated"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e))
    def delete(self,request):
        try:
            user=request.user
            if not user:
                return Response({"status":"error","message":"Token not found"},status=status.HTTP_400_BAD_REQUEST)
            role_name = get_user_roles(request)
            if not role_name in ['consumer']:
                return Response({"status":"error","message":"unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
            cart_id=request.data.get('cart_id')
            if not cart_id:
                return Response({"status":"error","message":"cart_id required"},status=status.HTTP_400_BAD_REQUEST)
            domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
            iu_id = get_iuobj(domain)
            user_cart=self.get_object(cart_id,user.id,iu_id)
            user_cart.is_removed=True
            user_cart.is_active=False
            user_cart.save()
            return Response({"status":"success","message":"cart removed successfully"},status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
                return Response({"status":"error","message":"cart does not exist"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"error","message":str(e)},status=status.HTTP_400_BAD_REQUEST)
        
class FeedbackAPI(APIView):
    serializerclass=FeedbackSerializer
    def get(self,request):
        if not request.user:
            return Response({"status":"error","message":"Token not found"},status=status.HTTP_400_BAD_REQUEST)
        try:
            domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
            iu_id = get_iuobj(domain)
            try:
                product_id=request.query_params.get('product_id')
                feedback=FeedbackDetails.objects.filter(is_active=True,iu_id=iu_id,product=product_id)
                feedbackserializer=self.serializerclass(feedback,many=True,fields=['id','product','comments','ratings','images','like_count','dislike_count'])
                return Response({"status":"Success","message":"feedback details","data":feedbackserializer.data},status=status.HTTP_200_OK)
            
            except FeedbackDetails.DoesNotExist:
                    return Response({"status":"error","message":"feedback id not found"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error","message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
    def post(self,request):
        role_name = get_user_roles(request)
        if not role_name in ['consumer']:
            return Response({"status":"error","message":"unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
        if not request.user:
            return Response({"status":"error","message":"Token not found"},status=status.HTTP_400_BAD_REQUEST)
        user=request.user
        data=request.data
        try:
            domain = request.META.get('HTTTP_ORIGIN',settings.APPLICATION_HOST)
            iu_id = get_iuobj(domain)
            try:
                data['user']=user.id
                data['iu_id']=iu_id.id
                data['created_by']=user.id
                order_items=OrderItems.objects.get(iu_id=iu_id,product=data['product'],order_status=ORDER_CONFIRMED,user=user)
                feedback=self.serializerclass(data=data)
                if not feedback.is_valid():
                    return Response({"status":"error","message":feedback.errors},status=status.HTTP_400_BAD_REQUEST)
                feedback.save()
                return Response({"status":"success","message":"feedback posted"},status=status.HTTP_200_OK)
            except OrderItems.DoesNotExist:
                    return Response({"status":"error","message":" Haven't purchased this product"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"error","message":str(e)},status=status.HTTP_400_BAD_REQUEST)
    
