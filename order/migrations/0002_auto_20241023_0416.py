# Generated by Django 3.0.6 on 2024-10-23 04:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seller', '0001_initial'),
        ('adminapp', '0001_initial'),
        ('order', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlistitem',
            name='User',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='wishlistitem',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='wishlistitem',
            name='product_variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_product_variant', to='order.ProductVariation'),
        ),
        migrations.AddField(
            model_name='variantoption',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='variantoption',
            name='variation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Variantoption_variation', to='order.VariantMaster'),
        ),
        migrations.AddField(
            model_name='variantmaster',
            name='categroy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='VariantMaster_category', to='order.ProductCategoryMaster'),
        ),
        migrations.AddField(
            model_name='variantmaster',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='productvariation',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='productvariation',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ProductVariation_product_master', to='order.ProductMaster'),
        ),
        migrations.AddField(
            model_name='productvariation',
            name='variation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ProductVariation_variation', to='order.VariantMaster'),
        ),
        migrations.AddField(
            model_name='productmaster',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='productmaster',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_master_seller', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='productmaster',
            name='subcategroy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_master_sub_category', to='order.ProductCategoryMaster'),
        ),
        migrations.AddField(
            model_name='productcategorymaster',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_category_master_iu', to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='productcategorymaster',
            name='sub_categories',
            field=models.ManyToManyField(blank=True, related_name='_productcategorymaster_sub_categories_+', to='order.ProductCategoryMaster'),
        ),
        migrations.AddField(
            model_name='paymenttypemaster',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PaymentTypeMaster_iuid', to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='paymentdetails',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PaymentDetails_order', to='order.OrderDetails'),
        ),
        migrations.AddField(
            model_name='paymentdetails',
            name='payment_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PaymentDetails_payment_type', to='order.PaymentTypeMaster'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderItems_iu_id', to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderItems_order', to='order.OrderDetails'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderItems_product', to='order.ProductMaster'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderItems_seller', to='seller.SellerProfile'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderItems_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='variation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderItems_variation', to='order.VariantOption'),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderDetails_iuid', to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderDetails_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='feedbackdetails',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='feedbackdetails',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbackdetails_product', to='order.ProductMaster'),
        ),
        migrations.AddField(
            model_name='feedbackdetails',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbackdetails_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='Product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cartitem_user_product', to='order.ProductMaster'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='User',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cartitem_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='iu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.IUMaster'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cartitem_product_variant', to='order.ProductVariation'),
        ),
    ]