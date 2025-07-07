from django.urls import path, include
from . import views

urlpatterns = [
    path('users/<int:id>/', views.user_login, name='user_detail'),  # Correct pattern for a user ID
    path('users/register/', views.register_user, name='register_user'),
    path('users/login/', views.user_login, name='user_login'),
    # Include any other URLs for other views or viewsets
]
