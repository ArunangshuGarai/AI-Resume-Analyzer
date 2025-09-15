"""
Enhanced Google AI client for HR-Tech applications
"""

import os
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import json
import time
import yaml
from pathlib import Path

class GoogleAIClient:
    def __init__(self, api_key: str = None, model_name: str = None, config_path: str = "config/prompts.yaml"):
        """Initialize Google AI client with configuration"""
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        self.model_name = model_name or os.getenv('MODEL_NAME', 'models/gemini-2.0-flash')
        
        if not self.api_key:
            raise ValueError("Google AI API key is required")
        
        # Configure Google AI
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # Load prompt templates
        self.prompts = self._load_prompts(config_path)
        
        # Generation settings
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=2000,
            top_p=0.8,
            top_k=40
        )
    
    def _load_prompts(self, config_path: str) -> Dict:
        """Load prompt templates from YAML file"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                print(f"⚠️ Prompt config file not found: {config_path}")
                return {}
        except Exception as e:
            print(f"⚠️ Error loading prompts: {str(e)}")
            return {}
    
    def generate_response(self, prompt: str, system_prompt: str = None, 
                         temperature: float = None, max_tokens: int = None, 
                         retry_count: int = 3) -> str:
        """Generate response from Google AI model"""
        
        # Use custom generation config if parameters provided
        gen_config = self.generation_config
        if temperature is not None or max_tokens is not None:
            gen_config = genai.types.GenerationConfig(
                temperature=temperature or self.generation_config.temperature,
                max_output_tokens=max_tokens or self.generation_config.max_output_tokens,
                top_p=self.generation_config.top_p,
                top_k=self.generation_config.top_k
            )
        
        # Combine system and user prompts
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        else:
            full_prompt = prompt
        
        for attempt in range(retry_count):
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=gen_config
                )
                return response.text
            
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
    
    def generate_json_response(self, prompt: str, system_prompt: str = None, **kwargs) -> Dict[Any, Any]:
        """Generate JSON response from model with error handling"""
        
        # Add JSON instruction to prompt
        if "Return ONLY a valid JSON object" not in prompt:
            prompt += "\n\nReturn ONLY a valid JSON object. No additional text."
        
        response = self.generate_response(prompt, system_prompt, **kwargs)
        
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict[Any, Any]:
        """Parse JSON from model response with multiple fallback strategies"""
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON block
        try:
            # Look for JSON between ```json blocks
            json_match = response.find('```json')
            if json_match != -1:
                start = json_match + 7
                end = response.find('```', start)
                if end != -1:
                    json_text = response[start:end].strip()
                    return json.loads(json_text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Find JSON object boundaries
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_text = response[start:end]
                return json.loads(json_text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 4: Clean and retry
        try:
            # Remove common prefixes/suffixes
            cleaned = response.strip()
            for prefix in ["Here's the JSON:", "JSON Response:", "```json", "```"]:
                cleaned = cleaned.replace(prefix, "").strip()
            
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start != -1 and end > start:
                json_text = cleaned[start:end]
                return json.loads(json_text)
        except json.JSONDecodeError:
            pass
        
        # If all strategies fail, return error structure
        return {
            "error": "Failed to parse JSON response",
            "raw_response": response[:500] + "..." if len(response) > 500 else response
        }
    
    # Resume Screening Methods
    def extract_resume_skills(self, resume_text: str) -> Dict[str, List[str]]:
        """Extract technical skills from resume using LLM"""
        if 'resume_screening' not in self.prompts:
            raise ValueError("Resume screening prompts not loaded")
        
        skill_prompts = self.prompts['resume_screening']['skill_extraction']
        system_prompt = skill_prompts['system_prompt']
        user_prompt = skill_prompts['user_prompt'].format(resume_text=resume_text)
        
        return self.generate_json_response(user_prompt, system_prompt)
    
    def analyze_resume_experience(self, resume_text: str) -> Dict[str, any]:
        """Analyze work experience from resume using LLM"""
        if 'resume_screening' not in self.prompts:
            raise ValueError("Resume screening prompts not loaded")
        
        exp_prompts = self.prompts['resume_screening']['experience_analysis']
        system_prompt = exp_prompts['system_prompt']
        user_prompt = exp_prompts['user_prompt'].format(resume_text=resume_text)
        
        return self.generate_json_response(user_prompt, system_prompt)
    
    def match_job_candidate(self, resume_text: str, job_requirements: Dict, 
                           extracted_skills: Dict, extracted_experience: Dict) -> Dict[str, any]:
        """Match candidate against job requirements using LLM"""
        if 'resume_screening' not in self.prompts:
            raise ValueError("Resume screening prompts not loaded")
        
        match_prompts = self.prompts['resume_screening']['job_matching']
        system_prompt = match_prompts['system_prompt']
        user_prompt = match_prompts['user_prompt'].format(
            job_requirements=json.dumps(job_requirements, indent=2),
            resume_text=resume_text[:2000],  # Truncate for context limits
            extracted_skills=json.dumps(extracted_skills, indent=2),
            extracted_experience=json.dumps(extracted_experience, indent=2)
        )
        
        return self.generate_json_response(user_prompt, system_prompt)
    
    # Sentiment Analysis Methods
    def analyze_sentiment(self, feedback_text: str, employee_context: Dict) -> Dict[str, any]:
        """Analyze employee feedback sentiment using LLM"""
        if 'sentiment_analysis' not in self.prompts:
            raise ValueError("Sentiment analysis prompts not loaded")
        
        sentiment_prompts = self.prompts['sentiment_analysis']['sentiment_classification']
        system_prompt = sentiment_prompts['system_prompt']
        user_prompt = sentiment_prompts['user_prompt'].format(
            feedback_text=feedback_text,
            department=employee_context.get('department', 'Unknown'),
            position=employee_context.get('position', 'Unknown'),
            tenure_months=employee_context.get('tenure_months', 0),
            manager_rating=employee_context.get('manager_rating', 3)
        )
        
        return self.generate_json_response(user_prompt, system_prompt)
    
    def recommend_engagement_strategies(self, employee_context: Dict, 
                                      sentiment_analysis: Dict, feedback_text: str) -> Dict[str, any]:
        """Generate engagement recommendations using LLM"""
        if 'sentiment_analysis' not in self.prompts:
            raise ValueError("Sentiment analysis prompts not loaded")
        
        rec_prompts = self.prompts['sentiment_analysis']['engagement_recommendations']
        system_prompt = rec_prompts['system_prompt']
        user_prompt = rec_prompts['user_prompt'].format(
            department=employee_context.get('department', 'Unknown'),
            position=employee_context.get('position', 'Unknown'),
            tenure_months=employee_context.get('tenure_months', 0),
            sentiment=sentiment_analysis.get('sentiment', 'neutral'),
            attrition_risk=sentiment_analysis.get('attrition_risk', 'medium'),
            key_concerns=', '.join(sentiment_analysis.get('key_concerns', [])),
            manager_rating=employee_context.get('manager_rating', 3),
            feedback_text=feedback_text
        )
        
        return self.generate_json_response(user_prompt, system_prompt)

# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        client = GoogleAIClient()
        
        # Test resume skill extraction
        sample_resume = """
        John Smith - Software Engineer
        5 years experience in Python, React, and AWS.
        Worked with PostgreSQL and Docker containers.
        """
        
        print("🧪 Testing skill extraction...")
        skills = client.extract_resume_skills(sample_resume)
        print(f"Extracted skills: {skills}")
        
        # Test sentiment analysis
        print("\n🧪 Testing sentiment analysis...")
        feedback = "I love working here but the workload is getting overwhelming."
        context = {
            'department': 'Engineering',
            'position': 'Software Engineer',
            'tenure_months': 18,
            'manager_rating': 4
        }
        
        sentiment = client.analyze_sentiment(feedback, context)
        print(f"Sentiment analysis: {sentiment}")
        
        print("✅ LLM client testing complete!")
        
    except Exception as e:
        print(f"❌ Error testing LLM client: {str(e)}")