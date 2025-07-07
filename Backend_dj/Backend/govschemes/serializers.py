from rest_framework import serializers
from .models import GovernmentScheme

class GovernmentSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernmentScheme
        fields = '__all__'
