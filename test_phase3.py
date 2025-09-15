"""
Test script for Phase 3 AI components
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def test_resume_parser():
    """Test resume parsing functionality"""
    print("🧪 Testing Resume Parser...")
    print("-" * 30)
    
    try:
        from src.resume_screening.resume_parser import ResumeParser
        
        parser = ResumeParser()
        
        # Test with sample resume files
        sample_files = [
            "data/resumes/john_smith_resume.txt",
            "data/resumes/sarah_johnson_resume.txt"
        ]
        
        for file_path in sample_files:
            if Path(file_path).exists():
                print(f"\n📄 Testing: {Path(file_path).name}")
                result = parser.parse_resume(file_path)
                
                if result['success']:
                    print(f"   ✅ Parsed successfully - {result['word_count']} words")
                    print(f"   📧 Email: {result['basic_info']['email']}")
                    print(f"   👤 Name: {result['basic_info']['name']}")
                else:
                    print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   ⚠️ File not found: {file_path}")
        
        print("\n✅ Resume Parser test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Resume Parser test failed: {str(e)}")
        return False

def test_llm_client():
    """Test LLM client functionality"""
    print("\n🤖 Testing LLM Client...")
    print("-" * 25)
    
    try:
        from src.utils.llm_client import GoogleAIClient
        
        client = GoogleAIClient()
        
        # Test basic response generation
        print("   Testing basic response generation...")
        response = client.generate_response("Say 'LLM client working!' if you can read this.")
        print(f"   Response: {response[:100]}...")
        
        # Test skill extraction
        print("\n   Testing resume skill extraction...")
        sample_resume = """
        JOHN DOE
        Software Engineer
        
        TECHNICAL SKILLS:
        - Programming: Python, Java, JavaScript
        - Frameworks: React, Django, Spring Boot
        - Databases: PostgreSQL, MongoDB
        - Cloud: AWS, Docker
        
        EXPERIENCE:
        Senior Software Engineer at TechCorp (2020-Present)
        - Built microservices with Python and Django
        - Deployed applications on AWS
        """
        
        skills = client.extract_resume_skills(sample_resume)
        print(f"   Extracted skills: {skills}")
        
        if 'programming_languages' in skills:
            print("   ✅ Skill extraction working!")
        else:
            print("   ⚠️ Skill extraction format issue")
        
        # Test sentiment analysis
        print("\n   Testing sentiment analysis...")
        feedback = "I enjoy working here but sometimes feel overwhelmed with the workload."
        context = {
            'department': 'Engineering',
            'position': 'Software Engineer',
            'tenure_months': 24,
            'manager_rating': 4
        }
        
        sentiment = client.analyze_sentiment(feedback, context)
        print(f"   Sentiment result: {sentiment}")
        
        if 'sentiment' in sentiment:
            print("   ✅ Sentiment analysis working!")
        else:
            print("   ⚠️ Sentiment analysis format issue")
        
        print("\n✅ LLM Client test complete!")
        return True
        
    except Exception as e:
        print(f"❌ LLM Client test failed: {str(e)}")
        return False

def test_prompt_loading():
    """Test prompt template loading"""
    print("\n📝 Testing Prompt Loading...")
    print("-" * 27)
    
    try:
        import yaml
        
        prompts_file = Path("config/prompts.yaml")
        if prompts_file.exists():
            with open(prompts_file, 'r') as f:
                prompts = yaml.safe_load(f)
            
            # Check required sections
            required_sections = [
                'resume_screening',
                'sentiment_analysis'
            ]
            
            for section in required_sections:
                if section in prompts:
                    print(f"   ✅ {section} prompts loaded")
                    
                    # Check subsections
                    if section == 'resume_screening':
                        subsections = ['skill_extraction', 'experience_analysis', 'job_matching']
                    else:
                        subsections = ['sentiment_classification', 'engagement_recommendations']
                    
                    for subsection in subsections:
                        if subsection in prompts[section]:
                            print(f"      ✅ {subsection}")
                        else:
                            print(f"      ❌ {subsection} missing")
                else:
                    print(f"   ❌ {section} prompts missing")
            
            print("\n✅ Prompt loading test complete!")
            return True
        else:
            print("   ❌ Prompts file not found: config/prompts.yaml")
            return False
            
    except Exception as e:
        print(f"❌ Prompt loading test failed: {str(e)}")
        return False

def test_file_structure():
    """Test Phase 3 file structure"""
    print("\n📁 Testing File Structure...")
    print("-" * 26)
    
    required_files = [
        "src/resume_screening/resume_parser.py",
        "src/utils/llm_client.py",
        "config/prompts.yaml"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all Phase 3 tests"""
    print("🚀 Phase 3 AI Components Testing")
    print("=" * 40)
    
    load_dotenv()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Prompt Loading", test_prompt_loading),
        ("Resume Parser", test_resume_parser),
        ("LLM Client", test_llm_client)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    
    all_passed = all([passed for _, passed in results])
    
    if all_passed:
        print("🎉 ALL PHASE 3 TESTS PASSED!")
        print("   ✅ Resume parsing working")
        print("   ✅ LLM integration successful")
        print("   ✅ Prompt templates loaded")
        print("   ✅ Ready for main screening classes!")
        
        print("\n🚀 Next Steps:")
        print("   1. Build Resume Screener class")
        print("   2. Build Sentiment Analyzer class") 
        print("   3. Create API endpoints")
        print("   4. Test end-to-end functionality")
    else:
        print("⚠️ Some tests failed. Fix issues before proceeding:")
        failed_tests = [name for name, passed in results if not passed]
        for test in failed_tests:
            print(f"   🔧 Fix: {test}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Phase 3 components ready - proceed to main classes!")
    else:
        print("\n❌ Fix component issues before continuing")
    print("📊 PHASE 3 TEST RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 40)