from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from bookings.models import Booking
from .models import Payment, PaymentWebhookLog
from .serializers import PaymentSerializer, PaymentWebhookLogSerializer
import paypalrestsdk
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

# ------------------------------
# Create PayPal Payment (booking_ref in request body)
# ------------------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_paypal_payment(request):
    booking_ref = request.data.get('booking_reference')  # new variable
    if not booking_ref:
        return Response({'error': 'Booking reference is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        booking = Booking.objects.get(booking_reference=booking_ref, user=request.user)

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"{settings.FRONTEND_URL}/payment/success/",
                "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel/"
            },
            "transactions": [{
                "amount": {"total": f"{float(booking.total_amount):.2f}", "currency": "USD"},
                "description": f"Flight booking {booking.booking_reference}",
                "custom": json.dumps({"booking_ref": booking.booking_reference, "user_id": request.user.id})
            }]
        })

        if payment.create():
            db_payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_amount,
                payment_method='paypal',
                paypal_order_id=payment.id,
                status='pending'
            )
            serializer = PaymentSerializer(db_payment)
            return Response(serializer.data)
        else:
            return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)

    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


# ------------------------------
# Execute PayPal Payment
# ------------------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def execute_paypal_payment(request):
    payment_id = request.data.get('payment_id')
    payer_id = request.data.get('payer_id')
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            db_payment = Payment.objects.get(paypal_order_id=payment_id)
            db_payment.status = 'completed'
            db_payment.paypal_payer_id = payer_id
            db_payment.save()
            serializer = PaymentSerializer(db_payment)
            return Response(serializer.data)
        else:
            return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------
# PayPal Webhook
# ------------------------------
@api_view(['POST'])
@csrf_exempt
def paypal_webhook(request):
    serializer = PaymentWebhookLogSerializer(data={
        'payload': request.data,
        'event_type': request.data.get('event_type', 'unknown')
    })
    if serializer.is_valid():
        serializer.save()
    return Response(status=status.HTTP_200_OK)
