"""
API Testing Script for HR-Tech Challenge
Test all endpoints and functionality
"""

import requests
import json
from pathlib import Path
import time

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("🏥 Testing health check endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                print(f"   Components: {data.get('components')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def test_resume_screening(self):
        """Test resume screening endpoint"""
        print("\n📄 Testing resume screening endpoint...")
        
        # Test with sample resume file
        test_resume = "data/resumes/john_smith_resume.txt"
        
        if not Path(test_resume).exists():
            print(f"⚠️ Test resume not found: {test_resume}")
            return False
        
        try:
            with open(test_resume, 'rb') as file:
                files = {'file': ('resume.txt', file, 'text/plain')}
                response = self.session.post(f"{self.base_url}/screen-resume", files=files)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Resume screening successful")
                print(f"   Candidate: {data.get('candidate_name', 'Unknown')}")
                print(f"   Score: {data.get('final_score', 0):.1f}/100")
                print(f"   Recommendation: {data.get('recommendation')}")
                print(f"   Interview: {data.get('interview_recommended')}")
                return True
            else:
                print(f"❌ Resume screening failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Resume screening error: {str(e)}")
            return False
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis endpoint"""
        print("\n💭 Testing sentiment analysis endpoint...")
        
        test_data = {
            "feedback_text": "I love working here but sometimes feel overwhelmed with the workload.",
            "employee_id": "TEST001",
            "department": "Engineering",
            "position": "Software Engineer",
            "tenure_months": 24,
            "manager_rating": 4,
            "performance_rating": 4
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/analyze-sentiment", 
                json=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sentiment analysis successful")
                print(f"   Employee: {data.get('employee_id')}")
                print(f"   Sentiment: {data.get('sentiment')}")
                print(f"   Confidence: {data.get('confidence_score', 0):.2f}")
                print(f"   Attrition Risk: {data.get('attrition_risk')}")
                print(f"   Key Concerns: {len(data.get('key_concerns', []))} concerns")
                return True
            else:
                print(f"❌ Sentiment analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Sentiment analysis error: {str(e)}")
            return False
    
    def test_batch_sentiment_analysis(self):
        """Test batch sentiment analysis endpoint"""
        print("\n📊 Testing batch sentiment analysis endpoint...")
        
        test_data = {
            "feedback_entries": [
                {
                    "feedback_text": "Great team collaboration and interesting projects!",
                    "employee_id": "BATCH001",
                    "department": "Engineering",
                    "position": "Developer",
                    "tenure_months": 12,
                    "manager_rating": 5
                },
                {
                    "feedback_text": "Work-life balance could be better, feeling stressed.",
                    "employee_id": "BATCH002",
                    "department": "Marketing",
                    "position": "Specialist",
                    "tenure_months": 6,
                    "manager_rating": 3
                }
            ]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/analyze-sentiment-batch",
                json=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Batch sentiment analysis successful")
                print(f"   Total entries: {data.get('total_entries')}")
                print(f"   Successful: {data.get('successful_analyses')}")
                print(f"   Failed: {data.get('failed_analyses')}")
                
                summary = data.get('summary', {})
                print(f"   Sentiment distribution: {summary.get('sentiment_distribution', {})}")
                return True
            else:
                print(f"❌ Batch sentiment analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Batch sentiment analysis error: {str(e)}")
            return False
    
    def test_demo_endpoints(self):
        """Test demo endpoints"""
        print("\n🎮 Testing demo endpoints...")
        
        # Test sample resume endpoint
        try:
            response = self.session.get(f"{self.base_url}/test-sample-resume")
            if response.status_code == 200:
                print("✅ Sample resume endpoint working")
            else:
                print(f"⚠️ Sample resume endpoint: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Sample resume error: {str(e)}")
        
        # Test sample sentiment endpoint  
        try:
            response = self.session.get(f"{self.base_url}/test-sample-sentiment")
            if response.status_code == 200:
                print("✅ Sample sentiment endpoint working")
                return True
            else:
                print(f"⚠️ Sample sentiment endpoint: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Sample sentiment error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 HR-Tech API Testing")
        print("=" * 30)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Resume Screening", self.test_resume_screening),
            ("Sentiment Analysis", self.test_sentiment_analysis), 
            ("Batch Sentiment Analysis", self.test_batch_sentiment_analysis),
            ("Demo Endpoints", self.test_demo_endpoints)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"💥 {test_name} crashed: {str(e)}")
                results.append((test_name, False))
            
            # Small delay between tests
            time.sleep(1)
        
        # Summary
        print(f"\n{'='*30}")
        print("📊 API TEST RESULTS:")
        
        passed = [name for name, result in results if result]
        failed = [name for name, result in results if not result]
        
        print(f"✅ Passed: {len(passed)}/{len(results)}")
        for test in passed:
            print(f"   ✅ {test}")
        
        if failed:
            print(f"❌ Failed: {len(failed)}")
            for test in failed:
                print(f"   ❌ {test}")
        
        return len(failed) == 0

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All API tests passed!")
        print(f"🚀 API is ready for deployment!")
    else:
        print(f"\n⚠️ Some API tests failed")
        print(f"🔧 Fix issues before deployment")