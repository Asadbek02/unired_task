from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Transaction
from datetime import datetime
import json
import random


@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = request.user

        transaction = Transaction(
            user=user,
            amount=data['amount'],
            description=data['description'],
            otp=str(random.randint(100000, 999999))
        )
        transaction.save()
        return JsonResponse({'transaction_id': transaction.id, 'status': transaction.status, 'otp': transaction.otp})


@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def confirm_transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            transaction = Transaction.objects.get(id=data['transaction_id'])
            if transaction.otp == data['otp']:
                transaction.status = 'confirmed'
            else:
                transaction.status = 'failed'
            transaction.save()
            return JsonResponse({'status': transaction.status})
        except Transaction.DoesNotExist:
            return JsonResponse({'message': 'Transaction not found'}, status=404)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def cancel_transaction(request):
    user = request.user
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            if user.is_superuser != 1:
                return JsonResponse({'message': 'You do not have permission for this action.'}, status=403)

            transaction = Transaction.objects.get(id=data['transaction_id'])
            transaction.status = 'cancelled'
            transaction.save()
            return JsonResponse({'status': transaction.status})
        except Transaction.DoesNotExist:
            return JsonResponse({'message': 'Transaction not found'}, status=404)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user)

    if request.method == 'GET':
        status = request.GET.get('status')
        begin_date = request.GET.get('begin_date')
        end_date = request.GET.get('end_date')

        if status:
            transactions = transactions.filter(status=status)

        if begin_date and end_date:
            try:
                begin_date_obj = datetime.strptime(begin_date, '%Y-%m-%d')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

                transactions = transactions.filter(created_at__range=[begin_date_obj, end_date_obj])
            except ValueError:
                return JsonResponse({'message': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)

            transactions = transactions.filter(created_at__range=[begin_date, end_date])

        transactions_list = list(transactions.values())

        if not transactions_list:
            return JsonResponse({'message': 'No transactions found.'}, status=404)

        return JsonResponse(transactions_list, safe=False)



