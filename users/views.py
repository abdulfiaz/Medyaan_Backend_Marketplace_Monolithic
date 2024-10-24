from django.shortcuts import render
from django.contrib.auth.hashers import make_password,check_password
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.db import transaction, IntegrityError
from users.models import *
from rest_framework.response import Response
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from .auth import *
# Create your views here.



'''Login API for user login'''
@api_view(['POST'])
@permission_classes([AllowAny, ])
def login(request):
    if request.method == 'POST':
        try:
            mobile_number = request.data['mobile_number']
            password = request.data['password']
 
            try:
                user = CustomUser.objects.get(mobile_number =mobile_number )
            except CustomUser.DoesNotExist:
                return Response({'status': 'error', 'message': 'Email / mobile number not found'}, status=status.HTTP_401_UNAUTHORIZED)
 
            if not check_password(password, user.password):
                return Response({'status': 'error', 'message': 'Incorrect Password'}, status=status.HTTP_401_UNAUTHORIZED)

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
                    
            message = 'Login successfull'
            response_data = {'status': 'success', 'message': message, 'token': token}

            return Response({'status' : 'success' , 'message' : response_data})
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            transaction.rollback()
            return Response({'status': 'error', 'message': 'Something went wrong...' + str(e)},status=status.HTTP_400_BAD_REQUEST)
    