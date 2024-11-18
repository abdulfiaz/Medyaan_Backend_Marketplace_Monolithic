from rest_framework import serializers
from users.models import CustomUser, UserPersonalProfile, RoleMaster
from adminapp.models import IUMaster
from django.contrib.auth.hashers import make_password,check_password


class CustomUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True) 
    class Meta:
        model = CustomUser
        fields = ['mobile_number', 'email','password','temp_code', 'is_approval', 'approved_by', 'iu_id','created_by','modified_by','confirm_password','is_active']
    
    def validate(self, data):
        if 'password' in data:
            if data['password'] != data.pop('confirm_password'):
                raise serializers.ValidationError('Passwords do not match')
            data['password'] = make_password(data['password'])  

        return data
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(CustomUserSerializer, self).__init__(*args, **kwargs)
 
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    



class UserPersonalProfileSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = UserPersonalProfile
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(UserPersonalProfileSerializer, self).__init__(*args, **kwargs)
 
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    
        
    def to_representation(self,instance):
        data=super().to_representation(instance)
        
        customuser_details= CustomUserSerializer(instance.user).data
        data['custom_user_details']={field:customuser_details[field] for field in ['mobile_number', 'email']}
    
        return data




class GetCustomUserSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(source='userdetails.first.firstname', default=None)
    lastname = serializers.CharField(source='userdetails.first.lastname', default=None)
    profilephoto = serializers.CharField(source='userdetails.first.profilephoto', default={})
    gender = serializers.CharField(source='userdetails.first.gender', default=None)
    age = serializers.IntegerField(source='userdetails.first.age', default=None)
    language = serializers.CharField(source='userdetails.first.language', default=None)
    primary_address = serializers.CharField(source='userdetails.first.primary_address', default=None)
    secondary_address = serializers.CharField(source='userdetails.first.secondary_address', default=None)

    class Meta:
        model = CustomUser
        fields = ['mobile_number', 'email', 'firstname', 'lastname','profilephoto', 'gender', 'age', 'language','primary_address', 'secondary_address']

