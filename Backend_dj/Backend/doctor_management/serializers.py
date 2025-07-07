from rest_framework import serializers
from .models import Doctor, Slot, OPDBooking, WalkInSlot

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class SlotSerializer(serializers.ModelSerializer):
    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    class Meta:
        model = Slot 
        fields = '__all__'

    def validate(self, data):
        # Custom validation example
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")
        return data

class OPDBookingSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor_id.doctor_name', read_only=True)  # Fetch doctor's name
    
    class Meta:
        model = OPDBooking
        fields = ['booking_id', 'start_time', 'end_time', 'date', 'patient_id', 'slot_id', 'doctor_id', 'doctor_name', 'patient_name', 'hospital_id', 'is_booked']

class WalkInSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalkInSlot
        fields = '__all__'


