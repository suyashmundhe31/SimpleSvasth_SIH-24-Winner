from django.contrib import admin
from .models import Doctor, Slot, OPDBooking, WalkInSlot

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('doctor_name', 'doctor_email', 'doctor_phone', 'department', 'hospital_id', 'fees')
    search_fields = ('doctor_name', 'doctor_email', 'department')
    list_filter = ('department', 'hospital_id')

class SlotAdmin(admin.ModelAdmin):
    list_display = ('doctor_id', 'day', 'start_time', 'end_time', 'interval', 'online_hours')

admin.site.register(Slot, SlotAdmin)

class OPDBookingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OPDBooking._meta.fields]  
    search_fields = ['patient_name', 'doctor_id', 'hospital_id']
    list_filter = ['date', 'doctor_id', 'hospital_id', 'is_booked'] 
    
admin.site.register(OPDBooking, OPDBookingAdmin)


@admin.register(WalkInSlot)
class WalkInSlotAdmin(admin.ModelAdmin):
    # List of fields to display in the admin list view
    list_display = (
        'walkin_id', 
        'doctor', 
        'patient_name', 
        'patient_id', 
        'token_number', 
        'created_at'
    )
    
    # Fields that can be used to filter the list
    list_filter = (
        'doctor', 
        'created_at'
    )
    
    # Fields that can be searched
    search_fields = (
        'patient_name', 
        'patient_id__username',  # Assuming User model has a username field
        'doctor__doctor_name'
    )
    
    # Read-only fields (cannot be edited in admin)
    readonly_fields = (
        'walkin_id', 
        'token_number', 
        'created_at'
    )
    
    # Customize the form
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_name', 'patient_id')
        }),
        ('Appointment Details', {
            'fields': ('doctor', 'token_number', 'created_at')
        }),
    )
    
    # Sort by created_at in descending order by default
    ordering = ('-created_at',)