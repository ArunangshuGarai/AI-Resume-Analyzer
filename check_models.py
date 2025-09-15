"""
Script to check available Google AI models
Run this to see what models you can use
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def check_available_models():
    """Check what models are available in Google AI"""
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        
        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            print("❌ API key not set properly in .env file")
            return False
        
        # Configure Google AI
        genai.configure(api_key=api_key)
        
        print("🔍 Checking available models...")
        print("=" * 50)
        
        # List all available models
        models = genai.list_models()
        
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"✅ {model.name}")
                print(f"   Display Name: {model.display_name}")
                print(f"   Description: {model.description}")
                print(f"   Supported Methods: {model.supported_generation_methods}")
                print("-" * 50)
        
        if available_models:
            print(f"\n🎯 Recommended model to use: {available_models[0]}")
            
            # Test the first available model
            print(f"\n🧪 Testing connection with {available_models[0]}...")
            model = genai.GenerativeModel(available_models[0])
            response = model.generate_content("Hello! Say 'Connection successful!' if you can read this.")
            
            print("✅ Connection test successful!")
            print(f"Response: {response.text}")
            
            return available_models[0]
        else:
            print("❌ No compatible models found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking models: {str(e)}")
        return None

if __name__ == "__main__":
    recommended_model = check_available_models()
    if recommended_model:
        print(f"\n📝 Update your .env file with:")
        print(f"MODEL_NAME={recommended_model}")
    else:
        print("\n⚠️  Please check your API key and try again")