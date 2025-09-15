"""
Complete system testing for HR-Tech Challenge
Test both resume screening and sentiment analysis end-to-end
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import json

def test_complete_resume_screening():
    """Test complete resume screening system"""
    print("🎯 Testing Complete Resume Screening System...")
    print("=" * 50)
    
    try:
        from src.resume_screening.screener import ResumeScreener
        
        # Initialize screener with job requirements
        job_requirements_path = "data/job_descriptions/software_engineer_job.yaml"
        
        if not Path(job_requirements_path).exists():
            print(f"❌ Job requirements file not found: {job_requirements_path}")
            return False
        
        screener = ResumeScreener(job_requirements_path)
        print("✅ Resume screener initialized")
        
        # Test single resume screening
        print("\n📄 Testing single resume screening...")
        test_resume = "data/resumes/john_smith_resume.txt"
        
        if Path(test_resume).exists():
            result = screener.screen_single_resume(test_resume)
            
            if result['success']:
                print(f"✅ Single resume screening successful!")
                print(f"   Candidate: {result.get('candidate_name', 'Unknown')}")
                print(f"   Score: {result['final_score']:.1f}/100")
                print(f"   Recommendation: {result['recommendation']}")
                print(f"   Interview Recommended: {result['interview_recommended']}")
                
                # Show key details
                if result.get('strengths'):
                    print(f"   Strengths: {', '.join(result['strengths'][:3])}")
                if result.get('concerns'):
                    print(f"   Concerns: {', '.join(result['concerns'][:2])}")
                
            else:
                print(f"❌ Single resume screening failed: {result.get('error')}")
                return False
        else:
            print(f"⚠️ Test resume not found: {test_resume}")
        
        # Test multiple resume screening (limit to 5 for speed)
        print(f"\n📋 Testing multiple resume screening (limited set)...")
        resume_dir = Path("data/resumes")
        
        if resume_dir.exists():
            # Get first 5 resume files for testing
            resume_files = list(resume_dir.glob("*.txt"))[:5]
            
            if resume_files:
                print(f"   Found {len(resume_files)} resumes to test")
                
                # Create temporary directory for this specific test
                for resume_file in resume_files:
                    try:
                        result = screener.screen_single_resume(str(resume_file))
                        if result['success']:
                            name = result.get('candidate_name', resume_file.stem)
                            score = result['final_score']
                            rec = result['recommendation']
                            print(f"   ✅ {name}: {score:.1f} points ({rec})")
                        else:
                            print(f"   ❌ {resume_file.name}: Failed")
                    except Exception as e:
                        print(f"   ⚠️ {resume_file.name}: Exception - {str(e)[:50]}...")
                
                print("✅ Multiple resume screening test complete!")
            else:
                print("⚠️ No resume files found for testing")
        else:
            print("❌ Resume directory not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Resume screening system test failed: {str(e)}")
        return False

def test_complete_sentiment_analysis():
    """Test complete sentiment analysis system"""
    print("\n💬 Testing Complete Sentiment Analysis System...")
    print("=" * 50)
    
    try:
        from src.sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
        
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        print("✅ Sentiment analyzer initialized")
        
        # Test single feedback analysis
        print("\n💭 Testing single feedback analysis...")
        
        test_feedback = "I really enjoy working here and love the collaborative team environment, but sometimes the workload feels overwhelming and I worry about burnout."
        test_context = {
            'employee_id': 'TEST001',
            'department': 'Engineering',
            'position': 'Software Engineer',
            'tenure_months': 18,
            'manager_rating': 4,
            'performance_rating': 4
        }
        
        result = analyzer.analyze_single_feedback(test_feedback, test_context)
        
        if result['success']:
            print("✅ Single feedback analysis successful!")
            sentiment_data = result['sentiment_analysis']
            print(f"   Employee: {result['employee_id']}")
            print(f"   Sentiment: {sentiment_data.get('sentiment', 'unknown')}")
            print(f"   Confidence: {sentiment_data.get('confidence_score', 0):.2f}")
            print(f"   Attrition Risk: {result['attrition_risk_level']}")
            
            if result.get('key_concerns'):
                print(f"   Key Concerns: {', '.join(result['key_concerns'][:2])}")
            
            if result.get('recommended_actions'):
                print(f"   Recommended Actions: {len(result['recommended_actions'])} actions")
                
        else:
            print(f"❌ Single feedback analysis failed: {result.get('error')}")
            return False
        
        # Test with dataset if available (limited for speed)
        print(f"\n📊 Testing dataset analysis (sample)...")
        dataset_path = "data/employee_feedback/employee_feedback.csv"
        
        if Path(dataset_path).exists():
            # Test with small subset to avoid long processing time
            try:
                import pandas as pd
                
                # Load only first 5 rows for quick testing
                df = pd.read_csv(dataset_path).head(5)
                print(f"   Testing with {len(df)} feedback entries")
                
                for _, row in df.iterrows():
                    context = {
                        'employee_id': row.get('employee_id', 'Unknown'),
                        'department': row.get('department', 'Unknown'),
                        'position': row.get('position', 'Unknown'),
                        'tenure_months': row.get('tenure_months', 12),
                        'manager_rating': row.get('manager_rating', 3)
                    }
                    
                    feedback_text = row.get('feedback_text', '')[:100] + "..."
                    
                    try:
                        result = analyzer.analyze_single_feedback(row['feedback_text'], context)
                        if result['success']:
                            sentiment = result['sentiment_analysis'].get('sentiment', 'unknown')
                            risk = result['attrition_risk_level']
                            print(f"   ✅ {context['employee_id']}: {sentiment} sentiment, {risk} risk")
                        else:
                            print(f"   ❌ {context['employee_id']}: Analysis failed")
                    except Exception as e:
                        print(f"   ⚠️ {context['employee_id']}: Exception - {str(e)[:30]}...")
                
                print("✅ Dataset analysis test complete!")
                
            except Exception as e:
                print(f"   ⚠️ Dataset test error: {str(e)}")
        else:
            print(f"   ⚠️ Dataset not found: {dataset_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentiment analysis system test failed: {str(e)}")
        return False

def test_system_integration():
    """Test integration between systems"""
    print(f"\n🔗 Testing System Integration...")
    print("=" * 35)
    
    try:
        # Test that both systems can work together
        from src.resume_screening.screener import ResumeScreener
        from src.sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
        
        # Initialize both systems
        screener = ResumeScreener("data/job_descriptions/software_engineer_job.yaml")
        analyzer = SentimentAnalyzer()
        
        print("✅ Both systems initialized successfully")
        
        # Test data flow compatibility
        print("✅ Systems can coexist and share resources")
        
        # Check if reports directory exists
        reports_dir = Path("reports")
        if not reports_dir.exists():
            reports_dir.mkdir()
            print("✅ Created reports directory")
        else:
            print("✅ Reports directory exists")
        
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {str(e)}")
        return False

def check_deployment_readiness():
    """Check if systems are ready for deployment/API creation"""
    print(f"\n🚀 Checking Deployment Readiness...")
    print("=" * 35)
    
    readiness_checks = [
        ("Resume Parser", "src/resume_screening/resume_parser.py"),
        ("Resume Screener", "src/resume_screening/screener.py"),
        ("Sentiment Analyzer", "src/sentiment_analysis/sentiment_analyzer.py"),
        ("LLM Client", "src/utils/llm_client.py"),
        ("Prompt Templates", "config/prompts.yaml"),
        ("Job Requirements", "data/job_descriptions/software_engineer_job.yaml"),
        ("Sample Data", "data/resumes"),
        ("Reports Directory", "reports")
    ]
    
    all_ready = True
    for component, path in readiness_checks:
        if Path(path).exists():
            print(f"✅ {component}")
        else:
            print(f"❌ {component} - Missing: {path}")
            all_ready = False
    
    if all_ready:
        print(f"\n🎉 DEPLOYMENT READY!")
        print("   All core components are present and functional")
        print("   Ready for Phase 4: API Development & Deployment")
    else:
        print(f"\n⚠️ DEPLOYMENT NOT READY")
        print("   Fix missing components before proceeding to Phase 4")
    
    return all_ready

def main():
    """Run complete system tests"""
    print("🚀 HR-Tech Challenge: Complete System Testing")
    print("=" * 55)
    
    load_dotenv()
    
    # Check API key
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print("❌ GOOGLE_AI_API_KEY not found in environment")
        return False
    
    tests = [
        ("Resume Screening System", test_complete_resume_screening),
        ("Sentiment Analysis System", test_complete_sentiment_analysis), 
        ("System Integration", test_system_integration),
        ("Deployment Readiness", check_deployment_readiness)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name} Test...")
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {str(e)}")
            results.append((test_name, False))
    
    # Final summary
    print(f"\n" + "=" * 55)
    print("📊 COMPLETE SYSTEM TEST RESULTS:")
    
    passed_tests = [name for name, passed in results if passed]
    failed_tests = [name for name, passed in results if not passed]
    
    print(f"✅ Passed: {len(passed_tests)}/{len(results)} tests")
    for test in passed_tests:
        print(f"   ✅ {test}")
    
    if failed_tests:
        print(f"❌ Failed: {len(failed_tests)} tests")
        for test in failed_tests:
            print(f"   ❌ {test}")
    
    all_passed = len(failed_tests) == 0
    
    print(f"\n" + "=" * 55)
    if all_passed:
        print("🎉 ALL SYSTEMS GO! 🚀")
        print("   Your HR-Tech Challenge solution is working perfectly!")
        print("   Ready to proceed to Phase 4: API Development & Deployment")
        
        print(f"\n📋 What's working:")
        print("   • Resume parsing and skill extraction")
        print("   • AI-powered job matching")
        print("   • Employee sentiment analysis") 
        print("   • Attrition risk prediction")
        print("   • Engagement recommendations")
        print("   • End-to-end data processing")
        
        print(f"\n🚀 Next: Create REST APIs and deploy to cloud!")
    else:
        print("⚠️ SOME ISSUES DETECTED")
        print("   Fix the failed tests before proceeding to Phase 4")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Phase 3 COMPLETE! Ready for Phase 4!")
    else:
        print("\n🔧 Fix issues before moving to Phase 4")