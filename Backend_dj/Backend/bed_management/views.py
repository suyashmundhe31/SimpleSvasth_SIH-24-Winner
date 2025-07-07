from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Ward, Bed , BedBooking, PatientAdmission, PatientDischarge, DeathRecord
from .serializers import WardSerializer, BedBookingSerializer, PatientAdmissionSerializer, PatientDischargeSerializer, DeathRecordSerializer
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from api.models import Hospital
from django.db import IntegrityError
from django.db import transaction, IntegrityError
from rest_framework import status
from django.db.models import Max, F
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
# class WardAddView(APIView):
#     def post(self, request, hosp_id):  # Changed from hosp_ID 
#         try:
#             ward_data = {
#                 **request.data,
#                 'hospital': hosp_id
#             }
#             serializer = WardSerializer(data=ward_data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=201)
#             return Response(serializer.errors, status=400)
#         except Hospital.DoesNotExist:
#             return Response({'error': 'Hospital not found'}, status=404)

    # def get(self, request, hosp_id):  # Changed from hosp_ID
    #     wards = Ward.objects.filter(hospital=hosp_id)
    #     serializer = WardSerializer(wards, many=True)
    #     return Response(serializer.data)


class WardAddView(APIView):
    def post(self, request, hosp_id):
        ward_id = request.data.get('ward')
        if not ward_id:
            return Response({'error': 'ward_id is required'}, status=400)

        try:
            with transaction.atomic():
                ward = Ward.objects.select_for_update().get(id=ward_id, hospital_id=hosp_id)
                
                # Simply increment no_of_beds by 1
                ward.no_of_beds += 1
                ward.save()
                
                serializer = WardSerializer(ward)
                return Response(serializer.data)
                
        except Ward.DoesNotExist:
            return Response({'error': 'Ward not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        
    def get(self, request, hosp_id):
        wards = Ward.objects.filter(hospital=hosp_id)
        serializer = WardSerializer(wards, many=True)
        return Response(serializer.data)       


        
class WardBedDeleteView(APIView):
    def post(self, request, hosp_id):
        try:
            ward_id = request.data.get('ward')
            ward = Ward.objects.get(id=ward_id, hospital=hosp_id)
            
            # Prevent deletion if only 1 bed remains
            if ward.no_of_beds <= 1:
                return Response({
                    'error': 'Cannot delete the last bed in ward'
                }, status=400)
            
            # Get the last bed and delete it
            last_bed = ward.beds.order_by('-id').first()
            if last_bed:
                if last_bed.status == 'occupied':
                    return Response({
                        'error': 'Cannot delete an occupied bed'
                    }, status=400)
                    
                last_bed.delete()
                ward.no_of_beds -= 1
                ward.save()
                
                return Response({
                    'message': 'Bed deleted successfully',
                    'ward': WardSerializer(ward).data
                })
            
            return Response({
                'error': 'No beds found in ward'
            }, status=404)
            
        except Ward.DoesNotExist:
            return Response({
                'error': 'Ward not found'
            }, status=404)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=400)
    
    
    

class WardBedUpdateView(APIView):
    def post(self, request, hosp_id):
        ward_id = request.data.get('ward')
        try:
            ward = Ward.objects.get(id=ward_id, hospital_id=hosp_id)
            ward.no_of_beds += 1
            ward.save()  # This will trigger the auto-creation of beds
            serializer = WardSerializer(ward)
            return Response(serializer.data)
        except Ward.DoesNotExist:
            return Response({'error': 'Ward not found'}, status=404)

# class WardListView(APIView):
#    def get(self, request, hosp_id):
#        wards = Ward.objects.filter(hospital=hosp_id).prefetch_related('beds')
#        serializer = WardSerializer(wards, many=True)
#        return Response(serializer.data, status=status.HTTP_200_OK)
       
       
class WardListView(APIView):
    def get(self, request, hosp_id):
        wards = Ward.objects.filter(hospital=hosp_id).prefetch_related('beds')
        serializer = WardSerializer(wards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, hosp_id):
        action = request.data.get('action')
        if action == 'add_bed':
            try:
                ward_id = request.data.get('ward_id')
                ward = Ward.objects.get(id=ward_id, hospital=hosp_id)
                
                # Get the last bed number and increment
                last_bed = ward.beds.order_by('-id').first()
                if last_bed:
                    last_num = int(last_bed.id.split('B')[1])
                    new_bed_num = str(last_num + 1).zfill(3)
                else:
                    new_bed_num = '001'
                
                # Create new bed with formatted ID
                new_bed = Bed.objects.create(
                    id=f"{ward_id}-B{new_bed_num}",
                    ward=ward,
                    status='vacant'
                )

                # Update no_of_beds in ward
                ward.no_of_beds = ward.beds.count()
                ward.save()
                
                # Return updated ward list
                updated_wards = Ward.objects.filter(hospital=hosp_id).prefetch_related('beds')
                serializer = WardSerializer(updated_wards, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Ward.DoesNotExist:
                return Response(
                    {"error": "Ward not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

    def delete(self, request, hosp_id):
        action = request.data.get('action')
        if action == 'delete_bed':
            try:
                ward_id = request.data.get('ward_id')
                bed_id = request.data.get('bed_id')  # This should be in "ward_id-B001" format
                
                ward = Ward.objects.get(id=ward_id, hospital=hosp_id)
                bed = Bed.objects.get(id=bed_id, ward=ward)

                # Only allow deletion of vacant beds
                if bed.status != 'vacant':
                    return Response(
                        {"error": "Cannot delete an occupied bed"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Delete the bed
                bed.delete()

                # Update no_of_beds in ward
                ward.no_of_beds = ward.beds.count()
                ward.save()

                # Return updated ward list
                updated_wards = Ward.objects.filter(hospital=hosp_id).prefetch_related('beds')
                serializer = WardSerializer(updated_wards, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except Ward.DoesNotExist:
                return Response(
                    {"error": "Ward not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Bed.DoesNotExist:
                return Response(
                    {"error": "Bed not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"error": "Invalid action"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class BedStatusUpdateView(APIView):
    def put(self, request, hosp_id):
        bed_id = request.data.get('bed_id')
        new_status = request.data.get('status')
        
        if new_status not in ['vacant', 'occupied', 'maintenance']:
            return Response({'error': 'Invalid status'}, status=400)
        
        try:
            bed = Bed.objects.select_related('ward').get(
                id=bed_id,
                ward__hospital_id=hosp_id
            )
            bed.status = new_status
            bed.save()
            return Response({'message': 'Status updated'}, status=200)
        except Bed.DoesNotExist:
            return Response({'error': 'Bed not found'}, status=404) 
        
@csrf_exempt          
def update_bed_status(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            bed_id = data.get('bed_id')
            new_status = data.get('status')

            if not bed_id or not new_status:
                return JsonResponse({'error': 'Invalid data'}, status=400)

            if new_status not in ['vacant', 'occupied', 'maintenance']:
                return JsonResponse({'error': 'Invalid status'}, status=400)

            try:
                bed = Bed.objects.get(id=bed_id)
                bed.status = new_status
                bed.save()
                return JsonResponse({'message': 'Bed status updated successfully'}, status=200)
            except Bed.DoesNotExist:
                return JsonResponse({'error': 'Bed not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if request.method == 'GET':
        bed_id = request.GET.get('bed_id')

        if bed_id:
            try:
                bed = Bed.objects.get(id=bed_id)
                return JsonResponse({
                    'bed_id': bed.id,
                    'status': bed.status,
                    'ward': bed.ward.name,
                    'hospital_id': bed.ward.hospital_id
                }, status=200)
            except Bed.DoesNotExist:
                return JsonResponse({'error': 'Bed not found'}, status=404)
        else:
            beds = Bed.objects.all()
            bed_list = [
                {
                    'bed_id': bed.id,
                    'status': bed.status,
                    'ward': bed.ward.name,
                    'hospital_id': bed.ward.hospital_id
                } for bed in beds
            ]
            return JsonResponse(bed_list, safe=False, status=200)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

class BedBookingView(APIView):  # Changed from BedBooking to BedBookingView
    def post(self, request, hospital_id=None, booking_id=None, action=None):
        # Handle booking creation
        if hospital_id and not booking_id:
            try:
                booking_data = {
                    'aadhar_number': request.data.get('aadhar_number'),
                    'prescription': request.data.get('prescription'),
                    'booking_date': request.data.get('booking_date'),
                    'ward': request.data.get('ward'),
                    'hospital': hospital_id,
                    'status': 'pending'  # Set initial status
                }
                
                serializer = BedBookingSerializer(data=booking_data)
                if serializer.is_valid():
                    booking = serializer.save()
                    return Response({
                        'message': 'Booking request submitted successfully',
                        'booking_id': booking.id
                    }, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
                
        # Handle approve/reject actions
        elif booking_id and action:
            try:
                booking = BedBooking.objects.get(id=booking_id)
                
                if action == 'approve':
                    bed_id = request.data.get('bed_id')
                    if not bed_id:
                        return Response({'error': 'bed_id required'}, status=400)
                        
                    bed = Bed.objects.get(id=bed_id)
                    bed.status = 'occupied'
                    bed.save()
                    
                    booking.bed = bed
                    booking.status = 'approved'
                    booking.save()
                    
                    return Response({'status': 'success'}, status=status.HTTP_200_OK)
                    
                elif action == 'reject':
                    booking.status = 'rejected'
                    booking.save()
                    
                return Response({'status': 'success'})
                
            except (BedBooking.DoesNotExist, Bed.DoesNotExist) as e:
                return Response({'error': str(e)}, status=404)
            except Exception as e:
                return Response({'error': str(e)}, status=500)
            
    def put(self, request, booking_id, action):
        try:
            booking = BedBooking.objects.get(id=booking_id)
            
            if action == 'approve':
                booking.status = 'approved'
                # Update the bed status to 'occupied'
                bed = booking.bed
                bed.status = 'occupied'
                bed.save()
            elif action == 'reject':
                booking.status = 'rejected'
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking.save()
            
            return Response({'message': 'Booking status updated successfully'}, status=status.HTTP_200_OK)
        
        except BedBooking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request, hospital_id=None, booking_id=None):
        if booking_id:
            try:
                booking = BedBooking.objects.get(id=booking_id)
                serializer = BedBookingSerializer(booking)
                return Response(serializer.data)
            except BedBooking.DoesNotExist:
                return Response({'error': 'Booking not found'}, status=404)
        
        if hospital_id:
            bookings = BedBooking.objects.filter(hospital_id=hospital_id)
            serializer = BedBookingSerializer(bookings, many=True)
            return Response(serializer.data)
        
        return Response({'error': 'Hospital ID or Booking ID required'}, status=400)
    
class BedBookingView(APIView):
    def post(self, request, hospital_id=None, booking_id=None, action=None):
        # Handle booking creation
        if hospital_id and not booking_id:
            try:
                booking_data = {
                    'aadhar_number': request.data.get('aadhar_number'),
                    # 'prescription': request.data.get('prescription'),
                    'booking_date': request.data.get('booking_date'),
                    'ward': request.data.get('ward'),
                    'hospital': hospital_id,
                    'status': 'pending'
                }
                
                prescription_file = request.FILES.get('prescription')
                if prescription_file:
                    booking_data['prescription'] = prescription_file
                
                serializer = BedBookingSerializer(data=booking_data)
                if serializer.is_valid():
                    booking = serializer.save()
                    # Updated response format
                    return Response({
                        'book_id': booking.id,
                        'aadhar_number': booking.aadhar_number,
                        # 'prescription': booking.prescription.url if booking.prescription else None,
                        'booking_date': booking.booking_date,
                        'ward': booking.ward.id,
                        'hospital': booking.hospital.hosp_ID,
                        'status': booking.status
                        
                    }, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle approve endpoint
        elif booking_id and 'approve' in request.path:
            try:
                booking = BedBooking.objects.get(id=booking_id)
                
                if booking.status != 'pending':
                    return Response({
                        'error': 'This booking has already been processed'
                    }, status=status.HTTP_400_BAD_REQUEST)

                bed_id = request.data.get('bed_id')
                if not bed_id:
                    return Response({
                        'error': 'bed_id required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                try:
                    bed = Bed.objects.get(id=bed_id)
                    # Check if bed is actually vacant
                    if bed.status != 'vacant':
                        return Response({
                            'error': 'Selected bed is not vacant'
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                    bed.status = 'occupied'
                    bed.save()
                    
                    booking.bed = bed
                    booking.status = 'approved'
                    booking.save()
                    
                    # Updated response format
                    return Response({
                        'book_id': booking.id,
                        'aadhar_number': booking.aadhar_number,
                        # 'prescription': booking.prescription,
                        'booking_date': booking.booking_date,
                        'ward': booking.ward.id,
                        'hospital': booking.hospital.hosp_ID,
                        'status': booking.status
                    }, status=status.HTTP_200_OK)
                    
                except Bed.DoesNotExist:
                    return Response({
                        'error': 'Bed not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
            except BedBooking.DoesNotExist:
                return Response({
                    'error': 'Booking not found'
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Handle reject endpoint
        elif booking_id and 'reject' in request.path:
            try:
                booking = BedBooking.objects.get(id=booking_id)
                booking.status = 'rejected'
                booking.save()
                
                # Updated response format
                return Response({
                    'book_id': booking.id,
                    'aadhar_number': booking.aadhar_number,
                    # 'prescription': booking.prescription,
                    'booking_date': booking.booking_date,
                    'ward': booking.ward,
                    'hospital': booking.hospital.id,
                    'status': booking.status
                }, status=status.HTTP_200_OK)
                
            except BedBooking.DoesNotExist:
                return Response({
                    'error': 'Booking not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
        return Response({
            'error': 'Invalid request'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, hospital_id=None, booking_id=None):
        if booking_id:
            try:
                booking = BedBooking.objects.get(id=booking_id)
                serializer = BedBookingSerializer(booking)
                return Response(serializer.data)
            except BedBooking.DoesNotExist:
                return Response({'error': 'Booking not found'}, status=404)
        
        if hospital_id:
            bookings = BedBooking.objects.filter(hospital_id=hospital_id)
            serializer = BedBookingSerializer(bookings, many=True)
            return Response(serializer.data)
        
        return Response({'error': 'Hospital ID or Booking ID required'}, status=400)


# class PatientAdmissionView(APIView):
#     def post(self, request, hosp_id):
#         try:
#             ward_id = request.data.get('ward_id')
#             bed_id = request.data.get('bed_id')
            
#             ward = get_object_or_404(Ward, id=ward_id, hospital_id=hosp_id)
#             bed = get_object_or_404(Bed, id=bed_id, ward=ward)
            
#             if bed.status != 'vacant':
#                 return Response(
#                     {'error': 'Selected bed is not available'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             admission_letter = request.FILES.get('admission_letter')
            
#             admission_data = {
#                 'patient_name': request.data.get('patient_name'),
#                 'doctor_name': request.data.get('doctor_name'),  # Changed from doctor_id
#                 'ward': ward.id,
#                 'bed': bed.id,
#                 'hospital': hosp_id,
#                 'admission_date': request.data.get('admission_date'),
#                 'admission_letter': admission_letter
#             }
            
#             serializer = PatientAdmissionSerializer(data=admission_data)
#             if serializer.is_valid():
#                 admission = serializer.save()
#                 response_data = serializer.data
#                 response_data['message'] = 'Patient admitted successfully'
#                 return Response(
#                     response_data,
#                     status=status.HTTP_201_CREATED
#                 )
#             return Response(
#                 serializer.errors,
#                 status=status.HTTP_400_BAD_REQUEST
#             )
            
#         except Exception as e:
#             return Response(
#                 {'error': str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
            
#     def get(self, request, hosp_id):
#         try:
#             # Fetch all admissions for the hospital
#             admissions = PatientAdmission.objects.filter(hospital=hosp_id)
            
#             if not admissions.exists():
#                 return Response(
#                     {'error': 'No admissions found for the specified hospital'},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
            
#             admission_data = []
#             for admission in admissions:
#                 admission_data.append({
#                     'admission_id': admission.id,
#                     'patient_name': admission.patient_name,
#                     'doctor_name': admission.doctor_name,
#                     'ward_id': admission.ward.id,
#                     'ward_name': admission.ward.ward_name,
#                     'bed_id': admission.bed.id,
#                     'admission_date': admission.admission_date,
#                 })
            
#             return Response(
#                 {
#                     'hospital_id': hosp_id,
#                     'admissions': admission_data,
#                     'message': 'Data retrieved successfully'
#                 },
#                 status=status.HTTP_200_OK
#             )
            
#         except Exception as e:
#             return Response(
#                 {'error': str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

class ExtendTimeView(APIView):
    def post(self, request, hosp_id):
        try:
            bed_id = request.data.get('bed_id')
            additional_hours = int(request.data.get('additional_hours'))
            
            if not all([bed_id, additional_hours]):
                return Response(
                    {'error': 'Missing required fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the latest admission for this bed
            admission = PatientAdmission.objects.filter(
                bed_id=bed_id,
                hospital_id=hosp_id,
                status='admitted'
            ).latest('created_at')
            
            # Update occupation_hours and release_time
            admission.occupation_hours += additional_hours
            admission.release_time = admission.release_time + timedelta(hours=additional_hours)
            admission.save()
            
            # Calculate remaining time
            remaining_time = admission.release_time - timezone.now()
            hours = max(0, int(remaining_time.total_seconds() // 3600))
            minutes = max(0, int((remaining_time.total_seconds() % 3600) // 60))
            
            return Response({
                'message': 'Time extended successfully',
                'occupation_hours': admission.occupation_hours,
                'remaining_time': f"{hours}h {minutes}m"
            }, status=status.HTTP_200_OK)
            
        except PatientAdmission.DoesNotExist:
            return Response(
                {'error': 'No active admission found for this bed'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error extending time: {e}")  # Add logging
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PatientAdmissionView(APIView):
    def post(self, request, hosp_id):
        try:
            ward_id = request.data.get('ward_id')
            bed_id = request.data.get('bed_id')
            occupation_hours = int(request.data.get('occupation_hours', 24))  # Default 24 hours
            
            ward = get_object_or_404(Ward, id=ward_id, hospital_id=hosp_id)
            bed = get_object_or_404(Bed, id=bed_id, ward=ward)
            
            if bed.status != 'vacant':
                return Response(
                    {'error': 'Selected bed is not available'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            admission_letter = request.FILES.get('admission_letter')
            
            # Calculate release time
            release_time = timezone.now() + timedelta(hours=occupation_hours)
            
            admission_data = {
                'patient_name': request.data.get('patient_name'),
                'doctor_name': request.data.get('doctor_name'),
                'ward': ward.id,
                'bed': bed.id,
                'hospital': hosp_id,
                'admission_date': request.data.get('admission_date'),
                'admission_letter': admission_letter,
                'occupation_hours': occupation_hours,
                'release_time': release_time
            }
            
            serializer = PatientAdmissionSerializer(data=admission_data)
            if serializer.is_valid():
                admission = serializer.save()
                response_data = serializer.data
                response_data['message'] = 'Patient admitted successfully'
                response_data['remaining_time'] = f"{occupation_hours}h 0m"
                return Response(
                    response_data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            print(f"Error in admission: {e}")  # Add logging
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    def get(self, request, hosp_id):
        try:
            admissions = PatientAdmission.objects.filter(
                hospital=hosp_id,
                status='admitted'
            ).select_related('ward', 'bed')
            
            if not admissions.exists():
                return Response(
                    {'error': 'No admissions found for the specified hospital'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            admission_data = []
            now = timezone.now()
            
            for admission in admissions:
                # Calculate remaining time
                if admission.release_time:
                    time_diff = admission.release_time - now
                    total_seconds = max(0, time_diff.total_seconds())
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    remaining_time = f"{hours}h {minutes}m"
                else:
                    remaining_time = "0h 0m"
                
                admission_data.append({
                    'admission_id': admission.id,
                    'patient_name': admission.patient_name,
                    'doctor_name': admission.doctor_name,
                    'ward_id': admission.ward.id,
                    'ward_name': admission.ward.ward_name,
                    'bed_id': admission.bed.id,
                    'admission_date': admission.admission_date,
                    'remaining_time': remaining_time,
                    'occupation_hours': admission.occupation_hours
                })
            
            return Response(
                {
                    'hospital_id': hosp_id,
                    'admissions': admission_data,
                    'message': 'Data retrieved successfully'
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            print(f"Error fetching admissions: {e}")  # Add logging
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PatientDischargeView(APIView):
    def post(self, request, hosp_id):
        try:
            bed_id = request.data.get('bed_id')
            
            # Find the admission record for this bed
            admission = PatientAdmission.objects.filter(
                hospital=hosp_id,
                bed_id=bed_id,
                bed__status='occupied'  # Verify bed is currently occupied
            ).latest('admission_date')
            
            if not admission:
                return Response(
                    {'error': 'No active admission record found for this bed'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            discharge_data = {
                'admission': admission.id,
                'discharge_date': request.data.get('discharge_date'),
                'discharge_document': request.FILES.get('discharge_document')
            }
            
            serializer = PatientDischargeSerializer(data=discharge_data)
            if serializer.is_valid():
                # Start transaction to ensure both discharge creation and bed status update happen together
                with transaction.atomic():
                    # Create discharge record
                    discharge = serializer.save()
                    
                    # Update bed status to vacant
                    bed = admission.bed
                    bed.status = 'vacant'
                    bed.save()
                    
                    # Optional: Log the bed status change
                    print(f"Bed {bed.id} status changed from occupied to vacant")
                
                return Response({
                    'message': 'Patient discharged successfully',
                    'discharge_id': discharge.discharge_id,
                    'bed_status': 'vacant',
                    'bed_number': bed.id
                }, status=status.HTTP_201_CREATED)
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except PatientAdmission.DoesNotExist:
            return Response(
                {'error': 'No active admission found for this bed'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    def get(self, request, hosp_id):
        try:
            # Get all discharges for the hospital by joining with PatientAdmission
            discharges = PatientDischarge.objects.filter(
                admission__hospital=hosp_id
            ).select_related('admission', 'admission__ward', 'admission__bed')

            if not discharges:
                return Response(
                    {'message': 'No discharge records found for this hospital'},
                    status=status.HTTP_404_NOT_FOUND
                )

            discharge_data = []
            for discharge in discharges:
                data = {
                    'discharge_id': discharge.discharge_id,
                    'patient_name': discharge.admission.patient_name,
                    'doctor_name': discharge.admission.doctor_name,
                    'ward_name': discharge.admission.ward.ward_name,
                    'bed_number': discharge.admission.bed.id,
                    'admission_date': discharge.admission.admission_date,
                    'discharge_date': discharge.discharge_date,
                    'discharge_document': request.build_absolute_uri(discharge.discharge_document.url) if discharge.discharge_document else None
                }
                discharge_data.append(data)

            return Response({
                'hospital_id': hosp_id,
                'discharges': discharge_data,
                'total_discharges': len(discharge_data),
                'message': 'Discharge records retrieved successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
class DeathRecordView(APIView):
    def post(self, request, hosp_id):
        try:
            # Get the patient admission
            bed_id = request.data.get('bed_id')
            admission = PatientAdmission.objects.filter(
                hospital=hosp_id,
                bed_id=bed_id,
                bed__status='occupied'
            ).latest('admission_date')

            if not admission:
                return Response(
                    {'error': 'No active admission found for this bed'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Create death record
            death_record_data = {
                'patient_admission': admission.id,
                'death_date': request.data.get('death_date'),
                'death_certificate': request.FILES.get('death_certificate')
            }

            serializer = DeathRecordSerializer(data=death_record_data)
            if serializer.is_valid():
                # Use transaction to ensure both operations complete or neither does
                with transaction.atomic():
                    # Create death record
                    death_record = serializer.save()
                    
                    # Update bed status to vacant
                    bed = admission.bed
                    bed.status = 'vacant'
                    bed.save()

                    # Update admission status if needed
                    admission.status = 'deceased'
                    admission.save()

                return Response({
                    'message': 'Death record created successfully',
                    'death_record': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except PatientAdmission.DoesNotExist:
            return Response(
                {'error': 'No active admission found for this bed'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, hosp_id):
        try:
            death_records = DeathRecord.objects.filter(
                patient_admission__hospital=hosp_id
            ).select_related(
                'patient_admission',
                'patient_admission__ward',
                'patient_admission__bed'
            )

            serializer = DeathRecordSerializer(death_records, many=True)
            
            return Response({
                'death_records': serializer.data,
                'count': len(serializer.data),
                'message': 'Death records retrieved successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
class ExtendTimeView(APIView):
    def post(self, request, hosp_id):
        try:
            bed_id = request.data.get('bed_id')
            additional_hours = int(request.data.get('additional_hours'))
            
            if not all([bed_id, additional_hours]):
                return Response(
                    {'error': 'Missing required fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the latest admission for this bed
            admission = PatientAdmission.objects.filter(
                bed_id=bed_id,
                hospital_id=hosp_id,
                status='admitted'
            ).latest('created_at')
            
            # Update occupation_hours and release_time
            admission.occupation_hours += additional_hours
            admission.release_time = admission.release_time + timedelta(hours=additional_hours)
            admission.save()
            
            # Return updated time information
            remaining_time = admission.release_time - timezone.now()
            hours = int(remaining_time.total_seconds() // 3600)
            minutes = int((remaining_time.total_seconds() % 3600) // 60)
            
            return Response({
                'message': 'Time extended successfully',
                'occupation_hours': admission.occupation_hours,
                'remaining_time': f"{hours}h {minutes}m"
            }, status=status.HTTP_200_OK)
            
        except PatientAdmission.DoesNotExist:
            return Response(
                {'error': 'No active admission found for this bed'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    def get(self, request, hosp_id):
        try:
            # Fetch all admissions for the hospital
            admissions = PatientAdmission.objects.filter(hospital=hosp_id)
            
            if not admissions.exists():
                return Response(
                    {'error': 'No admissions found for the specified hospital'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = PatientAdmissionSerializer(admissions, many=True)
            
            return Response(
                {
                    'hospital_id': hosp_id,
                    'admissions': serializer.data,
                    'message': 'Data retrieved successfully'
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )