import paypalrestsdk
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from bookings.models import Booking
from flights.models import Flight
from .models import Payment, PaymentWebhookLog

# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_paypal_payment(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
        
        if booking.status != 'pending_payment':
            return Response(
                {'error': 'Booking is not in payment pending state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{settings.FRONTEND_URL}/payment/success/",
                "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel/"
            },
            "transactions": [{
                "amount": {
                    "total": f"{float(booking.total_amount):.2f}",
                    "currency": "USD"
                },
                "description": f"Flight booking {booking.booking_reference}",
                "custom": json.dumps({
                    "booking_id": booking.id,
                    "user_id": request.user.id
                })
            }]
        })
        
        if payment.create():
            # Store payment information
            Payment.objects.create(
                booking=booking,
                amount=booking.total_amount,
                payment_method='paypal',
                paypal_order_id=payment.id,
                status='pending'
            )
            
            # Find approval URL
            approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
            
            return Response({
                'payment_id': payment.id,
                'approval_url': approval_url,
                'booking_reference': booking.booking_reference,
                'amount': float(booking.total_amount)
            })
        else:
            return Response(
                {'error': payment.error},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Booking.DoesNotExist:
        return Response(
            {'error': 'Booking not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def execute_paypal_payment(request):
    try:
        payment_id = request.data.get('payment_id')
        payer_id = request.data.get('payer_id')
        
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Update booking and payment status
            db_payment = Payment.objects.get(paypal_order_id=payment_id)
            db_payment.status = 'completed'
            db_payment.paypal_payer_id = payer_id
            db_payment.save()
            
            booking = db_payment.booking
            booking.status = 'confirmed'
            booking.save()
            
            # Update flight seats
            flight = booking.flight
            flight.available_seats -= len(booking.passengers)
            flight.save()
            
            return Response({
                'success': True,
                'booking_reference': booking.booking_reference,
                'status': 'confirmed',
                'message': 'Payment completed successfully!'
            })
        else:
            return Response(
                {'error': payment.error},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@csrf_exempt
def paypal_webhook(request):
    try:
        # Log webhook payload
        webhook_log = PaymentWebhookLog.objects.create(
            payload=request.data,
            event_type=request.data.get('event_type', 'unknown')
        )
        
        event_type = request.data.get('event_type')
        
        if event_type == 'PAYMENT.SALE.COMPLETED':
            resource = request.data.get('resource', {})
            payment_id = resource.get('parent_payment')
            
            try:
                payment = Payment.objects.get(paypal_order_id=payment_id)
                payment.status = 'completed'
                payment.save()
                
                booking = payment.booking
                booking.status = 'confirmed'
                booking.save()
                
            except Payment.DoesNotExist:
                pass
        
        elif event_type == 'PAYMENT.SALE.REFUNDED':
            resource = request.data.get('resource', {})
            payment_id = resource.get('parent_payment')
            
            try:
                payment = Payment.objects.get(paypal_order_id=payment_id)
                payment.status = 'refunded'
                payment.save()
                
                booking = payment.booking
                booking.status = 'cancelled'
                booking.save()
                
            except Payment.DoesNotExist:
                pass
        
        return Response(status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )