from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

import json

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = User(
            fullname=data['fullname'],
            email=data['email'],
            password=make_password(data['password'])
        )
        user.save()
        return JsonResponse({'message': 'User registered successfully'})

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            user = User.objects.get(email=data['email'])
            if check_password(data['password'], user.password):

                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return JsonResponse({'message': 'Invalid credentials'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=404)
