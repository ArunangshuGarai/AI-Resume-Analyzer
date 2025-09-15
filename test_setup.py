"""
Test script to verify HR-Tech Challenge setup
Run this after completing the installation steps
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def test_packages():
    """Test required packages"""
    print("\n📦 Testing package installations...")
    required_packages = [
        'google.generativeai',
        'pandas',
        'numpy',
        'sklearn',
        'matplotlib',
        'PyPDF2',
        'docx',
        'fastapi',
        'streamlit',
        'dotenv',
        'yaml'
    ]
    
    failed_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            failed_packages.append(package)
    
    return len(failed_packages) == 0

def test_project_structure():
    """Test project directory structure"""
    print("\n📁 Testing project structure...")
    required_dirs = [
        'data/resumes',
        'data/job_descriptions', 
        'data/employee_feedback',
        'notebooks',
        'src/utils',
        'src/resume_screening',
        'src/sentiment_analysis',
        'models',
        'reports',
        'config'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/ - OK")
        else:
            print(f"❌ {dir_path}/ - MISSING")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0

def test_environment_file():
    """Test .env file exists"""
    print("\n🔐 Testing environment file...")
    if Path('.env').exists():
        print("✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'GOOGLE_AI_API_KEY' in content:
                if 'YOUR_API_KEY_HERE' in content:
                    print("⚠️  Warning: Please update your API key in .env file")
                    return False
                else:
                    print("✅ API key appears to be set")
                    return True
            else:
                print("❌ GOOGLE_AI_API_KEY not found in .env")
                return False
    else:
        print("❌ .env file missing")
        return False

def test_google_ai_connection():
    """Test Google AI connection"""
    print("\n🤖 Testing Google AI connection...")
    try:
        from dotenv import load_dotenv
        import google.generativeai as genai
        
        load_dotenv()
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        model_name = os.getenv('MODEL_NAME', 'models/gemini-1.5-flash')
        
        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            print("❌ API key not set properly")
            return False
        
        genai.configure(api_key=api_key)
        
        # Try to use the configured model, with fallback options
        model_names_to_try = [
            model_name,
            'models/gemini-1.5-flash', 
            'models/gemini-1.5-pro',
            'models/gemini-pro'
        ]
        
        for model_name_attempt in model_names_to_try:
            try:
                print(f"   Trying model: {model_name_attempt}")
                model = genai.GenerativeModel(model_name_attempt)
                response = model.generate_content("Say 'Setup test successful!' if you can read this.")
                
                if response.text:
                    print("✅ Google AI connection successful!")
                    print(f"   Model used: {model_name_attempt}")
                    print(f"   Response: {response.text.strip()}")
                    
                    # Update .env file with working model if different
                    if model_name_attempt != os.getenv('MODEL_NAME'):
                        print(f"   💡 Tip: Update MODEL_NAME in .env to: {model_name_attempt}")
                    
                    return True
            except Exception as model_error:
                print(f"   ❌ {model_name_attempt} failed: {str(model_error)}")
                continue
        
        print("❌ All model attempts failed")
        return False
            
    except Exception as e:
        print(f"❌ Google AI connection failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 HR-Tech Challenge Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Required Packages", test_packages),
        ("Project Structure", test_project_structure),
        ("Environment File", test_environment_file),
        ("Google AI Connection", test_google_ai_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! You're ready for Phase 2!")
        print("   Run: python -c \"print('Phase 1 Complete!')\"")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("   Common fixes:")
        print("   1. Make sure virtual environment is activated")
        print("   2. Update your API key in the .env file")
        print("   3. Re-run package installations")
    
    return all_passed

if __name__ == "__main__":
    main()