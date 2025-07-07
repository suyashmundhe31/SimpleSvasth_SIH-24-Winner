# # from rest_framework import serializers
# # from .models import Ward

# # class WardSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Ward
# #         fields = [ 'ward_name', 'no_of_beds', 'cost', 'ward_img', 'ward_details'
# #             ] 
        
# #     def get_beds(self, obj):
# #         # Assuming you have a Bed model related to Ward
# #         # If not, you'll need to create one
# #         return [
# #             {
# #                 'bed_id': bed.id,
# #                 'status': bed.status
# #             } for bed in obj.beds.all()
# #         ]
        
        
        
# from rest_framework import serializers
# from .models import Ward, Bed

# class BedSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bed
#         fields = ['id', 'status']

# class WardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ward
#         fields = ['id', 'ward_name', 'no_of_beds', 'hospital', 'cost', 'ward_img', 'ward_details']

from rest_framework import serializers
from .models import Ward, Bed, BedBooking, PatientAdmission, PatientDischarge, DeathRecord
from datetime import timezone, timedelta

class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = ['id', 'status']

class WardSerializer(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)
    ward = serializers.CharField(source='id', read_only=True)# Include beds in the response

    class Meta:
        model = Ward
        fields = ['ward', 'ward_name', 'no_of_beds', 'hospital', 'cost', 'ward_img', 'ward_details', 'beds']
        
class BedBookingSerializer(serializers.ModelSerializer):
    ward_name = serializers.CharField(source='ward.name', read_only=True)
    book_id = serializers.IntegerField(source='id', read_only=True)  # Make it read-only
    prescription = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = BedBooking
        fields = [
            'book_id',
            'aadhar_number',
            'prescription',
            'booking_date',
            'ward',
            'ward_name',
            'hospital',
            'status'
        ]
        read_only_fields = ['status']
        
    # def to_representation(self, instance):
    #     # Convert the object to a dict
    #     ret = super().to_representation(instance)
    #     # Replace the prescription file object with its URL
    #     if ret.get('prescription'):
    #         ret['prescription'] = ret['prescription'].url if hasattr(ret['prescription'], 'url') else str(ret['prescription'])
    #     # Convert Ward object to string/ID if needed
    #     if ret.get('ward') and not isinstance(ret['ward'], (str, int)):
    #         ret['ward'] = ret['ward'].pk
    #     return ret
    
class PatientAdmissionSerializer(serializers.ModelSerializer):
    ward_name = serializers.CharField(source='ward.ward_name', read_only=True)
    bed_id = serializers.CharField(source='bed.id', read_only=True)
    
    class Meta:
        model = PatientAdmission
        fields = ['id', 'patient_id', 'patient_name', 'doctor_name', 'ward', 
                 'ward_name', 'bed', 'bed_id', 'hospital', 'admission_date', 
                 'admission_letter', 'created_at', 'status', 'occupation_hours',
                 'release_time']
        read_only_fields = ['id', 'patient_id', 'created_at', 'status']
    
    def get_remaining_time(self, obj):
        """Calculate remaining time for the admission"""
        if not obj.release_time:
            return None
            
        now = timezone.now()
        if now >= obj.release_time:
            return "0h 0m"
            
        time_diff = obj.release_time - now
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"


class PatientDischargeSerializer(serializers.ModelSerializer):
    admission_details = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientDischarge
        fields = ['discharge_id', 'admission', 'admission_details', 'discharge_date', 'discharge_document']
        
    def get_admission_details(self, obj):
        return {
            'admission_id': obj.admission.id,
            'patient_name': obj.admission.patient_name,
            'doctor_name': obj.admission.doctor_name,
            'ward_id': obj.admission.ward.id,
            'ward_name': obj.admission.ward.ward_name,
            'bed_id': obj.admission.bed.id,
            'admission_date': obj.admission.admission_date
        }
        
class DeathRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient_admission.patient_name', read_only=True)
    ward_name = serializers.CharField(source='patient_admission.ward.ward_name', read_only=True)
    bed_id = serializers.CharField(source='patient_admission.bed.id', read_only=True)

    class Meta:
        model = DeathRecord
        fields = [
            'id', 
            'patient_admission', 
            'patient_name',
            'ward_name',
            'bed_id',
            'death_date', 
            'death_certificate',
            'created_at'
        ]
        read_only_fields = ['created_at']