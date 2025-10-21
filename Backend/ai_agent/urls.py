from django.urls import path
from .views import chat_with_agent, get_company_policies

urlpatterns = [
    path('chat/', chat_with_agent, name='ai-chat'),
    path('policies/', get_company_policies, name='company-policies'),
]