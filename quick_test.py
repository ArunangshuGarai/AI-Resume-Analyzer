"""
Quick test for Flash models to avoid rate limits
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_flash_models():
    load_dotenv()
    genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
    
    models_to_try = [
        'models/gemini-1.5-flash',
        'models/gemini-2.0-flash',
        'models/gemini-1.5-flash-8b'
    ]
    
    working_models = []
    
    print("Testing all models...\n" + "="*50)
    
    for i, model_name in enumerate(models_to_try, 1):
        try:
            print(f"[{i}/3] Testing {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content('Hello! Connection test successful.')
            
            print(f"✅ {model_name} works!")
            print(f"    Response: {response.text}")
            working_models.append(model_name)
            
        except Exception as e:
            print(f"❌ {model_name} failed:")
            print(f"    Error: {str(e)}")
        
        print("-" * 50)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"Working models: {len(working_models)}/3")
    
    if working_models:
        print(f"\n✅ Available models:")
        for i, model in enumerate(working_models, 1):
            print(f"   {i}. {model}")
        
        print(f"\n🎯 Recommended model (fastest): {working_models[0]}")
        print(f"📝 Update your .env with: MODEL_NAME={working_models[0]}")
        return working_models[0]
    else:
        print("❌ All Flash models failed. Please wait for rate limit reset.")
        return None

if __name__ == "__main__":
    working_model = test_flash_models()
    if working_model:
        print(f"\n🎉 Success! Use this model: {working_model}")
    else:
        print("\n⏰ Please wait a few minutes for rate limits to reset.")