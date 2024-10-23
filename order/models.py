from django.db import models
from adminapp.models import *
from seller.models import *
from django.contrib.postgres.fields import ArrayField
from users.models import CustomUser

class ProductCategoryMaster(BaseModel):
    """To store the type of catgory """
    name=models.CharField(max_length=150,null=True,blank=True) #category name
    description=models.CharField(max_length=300,null=True,blank=True) #description about the category
    sub_categories = models.ManyToManyField('self', blank=True,related_name='product_subcategory')
    can_be_deleted=models.BooleanField(default=False)
    image=ArrayField(models.TextField(),blank=True,null=True)#image for each product
    iu_id = models.ForeignKey(IUMaster, on_delete=models.CASCADE, related_name='product_category_master_iu')


    class Meta:
        db_table='product_category_master'
        ordering = ['created_at']
                    
                    

class ProductMaster(BaseModel):
    """product table for store the products details"""
    seller=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='product_master_seller')#seller reference for approval details
    subcategroy=models.ForeignKey(ProductCategoryMaster,on_delete=models.CASCADE,related_name='product_master_sub_category')#refer the subcategory
    name=models.CharField(max_length=200,null=True,blank=True)#product name
    body_content=models.TextField(null=True,blank=True)#details about the products
    description=models.TextField(max_length=300,null=True,blank=True)#intro or summary about the product
    is_approved=models.BooleanField(default=False)#product approval or not
    is_published=models.BooleanField(default=False)
    approved_by=models.IntegerField(blank=True,null=True)#check approved by
    product_status=models.CharField(max_length=20,default='pending')#initial status for the product
    image=ArrayField(models.TextField(),blank=True,null=True)#image for each product
    can_be_deleted=models.BooleanField(default=False)
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer the iu_id

    class Meta:
        db_table='product_master'
        ordering = ['created_at']


class VariantMaster(BaseModel):
    """store the type of varient for the products"""
    categroy=models.ForeignKey(ProductCategoryMaster,on_delete=models.CASCADE,related_name='VariantMaster_category')#refer the categorymaster table
    name=models.CharField(max_length=200,null=True,blank=True)#varient type name
    description=models.CharField(max_length=300,null=True,blank=True)#type description
    can_be_deleted=models.BooleanField(default=False)
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer iu_id


    class Meta:
        db_table='varient_master'
        ordering = ['created_at']

class VariantOption(BaseModel):
    """To store the Specific varient for the  product"""
    variation=models.ForeignKey(VariantMaster,on_delete=models.CASCADE,related_name='Variantoption_variation')#refer the variation table for type
    name=models.CharField(max_length=200,null=True,blank=True)
    description=models.CharField(max_length=300,null=True,blank=True)
    image=ArrayField(models.TextField(),blank=True,null=True)
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)

    class Meta:
        db_table='varient_option'
        ordering = ['created_at']


class ProductVariation(BaseModel):
    """It will store the variations for the particular products"""
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE,related_name='ProductVariation_product_master')#refer the productMaster
    variation=models.ForeignKey(VariantMaster,on_delete=models.CASCADE,related_name='ProductVariation_variation')#variations for the particular product
    total_price=models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)#price of the product
    selling_price=models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)#selling price of the product
    stock=models.IntegerField(blank=True,null=True)#quantity of the product 
    image=ArrayField(models.TextField(),blank=True,null=True)#image for each product
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)#refer the iu_id


    class Meta:
        db_table='product_variation'
        ordering = ['created_at']

"""fetch the whole order for specific user"""
class OrderDetails(BaseModel):
    #store the user where user is in CustomUser
    user = models.ForeignKey(CustomUser, related_name='OrderDetails_user', on_delete=models.CASCADE)
    #fetch whole product and its price stored in it
    total_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=0) 
    #store the iu id from the IUMaster
    iu_id=models.ForeignKey(IUMaster,related_name='OrderDetails_iuid',on_delete=models.CASCADE)
   
   
    class Meta:
        db_table = 'order_details'
        ordering = ['created_at']

"""store the order items one by one from order details for specific user"""    
class OrderItems(BaseModel):
    user = models.ForeignKey(CustomUser, related_name='OrderItems_user', on_delete=models.CASCADE)
    order=models.ForeignKey(OrderDetails, related_name='OrderItems_order',on_delete=models.CASCADE)
    product=models.ForeignKey(ProductMaster,related_name='OrderItems_product',on_delete=models.CASCADE)
    variation=models.ForeignKey(VariantOption,related_name='OrderItems_variation',on_delete=models.CASCADE)
    seller=models.ForeignKey(SellerProfile,related_name='OrderItems_seller',on_delete=models.CASCADE)
    quantity=models.IntegerField(null=True,blank=True)
    price=models.DecimalField(max_digits=10,null=True,blank=True,default=0,decimal_places=3)
    order_status=models.CharField(max_length=50,default="pending")
    delivered_location= models.TextField(null=True, blank=True)
    delivered_time=models.DateTimeField(null=True, blank=True)
    is_returned=models.BooleanField(default=False)
    return_pickup_location=models.CharField( max_length=250,null=True, blank=True)
    return_reason=models.TextField(blank=True,null=True)
    approved_by=models.IntegerField(blank=True, null=True)
    return_completed_time=models.DateTimeField(null=True, blank=True)
    iu_id=models.ForeignKey(IUMaster,related_name='OrderItems_iu_id',on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'order_items'
        ordering = ['created_at']
        
class PaymentTypeMaster(BaseModel):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=50,blank=True,null=True)
    iu_id=models.ForeignKey(IUMaster,related_name='PaymentTypeMaster_iuid',on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'payment_type'
        ordering = ['created_at']
        
class PaymentDetails(BaseModel):
    #fetch specific user order from the OrderDetails and store it 
    order=models.ForeignKey(OrderDetails, related_name='PaymentDetails_order',on_delete=models.CASCADE)
    payment_type=models.ForeignKey(PaymentTypeMaster, related_name='PaymentDetails_payment_type',on_delete=models.CASCADE)
    paid_amount=models.DecimalField(max_digits=10,null=True,blank=True,default=0,decimal_places=3)
    payment_status=models.CharField(max_length=50,default="pending")
    return_amount=models.DecimalField(max_digits=10,null=True,blank=True,default=0,decimal_places=3)
    
    
class WishlistItem(BaseModel):
    User=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name = 'wishlist_user')
    product_variant=models.ForeignKey(ProductVariation,on_delete=models.CASCADE,blank=True,null=True,related_name = 'wishlist_product_variant')
    Product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE)
    is_removed=models.BooleanField(default=False)#item is removed from wishlist or not
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)
    
    class Meta:
        db_table="wishlist_item"
        ordering=['created_at']

"""this table is used to store the products of user which are adding to cart
        1.get all products from cart.
        2.add product to cart.
        3.update quantity of cart.
        4.remove product from cart.
"""
class CartItem(BaseModel):
    User=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name = 'cartitem_user')
    product_variant=models.ForeignKey(ProductVariation,on_delete=models.CASCADE,blank=True,null=True,related_name = 'cartitem_product_variant')
    Product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE,related_name = 'cartitem_user_product')
    quantity=models.IntegerField(default=1)  # quantity of item add to cart
    is_removed=models.BooleanField(default=False) # boolean field to cart product is removed or not
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)

    class Meta:
        db_table="cart_item"
        ordering=['created_at']

class FeedbackDetails(BaseModel):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name = 'feedbackdetails_user')
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE,related_name = 'feedbackdetails_product')
    comments=models.TextField(blank=True,null=True)
    ratings=models.IntegerField(default=1)
    images=ArrayField(models.TextField(null=True,blank=True,default=dict))
    like_count=models.IntegerField(default=0)
    dislike_count=models.IntegerField(default=0)
    iu_id=models.ForeignKey(IUMaster,on_delete=models.CASCADE)    

    class Meta:
        db_table="feedback_details"
        ordering=['created_at']



 
