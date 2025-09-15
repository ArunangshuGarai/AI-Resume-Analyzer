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
            'very_low': 0.2,
            'low': 0.4,
            'medium': 0.6,
            'high': 0.8,
            'very_high': 1.0
        }
        
        # Sentiment scoring with more granular sentiment levels
        self.sentiment_scores = {
            'very_positive': 1.0,
            'positive': 0.8,
            'slightly_positive': 0.6,
            'neutral': 0.5,
            'slightly_negative': 0.4,
            'negative': 0.2,
            'very_negative': 0.0
        }
    
    def analyze_single_feedback(self, feedback_text: str, employee_context: Dict) -> Dict:
        """Analyze a single piece of employee feedback"""
        
        print(f"💬 Analyzing feedback for {employee_context.get('employee_id', 'Unknown')}...")
        
        try:
            # Analyze sentiment using LLM with enhanced context
            sentiment_analysis = self.llm_client.analyze_sentiment(feedback_text, employee_context)
            
            # Generate engagement recommendations
            recommendations = self.llm_client.recommend_engagement_strategies(
                employee_context, sentiment_analysis, feedback_text
            )
            
            # Calculate numerical risk score
            risk_score = self._calculate_risk_score(sentiment_analysis, employee_context)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(sentiment_analysis, employee_context)
            
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
                'analysis_confidence': confidence_score,
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
        """Calculate numerical attrition risk score (0.0 to 1.0) with enhanced factors"""
        
        if 'error' in sentiment_analysis:
            return 0.5  # Default medium risk for errors
        
        # Get base sentiment score with more granular levels
        sentiment = sentiment_analysis.get('sentiment', 'neutral')
        sentiment_score = self.sentiment_scores.get(sentiment, 0.5)
        
        # Initialize weighted factors
        factors = []
        
        # 1. Sentiment-based factor (30% weight)
        sentiment_factor = 1.0 - sentiment_score
        factors.append((sentiment_factor, 0.30))
        
        # 2. LLM attrition risk assessment (25% weight)
        llm_risk = sentiment_analysis.get('attrition_risk', 'medium').lower()
        risk_scores = {
            'very_low': 0.1,
            'low': 0.3,
            'medium': 0.5,
            'high': 0.7,
            'very_high': 0.9
        }
        llm_risk_score = risk_scores.get(llm_risk, 0.5)
        factors.append((llm_risk_score, 0.25))
        
        # 3. Tenure-based factor (15% weight)
        tenure_months = employee_context.get('tenure_months', 12)
        tenure_factor = self._calculate_tenure_risk(tenure_months)
        factors.append((tenure_factor, 0.15))
        
        # 4. Performance indicators (20% weight)
        performance_factor = self._calculate_performance_risk(
            employee_context.get('manager_rating', 3),
            employee_context.get('performance_rating', 3)
        )
        factors.append((performance_factor, 0.20))
        
        # 5. Key concerns impact (10% weight)
        concern_count = len(sentiment_analysis.get('key_concerns', []))
        concern_factor = min(1.0, concern_count * 0.15)  # Each concern adds 15% up to 100%
        factors.append((concern_factor, 0.10))
        
        # Calculate weighted average
        weighted_score = sum(score * weight for score, weight in factors)
        
        # Apply historical trend adjustment if available
        if employee_context.get('previous_risk_score') is not None:
            prev_score = float(employee_context['previous_risk_score'])
            trend_adjustment = (weighted_score - prev_score) * 0.2  # 20% impact from trend
            weighted_score += trend_adjustment
        
        # Ensure final score is between 0 and 1
        return max(0.0, min(1.0, weighted_score))
    
    def _calculate_tenure_risk(self, tenure_months: int) -> float:
        """Calculate risk factor based on employee tenure"""
        if tenure_months < 3:
            return 0.8  # Very high risk for new employees
        elif tenure_months < 6:
            return 0.6  # High risk
        elif tenure_months < 12:
            return 0.4  # Medium risk
        elif tenure_months < 24:
            return 0.3  # Low risk
        elif tenure_months < 36:
            return 0.2  # Very low risk
        else:
            return 0.1  # Minimal risk for tenured employees
    
    def _calculate_performance_risk(self, manager_rating: int, performance_rating: int) -> float:
        """Calculate risk factor based on performance indicators"""
        # Convert 1-5 ratings to 0-1 scale
        mgr_score = (6 - manager_rating) / 4  # Invert so lower ratings = higher risk
        perf_score = (6 - performance_rating) / 4
        
        # Weight manager rating slightly higher than performance rating
        weighted_score = (mgr_score * 0.6) + (perf_score * 0.4)
        
        return weighted_score
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert numerical risk score to categorical level"""
        for level, threshold in sorted(self.attrition_thresholds.items(), key=lambda x: x[1]):
            if risk_score <= threshold:
                return level
        return 'very_high'
    
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
    
    def _calculate_confidence_score(self, sentiment_analysis: Dict, employee_context: Dict) -> float:
        """Calculate confidence score with enhanced dynamic scaling (0.0 to 1.0)"""
        
        # Base factors
        base_score = 0.0
        total_weight = 0.0
        
        # 1. Text Quality (25%)
        text = employee_context.get('feedback_text', '')
        words = len(text.split())
        if words < 10:
            text_score = 0.1
        elif words < 30:
            text_score = 0.3
        elif words < 100:
            text_score = 0.6
        elif words < 300:
            text_score = 0.8
        else:
            text_score = 0.7  # Penalize extremely long text slightly
        base_score += text_score * 0.25
        total_weight += 0.25
        
        # 2. Sentiment Decisiveness (30%)
        sentiment_scores = sentiment_analysis.get('sentiment_scores', {})
        if sentiment_scores:
            scores = sorted(sentiment_scores.values(), reverse=True)
            if len(scores) >= 2:
                # Calculate how decisive the top sentiment is
                score_gap = scores[0] - scores[1]
                sentiment_score = min(1.0, score_gap * 2)
            else:
                sentiment_score = 0.5
        else:
            sentiment_score = 0.3
        base_score += sentiment_score * 0.30
        total_weight += 0.30
        
        # 3. Context Quality (25%)
        context_quality = 0.0
        key_fields = {
            'department': 0.05,
            'position': 0.05,
            'tenure_months': 0.05,
            'manager_rating': 0.05,
            'performance_rating': 0.05
        }
        for field, weight in key_fields.items():
            if employee_context.get(field):
                context_quality += weight
        base_score += context_quality
        total_weight += 0.25
        
        # 4. Analysis Detail (20%)
        detail_score = 0.0
        if sentiment_analysis.get('key_concerns'):
            detail_score += 0.07
        if sentiment_analysis.get('positive_indicators'):
            detail_score += 0.07
        if sentiment_analysis.get('key_phrases'):
            detail_score += 0.06
        base_score += detail_score
        total_weight += 0.20
        
        # Normalize base score
        if total_weight > 0:
            normalized_score = base_score / total_weight
        else:
            normalized_score = 0.5
        
        # Apply non-linear transformation to spread out scores
        # Using modified sigmoid function with adjustable steepness
        steepness = 6.0  # Higher values create more spread
        midpoint = 0.5   # Center point of the sigmoid
        scaled_score = 1 / (1 + np.exp(-steepness * (normalized_score - midpoint)))
        
        # Apply dynamic range limiting
        min_confidence = 0.15  # Never go below 15%
        max_confidence = 0.95  # Never hit 100%
        
        # Additional penalties
        if words < 20:  # Very short feedback
            scaled_score *= 0.7
        elif words < 50:  # Short feedback
            scaled_score *= 0.85
        
        # Ensure final score is within bounds
        final_score = min_confidence + (max_confidence - min_confidence) * scaled_score
        
        return max(min_confidence, min(max_confidence, final_score))
    
    def _calculate_sentiment_clarity(self, sentiment_scores: Dict[str, float], dominant_sentiment: str) -> float:
        """Calculate how clear and decisive the sentiment analysis is"""
        if not sentiment_scores:
            return 0.5  # Default if no detailed scores
            
        # Calculate the spread between the highest and second-highest scores
        sorted_scores = sorted(sentiment_scores.values(), reverse=True)
        if len(sorted_scores) >= 2:
            score_gap = sorted_scores[0] - sorted_scores[1]
        else:
            score_gap = 0.5
            
        # Consider the absolute strength of the sentiment
        sentiment_strength = abs(self.sentiment_scores.get(dominant_sentiment, 0.5) - 0.5) * 2
        
        # Combine gap and strength
        clarity = (score_gap * 0.6) + (sentiment_strength * 0.4)
        
        return max(0.3, min(1.0, clarity))  # Minimum 30% confidence
        
    def _calculate_context_reliability(self, context: Dict) -> float:
        """Evaluate the reliability and completeness of the context data"""
        
        # Critical fields with weights
        field_weights = {
            'department': 0.2,
            'position': 0.2,
            'tenure_months': 0.15,
            'manager_rating': 0.25,
            'performance_rating': 0.2
        }
        
        reliability_score = 0.0
        total_weight = 0.0
        
        for field, weight in field_weights.items():
            if field in context and context[field] is not None:
                # Check for numeric fields
                if field in ['tenure_months', 'manager_rating', 'performance_rating']:
                    try:
                        value = float(context[field])
                        if 0 <= value <= 5:  # Assuming ratings are 0-5
                            reliability_score += weight
                    except (ValueError, TypeError):
                        pass
                else:
                    # String fields should be non-empty and meaningful
                    if isinstance(context[field], str) and context[field].lower() not in ['', 'unknown', 'none', 'n/a']:
                        reliability_score += weight
            total_weight += weight
            
        return reliability_score / total_weight if total_weight > 0 else 0.5
        
    def _calculate_feedback_substance(self, concerns: List[str], positives: List[str], 
                                   key_phrases: List[str], feedback_text: str) -> float:
        """Evaluate the substantive quality of the feedback"""
        
        # Initialize base score
        substance_score = 0.5
        
        # Text length evaluation (10-20%)
        length = len(feedback_text.split())
        if length < 10:
            length_factor = 0.3
        elif length < 30:
            length_factor = 0.6
        elif length < 100:
            length_factor = 0.8
        elif length < 300:
            length_factor = 1.0
        else:
            length_factor = 0.9  # Penalize overly long feedback slightly
        
        # Content richness (40%)
        unique_insights = set(concerns + positives + key_phrases)
        insight_density = min(1.0, len(unique_insights) / 10)  # Cap at 10 unique insights
        
        # Balanced perspective (30%)
        if concerns and positives:
            balance_factor = min(len(concerns), len(positives)) / max(len(concerns), len(positives))
        else:
            balance_factor = 0.5
        
        # Combine factors with weights
        substance_score = (length_factor * 0.2 +
                         insight_density * 0.4 +
                         balance_factor * 0.3 +
                         substance_score * 0.1)  # Keep some of base score
                         
        return max(0.0, min(1.0, substance_score))
        
    def _check_analysis_consistency(self, sentiment_analysis: Dict, context: Dict) -> float:
        """Check if sentiment analysis is consistent with other indicators"""
        
        consistency_score = 0.5
        checks_performed = 0
        
        # Get sentiment polarity (-1 to 1 scale)
        sentiment = sentiment_analysis.get('sentiment', 'neutral')
        sentiment_polarity = (self.sentiment_scores.get(sentiment, 0.5) - 0.5) * 2
        
        # Check against performance rating
        if 'performance_rating' in context:
            try:
                perf_rating = float(context['performance_rating'])
                perf_polarity = (perf_rating - 2.5) / 2.5  # Convert 0-5 to -1 to 1
                rating_consistency = 1 - min(1, abs(sentiment_polarity - perf_polarity))
                consistency_score += rating_consistency
                checks_performed += 1
            except (ValueError, TypeError):
                pass
        
        # Check against manager rating
        if 'manager_rating' in context:
            try:
                mgr_rating = float(context['manager_rating'])
                mgr_polarity = (mgr_rating - 2.5) / 2.5
                mgr_consistency = 1 - min(1, abs(sentiment_polarity - mgr_polarity))
                consistency_score += mgr_consistency
                checks_performed += 1
            except (ValueError, TypeError):
                pass
        
        # Check sentiment-concern alignment
        if sentiment in ['negative', 'very_negative', 'slightly_negative']:
            concern_alignment = 1.0 if sentiment_analysis.get('key_concerns', []) else 0.5
        elif sentiment in ['positive', 'very_positive', 'slightly_positive']:
            concern_alignment = 1.0 if sentiment_analysis.get('positive_indicators', []) else 0.5
        else:
            concern_alignment = 0.8  # Neutral sentiment needs less validation
            
        consistency_score += concern_alignment
        checks_performed += 1
        
        # Calculate final consistency score
        final_score = consistency_score / (checks_performed or 1)
        
        return max(0.0, min(1.0, final_score))

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