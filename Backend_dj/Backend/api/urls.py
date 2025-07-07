from django.urls import path
from .views import HospitalRegistrationView, HospitalLoginView


urlpatterns = [
    path('hospital/register/', HospitalRegistrationView.as_view(), name='hospital-registration'),
    path('hospital/login/', HospitalLoginView.as_view(), name='hospital_login')
]