from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .agent import TravelAIAgent

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chat_with_agent(request):
    user_message = request.data.get('message', '')
    user_id = request.user.id
    
    if not user_message:
        return Response({'error': 'Message is required'}, status=400)
    
    try:
        agent = TravelAIAgent()
        response = agent.process_message(user_message, user_id)
        
        return Response({'response': response})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_company_policies(request):
    category = request.GET.get('category')
    
    try:
        agent = TravelAIAgent()
        policies = agent.knowledge_base.get_company_policies(category)
        return Response({'policies': policies})
    except Exception as e:
        return Response({'error': str(e)}, status=500)