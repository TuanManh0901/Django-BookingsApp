#!/usr/bin/env python
"""
Test Gemini API key and list available models
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vn_travel.settings')
django.setup()

from django.conf import settings
import google.generativeai as genai

def test_gemini_api():
    """Test Gemini API key và list available models"""
    
    # Get API key
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    
    print("🔍 Testing Gemini API...")
    print(f"API Key: {'✅ Present' if api_key else '❌ Missing'}")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in settings!")
        return False
    
    # Mask API key for security (show only first/last few chars)
    masked_key = f"{api_key[:10]}...{api_key[-10:]}" if len(api_key) > 20 else "***"
    print(f"Key preview: {masked_key}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        print("\n📋 Listing available models...")
        
        # List models
        models = list(genai.list_models())
        
        if not models:
            print("❌ No models returned - API key invalid or no access")
            return False
            
        print(f"✅ Found {len(models)} models")
        
        # Show models with generateContent support
        print("\n🤖 Models supporting generateContent:")
        supported_models = []
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                supported_models.append(model.name)
                print(f"  ✅ {model.name}")
        
        if not supported_models:
            print("❌ No models support generateContent")
            return False
            
        # Test actual generation with first model
        print(f"\n🧪 Testing generation with: {supported_models[0]}")
        
        test_model = genai.GenerativeModel(model_name=supported_models[0])
        response = test_model.generate_content("Hello, reply in Vietnamese")
        
        if hasattr(response, 'text') and response.text:
            print(f"✅ Success! Response: {response.text[:100]}...")
            return True
        else:
            print("❌ No text in response")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("\n🎉 Gemini API is working!")
        sys.exit(0)
    else:
        print("\n💥 Gemini API failed!")
        sys.exit(1)