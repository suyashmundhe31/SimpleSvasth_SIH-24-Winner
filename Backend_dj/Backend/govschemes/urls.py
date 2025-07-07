from django.urls import path
from .views import GovernmentSchemeListCreateAPIView, GovernmentSchemeDetailAPIView

urlpatterns = [
    path('schemes/', GovernmentSchemeListCreateAPIView.as_view(), name='scheme-list-create'),
    path('schemes/<int:pk>/', GovernmentSchemeDetailAPIView.as_view(), name='scheme-detail'),
    
]
