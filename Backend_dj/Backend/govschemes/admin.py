from django.contrib import admin
from .models import GovernmentScheme

@admin.register(GovernmentScheme)
class GovernmentSchemeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'schemeName', 
        'schemeUrl', 
        'userState', 
        'userAge', 
        'income', 
        'gender', 
        'familySize', 
        'maritalStatus', 
        'caste'
    )
    search_fields = ('schemeName', 'userState', 'income', 'gender', 'caste')
    list_filter = ('gender', 'maritalStatus', 'userState', 'caste')
    ordering = ('schemeName',)
