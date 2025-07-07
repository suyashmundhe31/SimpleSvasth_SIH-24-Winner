# urls.py
from django.urls import path
from .views import WardAddView, WardListView, BedStatusUpdateView, BedBookingView , WardBedDeleteView, PatientAdmissionView, PatientDischargeView, DeathRecordView, ExtendTimeView

from . import views


urlpatterns = [
    # path('ward/add/', WardAddView.as_view(), name='ward-add'),
    # path('ward/list/', WardListView.as_view(), name='ward-list'),
    path('ward/list/<int:hosp_id>/', WardListView.as_view()),
    path('ward/add/<int:hosp_id>/', WardAddView.as_view()),
    path('ward/update-bed-status/<int:hosp_id>/', BedStatusUpdateView.as_view(), name='update-bed-status'),
    path('bookings/create/<int:hospital_id>/', BedBookingView.as_view(), name='booking-create'),
    path('bookings/<int:booking_id>/approve/', BedBookingView.as_view(), name='approve-booking'),
    path('bookings/<int:booking_id>/', BedBookingView.as_view(), name='booking-detail'),
    path('bookings/<int:booking_id>/<str:action>/', BedBookingView.as_view(), name='booking-action'),
    path('bookings/<int:booking_id>/approve/', BedBookingView.as_view(), name='approve-booking'),
    path('ward/delete-bed/<int:hosp_id>/', WardBedDeleteView.as_view(), name='ward-bed-delete'),
    path('patient-admission/<int:hosp_id>/', PatientAdmissionView.as_view(), name='patient-admission'),
    path('discharge/<int:hosp_id>/', PatientDischargeView.as_view(), name='patient-discharge'),
    path('death-record/<int:hosp_id>/', DeathRecordView.as_view(), name='death-record'),
    path('extend-time/<int:hosp_id>/', ExtendTimeView.as_view(), name='extend-time'),
    
    # path('bed_management/ward/update/<int:hosp_id>/', BedUpdateView.as_view(), name='ward-update'),
]