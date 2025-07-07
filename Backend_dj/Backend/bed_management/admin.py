from django.contrib import admin
from .models import Ward
from .models import Bed

class WardAdmin(admin.ModelAdmin):
    
    list_display = (
        'ward_name', 
        'no_of_beds', 
        'cost', 
        'ward_img', 
        'ward_details'
    )
    
admin.site.register(Ward)

class BedAdmin(admin.ModelAdmin):
    list_display = ('id', 'ward', 'status')  # Display the bed's id, ward, and status in the list
    list_filter = ('status',)  # Allow filtering by status (vacant, occupied, maintenance)
    search_fields = ('id', 'ward__ward_name')  # Allow searching by bed id or ward name

    # Optional: You can add more actions like changing status from the list view
    actions = ['mark_as_occupied', 'mark_as_vacant', 'mark_as_maintenance']

    def mark_as_occupied(self, request, queryset):
        queryset.update(status=Bed.OCCUPIED)
    mark_as_occupied.short_description = "Mark selected beds as Occupied"

    def mark_as_vacant(self, request, queryset):
        queryset.update(status=Bed.VACANT)
    mark_as_vacant.short_description = "Mark selected beds as Vacant"

    def mark_as_maintenance(self, request, queryset):
        queryset.update(status=Bed.MAINTENANCE)
    mark_as_maintenance.short_description = "Mark selected beds as Maintenance"

admin.site.register(Bed, BedAdmin)