from django.conf import settings
from django.utils import timezone
import boto3
from botocore.config import Config
from rest_framework.response import Response
from rest_framework.views import status
import jwt


def upload_image_s3(image_file, file_name):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version='s3v4')
        )
        
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M')
        timestamps = current_time
        file_extension = file_name.split('.')[-1]
        unique_filename = f"{file_name.split('.')[0]}_{timestamps}.{file_extension}"
        
        s3_client.upload_fileobj(
            image_file,
            settings.AWS_STORAGE_BUCKET_NAME,
            f"product_images/{unique_filename}",
            ExtraArgs={'ACL': 'public-read', 'ServerSideEncryption': 'AES256'}
        )
        
        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/product_images/{unique_filename}"
        return image_url
    except Exception as e:
        raise Exception(f"Image upload failed: {str(e)}") 