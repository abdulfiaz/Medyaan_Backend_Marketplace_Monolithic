from rest_framework import serializers
from order.models import *
from users.serializers import *
import random
import string

class Categoryserializer(serializers.ModelSerializer):
    is_parent_category = serializers.SerializerMethodField()
    parent_category_id = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategoryMaster
        fields = ['id', 'name', 'description', 'is_parent_category','parent_category_id','image','created_by','iu_id','modified_by']

    def update(self, obj, validated_data):
        
        for attr, value in validated_data.items():
            if value:  
                setattr(obj, attr, value)
        obj.save()
        return obj

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def get_is_parent_category(self, obj): #fetch the category only
        return obj.is_parent_category()
    
    def is_sub_category(self): #fetch the subcategory only
        return ProductCategoryMaster.objects.filter(sub_categories=self).exists()
    
    def get_parent_category_id(self, obj):# Fetch the IDs of parent categories
        parent_categories = ProductCategoryMaster.objects.filter(sub_categories=obj)
        return [parent.id for parent in parent_categories] if parent_categories.exists() else None

    
class VariantMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model=VariantMaster
        fields=['id','category','name', 'description','iu_id','created_by','modified_by']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def update(self, obj, validated_data):
        for attr, value in validated_data.items():
            if value:  
                setattr(obj, attr, value)
        obj.save()
        return obj
    
   
 
 
class VariantOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model=VariantOption
        fields=['id','variation','name', 'description','iu_id','image','created_by','modified_by']
        
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def update(self, obj, validated_data):
        for attr, value in validated_data.items():
            if value:  
                setattr(obj, attr, value)
        obj.save()
        return obj
    
class ProductMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaster  
        fields ='__all__'

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def update(self, obj, validated_data):
        for attr, value in validated_data.items():
            if value:  
                setattr(obj, attr, value)
        obj.save()
        return obj
   
class ProductVariationSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = ProductVariation  
        fields = ['id',  'total_price', 'selling_price', 'stock', 'image','product', 'variation', 'iu_id', 'created_by','modified_by',"is_active"]
        
    def to_representation(self,instance):
        data=super().to_representation(instance)
        
        product_master_details= ProductMasterSerializer(instance.product).data
        data['product_master']={field:product_master_details[field] for field in ['id','name','body_content','description']}
    
        variation_details=VariantOptionSerializer(instance.variation).data
        data['variation_details']={field:variation_details[field] for field in['id','name', 'description']}
        return data
    
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(ProductVariationSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def update(self, obj, validated_data):
        for attr, value in validated_data.items():
            if value:  
                setattr(obj, attr, value)
        obj.save()
        return obj
    
    
    
    
class OrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['user', 'iu_id', 'total_price', 'created_by']

class OrderItemsSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItems
        fields = ['order', 'user', 'product', 'variation', 'seller', 'iu_id', 'quantity', 'price','order_status', 'delivered_location','created_by','created_at_timestamp']
    
    def get_created_by(self, obj):
        if obj.created_by:  # Check if created_by is not None
            try:
                user_profile = UserPersonalProfile.objects.get(user=obj.created_by)
                return f"{user_profile.firstname} {user_profile.lastname}"
            except UserPersonalProfile.DoesNotExist:
                return None
        return None
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(OrderItemsSerializer, self).__init__(*args, **kwargs)
 
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    
    def to_representation(self,instance):
        data=super().to_representation(instance)
        
        product_details= ProductVariationSerializer(instance.product).data
        data['product_details']={field:product_details[field] for field in ['id','total_price', 'selling_price', 'stock','product']}
        
        user_details=CustomUserSerializer(instance.user).data
        data['user_details']={field:user_details[field] for field in ["mobile_number","email"]}
        
        variation_details=VariantOptionSerializer(instance.variation).data
        data['variation_details']={field:variation_details[field] for field in['id','variation','name', 'description']}
        return data
       
class InvoiceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceModel
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(InvoiceModelSerializer, self).__init__(*args, **kwargs)
 
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
       
                    
    
    def generate_invoice_number(self):
        while True:
            letters_part = ''.join(random.choice(string.ascii_uppercase) for _ in range(8))            
            numbers_part = ''.join(random.choice(string.digits) for _ in range(8))
            invoice_number = letters_part + numbers_part
            
            if not InvoiceModel.objects.filter(invoice_number=invoice_number).exists():
                return invoice_number

    def create(self, validated_data):
        validated_data['invoice_number'] = self.generate_invoice_number()
        return super().create(validated_data)    
   
# class InvoiceItemsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InvoiceItems
#         fields = '__all__'
    
#     def __init__(self, *args, **kwargs):
#         fields = kwargs.pop('fields', None)
#         super(InvoiceItemsSerializer, self).__init__(*args, **kwargs)
 
#         if fields is not None:
#             allowed = set(fields)
#             existing = set(self.fields)
#             for field_name in existing - allowed:
#                 self.fields.pop(field_name)
                
#     def to_representation(self,instance):
#         data=super().to_representation(instance)
        
#         product_details= ProductVariationSerializer(instance.product).data
#         data['product_details']={field:product_details[field] for field in ['id','total_price', 'selling_price', 'stock','product']}
        
#         invoice_details= InvoiceModelSerializer(instance.invoice).data
#         data['invoice_details']={field:invoice_details[field] for field in ['id','user', 'invoice_number', 'order_detail','total_amount','tax_amount','total_discount_percentage','total_discount_amount','overall_total']}
        
#         return data
    
class InvoiceItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItems
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(InvoiceItemsSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        product_variation_details = ProductVariationSerializer(instance.product).data
        product_master = ProductMaster.objects.get(pk=product_variation_details['product'])
        product_master_details = {
            'id': product_master.id,
            'name': product_master.name,
            'body_content': product_master.body_content,
            'description': product_master.description
        }
        
        data['product_details'] = {
            'id': product_variation_details['id'],
            'total_price': product_variation_details['total_price'],
            'selling_price': product_variation_details['selling_price'],
            'stock': product_variation_details['stock'],
            'product': product_master_details  
        }

        invoice_details = InvoiceModelSerializer(instance.invoice).data
        data['invoice_details'] = {
            field: invoice_details[field] 
            for field in ['id', 'user', 'invoice_number', 'order_detail', 'total_amount', 'tax_amount', 
                          'total_discount_percentage', 'total_discount_amount', 'overall_total']
        }
        
        return data

    
class PaymentTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypeMaster
        fields = '__all__'
        
class OrderTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTypeMaster
        fields = '__all__'
    
class PaymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetails
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(PaymentDetailsSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    def to_representation(self,instance):
        data=super().to_representation(instance)
        
        ordertype_details=OrderTypeMasterSerializer (instance.ordertype).data
        data['order_type']={field:ordertype_details[field] for field in ['id','name','description']}

        return data
        
class PaymentReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReference
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(PaymentReferenceSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
                
    def to_representation(self,instance):
        data=super().to_representation(instance)
        
        paymenttype_details=PaymentTypeMasterSerializer(instance.payment_type).data
        data['payment_type']={field:paymenttype_details[field] for field in ['id','name','description']}

        return data

class GetPaymentTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypeMaster
        fields = ['id','name','description']

class WishlistItemSerializers(serializers.ModelSerializer):
    
    class Meta:
        model=WishlistItem
        fields='__all__'
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(WishlistItemSerializers, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        Product_data = ProductMasterSerializer(instance.Product).data
        data['product_details'] = {field: Product_data[field] for field in ['id', 'name', 'body_content', 'description', 'image']}
        
        product_variant_data = ProductVariationSerializer(instance.product_variant).data
        data['product_variant'] = {field: product_variant_data[field] for field in ['id', 'selling_price', 'total_price', 'stock', 'image']}
        
        variation_data = product_variant_data.get('variation')
        print(variation_data)
        if variation_data:
            data['variation'] = {field: variation_data[field] for field in ['id', 'name', 'description', 'image']}
        
        return data
        
    

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields=['id','quantity','Product','product_variant','User','iu_id','is_removed','is_active','created_by','modified_by','iu_id']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(CartItemSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def validate_quantity(self,value):
        product_variation_id=self.initial_data.get('product_variant')
        cart_id=self.initial_data.get('cart_id')
        if not product_variation_id:
            cart_item=CartItem.objects.get(id=cart_id)
            product_variation_id=cart_item.product_variant.id
        product_quantity=ProductVariation.objects.get(id=product_variation_id,is_active=True)
        if value > product_quantity.stock:
            raise serializers.ValidationError("product does not have enough stock")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        Product_data = ProductMasterSerializer(instance.Product).data
        data['product_details'] = {field: Product_data[field] for field in ['id', 'name', 'body_content', 'description', 'image']}
        
        product_variant_data = ProductVariationSerializer(instance.product_variant).data
        data['product_variant'] = {field: product_variant_data[field] for field in ['id', 'selling_price', 'total_price', 'stock', 'image']}
        
        variation_data = product_variant_data.get('variation')
        if variation_data:
            data['variation'] = {field: variation_data[field] for field in ['id', 'name', 'description', 'image']}
        
        return data

# class FeedbackSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=FeedbackDetails
#         fields='__all__'
        
#     def __init__(self, *args, **kwargs):
#         fields = kwargs.pop('fields', None)
#         super(FeedbackSerializer, self).__init__(*args, **kwargs)

#         if fields is not None:
#             allowed = set(fields)
#             existing = set(self.fields)
#             for field_name in existing - allowed:
#                 self.fields.pop(field_name)
    
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
        
#         product_variant_data = ProductVariationSerializer(instance.product).data
#         data['product_variant'] = {field: product_variant_data[field] for field in ['id', 'selling_price', 'total_price', 'stock', 'image']}


class FeedbackSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackDetails
        fields='__all__'

    def get_likes(self, obj):
        return obj.likes.count()

    def get_dislikes(self, obj):
        return obj.dislikes.count()
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(FeedbackSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     product = instance.product
    #     if product:
    #         product_variant_data = ProductVariationSerializer(product).data
    #         data['product_variant'] = {
    #             field: product_variant_data.get(field)
    #             for field in ['id', 'selling_price', 'total_price', 'stock', 'image']
    #         }
        
    #     else:
    #         data['product_variant'] = None

    #     return data
