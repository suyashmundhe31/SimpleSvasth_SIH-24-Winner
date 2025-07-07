from django.contrib import admin
from .models import Hospital  # Import your Hospital model

# Simple admin registration
class HospitalAdmin(admin.ModelAdmin):
    # Customize the list display in admin panel
    list_display = (
        'hosp_ID', 
        'hosp_name', 
        'hosp_email', 
        'hosp_contact_no', 
        'hosp_address'
    )
    
    # Add search fields
    search_fields = (
        'hosp_ID', 
        'hosp_name', 
        'hosp_email'
    )
    
    # Add filter options
    list_filter = (
        'hosp_no_of_beds',
    )

# Register the model with the admin site
admin.site.register(Hospital, HospitalAdmin)