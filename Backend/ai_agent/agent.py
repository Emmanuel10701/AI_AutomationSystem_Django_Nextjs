import json
import random
import string
import paypalrestsdk
from django.conf import settings
from django.db.models import Q
from users.models import User
from flights.models import Flight
from bookings.models import Booking
from payments.models import Payment
from .knowledge_base import KnowledgeBase

# Modern LangChain imports
try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langchain_core.tools import Tool
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.memory import ConversationBufferMemory
    
    # Use the correct import for Google Generative AI
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        from langchain_community.chat_models import ChatGoogleGenerativeAI
        
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain imports successful")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"⚠️ LangChain not available: {e}")

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

class TravelAIAgent:
    def __init__(self):
        """Initialize AI agent with Gemini Flash 2.5"""
        self.knowledge_base = KnowledgeBase()
        self.agent_executor = None
        self.casual_chat_llm = None  # Separate LLM for casual chat
        
        print(f"🔧 Initializing AI Agent with Gemini Flash 2.5...")
        print(f"   GOOGLE_API_KEY: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Missing'}")
        print(f"   GEMINI_MODEL: {getattr(settings, 'GEMINI_MODEL', 'Not set')}")

        if LANGCHAIN_AVAILABLE and settings.GOOGLE_API_KEY:
            try:
                # Initialize Gemini Flash 2.5 explicitly for main agent
                self.llm = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,  # This should be 'gemini-2.0-flash-exp'
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0.7,
                )
                
                # Initialize separate LLM for casual chat with higher temperature
                self.casual_chat_llm = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0.9,  # Higher temperature for more creative responses
                )
                
                print(f"✅ Gemini Model: {settings.GEMINI_MODEL}")

                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True,
                )

                self.tools = self._setup_tools()
                self.agent_executor = self._create_modern_agent()
                print("✅ Modern LangChain agent with Gemini Flash 2.5 initialized!")
                
            except Exception as e:
                print(f"❌ Failed to initialize LangChain agent: {e}")
                self.agent_executor = None
        else:
            print("⚠️ Using simple rule-based agent (LangChain not available or API key missing)")
            self.agent_executor = None

    def _setup_tools(self):
        """Define the tools available to the AI agent."""
        return [
            Tool(
                name="SearchFlights",
                func=self.search_flights,
                description="Search for available flights between cities. Input should be a query like 'flights from New York to Los Angeles'."
            ),
            Tool(
                name="CheckCompanyPolicies",
                func=self.check_company_policies,
                description="Get information about company policies including baggage rules, cancellation policies, check-in requirements."
            ),
            Tool(
                name="InitiateBooking",
                func=self.initiate_booking,
                description="Start a booking process for a flight. Requires flight_id and passenger details in JSON format."
            ),
            Tool(
                name="CreatePayPalPayment",
                func=self.create_paypal_payment,
                description="Create a PayPal payment for an existing booking. Requires booking_id and user_id in JSON format."
            ),
            Tool(
                name="CheckBookingStatus",
                func=self.check_booking_status,
                description="Check the status of a booking using booking reference number."
            ),
            Tool(
                name="GetUserBookings",
                func=self.get_user_bookings,
                description="Get all bookings for a specific user by user_id."
            ),
            Tool(
                name="QueryKnowledgeBase",
                func=self.query_knowledge_base,
                description="Search for detailed information in the company knowledge base about policies, procedures, or general information."
            ),
        ]

    def _create_modern_agent(self):
        """Build a modern LangChain agent with Gemini Flash 2.5"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a friendly, knowledgeable travel assistant for a flight booking platform. 
                You help users with:
                - Finding and searching for flights
                - Understanding company policies (baggage, cancellation, check-in)
                - Booking flights and managing reservations
                - Processing payments via PayPal
                - Checking booking status and user history
                
                Always be helpful, patient, and provide accurate information. Guide users through processes step by step.
                Use the available tools to get real-time information when needed.
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            agent = create_tool_calling_agent(
                llm=self.llm,
                prompt=prompt,
                tools=self.tools,
            )

            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                return_intermediate_steps=False,
            )
            
            return agent_executor
            
        except Exception as e:
            print(f"❌ Failed to create modern agent: {e}")
            return None

    # ---------- Casual Chat Function ----------
    def casual_chat(self, message, chat_history=None):
        """
        Have a casual conversation with the AI without using travel-specific tools.
        Perfect for general chatting, questions, or casual conversation.
        """
        if not self.casual_chat_llm:
            return "I'd love to chat, but the AI chat system isn't available right now. Please check the configuration."
        
        try:
            # Create a casual chat prompt
            casual_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a friendly, helpful, and engaging AI assistant. 
                You can have casual conversations, answer general questions, tell jokes, 
                discuss various topics, and be generally conversational.
                
                Keep your responses friendly, natural, and engaging. You can be witty, 
                humorous, and show personality while remaining helpful and appropriate.
                
                If someone asks travel-related questions, you can answer generally but 
                suggest they use the travel-specific features for detailed assistance.
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ])
            
            # Prepare the messages
            messages = casual_prompt.format_messages(
                input=message,
                chat_history=chat_history or []
            )
            
            # Get response from the casual chat LLM
            response = self.casual_chat_llm.invoke(messages)
            return response.content
            
        except Exception as e:
            print(f"❌ Error in casual chat: {e}")
            return "Sorry, I'm having trouble chatting right now. Let's try again!"

    # ---------- Tool Functions (Keep all your existing tool functions exactly as they were) ----------
    def search_flights(self, query):
        try:
            query_lower = query.lower()
            departure, arrival = None, None

            if " to " in query_lower:
                parts = query_lower.split(" to ")
                departure, arrival = parts[0].strip(), parts[1].strip()
            elif " from " in query_lower:
                parts = query_lower.split(" from ")
                arrival, departure = parts[0].strip(), parts[1].strip()

            flights = Flight.objects.filter(available_seats__gt=0)
            if departure:
                flights = flights.filter(
                    Q(departure_airport__city__icontains=departure)
                    | Q(departure_airport__code__icontains=departure)
                )
            if arrival:
                flights = flights.filter(
                    Q(arrival_airport__city__icontains=arrival)
                    | Q(arrival_airport__code__icontains=arrival)
                )

            flights = flights.select_related("departure_airport", "arrival_airport")[:15]

            results = []
            for flight in flights:
                duration = flight.arrival_time - flight.departure_time
                hours = duration.seconds // 3600
                minutes = (duration.seconds % 3600) // 60

                results.append({
                    "flight_number": flight.flight_number,
                    "airline": flight.airline,
                    "departure": {
                        "airport": flight.departure_airport.code,
                        "city": flight.departure_airport.city,
                        "time": flight.departure_time.strftime("%Y-%m-%d %H:%M"),
                    },
                    "arrival": {
                        "airport": flight.arrival_airport.code,
                        "city": flight.arrival_airport.city,
                        "time": flight.arrival_time.strftime("%Y-%m-%d %H:%M"),
                    },
                    "duration": f"{hours}h {minutes}m",
                    "price": float(flight.price),
                    "available_seats": flight.available_seats,
                    "aircraft_type": flight.aircraft_type or "Not specified",
                })
            return json.dumps(results, default=str)

        except Exception as e:
            return f"Error searching flights: {str(e)}"

    def check_company_policies(self, query):
        try:
            return self.knowledge_base.query_knowledge_base(query)
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
            flight = Flight.objects.get(id=data["flight_id"])
            user = User.objects.get(id=data["user_id"])

            if flight.available_seats < len(data["passengers"]):
                return json.dumps({
                    "success": False,
                    "error": f"Only {flight.available_seats} seats available"
                })

            booking = Booking.objects.create(
                user=user,
                flight=flight,
                booking_reference=self._generate_booking_reference(),
                status="pending_payment",
                passengers=data["passengers"],
                total_amount=flight.price * len(data["passengers"]),
            )

            return json.dumps({
                "success": True,
                "booking_reference": booking.booking_reference,
                "amount": float(booking.total_amount),
                "passengers": len(data["passengers"]),
                "next_step": "Please proceed with payment to confirm your booking.",
                "message": f"Booking {booking.booking_reference} created successfully.",
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    def create_paypal_payment(self, booking_data):
        try:
            data = json.loads(booking_data)
            booking = Booking.objects.get(
                id=data["booking_id"],
                user__id=data["user_id"],
                status="pending_payment",
            )

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": f"{settings.FRONTEND_URL}/payment/success/",
                    "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel/",
                },
                "transactions": [{
                    "amount": {
                        "total": f"{float(booking.total_amount):.2f}",
                        "currency": "USD",
                    },
                    "description": f"Flight booking {booking.booking_reference}",
                    "custom": json.dumps({"user_id": data["user_id"]}),
                }],
            })

            if payment.create():
                Payment.objects.create(
                    booking=booking,
                    amount=booking.total_amount,
                    payment_method="paypal",
                    paypal_order_id=payment.id,
                    status="pending",
                )

                approval_url = next(
                    link.href for link in payment.links if link.rel == "approval_url"
                )

                return json.dumps({
                    "success": True,
                    "payment_id": payment.id,
                    "approval_url": approval_url,
                    "booking_reference": booking.booking_reference,
                    "amount": float(booking.total_amount),
                    "message": "PayPal payment created successfully.",
                })
            else:
                return json.dumps({"success": False, "error": str(payment.error)})

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    def check_booking_status(self, booking_ref):
        try:
            booking = Booking.objects.get(booking_reference=booking_ref)
            payment = Payment.objects.filter(booking=booking).first()

            result = {
                "booking_reference": booking.booking_reference,
                "status": booking.status,
                "flight": f"{booking.flight.departure_airport.city} → {booking.flight.arrival_airport.city}",
                "departure_time": booking.flight.departure_time.strftime("%Y-%m-%d %H:%M"),
                "passengers": len(booking.passengers),
                "total_amount": float(booking.total_amount),
            }

            if payment:
                result["payment_status"] = payment.status
                result["payment_method"] = payment.payment_method

            return json.dumps(result)
        except Booking.DoesNotExist:
            return json.dumps({"error": "Booking not found"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_user_bookings(self, user_id):
        try:
            bookings = Booking.objects.filter(user__id=user_id).select_related("flight").order_by("-created_at")[:10]
            results = [{
                "booking_reference": b.booking_reference,
                "status": b.status,
                "flight": f"{b.flight.departure_airport.city} → {b.flight.arrival_airport.city}",
                "departure_time": b.flight.departure_time.strftime("%Y-%m-%d %H:%M"),
                "passengers": len(b.passengers),
                "total_amount": float(b.total_amount),
                "created_at": b.created_at.strftime("%Y-%m-%d %H:%M"),
            } for b in bookings]
            return json.dumps(results)
        except Exception as e:
            return json.dumps({"error": f"Error retrieving bookings: {str(e)}"})

    def _generate_booking_reference(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def process_message(self, user_message, user_id=None):
        """Process user messages with Gemini Flash 2.5"""
        if not self.agent_executor:
            return self._simple_process_message(user_message, user_id)

        try:
            response = self.agent_executor.invoke({
                "input": f"User (ID: {user_id}) says: {user_message}",
                "chat_history": self.memory.chat_memory.messages,
            })
            return response.get("output", "I apologize, but I couldn't process your request. Please try again.")
        except Exception as e:
            print(f"⚠️ Agent error: {e}")
            return self._simple_process_message(user_message, user_id)

    def _simple_process_message(self, user_message, user_id=None):
        """Fallback when LangChain is not available"""
        text = user_message.lower()

        if any(k in text for k in ["flight", "travel", "search", "fly"]):
            result = self.search_flights(user_message)
            return f"I found these flights for you:\n{result}" if "Error" not in result else "Sorry, I couldn't search flights right now."
        elif any(k in text for k in ["policy", "baggage", "cancellation", "check-in"]):
            return self.knowledge_base.query_knowledge_base(user_message)
        elif any(k in text for k in ["book", "reserve", "buy ticket"]):
            return "I can help you book a flight! Please tell me your departure city, destination, and number of passengers."
        elif any(k in text for k in ["status", "my booking", "bookings"]):
            return self.get_user_bookings(user_id) if user_id else "Please provide your booking reference to check your status."
        else:
            return "I'm here to help with your travel needs! You can ask me about flights, bookings, policies, or payments."