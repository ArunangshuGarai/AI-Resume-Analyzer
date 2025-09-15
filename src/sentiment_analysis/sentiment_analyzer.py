"""
Main Employee Sentiment Analysis System
src/sentiment_analysis/sentiment_analyzer.py
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

from ..utils.llm_client import GoogleAIClient

class SentimentAnalyzer:
    """Main class for AI-powered employee sentiment analysis"""
    
    def __init__(self):
        """Initialize the sentiment analyzer"""
        self.llm_client = GoogleAIClient()
        
        # Attrition risk thresholds
        self.attrition_thresholds = {
            'low': 0.3,
            'medium': 0.7,
            'high': 1.0
        }
        
        # Sentiment scoring
        self.sentiment_scores = {
            'positive': 1.0,
            'neutral': 0.5,
            'negative': 0.0
        }
    
    def analyze_single_feedback(self, feedback_text: str, employee_context: Dict) -> Dict:
        """Analyze a single piece of employee feedback"""
        
        print(f"💬 Analyzing feedback for {employee_context.get('employee_id', 'Unknown')}...")
        
        try:
            # Analyze sentiment using LLM
            sentiment_analysis = self.llm_client.analyze_sentiment(feedback_text, employee_context)
            
            # Generate engagement recommendations
            recommendations = self.llm_client.recommend_engagement_strategies(
                employee_context, sentiment_analysis, feedback_text
            )
            
            # Calculate numerical risk score
            risk_score = self._calculate_risk_score(sentiment_analysis, employee_context)
            
            # Compile results
            analysis_result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'employee_id': employee_context.get('employee_id'),
                'feedback_text': feedback_text,
                
                # Core analysis
                'sentiment_analysis': sentiment_analysis,
                'engagement_recommendations': recommendations,
                
                # Risk assessment
                'attrition_risk_score': risk_score,
                'attrition_risk_level': self._get_risk_level(risk_score),
                
                # Employee context
                'employee_context': employee_context,
                
                # Analysis metadata
                'analysis_confidence': sentiment_analysis.get('confidence_score', 0.0),
                'key_concerns': sentiment_analysis.get('key_concerns', []),
                'positive_indicators': sentiment_analysis.get('positive_indicators', []),
                'recommended_actions': recommendations.get('immediate_actions', [])
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'employee_id': employee_context.get('employee_id'),
                'feedback_text': feedback_text,
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_feedback_dataset(self, csv_file_path: str, output_file: str = None) -> List[Dict]:
        """Analyze employee feedback from CSV dataset"""
        
        # Load dataset
        try:
            df = pd.read_csv(csv_file_path)
            print(f"📊 Loaded {len(df)} feedback entries from {csv_file_path}")
        except Exception as e:
            raise ValueError(f"Failed to load dataset: {str(e)}")
        
        # Validate required columns
        required_columns = ['employee_id', 'feedback_text']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Analyze each feedback entry
        results = []
        total_entries = len(df)
        
        print(f"🚀 Starting sentiment analysis of {total_entries} entries...")
        print("=" * 60)
        
        for index, row in df.iterrows():
            try:
                print(f"\n[{index + 1}/{total_entries}] Processing Employee {row['employee_id']}")
                
                # Prepare employee context
                employee_context = {
                    'employee_id': row['employee_id'],
                    'department': row.get('department', 'Unknown'),
                    'position': row.get('position', 'Unknown'),
                    'tenure_months': row.get('tenure_months', 0),
                    'manager_rating': row.get('manager_rating', 3),
                    'performance_rating': row.get('performance_rating', 3),
                    'feedback_type': row.get('feedback_type', 'survey'),
                    'feedback_date': row.get('feedback_date', '')
                }
                
                # Analyze feedback
                result = self.analyze_single_feedback(row['feedback_text'], employee_context)
                results.append(result)
                
                if result['success']:
                    sentiment = result['sentiment_analysis'].get('sentiment', 'unknown')
                    risk = result['attrition_risk_level']
                    print(f"   ✅ Sentiment: {sentiment} | Risk: {risk}")
                else:
                    print(f"   ❌ Analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                error_result = {
                    'success': False,
                    'error': str(e),
                    'employee_id': row.get('employee_id', 'Unknown'),
                    'feedback_text': row.get('feedback_text', ''),
                    'timestamp': datetime.now().isoformat()
                }
                results.append(error_result)
                print(f"   ❌ Exception: {str(e)}")
        
        # Save results if output file specified
        if output_file:
            self._save_analysis_results(results, output_file)
        
        # Print summary
        self._print_analysis_summary(results)
        
        return results
    
    def generate_department_insights(self, analysis_results: List[Dict]) -> Dict:
        """Generate department-level insights from analysis results"""
        
        successful_results = [r for r in analysis_results if r['success']]
        
        if not successful_results:
            return {'error': 'No successful analysis results to process'}
        
        # Group by department
        dept_data = {}
        for result in successful_results:
            dept = result['employee_context'].get('department', 'Unknown')
            if dept not in dept_data:
                dept_data[dept] = []
            dept_data[dept].append(result)
        
        # Calculate department insights
        department_insights = {}
        for dept, results in dept_data.items():
            
            # Sentiment distribution
            sentiments = [r['sentiment_analysis'].get('sentiment') for r in results]
            sentiment_dist = {
                'positive': sentiments.count('positive'),
                'neutral': sentiments.count('neutral'), 
                'negative': sentiments.count('negative')
            }
            
            # Attrition risk distribution
            risk_levels = [r['attrition_risk_level'] for r in results]
            risk_dist = {
                'low': risk_levels.count('low'),
                'medium': risk_levels.count('medium'),
                'high': risk_levels.count('high')
            }
            
            # Average scores
            risk_scores = [r['attrition_risk_score'] for r in results]
            confidence_scores = [r['analysis_confidence'] for r in results if r['analysis_confidence']]
            
            # Top concerns
            all_concerns = []
            for result in results:
                all_concerns.extend(result.get('key_concerns', []))
            
            concern_counts = {}
            for concern in all_concerns:
                concern_counts[concern] = concern_counts.get(concern, 0) + 1
            
            top_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Department insights
            department_insights[dept] = {
                'total_feedback': len(results),
                'sentiment_distribution': sentiment_dist,
                'attrition_risk_distribution': risk_dist,
                'average_risk_score': np.mean(risk_scores) if risk_scores else 0,
                'average_confidence': np.mean(confidence_scores) if confidence_scores else 0,
                'top_concerns': [concern for concern, count in top_concerns],
                'high_risk_employees': [
                    r['employee_id'] for r in results 
                    if r['attrition_risk_level'] == 'high'
                ]
            }
        
        return department_insights
    
    def _calculate_risk_score(self, sentiment_analysis: Dict, employee_context: Dict) -> float:
        """Calculate numerical attrition risk score (0.0 to 1.0)"""
        
        if 'error' in sentiment_analysis:
            return 0.5  # Default medium risk for errors
        
        # Base score from sentiment
        sentiment = sentiment_analysis.get('sentiment', 'neutral')
        base_score = 1.0 - self.sentiment_scores.get(sentiment, 0.5)
        
        # Adjust based on LLM attrition risk assessment
        llm_risk = sentiment_analysis.get('attrition_risk', 'medium').lower()
        risk_adjustments = {
            'low': -0.2,
            'medium': 0.0,
            'high': 0.3
        }
        base_score += risk_adjustments.get(llm_risk, 0.0)
        
        # Context adjustments
        tenure_months = employee_context.get('tenure_months', 12)
        if tenure_months < 6:
            base_score += 0.1  # New employees higher risk
        elif tenure_months > 36:
            base_score -= 0.1  # Tenured employees lower risk
        
        manager_rating = employee_context.get('manager_rating', 3)
        if manager_rating <= 2:
            base_score += 0.2  # Poor management increases risk
        elif manager_rating >= 4:
            base_score -= 0.1  # Good management decreases risk
        
        # Key concerns boost risk
        concern_count = len(sentiment_analysis.get('key_concerns', []))
        base_score += min(0.2, concern_count * 0.05)
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, base_score))
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert numerical risk score to categorical level"""
        if risk_score <= self.attrition_thresholds['low']:
            return 'low'
        elif risk_score <= self.attrition_thresholds['medium']:
            return 'medium'
        else:
            return 'high'
    
    def _save_analysis_results(self, results: List[Dict], output_file: str):
        """Save analysis results to JSON file"""
        
        # Calculate summary statistics
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        # Department insights
        department_insights = self.generate_department_insights(results)
        
        output_data = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_feedback': len(results),
                'successful_analyses': len(successful),
                'failed_analyses': len(failed),
                'analysis_tool': 'AI-Powered Sentiment Analyzer'
            },
            'department_insights': department_insights,
            'detailed_results': results
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n💾 Analysis results saved to: {output_file}")
    
    def _print_analysis_summary(self, results: List[Dict]):
        """Print analysis summary statistics"""
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n📊 SENTIMENT ANALYSIS SUMMARY")
        print("=" * 35)
        print(f"📋 Total Feedback Entries: {len(results)}")
        print(f"✅ Successfully Analyzed: {len(successful)}")
        print(f"❌ Analysis Failures: {len(failed)}")
        
        if successful:
            # Sentiment distribution
            sentiments = [r['sentiment_analysis'].get('sentiment') for r in successful]
            sentiment_counts = {
                'positive': sentiments.count('positive'),
                'neutral': sentiments.count('neutral'),
                'negative': sentiments.count('negative')
            }
            
            print(f"\n😊 SENTIMENT DISTRIBUTION")
            print("-" * 25)
            for sentiment, count in sentiment_counts.items():
                percentage = (count / len(successful)) * 100
                print(f"{sentiment.capitalize()}: {count} ({percentage:.1f}%)")
            
            # Risk level distribution
            risk_levels = [r['attrition_risk_level'] for r in successful]
            risk_counts = {
                'low': risk_levels.count('low'),
                'medium': risk_levels.count('medium'),
                'high': risk_levels.count('high')
            }
            
            print(f"\n⚠️  ATTRITION RISK LEVELS")
            print("-" * 24)
            for risk, count in risk_counts.items():
                percentage = (count / len(successful)) * 100
                print(f"{risk.capitalize()} Risk: {count} ({percentage:.1f}%)")
            
            # High risk employees
            high_risk = [r for r in successful if r['attrition_risk_level'] == 'high']
            if high_risk:
                print(f"\n🚨 HIGH RISK EMPLOYEES ({len(high_risk)} total)")
                print("-" * 25)
                for emp in high_risk[:10]:  # Show top 10
                    emp_id = emp['employee_id']
                    dept = emp['employee_context'].get('department', 'Unknown')
                    risk_score = emp['attrition_risk_score']
                    print(f"   {emp_id} ({dept}) - Risk: {risk_score:.2f}")
                
                if len(high_risk) > 10:
                    print(f"   ... and {len(high_risk) - 10} more")

# Example usage
if __name__ == "__main__":
    try:
        # Initialize analyzer
        analyzer = SentimentAnalyzer()
        
        # Analyze feedback dataset
        results = analyzer.analyze_feedback_dataset(
            "data/employee_feedback/employee_feedback.csv",
            output_file="reports/sentiment_analysis_results.json"
        )
        
        print(f"\n✅ Sentiment analysis complete! {len(results)} entries processed.")
        
        # Generate department insights
        insights = analyzer.generate_department_insights(results)
        print(f"\n📈 Department insights generated for {len(insights)} departments.")
        
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {str(e)}")