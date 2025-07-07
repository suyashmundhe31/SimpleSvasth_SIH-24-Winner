from rest_framework import serializers
from .models import Hospital

class HospitalRegistrationSerializer(serializers.ModelSerializer):
    hosp_Cpassword = serializers.CharField(write_only=True)
    
    class Meta:
        model = Hospital
        fields = [
            'hosp_ID', 'hosp_name', 'hosp_email', 'hosp_contact_no', 
            'image_url', 'hosp_lat', 'hosp_log', 'hosp_address', 
            'hosp_no_of_beds', 'hosp_password', 'hosp_Cpassword'
        ]
        extra_kwargs = {
            'hosp_password': {'write_only': True},
        }
    
    def validate(self, data):
        # Password confirmation validation
        if data['hosp_password'] == data['hosp_Cpassword']:
            raise serializers.ValidationError({"hosp_Cpassword": "Passwords do not match."})
        
        # Remove confirm password field before saving
        data.pop('hosp_Cpassword')
        return data