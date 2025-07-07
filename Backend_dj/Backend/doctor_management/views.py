from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Doctor, Slot, OPDBooking, WalkInSlot
from .serializers import (
    DoctorSerializer,
    SlotSerializer,
    OPDBookingSerializer,
    WalkInSlotSerializer
)
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Avg
from .models import PatientSymptom, ConsultationRecord, QueuePrediction, ConsultationPredictor
from datetime import datetime


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer


class OPDBookingViewSet(viewsets.ViewSet):
    def list(self, request):
        doctor_id = request.query_params.get('doctor_id')
        date = request.query_params.get('date')

        if doctor_id and date:
            bookings = OPDBooking.objects.filter(doctor_id=doctor_id, date=date)
        else:
            bookings = OPDBooking.objects.all()

        serializer = OPDBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            booking = OPDBooking.objects.get(pk=pk)
            serializer = OPDBookingSerializer(booking)
            return Response(serializer.data)
        except OPDBooking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        try:
            booking = OPDBooking.objects.get(pk=pk)
            serializer = OPDBookingSerializer(booking, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except OPDBooking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk, format=None):
        try:
            booking = OPDBooking.objects.get(pk=pk)
            booking.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except OPDBooking.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, booking_id):
        try:
            booking = OPDBooking.objects.get(booking_id=booking_id)
            booking.patient_name = request.data.get('patient_name')
            booking.is_booked = request.data.get('is_booked', False)
            booking.save()
            return Response({"message": "Booking updated successfully"}, status=status.HTTP_200_OK)
        except OPDBooking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

class WalkInSlotAPIView(viewsets.ModelViewSet):
    queryset = WalkInSlot.objects.all()
    serializer_class = WalkInSlotSerializer


@api_view(['POST', 'GET'])
def manage_walkin(request):
    if request.method == "POST":
        try:
            data = request.data
            doctor_id = data.get("doctor_id")
            patient_name = data.get("patient_name")

            if not doctor_id or not patient_name:
                return Response(
                    {"error": "Doctor and patient name are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if patient is already in the queue for the same day
            today = timezone.now().date()
            existing_patient = WalkInSlot.objects.filter(
                doctor_id=doctor_id, patient_name__iexact=patient_name, date=today
            ).first()

            if existing_patient:
                return Response(
                    {
                        "error": "Patient already in queue",
                        "token_number": existing_patient.token_number,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Retrieve the doctor instance
            doctor = Doctor.objects.get(pk=doctor_id)

            # Create the new WalkInSlot instance
            walkin = WalkInSlot.objects.create(
                doctor=doctor, 
                patient_name=patient_name,
                token_number=WalkInSlot.objects.filter(doctor=doctor, date=today).count() + 1,  # Generate token number
                date=today
            )

            return Response(
                {
                    "message": "Walk-in added successfully",
                    "walkin_id": walkin.walkin_id,
                    "token_number": walkin.token_number,
                },
                status=status.HTTP_201_CREATED,
            )
        except Doctor.DoesNotExist:
            return Response(
                {"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "GET":
        try:
            doctor_id = request.query_params.get("doctor_id")
            department = request.query_params.get("department")
            today = timezone.now().date()

            queryset = WalkInSlot.objects.filter(date=today)

            if doctor_id and doctor_id != 'all':
                queryset = queryset.filter(doctor_id=doctor_id)
            if department and department != 'All':
                queryset = queryset.filter(doctor__department=department)

            walkin_data = [
                {
                    "walkin_id": walkin.walkin_id,
                    "doctor_name": f"Dr. {walkin.doctor.doctor_name}",
                    "patient_name": walkin.patient_name,
                    "token_number": walkin.token_number,
                    "date": walkin.date.strftime("%Y-%m-%d"),
                    "department": walkin.doctor.department,
                }
                for walkin in queryset
            ]
            return Response({"walkins": walkin_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid request method."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def walkin_list(request):
    fetch_all = request.query_params.get('fetch_all', False)
    doctor_id = request.query_params.get('doctor_id')

    if fetch_all:
        walkins = WalkInSlot.objects.all().order_by('-date')
    elif doctor_id:
        walkins = WalkInSlot.objects.filter(doctor_id=doctor_id).order_by('-date')
    else:
        walkins = WalkInSlot.objects.none()

    serializer = WalkInSlotSerializer(walkins, many=True)
    return Response({'walkins': serializer.data}, status=status.HTTP_200_OK)

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def create_checkout_session(request):
    try:
        booking_id = request.data.get('booking_id')
        with transaction.atomic():
            booking = OPDBooking.objects.select_for_update().get(pk=booking_id)
            
            # Check if slot is already booked
            if booking.is_booked:
                return Response(
                    {'error': 'This slot has already been booked'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            doctor = booking.doctor_id
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'unit_amount': doctor.fees * 100,
                        'product_data': {
                            'name': f'Appointment with Dr. {doctor.doctor_name}',
                            'description': f'Appointment on {booking.date} at {booking.start_time}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.FRONTEND_SUCCESS_URL + f'?booking_id={booking_id}&session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=settings.FRONTEND_CANCEL_URL,
                metadata={
                    'booking_id': booking_id,
                    'patient_name': request.data.get('patient_name'),
                }
            )

            # Temporarily mark slot as pending
            booking.is_booked = True
            booking.save()

            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            })

    except OPDBooking.DoesNotExist:
        return Response(
            {'error': 'Booking not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session['metadata']['booking_id']
        patient_name = session['metadata']['patient_name']

        try:
            with transaction.atomic():
                booking = OPDBooking.objects.select_for_update().get(pk=booking_id)
                booking.patient_name = patient_name
                booking.save()

                # Create payment record
                Payment.objects.create(
                    booking=booking,
                    stripe_payment_id=session.payment_intent,
                    amount=session.amount_total,
                    status='completed'
                )

        except OPDBooking.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def refund_payment(request):
    try:
        booking_id = request.data.get('booking_id')
        with transaction.atomic():
            booking = OPDBooking.objects.select_for_update().get(pk=booking_id)
            payment = Payment.objects.get(booking=booking)

            if payment.refunded:
                return Response(
                    {'error': 'Payment has already been refunded'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create refund in Stripe
            refund = stripe.Refund.create(
                payment_intent=payment.stripe_payment_id,
                reason='requested_by_customer'
            )

            if refund.status == 'succeeded':
                # Update payment record
                payment.refunded = True
                payment.save()

                # Update booking status
                booking.is_booked = False
                booking.patient_name = None
                booking.save()

                return Response({'message': 'Refund processed successfully'})
            else:
                raise Exception('Refund failed')

    except (OPDBooking.DoesNotExist, Payment.DoesNotExist):
        return Response(
            {'error': 'Booking or payment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def verify_booking_status(request, booking_id):
    try:
        booking = OPDBooking.objects.get(pk=booking_id)
        payment = Payment.objects.filter(booking=booking).first()
        
        return Response({
            'is_booked': booking.is_booked,
            'patient_name': booking.patient_name,
            'payment_status': payment.status if payment else 'no_payment',
            'refunded': payment.refunded if payment else False
        })
    except OPDBooking.DoesNotExist:
        return Response(
            {'error': 'Booking not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    


predictor = ConsultationPredictor()

@api_view(['POST'])
def predict_consultation_time(request):
    try:
        data = request.data
        doctor_id = data.get('doctor_id')
        patient_name = data.get('patient_name')
        symptoms = data.get('symptoms', [])
        
        if not all([doctor_id, patient_name, symptoms]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get doctor's current queue length
        current_queue = QueuePrediction.objects.filter(
            doctor_id=doctor_id,
            actual_time__isnull=True
        ).count()
        
        # Predict consultation time
        prediction_data = {
            'age': data.get('age', 30),
            'gender': data.get('gender', 'M'),
            'symptom_severity': max(s['severity'] for s in symptoms),
            'previous_visits': data.get('previous_visits', 0),
            'is_emergency': data.get('is_emergency', False)
        }
        
        predicted_time = predictor.predict_time(prediction_data)
        
        # Create queue prediction record
        prediction = QueuePrediction.objects.create(
            patient_name=patient_name,
            predicted_time=predicted_time,
            doctor_id=doctor_id,
            token_number=current_queue + 1
        )
        
        # Add symptoms to prediction
        for symptom_data in symptoms:
            symptom, _ = PatientSymptom.objects.get_or_create(
                name=symptom_data['name'],
                severity=symptom_data['severity']
            )
            prediction.symptoms.add(symptom)
        
        # Calculate estimated wait time based on queue
        queue_predictions = QueuePrediction.objects.filter(
            doctor_id=doctor_id,
            actual_time__isnull=True,
            token_number__lt=prediction.token_number
        )
        
        total_wait_time = sum(p.predicted_time for p in queue_predictions)
        
        return Response({
            'token_number': prediction.token_number,
            'predicted_consultation_time': predicted_time,
            'estimated_wait_time': total_wait_time,
            'queue_position': current_queue + 1
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_queue_status(request):
    doctor_id = request.query_params.get('doctor_id')
    if not doctor_id:
        return Response({
            'error': 'Doctor ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get current queue
    queue = QueuePrediction.objects.filter(
        doctor_id=doctor_id,
        actual_time__isnull=True
    ).order_by('token_number')
    
    queue_data = []
    for prediction in queue:
        symptoms = [
            {'name': s.name, 'severity': s.severity}
            for s in prediction.symptoms.all()
        ]
        
        queue_data.append({
            'token_number': prediction.token_number,
            'patient_name': prediction.patient_name,
            'predicted_time': prediction.predicted_time,
            'symptoms': symptoms,
            'created_at': prediction.created_at
        })
    
    # Get average accuracy of predictions
    completed = ConsultationRecord.objects.filter(doctor_id=doctor_id)
    if completed.exists():
        avg_accuracy = completed.aggregate(
            avg_accuracy=Avg(
                100 * (1 - abs(F('consultation_time') - F('predicted_time')) / F('consultation_time'))
            )
        )['avg_accuracy']
    else:
        avg_accuracy = None
    
    return Response({
        'queue': queue_data,
        'prediction_accuracy': avg_accuracy,
        'queue_length': len(queue_data)
    })