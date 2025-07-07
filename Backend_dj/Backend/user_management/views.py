from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from .models import User
from .serializers import UserRegistrationSerializer
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, get_object_or_404

# Register User view
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        phone_no = request.data.get('phone_no')
        username = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if the phone number already exists
        if User.objects.filter(phone_no=phone_no).exists():
            return Response({'message': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the user
        user = User.objects.create_user(username=username, phone_no=phone_no, email=email, password=password)
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    
    return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


# Login User view
@csrf_exempt
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_no = data.get('phone_no')
        password = data.get('password')
        
        # Authenticate the user
        user = authenticate(request, phone_no=phone_no, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Login successful', 
                'username': user.username,
                'phone_no': user.phone_no,  # Include phone_no
                'email': user.email  # Include email
            })
        else:
            return Response({'message': 'Invalid phone number or password'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

def user_detail(request, id):
    user = get_object_or_404(User, pk=id)  # Retrieve the user with the given ID
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)  # Bind the form with the existing user data
        if form.is_valid():
            form.save()  # Save the updated user data
            return redirect('user_detail', id=user.id)  # Redirect to the updated user's detail page
    else:
        form = UserForm(instance=user)  # Initialize the form with the existing user data

    return render(request, 'user_detail.html', {'user': user, 'form': form})

