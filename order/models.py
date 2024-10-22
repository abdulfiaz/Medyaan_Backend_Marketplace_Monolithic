from django.db import models
from adminapp.models import *
from seller.models import *
from django.contrib.postgres.fields import ArrayField

class ProductCategoryMaster(BaseModel):
    """To store the type of catgory """
    name=models.CharField(max_length=150,null=True,blank=True) #category name
    description=models.CharField(max_length=200,null=True,blank=True) #description about the category
    sub_categories = models.ManyToManyField('self', blank=True,null=True,related_name='sub_category')
    can_be_deleted=models.BooleanField(default=False)
    image=ArrayField(models.TextField(),blank=True,null=True)#image for each product
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)

    class Meta:
        db_table='product_category_master'
        ordering = ['created_at']
                    
                    

class ProductMaster(BaseModel):
    """product table for store the products details"""
    seller=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='seller_application')#seller reference for approval details
    subcategroy=models.ForeignKey(ProductCategoryMaster,on_delete=models.CASCADE,related_name='sub_category')#refer the subcategory
    name=models.CharField(max_length=200,null=True,blank=True)#product name
    body_content=models.TextField(null=True,blank=True)#details about the products
    description=models.TextField(max_length=300,null=True,blank=True)#intro or summary about the product
    is_approved=models.BooleanField(default=False)#product approval or not
    approved_by=models.IntegerField(blank=True,null=True)#check approved by
    product_status=models.CharField(default='pending')#initial status for the product
    image=ArrayField(models.TextField(),blank=True,null=True)#image for each product
    can_be_deleted=models.BooleanField(default=False)
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer the iu_id

    class Meta:
        db_table='product_master'
        ordering = ['created_at']


class VariantMaster(BaseModel):
    """store the type of varient for the products"""
    categroy=models.ForeignKey(ProductCategoryMaster,on_delete=models.CASCADE,related_name='category')#refer the categorymaster table
    name=models.CharField(max_length=200,null=True,blank=True)#varient type name
    description=models.CharField(max_length=200,null=True,blank=True)#type description
    can_be_deleted=models.BooleanField(default=False)
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer iu_id


    class Meta:
        db_table='varient_master'
        ordering = ['created_at']

class VariantOption(BaseModel):
    """To store the Specific varient for the  product"""
    variation=models.ForeignKey(VariantMaster,on_delete=models.CASCADE,related_name='variation')#refer the variation table for type
    name=models.CharField(max_length=200,null=True,blank=True)#name of the specific varient name
    description=models.CharField(max_length=200,null=True,blank=True)#specific varient description
    image=ArrayField(models.TextField(),blank=True,null=True)#image for each product
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer iu_id

    class Meta:
        db_table='varient_option'
        ordering = ['created_at']


class ProductVariation(BaseModel):
    """It will store the variations for the particular products"""
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE,related_name='product_master')#refer the productMaster
    variation=models.ForeignKey(VariantMaster,on_delete=models.CASCADE,related_name='variation')#variations for the particular product
    total_price=models.DecimalField(blank=True,null=True,decimal_places=3)#price of the product
    selling_price=models.DecimalField(blank=True,null=True,decimal_places=3)#selling price of the product
    stock=models.IntegerField(blank=True,null=True)#quantity of the product 
    image=ArrayField(models.TextField(),blank=True,null=True)#image for each product
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer the iu_id


    class Meta:
        db_table='product_variation'
        ordering = ['created_at']

"""fetch the whole order for specific user"""
class OrderDetails(models.Model):
    #store the user where user is in CustomUser
    user = models.ForeignKey(CustomUser, related_name='OrderDetails', on_delete=models.CASCADE)
    #fetch whole product and its price stored in it
    total_price=models.DecimalField(null=True,blank=True,default=0,decimal_places=3)
    #store the iu id from the IUMaster
    iu_id=models.ForeignKey(IUMaster,related_name='OrderDetails',on_delete=models.CASCADE)
   
   
    class Meta:
        db_table = 'order_details'
        ordering = ['created_at']

"""store the order items one by one from order details for specific user"""    
class OrderItems(BaseModel):
    #store the user where user is in CustomUser
    user = models.ForeignKey(CustomUser, related_name='OrderItems', on_delete=models.CASCADE)
    #fetch specific user order from the OrderDetails and store it 
    order=models.ForeignKey(OrderDetails, related_name='OrderItems',on_delete=models.CASCADE)
    #store the product where in order
    product=models.ForeignKey(ProductMaster,related_name='OrderItems',on_delete=models.CASCADE)
    #store the variant where in order
    variation=models.ForeignKey(VariantOption,related_name='OrderItems',on_delete=models.CASCADE)
    #fetch the seller from the product details
    seller=models.ForeignKey(SellerProfile,related_name='OrderItems',on_delete=models.CASCADE)
    #fetch the quantity from specific product 
    quantity=models.IntegerField(null=True,blank=True)
    #fetch the price from specific product 
    price=models.DecimalField(null=True,blank=True,default=0,decimal_places=3)
    #deliver status
    order_status=models.CharField(max_length=50,default="pending")
    #product delivered location
    delivered_location= models.TextField(null=True, blank=True)
    #product delerived time
    delivered_time=models.DateTimeField(null=True, blank=True)
    #if buyer return product then its changed to True
    is_returned=models.BooleanField(default=False)
    #then buyer enter its location for pickup the product
    return_pickup_location=models.CharField( max_length=250,null=True, blank=True)
    #buyer explain about the return product
    return_reason=models.TextField(blank=True,null=True)
    #product return process approved by whom is stored in it
    approved_by=models.IntegerField(blank=True, null=True)
    return_completed_time=models.DateTimeField(null=True, blank=True)
    #store the iu id from the IUMaster
    iu_id=models.ForeignKey(IUMaster,related_name='OrderItems',on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'order_items'
        ordering = ['created_at']
        
class PaymentTypeMaster(BaseModel):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=50,blank=True,null=True)
    #store the iu id from the IUMaster
    iu_id=models.ForeignKey(IUMaster,related_name='PaymentTypeMaster',on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'payment_type'
        ordering = ['created_at']
        
class PaymentDetails(BaseModel):
    #fetch specific user order from the OrderDetails and store it 
    order=models.ForeignKey(OrderDetails, related_name='PaymentDetails',on_delete=models.CASCADE)
    payment_type=models.ForeignKey(PaymentTypeMaster, related_name='PaymentDetails',on_delete=models.CASCADE)
    paid_amount=models.DecimalField(null=True,blank=True,default=0,decimal_places=3)
    payment_status=models.CharField(max_length=50,default="pending")
    return_amount=models.DecimalField(null=True,blank=True,default=0,decimal_places=3)
    
    



 
