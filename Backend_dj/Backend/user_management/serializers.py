from rest_framework import serializers
from .models import User
from django import forms


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'phone_no', 'email', 'password', 'role', 'gender', 'blood_group', 'date_of_birth']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_no', 
            'gender', 'blood_group', 'date_of_birth', 'role'
        ]
        read_only_fields = ['id', 'role']

    def update(self, instance, validated_data):
        # Allow updating specific fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_no = validated_data.get('phone_no', instance.phone_no)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.blood_group = validated_data.get('blood_group', instance.blood_group)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        
        instance.save()
        return instance
    