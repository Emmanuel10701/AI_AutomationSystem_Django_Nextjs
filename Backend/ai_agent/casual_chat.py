import os
import sys
import django

# Setup Django environment
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    django.setup()
    print("✅ Django setup successful!")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.conf import settings

def direct_gemini_chat():
    """Direct chat using Gemini API without LangChain"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Create the model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("🤖 GEMINI CHAT - READY TO TALK!")
        print("=" * 40)
        print("Just type your messages and press Enter")
        print("Type 'quit' to exit")
        print("=" * 40)
        
        chat_history = []
        
        while True:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit command
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("🤖 AI: Goodbye! Thanks for chatting! 👋")
                break
                
            # Skip empty input
            if not user_input:
                continue
            
            try:
                # Generate response
                response = model.generate_content(user_input)
                print(f"🤖 AI: {response.text}")
                
                # Store in history
                chat_history.append(f"You: {user_input}")
                chat_history.append(f"AI: {response.text}")
                
                # Limit history
                if len(chat_history) > 20:
                    chat_history = chat_history[-20:]
                    
            except Exception as e:
                print(f"🤖 AI: Sorry, I encountered an error: {e}")
                
    except ImportError:
        print("❌ google-generativeai package not installed.")
        print("💡 Install it with: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Failed to setup Gemini: {e}")

if __name__ == "__main__":
    direct_gemini_chat()