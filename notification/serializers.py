from django.conf import settings
from requests import Response
from rest_framework import serializers
from users.models import CustomUser
from .models import TemplateMaster,EventMaster,Notification

class TemplateMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model=TemplateMaster
        fields=['id','template_name','content']

class EventMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model=EventMaster
        fields=['id','name','email','role','sms_templateid','iu_id']
    def validate(self, data):       
        name = data.get('name')        
        if name:
            try:            
                template = TemplateMaster.objects.get(template_name=name)
                data['sms_templateid'] = template.id
            except TemplateMaster.DoesNotExist:
                raise serializers.ValidationError("The template name provided does not exist in TemplateMaster.")
        
        return data

class NotificationSerializer(serializers.ModelSerializer):
    event=serializers.PrimaryKeyRelatedField(queryset=EventMaster.objects.all())
    class Meta:
        model=Notification
        fields=['id','event','sender','receiver','subject','message','email_id','notification_message','redirect_link','role','iu_id']