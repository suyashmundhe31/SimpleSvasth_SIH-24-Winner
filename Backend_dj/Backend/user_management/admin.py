from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'username', 'email', 'phone_no', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'gender', 'blood_group')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'phone_no', 'gender', 'blood_group', 'date_of_birth')}),
        ('Permissions', {'fields': ('role', 'is_active')}),
        ('Important dates', {'fields': ('created_at',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'phone_no', 'role'),
        }),
    )
    search_fields = ('username', 'email', 'phone_no')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

admin.site.register(User, CustomUserAdmin)