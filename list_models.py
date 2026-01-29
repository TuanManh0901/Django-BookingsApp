
import google.generativeai as genai
import os
import django
from django.conf import settings

# Setup Django to get keys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vn_travel.settings')
django.setup()

api_key = settings.GEMINI_API_KEY
print(f"Checking models for API Key: {api_key[:5]}...")

try:
    genai.configure(api_key=api_key)
    print("\n--- AVAILABLE MODELS ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
