"""
AI Chatbot Views - Web Chat Interface
Uses TravelAdvisor service (same as Telegram bot)
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
import json
import uuid
from .models import ChatMessage
import logging

logger = logging.getLogger(__name__)

# Note: genai configuration and model initialization are done inside the
# request handler to allow graceful failure when the API key is missing
# or the external service returns an error.

def ai_chat_view(request):
    """Main AI chat interface - accessible to all users"""
    return render(request, 'ai_chatbot/chat.html')

@csrf_exempt
def ai_chat_api(request):
    """API endpoint for AI chat - uses TravelAdvisor service like Telegram bot"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            session_id = data.get('session_id', str(uuid.uuid4()))

            if not user_message:
                return JsonResponse({'error': 'Message is required'}, status=400)

            # Initialize TravelAdvisor (same as Telegram bot)
            from .services import TravelAdvisor
            
            try:
                advisor = TravelAdvisor()
                # Get AI response using TravelAdvisor service
                ai_response = advisor.get_advice(user_message, include_tours=True)
                
            except ValueError as ve:
                # API key not configured
                logger.error(f"TravelAdvisor initialization error: {ve}")
                return JsonResponse({'error': 'AI service not configured'}, status=503)
                
            except Exception as gen_e:
                # Gemini API error
                logger.exception('Error calling TravelAdvisor')
                ai_response = 'Xin lỗi, AI hiện không khả dụng. Vui lòng thử lại sau.'

            # Save to database (best-effort)
            try:
                user = request.user if request.user.is_authenticated else None
                ChatMessage.objects.create(
                    user=user,
                    session_id=session_id,
                    message=user_message,
                    response=ai_response,
                    is_ai_response=True
                )
            except Exception:
                logger.exception('Failed to save ChatMessage')

            return JsonResponse({
                'response': ai_response,
                'session_id': session_id
            })

        except Exception as e:
            logger.exception('Unexpected error in ai_chat_api')
            return JsonResponse({'error': 'Unexpected server error'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def chat_history_api(request):
    """API endpoint to fetch chat history - PRIVATE PER USER"""
    if request.method == 'GET':
        session_id = request.GET.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'session_id is required'}, status=400)
        
        try:
            # PRIVACY FIX: Filter by user OR session_id for anonymous
            if request.user.is_authenticated:
                # Logged in users only see their own messages
                messages = ChatMessage.objects.filter(
                    user=request.user,
                    session_id=session_id
                ).order_by('timestamp').values('message', 'response', 'timestamp')
            else:
                # Anonymous users can only see messages from their session
                messages = ChatMessage.objects.filter(
                    user__isnull=True,
                    session_id=session_id
                ).order_by('timestamp').values('message', 'response', 'timestamp')
            
            # Format messages for frontend
            history = []
            for msg in messages:
                # Add user message
                history.append({
                    'text': msg['message'],
                    'type': 'user',
                    'timestamp': msg['timestamp'].strftime('%H:%M:%S')
                })
                # Add bot response
                history.append({
                    'text': msg['response'],
                    'type': 'bot',
                    'timestamp': msg['timestamp'].strftime('%H:%M:%S')
                })
            
            return JsonResponse({
                'history': history,
                'session_id': session_id
            })
            
        except Exception as e:
            logger.exception('Error fetching chat history')
            return JsonResponse({'error': 'Failed to fetch history'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def chat_sessions_list_api(request):
    """API endpoint to list all chat sessions - PRIVATE PER USER"""
    if request.method == 'GET':
        try:
            from django.db.models import Min, Count
            
            # PRIVACY FIX: Filter by current user only
            if request.user.is_authenticated:
                # Logged in users only see their own sessions
                base_queryset = ChatMessage.objects.filter(user=request.user)
            else:
                # Anonymous users - no sessions list (they only have current session)
                return JsonResponse({'sessions': []})
            
            sessions = base_queryset.values('session_id').annotate(
                created_at=Min('timestamp'),
                message_count=Count('id')
            ).order_by('-created_at')
            
            # Get preview (first message) for each session
            sessions_list = []
            for session in sessions[:20]:  # Limit to 20 recent sessions
                session_id = session['session_id']
                first_msg = base_queryset.filter(
                    session_id=session_id
                ).order_by('timestamp').first()
                
                if first_msg:
                    preview = first_msg.message[:50] + '...' if len(first_msg.message) > 50 else first_msg.message
                    sessions_list.append({
                        'session_id': session_id,
                        'created_at': session['created_at'].strftime('%Y-%m-%d %H:%M'),
                        'message_count': session['message_count'],
                        'preview': preview
                    })
            
            return JsonResponse({
                'sessions': sessions_list
            })
            
        except Exception as e:
            logger.exception('Error fetching chat sessions')
            return JsonResponse({'error': 'Failed to fetch sessions'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def delete_session_api(request):
    """API endpoint to delete a conversation session - PRIVATE PER USER"""
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('session_id')
            
            if not session_id:
                return JsonResponse({'error': 'session_id is required'}, status=400)
            
            # PRIVACY FIX: Only delete user's own messages
            if request.user.is_authenticated:
                deleted_count = ChatMessage.objects.filter(
                    user=request.user,
                    session_id=session_id
                ).delete()[0]
            else:
                # Anonymous users can only delete messages with no user
                deleted_count = ChatMessage.objects.filter(
                    user__isnull=True,
                    session_id=session_id
                ).delete()[0]
            
            return JsonResponse({
                'success': True,
                'deleted_count': deleted_count,
                'message': f'Đã xóa {deleted_count} tin nhắn'
            })
            
        except Exception as e:
            logger.exception('Error deleting session')
            return JsonResponse({'error': 'Failed to delete session'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

