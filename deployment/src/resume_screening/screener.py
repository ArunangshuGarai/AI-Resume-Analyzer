"""
Main Resume Screening System
src/resume_screening/screener.py
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..utils.llm_client import GoogleAIClient
from .resume_parser import ResumeParser

class ResumeScreener:
    """Main class for AI-powered resume screening"""
    
    def __init__(self, job_requirements_path: str = None):
        """Initialize the resume screener"""
        self.parser = ResumeParser()
        self.llm_client = GoogleAIClient()
        self.job_requirements = None
        
        # Load job requirements if provided
        if job_requirements_path:
            self.load_job_requirements(job_requirements_path)
        
        # Scoring weights
        self.scoring_weights = {
            'skills': 0.40,
            'experience': 0.35,
            'education': 0.15,
            'additional': 0.10
        }
    
    def load_job_requirements(self, file_path: str) -> bool:
        """Load job requirements from YAML file"""
        try:
            with open(file_path, 'r') as f:
                self.job_requirements = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Error loading job requirements: {str(e)}")
            return False
    
    def screen_single_resume(self, resume_path: str, job_requirements: Dict = None) -> Dict:
        """Screen a single resume against job requirements"""
        
        # Use provided job requirements or default
        job_req = job_requirements or self.job_requirements
        if not job_req:
            raise ValueError("No job requirements provided")
        
        # Parse resume
        print(f"📄 Parsing resume: {Path(resume_path).name}")
        parsed_resume = self.parser.parse_resume(resume_path)
        
        if not parsed_resume['success']:
            return {
                'success': False,
                'error': f"Failed to parse resume: {parsed_resume['error']}",
                'file_path': resume_path
            }
        
        # Extract skills using LLM
        print("🔍 Extracting skills...")
        try:
            extracted_skills = self.llm_client.extract_resume_skills(
                parsed_resume['cleaned_text']
            )
        except Exception as e:
            extracted_skills = {"error": f"Skill extraction failed: {str(e)}"}
        
        # Analyze experience using LLM
        print("💼 Analyzing experience...")
        try:
            extracted_experience = self.llm_client.analyze_resume_experience(
                parsed_resume['cleaned_text']
            )
        except Exception as e:
            extracted_experience = {"error": f"Experience analysis failed: {str(e)}"}
        
        # Match against job requirements using LLM
        print("🎯 Matching against job requirements...")
        try:
            job_match = self.llm_client.match_job_candidate(
                parsed_resume['cleaned_text'],
                job_req,
                extracted_skills,
                extracted_experience
            )
        except Exception as e:
            job_match = {"error": f"Job matching failed: {str(e)}"}
        
        # Calculate final score
        final_score = self._calculate_final_score(job_match, extracted_skills, extracted_experience)
        
        # Determine recommendation
        recommendation = self._get_recommendation(final_score, job_match)
        
        # Compile results
        screening_result = {
            'success': True,
            'file_path': resume_path,
            'candidate_name': parsed_resume['basic_info']['name'],
            'candidate_email': parsed_resume['basic_info']['email'],
            'timestamp': datetime.now().isoformat(),
            
            # Extracted information
            'extracted_skills': extracted_skills,
            'extracted_experience': extracted_experience,
            'job_match_analysis': job_match,
            
            # Scoring
            'final_score': final_score,
            'score_breakdown': {
                'skills_score': job_match.get('skills_match_score', 0),
                'experience_score': job_match.get('experience_match_score', 0),
                'education_score': job_match.get('education_match_score', 0),
                'overall_match_score': job_match.get('overall_match_score', 0)
            },
            
            # Recommendations
            'recommendation': recommendation,
            'interview_recommended': job_match.get('interview_recommendation', False),
            'strengths': job_match.get('detailed_analysis', {}).get('strengths', []),
            'concerns': job_match.get('detailed_analysis', {}).get('concerns', []),
            'missing_skills': job_match.get('detailed_analysis', {}).get('missing_skills', []),
            
            # Additional info
            'resume_word_count': parsed_resume['word_count'],
            'parsing_success': True
        }
        
        return screening_result
    
    def screen_multiple_resumes(self, resume_directory: str, job_requirements: Dict = None, 
                              output_file: str = None) -> List[Dict]:
        """Screen multiple resumes and return sorted results"""
        
        job_req = job_requirements or self.job_requirements
        if not job_req:
            raise ValueError("No job requirements provided")
        
        # Find all resume files
        resume_dir = Path(resume_directory)
        if not resume_dir.exists():
            raise ValueError(f"Resume directory not found: {resume_directory}")
        
        resume_files = []
        for ext in ['.pdf', '.docx', '.txt']:
            resume_files.extend(resume_dir.glob(f'*{ext}'))
        
        if not resume_files:
            raise ValueError(f"No resume files found in {resume_directory}")
        
        print(f"🎯 Screening {len(resume_files)} resumes...")
        print("=" * 50)
        
        # Screen each resume
        results = []
        for i, resume_file in enumerate(resume_files, 1):
            print(f"\n📋 [{i}/{len(resume_files)}] Processing: {resume_file.name}")
            
            try:
                result = self.screen_single_resume(str(resume_file), job_req)
                results.append(result)
                
                if result['success']:
                    score = result['final_score']
                    recommendation = result['recommendation']
                    print(f"   ✅ Score: {score:.1f}/100 | {recommendation}")
                else:
                    print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                error_result = {
                    'success': False,
                    'file_path': str(resume_file),
                    'error': str(e),
                    'final_score': 0
                }
                results.append(error_result)
                print(f"   ❌ Exception: {str(e)}")
        
        # Sort results by score (highest first)
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        successful_results.sort(key=lambda x: x['final_score'], reverse=True)
        sorted_results = successful_results + failed_results
        
        # Save results if output file specified
        if output_file:
            self._save_screening_results(sorted_results, output_file, job_req)
        
        # Print summary
        self._print_screening_summary(sorted_results)
        
        return sorted_results
    
    def _calculate_final_score(self, job_match: Dict, skills: Dict, experience: Dict) -> float:
        """Calculate final screening score"""
        
        # Handle errors in LLM responses
        if 'error' in job_match:
            return 0.0
        
        # Get individual scores
        skills_score = job_match.get('skills_match_score', 0)
        experience_score = job_match.get('experience_match_score', 0)
        education_score = job_match.get('education_match_score', 0)
        overall_score = job_match.get('overall_match_score', 0)
        
        # Calculate weighted average
        weighted_score = (
            skills_score * self.scoring_weights['skills'] +
            experience_score * self.scoring_weights['experience'] +
            education_score * self.scoring_weights['education'] +
            overall_score * self.scoring_weights['additional']
        )
        
        # Ensure score is between 0-100
        return max(0, min(100, weighted_score))
    
    def _get_recommendation(self, score: float, job_match: Dict) -> str:
        """Get hiring recommendation based on score and analysis"""
        
        if 'error' in job_match:
            return "review_required"
        
        # Check LLM recommendation first
        llm_recommendation = job_match.get('recommendation', '').lower()
        interview_rec = job_match.get('interview_recommendation', False)
        
        # Map LLM recommendations to our categories
        if llm_recommendation in ['strong_match'] and score >= 80:
            return "strong_hire"
        elif llm_recommendation in ['good_match'] and score >= 65:
            return "hire"
        elif llm_recommendation in ['partial_match'] and score >= 50:
            return "maybe"
        elif score >= 80:
            return "strong_hire"
        elif score >= 65:
            return "hire" 
        elif score >= 50:
            return "maybe"
        else:
            return "pass"
    
    def _save_screening_results(self, results: List[Dict], output_file: str, job_requirements: Dict):
        """Save screening results to JSON file"""
        
        output_data = {
            'screening_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_resumes': len(results),
                'successful_screenings': len([r for r in results if r['success']]),
                'job_requirements': job_requirements,
                'scoring_weights': self.scoring_weights
            },
            'results': results
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {output_file}")
    
    def _print_screening_summary(self, results: List[Dict]):
        """Print screening summary statistics"""
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n📊 SCREENING SUMMARY")
        print("=" * 30)
        print(f"📋 Total Resumes: {len(results)}")
        print(f"✅ Successfully Processed: {len(successful)}")
        print(f"❌ Failed to Process: {len(failed)}")
        
        if successful:
            scores = [r['final_score'] for r in successful]
            avg_score = sum(scores) / len(scores)
            
            print(f"\n📈 SCORE STATISTICS")
            print("-" * 20)
            print(f"Average Score: {avg_score:.1f}")
            print(f"Highest Score: {max(scores):.1f}")
            print(f"Lowest Score: {min(scores):.1f}")
            
            # Recommendation breakdown
            recommendations = {}
            for result in successful:
                rec = result['recommendation']
                recommendations[rec] = recommendations.get(rec, 0) + 1
            
            print(f"\n🎯 RECOMMENDATIONS")
            print("-" * 18)
            for rec, count in sorted(recommendations.items()):
                print(f"{rec.replace('_', ' ').title()}: {count}")
            
            # Top candidates
            print(f"\n🏆 TOP 5 CANDIDATES")
            print("-" * 18)
            top_candidates = successful[:5]
            for i, candidate in enumerate(top_candidates, 1):
                name = candidate.get('candidate_name', 'Unknown')
                score = candidate['final_score']
                rec = candidate['recommendation']
                print(f"{i}. {name} - {score:.1f} points ({rec})")

# Example usage
if __name__ == "__main__":
    try:
        # Initialize screener
        screener = ResumeScreener("data/job_descriptions/software_engineer_job.yaml")
        
        # Screen multiple resumes
        results = screener.screen_multiple_resumes(
            "data/resumes",
            output_file="reports/screening_results.json"
        )
        
        print(f"\n✅ Screening complete! {len(results)} resumes processed.")
        
    except Exception as e:
        print(f"❌ Screening failed: {str(e)}")