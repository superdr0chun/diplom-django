# diplom/api/views.py
from django.contrib.auth import authenticate, login as auth_login
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import CustomUser

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'Регистрация прошла успешно!',
            'user_id': user.id,
            'username': user.username,
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'success': False,
            'error': 'Ошибка регистрации',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login(request):
    print("Login attempt with data:", request.data)
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'success': False,
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    print("User authenticated:", user)

    if user is not None:
        auth_login(request, user)
        return Response({
            'success': True,
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
        }, status=status.HTTP_200_OK)
    else:
        print("Authentication failed for user:", username)
        return Response({
            'success': False,
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)