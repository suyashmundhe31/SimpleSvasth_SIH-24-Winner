# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .models import Hospital
# from .serializers import HospitalRegistrationSerializer

# class HospitalRegistrationView(APIView):
#     def get(self, request):
#         # Get all hospitals
#         hospitals = Hospital.objects.all()  # Fetch all hospitals from the database
#         serializer = HospitalRegistrationSerializer(hospitals, many=True)
        
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     def post(self, request):
#         # Handle the hospital registration logic
#         serializer = HospitalRegistrationSerializer(data=request.data)
        
#         if serializer.is_valid():
#             # Save the hospital registration
#             serializer.save()
#             return Response({
#                 'message': 'Hospital registered successfully',
#                 'hospital_id': serializer.data['hosp_ID']
#             }, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password, check_password
import time
from .models import Hospital
from .serializers import HospitalRegistrationSerializer

class HospitalRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Get all hospitals
        hospitals = Hospital.objects.all()  # Fetch all hospitals from the database
        serializer = HospitalRegistrationSerializer(hospitals, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        # Handle the hospital registration logic
        # Create a copy of the request data to modify password
        registration_data = request.data.copy()
        
        # Hash the password before saving
        if 'hosp_password' in registration_data:
            registration_data['hosp_password'] = make_password(registration_data['hosp_password'])
        
        serializer = HospitalRegistrationSerializer(data=registration_data)
        
        if serializer.is_valid():
            # Save the hospital registration
            serializer.save()
            return Response({
                'message': 'Hospital registered successfully',
                'hospital_id': serializer.data['hosp_ID']
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HospitalLoginView(APIView):
   permission_classes = [AllowAny]

   def post(self, request):
       hosp_ID = request.data.get('hosp_ID')
       hosp_email = request.data.get('hosp_email')
       if not hosp_ID or not hosp_email:
           return Response({'error': 'Hospital ID and Email are required'}, status=status.HTTP_400_BAD_REQUEST)
       try:
           hospital = Hospital.objects.get(hosp_ID=hosp_ID, hosp_email=hosp_email)
           return Response({
               'message': 'Login successful',
               'hospital_name': hospital.hosp_name,
               'hospital_id': hospital.hosp_ID,
               'hospital_email': hospital.hosp_email,
               'hospital_no_of_beds': hospital.hosp_no_of_beds
           })
       except Hospital.DoesNotExist:
           return Response({'error': 'Invalid Hospital ID or Email'}, status=status.HTTP_401_UNAUTHORIZED)
   
        