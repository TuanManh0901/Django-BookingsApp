"""
Health Check Views for DevOps Monitoring
Provides endpoints for container orchestration and monitoring tools
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import time


def health_check_view(request):
    """
    Health check endpoint for DevOps monitoring
    Used by: Docker, Kubernetes, UptimeRobot, Load Balancers
    
    Returns JSON with status of all system components
    """
    start_time = time.time()
    
    status = {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check 1: Database Connection
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status["checks"]["database"] = {
            "status": "ok",
            "type": "postgresql"
        }
    except Exception as e:
        status["checks"]["database"] = {
            "status": "error",
            "message": str(e)
        }
        status["status"] = "unhealthy"
    
    # Check 2: AI Service (Gemini)
    try:
        from ai_chatbot.services import TravelAdvisor
        TravelAdvisor()
        status["checks"]["ai_service"] = {
            "status": "ok",
            "provider": "gemini-2.5-flash"
        }
    except Exception as e:
        status["checks"]["ai_service"] = {
            "status": "degraded",
            "message": str(e)[:100]
        }
        if status["status"] == "healthy":
            status["status"] = "degraded"
    
    # Check 3: Email Configuration
    try:
        email_configured = bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)
        status["checks"]["email"] = {
            "status": "ok" if email_configured else "not_configured",
            "provider": "smtp"
        }
    except:
        status["checks"]["email"] = {"status": "error"}
    
    # Check 4: Static Files
    try:
        import os
        static_exists = os.path.exists(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT else True
        status["checks"]["static_files"] = {
            "status": "ok" if static_exists else "warning"
        }
    except:
        status["checks"]["static_files"] = {"status": "unknown"}
    
    # Response time
    status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # HTTP status code based on health
    http_status = 200 if status["status"] == "healthy" else 503 if status["status"] == "unhealthy" else 200
    
    return JsonResponse(status, status=http_status)


def readiness_check_view(request):
    """
    Readiness probe for Kubernetes
    Returns 200 only when app is ready to receive traffic
    """
    try:
        # Check database is ready
        connection.ensure_connection()
        return JsonResponse({"ready": True}, status=200)
    except:
        return JsonResponse({"ready": False}, status=503)


def liveness_check_view(request):
    """
    Liveness probe for Kubernetes
    Returns 200 if app is alive (not deadlocked)
    """
    return JsonResponse({"alive": True}, status=200)
