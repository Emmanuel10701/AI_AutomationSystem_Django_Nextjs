import json
import random
import string
import paypalrestsdk
# --- CORRECTED LANGCHAIN IMPORTS ---
# Tool and SystemMessage have moved to core
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage
# initialize_agent is deprecated and removed from modern chains.
# We'll import the recommended replacement: create_conversational_agent
# Note: For now, we'll import initialize_agent from an older path for compatibility,
# but the modern approach uses LangGraph or create_conversational_agent.
# Since your code uses 'initialize_agent', we'll try the likely current location in the main package.
from langchain.agents import initialize_agent # Check this first. If it fails, you may need a different agent type.
from langchain.memory import ConversationBufferMemory # This path is usually still correctfrom langchain_community.chat_models import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent
# --- END CORRECTED LANGCHAIN IMPORTS ---

from django.conf import settings
from django.db.models import Q
from users.models import User
from flights.models import Flight, Airport
from bookings.models import Booking
from payments.models import Payment
from .knowledge_base import KnowledgeBase

# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class TravelAIAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7
        )
        
        # NOTE: LangChain recommends 'return_messages=True' for agents
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.knowledge_base = KnowledgeBase()
        self.tools = self._setup_tools()
        self.agent_executor = self._create_agent()
    
    def _setup_tools(self):
        return [
            Tool(
                name="SearchFlights",
                func=self.search_flights,
                description="Search for available flights between cities or airports"
            ),
            Tool(
                name="CheckCompanyPolicies",
                func=self.check_company_policies,
                description="Check company policies, baggage rules, cancellation policies, etc."
            ),
            Tool(
                name="InitiateBooking",
                func=self.initiate_booking,
                description="Start the booking process for a flight with passenger details"
            ),
            Tool(
                name="CreatePayPalPayment",
                func=self.create_paypal_payment,
                description="Create a PayPal payment for a pending booking"
            ),
            Tool(
                name="CheckBookingStatus",
                func=self.check_booking_status,
                description="Check the status of existing bookings"
            ),
            Tool(
                name="GetUserBookings",
                func=self.get_user_bookings,
                description="Get all bookings for the current user"
            ),
            Tool(
                name="QueryKnowledgeBase",
                func=self.query_knowledge_base,
                description="Query company knowledge base for detailed information"
            )
        ]
    
    def search_flights(self, query):
        try:
            # Enhanced query parsing
            query_lower = query.lower()
            departure = None
            arrival = None
            
            if ' to ' in query_lower:
                parts = query_lower.split(' to ')
                departure = parts[0].strip()
                arrival = parts[1].strip()
            elif ' from ' in query_lower:
                parts = query_lower.split(' from ')
                arrival = parts[0].strip()
                departure = parts[1].strip()
            
            flights = Flight.objects.filter(available_seats__gt=0)
            
            if departure:
                flights = flights.filter(
                    Q(departure_airport__city__icontains=departure) |
                    Q(departure_airport__code__icontains=departure)
                )
            if arrival:
                flights = flights.filter(
                    Q(arrival_airport__city__icontains=arrival) |
                    Q(arrival_airport__code__icontains=arrival)
                )
            
            flights = flights.select_related('departure_airport', 'arrival_airport')[:15]
            
            results = []
            for flight in flights:
                duration = flight.arrival_time - flight.departure_time
                hours = duration.seconds // 3600
                minutes = (duration.seconds % 3600) // 60
                
                results.append({
                    'id': flight.id,
                    'flight_number': flight.flight_number,
                    'airline': flight.airline,
                    'departure': {
                        'airport': flight.departure_airport.code,
                        'city': flight.departure_airport.city,
                        'time': flight.departure_time.strftime("%Y-%m-%d %H:%M")
                    },
                    'arrival': {
                        'airport': flight.arrival_airport.code,
                        'city': flight.arrival_airport.city,
                        'time': flight.arrival_time.strftime("%Y-%m-%d %H:%M")
                    },
                    'duration': f"{hours}h {minutes}m",
                    'price': float(flight.price),
                    'available_seats': flight.available_seats,
                    'aircraft_type': flight.aircraft_type or 'Not specified'
                })
            
            return json.dumps(results, default=str)
        except Exception as e:
            return f"Error searching flights: {str(e)}"
    
    def check_company_policies(self, query):
        try:
            # Use knowledge base to answer policy questions
            response = self.knowledge_base.query_knowledge_base(query)
            return response
        except Exception as e:
            return f"Error checking policies: {str(e)}"
    
    def query_knowledge_base(self, query):
        try:
            return self.knowledge_base.query_knowledge_base(query)
        except Exception as e:
            return f"Error querying knowledge base: {str(e)}"
    
    def initiate_booking(self, booking_data):
        try:
            data = json.loads(booking_data)
            flight = Flight.objects.get(id=data['flight_id'])
            user = User.objects.get(id=data['user_id'])
            
            if flight.available_seats < len(data['passengers']):
                return json.dumps({
                    'success': False,
                    'error': f'Only {flight.available_seats} seats available'
                })
            
            booking = Booking.objects.create(
                user=user,
                flight=flight,
                booking_reference=self._generate_booking_reference(),
                status='pending_payment',
                passengers=data['passengers'],
                total_amount=flight.price * len(data['passengers'])
            )
            
            return json.dumps({
                'success': True,
                'booking_id': booking.id,
                'booking_reference': booking.booking_reference,
                'amount': float(booking.total_amount),
                'passengers': len(data['passengers']),
                'next_step': 'Please proceed with payment to confirm your booking.',
                'message': f'Booking {booking.booking_reference} created successfully. Ready for payment.'
            })
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def create_paypal_payment(self, booking_data):
        try:
            data = json.loads(booking_data)
            booking = Booking.objects.get(
                id=data['booking_id'],
                user__id=data['user_id'],
                status='pending_payment'
            )
            
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
                        "user_id": data['user_id']
                    })
                }]
            })
            
            if payment.create():
                Payment.objects.create(
                    booking=booking,
                    amount=booking.total_amount,
                    payment_method='paypal',
                    paypal_order_id=payment.id,
                    status='pending'
                )
                
                approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
                
                return json.dumps({
                    'success': True,
                    'payment_id': payment.id,
                    'approval_url': approval_url,
                    'booking_reference': booking.booking_reference,
                    'amount': float(booking.total_amount),
                    'message': 'PayPal payment created. Please complete the payment.'
                })
            else:
                return json.dumps({
                    'success': False,
                    'error': str(payment.error)
                })
                
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def check_booking_status(self, booking_ref):
        try:
            booking = Booking.objects.get(booking_reference=booking_ref)
            payment = Payment.objects.filter(booking=booking).first()
            
            result = {
                'booking_reference': booking.booking_reference,
                'status': booking.status,
                'flight': f"{booking.flight.departure_airport.city} to {booking.flight.arrival_airport.city}",
                'departure_time': booking.flight.departure_time.strftime("%Y-%m-%d %H:%M"),
                'passengers': len(booking.passengers),
                'total_amount': float(booking.total_amount)
            }
            
            if payment:
                result['payment_status'] = payment.status
                result['payment_method'] = payment.payment_method
            
            return json.dumps(result)
        except Booking.DoesNotExist:
            return json.dumps({'error': 'Booking not found'})
        except Exception as e:
            return json.dumps({'error': str(e)})
    
    def get_user_bookings(self, user_id):
        try:
            bookings = Booking.objects.filter(user__id=user_id).select_related('flight').order_by('-created_at')[:10]
            
            results = []
            for booking in bookings:
                results.append({
                    'booking_reference': booking.booking_reference,
                    'status': booking.status,
                    'flight': f"{booking.flight.departure_airport.city} to {booking.flight.arrival_airport.city}",
                    'departure_time': booking.flight.departure_time.strftime("%Y-%m-%d %H:%M"),
                    'passengers': len(booking.passengers),
                    'total_amount': float(booking.total_amount),
                    'created_at': booking.created_at.strftime("%Y-%m-%d %H:%M")
                })
            
            return json.dumps(results)
        except Exception as e:
            return json.dumps({'error': f"Error retrieving bookings: {str(e)}"})
    
    def _generate_booking_reference(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def _create_agent(self):
        system_message = SystemMessage(
            content="""You are a helpful travel assistant for a flight booking platform. 
            Help users search for flights, book tickets, check company policies, and complete payments. 
            Use the knowledge base to provide accurate information about company policies, baggage rules, and flight details.
            Be friendly, informative, and guide users through the booking process step by step.
            When users want to book a flight, ask for passenger details and then initiate the booking.
            After booking is created, offer to proceed with PayPal payment."""
        )
        
        try:
            return initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent="chat-conversational-react-description",
                verbose=True,
                memory=self.memory,
                handle_parsing_errors=True,
                agent_kwargs={
                    "system_message": system_message,
                }
            )
        except Exception as e:
            # Fallback if agent initialization fails
            print(f"Agent initialization failed: {e}")
            return None
    
    def process_message(self, user_message, user_id=None):
        try:
            if not self.agent_executor:
                return "I apologize, but the AI assistant is currently unavailable. Please try again later."
                
            context_message = f"User ID: {user_id}. {user_message}"
            
            response = self.agent_executor.run(
                input=context_message
            )
            return response
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or contact support."